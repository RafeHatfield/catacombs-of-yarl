using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Balance;

/// <summary>
/// Tests for DungeonRunHarness — the multi-floor bot run reusable class.
/// Complements ScenarioHarness (arena scenarios) with a full floor-progression view.
/// </summary>
[TestFixture]
[Description("DungeonRunHarness: multi-floor bot runs with per-floor metrics")]
public class DungeonRunTests
{
    private DungeonRunHarness _harness = null!;
    private const int BaseSeed = 1337;

    [OneTimeSetUp]
    public void Setup()
    {
        var testDir = TestContext.CurrentContext.TestDirectory;
        var entitiesPath = Path.Combine(testDir, "..", "..", "..", "..", "config", "entities.yaml");
        var levelTemplatesPath = Path.Combine(testDir, "..", "..", "..", "..", "config", "level_templates.yaml");

        Assert.That(File.Exists(entitiesPath), Is.True, $"entities.yaml not found at {entitiesPath}");
        Assert.That(File.Exists(levelTemplatesPath), Is.True, $"level_templates.yaml not found at {levelTemplatesPath}");

        var loader = new ContentLoader();
        var content = loader.LoadAllFromFile(entitiesPath);
        var entityFactory = new EntityFactory();
        var itemFactory = new ItemFactory(content.Items, entityFactory);
        var monsterFactory = new MonsterFactory(content.Monsters, entityFactory, itemFactory);
        var consumableFactory = new ConsumableFactory(content.Consumables, entityFactory);
        var templates = LevelTemplateRegistry.FromFile(levelTemplatesPath);

        var floorBuilder = new DungeonFloorBuilder(templates, monsterFactory, itemFactory, consumableFactory);
        _harness = new DungeonRunHarness(floorBuilder);
    }

    /// <summary>
    /// Two runs with the same seed must produce identical per-floor metrics.
    /// The dungeon campaign loop must be as deterministic as the scenario harness.
    /// </summary>
    [Test]
    [Description("Same seed produces identical per-floor metrics — full dungeon campaign determinism")]
    public void ThreeFloors_Deterministic()
    {
        var result1 = _harness.Run(floors: 3, baseSeed: BaseSeed);
        var result2 = _harness.Run(floors: 3, baseSeed: BaseSeed);

        Assert.That(result1.TotalTurns, Is.EqualTo(result2.TotalTurns),
            "Same seed should produce the same total turn count");
        Assert.That(result1.FloorsCompleted, Is.EqualTo(result2.FloorsCompleted),
            "Same seed should produce the same number of completed floors");
        Assert.That(result1.TotalKills, Is.EqualTo(result2.TotalKills),
            "Same seed should produce the same total kill count");

        Assert.That(result1.PerFloor.Count, Is.EqualTo(result2.PerFloor.Count));
        for (int i = 0; i < result1.PerFloor.Count; i++)
        {
            var f1 = result1.PerFloor[i];
            var f2 = result2.PerFloor[i];
            Assert.That(f1.TurnsTaken, Is.EqualTo(f2.TurnsTaken),
                $"Floor {f1.Depth}: TurnsTaken differs between runs");
            Assert.That(f1.MonstersKilled, Is.EqualTo(f2.MonstersKilled),
                $"Floor {f1.Depth}: MonstersKilled differs between runs");
            Assert.That(f1.PlayerHpAtEnd, Is.EqualTo(f2.PlayerHpAtEnd),
                $"Floor {f1.Depth}: PlayerHpAtEnd differs between runs");
        }
    }

    /// <summary>
    /// 5-floor run completes at least 2 floors and produces non-zero metrics.
    /// The bot may die on deeper floors — 2/5 is the minimum signal
    /// that the floor-progression loop is working, not just stalling.
    /// </summary>
    [Test]
    [Description("5-floor run completes >= 2 floors, has non-zero turns, positive kill counts")]
    public void FiveFloors_CompletesWithMetrics()
    {
        var result = _harness.Run(floors: 5, baseSeed: BaseSeed);

        TestContext.WriteLine($"5-floor run (seed {BaseSeed}):");
        TestContext.WriteLine($"  Floors completed: {result.FloorsCompleted}/{result.FloorsAttempted}");
        TestContext.WriteLine($"  Total turns: {result.TotalTurns}");
        TestContext.WriteLine($"  Total kills: {result.TotalKills}");
        TestContext.WriteLine($"  Player died: {result.PlayerDied}");
        TestContext.WriteLine($"  Final HP: {result.FinalHp}");
        TestContext.WriteLine("");
        foreach (var floor in result.PerFloor)
        {
            TestContext.WriteLine($"  Depth {floor.Depth}: turns={floor.TurnsTaken} kills={floor.MonstersKilled} " +
                                  $"hp={floor.PlayerHpAtEnd} died={floor.PlayerDied} descended={floor.Descended}");
        }

        Assert.That(result.FloorsCompleted, Is.GreaterThanOrEqualTo(2),
            $"Bot should complete at least 2 of 5 floors (completed {result.FloorsCompleted})");
        Assert.That(result.TotalTurns, Is.GreaterThan(0),
            "Run should have taken at least one turn");
        Assert.That(result.TotalKills, Is.GreaterThan(0),
            "Bot should have killed at least one monster across 5 floors");
        Assert.That(result.PerFloor.Count, Is.GreaterThan(0),
            "PerFloor list should contain at least one entry");
    }

    /// <summary>
    /// 10-floor run completes within a bounded turn count.
    /// Guards against infinite loops, stuck bots, or pathfinding regressions.
    /// Threshold is generous to account for deep floors with more rooms + monsters.
    ///
    /// Tagged Slow because it builds and traverses 10 procedural floors.
    /// </summary>
    [Test]
    [Category("Slow")]
    [Description("10-floor run completes within 5000 total turns — guards against stuck-bot regressions")]
    public void TenFloors_BoundedTurns()
    {
        var result = _harness.Run(floors: 10, baseSeed: BaseSeed);

        TestContext.WriteLine($"10-floor run: {result.TotalTurns} total turns, " +
                              $"{result.FloorsCompleted}/{result.FloorsAttempted} floors completed");

        Assert.That(result.TotalTurns, Is.LessThan(5000),
            $"10-floor run took {result.TotalTurns} turns — bot may be stuck. " +
            $"Per-floor breakdown: {string.Join(", ", result.PerFloor.Select(f => $"d{f.Depth}:{f.TurnsTaken}t"))}");
    }
}
