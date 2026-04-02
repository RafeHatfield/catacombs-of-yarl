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

    /// <summary>
    /// Item category. Potions are ItemCategory.Potion by default; override via YAML.
    /// </summary>
    [YamlMember(Alias = "category")]
    public ItemCategory Category { get; set; } = ItemCategory.Potion;

    /// <summary>
    /// Human-readable display name. Defaults to Name if not set.
    /// Used as the IdentifiedName in the IdentifiableItem component.
    /// </summary>
    public string DisplayName => Name ?? "";

    /// <summary>
    /// YAML key (e.g. "healing_potion"). Set by ContentLoader after deserialization.
    /// </summary>
    public string Id { get; set; } = "";
}
