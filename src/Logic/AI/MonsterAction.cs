using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.AI;

/// <summary>
/// Represents a monster's chosen action for the current turn.
/// Returned by MonsterAI.Decide, resolved by TurnController.
/// Mirrors PlayerAction — immutable, created by AI, consumed by controller.
/// </summary>
public sealed class MonsterAction
{
    public enum ActionKind { Wait, Attack, MoveTo, SeekItem, PickUp, UseItem, RaiseDead }

    public ActionKind Kind { get; }

    /// <summary>Attack target or item entity (PickUp/UseItem).</summary>
    public Entity? Target { get; }

    /// <summary>Destination tile for MoveTo and SeekItem actions.</summary>
    public int TargetX { get; }
    public int TargetY { get; }

    private MonsterAction(ActionKind kind, Entity? target = null, int x = 0, int y = 0)
    {
        Kind = kind;
        Target = target;
        TargetX = x;
        TargetY = y;
    }

    public static MonsterAction Wait() => new(ActionKind.Wait);
    public static MonsterAction Attack(Entity target) => new(ActionKind.Attack, target: target);
    public static MonsterAction MoveTo(int x, int y) => new(ActionKind.MoveTo, x: x, y: y);

    /// <summary>Move toward an item that isn't adjacent yet — navigate to its tile first.</summary>
    public static MonsterAction SeekItem(int x, int y) => new(ActionKind.SeekItem, x: x, y: y);

    public static MonsterAction PickUp(Entity item) => new(ActionKind.PickUp, target: item);
    public static MonsterAction UseItem(Entity item) => new(ActionKind.UseItem, target: item);

    /// <summary>Raise a corpse entity in-place. Target is the corpse entity to raise.</summary>
    public static MonsterAction RaiseDead(Entity corpse) => new(ActionKind.RaiseDead, target: corpse);
}
