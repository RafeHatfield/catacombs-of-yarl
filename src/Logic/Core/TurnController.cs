using CatacombsOfYarl.Logic.AI;
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

            case PlayerAction.ActionKind.EquipItem:
                ResolveEquip(state, action.Item!, events);
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
                break;

            case PlayerAction.ActionKind.UnequipItem:
                ResolveUnequip(state, action.Slot!.Value, events);
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
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
            DropMonsterLoot(state, target, events);
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

    /// <summary>
    /// Equip an item from the player's inventory into its designated slot.
    /// If the slot is already occupied, the displaced item is returned to inventory.
    /// Costs a turn. Guard: item must be in inventory and have an Equippable component.
    /// </summary>
    private static void ResolveEquip(GameState state, Entity item, List<TurnEvent> events)
    {
        var inventory = state.PlayerInventory;
        if (inventory == null) return;

        var equippable = item.Get<Equippable>();
        if (equippable == null) return;

        // Item must be in the player's inventory.
        if (!inventory.Remove(item)) return;

        var equipment = state.Player.GetOrAdd<Equipment>();
        var displaced = equipment.SetSlot(equippable.Slot, item);

        // Attempt to return the displaced item to inventory. If inventory is full and
        // the displaced item can't be stacked, drop it at the player's feet instead.
        int? displacedId = null;
        string? displacedName = null;
        if (displaced != null)
        {
            displacedId   = displaced.Id;
            displacedName = displaced.Name;
            if (!inventory.Add(displaced))
            {
                // Inventory full — drop displaced item on floor.
                displaced.X = state.Player.X;
                displaced.Y = state.Player.Y;
                state.FloorItems.Add(displaced);
                state.Map.RegisterEntity(displaced);
                events.Add(new DropEvent
                {
                    ActorId  = state.Player.Id,
                    ItemId   = displaced.Id,
                    ItemName = displaced.Name,
                });
            }
        }

        // Propagate weapon speed_bonus to player's SpeedBonusTracker so momentum
        // system activates when equipping a weapon that has a speed bonus.
        if (equippable.Slot == EquipmentSlot.MainHand)
        {
            double weaponSpeed = item.Get<SpeedBonusTracker>()?.EquipmentRatio ?? 0;
            var tracker = state.Player.Get<SpeedBonusTracker>();
            if (tracker == null && weaponSpeed > 0)
            {
                tracker = new SpeedBonusTracker();
                state.Player.Add(tracker);
            }
            if (tracker != null) tracker.EquipmentRatio = weaponSpeed;
        }

        events.Add(new EquipEvent
        {
            ActorId          = state.Player.Id,
            ItemId           = item.Id,
            ItemName         = item.Name,
            Slot             = equippable.Slot,
            DisplacedItemId  = displacedId,
            DisplacedItemName = displacedName,
        });
    }

    /// <summary>
    /// Unequip the item in the given slot and return it to the player's inventory.
    /// Guard: slot must be occupied; inventory must not be full (unless the item can stack).
    /// If inventory is full, the action is silently ignored (no event emitted).
    /// </summary>
    private static void ResolveUnequip(GameState state, EquipmentSlot slot, List<TurnEvent> events)
    {
        var equipment = state.Player.Get<Equipment>();
        if (equipment == null) return;

        var item = equipment.GetSlot(slot);
        if (item == null) return;

        var inventory = state.Player.GetOrAdd<Inventory>();
        if (!inventory.Add(item)) return; // Inventory full — block the action

        equipment.SetSlot(slot, null);

        // Clear weapon speed contribution when unequipping from main hand.
        if (slot == EquipmentSlot.MainHand)
        {
            var tracker = state.Player.Get<SpeedBonusTracker>();
            if (tracker != null) tracker.EquipmentRatio = 0;
        }

        events.Add(new UnequipEvent
        {
            ActorId  = state.Player.Id,
            ItemId   = item.Id,
            ItemName = item.Name,
            Slot     = slot,
        });
    }

    private static void ResolveMonsterTurns(GameState state, List<TurnEvent> events)
    {
        // Snapshot the list — monsters may die during resolution (e.g. player bonus attacks
        // killing a monster before its turn, or future reflect damage). Iterating a snapshot
        // prevents collection-modified exceptions and mirrors the Python prototype's behavior.
        var monsters = state.AliveMonsters.ToList();

        foreach (var monster in monsters)
        {
            if (!monster.Require<Fighter>().IsAlive) continue;
            if (!state.PlayerFighter.IsAlive) break; // player died mid-turn — stop processing

            var action = MonsterAI.Decide(monster, state);

            switch (action.Kind)
            {
                case MonsterAction.ActionKind.Attack:
                    ResolveMonsterAttack(state, monster, action.Target!, events, isBonusAttack: false);
                    break;

                case MonsterAction.ActionKind.MoveTo:
                case MonsterAction.ActionKind.SeekItem:
                    // A* already computed the exact next step (adjacent tile), so MoveToward
                    // resolves directly without extra greedy computation.
                    int fromX = monster.X, fromY = monster.Y;
                    bool moved = state.Map.MoveToward(monster, action.TargetX, action.TargetY);
                    if (moved)
                    {
                        events.Add(new MoveEvent
                        {
                            ActorId = monster.Id,
                            FromX = fromX, FromY = fromY,
                            ToX = monster.X, ToY = monster.Y,
                        });
                    }
                    break;

                case MonsterAction.ActionKind.PickUp:
                    ResolveMonsterPickUp(state, monster, action.Target!, events);
                    break;

                case MonsterAction.ActionKind.UseItem:
                    ResolveMonsterItemUse(state, monster, action.Target!, events);
                    break;

                case MonsterAction.ActionKind.Wait:
                    break;
            }
        }
    }

    private static void ResolveMonsterAttack(GameState state, Entity monster, Entity target, List<TurnEvent> events, bool isBonusAttack)
    {
        var result = CombatResolver.ResolveAttack(monster, target, state.Rng);

        events.Add(new AttackEvent
        {
            ActorId = monster.Id,
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
            events.Add(new DeathEvent { ActorId = target.Id, KillerId = monster.Id });
            // target here is the player — players don't have equipment to drop
        }

        // Monster bonus attacks — recurse if triggered and target still alive
        if (result.BonusAttackTriggered && target.Require<Fighter>().IsAlive)
        {
            ResolveMonsterAttack(state, monster, target, events, isBonusAttack: true);
        }
    }

    /// <summary>
    /// Handle a monster picking up a floor item.
    ///
    /// Priority: auto-equip if the slot is empty and the item fits (weapon→MainHand, armor→Chest).
    /// If neither condition is met, add to the monster's inventory.
    /// Items that can't be stored (no equipment slot, inventory full) are left on the floor.
    /// </summary>
    private static void ResolveMonsterPickUp(GameState state, Entity monster, Entity item, List<TurnEvent> events)
    {
        // Verify the item is still on the floor (it may have been picked up in the same turn
        // by another monster in a future iteration — shouldn't happen with snapshot iteration
        // but guard defensively).
        if (!state.FloorItems.Contains(item)) return;

        var equippable = item.Get<Equippable>();
        var equipment = monster.Get<Equipment>();
        var inventory = monster.Get<Inventory>();

        bool picked = false;

        // Auto-equip weapons and armor into empty slots — this is what makes item-seekers
        // meaningful in combat: they arm themselves, not just hoard.
        if (equippable != null && equipment != null)
        {
            if (equippable.IsWeapon && equipment.MainHand == null)
            {
                equipment.SetSlot(EquipmentSlot.MainHand, item);
                picked = true;
            }
            else if (!equippable.IsWeapon && equippable.Slot == EquipmentSlot.Chest && equipment.Chest == null)
            {
                equipment.SetSlot(EquipmentSlot.Chest, item);
                picked = true;
            }
        }

        // Fall back to inventory for consumables, extras, or when equipment slot is occupied.
        if (!picked && inventory != null)
        {
            picked = inventory.Add(item);
        }

        if (!picked) return; // inventory full and no slot available — leave on floor

        state.FloorItems.Remove(item);
        state.Map.UnregisterEntity(item);

        events.Add(new PickUpEvent
        {
            ActorId = monster.Id,
            ItemId = item.Id,
            ItemName = item.Name,
        });
    }

    /// <summary>
    /// Resolve a monster's attempt to use an item from its inventory.
    ///
    /// Failure rates reflect monster intelligence — orcs fumble potions often,
    /// scrolls are nearly impossible without arcane training.
    /// Three failure modes keep even fumbles interesting:
    ///   fizzle          — wastes the turn and item, nothing happens
    ///   wrong_target    — healing hits the player instead (dangerous backfire)
    ///   equipment_damage — monster's weapon loses 1 DamageMax (weakens it mid-fight)
    ///
    /// Item is consumed regardless of success or failure — mirrors PoC item use logic.
    /// </summary>
    private static void ResolveMonsterItemUse(GameState state, Entity monster, Entity item, List<TurnEvent> events)
    {
        // Scrolls require a spell system — keep failure rate high so the framework
        // is wired but scrolls aren't meaningful until the spell system lands.
        const int ScrollFailurePercent = 75;
        const int PotionFailurePercent = 20;

        var consumable = item.Get<Consumable>();
        if (consumable == null) return;

        int failurePercent = consumable.IsHealing ? PotionFailurePercent : ScrollFailurePercent;
        bool success = state.Rng.Next(0, 100) >= failurePercent;

        string failureMode = "";
        int effectAmount   = 0;

        if (success)
        {
            if (consumable.IsHealing)
                effectAmount = monster.Require<Fighter>().Heal(consumable.HealAmount);
        }
        else
        {
            // Three equally probable failure modes — roll once into [0, 3).
            switch (state.Rng.Next(0, 3))
            {
                case 0:
                    // Fizzle — nothing happens, item still consumed.
                    failureMode = "fizzle";
                    break;

                case 1:
                    // Wrong target — healing applies to the player.
                    // Intentionally punishing: the monster heals its enemy.
                    failureMode = "wrong_target";
                    if (consumable.IsHealing)
                        effectAmount = state.PlayerFighter.Heal(consumable.HealAmount);
                    break;

                default:
                    // Equipment damage — main weapon loses 1 DamageMax.
                    // Guard: DamageMax must exceed DamageMin to preserve a valid damage range.
                    failureMode = "equipment_damage";
                    var equipment = monster.Get<Equipment>();
                    if (equipment?.MainHand != null)
                    {
                        var equippable = equipment.MainHand.Get<Equippable>();
                        if (equippable != null && equippable.DamageMax > equippable.DamageMin)
                        {
                            equippable.DamageMax--;
                            effectAmount = 1;
                        }
                    }
                    break;
            }
        }

        // Consume regardless of outcome — matches player potion consumption.
        consumable.StackSize--;
        if (consumable.StackSize <= 0)
            monster.Get<Inventory>()?.Remove(item);

        events.Add(new ItemUseEvent
        {
            ActorId      = monster.Id,
            ItemName     = item.Name,
            Success      = success,
            FailureMode  = failureMode,
            EffectAmount = effectAmount,
        });
    }

    /// <summary>
    /// Drop all equipped and carried items from a monster that just died.
    /// Items are placed at the monster's current position — floor items may stack,
    /// which is intentional (the PoC allows this; player picks up all on the tile).
    /// The monster entity itself is kept in state.Monsters so the death animation
    /// can still reference it — we only release its items.
    /// </summary>
    private static void DropMonsterLoot(GameState state, Entity monster, List<TurnEvent> events)
    {
        var equipment = monster.Get<Equipment>();
        var inventory = monster.Get<Inventory>();

        if (equipment == null && inventory == null) return;

        var itemsToDrop = new List<Entity>();

        if (equipment != null)
        {
            // Collect and clear all equipped slots
            foreach (EquipmentSlot slot in Enum.GetValues<EquipmentSlot>())
            {
                var item = equipment.GetSlot(slot);
                if (item != null)
                {
                    itemsToDrop.Add(item);
                    equipment.SetSlot(slot, null);
                }
            }
        }

        if (inventory != null)
        {
            foreach (var item in inventory.Items.ToList())
            {
                itemsToDrop.Add(item);
                inventory.Remove(item);
            }
        }

        foreach (var item in itemsToDrop)
        {
            item.X = monster.X;
            item.Y = monster.Y;
            state.FloorItems.Add(item);
            state.Map.RegisterEntity(item);

            events.Add(new DropEvent
            {
                ActorId = monster.Id,
                ItemId = item.Id,
                ItemName = item.Name,
            });
        }
    }
}
