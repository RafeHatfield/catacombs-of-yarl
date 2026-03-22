using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Balance;

/// <summary>
/// Integration test: loads real YAML, runs the depth 2 orc baseline scenario,
/// and validates metrics are in reasonable ranges.
/// </summary>
[TestFixture]
public class BaselineScenarioTests
{
    private ScenarioHarness _harness = null!;

    [OneTimeSetUp]
    public void Setup()
    {
        const string entitiesYaml = @"
monsters:
  orc:
    stats:
      hp: 28
      power: 0
      defense: 0
      xp: 35
      damage_min: 4
      damage_max: 6
      strength: 14
      dexterity: 10
      constitution: 12
      accuracy: 4
      evasion: 1
    char: ""o""
    color: [63, 127, 63]
    blocks: true
    faction: ""orc""
    etp_base: 27

  orc_grunt:
    name: ""Orc""
    extends: orc

weapons:
  dagger:
    name: ""Dagger""
    slot: ""main_hand""
    damage_min: 1
    damage_max: 4
    to_hit_bonus: 1
    damage_type: ""piercing""
    char: ""-""
    color: [139, 69, 19]

armor:
  leather_armor:
    name: ""Leather Armor""
    slot: ""chest""
    armor_class_bonus: 2
    armor_type: ""light""
    char: ""[""
    color: [139, 69, 19]
";
        var loader = new ContentLoader();
        var entityFactory = new EntityFactory();
        var monsters = loader.LoadMonsters(entitiesYaml);
        var items = loader.LoadItems(entitiesYaml);

        _harness = new ScenarioHarness(
            new MonsterFactory(monsters, entityFactory),
            new ItemFactory(items, entityFactory));
    }

    private static ScenarioDefinition Depth2OrcBaseline() => new()
    {
        ScenarioId = "depth2_orc_baseline",
        Name = "Depth 2 - Orc Baseline",
        Depth = 2,
        TurnLimit = 100,
        Runs = 50,
        Player = new ScenarioPlayer
        {
            Hp = 54,
            Strength = 12,
            Dexterity = 14,
            Constitution = 12,
            Accuracy = 2,
            Evasion = 1,
            DamageMin = 1,
            DamageMax = 4,
            Weapon = "dagger",
            Armor = "leather_armor",
        },
        Monsters = new List<ScenarioMonster>
        {
            new() { Type = "orc_grunt", Count = 3 }
        }
    };

    [Test]
    public void Depth2OrcBaseline_Deterministic()
    {
        var scenario = Depth2OrcBaseline();
        var agg1 = _harness.Run(scenario, baseSeed: 1337);
        var agg2 = _harness.Run(scenario, baseSeed: 1337);

        Assert.That(agg1.DeathRate, Is.EqualTo(agg2.DeathRate));
        Assert.That(agg1.PlayerHitRate, Is.EqualTo(agg2.PlayerHitRate));
        Assert.That(agg1.MonsterHitRate, Is.EqualTo(agg2.MonsterHitRate));
        Assert.That(agg1.AvgTurns, Is.EqualTo(agg2.AvgTurns));
    }

    [Test]
    public void Depth2OrcBaseline_PlayerHitRate_InRange()
    {
        var agg = _harness.Run(Depth2OrcBaseline(), baseSeed: 1337);

        // Player: DEX 14 (mod +2) + dagger to-hit +1 = +3
        // vs Orc AC: 10 + DEX mod 0 = 10
        // d20 + 3 >= 10 → hits on 7+ = 70%, plus crits/fumbles
        Assert.That(agg.PlayerHitRate, Is.InRange(0.55, 0.85),
            $"Player hit rate {agg.PlayerHitRate:P1} outside expected range");
    }

    [Test]
    public void Depth2OrcBaseline_MonsterHitRate_InRange()
    {
        var agg = _harness.Run(Depth2OrcBaseline(), baseSeed: 1337);

        // Orc: DEX 10 (mod 0)
        // vs Player AC: 10 + DEX mod 2 + leather +2 = 14
        // d20 + 0 >= 14 → hits on 14+ = 35%, plus crits/fumbles
        Assert.That(agg.MonsterHitRate, Is.InRange(0.25, 0.50),
            $"Monster hit rate {agg.MonsterHitRate:P1} outside expected range");
    }

    [Test]
    public void Depth2OrcBaseline_DeathRate_HighWithoutHealingOrPositioning()
    {
        var agg = _harness.Run(Depth2OrcBaseline(), baseSeed: 1337);

        // Without healing potions and positioning, 3 orcs simultaneously
        // attacking is overwhelming. Death rate will be very high.
        // This will come down as we add: healing, positioning, smarter bot AI.
        // For now, just confirm the harness produces consistent, non-trivial results.
        Assert.That(agg.DeathRate, Is.InRange(0.5, 1.0),
            $"Death rate {agg.DeathRate:P1} — expected high without healing/positioning");
        Assert.That(agg.AvgMonstersKilled, Is.GreaterThanOrEqualTo(0.0));
    }

    [Test]
    public void Depth2_PlayerVsSingleOrc_Equipped_MostlyWins()
    {
        // 1v1 with dagger + leather armor — player should dominate
        var scenario = new ScenarioDefinition
        {
            ScenarioId = "depth2_1v1_equipped",
            Depth = 2, TurnLimit = 100, Runs = 50,
            Player = new ScenarioPlayer
            {
                Hp = 54, Strength = 12, Dexterity = 14, Constitution = 12,
                Accuracy = 2, Evasion = 1, DamageMin = 1, DamageMax = 4,
                Weapon = "dagger", Armor = "leather_armor",
            },
            Monsters = new() { new() { Type = "orc_grunt", Count = 1 } }
        };

        var agg = _harness.Run(scenario, baseSeed: 1337);

        // Player should win nearly all 1v1s with equipment advantage
        Assert.That(agg.DeathRate, Is.LessThan(0.15),
            $"Death rate {agg.DeathRate:P1} — equipped player should beat single orc");
        Assert.That(agg.AvgMonstersKilled, Is.GreaterThanOrEqualTo(0.85));
    }

    [Test]
    public void Depth2OrcBaseline_PrintMetrics()
    {
        var agg = _harness.Run(Depth2OrcBaseline(), baseSeed: 1337);

        TestContext.WriteLine($"=== Depth 2 Orc Baseline (seed 1337, {agg.TotalRuns} runs) ===");
        TestContext.WriteLine($"  Death Rate:       {agg.DeathRate:P1}");
        TestContext.WriteLine($"  Avg Turns:        {agg.AvgTurns:F1}");
        TestContext.WriteLine($"  Player Hit Rate:  {agg.PlayerHitRate:P1}");
        TestContext.WriteLine($"  Monster Hit Rate: {agg.MonsterHitRate:P1}");
        TestContext.WriteLine($"  Avg Player DMG:   {agg.AvgPlayerDamageDealt:F1}");
        TestContext.WriteLine($"  Avg Monster DMG:  {agg.AvgMonsterDamageDealt:F1}");
        TestContext.WriteLine($"  Avg Kills:        {agg.AvgMonstersKilled:F1}");

        Assert.Pass(); // informational test
    }
}
