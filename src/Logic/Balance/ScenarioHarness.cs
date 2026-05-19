using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Bot heal thresholds — matches the Python prototype's "balanced" persona.
/// </summary>
public static class BotConfig
{
    public const double HealThreshold = 0.30;
    public const double PanicThreshold = 0.15;
}

/// <summary>
/// Runs scenario simulations with tile-based positioning and BotBrain AI.
/// Delegates turn processing to TurnController — the shared engine used by
/// both the harness and the presentation layer.
/// </summary>
public sealed class ScenarioHarness
{
    private readonly MonsterFactory _monsterFactory;
    private readonly ItemFactory? _itemFactory;
    private readonly ConsumableFactory? _consumableFactory;
    private readonly SpellItemFactory? _spellItemFactory;

    public ScenarioHarness(
        MonsterFactory monsterFactory,
        ItemFactory? itemFactory = null,
        ConsumableFactory? consumableFactory = null,
        SpellItemFactory? spellItemFactory = null)
    {
        _monsterFactory = monsterFactory;
        _itemFactory = itemFactory;
        _consumableFactory = consumableFactory;
        _spellItemFactory = spellItemFactory;
    }

    public AggregatedMetrics Run(ScenarioDefinition scenario, int baseSeed = 1337, int? runsOverride = null)
    {
        int runCount = runsOverride ?? scenario.Runs;
        var allRuns = new List<RunMetrics>();
        for (int i = 0; i < runCount; i++)
            allRuns.Add(RunOnce(scenario, baseSeed + i));
        return AggregatedMetrics.FromRuns(scenario.ScenarioId, baseSeed, allRuns,
            name: scenario.Name, depth: scenario.Depth, isProbe: scenario.IsProbe);
    }

    /// <summary>
    /// Run a single scenario iteration, returning per-run metrics.
    ///
    /// The optional <paramref name="context"/> is passed through to BotBrain.Decide() unchanged.
    /// ScenarioHarness does not create or consume the recorder — callers that want telemetry
    /// create a BotDecisionContext with their own recorder and pass it here. The public Run()
    /// method does not use telemetry; callers that need it call RunOnce() directly.
    ///
    /// All existing test callers that omit context continue to work unchanged.
    /// </summary>
    public RunMetrics RunOnce(ScenarioDefinition scenario, int seed, BotDecisionContext? context = null)
    {
        var state = GameStateFactory.FromScenario(
            scenario, seed, _monsterFactory, _itemFactory, _consumableFactory, _spellItemFactory);
        // PoC scenario_level_loader ignores state:"aware" on monsters — they activate via
        // item-seeking diversion (ground potion draws sequential aggro). C# harness mode
        // replicates this: monsters passive until attacked (Hp < MaxHp proxy).
        // Exception: state:"aware" in the scenario YAML pre-sets AlertedState so the monster
        // acts from turn 1 — needed for ranged scenarios where denial shots deal no damage.
        state.IsHarnessMode = true;

        // Wire state:"aware" → AlertedState pre-set. Monsters are created in YAML order;
        // we expand count>1 groups so index correspondence holds.
        int monsterIdx = 0;
        var player0 = state.Player;
        foreach (var monsterDef in scenario.Monsters)
        {
            for (int i = 0; i < monsterDef.Count; i++, monsterIdx++)
            {
                if (monsterIdx >= state.Monsters.Count) break;
                if (monsterDef.State == "aware")
                {
                    var alert = state.Monsters[monsterIdx].GetOrAdd<AlertedState>();
                    alert.LastKnownPlayerX = player0.X;
                    alert.LastKnownPlayerY = player0.Y;
                    alert.TurnsUntilDeaggro = AlertedState.DeaggroTurns;
                }
            }
        }

        var metrics = new RunMetrics();
        var player = state.Player;
        var playerFighter = state.PlayerFighter;
        var inventory = state.PlayerInventory;

        // Capture initial HP values for H_PM / H_MP calculations
        metrics.PlayerMaxHp = playerFighter.MaxHp;
        if (state.Monsters.Count > 0)
        {
            var monsterHps = state.Monsters
                .Select(m => m.Get<Fighter>()?.MaxHp ?? 0)
                .Where(hp => hp > 0)
                .ToList();
            if (monsterHps.Count > 0)
                metrics.MonsterAvgMaxHp = monsterHps.Average();
        }

        while (!state.IsGameOver)
        {
            // Bot dispatch: ranged_net_arrow uses the kiting bot; everything else uses BotBrain.
            // player_bot field in scenario YAML selects the policy.
            PlayerAction playerAction;
            if (scenario.Player.PlayerBot == "ranged_net_arrow")
            {
                playerAction = RangedNetArrowBot.Decide(player, playerFighter, inventory, state.Monsters, state.Map, state);
            }
            else
            {
                var botAction = BotBrain.Decide(player, playerFighter, inventory, state.Monsters, state.Map, context);
                playerAction = BotBrain.ToPlayerAction(botAction);
            }
            var result = TurnController.ProcessTurn(state, playerAction);
            metrics.RecordTurn(result, player.Id);
        }

        metrics.PlayerDied = !playerFighter.IsAlive;
        return metrics;
    }
}
