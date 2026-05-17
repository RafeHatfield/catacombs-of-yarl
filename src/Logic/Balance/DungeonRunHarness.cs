using System.Diagnostics;
using System.Text;
using CatacombsOfYarl.Logic.Combat;
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

    /// <summary>Player max HP at end of floor. Used for HP-fraction calculations per floor.</summary>
    public int PlayerMaxHp { get; set; }

    /// <summary>True if the player died on this floor.</summary>
    public bool PlayerDied { get; set; }

    /// <summary>True if the player successfully descended (reached stair after clearing floor).</summary>
    public bool Descended { get; set; }

    /// <summary>
    /// Healing potions used on this floor (player HealEvent count, filtered to player ActorId only).
    /// Does NOT count accidental monster item-use that heals the player.
    /// </summary>
    public int PotionsUsed { get; set; }

    /// <summary>
    /// True when this floor ended because the per-floor turn cap was hit, rather than
    /// descent or death. Indicates a potential stuck-bot or pathfinding regression.
    /// </summary>
    public bool HitMaxTurns { get; set; }

    /// <summary>
    /// Loot category counts for this floor — how many items of each category spawned.
    /// Null if loot telemetry was not collected (e.g., no PityTracker was wired).
    /// Keys match loot_tags.yaml categories: healing, panic, offensive, utility,
    /// upgrade_weapon, upgrade_armor, rare, defensive, key.
    /// </summary>
    public IReadOnlyDictionary<string, int>? LootCategoryCounts { get; set; }

    /// <summary>
    /// Number of times hard pity forced a guaranteed item on this floor.
    /// </summary>
    public int LootHardPityFires { get; set; }
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
///   var summary = harness.RunSoak(floors: 3, runs: 100, baseSeed: 1337);
/// </summary>
public sealed class DungeonRunHarness
{
    // After floor is cleared, bot walks toward stair. Cap turns per floor to prevent
    // infinite loops if the bot gets stuck (e.g. pathfinding edge case).
    // 1000 gives a full dungeon floor (120×80, ~40 rooms, 10+ monsters) comfortable clearance.
    // 500 was too tight — large floors with scattered monsters could time out legitimately.
    private const int MaxTurnsPerFloor = 1000;

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
    ///
    /// Backward-compatible: callers that used Run() previously get identical results.
    /// </summary>
    public DungeonRunResult Run(int floors, int baseSeed = 1337)
    {
        var soakResult = RunSingle(floors, baseSeed, enableTelemetry: false);

        // Reconstruct the legacy DungeonRunResult from the enriched soak result.
        // FloorsAttempted is PerFloor.Count — same logic as before.
        return new DungeonRunResult
        {
            Seed             = soakResult.Seed,
            FloorsAttempted  = soakResult.PerFloor.Count,
            FloorsCompleted  = soakResult.FloorsCompleted,
            TotalTurns       = soakResult.TotalTurns,
            TotalKills       = soakResult.TotalKills,
            FinalHp          = soakResult.FinalHp,
            PlayerDied       = soakResult.Outcome == OutcomeClassifier.Died,
            PerFloor         = soakResult.PerFloor,
        };
    }

    /// <summary>
    /// Run a single dungeon campaign and return a formatted narrative transcript.
    /// Captures floor entries, voice lines, monster kills, deaths, descents, and traps.
    /// Intended for D1 narrative testing — prints a human-readable play-by-play.
    /// </summary>
    public string RunTranscript(int floors, int seed)
    {
        var entries = new List<TranscriptEntry>();
        var result = RunSingle(floors, seed, enableTelemetry: false, transcript: entries);
        return FormatTranscript(result, entries, floors, seed);
    }

