using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat;

/// <summary>
/// Result of a single attack resolution.
/// </summary>
public sealed class AttackResult
{
    public bool Hit { get; init; }
    public bool IsCritical { get; init; }
    public bool IsFumble { get; init; }
    public int Damage { get; init; }
    public int D20Roll { get; init; }
    public bool TargetKilled { get; init; }
}

/// <summary>
/// Resolves combat between entities. Single source of truth for attack resolution.
/// Stateless — all randomness comes from the injected SeededRandom.
/// </summary>
public static class CombatResolver
{
    /// <summary>
    /// Resolve a melee attack from attacker to defender.
    /// Uses d20 roll vs AC for hit determination, then rolls damage on hit.
    /// Natural 20 = critical (2x damage). Natural 1 = fumble (auto-miss).
    /// </summary>
    public static AttackResult ResolveAttack(Entity attacker, Entity defender, SeededRandom rng)
    {
        var atk = attacker.Require<Fighter>();
        var def = defender.Require<Fighter>();

        int d20 = rng.Next(1, 21); // 1-20 inclusive

        int toHitBonus = atk.DexterityMod;
        int attackRoll = d20 + toHitBonus;
        int targetAc = def.BaseArmorClass;

        bool isCritical = d20 == 20;
        bool isFumble = d20 == 1;

        bool hit;
        if (isCritical) hit = true;
        else if (isFumble) hit = false;
        else hit = attackRoll >= targetAc;

        int damage = 0;
        bool killed = false;

        if (hit)
        {
            // Roll natural damage + strength modifier
            int baseDmg = CombatMath.RollDamage(rng, atk.DamageMin, atk.DamageMax);
            damage = baseDmg + atk.StrengthMod;

            if (isCritical)
                damage *= 2;

            damage = Math.Max(1, damage); // minimum 1 damage on hit
            def.TakeDamage(damage);
            killed = !def.IsAlive;
        }

        return new AttackResult
        {
            Hit = hit,
            IsCritical = isCritical,
            IsFumble = isFumble,
            Damage = damage,
            D20Roll = d20,
            TargetKilled = killed,
        };
    }
}
