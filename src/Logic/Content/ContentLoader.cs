using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Root YAML structure for entities file.
/// </summary>
public sealed class EntitiesFile
{
    [YamlMember(Alias = "monsters")]
    public Dictionary<string, MonsterDefinition> Monsters { get; set; } = new();

    [YamlMember(Alias = "weapons")]
    public Dictionary<string, ItemDefinition> Weapons { get; set; } = new();

    [YamlMember(Alias = "armor")]
    public Dictionary<string, ItemDefinition> Armor { get; set; } = new();

    [YamlMember(Alias = "consumables")]
    public Dictionary<string, ConsumableDefinition> Consumables { get; set; } = new();
}

/// <summary>
/// Loads YAML content files and resolves inheritance.
/// Single source of truth for content loading — all YAML goes through here.
/// </summary>
public sealed class ContentLoader
{
    private readonly IDeserializer _deserializer;

    public ContentLoader()
    {
        _deserializer = new DeserializerBuilder()
            .WithNamingConvention(UnderscoredNamingConvention.Instance)
            .IgnoreUnmatchedProperties()
            .WithObjectFactory(new AotObjectFactory())
            .Build();
    }

    /// <summary>
    /// Load monster definitions from a YAML string. Resolves inheritance.
    /// Returns a dictionary of monster ID → resolved MonsterDefinition.
    /// </summary>
    public Dictionary<string, MonsterDefinition> LoadMonsters(string yaml)
    {
        // Deserialize to a generic dictionary tree instead of EntitiesFile.
        // NativeAOT trims PropertyInfo.SetValue which prevents YamlDotNet from
        // populating typed wrapper classes. Deserializing directly to the section
        // we need avoids the property-setter reflection entirely.
        var root = _deserializer.Deserialize<Dictionary<string, Dictionary<string, MonsterDefinition>>>(yaml);
        if (root == null || !root.TryGetValue("monsters", out var monsters) || monsters.Count == 0)
            return new Dictionary<string, MonsterDefinition>();

        return ResolveInheritance(monsters);
    }

    /// <summary>
    /// Load monster definitions from a YAML file path.
    /// </summary>
    public Dictionary<string, MonsterDefinition> LoadMonstersFromFile(string path)
    {
        string yaml = File.ReadAllText(path);
        return LoadMonsters(yaml);
    }

    /// <summary>
    /// Load item definitions (weapons + armor) from a YAML string.
    /// Returns a combined dictionary of item ID to ItemDefinition.
    /// </summary>
    public Dictionary<string, ItemDefinition> LoadItems(string yaml)
    {
        var root = _deserializer.Deserialize<Dictionary<string, Dictionary<string, ItemDefinition>>>(yaml);
        var items = new Dictionary<string, ItemDefinition>();

        if (root != null && root.TryGetValue("weapons", out var weapons))
        {
            foreach (var (id, def) in weapons)
            {
                def.Name ??= TitleCase(id);
                items[id] = def;
            }
        }

        if (root != null && root.TryGetValue("armor", out var armor))
        {
            foreach (var (id, def) in armor)
            {
                def.Name ??= TitleCase(id);
                items[id] = def;
            }
        }

        return items;
    }

    /// <summary>
    /// Load consumable definitions from a YAML string.
    /// </summary>
    public Dictionary<string, ConsumableDefinition> LoadConsumables(string yaml)
    {
        var root = _deserializer.Deserialize<Dictionary<string, Dictionary<string, ConsumableDefinition>>>(yaml);
        var consumables = new Dictionary<string, ConsumableDefinition>();

        if (root != null && root.TryGetValue("consumables", out var section))
        {
            foreach (var (id, def) in section)
            {
                def.Name ??= TitleCase(id);
                consumables[id] = def;
            }
        }

        return consumables;
    }

    /// <summary>
    /// Load a scenario definition from a YAML string.
    /// </summary>
    public Balance.ScenarioDefinition LoadScenario(string yaml)
    {
        return _deserializer.Deserialize<Balance.ScenarioDefinition>(yaml);
    }

    /// <summary>
    /// Load a scenario definition from a YAML file path.
    /// </summary>
    public Balance.ScenarioDefinition LoadScenarioFromFile(string path)
    {
        return LoadScenario(File.ReadAllText(path));
    }

    /// <summary>
    /// Load all content from a single entities YAML string.
    /// Returns monsters, items, and consumables in one call.
    /// </summary>
    public ContentBundle LoadAll(string yaml)
    {
        return new ContentBundle
        {
            Monsters = LoadMonsters(yaml),
            Items = LoadItems(yaml),
            Consumables = LoadConsumables(yaml),
        };
    }

