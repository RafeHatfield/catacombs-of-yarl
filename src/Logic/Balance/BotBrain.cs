using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Balance;

/// <summary>
/// Bot decision-making for the scenario harness. Matches the Python prototype's
/// "balanced" persona behavior.
///
/// Decision priority:
/// 1. Panic heal (HP <= 15% and enemies alive)
/// 2. Retreat if overwhelmed (2+ adjacent, HP < 50%) — forces sequential engagement
/// 3. Attack adjacent enemy (prefer lowest HP — focus fire)
/// 4. Threshold heal (HP <= 30% and no adjacent enemies — safe moment)
/// 5. Move toward nearest alive enemy
/// </summary>
public static class BotBrain
{
    /// <summary>Retreat when 2+ enemies adjacent and HP below this fraction.</summary>
    private const double RetreatThreshold = 0.70;

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

        // 2. Retreat if overwhelmed — 2+ adjacent enemies and HP below 50%
        //    Move away from the centroid of adjacent enemies to force sequential engagement.
        //    Only retreat if there's somewhere to go.
        if (adjacent.Count >= 2 && hpFraction < RetreatThreshold)
        {
            var retreatTarget = FindRetreatPosition(player, adjacent, map);
            if (retreatTarget != null)
                return BotAction.Move(retreatTarget);
        }

        // 3. Attack adjacent enemy — focus fire lowest HP
        if (adjacent.Count > 0)
        {
            var target = PickTarget(adjacent);
            return BotAction.Attack(target);
        }

        // 4. Threshold heal — below 30% and safe (no adjacent enemies)
        if (hpFraction <= BotConfig.HealThreshold && HasHealingPotion(inventory))
            return BotAction.Heal;

        // 5. Move toward nearest alive enemy
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

    /// <summary>
    /// Find a position to retreat to — move away from the centroid of adjacent enemies.
    /// Returns a temporary entity at the retreat position for MoveToward, or null if stuck.
    /// </summary>
    private static Entity? FindRetreatPosition(Entity player, List<Entity> adjacent, GameMap map)
    {
        // Compute centroid of adjacent enemies
        double cx = adjacent.Average(e => (double)e.X);
        double cy = adjacent.Average(e => (double)e.Y);

        // Direction away from centroid
        int dx = Math.Sign(player.X - (int)Math.Round(cx));
        int dy = Math.Sign(player.Y - (int)Math.Round(cy));

        // If centroid is on the player, pick a default retreat direction
        if (dx == 0 && dy == 0) dx = -1;

        // Try the retreat direction
        int tx = player.X + dx;
        int ty = player.Y + dy;

        if (map.CanMoveTo(tx, ty))
        {
            // Create a temporary target entity at the retreat position
            var retreatTarget = new Entity(-1, "_retreat", tx, ty);
            return retreatTarget;
        }

        // Try axis-aligned alternatives
        if (dx != 0 && map.CanMoveTo(player.X + dx, player.Y))
            return new Entity(-1, "_retreat", player.X + dx, player.Y);
        if (dy != 0 && map.CanMoveTo(player.X, player.Y + dy))
            return new Entity(-1, "_retreat", player.X, player.Y + dy);

        return null; // cornered, can't retreat
    }

    private static bool HasHealingPotion(Inventory? inventory)
    {
        if (inventory == null) return false;
        return inventory.FindFirst(item => item.Get<Consumable>()?.IsHealing == true) != null;
    }
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
