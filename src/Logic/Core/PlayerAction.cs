using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// What the player (or UI) submits as their action for a turn.
/// Immutable. The presentation layer creates these; the logic layer consumes them.
/// The bot creates these via BotBrain.ToPlayerAction().
/// </summary>
public sealed class PlayerAction
{
    public enum ActionKind { Wait, Attack, Move, UseItem, Descend, DropItem, EquipItem, UnequipItem, CastSpell }

    public ActionKind Kind { get; }

    /// <summary>Attack target, or entity to move toward.</summary>
    public Entity? Target { get; }

    /// <summary>Move destination (for tap-to-move from UI) or spell target tile.</summary>
    public int? TargetX { get; }
    public int? TargetY { get; }

    /// <summary>Specific item to use, equip, or cast (scroll/wand). Null = auto-find first healing potion (bot behavior).</summary>
    public Entity? Item { get; }

    /// <summary>Equipment slot to unequip. Only set for UnequipItem actions.</summary>
    public EquipmentSlot? Slot { get; }

    /// <summary>
    /// For targeted spells: the entity ID to target (single-target spells).
    /// Null for Self, AoeSelf, and AutoClosest targeting modes (resolver picks the target).
    /// </summary>
    public int? TargetEntityId { get; }

    /// <summary>
    /// Second target tile for portal placement — the exit position.
    /// TargetX/Y hold the entrance; TargetX2/Y2 hold the exit.
    /// Only set for Portal targeting mode (Wand of Portals).
    /// </summary>
    public int? TargetX2 { get; }
    public int? TargetY2 { get; }

    private PlayerAction(ActionKind kind, Entity? target = null,
        int? targetX = null, int? targetY = null, Entity? item = null,
        EquipmentSlot? slot = null, int? targetEntityId = null,
        int? targetX2 = null, int? targetY2 = null)
    {
        Kind = kind;
        Target = target;
        TargetX = targetX;
        TargetY = targetY;
        Item = item;
        Slot = slot;
        TargetEntityId = targetEntityId;
        TargetX2 = targetX2;
        TargetY2 = targetY2;
    }

    public static PlayerAction Wait => new(ActionKind.Wait);
    public static PlayerAction Descend => new(ActionKind.Descend);
    public static PlayerAction Attack(Entity target) => new(ActionKind.Attack, target: target);
    public static PlayerAction MoveTo(int x, int y) => new(ActionKind.Move, targetX: x, targetY: y);
    public static PlayerAction MoveToward(Entity target) => new(ActionKind.Move, target: target);
    public static PlayerAction UseItem(Entity? item = null) => new(ActionKind.UseItem, item: item);
    public static PlayerAction Drop(Entity item) => new(ActionKind.DropItem, item: item);
    public static PlayerAction Equip(Entity item) => new(ActionKind.EquipItem, item: item);
    public static PlayerAction Unequip(EquipmentSlot slot) => new(ActionKind.UnequipItem, slot: slot);

    /// <summary>
    /// Cast a spell via a scroll or wand item.
    /// For Self/AoeSelf/AutoClosest targeting modes, omit targetEntityId/targetX/targetY —
    /// SpellResolver finds the target automatically.
    /// For SingleTarget spells, pass targetEntityId.
    /// For Location spells, pass targetX/targetY.
    /// </summary>
    public static PlayerAction CastSpell(Entity item, int? targetEntityId = null,
        int? targetX = null, int? targetY = null)
        => new(ActionKind.CastSpell, item: item,
               targetEntityId: targetEntityId, targetX: targetX, targetY: targetY);

    /// <summary>
    /// Cast the Wand of Portals — a two-point targeting action.
    /// Entrance is placed at (entranceX, entranceY); exit at (exitX, exitY).
    /// Both must be walkable tiles. TurnController validates before calling PortalSystem.
    /// </summary>
    public static PlayerAction CastSpellPortal(Entity item,
        int entranceX, int entranceY, int exitX, int exitY)
        => new(ActionKind.CastSpell, item: item,
               targetX: entranceX, targetY: entranceY,
               targetX2: exitX, targetY2: exitY);
}