    private static string FormatTranscript(DungeonSoakRunResult result, List<TranscriptEntry> entries, int floors, int seed)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"=== Run Transcript (seed {seed}, {floors} floors) ===");
        sb.AppendLine($"Outcome: {result.Outcome}  |  Floors completed: {result.FloorsCompleted}/{floors}  |  Kills: {result.TotalKills}  |  Turns: {result.TotalTurns}");
        if (!string.IsNullOrEmpty(result.FailureDetail))
            sb.AppendLine($"Death: {result.FailureDetail}");
        sb.AppendLine();

        int currentDepth = 0;
        foreach (var entry in entries)
        {
            if (entry.Depth != currentDepth)
            {
                currentDepth = entry.Depth;
                // floor_enter entries are the depth header — skip duplicate header
            }

            string line = entry.EventType switch
            {
                "floor_enter"    => $"\n[Floor {entry.Depth}]",
                "voice"          => $"  T{entry.FloorTurn,4} | Voice:   {entry.Detail}",
                "monster_killed" => $"  T{entry.FloorTurn,4} | Kill:    {entry.Detail}",
                "player_died"    => $"  T{entry.FloorTurn,4} | DIED:    killed by {entry.Detail}",
                "descended"      => $"  T{entry.FloorTurn,4} | Descended to floor {entry.Depth + 1}",
                "trap_triggered" => $"  T{entry.FloorTurn,4} | Trap:    {entry.Detail}",
                _                => $"  T{entry.FloorTurn,4} | {entry.EventType}: {entry.Detail}",
            };
            sb.AppendLine(line);
        }

        // Voice-line summary at end of transcript
        if (result.VoiceLineHits?.Count > 0)
        {
            sb.AppendLine();
            sb.AppendLine("Voice Line Summary:");
            foreach (var (triggerId, count) in result.VoiceLineHits.OrderByDescending(kv => kv.Value))
                sb.AppendLine($"  {triggerId,-55}  x{count}");
        }

        sb.AppendLine();
        return sb.ToString();
    }

    /// <summary>
    /// Run N dungeon campaigns and return aggregate soak statistics.
    ///
    /// Seed per run: baseSeed + i (i = 0..runs-1), matching the PoC convention.
    /// Each run is wrapped in try/catch — exceptions produce an "exception" result
    /// and are logged to stderr, but do NOT abort the whole session.
    ///
    /// This is the primary entry point for automated regression testing.
    /// </summary>
    public DungeonSoakSummary RunSoak(int floors, int runs, int baseSeed = 1337)
    {
        var results = new List<DungeonSoakRunResult>(runs);

        for (int i = 0; i < runs; i++)
        {
            int seed = baseSeed + i;
            try
            {
                // Telemetry always enabled in soak mode — no reason to run N iterations without it.
                var result = RunSingle(floors, seed, enableTelemetry: true);
                results.Add(result);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"  [soak] run {i} (seed {seed}) threw: {ex.Message}");
                results.Add(new DungeonSoakRunResult
                {
                    Seed          = seed,
                    Outcome       = OutcomeClassifier.Exception,
                    FailureType   = OutcomeClassifier.FailureException,
                    FailureDetail = ex.Message,
                    FloorsCompleted = 0,
                    PerFloor      = Array.Empty<FloorRunMetrics>(),
                });
            }
        }

        return DungeonSoakSummary.ComputeFrom(results, configuredFloors: floors);
    }

    /// <summary>
    /// Core single-run implementation. Returns a fully populated DungeonSoakRunResult
    /// including killerName, potions tracking, boon count, and timing.
    ///
    /// Both Run() and RunSoak() call this method. It replaces the original run loop
    /// while preserving identical behavior for all existing callers.
    ///
    /// When <paramref name="enableTelemetry"/> is true (default for soak mode), creates a
    /// BotTelemetryRecorder and passes a BotDecisionContext to every BotBrain.Decide() call,
    /// storing the resulting BotRunSummary in the returned DungeonSoakRunResult.BotSummary.
    /// When false (legacy Run() path), no recorder is created and BotSummary is null.
    /// </summary>
    private DungeonSoakRunResult RunSingle(int floors, int baseSeed, bool enableTelemetry = false, IList<TranscriptEntry>? transcript = null)
    {
        var sw = Stopwatch.StartNew();

        var perFloor      = new List<FloorRunMetrics>(floors);
        Entity? player    = null;
        Entity? lastFloorPlayer = null; // always the last floor's player entity (even on death)
        BoonTracker? boonTracker = null;
        PityTracker? pityTracker = null;
        int totalTurns    = 0;
        int totalKills    = 0;
        int floorsCompleted = 0;
        int totalPotionsUsed = 0;
        int finalHp       = 0;
        int finalMaxHp    = 0;
        string? killerName = null;
        var voiceLineHits = new Dictionary<string, int>();

        // Create a single recorder for the whole run when telemetry is enabled.
        // All BotBrain.Decide() calls share this recorder; context carries per-call metadata.
        BotTelemetryRecorder? recorder = enableTelemetry ? new BotTelemetryRecorder() : null;

        for (int depth = 1; depth <= floors; depth++)
        {
            transcript?.Add(new TranscriptEntry { Depth = depth, FloorTurn = 0, EventType = "floor_enter", Detail = $"Depth {depth}" });

            // Distinct-but-reproducible seed per depth — same pattern as smoke tests
            var rng = new SeededRandom(baseSeed + depth * 1_000_003);
            var state = _floorBuilder.Build(depth, rng, player, boonTracker: boonTracker, pityTracker: pityTracker);

            // Dungeon floors need far more turns than the scenario default (100).
            // Set a generous limit so IsGameOver only fires on player death, not turn-out.
            state.TurnLimit = DungeonFloorTurnLimit;

            var floorMetrics = new FloorRunMetrics { Depth = depth };
            int floorTurns   = 0;
            int floorKills   = 0;
            int floorPotions = 0;
            int playerId     = state.Player.Id;
            bool descended   = false;

            while (!state.IsGameOver && floorTurns < MaxTurnsPerFloor)
            {
                PlayerAction action;
                // TurnNumber for telemetry: accumulated total turns so far + current floor turns.
                // This gives a monotonically increasing turn number across the whole run.
                int currentTurnNumber = totalTurns + floorTurns + 1;

                if (state.IsFloorClear && state.StairDown != null)
                {
                    // All monsters dead — navigate to the stair and descend.
                    // Emit NavigateToStair telemetry for the harness-driven path,
                    // which is not inside BotBrain.Decide() (see plan risk #3).
                    if (state.PlayerOnStairDown)
                    {
                        // Emit a Descend decision for the actual descend step
                        recorder?.Record(BuildNavigateRecord(state, currentTurnNumber, depth, "Descend", "navigate_stair"));
                        action = PlayerAction.Descend;
                    }
                    else
                    {
                        // Path one step toward the stair
                        var path = Pathfinder.AStar(
                            state.Map,
                            state.Player.X, state.Player.Y,
                            state.StairDown.X, state.StairDown.Y,
                            state.Player,
                            canPassDoors: true);

                        if (path != null && path.Count > 0)
                        {
                            recorder?.Record(BuildNavigateRecord(state, currentTurnNumber, depth, "NavigateToStair", "navigate_stair"));
                            var (nx, ny) = path[0];
                            action = PlayerAction.MoveTo(nx, ny);
                        }
                        else
                        {
                            // Pathfinding failed (stair unreachable) — wait rather than infinite-loop
                            recorder?.Record(BuildNavigateRecord(state, currentTurnNumber, depth, "Wait", "navigate_stair"));
                            action = PlayerAction.Wait;
                        }
                    }
                }
                else
                {
                    // Normal combat/heal decision via BotBrain.
                    // Pass context when telemetry is enabled so BotBrain emits a decision record.
                    BotDecisionContext? decisionContext = recorder != null
                        ? new BotDecisionContext(recorder, currentTurnNumber, depth)
                        : null;

                    var botAction = BotBrain.Decide(
                        state.Player,
                        state.PlayerFighter,
                        state.PlayerInventory,
                        state.Monsters,
                        state.Map,
                        decisionContext,
                        floorItems: state.FloorItems);

                    // BotBrain.ToPlayerAction uses GameMap.MoveToward — a greedy directional
                    // step that gets stuck at walls. In a dungeon with rooms and corridors, we
                    // need proper A* to navigate across the floor. Override MoveToward actions
                    // with A*-pathed moves so the bot can reach monsters in other rooms.
                    if (botAction.Type == BotAction.ActionType.MoveToward && botAction.Target != null)
                    {
                        var target = botAction.Target;

                        // Build detected trap set so the bot routes around known hazards.
                        // If trap-avoidance produces no path (bot is completely surrounded),
                        // fall back to unconstrained A* to keep the bot moving.
                        var trapTiles = Pathfinder.DetectedTrapTiles(state.Features);
                        var path = Pathfinder.AStar(
                            state.Map,
                            state.Player.X, state.Player.Y,
                            target.X, target.Y,
                            state.Player,
                            canPassDoors: true,
                            avoidTiles: trapTiles.Count > 0 ? trapTiles : null);

                        // Fallback: if trap-avoiding path fails, try without avoidance
                        path ??= Pathfinder.AStar(
                            state.Map,
                            state.Player.X, state.Player.Y,
                            target.X, target.Y,
                            state.Player,
                            canPassDoors: true);

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

                var turnResult = TurnController.ProcessTurn(state, action);
                floorTurns++;

                // Process events from this turn
                foreach (var evt in turnResult.Events)
                {
                    switch (evt)
                    {
                        case DeathEvent death when death.ActorId != playerId:
                            // Monster died — count kill
                            floorKills++;
                            if (transcript != null)
                            {
                                string mName = state.Monsters.FirstOrDefault(m => m.Id == death.ActorId)?.Name ?? "unknown";
                                transcript.Add(new TranscriptEntry { Depth = depth, FloorTurn = floorTurns, EventType = "monster_killed", Detail = mName });
                            }
                            break;

                        case DeathEvent death when death.ActorId == playerId:
                            // Player died — capture killer name immediately.
                            // Dead monsters remain in state.Monsters (not removed until next floor),
                            // so this lookup works even if the killer died in the same turn.
                            // KillerId = -1 means a ground hazard kill (fire/gas); no entity to look up.
                            killerName = death.KillerId == -1
                                ? "Ground Hazard"
                                : state.Monsters.FirstOrDefault(m => m.Id == death.KillerId)?.Name;
                            transcript?.Add(new TranscriptEntry { Depth = depth, FloorTurn = floorTurns, EventType = "player_died", Detail = killerName ?? "unknown" });
                            break;

                        case HealEvent heal when heal.ActorId == playerId:
                            // Player used a healing item. Filter to player only — monster item-use
                            // that accidentally heals the player via HealEvent also has a different
                            // ActorId (the monster), so this check is correct.
                            floorPotions++;
                            break;

                        case DescendEvent:
                            descended = true;
                            floorsCompleted++;
                            transcript?.Add(new TranscriptEntry { Depth = depth, FloorTurn = floorTurns, EventType = "descended", Detail = "" });
                            break;

                        case VoiceLineEvent v:
                            voiceLineHits.TryGetValue(v.TriggerId, out int vlc);
                            voiceLineHits[v.TriggerId] = vlc + 1;
                            transcript?.Add(new TranscriptEntry { Depth = depth, FloorTurn = floorTurns, EventType = "voice", Detail = v.TriggerId });
                            break;

                        case TrapTriggeredEvent trap when trap.TargetId == playerId:
                            transcript?.Add(new TranscriptEntry { Depth = depth, FloorTurn = floorTurns, EventType = "trap_triggered", Detail = trap.Source });
                            break;
                    }
                }

                if (descended) break;
            }

            floorMetrics.TurnsTaken    = floorTurns;
            floorMetrics.MonstersKilled = floorKills;
            floorMetrics.PlayerHpAtEnd  = state.PlayerFighter.Hp;
            floorMetrics.PlayerMaxHp    = state.PlayerFighter.MaxHp;
            floorMetrics.PlayerDied     = !state.PlayerFighter.IsAlive;
            floorMetrics.Descended      = descended;
            floorMetrics.PotionsUsed    = floorPotions;
            // HitMaxTurns: floor ended at the cap without descent or death
            floorMetrics.HitMaxTurns    = floorTurns >= MaxTurnsPerFloor
                && !floorMetrics.Descended
                && !floorMetrics.PlayerDied;

            // Snapshot per-floor loot telemetry from PityTracker before carrying it forward.
            if (state.PityTracker != null)
            {
                var (counts, fires) = state.PityTracker.SnapshotAndResetFloorTelemetry();
                floorMetrics.LootCategoryCounts = counts;
                floorMetrics.LootHardPityFires  = fires;
            }

            perFloor.Add(floorMetrics);

            totalTurns   += floorTurns;
            totalKills   += floorKills;
            totalPotionsUsed += floorPotions;
            finalHp      = state.PlayerFighter.Hp;
            finalMaxHp   = state.PlayerFighter.MaxHp;
            // Track the last-seen player entity for post-run inventory scan.
            // On death, this is the dead player entity from the final floor.
            lastFloorPlayer = state.Player;

            if (!state.PlayerFighter.IsAlive)
                break;

            // Carry the same player entity, boon tracker, and pity tracker forward to the next floor.
            // PityTracker persists across floors — drought counters don't reset on descent (PoC-exact).
            player       = state.Player;
            boonTracker  = state.BoonTracker;
            pityTracker  = state.PityTracker;
        }

        sw.Stop();

        // Build the intermediate DungeonRunResult for OutcomeClassifier.
        bool playerDiedThisRun = killerName != null
            || (perFloor.Count > 0 && perFloor[^1].PlayerDied);

        var runResult = new DungeonRunResult
        {
            Seed            = baseSeed,
            FloorsAttempted = perFloor.Count,
            FloorsCompleted = floorsCompleted,
            TotalTurns      = totalTurns,
            TotalKills      = totalKills,
            FinalHp         = finalHp,
            PlayerDied      = playerDiedThisRun,
            PerFloor        = perFloor,
        };

        var (outcome, failureType, failureDetail) = OutcomeClassifier.Classify(runResult, killerName);

        // Clamp finalHp to 0 on death — the plan specifies "0 if player died".
        // In-game HP can go below 0 on a fatal hit; clamp here for clean data.
        int reportedFinalHp = playerDiedThisRun ? 0 : finalHp;
        double hpFraction   = (finalMaxHp > 0 && !playerDiedThisRun)
            ? (double)finalHp / finalMaxHp
            : 0.0;

        // Count remaining potions from the last-seen player entity.
        // lastFloorPlayer is set every floor (including the death floor), so it is
        // never null after at least one floor was attempted.
        int potionsRemaining = CountHealingPotions(lastFloorPlayer);

        // Finalize telemetry: summarize and adjust DeathsWithUnusedPotions.
        // ComputeFrom() sets DeathsWithUnusedPotions = 1 if last decision had potions.
        // We correct it here: only count if the run actually ended in death.
        BotRunSummary? botSummary = null;
        if (recorder != null && recorder.Decisions.Count > 0)
        {
            var rawSummary = recorder.Summarize();
            int deathsWithUnused = playerDiedThisRun && rawSummary.DeathsWithUnusedPotions > 0 ? 1 : 0;

            botSummary = new BotRunSummary
            {
                TotalDecisions          = rawSummary.TotalDecisions,
                FloorsVisited           = rawSummary.FloorsVisited,
                ActionCounts            = rawSummary.ActionCounts,
                ReasonCounts            = rawSummary.ReasonCounts,
                ContextCounts           = rawSummary.ContextCounts,
                AvgHpWhenHealing        = rawSummary.AvgHpWhenHealing,
                HealDecisions           = rawSummary.HealDecisions,
                DeathsWithUnusedPotions = deathsWithUnused,
            };
        }

        return new DungeonSoakRunResult
        {
            Seed                = baseSeed,
            Outcome             = outcome,
            FailureType         = failureType,
            FailureDetail       = failureDetail,
            DeepestFloorReached = perFloor.Count > 0 ? perFloor[^1].Depth : 0,
            FloorsCompleted     = floorsCompleted,
            TotalTurns          = totalTurns,
            TotalKills          = totalKills,
            FinalHp             = reportedFinalHp,
            FinalMaxHp          = finalMaxHp,
            FinalHpFraction     = hpFraction,
            PotionsUsed         = totalPotionsUsed,
            PotionsRemaining    = potionsRemaining,
            BoonsAcquired       = boonTracker?.BoonsApplied.Count ?? 0,
            DurationSeconds     = sw.Elapsed.TotalSeconds,
            PerFloor            = perFloor,
            BotSummary          = botSummary,
            VoiceLineHits       = voiceLineHits.Count > 0 ? voiceLineHits : null,
        };
    }

    /// <summary>
    /// Build a BotDecisionRecord for the harness-driven navigate-to-stair path.
    /// This path is NOT inside BotBrain.Decide() (it's harness logic), so we emit
    /// telemetry manually here with the player's current state.
    /// </summary>
    private static BotDecisionRecord BuildNavigateRecord(
        GameState state,
        int turnNumber,
        int floorDepth,
        string actionType,
        string reason)
    {
        var fighter = state.PlayerFighter;
        double hpFraction = fighter.MaxHp > 0 ? (double)fighter.Hp / fighter.MaxHp : 0.0;
        var inventory = state.PlayerInventory;

        int potions = 0;
        if (inventory != null)
        {
            foreach (var item in inventory.Items)
            {
                var consumable = item.Get<Consumable>();
                if (consumable?.IsHealing == true)
                    potions += consumable.StackSize;
            }
        }

        return new BotDecisionRecord
        {
            TurnNumber              = turnNumber,
            FloorDepth              = floorDepth,
            ActionType              = actionType,
            Reason                  = reason,
            HpFraction              = hpFraction,
            VisibleEnemies          = 0, // floor is clear when navigating to stair
            AdjacentEnemies         = 0,
            HealingPotionsAvailable = potions,
            InCombat                = false,
            LowHp                   = hpFraction <= BotConfig.HealThreshold,
        };
    }

    /// <summary>
    /// Count healing potions in the entity's inventory.
    /// Returns 0 if entity is null or has no inventory.
    /// </summary>
    private static int CountHealingPotions(Entity? entity)
    {
        var inventory = entity?.Get<Inventory>();
        if (inventory == null) return 0;

        int count = 0;
        foreach (var item in inventory.Items)
        {
            var consumable = item.Get<Consumable>();
            if (consumable?.IsHealing == true)
                count += consumable.StackSize;
        }
        return count;
    }
}
