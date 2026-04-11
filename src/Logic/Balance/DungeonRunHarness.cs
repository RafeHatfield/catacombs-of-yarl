using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Per-floor metrics collected during a DungeonRun.
/// </summary>
public sealed class FloorRunMetrics
{
    /// <summary>Dungeon depth this floor was generated at (1-based).</summary>
    public int Depth { get; init; }

    /// <summary>Turns taken on this floor before descending or dying.</summary>
    public int TurnsTaken { get; set; }

    /// <summary>Monsters killed on this floor.</summary>
    public int MonstersKilled { get; set; }

    /// <summary>Player HP at end of floor (0 if player died).</summary>
    public int PlayerHpAtEnd { get; set; }

    /// <summary>True if the player died on this floor.</summary>
    public bool PlayerDied { get; set; }

    /// <summary>True if the player successfully descended (reached stair after clearing floor).</summary>
    public bool Descended { get; set; }
}

/// <summary>
/// Aggregate result of a full DungeonRun across multiple floors.
/// </summary>
public sealed class DungeonRunResult
{
    /// <summary>Seed used for this run.</summary>
    public int Seed { get; init; }

    /// <summary>Number of floors the bot attempted to traverse.</summary>
    public int FloorsAttempted { get; init; }

    /// <summary>Number of floors the bot successfully cleared and descended from.</summary>
    public int FloorsCompleted { get; set; }

    /// <summary>Total turns taken across all floors.</summary>
    public int TotalTurns { get; set; }

    /// <summary>Total monsters killed across all floors.</summary>
    public int TotalKills { get; set; }

    /// <summary>Player HP at end of the final floor (0 if player died).</summary>
    public int FinalHp { get; set; }

    /// <summary>Whether the player died before completing all floors.</summary>
    public bool PlayerDied { get; set; }

    /// <summary>Per-floor breakdown. Count == FloorsAttempted.</summary>
    public IReadOnlyList<FloorRunMetrics> PerFloor { get; init; } = Array.Empty<FloorRunMetrics>();
}

/// <summary>
/// Runs BotBrain through N dungeon floors, collecting per-floor metrics.
/// Pure Logic layer — no Godot dependency.
///
/// Reusable for balance experiments and regression tests on the dungeon campaign loop.
/// Complements ScenarioHarness (arena scenarios) with a full floor-progression view.
///
/// Usage:
///   var harness = new DungeonRunHarness(floorBuilder);
///   var result = harness.Run(floors: 5, baseSeed: 1337);
/// </summary>
public sealed class DungeonRunHarness
{
    // After floor is cleared, bot walks toward stair. Cap turns per floor to prevent
    // infinite loops if the bot gets stuck (e.g. pathfinding edge case).
    private const int MaxTurnsPerFloor = 500;

    // Override the GameState TurnLimit for dungeon floors. The default is 100 (scenario mode),
    // which is far too low for a procedural dungeon floor with pathfinding to a distant stair.
    // DungeonFloorBuilder does not set this — it's the harness's responsibility to impose
    // a reasonable bound without making IsGameOver trigger prematurely.
    private const int DungeonFloorTurnLimit = 2000;

    private readonly DungeonFloorBuilder _floorBuilder;

    public DungeonRunHarness(DungeonFloorBuilder floorBuilder)
    {
        _floorBuilder = floorBuilder;
    }

