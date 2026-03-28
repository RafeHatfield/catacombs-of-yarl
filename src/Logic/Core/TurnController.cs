using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.ECS;

namespace CatacombsOfYarl.Logic.Core;

/// <summary>
/// Processes one game turn. Stateless — all state lives in GameState.
/// This is the single source of truth for turn resolution.
/// Both the harness (via BotBrain → PlayerAction) and the UI call this.
/// </summary>
public static class TurnController
{
    /// <summary>
    /// Process one complete turn: player action + all monster responses.
    /// Mutates gameState. Returns events describing what happened.
    /// </summary>
    public static TurnResult ProcessTurn(GameState state, PlayerAction action)
    {
        var events = new List<TurnEvent>();
        state.TurnCount++;

        // === PLAYER TURN ===
        ResolvePlayerAction(state, action, events);
        state.RecomputeFov(); // update FOV after player moves (no-op in scenario mode)

        // === MONSTER TURNS ===
        // Skip monster turns on successful Descend — the floor transition is handled
        // by the presentation layer. Monsters should not get a free attack as the
        // player steps through the stair.
        bool descended = events.Any(e => e is DescendEvent);
        if (!descended && state.PlayerFighter.IsAlive)
        {
            ResolveMonsterTurns(state, events);
            state.RecomputeFov(); // update FOV after monsters move (no-op in scenario mode)
        }

        var aliveMonsters = state.AliveMonsters;
        return new TurnResult
        {
            TurnNumber = state.TurnCount,
            Events = events,
            GameOver = state.IsGameOver,
            PlayerDied = !state.PlayerFighter.IsAlive,
            AllMonstersDefeated = aliveMonsters.Count == 0,
        };
    }

    private static void ResolvePlayerAction(GameState state, PlayerAction action, List<TurnEvent> events)
    {
        var player = state.Player;

        switch (action.Kind)
        {
            case PlayerAction.ActionKind.Attack:
                ResolvePlayerAttack(state, action.Target!, events, isBonusAttack: false);
                break;

            case PlayerAction.ActionKind.UseItem:
                TryHeal(state, action.Item, events);
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
                break;

            case PlayerAction.ActionKind.Move:
                ResolvePlayerMove(state, action, events);
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
                break;

            case PlayerAction.ActionKind.Wait:
                events.Add(new WaitEvent { ActorId = player.Id });
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
                break;

            case PlayerAction.ActionKind.Descend:
                ResolveDescend(state, events);
                break;

            case PlayerAction.ActionKind.DropItem:
                ResolveDrop(state, action.Item!, events);
                break;
        }
    }

    private static void ResolvePlayerAttack(GameState state, Entity target, List<TurnEvent> events, bool isBonusAttack)
    {
        var player = state.Player;
        var result = CombatResolver.ResolveAttack(player, target, state.Rng);

        events.Add(new AttackEvent
        {
            ActorId = player.Id,
            TargetId = target.Id,
            Hit = result.Hit,
            Damage = result.Damage,
            IsCritical = result.IsCritical,
            IsFumble = result.IsFumble,
            TargetKilled = result.TargetKilled,
            IsBonusAttack = isBonusAttack,
        });

        if (result.TargetKilled)
        {
            events.Add(new DeathEvent { ActorId = target.Id, KillerId = player.Id });
        }

        // Bonus attack chain — recurse if triggered and target still alive
        if (result.BonusAttackTriggered && !result.TargetKilled && target.Require<Fighter>().IsAlive)
        {
            ResolvePlayerAttack(state, target, events, isBonusAttack: true);
        }
    }

    private static void ResolvePlayerMove(GameState state, PlayerAction action, List<TurnEvent> events)
    {
        var player = state.Player;
        int fromX = player.X, fromY = player.Y;

        bool moved;
        if (action.Target != null)
            moved = state.Map.MoveToward(player, action.Target.X, action.Target.Y);
        else if (action.TargetX.HasValue && action.TargetY.HasValue)
            moved = state.Map.MoveToward(player, action.TargetX.Value, action.TargetY.Value);
        else
            moved = false;

        if (moved)
        {
            events.Add(new MoveEvent
            {
                ActorId = player.Id,
                FromX = fromX, FromY = fromY,
                ToX = player.X, ToY = player.Y,
            });

            // Auto-descend: if the player walks onto the stair, descend immediately.
            // Matches PoC behavior — stairs are always usable, no kill requirement.
            if (state.IsDungeonMode && state.PlayerOnStairDown)
            {
                ResolveDescend(state, events);
            }

            // Walk-over pickup: auto-collect any floor item at the new position
            TryPickUpItemsAt(state, player.X, player.Y, events);
        }
    }

    /// <summary>
    /// Pick up all floor items at the given position. Each picked-up item is added to
    /// the player's inventory (creating one if needed), removed from FloorItems, and
    /// reported as a PickUpEvent.
    /// </summary>
    private static void TryPickUpItemsAt(GameState state, int x, int y, List<TurnEvent> events)
    {
        var toPickUp = state.FloorItems.Where(item => item.X == x && item.Y == y).ToList();
        if (toPickUp.Count == 0) return;

        var inventory = state.Player.GetOrAdd<Inventory>();

        foreach (var item in toPickUp)
        {
            // Add returns false when inventory is full and the item could not be stacked.
            // In that case leave the item on the floor — do NOT remove it or emit an event.
            if (!inventory.Add(item))
                continue;

            state.FloorItems.Remove(item);
            state.Map.UnregisterEntity(item);

            events.Add(new PickUpEvent
            {
                ActorId = state.Player.Id,
                ItemId = item.Id,
                ItemName = item.Name,
            });
        }
    }

