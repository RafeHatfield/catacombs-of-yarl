using CatacombsOfYarl.Logic.Content;
using NUnit.Framework;

namespace CatacombsOfYarl.Tests.Core;

/// <summary>
/// Validates that AotObjectFactory can create all YAML-mapped types.
/// Catches missing factory registrations before they hit iOS at runtime.
/// Run this after adding any new YAML content type.
/// </summary>
[TestFixture]
public class AotObjectFactoryTests
{
    private AotObjectFactory _factory = null!;

    [OneTimeSetUp]
    public void Setup() => _factory = new AotObjectFactory();

    // Content types
    [TestCase(typeof(EntitiesFile))]
    [TestCase(typeof(MonsterDefinition))]
    [TestCase(typeof(MonsterStats))]
    [TestCase(typeof(MonsterEquipmentConfig))]
    [TestCase(typeof(WeightedItem))]
    [TestCase(typeof(ItemDefinition))]
    [TestCase(typeof(ConsumableDefinition))]
    [TestCase(typeof(LevelTemplatesFile))]

    // Balance types
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.LevelOverride))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.GenerationParameters))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.GuaranteedSpawns))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.SpawnEntry))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.StairRules))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.SpawnRules))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.EncounterBudget))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.SpecialRoomDef))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.ScenarioDefinition))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.ScenarioPlayer))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.ScenarioMonster))]
    [TestCase(typeof(CatacombsOfYarl.Logic.Balance.ScenarioItem))]

    // Collection types used in YAML deserialization
    [TestCase(typeof(Dictionary<string, MonsterDefinition>))]
    [TestCase(typeof(Dictionary<string, ItemDefinition>))]
    [TestCase(typeof(Dictionary<string, ConsumableDefinition>))]
    [TestCase(typeof(Dictionary<string, CatacombsOfYarl.Logic.Balance.LevelOverride>))]
    [TestCase(typeof(Dictionary<string, Dictionary<string, MonsterDefinition>>))]
    [TestCase(typeof(Dictionary<string, Dictionary<string, ItemDefinition>>))]
    [TestCase(typeof(Dictionary<string, Dictionary<string, ConsumableDefinition>>))]
    [TestCase(typeof(Dictionary<string, List<WeightedItem>>))]
    [TestCase(typeof(List<CatacombsOfYarl.Logic.Balance.SpawnEntry>))]
    [TestCase(typeof(List<CatacombsOfYarl.Logic.Balance.SpecialRoomDef>))]
    [TestCase(typeof(List<CatacombsOfYarl.Logic.Balance.ScenarioMonster>))]
    [TestCase(typeof(List<CatacombsOfYarl.Logic.Balance.ScenarioItem>))]
    [TestCase(typeof(List<WeightedItem>))]
    [TestCase(typeof(List<string>))]
    [Description("AotObjectFactory can create all registered YAML-mapped types")]
    public void Create_RegisteredType_Succeeds(Type type)
    {
        var instance = _factory.Create(type);
        Assert.That(instance, Is.Not.Null, $"Factory returned null for {type.Name}");
        Assert.That(instance.GetType(), Is.EqualTo(type), $"Factory returned wrong type for {type.Name}");
    }
}
