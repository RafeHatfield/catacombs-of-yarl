using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Creates item entities from ItemDefinitions.
/// </summary>
public sealed class ItemFactory
{
    private readonly Dictionary<string, ItemDefinition> _definitions;
    private readonly EntityFactory _entityFactory;

    public ItemFactory(Dictionary<string, ItemDefinition> definitions, EntityFactory entityFactory)
    {
        _definitions = definitions;
        _entityFactory = entityFactory;
    }

    /// <summary>Create an item entity. Returns null if ID not found.</summary>
    public Entity? Create(string itemId)
    {
        if (!_definitions.TryGetValue(itemId, out var def))
            return null;

        var slot = ParseSlot(def.Slot);
        var entity = _entityFactory.Create(def.Name ?? itemId);

        entity.Add(new Equippable(slot)
        {
            DamageMin = def.DamageMin,
            DamageMax = def.DamageMax,
            ToHitBonus = def.ToHitBonus,
            ArmorClassBonus = def.ArmorClassBonus,
            DamageType = def.DamageType,
            ArmorType = def.ArmorType,
        });

        return entity;
    }

    private static EquipmentSlot ParseSlot(string slot) => slot switch
    {
        "main_hand" => EquipmentSlot.MainHand,
        "off_hand" => EquipmentSlot.OffHand,
        "head" => EquipmentSlot.Head,
        "chest" => EquipmentSlot.Chest,
        "feet" => EquipmentSlot.Feet,
        _ => EquipmentSlot.MainHand,
    };
}
