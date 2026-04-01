using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Combat.StatusEffects;

/// <summary>
/// Entity is aggravated against a specific faction — will attack all members of that faction
/// regardless of normal allegiance rules.
/// Applied by: Aggravation Scroll.
///
/// IsPermanent=true — this effect never expires via duration; only cleared on entity death
/// or explicit dispel. The faction system is not yet implemented (plan_faction_system).
/// TODO: When faction system lands, wire AggravatedEffect into faction targeting rules.
/// </summary>
public sealed class AggravatedEffect : IStatusEffect
{
    public Entity? Owner { get; set; }
    public string EffectName => "aggravated";

    /// <summary>
    /// IsPermanent=true — RemainingTurns is never decremented.
    /// Set to int.MaxValue as a sentinel that won't cause issues if IsPermanent check is bypassed.
    /// </summary>
    public int RemainingTurns { get; set; } = int.MaxValue;
    public bool IsPermanent => true;

    /// <summary>
    /// The faction this entity is now hostile toward.
    /// e.g. "orc", "undead", "humanoid"
    /// </summary>
    public string TargetFaction { get; set; } = "";
}
