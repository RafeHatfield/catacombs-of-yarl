using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat;

/// <summary>
/// Combat stats component. Anything that can fight or be fought has this.
/// Holds base stats — equipment and status modifiers are applied by services during resolution.
/// </summary>
public sealed class Fighter : IComponent
{
    public Entity? Owner { get; set; }

    // Health
    public int BaseMaxHp { get; }
    public int Hp { get; set; }

    // D&D-style ability scores (8-18 range, default 10)
    public int Strength { get; set; }
    public int Dexterity { get; set; }
    public int Constitution { get; set; }

    // Hit chance modifiers
    public int Accuracy { get; set; }
    public int Evasion { get; set; }

    // Natural damage range (fists/claws — used when no weapon equipped)
    public int DamageMin { get; set; }
    public int DamageMax { get; set; }

    // Legacy power/defense (kept for compatibility with YAML definitions)
    public int BasePower { get; set; }
    public int BaseDefense { get; set; }

    // Experience awarded on kill (monsters only)
    public int Xp { get; set; }

    public Fighter(
        int hp,
        int defense = 0,
        int power = 0,
        int xp = 0,
        int damageMin = 0,
        int damageMax = 0,
        int strength = 10,
        int dexterity = 10,
        int constitution = 10,
        int accuracy = HitModel.DefaultAccuracy,
        int evasion = HitModel.DefaultEvasion)
    {
        BaseMaxHp = hp;
        Hp = hp;
        BaseDefense = defense;
        BasePower = power;
        Xp = xp;
        DamageMin = damageMin;
        DamageMax = damageMax;
        Strength = strength;
        Dexterity = dexterity;
        Constitution = constitution;
        Accuracy = accuracy;
        Evasion = evasion;
    }

    /// <summary>Base max HP + constitution modifier. Equipment bonuses applied externally.</summary>
    public int MaxHp => BaseMaxHp + CombatMath.StatModifier(Constitution);

    /// <summary>Strength modifier from ability score.</summary>
    public int StrengthMod => CombatMath.StatModifier(Strength);

    /// <summary>Dexterity modifier from ability score.</summary>
    public int DexterityMod => CombatMath.StatModifier(Dexterity);

    /// <summary>Constitution modifier from ability score.</summary>
    public int ConstitutionMod => CombatMath.StatModifier(Constitution);

    /// <summary>
    /// Base armor class: 10 + dexterity modifier. Equipment and status effects add to this externally.
    /// </summary>
    public int BaseArmorClass => 10 + DexterityMod;

    public bool IsAlive => Hp > 0;

    /// <summary>
    /// Apply damage. Returns actual damage dealt (after floor of 0).
    /// Does not handle resistances — that's the combat resolver's job.
    /// </summary>
    public int TakeDamage(int amount)
    {
        int actual = Math.Max(0, amount);
        Hp -= actual;
        return actual;
    }

    /// <summary>Restore HP, capped at MaxHp. Returns actual amount healed.</summary>
    public int Heal(int amount)
    {
        if (amount <= 0) return 0;
        int maxHp = MaxHp;
        int before = Hp;
        Hp = Math.Min(Hp + amount, maxHp);
        return Hp - before;
    }
}
