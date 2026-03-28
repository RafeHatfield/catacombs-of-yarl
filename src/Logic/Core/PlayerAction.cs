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
    public enum ActionKind { Wait, Attack, Move, UseItem, Descend, DropItem, EquipItem, UnequipItem }

    public ActionKind Kind { get; }

    /// <summary>Attack target, or entity to move toward.</summary>
    public Entity? Target { get; }

    /// <summary>Move destination (for tap-to-move from UI).</summary>
    public int? TargetX { get; }
    public int? TargetY { get; }

    /// <summary>Specific item to use or equip. Null = auto-find first healing potion (bot behavior).</summary>
    public Entity? Item { get; }

    /// <summary>Equipment slot to unequip. Only set for UnequipItem actions.</summary>
    public EquipmentSlot? Slot { get; }

    private PlayerAction(ActionKind kind, Entity? target = null,
        int? targetX = null, int? targetY = null, Entity? item = null,
        EquipmentSlot? slot = null)
    {
        Kind = kind;
        Target = target;
        TargetX = targetX;
        TargetY = targetY;
        Item = item;
        Slot = slot;
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
}
