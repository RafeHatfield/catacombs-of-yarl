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

    /// <summary>
    /// Minimum dungeon depth at which this monster can spawn procedurally.
    /// Defaults to 1 (appears from the first floor). Use min_depth: N in YAML to restrict.
    /// </summary>
    [YamlMember(Alias = "min_depth")]
    public int MinDepth { get; set; } = 1;

    /// <summary>
    /// Relative spawn weight for procedural placement. Higher = more common.
    /// 0 means the monster is not procedurally spawnable (only via guaranteed spawns).
    /// Nullable so that spawn_weight: 0 (explicitly zeroed) is distinguishable from an
    /// omitted field during ContentLoader.Merge — both previously deserialized as 0.
    /// </summary>
    [YamlMember(Alias = "spawn_weight")]
    public int? SpawnWeight { get; set; }

    [YamlMember(Alias = "speed_bonus")]
    public double SpeedBonus { get; set; }

    [YamlMember(Alias = "damage_resistance")]
    public string? DamageResistance { get; set; }

    [YamlMember(Alias = "damage_vulnerability")]
    public string? DamageVulnerability { get; set; }

    [YamlMember(Alias = "equipment")]
    public MonsterEquipmentConfig? Equipment { get; set; }

    [YamlMember(Alias = "can_seek_items")]
    public bool CanSeekItems { get; set; }

    [YamlMember(Alias = "seek_distance")]
    public int SeekDistance { get; set; } = 5;

    [YamlMember(Alias = "inventory_size")]
    public int InventorySize { get; set; }

    // ── Corrosion ────────────────────────────────────────────────────────────────

    /// <summary>
    /// Probability [0.0–1.0] of corroding the player's equipped metal weapon on each hit.
    /// 0 = no corrosion (default). Set on acidic monsters (slime, large_slime).
    /// </summary>
    [YamlMember(Alias = "corrosion_chance")]
    public double CorrosionChance { get; set; }

    // ── Split-under-pressure ─────────────────────────────────────────────────────

    /// <summary>
    /// HP fraction [0.0–1.0] below which the monster splits into children.
    /// Null = no split mechanic. E.g. 0.40 triggers when HP &lt; 40%.
    /// One-time-only — guarded by SplitTracker.HasSplit at runtime.
    /// </summary>
    [YamlMember(Alias = "split_trigger_hp_pct")]
    public double? SplitTriggerHpPct { get; set; }

    /// <summary>Monster type ID for spawned children (e.g. "slime").</summary>
    [YamlMember(Alias = "split_child_type")]
    public string? SplitChildType { get; set; }

    /// <summary>Minimum children to spawn on split.</summary>
    [YamlMember(Alias = "split_min_children")]
    public int SplitMinChildren { get; set; } = 2;

    /// <summary>Maximum children to spawn on split.</summary>
    [YamlMember(Alias = "split_max_children")]
    public int SplitMaxChildren { get; set; } = 3;

    /// <summary>
    /// Weighted distribution over [SplitMinChildren, SplitMaxChildren].
    /// Length must equal SplitMaxChildren - SplitMinChildren + 1.
    /// Null = uniform random in [min, max].
    /// </summary>
    [YamlMember(Alias = "split_weights")]
    public List<int>? SplitWeights { get; set; }

    /// <summary>
    /// Whether this monster leaves a raisable corpse on death.
    /// Defaults to true. Set false for slimes and other non-flesh monsters.
    /// When false, no CorpseComponent is added and no CorpseCreatedEvent is emitted.
    /// </summary>
    [YamlMember(Alias = "leaves_corpse")]
    public bool LeavesCorpse { get; set; } = true;

    // ── Regeneration ─────────────────────────────────────────────────────────────

    /// <summary>
    /// HP healed per turn (HOT). 0 = no regeneration.
    /// When non-zero, MonsterFactory attaches a RegenerationEffect with a very long duration.
    /// PoC field: regeneration_amount. Used by troll.
    /// </summary>
    [YamlMember(Alias = "regeneration_amount")]
    public int RegenerationAmount { get; set; }

    // ── On-hit status effects ────────────────────────────────────────────────────

    /// <summary>
    /// Status effect applied to the target on each successful melee hit.
    /// Null = no on-hit effect. Supported values: "poison", "slowed", "burning".
    /// </summary>
    [YamlMember(Alias = "on_hit_effect")]
    public string? OnHitEffect { get; set; }

    /// <summary>
    /// Duration in turns for the on-hit effect. Only meaningful when OnHitEffect is set.
    /// </summary>
    [YamlMember(Alias = "on_hit_effect_duration")]
    public int OnHitEffectDuration { get; set; }

    // ── Necromancer AI parameters ─────────────────────────────────────────────

    [YamlMember(Alias = "raise_dead_range")]
    public int RaiseDeadRange { get; set; } = 5;

    [YamlMember(Alias = "raise_dead_cooldown_turns")]
    public int RaiseDeadCooldownTurns { get; set; } = 4;

    [YamlMember(Alias = "danger_radius_from_player")]
    public int DangerRadiusFromPlayer { get; set; } = 2;

    [YamlMember(Alias = "preferred_distance_min")]
    public int PreferredDistanceMin { get; set; } = 4;

    [YamlMember(Alias = "preferred_distance_max")]
    public int PreferredDistanceMax { get; set; } = 7;

    /// <summary>
    /// Optional depth-progression table for spawn weight.
    /// If set, overrides SpawnWeight — weight is resolved per depth via SpawnUtils.FromDungeonLevel.
    /// Mirrors the from_dungeon_level pattern from PoC spawn_service.py.
    ///
    /// Note on min_depth + depth_weights: both can coexist. min_depth on the definition is a hard
    /// pre-filter gate (monster excluded from allDepthEligible before weight resolution).
    /// depth_weights handles the ramp. For monsters using depth_weights, set the definition's
    /// min_depth to match the first entry's min_depth — it's redundant but serves as documentation.
    /// </summary>
    [YamlMember(Alias = "depth_weights")]
    public List<DepthWeightEntry>? DepthWeights { get; set; }
}

/// <summary>
/// Equipment spawning configuration for a monster.
/// Defines per-slot spawn chances and weighted item pools.
/// </summary>
public sealed class MonsterEquipmentConfig
{
    [YamlMember(Alias = "spawn_chances")]
    public Dictionary<string, double> SpawnChances { get; set; } = new();

    [YamlMember(Alias = "equipment_pool")]
    public Dictionary<string, List<WeightedItem>> EquipmentPool { get; set; } = new();
}

public sealed class WeightedItem
{
    [YamlMember(Alias = "item")]
    public string Item { get; set; } = "";

    [YamlMember(Alias = "weight")]
    public int Weight { get; set; } = 1;
}

/// <summary>
/// One row of a depth-weight progression table.
/// YAML: depth_weights: [{weight: int, min_depth: int}]
/// Entries must be in ascending min_depth order — ContentLoader validates this.
/// </summary>
public sealed class DepthWeightEntry
{
    [YamlMember(Alias = "weight")]
    public int Weight { get; set; }

    [YamlMember(Alias = "min_depth")]
    public int MinDepth { get; set; } = 1;
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
