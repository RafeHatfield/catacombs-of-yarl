using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat;

/// <summary>
/// Tracks momentum for bonus attacks. Each attack increments a counter.
/// Chance of bonus = counter * speed_bonus_ratio.
///
/// At chance >= 1.0: guaranteed bonus, counter resets.
/// Below 1.0: RNG roll. Early success gives the bonus but does NOT reset
/// the counter — momentum cascades.
///
/// Only the faster entity (relative speed) builds momentum.
/// Counter resets on guaranteed bonus or when momentum breaks (non-attack action).
/// </summary>
public sealed class SpeedBonusTracker : IComponent
{
    public Entity? Owner { get; set; }

    private int _attackCounter;

    /// <summary>Base speed ratio (from entity definition, e.g. monster speed_bonus).</summary>
    public double BaseRatio { get; set; }

    /// <summary>Additive bonus from equipment (stacks).</summary>
    public double EquipmentRatio { get; set; }

    /// <summary>Effective speed bonus ratio.</summary>
    public double SpeedBonusRatio => BaseRatio + EquipmentRatio;

    /// <summary>Current attack counter (for diagnostics).</summary>
    public int AttackCounter => _attackCounter;

    public SpeedBonusTracker(double baseRatio = 0.0)
    {
        BaseRatio = baseRatio;
    }

    /// <summary>
    /// Roll for a bonus attack after a successful hit.
    /// Call this after each attack lands. Returns true if a bonus attack triggers.
    /// </summary>
    public bool RollForBonusAttack(SeededRandom rng)
    {
        double ratio = SpeedBonusRatio;
        if (ratio <= 0) return false;

        _attackCounter++;
        double chance = _attackCounter * ratio;

        if (chance >= 1.0)
        {
            // Guaranteed bonus — reset counter
            _attackCounter = 0;
            return true;
        }

        // RNG roll — early bonus does NOT reset counter (momentum cascades)
        double roll = rng.NextDouble();
        return roll < chance;
    }

    /// <summary>
    /// Reset momentum. Called when the entity takes a non-attack action
    /// (moves, uses item, etc.).
    /// </summary>
    public void ResetMomentum()
    {
        _attackCounter = 0;
    }

    /// <summary>
    /// Check if this entity is faster than a defender.
    /// Only the faster entity builds momentum.
    /// </summary>
    public static bool CanBuildMomentum(Entity attacker, Entity defender)
    {
        double atkSpeed = attacker.Get<SpeedBonusTracker>()?.SpeedBonusRatio ?? 0;
        double defSpeed = defender.Get<SpeedBonusTracker>()?.SpeedBonusRatio ?? 0;
        return atkSpeed > defSpeed;
    }
}
