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
        // PoC scenario_level_loader ignores state:"aware" on monsters (see line 441: "not processed
        // to preserve existing baseline behavior"). Monsters activate via item-seeking diversion:
        // unattacked orcs move toward the ground potion between player and orcs, creating sequential
        // engagement. C# replicates this via harness mode: monsters passive until attacked.
        state.IsHarnessMode = true;

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
            var botAction = BotBrain.Decide(player, playerFighter, inventory, state.Monsters, state.Map, context);
            var playerAction = BotBrain.ToPlayerAction(botAction);
            var result = TurnController.ProcessTurn(state, playerAction);
            metrics.RecordTurn(result, player.Id);
        }

        metrics.PlayerDied = !playerFighter.IsAlive;
        return metrics;
    }
}
