using YamlDotNet.Serialization;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Deserialized monster definition from YAML. Matches the config/entities.yaml format.
/// Fields use YamlMember to map snake_case YAML keys to PascalCase C# properties.
/// </summary>
public sealed class MonsterDefinition
{
    [YamlMember(Alias = "name")]
    public string? Name { get; set; }

    [YamlMember(Alias = "extends")]
    public string? Extends { get; set; }

    [YamlMember(Alias = "stats")]
    public MonsterStats? Stats { get; set; }

    [YamlMember(Alias = "char")]
    public string Char { get; set; } = "?";

    [YamlMember(Alias = "color")]
    public int[] Color { get; set; } = [255, 255, 255];

    [YamlMember(Alias = "ai_type")]
    public string AiType { get; set; } = "basic";

    [YamlMember(Alias = "render_order")]
    public string RenderOrder { get; set; } = "actor";

    [YamlMember(Alias = "blocks")]
    public bool Blocks { get; set; } = true;

    [YamlMember(Alias = "faction")]
    public string Faction { get; set; } = "neutral";

    [YamlMember(Alias = "tags")]
    public List<string>? Tags { get; set; }

    [YamlMember(Alias = "etp_base")]
    public int EtpBase { get; set; }

    [YamlMember(Alias = "speed_bonus")]
    public double SpeedBonus { get; set; }

    [YamlMember(Alias = "damage_resistance")]
    public string? DamageResistance { get; set; }

    [YamlMember(Alias = "damage_vulnerability")]
    public string? DamageVulnerability { get; set; }
}

/// <summary>
/// Nested stats block within a monster definition.
/// </summary>
public sealed class MonsterStats
{
    [YamlMember(Alias = "hp")]
    public int Hp { get; set; }

    [YamlMember(Alias = "power")]
    public int Power { get; set; }

    [YamlMember(Alias = "defense")]
    public int Defense { get; set; }

    [YamlMember(Alias = "xp")]
    public int Xp { get; set; }

    [YamlMember(Alias = "damage_min")]
    public int DamageMin { get; set; }

    [YamlMember(Alias = "damage_max")]
    public int DamageMax { get; set; }

    [YamlMember(Alias = "strength")]
    public int Strength { get; set; } = 10;

    [YamlMember(Alias = "dexterity")]
    public int Dexterity { get; set; } = 10;

    [YamlMember(Alias = "constitution")]
    public int Constitution { get; set; } = 10;

    [YamlMember(Alias = "accuracy")]
    public int Accuracy { get; set; } = Combat.HitModel.DefaultAccuracy;

    [YamlMember(Alias = "evasion")]
    public int Evasion { get; set; } = Combat.HitModel.DefaultEvasion;
}
