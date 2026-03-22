using YamlDotNet.Serialization;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Deserialized consumable item definition from YAML.
/// </summary>
public sealed class ConsumableDefinition
{
    [YamlMember(Alias = "name")]
    public string? Name { get; set; }

    [YamlMember(Alias = "heal_amount")]
    public int HealAmount { get; set; }

    [YamlMember(Alias = "char")]
    public string Char { get; set; } = "!";

    [YamlMember(Alias = "color")]
    public int[] Color { get; set; } = [255, 255, 255];
}
