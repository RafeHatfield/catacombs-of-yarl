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

    public Consumable(int healAmount = 0)
    {
        HealAmount = healAmount;
    }

    public bool IsHealing => HealAmount > 0;
}
