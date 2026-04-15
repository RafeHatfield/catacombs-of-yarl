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
/// 3. Opportunistic loot: floor healing potion within 3 tiles, no adjacent enemies → deviate to pick it up
/// 4. Retreat to choke point (2+ adjacent enemies, HP < 50%, not at choke)
/// 5. Attack adjacent enemy (prefer lowest HP — focus fire)
/// 6. Move toward nearest alive enemy
///
/// Key insight: healing during combat costs an attack turn but prevents death.
/// The 40 HP potion restores ~73% of max HP — a massive swing.
/// </summary>
public static class BotBrain
{
    /// <summary>
    /// Decide what the bot should do this turn.
    ///
    /// The optional <paramref name="context"/> carries a telemetry recorder and per-call metadata
    /// (turn number, floor depth). When null (the default), no telemetry is emitted and there is
    /// zero overhead beyond the null check. All existing callers that omit context are unaffected.
    ///
    /// Use <see cref="BotDecisionContext"/> to inject a recorder from the harness without adding
    /// loose optional parameters to this signature. Future per-decision context (persona, difficulty)
    /// belongs in that struct, not here.
    /// </summary>
    public static BotAction Decide(
        Entity player,
        Fighter playerFighter,
        Inventory? inventory,
        List<Entity> monsters,
        GameMap map,
        BotDecisionContext? context = null,
        IReadOnlyList<Entity>? floorItems = null)
    {
        var aliveMonsters = GetAlive(monsters);
        if (aliveMonsters.Count == 0)
        {
            EmitDecision(context, player, playerFighter, inventory, aliveMonsters, "Wait", "no_targets");
            return BotAction.None;
        }

        double hpFraction = (double)playerFighter.Hp / playerFighter.MaxHp;
        var adjacent = GetAdjacent(player, aliveMonsters);

        // 1. Panic heal — HP at panic threshold (15%). PoC: never panic at full HP.
        if (hpFraction <= BotConfig.PanicThreshold && hpFraction < 1.0 && HasHealingPotion(inventory))
        {
            EmitDecision(context, player, playerFighter, inventory, aliveMonsters, "Heal", "panic_heal");
            return BotAction.Heal;
        }

        // 2. Threshold heal — below 30%, even during combat.
        //    When 2+ adjacent enemies, treat as additional pressure: heal at 30% not just 15%.
        //    PoC balanced persona heals at 30% threshold, panic at 15%.
        if (hpFraction <= BotConfig.HealThreshold && HasHealingPotion(inventory))
        {
            EmitDecision(context, player, playerFighter, inventory, aliveMonsters, "Heal", "threshold_heal");
            return BotAction.Heal;
        }

        // 3. Opportunistic loot: pick up a floor healing potion if one is close and we're not
        //    actively brawling. Only deviates when no enemies are adjacent — don't break off a
        //    fight for a potion. Pickup fires automatically via walk-over when we step onto the tile.
        if (adjacent.Count == 0 && floorItems != null)
        {
            var nearbyPotion = FindNearbyFloorPotion(player, floorItems, searchRadius: 3);
            if (nearbyPotion != null)
            {
                EmitDecision(context, player, playerFighter, inventory, aliveMonsters, "MoveTo", "loot_potion");
                return BotAction.MoveTo(nearbyPotion.X, nearbyPotion.Y);
            }
        }

        // 4. Multi-enemy retreat to choke point — when 2+ enemies adjacent and HP < 50%.
        //    Find the nearest corner/wall position that limits simultaneous approach angles.
        //    Once at a choke (3+ wall neighbors), stand and fight — don't keep retreating.
        //    PoC tactical_fighter: retreat_hp_threshold=0.5, panic_multi_enemy_count=2.
        if (adjacent.Count >= 2 && hpFraction < 0.5)
        {
            if (!AtChokePoint(player, map))
            {
                var choke = FindChokePoint(player, map);
                if (choke.HasValue)
                {
                    EmitDecision(context, player, playerFighter, inventory, aliveMonsters, "MoveTo", "retreat_to_choke");
                    return BotAction.MoveTo(choke.Value.x, choke.Value.y);
                }
            }
            // Already at choke or no choke found — fall through and fight
        }

        // 5. Attack adjacent enemy — focus fire lowest HP
        if (adjacent.Count > 0)
        {
            var target = PickTarget(adjacent);
            EmitDecision(context, player, playerFighter, inventory, aliveMonsters, "Attack", "attack_lowest_hp");
            return BotAction.Attack(target);
        }

        // 6. Move toward nearest alive enemy.
        //    Rushing toward the nearest enemy creates sequential engagement naturally:
        //    the player meets the nearest orc first while others are still approaching.
        //    The old "wait for enemies" heuristic was worse — standing still caused all orcs
        //    to converge simultaneously on a static position.
        var nearest = FindNearest(player, aliveMonsters);
        if (nearest != null)
        {
            EmitDecision(context, player, playerFighter, inventory, aliveMonsters, "MoveToward", "move_to_nearest");
            return BotAction.Move(nearest);
        }

        EmitDecision(context, player, playerFighter, inventory, aliveMonsters, "Wait", "no_targets");
        return BotAction.None;
    }

