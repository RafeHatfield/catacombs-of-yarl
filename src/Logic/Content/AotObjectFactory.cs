using System.Collections;
using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.ECS;
using YamlDotNet.Serialization;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Custom YamlDotNet object factory for NativeAOT compatibility.
///
/// NativeAOT trims Activator.CreateInstance(Type) calls that use reflection
/// to find parameterless constructors. YamlDotNet's DefaultObjectFactory
/// relies on this pattern, which fails on iOS (NativeAOT mandatory).
///
/// This factory explicitly maps every YAML-deserialized type to a direct
/// constructor call — no reflection needed, fully AOT-safe.
/// </summary>
public sealed class AotObjectFactory : IObjectFactory
{
    // Lookup from Type to factory function. Populated once, used on every deserialize.
    private static readonly Dictionary<Type, Func<object>> _factories = new()
    {
        // ECS components — not deserialized from YAML, but registered for NativeAOT safety
        // if any future serialization path needs to reconstruct them from saved state.
        [typeof(AiComponent)] = () => new AiComponent(),

        // Content layer
        [typeof(EntitiesFile)] = () => new EntitiesFile(),
        [typeof(MonsterDefinition)] = () => new MonsterDefinition(),
        [typeof(MonsterStats)] = () => new MonsterStats(),
        [typeof(MonsterEquipmentConfig)] = () => new MonsterEquipmentConfig(),
        [typeof(WeightedItem)] = () => new WeightedItem(),
        [typeof(ItemDefinition)] = () => new ItemDefinition(),
        [typeof(ConsumableDefinition)] = () => new ConsumableDefinition(),
        [typeof(SpellDefinition)] = () => new SpellDefinition(),
        [typeof(FloorItemPoolEntry)] = () => new FloorItemPoolEntry(),
        [typeof(FloorItemPoolFile)] = () => new FloorItemPoolFile(),
        [typeof(LevelTemplatesFile)] = () => new LevelTemplatesFile(),
        [typeof(DepthWeightEntry)] = () => new DepthWeightEntry(),

        // Balance layer
        [typeof(LevelOverride)] = () => new LevelOverride(),
        [typeof(GenerationParameters)] = () => new GenerationParameters(),
        [typeof(GuaranteedSpawns)] = () => new GuaranteedSpawns(),
        [typeof(SpawnEntry)] = () => new SpawnEntry(),
        [typeof(StairRules)] = () => new StairRules(),
        [typeof(SpawnRules)] = () => new SpawnRules(),
        [typeof(EncounterBudget)] = () => new EncounterBudget(),
        [typeof(SpecialRoomDef)] = () => new SpecialRoomDef(),
        [typeof(ScenarioDefinition)] = () => new ScenarioDefinition(),
        [typeof(ScenarioPlayer)] = () => new ScenarioPlayer(),
        [typeof(ScenarioMonster)] = () => new ScenarioMonster(),
        [typeof(ScenarioItem)] = () => new ScenarioItem(),

        // Standard library types YamlDotNet needs to create
        [typeof(Dictionary<string, MonsterDefinition>)] = () => new Dictionary<string, MonsterDefinition>(),
        [typeof(Dictionary<string, ItemDefinition>)] = () => new Dictionary<string, ItemDefinition>(),
        [typeof(Dictionary<string, ConsumableDefinition>)] = () => new Dictionary<string, ConsumableDefinition>(),
        [typeof(Dictionary<string, SpellDefinition>)] = () => new Dictionary<string, SpellDefinition>(),
        [typeof(Dictionary<string, LevelOverride>)] = () => new Dictionary<string, LevelOverride>(),
        // Nested dictionary types for top-level YAML parsing (avoids EntitiesFile wrapper)
        [typeof(Dictionary<string, Dictionary<string, MonsterDefinition>>)] = () => new Dictionary<string, Dictionary<string, MonsterDefinition>>(),
        [typeof(Dictionary<string, Dictionary<string, ItemDefinition>>)] = () => new Dictionary<string, Dictionary<string, ItemDefinition>>(),
        [typeof(Dictionary<string, Dictionary<string, ConsumableDefinition>>)] = () => new Dictionary<string, Dictionary<string, ConsumableDefinition>>(),
        [typeof(Dictionary<string, Dictionary<string, SpellDefinition>>)] = () => new Dictionary<string, Dictionary<string, SpellDefinition>>(),
        [typeof(Dictionary<string, string>)] = () => new Dictionary<string, string>(),
        [typeof(Dictionary<string, double>)] = () => new Dictionary<string, double>(),
        [typeof(List<string>)] = () => new List<string>(),
        [typeof(List<int>)] = () => new List<int>(),
        [typeof(List<SpawnEntry>)] = () => new List<SpawnEntry>(),
        [typeof(List<SpecialRoomDef>)] = () => new List<SpecialRoomDef>(),
        [typeof(List<ScenarioMonster>)] = () => new List<ScenarioMonster>(),
        [typeof(List<ScenarioItem>)] = () => new List<ScenarioItem>(),
        [typeof(List<WeightedItem>)] = () => new List<WeightedItem>(),
        [typeof(List<DepthWeightEntry>)] = () => new List<DepthWeightEntry>(),
        [typeof(List<FloorItemPoolEntry>)] = () => new List<FloorItemPoolEntry>(),
        [typeof(Dictionary<string, List<WeightedItem>>)] = () => new Dictionary<string, List<WeightedItem>>(),
        [typeof(Dictionary<string, double>)] = () => new Dictionary<string, double>(),
        [typeof(Dictionary<int, LevelOverride>)] = () => new Dictionary<int, LevelOverride>(),
        [typeof(List<double>)] = () => new List<double>(),
        [typeof(List<float>)] = () => new List<float>(),
        [typeof(int[])] = () => new int[0],
    };

    public object Create(Type type)
    {
        if (_factories.TryGetValue(type, out var factory))
            return factory();

        // Dynamic fallback for generic collection types we didn't pre-register.
        // NativeAOT can construct generic types if the concrete type arguments are preserved.
        // This handles Dictionary<string, List<T>>, List<T>, etc. without manual registration.
        try
        {
            return Activator.CreateInstance(type)!;
        }
        catch
        {
            // Log the missing type so we can add it to the factory for next time
            System.Diagnostics.Debug.WriteLine(
                $"AotObjectFactory: Activator.CreateInstance failed for {type.FullName}");
            throw new InvalidOperationException(
                $"AotObjectFactory: no factory registered for {type.FullName}. " +
                $"Add it to AotObjectFactory._factories for NativeAOT compatibility.");
        }
    }

    public object CreatePrimitive(Type type) => Create(type);

    public bool GetDictionary(IObjectDescriptor descriptor, out IDictionary? dictionary, out Type[]? genericArguments)
    {
        dictionary = null;
        genericArguments = null;
        return false;
    }

    public Type GetValueType(Type type) => typeof(object);

    public void ExecuteOnDeserialized(object value) { }
    public void ExecuteOnDeserializing(object value) { }
    public void ExecuteOnSerializing(object value) { }
    public void ExecuteOnSerialized(object value) { }
}
