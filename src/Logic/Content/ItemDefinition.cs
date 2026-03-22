using YamlDotNet.Serialization;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Deserialized item (weapon/armor) definition from YAML.
/// </summary>
public sealed class ItemDefinition
{
    [YamlMember(Alias = "name")]
    public string? Name { get; set; }

    [YamlMember(Alias = "slot")]
    public string Slot { get; set; } = "main_hand";

    [YamlMember(Alias = "damage_min")]
    public int DamageMin { get; set; }

    [YamlMember(Alias = "damage_max")]
    public int DamageMax { get; set; }

    [YamlMember(Alias = "to_hit_bonus")]
    public int ToHitBonus { get; set; }

    [YamlMember(Alias = "armor_class_bonus")]
    public int ArmorClassBonus { get; set; }

    [YamlMember(Alias = "damage_type")]
    public string? DamageType { get; set; }

    [YamlMember(Alias = "armor_type")]
    public string? ArmorType { get; set; }

    [YamlMember(Alias = "char")]
    public string Char { get; set; } = "?";

    [YamlMember(Alias = "color")]
    public int[] Color { get; set; } = [255, 255, 255];
}
