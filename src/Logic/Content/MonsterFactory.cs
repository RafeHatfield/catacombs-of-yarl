using CatacombsOfYarl.Logic.Balance;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Creates Entity instances from resolved MonsterDefinitions.
/// Bridges the content layer (YAML) to the ECS layer (entities + components).
/// Applies depth scaling at spawn time when depth is specified.
/// </summary>
public sealed class MonsterFactory
{
    private readonly Dictionary<string, MonsterDefinition> _definitions;
    private readonly EntityFactory _entityFactory;

    public MonsterFactory(Dictionary<string, MonsterDefinition> definitions, EntityFactory entityFactory)
    {
        _definitions = definitions;
        _entityFactory = entityFactory;
    }

    /// <summary>
    /// Create a monster entity from a definition ID.
    /// Depth > 0 applies depth scaling to stats.
    /// Returns null if the ID is not found.
    /// </summary>
    public Entity? Create(string monsterId, int x = 0, int y = 0, int depth = 0)
    {
        if (!_definitions.TryGetValue(monsterId, out var def))
            return null;

        return CreateFromDefinition(def, x, y, depth);
    }

    /// <summary>
    /// Create a monster entity directly from a definition.
    /// </summary>
    public Entity CreateFromDefinition(MonsterDefinition def, int x = 0, int y = 0, int depth = 0)
    {
        var stats = def.Stats ?? new MonsterStats();
        string name = def.Name ?? FallbackName(def);

        var entity = _entityFactory.Create(name, x, y, blocksMovement: def.Blocks);

        int hp = stats.Hp;
        int damageMin = stats.DamageMin;
        int damageMax = stats.DamageMax;
        int accuracy = stats.Accuracy;

        // Apply depth scaling if depth specified
        if (depth > 0)
        {
            var mult = DepthScaling.GetForTags(depth, def.Tags);
            hp = DepthScaling.ScaleHp(hp, mult.Hp);
            damageMin = DepthScaling.ScaleStat(damageMin, mult.Damage);
            damageMax = DepthScaling.ScaleStat(damageMax, mult.Damage);
            accuracy = DepthScaling.ScaleStat(accuracy, mult.ToHit);
        }

        entity.Add(new Fighter(
            hp: hp,
            defense: stats.Defense,
            power: stats.Power,
            xp: stats.Xp,
            damageMin: damageMin,
            damageMax: damageMax,
            strength: stats.Strength,
            dexterity: stats.Dexterity,
            constitution: stats.Constitution,
            accuracy: accuracy,
            evasion: stats.Evasion));

        // Speed bonus for momentum system
        if (def.SpeedBonus > 0)
            entity.Add(new SpeedBonusTracker(baseRatio: def.SpeedBonus));

        return entity;
    }

    /// <summary>All available monster IDs.</summary>
    public IEnumerable<string> AvailableIds => _definitions.Keys;

    private static string FallbackName(MonsterDefinition def) => def.Char ?? "?";
}