    /// <summary>
    /// Resolve a Descend action.
    ///
    /// Guards (any failing → treat as Wait, emit WaitEvent):
    ///   - Must be dungeon mode
    ///   - Player must be standing on the stair
    ///   - Floor must be clear (all monsters dead)
    ///
    /// On success: emit DescendEvent. Monsters do NOT act this turn (handled in ProcessTurn).
    /// The actual floor transition (building next GameState) is handled by the presentation layer
    /// on receipt of DescendEvent.
    /// </summary>
    private static void ResolveDescend(GameState state, List<TurnEvent> events)
    {
        var player = state.Player;

        if (!state.IsDungeonMode || !state.PlayerOnStairDown)
        {
            // Guard failed — treat as wait, do NOT reset momentum (stair tap is like waiting)
            events.Add(new WaitEvent { ActorId = player.Id });
            return;
        }

        events.Add(new DescendEvent
        {
            ActorId = player.Id,
            NewDepth = state.CurrentDepth + 1,
        });
    }

    private static void TryHeal(GameState state, Entity? specificItem, List<TurnEvent> events)
    {
        var fighter = state.PlayerFighter;
        var inventory = state.PlayerInventory;
        if (inventory == null) return;

        // Use specific item if provided (UI), otherwise find first healing potion (bot)
        var potion = specificItem ?? inventory.FindFirst(item =>
            item.Get<Consumable>()?.IsHealing == true);

        if (potion == null) return;

        var consumable = potion.Get<Consumable>();
        if (consumable == null) return;

        int healed = fighter.Heal(consumable.HealAmount);

        // Stack-aware consumption: decrement stack count; only remove the entity when
        // the last charge is used. This keeps the inventory slot alive for stacked potions.
        consumable.StackSize--;
        if (consumable.StackSize <= 0)
            inventory.Remove(potion);

        events.Add(new HealEvent
        {
            ActorId = state.Player.Id,
            AmountHealed = healed,
            ItemId = potion.Id,
            ItemName = potion.Name,
        });
    }

    /// <summary>
    /// Drop an item from the player's inventory onto the floor at the player's position.
    /// Dropping costs a turn — monsters will still act afterward.
    /// </summary>
    private static void ResolveDrop(GameState state, Entity item, List<TurnEvent> events)
    {
        var inventory = state.PlayerInventory;
        if (inventory == null) return;

        // Item must actually be in the player's inventory
        if (!inventory.Remove(item)) return;

        // Place the item at the player's current position
        item.X = state.Player.X;
        item.Y = state.Player.Y;

        state.FloorItems.Add(item);
        state.Map.RegisterEntity(item);

        events.Add(new DropEvent
        {
            ActorId = state.Player.Id,
            ItemId = item.Id,
            ItemName = item.Name,
        });
    }

    private static void ResolveMonsterTurns(GameState state, List<TurnEvent> events)
    {
        var player = state.Player;
        var playerFighter = state.PlayerFighter;

        foreach (var monster in state.Monsters)
        {
            var mf = monster.Require<Fighter>();
            if (!mf.IsAlive || !playerFighter.IsAlive)
                continue;

            // Symmetric FOV: if player can see the monster's tile, the monster sees the player.
            // In scenario mode (IsDungeonMode=false) fog of war is disabled — monsters always see the player.
            bool canSeePlayer = !state.IsDungeonMode || state.Map.IsVisible(monster.X, monster.Y);

            var alerted = monster.Get<AlertedState>();

            if (canSeePlayer)
            {
                // Update or create alerted state with current player position
                if (alerted == null)
                {
                    alerted = new AlertedState();
                    monster.Add(alerted);
                }
                alerted.LastKnownPlayerX = player.X;
                alerted.LastKnownPlayerY = player.Y;
                alerted.TurnsUntilDeaggro = AlertedState.DeaggroTurns;
            }
            else if (alerted != null)
            {
                // Lost sight — count down to de-aggro
                alerted.TurnsUntilDeaggro--;
                if (alerted.TurnsUntilDeaggro <= 0)
                {
                    monster.Remove<AlertedState>();
                    alerted = null;
                }
            }

            // Only act if the monster can see the player OR is still chasing (alerted)
            if (alerted == null) continue;

            if (monster.ChebyshevDistanceTo(player.X, player.Y) <= 1)
            {
                ResolveMonsterAttack(state, monster, events, isBonusAttack: false);
            }
            else
            {
                int fromX = monster.X, fromY = monster.Y;
                bool moved = state.Map.MoveToward(monster, alerted.LastKnownPlayerX, alerted.LastKnownPlayerY);
                if (moved)
                {
                    events.Add(new MoveEvent
                    {
                        ActorId = monster.Id,
                        FromX = fromX, FromY = fromY,
                        ToX = monster.X, ToY = monster.Y,
                    });
                }
            }
        }
    }

    private static void ResolveMonsterAttack(GameState state, Entity monster, List<TurnEvent> events, bool isBonusAttack)
    {
        var player = state.Player;
        var result = CombatResolver.ResolveAttack(monster, player, state.Rng);

        events.Add(new AttackEvent
        {
            ActorId = monster.Id,
            TargetId = player.Id,
            Hit = result.Hit,
            Damage = result.Damage,
            IsCritical = result.IsCritical,
            IsFumble = result.IsFumble,
            TargetKilled = result.TargetKilled,
            IsBonusAttack = isBonusAttack,
        });

        if (result.TargetKilled)
        {
            events.Add(new DeathEvent { ActorId = player.Id, KillerId = monster.Id });
        }

        // Monster bonus attacks
        if (result.BonusAttackTriggered && player.Require<Fighter>().IsAlive)
        {
            ResolveMonsterAttack(state, monster, events, isBonusAttack: true);
        }
    }
}