    /// <summary>
    /// Run BotBrain through <paramref name="floors"/> dungeon floors starting at depth 1.
    ///
    /// Seed derivation per floor: baseSeed + depth * 1_000_003
    /// (matches MultiFloorSmokeTests — ensures same floor geometry for the same seed).
    ///
    /// The bot uses BotBrain for combat and healing decisions. When a floor is clear
    /// (all monsters dead), the bot paths to the stair and descends. If the player dies
    /// or the per-floor turn cap is hit, the run stops early.
    /// </summary>
    public DungeonRunResult Run(int floors, int baseSeed = 1337)
    {
        var perFloor = new List<FloorRunMetrics>(floors);
        Entity? player = null;
        BoonTracker? boonTracker = null;
        int totalTurns = 0;
        int totalKills = 0;
        int floorsCompleted = 0;
        bool playerDied = false;
        int finalHp = 0;

        for (int depth = 1; depth <= floors; depth++)
        {
            // Distinct-but-reproducible seed per depth — same pattern as smoke tests
            var rng = new SeededRandom(baseSeed + depth * 1_000_003);
            var state = _floorBuilder.Build(depth, rng, player, boonTracker: boonTracker);

            // Dungeon floors need far more turns than the scenario default (100).
            // Set a generous limit so IsGameOver only fires on player death, not turn-out.
            state.TurnLimit = DungeonFloorTurnLimit;

            var floorMetrics = new FloorRunMetrics { Depth = depth };
            int floorTurns = 0;
            int floorKills = 0;

            while (!state.IsGameOver && floorTurns < MaxTurnsPerFloor)
            {
                PlayerAction action;

                if (state.IsFloorClear && state.StairDown != null)
                {
                    // All monsters dead — navigate to the stair and descend
                    if (state.PlayerOnStairDown)
                    {
                        action = PlayerAction.Descend;
                    }
                    else
                    {
                        // Path one step toward the stair
                        var path = Pathfinder.AStar(
                            state.Map,
                            state.Player.X, state.Player.Y,
                            state.StairDown.X, state.StairDown.Y,
                            state.Player);

                        if (path != null && path.Count > 0)
                        {
                            var (nx, ny) = path[0];
                            action = PlayerAction.MoveTo(nx, ny);
                        }
                        else
                        {
                            // Pathfinding failed (stair unreachable) — wait rather than infinite-loop
                            action = PlayerAction.Wait;
                        }
                    }
                }
                else
                {
                    // Normal combat/heal decision via BotBrain
                    var botAction = BotBrain.Decide(
                        state.Player,
                        state.PlayerFighter,
                        state.PlayerInventory,
                        state.Monsters,
                        state.Map);

                    // BotBrain.ToPlayerAction uses GameMap.MoveToward — a greedy directional
                    // step that gets stuck at walls. In a dungeon with rooms and corridors, we
                    // need proper A* to navigate across the floor. Override MoveToward actions
                    // with A*-pathed moves so the bot can reach monsters in other rooms.
                    if (botAction.Type == BotAction.ActionType.MoveToward && botAction.Target != null)
                    {
                        var target = botAction.Target;
                        var path = Pathfinder.AStar(
                            state.Map,
                            state.Player.X, state.Player.Y,
                            target.X, target.Y,
                            state.Player);

                        if (path != null && path.Count > 0)
                        {
                            var (nx, ny) = path[0];
                            action = PlayerAction.MoveTo(nx, ny);
                        }
                        else
                        {
                            action = PlayerAction.Wait; // unreachable target
                        }
                    }
                    else
                    {
                        action = BotBrain.ToPlayerAction(botAction);
                    }
                }

                var result = TurnController.ProcessTurn(state, action);
                floorTurns++;

                // Count kills from this turn's events
                floorKills += result.Events.OfType<DeathEvent>()
                    .Count(e => e.ActorId != state.Player.Id);

                // Descend signals floor completion — move to the next depth
                if (result.Events.Any(e => e is DescendEvent))
                {
                    floorMetrics.Descended = true;
                    floorsCompleted++;
                    break;
                }
            }

            floorMetrics.TurnsTaken = floorTurns;
            floorMetrics.MonstersKilled = floorKills;
            floorMetrics.PlayerHpAtEnd = state.PlayerFighter.Hp;
            floorMetrics.PlayerDied = !state.PlayerFighter.IsAlive;

            perFloor.Add(floorMetrics);

            totalTurns += floorTurns;
            totalKills += floorKills;
            finalHp = state.PlayerFighter.Hp;

            if (!state.PlayerFighter.IsAlive)
            {
                playerDied = true;
                break;
            }

            // Carry the same player entity and boon tracker forward to the next floor
            player = state.Player;
            boonTracker = state.BoonTracker;
        }

        return new DungeonRunResult
        {
            Seed = baseSeed,
            FloorsAttempted = perFloor.Count,
            FloorsCompleted = floorsCompleted,
            TotalTurns = totalTurns,
            TotalKills = totalKills,
            FinalHp = finalHp,
            PlayerDied = playerDied,
            PerFloor = perFloor,
        };
    }
}
