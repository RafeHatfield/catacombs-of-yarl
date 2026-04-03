using YamlDotNet.Serialization;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Item category — determines identification behaviour at runtime.
/// Weapons/armor are always identified (Other). Consumables with secrets start hidden.
/// </summary>
public enum ItemCategory
{
    Other,
    Potion,
    Scroll,
    Wand,
    Ring,
}

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

    [YamlMember(Alias = "crit_threshold")]
    public int CritThreshold { get; set; } = 20;

    [YamlMember(Alias = "speed_bonus")]
    public double SpeedBonus { get; set; }

    [YamlMember(Alias = "char")]
    public string Char { get; set; } = "?";

    [YamlMember(Alias = "color")]
    public int[] Color { get; set; } = [255, 255, 255];

    /// <summary>
    /// Physical material. "metal" weapons can be corroded by slimes.
    /// "wood" and null are immune.
    /// </summary>
    [YamlMember(Alias = "material")]
    public string? Material { get; set; }

    /// <summary>
    /// Item category. Weapons/armor default to Other (always identified).
    /// Potions/scrolls/wands/rings start hidden and need identification.
    /// </summary>
    [YamlMember(Alias = "category")]
    public ItemCategory Category { get; set; } = ItemCategory.Other;

    /// <summary>
    /// Ring effect type string (e.g. "protection", "speed"). Null for non-ring items.
    /// Set by ContentLoader.LoadRings when converting RingDefinition to ItemDefinition.
    /// Read by ItemFactory to attach a RingEffectComponent.
    /// </summary>
    [YamlMember(Alias = "ring_effect")]
    public string? RingEffect { get; set; }

    /// <summary>
    /// Ring effect strength (e.g. 2 for +2 AC, 20 for 20% teleport chance).
    /// Only meaningful when RingEffect is non-null.
    /// </summary>
    [YamlMember(Alias = "effect_strength")]
    public int EffectStrength { get; set; }

    /// <summary>
    /// Speed bonus ratio for speed rings (e.g. 0.10 for ring_of_speed, 0.25 for ring_of_hummingbird).
    /// Stored as a double here because the YAML integer EffectStrength cannot carry sub-integer precision.
    /// Set by ContentLoader.LoadRings based on ring_effect type.
    /// </summary>
    public double RingSpeedRatio { get; set; }

    /// <summary>
    /// Human-readable display name. Defaults to Name if not set.
    /// Used as the IdentifiedName in the IdentifiableItem component.
    /// </summary>
    public string DisplayName => Name ?? "";
}
