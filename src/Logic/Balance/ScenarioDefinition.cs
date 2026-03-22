using YamlDotNet.Serialization;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// YAML-deserialized scenario definition. Defines a controlled combat encounter
/// for harness testing — no worldgen, no RNG beyond the seeded combat rolls.
/// </summary>
public sealed class ScenarioDefinition
{
    [YamlMember(Alias = "scenario_id")]
    public string ScenarioId { get; set; } = "";

    [YamlMember(Alias = "name")]
    public string Name { get; set; } = "";

    [YamlMember(Alias = "depth")]
    public int Depth { get; set; } = 1;

    [YamlMember(Alias = "turn_limit")]
    public int TurnLimit { get; set; } = 100;

    [YamlMember(Alias = "runs")]
    public int Runs { get; set; } = 40;

    [YamlMember(Alias = "player")]
    public ScenarioPlayer Player { get; set; } = new();

    [YamlMember(Alias = "monsters")]
    public List<ScenarioMonster> Monsters { get; set; } = new();

    [YamlMember(Alias = "items")]
    public List<ScenarioItem> Items { get; set; } = new();
}

public sealed class ScenarioPlayer
{
    [YamlMember(Alias = "hp")]
    public int Hp { get; set; } = 54;

    [YamlMember(Alias = "strength")]
    public int Strength { get; set; } = 12;

    [YamlMember(Alias = "dexterity")]
    public int Dexterity { get; set; } = 14;

    [YamlMember(Alias = "constitution")]
    public int Constitution { get; set; } = 12;

    [YamlMember(Alias = "accuracy")]
    public int Accuracy { get; set; } = 2;

    [YamlMember(Alias = "evasion")]
    public int Evasion { get; set; } = 1;

    [YamlMember(Alias = "damage_min")]
    public int DamageMin { get; set; } = 1;

    [YamlMember(Alias = "damage_max")]
    public int DamageMax { get; set; } = 4;

    [YamlMember(Alias = "weapon")]
    public string? Weapon { get; set; }

    [YamlMember(Alias = "armor")]
    public string? Armor { get; set; }

    [YamlMember(Alias = "speed_bonus")]
    public double SpeedBonus { get; set; }
}

public sealed class ScenarioMonster
{
    [YamlMember(Alias = "type")]
    public string Type { get; set; } = "";

    [YamlMember(Alias = "count")]
    public int Count { get; set; } = 1;
}

public sealed class ScenarioItem
{
    [YamlMember(Alias = "type")]
    public string Type { get; set; } = "";

    [YamlMember(Alias = "count")]
    public int Count { get; set; } = 1;
}
