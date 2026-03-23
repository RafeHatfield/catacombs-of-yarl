using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Bot decision-making for the scenario harness. Matches the Python prototype's
/// "balanced" persona behavior.
///
/// Decision priority (balanced persona):
/// 1. Panic heal (HP <= 15%) — absolute priority, even mid-combat
/// 2. Threshold heal (HP <= 30%) — including during combat (allow_combat_healing)
/// 3. Attack adjacent enemy (prefer lowest HP — focus fire)
/// 4. Move toward nearest alive enemy
///
/// Key insight: healing during combat costs an attack turn but prevents death.
/// The 40 HP potion restores ~73% of max HP — a massive swing.
/// </summary>
public static class BotBrain
{
    /// <summary>
    /// Decide what the bot should do this turn.
    /// </summary>
    public static BotAction Decide(
        Entity player,
        Fighter playerFighter,
        Inventory? inventory,
        List<Entity> monsters,
        GameMap map)
    {
        var aliveMonsters = GetAlive(monsters);
        if (aliveMonsters.Count == 0)
            return BotAction.None;

        double hpFraction = (double)playerFighter.Hp / playerFighter.MaxHp;
        var adjacent = GetAdjacent(player, aliveMonsters);

        // 1. Panic heal — very low HP, enemies still alive
        if (hpFraction <= BotConfig.PanicThreshold && HasHealingPotion(inventory))
            return BotAction.Heal;

        // 2. Threshold heal — below 30%, even during combat
        //    The Python prototype's balanced persona allows combat healing.
        //    Trading one attack turn for 40 HP is almost always correct.
        if (hpFraction <= BotConfig.HealThreshold && HasHealingPotion(inventory))
            return BotAction.Heal;

        // 3. Attack adjacent enemy — focus fire lowest HP
        if (adjacent.Count > 0)
        {
            var target = PickTarget(adjacent);
            return BotAction.Attack(target);
        }

        // 4. Move toward nearest alive enemy
        var nearest = FindNearest(player, aliveMonsters);
        if (nearest != null)
            return BotAction.Move(nearest);

        return BotAction.None;
    }

    /// <summary>
    /// Pick the best target from adjacent enemies.
    /// Priority: lowest current HP (focus fire to reduce incoming damage faster).
    /// </summary>
    private static Entity PickTarget(List<Entity> adjacent)
    {
        Entity best = adjacent[0];
        int bestHp = best.Require<Fighter>().Hp;

        for (int i = 1; i < adjacent.Count; i++)
        {
            int hp = adjacent[i].Require<Fighter>().Hp;
            if (hp < bestHp)
            {
                best = adjacent[i];
                bestHp = hp;
            }
        }
        return best;
    }

    private static List<Entity> GetAlive(List<Entity> monsters)
        => monsters.Where(m => m.Require<Fighter>().IsAlive).ToList();

    private static List<Entity> GetAdjacent(Entity player, List<Entity> alive)
        => alive.Where(m => player.ChebyshevDistanceTo(m.X, m.Y) <= 1).ToList();

    private static Entity? FindNearest(Entity from, List<Entity> candidates)
    {
        Entity? nearest = null;
        double bestDist = double.MaxValue;
        foreach (var c in candidates)
        {
            double d = from.DistanceTo(c.X, c.Y);
            if (d < bestDist)
            {
                bestDist = d;
                nearest = c;
            }
        }
        return nearest;
    }

    private static bool HasHealingPotion(Inventory? inventory)
    {
        if (inventory == null) return false;
        return inventory.FindFirst(item => item.Get<Consumable>()?.IsHealing == true) != null;
    }

    /// <summary>
    /// Convert a BotAction to a PlayerAction for TurnController consumption.
    /// </summary>
    public static PlayerAction ToPlayerAction(BotAction action) => action.Type switch
    {
        BotAction.ActionType.AttackTarget => PlayerAction.Attack(action.Target!),
        BotAction.ActionType.HealSelf => PlayerAction.UseItem(),  // null = auto-find potion
        BotAction.ActionType.MoveToward => PlayerAction.MoveToward(action.Target!),
        _ => PlayerAction.Wait,
    };
}

/// <summary>
/// Immutable bot decision — what action to take and on whom.
/// </summary>
public sealed class BotAction
{
    public enum ActionType { DoNothing, AttackTarget, HealSelf, MoveToward }

    public ActionType Type { get; }
    public Entity? Target { get; }

    private BotAction(ActionType type, Entity? target = null)
    {
        Type = type;
        Target = target;
    }

    public static BotAction None => new(ActionType.DoNothing);
    public static BotAction Heal => new(ActionType.HealSelf);
    public static BotAction Attack(Entity target) => new(ActionType.AttackTarget, target);
    public static BotAction Move(Entity toward) => new(ActionType.MoveToward, toward);
}