    /// <summary>
    /// Load all content from a YAML file path.
    /// </summary>
    public ContentBundle LoadAllFromFile(string path)
    {
        return LoadAll(File.ReadAllText(path));
    }

    /// <summary>
    /// Resolve `extends` inheritance. Parent fields are deep-merged into children.
    /// Child values override parent values. Stats are merged field-by-field.
    /// </summary>
    private static Dictionary<string, MonsterDefinition> ResolveInheritance(
        Dictionary<string, MonsterDefinition> raw)
    {
        var resolved = new Dictionary<string, MonsterDefinition>();
        var resolving = new HashSet<string>();

        void Resolve(string id)
        {
            if (resolved.ContainsKey(id)) return;
            if (!raw.TryGetValue(id, out var def))
                throw new InvalidOperationException($"Unknown monster '{id}' referenced in inheritance.");
            if (resolving.Contains(id))
                throw new InvalidOperationException($"Circular inheritance detected for monster '{id}'.");

            if (string.IsNullOrEmpty(def.Extends))
            {
                resolved[id] = def;
                return;
            }

            resolving.Add(id);
            string parentId = def.Extends;
            Resolve(parentId);
            var parent = resolved[parentId];

            resolved[id] = Merge(parent, def, id);
            resolving.Remove(id);
        }

        foreach (var id in raw.Keys)
            Resolve(id);

        return resolved;
    }

    /// <summary>
    /// Merge parent definition into child. Child values win.
    /// Stats are merged field-by-field (child stats override individual fields, not the whole block).
    /// </summary>
    private static MonsterDefinition Merge(MonsterDefinition parent, MonsterDefinition child, string id)
    {
        var mergedStats = MergeStats(parent.Stats, child.Stats);

        return new MonsterDefinition
        {
            Name = child.Name ?? parent.Name ?? TitleCase(id),
            Extends = null, // resolved
            Stats = mergedStats,
            Char = child.Char != "?" ? child.Char : parent.Char,
            Color = child.Color is [255, 255, 255] ? parent.Color : child.Color,
            AiType = child.AiType != "basic" || parent.AiType == "basic" ? child.AiType : parent.AiType,
            RenderOrder = child.RenderOrder,
            Blocks = child.Blocks,
            Faction = child.Faction != "neutral" ? child.Faction : parent.Faction,
            Tags = child.Tags ?? parent.Tags,
            EtpBase = child.EtpBase != 0 ? child.EtpBase : parent.EtpBase,
            MinDepth = child.MinDepth != 1 ? child.MinDepth : parent.MinDepth,
            SpeedBonus = child.SpeedBonus != 0 ? child.SpeedBonus : parent.SpeedBonus,
            DamageResistance = child.DamageResistance ?? parent.DamageResistance,
            DamageVulnerability = child.DamageVulnerability ?? parent.DamageVulnerability,
            Equipment = child.Equipment ?? parent.Equipment,
            // Item-seeking behavior: child's true always wins; inherit parent's true if child didn't set it.
            // This matches PoC convention where non-seeking monsters explicitly set can_seek_items: false.
            CanSeekItems = child.CanSeekItems || parent.CanSeekItems,
            SeekDistance = child.SeekDistance != 5 ? child.SeekDistance : parent.SeekDistance,
            InventorySize = child.InventorySize != 0 ? child.InventorySize : parent.InventorySize,
        };
    }

    private static MonsterStats MergeStats(MonsterStats? parent, MonsterStats? child)
    {
        if (parent == null) return child ?? new MonsterStats();
        if (child == null) return parent;

        return new MonsterStats
        {
            Hp = child.Hp != 0 ? child.Hp : parent.Hp,
            Power = child.Power != 0 ? child.Power : parent.Power,
            Defense = child.Defense != 0 ? child.Defense : parent.Defense,
            Xp = child.Xp != 0 ? child.Xp : parent.Xp,
            DamageMin = child.DamageMin != 0 ? child.DamageMin : parent.DamageMin,
            DamageMax = child.DamageMax != 0 ? child.DamageMax : parent.DamageMax,
            Strength = child.Strength != 10 ? child.Strength : parent.Strength,
            Dexterity = child.Dexterity != 10 ? child.Dexterity : parent.Dexterity,
            Constitution = child.Constitution != 10 ? child.Constitution : parent.Constitution,
            Accuracy = child.Accuracy != Combat.HitModel.DefaultAccuracy ? child.Accuracy : parent.Accuracy,
            Evasion = child.Evasion != Combat.HitModel.DefaultEvasion ? child.Evasion : parent.Evasion,
        };
    }

    private static string TitleCase(string id)
    {
        return string.Join(' ', id.Split('_').Select(w =>
            w.Length > 0 ? char.ToUpper(w[0]) + w[1..] : w));
    }
}
