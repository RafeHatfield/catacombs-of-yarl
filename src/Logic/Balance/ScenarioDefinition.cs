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

    [YamlMember(Alias = "description")]
    public string Description { get; set; } = "";

    [YamlMember(Alias = "depth")]
    public int Depth { get; set; } = 1;

    [YamlMember(Alias = "turn_limit")]
    public int TurnLimit { get; set; } = 100;

    [YamlMember(Alias = "runs")]
    public int Runs { get; set; } = 40;

    [YamlMember(Alias = "map_width")]
    public int MapWidth { get; set; } = 12;

    [YamlMember(Alias = "map_height")]
    public int MapHeight { get; set; } = 12;

    [YamlMember(Alias = "player_start_x")]
    public int PlayerStartX { get; set; } = 3;

    [YamlMember(Alias = "player_start_y")]
    public int PlayerStartY { get; set; } = 6;

    [YamlMember(Alias = "player")]
    public ScenarioPlayer Player { get; set; } = new();

    [YamlMember(Alias = "monsters")]
    public List<ScenarioMonster> Monsters { get; set; } = new();

    [YamlMember(Alias = "items")]
    public List<ScenarioItem> Items { get; set; } = new();

    /// <summary>
    /// When true, this scenario routes through DungeonFloorBuilder instead of
    /// GameStateFactory.FromScenario. The player is constructed via CreateDefaultPlayer()
    /// and the floor is procedurally generated with GuaranteedSpawns injected.
    /// Defaults to false — all existing scenarios are backward compatible.
    /// </summary>
    [YamlMember(Alias = "dungeon_mode")]
    public bool DungeonMode { get; set; } = false;

    /// <summary>
    /// Guaranteed spawns injected into the procedural floor when DungeonMode=true.
    /// Reuses GuaranteedSpawns from LevelOverride so the same YAML schema applies.
    /// Null when DungeonMode=false (normal scenario path).
    /// </summary>
    [YamlMember(Alias = "guaranteed_spawns")]
    public GuaranteedSpawns? GuaranteedSpawns { get; set; }

    /// <summary>
    /// When true, this scenario is an affix/gear probe — designed to isolate weapon advantage,
    /// not to hit a death rate target. Probes are reported as PROBE (not PASS/FAIL) in the
    /// harness table and excluded from the pass/fail count. H_PM/H_MP are still checked.
    /// </summary>
    [YamlMember(Alias = "is_probe")]
    public bool IsProbe { get; set; } = false;
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

    /// <summary>
    /// Quiver item type to pre-equip (e.g. "net_arrow", "fire_arrow").
    /// When set, GameStateFactory equips this item in EquipmentSlot.Quiver at scenario start.
    /// Null = no special ammo (normal arrows, infinite).
    /// </summary>
    [YamlMember(Alias = "quiver")]
    public string? Quiver { get; set; }

    /// <summary>
    /// Bot policy for this scenario. "tactical_fighter" (default) uses BotBrain.
    /// "ranged_net_arrow" uses RangedNetArrowBot for kiting behavior.
    /// Dispatched in ScenarioHarness.RunOnce.
    /// </summary>
    [YamlMember(Alias = "player_bot")]
    public string? PlayerBot { get; set; }

    /// <summary>
    /// Base speed bonus ratio for the player. PoC default is 0.25 — always active,
    /// independent of equipment. Equipment speed adds on top via EquipmentRatio.
    /// </summary>
    [YamlMember(Alias = "speed_bonus")]
    public double SpeedBonus { get; set; } = 0.25;
}

public sealed class ScenarioMonster
{
    [YamlMember(Alias = "type")]
    public string Type { get; set; } = "";

    [YamlMember(Alias = "count")]
    public int Count { get; set; } = 1;

    /// <summary>
    /// Optional exact placement [x, y]. When set, overrides the default offset grid placement.
    /// Null = use existing offset logic (backward compatible).
    /// </summary>
    [YamlMember(Alias = "position")]
    public int[]? Position { get; set; }

    /// <summary>
    /// Monster awareness state. "aware" / "unaware". Stub — parsed but not yet processed.
    /// Future AI milestone will use this to set initial detection state.
    /// </summary>
    [YamlMember(Alias = "state")]
    public string? State { get; set; }
}

public sealed class ScenarioItem
{
    [YamlMember(Alias = "type")]
    public string Type { get; set; } = "";

    [YamlMember(Alias = "count")]
    public int Count { get; set; } = 1;

    /// <summary>
    /// Optional exact placement [x, y]. When set, overrides random placement.
    /// Null = random placement (existing behavior, backward compatible).
    /// </summary>
    [YamlMember(Alias = "position")]
    public int[]? Position { get; set; }
}
