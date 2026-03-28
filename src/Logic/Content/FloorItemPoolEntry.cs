using YamlDotNet.Serialization;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// One entry in the floor_item_pool YAML section.
/// Defines an item that can appear as floor loot, with a relative spawn weight and minimum depth.
/// </summary>
public sealed class FloorItemPoolEntry
{
    [YamlMember(Alias = "item")]
    public string ItemId { get; set; } = "";

    [YamlMember(Alias = "weight")]
    public int Weight { get; set; } = 10;

    [YamlMember(Alias = "min_depth")]
    public int MinDepth { get; set; } = 1;
}
