using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat;

/// <summary>
/// Makes an entity usable as a consumable item (potions, scrolls).
/// Consumed on use — removed from inventory after application.
/// StackSize tracks how many copies of this consumable are represented by a single
/// inventory entity. When StackSize > 1, using the item decrements the count rather
/// than removing the entity from inventory.
/// </summary>
public sealed class Consumable : IComponent
{
    public Entity? Owner { get; set; }

    /// <summary>HP restored on use. 0 for non-healing consumables.</summary>
    public int HealAmount { get; set; }

    /// <summary>
    /// How many of this consumable are stacked on this entity. Runtime-only — not
    /// persisted to YAML. Always >= 1.
    /// </summary>
    public int StackSize { get; set; } = 1;

    /// <summary>
    /// True for potions — bypasses the SilencedEffect gate in ResolveSpellAction.
    /// False for scrolls (default). Drinking a potion while silenced is permitted
    /// because potions are physical (swallowed), not magic (spoken).
    /// </summary>
    public bool IsPotion { get; set; }

    public Consumable(int healAmount = 0, bool isPotion = false)
    {
        HealAmount = healAmount;
        IsPotion = isPotion;
    }

    public bool IsHealing => HealAmount > 0;
}
