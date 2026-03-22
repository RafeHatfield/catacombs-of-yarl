using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Creates Entity instances from resolved MonsterDefinitions.
/// Bridges the content layer (YAML) to the ECS layer (entities + components).
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
    /// Returns null if the ID is not found.
    /// </summary>
    public Entity? Create(string monsterId, int x = 0, int y = 0)
    {
        if (!_definitions.TryGetValue(monsterId, out var def))
            return null;

        return CreateFromDefinition(def, x, y);
    }

    /// <summary>
    /// Create a monster entity directly from a definition.
    /// </summary>
    public Entity CreateFromDefinition(MonsterDefinition def, int x = 0, int y = 0)
    {
        var stats = def.Stats ?? new MonsterStats();
        string name = def.Name ?? monsterId(def);

        var entity = _entityFactory.Create(name, x, y, blocksMovement: def.Blocks);

        entity.Add(new Fighter(
            hp: stats.Hp,
            defense: stats.Defense,
            power: stats.Power,
            xp: stats.Xp,
            damageMin: stats.DamageMin,
            damageMax: stats.DamageMax,
            strength: stats.Strength,
            dexterity: stats.Dexterity,
            constitution: stats.Constitution,
            accuracy: stats.Accuracy,
            evasion: stats.Evasion));

        return entity;
    }

    /// <summary>All available monster IDs.</summary>
    public IEnumerable<string> AvailableIds => _definitions.Keys;

    // Fallback name derivation — should rarely be needed since ContentLoader resolves names
    private static string monsterId(MonsterDefinition def) => def.Char ?? "?";
}
