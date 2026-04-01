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

    public AggregatedMetrics Run(ScenarioDefinition scenario, int baseSeed = 1337)
    {
        var allRuns = new List<RunMetrics>();
        for (int i = 0; i < scenario.Runs; i++)
            allRuns.Add(RunOnce(scenario, baseSeed + i));
        return AggregatedMetrics.FromRuns(scenario.ScenarioId, baseSeed, allRuns);
    }

    public RunMetrics RunOnce(ScenarioDefinition scenario, int seed)
    {
        var state = GameStateFactory.FromScenario(
            scenario, seed, _monsterFactory, _itemFactory, _consumableFactory, _spellItemFactory);

        var metrics = new RunMetrics();
        var player = state.Player;
        var playerFighter = state.PlayerFighter;
        var inventory = state.PlayerInventory;

        while (!state.IsGameOver)
        {
            var botAction = BotBrain.Decide(player, playerFighter, inventory, state.Monsters, state.Map);
            var playerAction = BotBrain.ToPlayerAction(botAction);
            var result = TurnController.ProcessTurn(state, playerAction);
            metrics.RecordTurn(result, player.Id);
        }

        metrics.PlayerDied = !playerFighter.IsAlive;
        return metrics;
    }
}
