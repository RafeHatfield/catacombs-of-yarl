using CatacombsOfYarl.Logic.Combat.StatusEffects;
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
        UpdateAwareness(monster, player, state);

        // 3. Not alerted → idle.
        var alertedState = monster.Get<AlertedState>();
        if (alertedState == null)
            return MonsterAction.Wait();

        // ── Phase 2/4: Status effect AI overrides ─────────────────────────────

        // FearEffect: monster flees from player. Does NOT attack, even when adjacent.
        // If no valid move away exists, stays in place. PoC-verified.
        if (monster.Has<FearEffect>())
            return DecideFlee(monster, player, state);

        // Resolve target: TauntedEffect forces targeting the player (overrides EnragedEffect).
        // EnragedEffect (HostileToAll) targets nearest entity regardless of allegiance.
        // Both are handled in ChooseTarget.
        var target = ChooseTarget(monster, player, state);

        bool targetAdjacent = monster.ChebyshevDistanceTo(target.X, target.Y) <= 1;

        // DisorientationEffect: monster moves in a random direction instead of pursuing.
        // Attacks are NOT affected — if already adjacent, monster still attacks.
        // Movement randomization applies to the pursuit path only (PoC-verified).
        if (monster.Has<DisorientationEffect>())
        {
            if (targetAdjacent && !target.Has<InvisibilityEffect>())
                return MonsterAction.Attack(target);
            return DecideRandomMove(monster, state);
        }

        // EntangledEffect: monster cannot move but CAN attack adjacent targets.
        if (monster.Has<EntangledEffect>())
        {
            if (targetAdjacent && !target.Has<InvisibilityEffect>())
                return MonsterAction.Attack(target);
            return MonsterAction.Wait(); // rooted, cannot pursue
        }

        // ImmobilizedEffect: ProcessTurnStart already returns skipTurn=true for the full-action block.
        // We don't need to intercept here — TurnController skips the entire action.
        // This branch is kept as documentation clarity but should never fire in practice.

        // ── Normal AI flow ─────────────────────────────────────────────────────

        // 4. Item seeking — only when not actively in melee contact with the chosen target.
        if (!targetAdjacent)
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

        // 6. Adjacent to target → attack immediately.
        // Chebyshev distance 1 = any of the 8 surrounding tiles (diagonal melee included).
        // Invisible entities cannot be targeted for direct attacks — the AI can't see them.
        // They can still be damaged by AoE. InvisibilityEffect breaks on the player's own attack.
        if (targetAdjacent && !target.Has<InvisibilityEffect>())
            return MonsterAction.Attack(target);

        // If adjacent but target is invisible: fall through to movement logic.
        // Monster will wait or pursue a remembered position instead of attacking.

        // 7. Pursue toward last known player position using A*.
        // For EnragedEffect (HostileToAll), pursue the chosen target (nearest entity).
        // Pass the monster as movingEntity so the pathfinder doesn't treat it as self-blocking.
        int pursueX = monster.Has<EnragedEffect>() ? target.X : alertedState.LastKnownPlayerX;
        int pursueY = monster.Has<EnragedEffect>() ? target.Y : alertedState.LastKnownPlayerY;

        var path = Pathfinder.AStar(
            state.Map,
            monster.X, monster.Y,
            pursueX, pursueY,
            movingEntity: monster);

        if (path != null && path.Count > 0)
            return MonsterAction.MoveTo(path[0].X, path[0].Y);

        // 8. A* failed (unreachable or no valid path) — try greedy as a last resort.
        // MoveToward mutates the entity's position directly, so we only call it if
        // a greedy step actually exists. We detect this by checking if the target differs
        // from the monster's current position (otherwise MoveToward is a no-op anyway).
        if (monster.X != pursueX || monster.Y != pursueY)
        {
            // Greedy step: attempt to move one tile closer, return MoveTo if a direction is free.
            // We compute the intended greedy destination rather than mutating position here —
            // let TurnController apply the move to stay consistent with the action model.
            int dx = Math.Sign(pursueX - monster.X);
            int dy = Math.Sign(pursueY - monster.Y);

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
    /// Updates the monster's AlertedState based on current FOV (dungeon mode) or always-alerted
    /// (scenario/harness mode). Shared by all specialized AI types.
    /// </summary>
    internal static void UpdateAwareness(Entity monster, Entity player, GameState state)
    {
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
                var alert = monster.GetOrAdd<AlertedState>();
                alert.LastKnownPlayerX = player.X;
                alert.LastKnownPlayerY = player.Y;
                alert.TurnsUntilDeaggro = AlertedState.DeaggroTurns;
            }
            else
            {
                var alert = monster.Get<AlertedState>();
                if (alert != null)
                {
                    alert.TurnsUntilDeaggro--;
                    if (alert.TurnsUntilDeaggro <= 0)
                        monster.Remove<AlertedState>();
                }
            }
        }
        else
        {
            var alert = monster.GetOrAdd<AlertedState>();
            alert.LastKnownPlayerX = player.X;
            alert.LastKnownPlayerY = player.Y;
            alert.TurnsUntilDeaggro = AlertedState.DeaggroTurns;
        }
    }

    /// <summary>
    /// Choose the attack target for this monster.
    ///
    /// Priority:
    ///   1. TauntedEffect: always target the taunted entity's TauntTargetId (player).
    ///   2. EnragedEffect (HostileToAll): find nearest alive entity — player or any monster.
    ///   3. Default: target the player.
    ///
    /// Returns player if no special targeting applies or if the special target is not found.
    /// </summary>
    internal static Entity ChooseTarget(Entity monster, Entity player, GameState state)
    {
        // Taunt overrides everything — even EnragedEffect.
        var taunt = monster.Get<TauntedEffect>();
        if (taunt != null)
        {
            // TauntTargetId -1 means unset; default to player.
            if (taunt.TauntTargetId == player.Id || taunt.TauntTargetId < 0)
                return player;
            // Future: look up the entity by ID if we have non-player taunt targets.
            return player;
        }

        // EnragedEffect: HostileToAll flag set on the effect component.
        // Find nearest entity (player or alive monster) — we want whoever is closest.
        if (monster.Has<EnragedEffect>())
        {
            Entity? nearest = null;
            int nearestDist = int.MaxValue;

            // Check player first.
            int playerDist = monster.ChebyshevDistanceTo(player.X, player.Y);
            if (playerDist < nearestDist)
            {
                nearest = player;
                nearestDist = playerDist;
            }

            // Check all alive monsters (excluding self).
            foreach (var other in state.AliveMonsters)
            {
                if (other.Id == monster.Id) continue;
                int d = monster.ChebyshevDistanceTo(other.X, other.Y);
                if (d < nearestDist)
                {
                    nearest = other;
                    nearestDist = d;
                }
            }

            return nearest ?? player;
        }

        // Invisible player: monster AI cannot target an invisible entity for attack.
        // The invisible entity can still be damaged by AoE — this is a targeting gate only.
        // Returning null signals the caller that no valid attack target exists.
        // NOTE: We still return player here (not null) because ChooseTarget returns Entity, not Entity?.
        // The invisibility attack gate is enforced in Decide() before the Attack action is returned.
        // See: "if (targetAdjacent && !target.Has<InvisibilityEffect>())" in the main decision flow.

        return player;
    }

    /// <summary>
    /// Flee AI: move to maximize distance from the player.
    /// If all adjacent passable tiles are blocked or none increases distance, stay in place.
    /// Never attacks while feared (PoC-verified).
    /// </summary>
    internal static MonsterAction DecideFlee(Entity monster, Entity player, GameState state)
    {
        int bestX = monster.X, bestY = monster.Y;
        // Use Manhattan consistently: both the baseline and candidate evaluations use the same metric.
        int bestDist = Math.Abs(monster.X - player.X) + Math.Abs(monster.Y - player.Y);

        // Try all 8 adjacent tiles; pick the one that maximizes distance from player.
        for (int dx = -1; dx <= 1; dx++)
        {
            for (int dy = -1; dy <= 1; dy++)
            {
                if (dx == 0 && dy == 0) continue;
                int nx = monster.X + dx;
                int ny = monster.Y + dy;
                if (!state.Map.CanMoveTo(nx, ny)) continue;

                int dist = Math.Abs(nx - player.X) + Math.Abs(ny - player.Y);
                if (dist > bestDist)
                {
                    bestDist = dist;
                    bestX = nx;
                    bestY = ny;
                }
            }
        }

        // If no better tile found (cornered), stay in place.
        if (bestX == monster.X && bestY == monster.Y)
            return MonsterAction.Wait();

        return MonsterAction.MoveTo(bestX, bestY);
    }

    /// <summary>
    /// Random movement for DisorientationEffect: pick a random adjacent passable tile.
    /// If the chosen direction hits a wall, no movement this turn (PoC-verified).
    /// </summary>
    internal static MonsterAction DecideRandomMove(Entity monster, GameState state)
    {
        // All 8 adjacent directions
        var dirs = new (int dx, int dy)[]
        {
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1),
        };

        // Shuffle using Fisher-Yates with the game's RNG to stay deterministic.
        var shuffled = dirs.ToList();
        for (int i = shuffled.Count - 1; i > 0; i--)
        {
            int j = state.Rng.Next(0, i + 1);
            (shuffled[i], shuffled[j]) = (shuffled[j], shuffled[i]);
        }

        foreach (var (dx, dy) in shuffled)
        {
            int nx = monster.X + dx;
            int ny = monster.Y + dy;
            if (state.Map.CanMoveTo(nx, ny))
                return MonsterAction.MoveTo(nx, ny);
        }

        // All directions blocked — no move.
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
