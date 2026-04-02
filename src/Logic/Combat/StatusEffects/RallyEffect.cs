using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat.StatusEffects;

/// <summary>
/// Entity has been rallied by an Orc Chieftain — gains a bonus to attack accuracy and damage.
/// Applied by: Orc Chieftain Rally Cry ability (one-time, requires 2+ orc allies in range 5).
/// PoC values: ToHitBonus=1, DamageBonus=1. Duration: very long (removed when chieftain takes damage).
/// </summary>
public sealed class RallyEffect : IStatusEffect
{
    public Entity? Owner { get; set; }
    public string EffectName => "rallied";
    public int RemainingTurns { get; set; } = 1000;
    public bool IsPermanent => false;

    /// <summary>Added to the rallied entity's attack roll. PoC value: 1.</summary>
    public int ToHitBonus { get; set; } = 1;

    /// <summary>Added to the rallied entity's damage on hit. PoC value: 1.</summary>
    public int DamageBonus { get; set; } = 1;
}
