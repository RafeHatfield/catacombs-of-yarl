using CatacombsOfYarl.Logic.Core;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Map;

namespace CatacombsOfYarl.Logic.AI;

/// <summary>
/// Standard monster AI: awareness tracking, A* pursuit, and melee combat.
///
/// Decision priority each turn:
///   1. Dead → Wait
///   2. Update awareness (FOV-based in dungeon mode, always-alerted in scenario mode)
///   3. Not alerted → Wait (idle)
///   4. Item seeking: if capable AND not actively fighting AND a floor item is closer than the player
///      → PickUp (on same tile) or SeekItem (A* toward item tile)
///   5. Item usage: 10% chance to use a held consumable (if AiComponent.CanUseItems = true)
///   6. Adjacent to player → Attack
///   7. Path exists → MoveTo first step
///   8. Path blocked → greedy MoveToward fallback, or Wait
/// </summary>
public static class BasicMonsterAI
{
    public static MonsterAction Decide(Entity monster, GameState state)
    {
        // 1. Dead monsters do nothing — guard against being called on a corpse.
        var fighter = monster.Get<Fighter>();
        if (fighter != null && !fighter.IsAlive)
            return MonsterAction.Wait();

        var player = state.Player;

        // 2. Awareness update.
        // Dungeon mode has per-turn FOV: only tiles currently visible to the player count as
        // "seen by the player". The monster itself doesn't compute sight — we use the player's FOV
        // as the shared visibility layer, which matches the prototype's map_is_in_fov check.
        //
        // Scenario mode (harness, tests): no FOV system, RevealAll() is called at startup.
        // Treat every monster as perpetually alerted so scenario combat proceeds normally.
        if (state.IsDungeonMode)
        {
            if (state.Map.IsVisible(monster.X, monster.Y))
            {
                // Monster is in the player's FOV this turn → alert/refresh
                var alert = monster.GetOrAdd<AlertedState>();
                alert.LastKnownPlayerX = player.X;
                alert.LastKnownPlayerY = player.Y;
                alert.TurnsUntilDeaggro = AlertedState.DeaggroTurns;
            }
            else
            {
                // Out of FOV — tick down the de-aggro timer if currently alerted
                var alert = monster.Get<AlertedState>();
                if (alert != null)
                {
                    alert.TurnsUntilDeaggro--;
                    if (alert.TurnsUntilDeaggro <= 0)
                        monster.Remove<AlertedState>(); // monster loses interest, returns to idle
                }
            }
        }
        else
        {
            // Scenario mode: always treat as alerted at player's current position.
            // TurnsUntilDeaggro is irrelevant in this path — set high to avoid confusion.
            var alert = monster.GetOrAdd<AlertedState>();
            alert.LastKnownPlayerX = player.X;
            alert.LastKnownPlayerY = player.Y;
            alert.TurnsUntilDeaggro = AlertedState.DeaggroTurns;
        }

        // 3. Not alerted → idle.
        var alertedState = monster.Get<AlertedState>();
        if (alertedState == null)
            return MonsterAction.Wait();

        // 4. Item seeking — only when not actively in melee contact with the player.
        // "In combat" = alerted AND player is adjacent. Once the player is adjacent the
        // monster should fight, not sidestep to grab a sword. This mirrors the PoC's
        // `if not self.in_combat` check in BasicMonster.take_turn.
        bool playerAdjacent = monster.ChebyshevDistanceTo(player.X, player.Y) <= 1;
        if (!playerAdjacent)
        {
            var itemAction = TryItemSeek(monster, state);
            if (itemAction != null)
                return itemAction;
        }

        // 5. Item usage: 10% chance per turn to use a held consumable.
        // Gated behind AiComponent.CanUseItems — false by default to match PoC's
        // can_use_potions = False. Enable per-monster in YAML once the scroll system
        // lands and balance is validated.
        // Fires before the attack check so a monster might heal instead of swinging.
        var ai = monster.Get<AiComponent>();
        if (ai != null && ai.CanUseItems)
        {
            var monsInventory = monster.Get<Inventory>();
            if (monsInventory != null && monsInventory.Count > 0 && state.Rng.Next(0, 100) < 10)
            {
                var usable = monsInventory.FindFirst(item => item.Get<Consumable>()?.IsHealing == true);
                if (usable != null)
                    return MonsterAction.UseItem(usable);
            }
        }

        // 6. Adjacent to player → attack immediately.
        // Chebyshev distance 1 = any of the 8 surrounding tiles (diagonal melee included).
        if (playerAdjacent)
            return MonsterAction.Attack(player);

        // 7. Pursue toward last known player position using A*.
        // Pass the monster as movingEntity so the pathfinder doesn't treat it as self-blocking.
        // The goal tile is the last known position — may or may not still be occupied by the player.
        var path = Pathfinder.AStar(
            state.Map,
            monster.X, monster.Y,
            alertedState.LastKnownPlayerX, alertedState.LastKnownPlayerY,
            movingEntity: monster);

        if (path != null && path.Count > 0)
            return MonsterAction.MoveTo(path[0].X, path[0].Y);

        // 8. A* failed (unreachable or no valid path) — try greedy as a last resort.
        // MoveToward mutates the entity's position directly, so we only call it if
        // a greedy step actually exists. We detect this by checking if the target differs
        // from the monster's current position (otherwise MoveToward is a no-op anyway).
        if (monster.X != alertedState.LastKnownPlayerX || monster.Y != alertedState.LastKnownPlayerY)
        {
            // Greedy step: attempt to move one tile closer, return MoveTo if a direction is free.
            // We compute the intended greedy destination rather than mutating position here —
            // let TurnController apply the move to stay consistent with the action model.
            int dx = Math.Sign(alertedState.LastKnownPlayerX - monster.X);
            int dy = Math.Sign(alertedState.LastKnownPlayerY - monster.Y);

            // Try diagonal, then axis-aligned — mirrors GameMap.MoveToward's priority order.
            if (dx != 0 && dy != 0 && state.Map.CanMoveTo(monster.X + dx, monster.Y + dy))
                return MonsterAction.MoveTo(monster.X + dx, monster.Y + dy);
            if (dx != 0 && state.Map.CanMoveTo(monster.X + dx, monster.Y))
                return MonsterAction.MoveTo(monster.X + dx, monster.Y);
            if (dy != 0 && state.Map.CanMoveTo(monster.X, monster.Y + dy))
                return MonsterAction.MoveTo(monster.X, monster.Y + dy);
        }

        // Fully blocked or already at the target — stand still.
        return MonsterAction.Wait();
    }

