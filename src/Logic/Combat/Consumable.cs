using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat;

/// <summary>
/// Makes an entity usable as a consumable item (potions, scrolls).
/// Consumed on use — removed from inventory after application.
/// </summary>
public sealed class Consumable : IComponent
{
    public Entity? Owner { get; set; }

    /// <summary>HP restored on use. 0 for non-healing consumables.</summary>
    public int HealAmount { get; set; }

    public Consumable(int healAmount = 0)
    {
        HealAmount = healAmount;
    }

    public bool IsHealing => HealAmount > 0;
}
