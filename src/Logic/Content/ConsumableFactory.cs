using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
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

    /// <summary>All available consumable IDs.</summary>
    public IEnumerable<string> AvailableIds => _definitions.Keys;

    /// <summary>Look up a consumable definition by ID. Returns null if not found.</summary>
    public ConsumableDefinition? GetDefinition(string consumableId) =>
        _definitions.TryGetValue(consumableId, out var def) ? def : null;

    /// <summary>
    /// Create a consumable entity.
    ///
    /// registry/pool/rng/difficulty: optional identification system parameters.
    /// When provided, pre-identification is applied — the item's type is identified or
    /// kept hidden according to the per-run decision for that type.
    /// When null (scenario harness, tests), identification is skipped and items appear identified.
    ///
    /// Returns null if the ID is not found in definitions.
    /// </summary>
    public Entity? Create(string consumableId,
        IdentificationRegistry? registry = null,
        AppearancePool? pool = null,
        SeededRandom? rng = null,
        Difficulty difficulty = Difficulty.Medium)
    {
        if (!_definitions.TryGetValue(consumableId, out var def))
            return null;

        var entity = _entityFactory.Create(def.Name ?? consumableId);
        entity.Add(new Consumable(healAmount: def.HealAmount));

        // ItemTag carries the canonical YAML type ID — required for identification and stacking.
        entity.Add(new ItemTag(consumableId));

        // IdentifiableItem holds the two possible display names.
        // UnidentifiedName is filled by PreIdentification.Apply (or left empty in scenario mode).
        entity.Add(new IdentifiableItem
        {
            IdentifiedName   = def.DisplayName,
            UnidentifiedName = "",
        });

        // Apply pre-identification decision. No-op if registry/pool/rng are null.
        if (registry != null && pool != null && rng != null)
            PreIdentification.Apply(entity, consumableId, def.Category, registry, pool, rng, difficulty);

        return entity;
    }
}