    /// <summary>
    /// Emit one BotDecisionRecord to the recorder in context, if context is non-null.
    /// Early-returns on null context — caller pays only one null check.
    /// </summary>
    private static void EmitDecision(
        BotDecisionContext? context,
        Entity player,
        Fighter playerFighter,
        Inventory? inventory,
        List<Entity> aliveMonsters,
        string actionType,
        string reason)
    {
        if (context is null) return;

        var ctx = context.Value;
        double hpFraction = playerFighter.MaxHp > 0
            ? (double)playerFighter.Hp / playerFighter.MaxHp
            : 0.0;
        var adjacent = GetAdjacent(player, aliveMonsters);
        int potions  = CountHealingPotions(inventory);

        ctx.Recorder.Record(new BotDecisionRecord
        {
            TurnNumber              = ctx.TurnNumber,
            FloorDepth              = ctx.FloorDepth,
            ActionType              = actionType,
            Reason                  = reason,
            HpFraction              = hpFraction,
            VisibleEnemies          = aliveMonsters.Count,
            AdjacentEnemies         = adjacent.Count,
            HealingPotionsAvailable = potions,
            InCombat                = adjacent.Count > 0,
            LowHp                   = hpFraction <= BotConfig.HealThreshold,
        });
    }

    /// <summary>
    /// Count healing potions in the inventory. Used by EmitDecision to record
    /// HealingPotionsAvailable without modifying the main Decide() flow.
    /// </summary>
    private static int CountHealingPotions(Inventory? inventory)
    {
        if (inventory == null) return 0;
        int count = 0;
        foreach (var item in inventory.Items)
        {
            var consumable = item.Get<Consumable>();
            if (consumable?.IsHealing == true)
                count += consumable.StackSize;
        }
        return count;
    }

    /// <summary>
    /// Count non-walkable (wall/out-of-bounds) tiles in the 8 neighbors of (x, y).
    /// Higher count = better defensive position (limits approach angles).
    /// Corner: ~5 walls; edge: ~3 walls; open floor: 0 walls.
    /// </summary>
    private static int CountWallNeighbors(int x, int y, GameMap map)
    {
        int count = 0;
        for (int dx = -1; dx <= 1; dx++)
            for (int dy = -1; dy <= 1; dy++)
            {
                if (dx == 0 && dy == 0) continue;
                if (!map.IsWalkable(x + dx, y + dy)) count++;
            }
        return count;
    }

    /// <summary>
    /// True if the player is already at a choke point (3+ wall neighbors).
    /// At a choke the bot should stand and fight rather than keep retreating.
    /// </summary>
    private static bool AtChokePoint(Entity player, GameMap map)
        => CountWallNeighbors(player.X, player.Y, map) >= 3;

