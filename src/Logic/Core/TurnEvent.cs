using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

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

    /// <summary>
    /// Non-null when the attack was blocked by a status effect rather than a die roll.
    /// Values: "disarmed" (DisarmedEffect active, weapon equipped), "" / null = normal miss.
    /// </summary>
    public string? FailReason { get; init; }
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

public sealed class EquipEvent : TurnEvent
{
    public int ItemId { get; init; }
    public string ItemName { get; init; } = "";
    public EquipmentSlot Slot { get; init; }
    /// <summary>Item that was displaced from the slot and returned to inventory, if any.</summary>
    public int? DisplacedItemId { get; init; }
    public string? DisplacedItemName { get; init; }
}

public sealed class UnequipEvent : TurnEvent
{
    public int ItemId { get; init; }
    public string ItemName { get; init; } = "";
    public EquipmentSlot Slot { get; init; }
}

/// <summary>
/// A splitting monster has divided into children after HP dropped below its threshold.
/// Original entity is removed from the map; children are added to state.Monsters.
/// No XP is awarded — split is not a kill.
/// </summary>
public sealed class SplitEvent : TurnEvent
{
    /// <summary>ID of the monster that split.</summary>
    public int OriginalId { get; init; }

    /// <summary>IDs of the spawned child entities.</summary>
    public IReadOnlyList<int> ChildIds { get; init; } = Array.Empty<int>();
}

/// <summary>
/// A metal weapon was corroded by acid on a successful monster hit.
/// Presentation layer should show an orange toast with the degradation percentage.
/// Format: "The [MonsterName] corrodes your [WeaponName]! [X%]"
/// where X% = (NewDamageMax / BaseDamageMax) * 100.
/// </summary>
public sealed class CorrosionEvent : TurnEvent
{
    /// <summary>ID of the weapon entity that was degraded.</summary>
    public int WeaponId { get; init; }

    /// <summary>Name of the weapon (for toast display).</summary>
    public string WeaponName { get; init; } = "";

    /// <summary>The weapon's new DamageMax after corrosion.</summary>
    public int NewDamageMax { get; init; }

    /// <summary>The weapon's original DamageMax at creation (never changes).</summary>
    public int BaseDamageMax { get; init; }

    /// <summary>Name of the monster that caused the corrosion (for toast display).</summary>
    public string MonsterName { get; init; } = "";
}

/// <summary>
/// Emitted when the player casts a spell (via scroll or wand).
/// AoE spells list all affected entity IDs in AffectedIds. Single-target spells
/// set TargetId. The harness uses this event to measure spell usage frequency
/// and effectiveness across scenario runs.
/// </summary>
public sealed class SpellEvent : TurnEvent
{
    public string SpellId { get; init; } = "";
    public string SpellName { get; init; } = "";

    /// <summary>Entity ID of primary target (single-target spells). Null for Self/AoE.</summary>
    public int? TargetId { get; init; }

    /// <summary>Damage dealt to each target (for damage spells).</summary>
    public int Damage { get; init; }

    /// <summary>IDs of all entities affected by the spell (AoE includes all, single-target is one).</summary>
    public IReadOnlyList<int> AffectedIds { get; init; } = Array.Empty<int>();

    /// <summary>True if the spell succeeded (had a valid target, not wasted).</summary>
    public bool Success { get; init; }

    /// <summary>
    /// Name of the status effect applied by this spell (e.g., "confused", "slowed").
    /// Empty string if no status effect was applied.
    /// Presentation layer uses this for toast messages: "The orc is confused!"
    /// </summary>
    public string StatusApplied { get; init; } = "";

    /// <summary>
    /// Duration of the applied status effect in turns.
    /// 0 if no status effect was applied, or -1 for permanent effects.
    /// </summary>
    public int StatusDuration { get; init; }
}

/// <summary>
/// Emitted when the player uses a wand (before spell resolution).
/// Lets the presentation layer show charge-count badge updates and the harness
/// track wand usage vs. charge depletion rates.
/// </summary>
public sealed class WandUseEvent : TurnEvent
{
    public string WandName { get; init; } = "";
    public int RemainingCharges { get; init; }

    /// <summary>True when the wand fired successfully (charges consumed).</summary>
    public bool Success { get; init; }

    /// <summary>True when wand was destroyed (charges reached 0 on this use).</summary>
    public bool WandDestroyed { get; init; }
}

/// <summary>
/// Emitted when a scroll is picked up and auto-recharged into a matching wand
/// instead of entering inventory. The presentation layer should show a toast:
/// "[WandName] recharged! ([NewCharges] charges)"
/// </summary>
public sealed class WandRechargeEvent : TurnEvent
{
    public string WandName { get; init; } = "";
    public string ScrollName { get; init; } = "";
    public int NewCharges { get; init; }
}

/// <summary>
/// Emitted when a map-reveal spell fires.
/// RevealType: "fov" for Light Scroll (marks current FOV tiles explored),
///             "full" for Magic Mapping (marks entire floor explored).
/// </summary>
public sealed class MapRevealEvent : TurnEvent
{
    public string RevealType { get; init; } = "";
}