    /// <summary>
    /// Check whether this monster should seek a floor item this turn.
    /// Returns a PickUp or SeekItem action if an eligible item exists, null otherwise.
    ///
    /// Eligibility rules (mirror the PoC's ItemSeekingAI):
    ///   - Monster has AiComponent.CanSeekItems = true
    ///   - Monster has an Inventory that isn't full (respecting AiComponent.InventorySize)
    ///   - At least one floor item within AiComponent.SeekDistance (Chebyshev)
    ///   - That item is closer to the monster than the player is (prevents abandoning pursuit
    ///     of a player to run across the map for gear)
    /// </summary>
    private static MonsterAction? TryItemSeek(Entity monster, GameState state)
    {
        var ai = monster.Get<AiComponent>();
        if (ai == null || !ai.CanSeekItems) return null;

        var inventory = monster.Get<Inventory>();
        if (inventory == null) return null;

        // Respect the per-monster inventory cap defined in AiComponent.InventorySize.
        // Equipment.MainHand/Chest count separately — the inventory cap covers carried (un-equipped) items.
        // Keep it simple: if AiComponent.InventorySize == 0 means unlimited (fall back to Inventory.Capacity).
        int effectiveCap = ai.InventorySize > 0 ? ai.InventorySize : Inventory.Capacity;
        if (inventory.Count >= effectiveCap) return null;

        var player = state.Player;
        int playerDist = monster.ChebyshevDistanceTo(player.X, player.Y);

        Entity? bestItem = null;
        int bestDist = int.MaxValue;

        foreach (var item in state.FloorItems)
        {
            int dist = monster.ChebyshevDistanceTo(item.X, item.Y);
            if (dist > ai.SeekDistance) continue;          // out of detection range
            if (dist >= playerDist) continue;              // player is closer or equal — fight first
            if (dist < bestDist)
            {
                bestItem = item;
                bestDist = dist;
            }
        }

        if (bestItem == null) return null;

        // On the same tile → pick up immediately.
        if (bestDist == 0)
            return MonsterAction.PickUp(bestItem);

        // Navigate toward the item using A* for the first step, just like player pursuit.
        var path = Pathfinder.AStar(
            state.Map,
            monster.X, monster.Y,
            bestItem.X, bestItem.Y,
            movingEntity: monster);

        if (path != null && path.Count > 0)
            return MonsterAction.SeekItem(path[0].X, path[0].Y);

        // A* blocked — skip seeking this turn rather than deadlocking.
        return null;
    }
}
