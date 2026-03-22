using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Creates consumable item entities from ConsumableDefinitions.
/// </summary>
public sealed class ConsumableFactory
{
    private readonly Dictionary<string, ConsumableDefinition> _definitions;
    private readonly EntityFactory _entityFactory;

    public ConsumableFactory(Dictionary<string, ConsumableDefinition> definitions, EntityFactory entityFactory)
    {
        _definitions = definitions;
        _entityFactory = entityFactory;
    }

    /// <summary>Create a consumable entity. Returns null if ID not found.</summary>
    public Entity? Create(string consumableId)
    {
        if (!_definitions.TryGetValue(consumableId, out var def))
            return null;

        var entity = _entityFactory.Create(def.Name ?? consumableId);
        entity.Add(new Consumable(healAmount: def.HealAmount));
        return entity;
    }
}