/// <summary>
/// Emitted by Detect Monsters scroll. All monster positions are snapshotted here
/// so the presentation layer can briefly flash them even through walls.
/// Duration is in turns (20 for the detect monsters scroll).
/// </summary>
public sealed class DetectMonstersEvent : TurnEvent
{
    public IReadOnlyList<(int X, int Y, int MonsterId)> MonsterPositions { get; init; }
        = Array.Empty<(int, int, int)>();
    public int Duration { get; init; }
}

/// <summary>
/// Emitted when a status effect is applied to an entity.
/// Complements SpellEvent for cases where multiple status effects are applied
/// in a single spell resolution (e.g., AoE fear applying FearEffect to many targets).
/// Presentation layer uses this for per-entity toast messages.
/// </summary>
public sealed class StatusAppliedEvent : TurnEvent
{
    public int TargetId { get; init; }
    public string EffectName { get; init; } = "";

    /// <summary>Duration in turns, or -1 for permanent effects.</summary>
    public int Duration { get; init; }
}

/// <summary>
/// Emitted when a status effect expires (duration hits 0 or is explicitly removed).
/// Reason is typically "duration" for natural expiry or a specific cause like "woke_on_damage".
/// </summary>
public sealed class StatusExpiredEvent : TurnEvent
{
    public int EntityId { get; init; }
    public string EffectName { get; init; } = "";

    /// <summary>"duration" for natural expiry, or a specific cause (e.g. "woke_on_damage").</summary>
    public string Reason { get; init; } = "duration";
}

/// <summary>
/// Emitted each turn when a DOT effect (poison, burning, plague) deals damage.
/// </summary>
public sealed class DotDamageEvent : TurnEvent
{
    public int EntityId { get; init; }
    public string EffectName { get; init; } = "";
    public int Damage { get; init; }
}

/// <summary>
/// Emitted each turn when a HOT effect (regeneration) heals the entity.
/// </summary>
public sealed class HotHealEvent : TurnEvent
{
    public int EntityId { get; init; }
    public string EffectName { get; init; } = "";
    public int Amount { get; init; }
}

/// <summary>
/// Emitted when an item type is identified for the first time this run.
/// Presentation layer should show a toast: "You realize this was a [IdentifiedName]!"
/// </summary>
public sealed class IdentificationEvent : TurnEvent
{
    /// <summary>The YAML type ID of the item type that was identified (e.g. "healing_potion").</summary>
    public string TypeId { get; init; } = "";

    /// <summary>The true name revealed (e.g. "Healing Potion", "Scroll of Lightning").</summary>
    public string IdentifiedName { get; init; } = "";

    /// <summary>
    /// Trigger that caused identification.
    /// Values: "used" (potion/scroll/wand used), "equipped" (ring equipped).
    /// </summary>
    public string Trigger { get; init; } = "used";
}

/// <summary>
/// Emitted when an entity's turn is skipped due to a status effect (SlowedEffect, ImmobilizedEffect, SleepEffect).
/// </summary>
public sealed class SkipTurnEvent : TurnEvent
{
    public int EntityId { get; init; }
    public string EffectName { get; init; } = "";
}

/// <summary>
/// Emitted when a teleport spell resolves (Teleport Scroll, Blink Scroll).
/// Misfire=true means the caster ended up at a random tile instead of the chosen one.
/// Presentation layer uses this to animate the teleport flash and show misfire toast.
/// </summary>
public sealed class TeleportEvent : TurnEvent
{
    public int EntityId { get; init; }
    public int FromX { get; init; }
    public int FromY { get; init; }
    public int ToX { get; init; }
    public int ToY { get; init; }
    public bool Misfire { get; init; }
}

/// <summary>
/// Emitted when a portal pair is placed by the Wand of Portals.
/// Two of these are emitted per wand use — one for entrance, one for exit.
/// Presentation layer spawns the portal sprite at Position using Type to pick the tint.
/// </summary>
public sealed class PortalPlacedEvent : TurnEvent
{
    public int PlacerId { get; init; }
    public PortalType Type { get; init; }
    public int PortalEntityId { get; init; }
    public int X { get; init; }
    public int Y { get; init; }
}

/// <summary>
/// Emitted when an entity (player or monster) teleports through a portal.
/// Presentation layer plays a teleport flash at From and To positions.
/// </summary>
public sealed class PortalTeleportEvent : TurnEvent
{
    public int EntityId { get; init; }
    public int FromX { get; init; }
    public int FromY { get; init; }
    public int ToX { get; init; }
    public int ToY { get; init; }
    public int PortalEntryId { get; init; }
    public int PortalExitId { get; init; }
}

/// <summary>
/// Emitted when an existing portal pair is removed — either because the Wand of Portals
/// placed a new pair (recycling the old one) or a floor transition cleared portals.
/// Presentation layer despawns the portal sprites.
/// </summary>
public sealed class PortalRemovedEvent : TurnEvent
{
    public int EntranceEntityId { get; init; }
    public int ExitEntityId { get; init; }
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
