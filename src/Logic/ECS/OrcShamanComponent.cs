namespace CatacombsOfYarl.Logic.ECS;

/// <summary>
/// Tracks state for the Orc Shaman's Crippling Hex and hang-back behavior.
/// Attached by MonsterFactory when ai_type is "orc_shaman".
/// The hex targets the player when in range and cooldown is 0.
/// </summary>
public sealed class OrcShamanComponent : IComponent
{
    public Entity? Owner { get; set; }

    /// <summary>Turns remaining before the next hex can fire. 0 = ready.</summary>
    public int HexCooldownRemaining { get; set; } = 0;

    /// <summary>Full cooldown applied after a successful hex. PoC value: 10.</summary>
    public int HexCooldownTurns { get; set; } = 10;

    /// <summary>Maximum range (Chebyshev) for Crippling Hex. PoC value: 6.</summary>
    public int HexRange { get; set; } = 6;

    /// <summary>Duration of the CrippledEffect applied to the player. PoC value: 5 turns.</summary>
    public int HexDuration { get; set; } = 5;

    /// <summary>Minimum preferred distance from player (retreat if closer). PoC value: 4.</summary>
    public int PreferredDistanceMin { get; set; } = 4;

    /// <summary>Maximum preferred distance from player (close if farther). PoC value: 7.</summary>
    public int PreferredDistanceMax { get; set; } = 7;

    /// <summary>Panic radius: if player is this close, always retreat. PoC value: 2.</summary>
    public int DangerRadius { get; set; } = 2;
}
