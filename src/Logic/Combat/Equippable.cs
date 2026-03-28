using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat;

public enum EquipmentSlot
{
    MainHand,
    OffHand,
    Head,
    Chest,
    Feet,
    LeftRing,
    RightRing,
    Neck,
}

/// <summary>
/// Makes an entity equippable in an equipment slot.
/// Weapons have damage ranges and to-hit bonuses.
/// Armor has AC bonuses and armor type (for DEX cap rules later).
/// </summary>
public sealed class Equippable : IComponent
{
    public Entity? Owner { get; set; }

    public EquipmentSlot Slot { get; }
    public int DamageMin { get; set; }
    public int DamageMax { get; set; }
    public int ToHitBonus { get; set; }
    public int ArmorClassBonus { get; set; }
    public string? DamageType { get; set; }
    public string? ArmorType { get; set; }
    public int CritThreshold { get; set; } = 20;

    public Equippable(EquipmentSlot slot)
    {
        Slot = slot;
    }

    /// <summary>Roll weapon damage. Returns 0 if no damage range (armor, etc).</summary>
    public int RollDamage(SeededRandom rng)
    {
        return CombatMath.RollDamage(rng, DamageMin, DamageMax);
    }

    public bool IsWeapon => DamageMin > 0 || DamageMax > 0;
}
