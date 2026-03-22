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

consumables:
  healing_potion:
    name: ""Healing Potion""
    heal_amount: 40
    char: ""!""
    color: [127, 0, 255]
";
        var loader = new ContentLoader();
        var entityFactory = new EntityFactory();
        var monsters = loader.LoadMonsters(entitiesYaml);
        var items = loader.LoadItems(entitiesYaml);
        var consumables = loader.LoadConsumables(entitiesYaml);

        _harness = new ScenarioHarness(
            new MonsterFactory(monsters, entityFactory),
            new ItemFactory(items, entityFactory),
            new ConsumableFactory(consumables, entityFactory));
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
    public void Depth2OrcBaseline_DeathRate_ReasonableWithPositioning()
    {
        var agg = _harness.Run(Depth2OrcBaseline(), baseSeed: 1337);

        // With positioning (player at x=3, orcs at x=8+), the player engages
        // orcs sequentially rather than all at once. Death rate should be low.
        // Depth 2 target band: 0-8% (from pressure model). Without healing,
        // expect slightly higher but much better than the 100% melee brawl.
        Assert.That(agg.DeathRate, Is.InRange(0.0, 0.40),
            $"Death rate {agg.DeathRate:P1} — positioning should keep this manageable");
        Assert.That(agg.AvgMonstersKilled, Is.GreaterThan(0.5));
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

    private static ScenarioDefinition Depth2WithHealing() => new()
    {
        ScenarioId = "depth2_orc_healing",
        Name = "Depth 2 - Orc Baseline with Healing",
        Depth = 2, TurnLimit = 100, Runs = 50,
        Player = new ScenarioPlayer
        {
            Hp = 54, Strength = 12, Dexterity = 14, Constitution = 12,
            Accuracy = 2, Evasion = 1, DamageMin = 1, DamageMax = 4,
            Weapon = "dagger", Armor = "leather_armor",
        },
        Monsters = new() { new() { Type = "orc_grunt", Count = 3 } },
        Items = new() { new() { Type = "healing_potion", Count = 1 } },
    };

    private static ScenarioDefinition Depth2_TwoOrcs_WithHealing() => new()
    {
        ScenarioId = "depth2_2orc_healing",
        Depth = 2, TurnLimit = 100, Runs = 50,
        Player = new ScenarioPlayer
        {
            Hp = 54, Strength = 12, Dexterity = 14, Constitution = 12,
            Accuracy = 2, Evasion = 1, DamageMin = 1, DamageMax = 4,
            Weapon = "dagger", Armor = "leather_armor",
        },
        Monsters = new() { new() { Type = "orc_grunt", Count = 2 } },
        Items = new() { new() { Type = "healing_potion", Count = 1 } },
    };

    private static ScenarioDefinition Depth2_TwoOrcs_NoHealing() => new()
    {
        ScenarioId = "depth2_2orc_no_heal",
        Depth = 2, TurnLimit = 100, Runs = 50,
        Player = new ScenarioPlayer
        {
            Hp = 54, Strength = 12, Dexterity = 14, Constitution = 12,
            Accuracy = 2, Evasion = 1, DamageMin = 1, DamageMax = 4,
            Weapon = "dagger", Armor = "leather_armor",
        },
        Monsters = new() { new() { Type = "orc_grunt", Count = 2 } },
    };

    [Test]
    public void Depth2_TwoOrcs_HealingReducesDeathRate()
    {
        var noHeal = _harness.Run(Depth2_TwoOrcs_NoHealing(), baseSeed: 1337);
        var heal = _harness.Run(Depth2_TwoOrcs_WithHealing(), baseSeed: 1337);

        // 2 orcs is survivable — healing should meaningfully reduce death rate
        Assert.That(heal.DeathRate, Is.LessThan(noHeal.DeathRate),
            $"With healing: {heal.DeathRate:P1}, Without: {noHeal.DeathRate:P1}");
    }

    [Test]
    public void Depth2_TwoOrcs_HealingIncreasesKills()
    {
        var noHeal = _harness.Run(Depth2_TwoOrcs_NoHealing(), baseSeed: 1337);
        var heal = _harness.Run(Depth2_TwoOrcs_WithHealing(), baseSeed: 1337);

        Assert.That(heal.AvgMonstersKilled, Is.GreaterThanOrEqualTo(noHeal.AvgMonstersKilled),
            $"With healing kills: {heal.AvgMonstersKilled:F1}, Without: {noHeal.AvgMonstersKilled:F1}");
    }

    [Test]
    public void Depth2_PrintMetrics_WithAndWithoutHealing()
    {
        var noHeal = _harness.Run(Depth2OrcBaseline(), baseSeed: 1337);
        var heal = _harness.Run(Depth2WithHealing(), baseSeed: 1337);

        TestContext.WriteLine("=== Depth 2 Orc Baseline — A/B Healing Comparison (seed 1337) ===");
        TestContext.WriteLine("");
        PrintRow("Metric", "No Healing", "1 Potion");
        PrintRow("Death Rate", $"{noHeal.DeathRate:P1}", $"{heal.DeathRate:P1}");
        PrintRow("Avg Turns", $"{noHeal.AvgTurns:F1}", $"{heal.AvgTurns:F1}");
        PrintRow("Player Hit Rate", $"{noHeal.PlayerHitRate:P1}", $"{heal.PlayerHitRate:P1}");
        PrintRow("Monster Hit Rate", $"{noHeal.MonsterHitRate:P1}", $"{heal.MonsterHitRate:P1}");
        PrintRow("Avg Player DMG", $"{noHeal.AvgPlayerDamageDealt:F1}", $"{heal.AvgPlayerDamageDealt:F1}");
        PrintRow("Avg Monster DMG", $"{noHeal.AvgMonsterDamageDealt:F1}", $"{heal.AvgMonsterDamageDealt:F1}");
        PrintRow("Avg Kills", $"{noHeal.AvgMonstersKilled:F1}", $"{heal.AvgMonstersKilled:F1}");

        Assert.Pass();
    }

    private static void PrintRow(string label, string col1, string col2)
    {
        TestContext.WriteLine(string.Format("  {0,-22} {1,12} {2,12}", label, col1, col2));
    }
}
