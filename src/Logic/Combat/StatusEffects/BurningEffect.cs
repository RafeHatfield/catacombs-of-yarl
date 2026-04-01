using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat.StatusEffects;

/// <summary>
/// Entity is on fire — takes 3 damage per turn for 5 turns.
/// Applied by: Fire hazards (future plan).
/// PoC values: DamagePerTurn=3, RemainingTurns=5.
/// </summary>
public sealed class BurningEffect : IStatusEffect
{
    public Entity? Owner { get; set; }
    public string EffectName => "burning";
    public int RemainingTurns { get; set; } = 5;
    public bool IsPermanent => false;

    /// <summary>Damage applied per turn. PoC value: 3.</summary>
    public int DamagePerTurn { get; set; } = 3;
}