    /// <summary>
    /// Find the best defensive choke point within searchRadius tiles.
    /// Prefers tiles with the most wall neighbors (limits simultaneous attackers),
    /// breaking ties by proximity. Returns null if no tile with 2+ walls found.
    /// </summary>
    private static (int x, int y)? FindChokePoint(Entity player, GameMap map, int searchRadius = 8)
    {
        (int x, int y)? best = null;
        int bestWalls = 1; // must beat this threshold
        double bestDist = double.MaxValue;

        for (int dx = -searchRadius; dx <= searchRadius; dx++)
        {
            for (int dy = -searchRadius; dy <= searchRadius; dy++)
            {
                if (dx == 0 && dy == 0) continue;
                int nx = player.X + dx;
                int ny = player.Y + dy;
                if (!map.CanMoveTo(nx, ny)) continue;

                int walls = CountWallNeighbors(nx, ny, map);
                double dist = Math.Sqrt(dx * dx + dy * dy);

                // Prefer more walls; break ties by proximity
                if (walls > bestWalls || (walls == bestWalls && dist < bestDist))
                {
                    bestWalls = walls;
                    bestDist = dist;
                    best = (nx, ny);
                }
            }
        }

        return best;
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
        => monsters.Where(m => m.Get<Fighter>()?.IsAlive == true).ToList();

    private static List<Entity> GetAdjacent(Entity player, List<Entity> alive)
        => alive.Where(m => player.ChebyshevDistanceTo(m.X, m.Y) <= 1).ToList();

    /// <summary>
    /// Find the nearest floor healing potion within <paramref name="searchRadius"/> Chebyshev tiles.
    /// Returns null if no eligible potion exists or floorItems is null/empty.
    ///
    /// Used for opportunistic loot pickup: bot deviates to pick up a nearby potion when not
    /// actively brawling (no adjacent enemies). Walk-over auto-pickup fires when bot steps onto
    /// the tile. Search radius is intentionally small (3) — we don't cross the map for a potion.
    /// </summary>
    private static Entity? FindNearbyFloorPotion(Entity player, IReadOnlyList<Entity> floorItems, int searchRadius)
    {
        Entity? best = null;
        double bestDist = double.MaxValue;

        foreach (var item in floorItems)
        {
            // Only seek healing potions — don't deviate for scrolls/wands/equipment
            var consumable = item.Get<Consumable>();
            if (consumable?.IsHealing != true) continue;

            int dx = Math.Abs(item.X - player.X);
            int dy = Math.Abs(item.Y - player.Y);
            if (Math.Max(dx, dy) > searchRadius) continue; // outside Chebyshev radius

            double dist = player.DistanceTo(item.X, item.Y);
            if (dist < bestDist)
            {
                bestDist = dist;
                best = item;
            }
        }

        return best;
    }

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
        BotAction.ActionType.MoveTo => PlayerAction.MoveTo(action.TargetX, action.TargetY),
        _ => PlayerAction.Wait,
    };
}

/// <summary>
/// Immutable bot decision — what action to take and on whom.
/// </summary>
public sealed class BotAction
{
    public enum ActionType { DoNothing, AttackTarget, HealSelf, MoveToward, MoveTo }

    public ActionType Type { get; }
    public Entity? Target { get; }
    public int TargetX { get; }
    public int TargetY { get; }

    private BotAction(ActionType type, Entity? target = null, int targetX = 0, int targetY = 0)
    {
        Type = type;
        Target = target;
        TargetX = targetX;
        TargetY = targetY;
    }

    public static BotAction None => new(ActionType.DoNothing);
    public static BotAction Heal => new(ActionType.HealSelf);
    public static BotAction Attack(Entity target) => new(ActionType.AttackTarget, target);
    public static BotAction Move(Entity toward) => new(ActionType.MoveToward, toward);
    public static BotAction MoveTo(int x, int y) => new(ActionType.MoveTo, targetX: x, targetY: y);
}
