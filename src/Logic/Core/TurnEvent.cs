namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// A single discrete thing that happened during a turn. The Presentation layer
/// animates these in sequence. The balance pipeline derives metrics from them.
/// Events use entity IDs (not references) — safe to serialize and hold after state changes.
/// </summary>
public abstract class TurnEvent
{
    public int ActorId { get; init; }
}

public sealed class AttackEvent : TurnEvent
{
    public int TargetId { get; init; }
    public bool Hit { get; init; }
    public int Damage { get; init; }
    public bool IsCritical { get; init; }
    public bool IsFumble { get; init; }
    public bool TargetKilled { get; init; }
    public bool IsBonusAttack { get; init; }
}

public sealed class MoveEvent : TurnEvent
{
    public int FromX { get; init; }
    public int FromY { get; init; }
    public int ToX { get; init; }
    public int ToY { get; init; }
}

public sealed class HealEvent : TurnEvent
{
    public int AmountHealed { get; init; }
    public int ItemId { get; init; }
    public string ItemName { get; init; } = "";
}

public sealed class WaitEvent : TurnEvent { }

public sealed class DescendEvent : TurnEvent
{
    /// <summary>The new depth the player is descending to.</summary>
    public int NewDepth { get; init; }
}

public sealed class DeathEvent : TurnEvent
{
    public int KillerId { get; init; }
}

public sealed class PickUpEvent : TurnEvent
{
    public int ItemId { get; init; }
    public string ItemName { get; init; } = "";
}

public sealed class DropEvent : TurnEvent
{
    public int ItemId { get; init; }
    public string ItemName { get; init; } = "";
}

/// <summary>
/// Emitted when a monster attempts to use an item from its inventory.
/// Both success and failure paths emit this event so the presentation layer
/// can show appropriate feedback (toast messages) and the harness can measure
/// how often item usage fires and what outcomes result.
/// </summary>
public sealed class ItemUseEvent : TurnEvent
{
    public string ItemName { get; init; } = "";
    public bool Success { get; init; }

    /// <summary>
    /// How the item usage failed. Empty string on success.
    /// Values: "fizzle" (nothing happens), "wrong_target" (player benefits),
    /// "equipment_damage" (monster's weapon loses a point of DamageMax).
    /// </summary>
    public string FailureMode { get; init; } = "";

    /// <summary>
    /// HP healed (success or wrong_target path) or DamageMax reduction (equipment_damage).
    /// 0 on fizzle.
    /// </summary>
    public int EffectAmount { get; init; }
}
