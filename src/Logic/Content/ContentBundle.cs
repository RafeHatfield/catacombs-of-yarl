namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// All content loaded from an entities YAML file.
/// </summary>
public sealed class ContentBundle
{
    public Dictionary<string, MonsterDefinition> Monsters { get; init; } = new();
    public Dictionary<string, ItemDefinition> Items { get; init; } = new();
    public Dictionary<string, ConsumableDefinition> Consumables { get; init; } = new();
    public IReadOnlyList<FloorItemPoolEntry> FloorItemPool { get; init; } = [];
}
