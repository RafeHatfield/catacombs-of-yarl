using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Content;

/// <summary>
/// Creates scroll and wand entities from SpellDefinitions.
///
/// Scrolls:  Consumable (stack=1, healAmount=0) + SpellEffect
/// Wands:    WandComponent (random charges from def range) + SpellEffect
///
/// Entity names match definition names (e.g., "Scroll of Lightning").
/// </summary>
public sealed class SpellItemFactory
{
    private readonly Dictionary<string, SpellDefinition> _definitions;
    private readonly EntityFactory _entityFactory;

    public SpellItemFactory(Dictionary<string, SpellDefinition> definitions, EntityFactory entityFactory)
    {
        _definitions = definitions;
        _entityFactory = entityFactory;
    }

    /// <summary>All spell/wand definition IDs available in this factory.</summary>
    public IEnumerable<string> AvailableIds => _definitions.Keys;

    /// <summary>
    /// Create a scroll entity from a definition ID.
    /// Returns null if the ID is unknown or the definition is marked is_wand=true.
    /// </summary>
    public Entity? CreateScroll(string spellId)
    {
        if (!_definitions.TryGetValue(spellId, out var def))
            return null;

        if (def.IsWand)
            return null; // Use CreateWand for wand definitions

        var entity = _entityFactory.Create(def.Name ?? spellId);

        // Consumable with HealAmount=0 — scrolls are consumed on use but don't heal.
        entity.Add(new Consumable(healAmount: 0));

        entity.Add(new SpellEffect
        {
            SpellId      = def.SpellId,
            Targeting    = def.ParseTargetingMode(),
            Damage       = def.Damage,
            Radius       = def.Radius,
            Range        = def.Range,
            Duration     = def.Duration,
            MisfireChance = def.MisfireChance,
        });

        return entity;
    }

    /// <summary>
    /// Create a wand entity from a definition ID.
    /// Charges are randomly selected from [def.MinCharges, def.MaxCharges] using the provided rng,
    /// then scaled by depth: charges += (depth - 1), capped at def.ChargeCap.
    /// PoC formula: rand(min_charges, max_charges) + (depth - 1), capped at charge_cap.
    /// Returns null if the ID is unknown or the definition is NOT marked is_wand=true.
    /// </summary>
    public Entity? CreateWand(string spellId, SeededRandom rng, int depth = 1)
    {
        if (!_definitions.TryGetValue(spellId, out var def))
            return null;

        if (!def.IsWand)
            return null; // Use CreateScroll for scroll definitions

        var entity = _entityFactory.Create(def.Name ?? spellId);

        int charges = def.Infinite ? 0
            : Math.Min(rng.Next(def.MinCharges, def.MaxCharges + 1) + (depth - 1), def.ChargeCap);

        entity.Add(new WandComponent
        {
            Charges         = charges,
            MaxCharges      = def.ChargeCap,
            Infinite        = def.Infinite,
            RechargeScrollId = def.RechargeScroll,
        });

        entity.Add(new SpellEffect
        {
            SpellId      = def.SpellId,
            Targeting    = def.ParseTargetingMode(),
            Damage       = def.Damage,
            Radius       = def.Radius,
            Range        = def.Range,
            Duration     = def.Duration,
            MisfireChance = def.MisfireChance,
        });

        return entity;
    }
}
