using CatacombsOfYarl.Logic.AI;
using CatacombsOfYarl.Logic.Combat;
using CatacombsOfYarl.Logic.Combat.StatusEffects;
using CatacombsOfYarl.Logic.Content;
using CatacombsOfYarl.Logic.ECS;
using CatacombsOfYarl.Logic.Knowledge;

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
    ///
    /// monsterFactory: required for split spawning. When null (most test environments),
    /// a split falls back to a kill (HP=0, DeathEvent) with no children spawned.
    /// All existing call sites that omit this parameter retain correct behavior.
    ///
    /// portalEntityFactory: required for portal placement (Wand of Portals). When null,
    /// portal cast actions silently do nothing. Tests that exercise portals must inject this.
    /// </summary>
    public static TurnResult ProcessTurn(GameState state, PlayerAction action,
        MonsterFactory? monsterFactory = null,
        EntityFactory? portalEntityFactory = null)
    {
        var events = new List<TurnEvent>();
        state.TurnCount++;

        // === PLAYER TURN ===
        // Process start-of-turn effects: DOT/HOT ticks, skip-turn determination.
        // If the player's turn is skipped (slowed, immobilized, asleep), skip the action.
        // ProcessTurnStart fires BEFORE the action; ProcessTurnEnd fires AFTER.
        // This means effects applied DURING a player action (e.g. a misfire applying
        // DisorientationEffect to the player) are decremented on the NEXT turn — not this one —
        // because ProcessTurnEnd has already run for this entity before the action.
        //
        // Effects applied to MONSTERS during the player's action (e.g. Fear scroll) ARE
        // decremented in the same round by the monster's ProcessTurnEnd at the end of its turn.
        // This is correct: the monster takes its full turn before the round ends.
        bool playerSkipTurn = StatusEffectProcessor.ProcessTurnStart(state.Player, events, state.TurnCount);
        if (!playerSkipTurn)
            ResolvePlayerAction(state, action, events, monsterFactory, portalEntityFactory);
        StatusEffectProcessor.ProcessTurnEnd(state.Player, events);

        // Ring of Regeneration: passive heal every 5 turns (not turn 0).
        // Checked after the player acts so the heal happens at the end of their action phase.
        // Using TurnCount % 5 == 0 matches PoC ring.py passive tick logic.
        // Two regen rings heal twice (we count both slots).
        if (state.TurnCount > 0 && state.TurnCount % 5 == 0)
        {
            int regenCount = CountRingEffect(state.Player.Get<Equipment>(), RingEffectKind.Regeneration);
            if (regenCount > 0)
            {
                var regenFighter = state.PlayerFighter;
                for (int r = 0; r < regenCount; r++)
                {
                    int healed = regenFighter.Heal(1);
                    if (healed > 0)
                        events.Add(new HotHealEvent
                        {
                            ActorId  = state.Player.Id,
                            EntityId = state.Player.Id,
                            EffectName = "ring_of_regeneration",
                            Amount   = healed,
                        });
                }
            }
        }

        state.RecomputeFov(); // update FOV after player moves (no-op in scenario mode)

        // === MONSTER TURNS ===
        // Skip monster turns on successful Descend — the floor transition is handled
        // by the presentation layer. Monsters should not get a free attack as the
        // player steps through the stair.
        bool descended = events.Any(e => e is DescendEvent);
        if (descended)
            state.Corpses.Clear(); // Corpses don't follow the player to the next floor
        if (!descended && state.PlayerFighter.IsAlive)
        {
            ResolveMonsterTurns(state, events, portalEntityFactory);
            TickEnvironment(state, events, monsterFactory);
            state.RecomputeFov(); // update FOV after monsters move (no-op in scenario mode)
        }

        // Clear portal UsedThisTurn flags at end of turn so portals can fire again next turn.
        // This is a no-op when no portals are active.
        PortalSystem.ClearPortalUsedFlags(state);

        // === KNOWLEDGE UPDATE ===
        // Update monster knowledge after all combat events are resolved.
        // Build a lookup of all monsters (including dead ones still in state.Monsters) so we
        // can resolve species IDs from entity IDs in AttackEvent and DeathEvent.
        UpdateKnowledge(state, events);

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

    /// <summary>
    /// Update MonsterKnowledgeSystem from the turn's events and current FOV.
    ///
    /// Three update sources:
    ///   1. AttackEvent where actor or target is a monster → RecordEngaged
    ///   2. DeathEvent for a monster → RecordKilled
    ///   3. FOV scan: all currently visible alive monsters → RecordSeen
    ///
    /// Uses entity ID lookup to find the SpeciesTag on each monster.
    /// If a monster has no SpeciesTag (hand-constructed in tests), the update is skipped silently.
    /// </summary>
    private static void UpdateKnowledge(GameState state, List<TurnEvent> events)
    {
        var knowledge = state.Knowledge;

        // Build id→entity map once. Include all monsters (dead ones may appear in DeathEvent).
        // Use a manual loop rather than ToDictionary to safely handle rare duplicate IDs — these
        // can occur in split tests where hand-constructed entities share IDs with factory children.
        // Last-entry wins (children overwrite the dead original, which is fine for knowledge purposes).
        var monsterById = new Dictionary<int, Entity>(state.Monsters.Count);
        foreach (var m in state.Monsters)
            monsterById[m.Id] = m;
        int playerId = state.Player.Id;

        foreach (var evt in events)
        {
            switch (evt)
            {
                case AttackEvent atk:
                    // Player attacked a monster, or a monster attacked the player.
                    // Both directions count as an engagement for that species.
                    if (atk.ActorId != playerId && monsterById.TryGetValue(atk.ActorId, out var attacker))
                    {
                        var tag = attacker.Get<SpeciesTag>();
                        if (tag != null) knowledge.RecordEngaged(tag.TypeId);
                    }
                    if (atk.TargetId != playerId && monsterById.TryGetValue(atk.TargetId, out var target))
                    {
                        var tag = target.Get<SpeciesTag>();
                        if (tag != null) knowledge.RecordEngaged(tag.TypeId);
                    }
                    break;

                case DeathEvent death:
                    // Only count monster deaths (not the player's own death).
                    if (death.ActorId != playerId && monsterById.TryGetValue(death.ActorId, out var dead))
                    {
                        var tag = dead.Get<SpeciesTag>();
                        if (tag != null) knowledge.RecordKilled(tag.TypeId);
                    }
                    break;
            }
        }

        // FOV: record seen for all monsters currently visible. In scenario mode (IsDungeonMode=false),
        // IsVisible returns true for all tiles, so all alive monsters get RecordSeen every turn.
        // This is intentional — scenario mode isn't bounded by FOV, and RecordSeen is idempotent
        // in effect (tier only advances, never regresses). In dungeon mode, only visible monsters count.
        foreach (var monster in state.AliveMonsters)
        {
            if (state.Map.IsVisible(monster.X, monster.Y))
            {
                var tag = monster.Get<SpeciesTag>();
                if (tag != null) knowledge.RecordSeen(tag.TypeId);
            }
        }
    }

    private static void ResolvePlayerAction(GameState state, PlayerAction action, List<TurnEvent> events,
        MonsterFactory? monsterFactory, EntityFactory? portalEntityFactory)
    {
        var player = state.Player;

        switch (action.Kind)
        {
            case PlayerAction.ActionKind.Attack:
                ResolvePlayerAttack(state, action.Target!, events, isBonusAttack: false, monsterFactory);
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

            case PlayerAction.ActionKind.CastSpell:
                ResolveSpellAction(state, action, events, portalEntityFactory);
                player.Get<SpeedBonusTracker>()?.ResetMomentum();
                break;

            case PlayerAction.ActionKind.ThrowItem:
                ResolveThrowItem(state, action, events);
                // Note: ThrowResolver.Resolve already calls ResetMomentum internally.
                // No second reset needed here.
                break;
        }
    }

    /// <summary>
    /// Resolve a throw action. Delegates to ThrowResolver which handles all three paths
    /// (potion, weapon, junk). The monsterFactory is not needed for throws — death from
    /// thrown weapons follows the spell-kill pattern (DeathEvent only, no loot/corpse here).
    /// </summary>
    private static void ResolveThrowItem(GameState state, PlayerAction action, List<TurnEvent> events)
    {
        var item = action.Item;
        if (item == null) return;
        if (!action.TargetX.HasValue || !action.TargetY.HasValue) return;

        var throwEvents = ThrowResolver.Resolve(
            state.Player,
            item,
            action.TargetX.Value,
            action.TargetY.Value,
            state);

        events.AddRange(throwEvents);
    }

    /// <summary>
    /// Resolve a scroll or wand use action.
    ///
    /// Flow:
    ///   1. Locate the SpellEffect component on the item — bail if missing.
    ///   2. If item has WandComponent: consume a charge. If out of charges, emit WandUseEvent(Success=false) and stop.
    ///   3. If item has Consumable (scroll): decrement stack, remove entity from inventory when depleted.
    ///   4. Delegate to SpellResolver.Resolve with the target info from the action.
    ///      Exception: Portal targeting mode is handled here via PortalSystem.PlacePortals —
    ///      SpellResolver does not have an EntityFactory, so portal placement is TurnController's job.
    ///   5. If wand, emit WandUseEvent with remaining charges (including destroyed=true if charges hit 0).
    ///   6. Also handle wand auto-recharge on scroll pickup (called from TryPickUpItemsAt).
    /// </summary>
    private static void ResolveSpellAction(GameState state, PlayerAction action, List<TurnEvent> events,
        EntityFactory? portalEntityFactory = null)
    {
        var item = action.Item;
        if (item == null) return;

        var spell = item.Get<SpellEffect>();
        if (spell == null) return;

        // SilencedEffect: blocks scroll AND wand use. Does NOT block potions or melee.
        // Potions are physical (swallowed), not magical (spoken) — silence doesn't stop drinking.
        // Gate here before charges or consumables are spent, so the player isn't charged for a blocked action.
        bool isPotion = item.Get<Consumable>()?.IsPotion == true;
        if (state.Player.Has<SilencedEffect>() && !isPotion)
            return;

        var wand = item.Get<WandComponent>();
        var consumable = item.Get<Consumable>();

        // ── Wand: check + consume charge ─────────────────────────────────────
        if (wand != null)
        {
            if (!wand.HasCharges)
            {
                events.Add(new WandUseEvent
                {
                    ActorId = state.Player.Id,
                    WandName = item.Name,
                    RemainingCharges = 0,
                    Success = false,
                });
                return;
            }

            wand.TryConsume();
        }

        // ── Scroll: consume one stack ─────────────────────────────────────────
        if (consumable != null)
        {
            var inventory = state.PlayerInventory;
            if (inventory != null)
            {
                consumable.StackSize--;
                if (consumable.StackSize <= 0)
                    inventory.Remove(item);
            }
        }

        // ── InvisibilityEffect break on spell cast ────────────────────────────
        // InvisibilityEffect breaks when the player casts a spell (scroll or wand).
        // Does NOT break on drinking a potion — potions are physical, not magical.
        // DOES break on throwing a potion — throwing at a target is an offensive action.
        // PoC-verified: invisibility persists through potion drinks, ends on offensive actions.
        bool throwingPotion = isPotion && action.TargetEntityId.HasValue;
        bool breaksInvisibility = !isPotion || throwingPotion;
        if (state.Player.Has<InvisibilityEffect>() && breaksInvisibility)
        {
            state.Player.Remove<InvisibilityEffect>();
            events.Add(new StatusExpiredEvent
            {
                ActorId = state.Player.Id,
                EntityId = state.Player.Id,
                EffectName = "invisibility",
                Reason = throwingPotion ? "threw_potion" : "cast_spell",
            });
        }

        // ── Resolve spell ─────────────────────────────────────────────────────
        // Portal casting is handled here (not SpellResolver) because it needs an EntityFactory.
        // All other targeting modes delegate to SpellResolver.
        if (spell.SpellId == "portal")
        {
            if (portalEntityFactory != null)
            {
                var portalEvents = PortalSystem.HandlePortalCast(
                    state.Player,
                    state,
                    item,
                    targetX: action.TargetX,
                    targetY: action.TargetY,
                    entityFactory: portalEntityFactory);

                if (portalEvents != null)
                    events.AddRange(portalEvents);
            }
            // If no factory: silently no-op (tests that don't exercise portals).
        }
        else
        {
            // Throwable potions: the item's primary SpellId is the drink spell (e.g., "drink_weakness").
            // When the player throws at a target (TargetEntityId is set), use ThrowSpellId instead
            // (e.g., "throw_weakness") so SpellResolver applies the effect to the target, not the caster.
            // Drink path (no TargetEntityId): overrideSpellId is null, SpellResolver uses spell.SpellId.
            string? overrideSpellId = null;
            if (action.TargetEntityId.HasValue && !string.IsNullOrEmpty(spell.ThrowSpellId))
                overrideSpellId = spell.ThrowSpellId;

            var spellEvents = SpellResolver.Resolve(
                state.Player,
                spell,
                state,
                targetEntityId: action.TargetEntityId,
                targetX: action.TargetX,
                targetY: action.TargetY,
                overrideSpellId: overrideSpellId);

            events.AddRange(spellEvents);
        }

        // ── Wand post-use: emit charge event ──────────────────────────────────
        if (wand != null)
        {
            bool destroyed = !wand.Infinite && wand.Charges <= 0;

            events.Add(new WandUseEvent
            {
                ActorId = state.Player.Id,
                WandName = item.Name,
                RemainingCharges = wand.Infinite ? int.MaxValue : wand.Charges,
                Success = true,
                WandDestroyed = destroyed,
            });

            // Remove depleted wand from inventory
            if (destroyed)
            {
                state.PlayerInventory?.Remove(item);
            }
        }

        // Identification on use: scrolls and wands are identified when used.
        // Spell effects fire first, then identification check, then toast if newly identified.
        TryIdentifyOnUse(state, item, events, trigger: "used");
    }

    private static void ResolvePlayerAttack(GameState state, Entity target, List<TurnEvent> events,
        bool isBonusAttack, MonsterFactory? monsterFactory)
    {
        var player = state.Player;

        // ImmobilizedEffect: cannot attack (or move, or cast — all actions blocked).
        // ProcessTurnStart already returns skipTurn=true for this, so in normal flow this
        // branch should not fire. Kept as an explicit guard for safety.
        if (player.Has<ImmobilizedEffect>())
            return;

        // DisarmedEffect: weapon attack is cancelled. Emit a failed attack event.
        // Does not prevent unarmed attacks if the player has no weapon equipped.
        var equipment = player.Get<Equipment>();
        bool hasWeaponEquipped = equipment?.MainHand != null;
        if (player.Has<DisarmedEffect>() && hasWeaponEquipped)
        {
            events.Add(new AttackEvent
            {
                ActorId = player.Id,
                TargetId = target.Id,
                Hit = false,
                Damage = 0,
                IsCritical = false,
                IsFumble = false,
                TargetKilled = false,
                IsBonusAttack = isBonusAttack,
                FailReason = "disarmed",
            });
            return;
        }

        // InvisibilityEffect breaks when the player makes any attack (PoC-verified).
        // NOT broken by taking damage or using items. Breaks before the attack resolves
        // so monsters can respond after the reveal.
        if (player.Has<InvisibilityEffect>())
        {
            player.Remove<InvisibilityEffect>();
            events.Add(new StatusExpiredEvent
            {
                ActorId = player.Id,
                EntityId = player.Id,
                EffectName = "invisibility",
                Reason = "attacked",
            });
        }

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

        if (result.Hit)
        {
            // Wake sleeping targets on attack damage (NOT DOT — PoC-verified).
            StatusEffectProcessor.OnDamageTaken(target, events);

            // Check split-under-pressure BEFORE death check — split wins over kill.
            // Only check on a hit because the HP hasn't changed on a miss.
            var splitTracker = target.Get<SplitTracker>();
            if (splitTracker != null && !splitTracker.HasSplit)
            {
                var tFighter = target.Require<Fighter>();
                double hpPct = tFighter.MaxHp > 0 ? (double)tFighter.Hp / tFighter.MaxHp : 0;
                if (hpPct < splitTracker.TriggerHpPct)
                {
                    splitTracker.HasSplit = true;
                    ResolveSplit(state, target, splitTracker, monsterFactory, events);
                    return; // original is gone — skip death processing
                }
            }
        }

        if (result.TargetKilled)
        {
            events.Add(new DeathEvent { ActorId = target.Id, KillerId = player.Id });
            DropMonsterLoot(state, target, events);
            TransformToCorpse(state, target, events, monsterFactory);
        }

        // Bonus attack chain — recurse if triggered and target still alive
        if (result.BonusAttackTriggered && !result.TargetKilled && target.Require<Fighter>().IsAlive)
        {
            ResolvePlayerAttack(state, target, events, isBonusAttack: true, monsterFactory);
        }
    }

    /// <summary>
    /// Resolve a split-under-pressure event. Original monster is removed and children are spawned.
    ///
    /// Null-factory fallback: test environments that don't inject a factory get a kill instead of
    /// a spawn — HP=0, emit DeathEvent. No crash, just no children.
    ///
    /// Children act on the spawn turn because they are added to state.Monsters before
    /// ResolveMonsterTurns completes. The AliveMonsters cache rebuilds on the next access.
    /// This is intentional: creates a dramatic "suddenly surrounded" moment matching PoC behavior.
    /// </summary>
    private static void ResolveSplit(GameState state, Entity original, SplitTracker split,
        MonsterFactory? monsterFactory, List<TurnEvent> events)
    {
        if (monsterFactory == null)
        {
            // No factory available — treat as a kill so tests that don't inject a factory
            // still see deterministic behavior (original dies, no children).
            original.Require<Fighter>().Hp = 0;
            events.Add(new DeathEvent { ActorId = original.Id, KillerId = state.Player.Id });
            TransformToCorpse(state, original, events, monsterFactory: null);
            return;
        }

        int numChildren = RollSplitChildren(split, state.Rng);
        var positions = FindSplitPositions(state.Map, original.X, original.Y, numChildren, state);

        // Remove original from the map (HP=0 marks it dead for AliveMonsters cache).
        // No XP event — split is not a kill.
        original.Require<Fighter>().Hp = 0;
        state.Map.UnregisterEntity(original);

        var childIds = new List<int>();
        for (int i = 0; i < Math.Min(numChildren, positions.Count); i++)
        {
            var child = monsterFactory.Create(
                split.ChildType,
                positions[i].X, positions[i].Y,
                state.CurrentDepth,
                state.Rng);
            if (child == null) continue;

            state.Monsters.Add(child);
            state.Map.RegisterEntity(child);
            childIds.Add(child.Id);
        }

        events.Add(new SplitEvent
        {
            ActorId = original.Id,
            OriginalId = original.Id,
            ChildIds = childIds,
        });
    }

    /// <summary>
    /// Roll the number of children to spawn, using the split tracker's weight table if present.
    /// </summary>
    private static int RollSplitChildren(SplitTracker split, SeededRandom rng)
    {
        if (split.Weights == null || split.Weights.Length == 0)
            return rng.Next(split.MinChildren, split.MaxChildren + 1);

        int total = split.Weights.Sum();
        int roll = rng.Next(total);
        int running = 0;
        for (int i = 0; i < split.Weights.Length; i++)
        {
            running += split.Weights[i];
            if (roll < running)
                return split.MinChildren + i;
        }
        return split.MaxChildren;
    }

    /// <summary>
    /// Find valid spawn positions for split children using an expanding ring search.
    /// Mirrors PoC's _get_valid_spawn_positions. Fallback: if no positions found,
    /// returns origin position (children stack on top — unusual but not a crash).
    /// </summary>
    private static List<(int X, int Y)> FindSplitPositions(
        GameMap map, int cx, int cy, int count, GameState state)
    {
        var found = new List<(int X, int Y)>();
        var occupied = new HashSet<(int, int)>(
            state.Monsters
                .Where(m => m.Require<Fighter>().IsAlive)
                .Select(m => (m.X, m.Y)));
        occupied.Add((state.Player.X, state.Player.Y));

        for (int radius = 1; radius <= 3 && found.Count < count; radius++)
        {
            for (int dx = -radius; dx <= radius && found.Count < count; dx++)
            for (int dy = -radius; dy <= radius && found.Count < count; dy++)
            {
                // Only walk the ring perimeter, not the interior
                if (Math.Abs(dx) != radius && Math.Abs(dy) != radius) continue;
                int nx = cx + dx, ny = cy + dy;
                if (map.IsWalkable(nx, ny) && !occupied.Contains((nx, ny)))
                {
                    found.Add((nx, ny));
                    occupied.Add((nx, ny)); // reserve so next child doesn't pick the same spot
                }
            }
        }

        if (found.Count == 0) found.Add((cx, cy)); // fallback: stack on origin
        return found;
    }

    private static void ResolvePlayerMove(GameState state, PlayerAction action, List<TurnEvent> events)
    {
        var player = state.Player;
        int fromX = player.X, fromY = player.Y;

        // EntangledEffect: player cannot move. CAN still attack (that's in ResolvePlayerAttack).
        if (player.Has<EntangledEffect>())
        {
            // Emit wait-equivalent (no movement), consume the turn.
            events.Add(new WaitEvent { ActorId = player.Id });
            return;
        }

        // DisorientationEffect: player's intended direction is replaced with a random direction.
        // The move still consumes a turn — player taps, the character stumbles elsewhere.
        // If the random direction hits a wall, no movement occurs (same as normal wall bump).
        bool moved;
        if (player.Has<DisorientationEffect>())
        {
            // Determine the intended destination so we can pick a random direction instead.
            int destX = action.TargetX ?? (action.Target?.X ?? player.X);
            int destY = action.TargetY ?? (action.Target?.Y ?? player.Y);

            // Pick a random cardinal/diagonal direction — using game RNG for determinism.
            var directions = new (int dx, int dy)[]
            {
                (-1, -1), (0, -1), (1, -1),
                (-1,  0),          (1,  0),
                (-1,  1), (0,  1), (1,  1),
            };
            int idx = state.Rng.Next(0, directions.Length);
            var (rdx, rdy) = directions[idx];
            int randomDestX = player.X + rdx;
            int randomDestY = player.Y + rdy;

            moved = state.Map.MoveToward(player, randomDestX, randomDestY);
        }
        else if (action.Target != null)
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

            // Portal collision: check if player stepped onto a portal and teleport if so.
            // Runs before stair check so portals near stairs don't cause confusion.
            var portalTeleport = PortalSystem.CheckPortalCollision(player, state);
            if (portalTeleport != null)
                events.Add(portalTeleport);

            // Stair reached: stop auto-explore so the player must consciously tap to descend.
            // Auto-descend would swallow floors unintentionally during explore mode.
            if (state.IsDungeonMode && state.PlayerOnStairDown)
            {
                var ae = state.Player.Get<AutoExploreState>();
                if (ae != null && ae.IsActive)
                    AutoExploreSystem.Stop(ae, "Reached stairs");
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
            // Wand auto-recharge: if the item is a scroll with a SpellEffect, check whether
            // the player holds a wand whose RechargeScrollId matches. If so, consume the scroll
            // to add one charge instead of placing it in inventory.
            var spellEffect = item.Get<SpellEffect>();
            if (spellEffect != null && TryRechargeWand(state, item, spellEffect, events))
            {
                // Scroll was consumed for recharge — remove from floor, do NOT add to inventory.
                state.FloorItems.Remove(item);
                state.Map.UnregisterEntity(item);
                continue;
            }

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
                ItemName = ItemDisplay.GetDisplayName(item, state.IdentificationRegistry, state.AppearancePool),
            });
        }
    }

    /// <summary>
    /// Check whether the item's type needs to be identified after a use/equip action.
    /// If the type is newly identified, emits an IdentificationEvent.
    ///
    /// No-op when the state has no identification registry (scenario/harness mode)
    /// or when the item has no ItemTag (weapons/armor — always identified).
    /// </summary>
    private static void TryIdentifyOnUse(GameState state, Entity item, List<TurnEvent> events, string trigger)
    {
        var registry = state.IdentificationRegistry;
        if (registry == null) return;

        var tag = item.Get<ECS.ItemTag>();
        if (tag == null) return;

        var idComp = item.Get<ECS.IdentifiableItem>();
        if (idComp == null) return;

        // Identify returns true only the FIRST time this type is identified this run.
        bool newlyIdentified = registry.Identify(tag.TypeId);
        if (newlyIdentified)
        {
            events.Add(new IdentificationEvent
            {
                ActorId        = state.Player.Id,
                TypeId         = tag.TypeId,
                IdentifiedName = idComp.IdentifiedName,
                Trigger        = trigger,
            });
        }
    }

    /// <summary>
    /// Check if a picked-up scroll should auto-recharge a wand the player is carrying.
    /// Returns true if the scroll was consumed for recharge (caller should skip normal pickup).
    ///
    /// Auto-recharge rule: if the player's inventory contains a wand whose RechargeScrollId
    /// matches the picked-up scroll's SpellId, and that wand is below MaxCharges, consume
    /// the scroll to add one charge instead of adding it to inventory.
    ///
    /// Gate: both scroll and wand must be identified. An unidentified scroll cannot be
    /// absorbed by an unidentified wand — the magical concealment prevents it.
    /// </summary>
    private static bool TryRechargeWand(GameState state, Entity scroll, SpellEffect scrollSpell,
        List<TurnEvent> events)
    {
        var inventory = state.PlayerInventory;
        if (inventory == null) return false;

        // Identification gate: an unidentified scroll cannot auto-recharge an unidentified wand.
        // The player doesn't know what either item is, so the wand doesn't "know" to accept it.
        // When the registry is null (scenario mode), identification is off and recharge always fires.
        var registry = state.IdentificationRegistry;
        if (registry != null)
        {
            var scrollTag = scroll.Get<ECS.ItemTag>();
            if (scrollTag != null && !registry.IsIdentified(scrollTag.TypeId))
                return false; // Unidentified scroll goes to inventory normally
        }

        // Find a wand in inventory that lists this scroll's spell_id as its recharge source
        var wand = inventory.Items.FirstOrDefault(item =>
        {
            var w = item.Get<WandComponent>();
            if (w == null || w.Infinite || w.RechargeScrollId != scrollSpell.SpellId || w.Charges >= w.MaxCharges)
                return false;

            // Identification gate: wand must also be identified for auto-recharge to fire.
            if (registry != null)
            {
                var wandTag = item.Get<ECS.ItemTag>();
                if (wandTag != null && !registry.IsIdentified(wandTag.TypeId))
                    return false;
            }

            return true;
        });

        if (wand == null) return false;

        var wandComp = wand.Require<WandComponent>();
        wandComp.Charges++;

        events.Add(new WandRechargeEvent
        {
            ActorId = state.Player.Id,
            WandName = wand.Name,
            ScrollName = scroll.Name,
            NewCharges = wandComp.Charges,
        });

        return true;
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
            ItemName = ItemDisplay.GetDisplayName(potion, state.IdentificationRegistry, state.AppearancePool),
        });

        // Identification on use: potions are identified when consumed.
        // Effect fires first (heal), then identification check, then toast if newly identified.
        TryIdentifyOnUse(state, potion, events, trigger: "used");
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

        // Ring slot auto-assignment: all rings are created with slot=LeftRing.
        // If LeftRing is occupied but RightRing is free, auto-redirect to RightRing.
        // This prevents forcing the player to manually juggle left vs. right.
        var targetSlot = equippable.Slot;
        if (targetSlot == EquipmentSlot.LeftRing && equipment.LeftRing != null && equipment.RightRing == null)
            targetSlot = EquipmentSlot.RightRing;

        var displaced = equipment.SetSlot(targetSlot, item);

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
        if (targetSlot == EquipmentSlot.MainHand)
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

        // If a ring was displaced, reverse its effect before applying the new ring's effect.
        // This ensures stat accounting stays correct when swapping rings.
        if (displaced != null && (targetSlot == EquipmentSlot.LeftRing || targetSlot == EquipmentSlot.RightRing))
        {
            var displacedEffect = displaced.Get<RingEffectComponent>();
            if (displacedEffect != null)
                ApplyRingEffect(state.Player, displacedEffect, equip: false, events);
        }

        // Apply equip effect for rings
        if (targetSlot == EquipmentSlot.LeftRing || targetSlot == EquipmentSlot.RightRing)
        {
            var ringEffect = item.Get<RingEffectComponent>();
            if (ringEffect != null)
                ApplyRingEffect(state.Player, ringEffect, equip: true, events);
        }

        events.Add(new EquipEvent
        {
            ActorId          = state.Player.Id,
            ItemId           = item.Id,
            ItemName         = item.Name,
            Slot             = targetSlot,
            DisplacedItemId  = displacedId,
            DisplacedItemName = displacedName,
        });

        // Identification on equip: rings are identified when equipped.
        // EquipEvent fires first, then identification check, then toast if newly identified.
        TryIdentifyOnUse(state, item, events, trigger: "equipped");
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

        // Reverse ring effects on unequip
        if (slot == EquipmentSlot.LeftRing || slot == EquipmentSlot.RightRing)
        {
            var ringEffect = item.Get<RingEffectComponent>();
            if (ringEffect != null)
                ApplyRingEffect(state.Player, ringEffect, equip: false, events);
        }

        events.Add(new UnequipEvent
        {
            ActorId  = state.Player.Id,
            ItemId   = item.Id,
            ItemName = item.Name,
            Slot     = slot,
        });
    }

    /// <summary>
    /// Environment phase: tick all active ground hazards, apply damage to any entity
    /// standing on a hazard tile, then age and expire the hazards.
    ///
    /// Runs after monster turns, before FOV recompute. Applies to player AND monsters.
    /// Damage decays linearly each tick: floor(base × remaining / max).
    /// Monster deaths from hazards are fully resolved (loot drop, corpse transform).
    /// </summary>
    private static void TickEnvironment(GameState state, List<TurnEvent> events,
        MonsterFactory? monsterFactory)
    {
        var manager = state.GroundHazards;
        if (manager.Hazards.Count == 0) return;

        // Snapshot so we don't mutate while iterating.
        var activeHazards = manager.Hazards.Values.ToList();

        // Clear JustPlaced flag on newly-placed hazards before damage/aging so they are
        // ready to tick from next turn. Don't damage or age them this turn.
        var toTickNow = new List<GroundHazard>(activeHazards.Count);
        foreach (var hazard in activeHazards)
        {
            if (hazard.JustPlaced) { hazard.JustPlaced = false; continue; }
            toTickNow.Add(hazard);
        }

        foreach (var hazard in toTickNow)
        {
            int dmg = hazard.CurrentDamage;
            if (dmg <= 0) continue;

            string effectName = hazard.Type == HazardType.Fire ? "fire" : "poison gas";

            // Player on this tile?
            var pf = state.PlayerFighter;
            if (pf.IsAlive && state.Player.X == hazard.X && state.Player.Y == hazard.Y)
            {
                pf.TakeDamage(dmg);
                events.Add(new DotDamageEvent
                {
                    ActorId    = state.Player.Id,
                    EntityId   = state.Player.Id,
                    EffectName = effectName,
                    Damage     = dmg,
                });
                if (!pf.IsAlive)
                    events.Add(new DeathEvent { ActorId = state.Player.Id, KillerId = -1 });
            }

            // Monsters on this tile?
            foreach (var monster in state.AliveMonsters.ToList())
            {
                if (monster.X != hazard.X || monster.Y != hazard.Y) continue;
                var mf = monster.Require<Fighter>();
                if (!mf.IsAlive) continue;

                mf.TakeDamage(dmg);
                events.Add(new DotDamageEvent
                {
                    ActorId    = monster.Id,
                    EntityId   = monster.Id,
                    EffectName = effectName,
                    Damage     = dmg,
                });
                if (!mf.IsAlive)
                {
                    events.Add(new DeathEvent { ActorId = monster.Id, KillerId = -1 });
                    DropMonsterLoot(state, monster, events);
                    TransformToCorpse(state, monster, events, monsterFactory);
                }
            }
        }

        // Age only hazards that ticked this turn; newly-placed ones are untouched.
        foreach (var hazard in toTickNow)
            hazard.RemainingTurns--;
        manager.RemoveExpired();
    }

    private static void ResolveMonsterTurns(GameState state, List<TurnEvent> events,
        EntityFactory? portalEntityFactory = null)
    {
        // Snapshot the list — monsters may die during resolution (e.g. player bonus attacks
        // killing a monster before its turn, or future reflect damage). Iterating a snapshot
        // prevents collection-modified exceptions and mirrors the Python prototype's behavior.
        var monsters = state.AliveMonsters.ToList();

        foreach (var monster in monsters)
        {
            if (!monster.Require<Fighter>().IsAlive) continue;
            if (!state.PlayerFighter.IsAlive) break; // player died mid-turn — stop processing

            // Process start-of-turn effects: DOT/HOT ticks, skip-turn determination.
            bool monsterSkipTurn = StatusEffectProcessor.ProcessTurnStart(monster, events, state.TurnCount);
            if (monsterSkipTurn)
            {
                // Still decrement durations even on a skipped turn — time passes for sleeping/immobilized entities.
                StatusEffectProcessor.ProcessTurnEnd(monster, events);
                continue;
            }

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

                        // Portal collision: monsters can also use portals.
                        var monsterPortalTeleport = PortalSystem.CheckPortalCollision(monster, state);
                        if (monsterPortalTeleport != null)
                            events.Add(monsterPortalTeleport);
                    }
                    break;

                case MonsterAction.ActionKind.PickUp:
                    ResolveMonsterPickUp(state, monster, action.Target!, events);
                    break;

                case MonsterAction.ActionKind.UseItem:
                    ResolveMonsterItemUse(state, monster, action.Target!, events);
                    break;

                case MonsterAction.ActionKind.RaiseDead:
                    ResolveNecromancerRaise(state, monster, action.Target!, events);
                    break;

                case MonsterAction.ActionKind.Wait:
                    break;
            }

            // Decrement duration for all monster effects after it acts.
            StatusEffectProcessor.ProcessTurnEnd(monster, events);
        }
    }

    /// <summary>
    /// Necromancer raises a fresh corpse in-place. Sets the raise cooldown and emits RaiseDeadEvent.
    /// For plague_necromancer, adds plague_carrier tag and a small stat boost to the raised entity.
    /// </summary>
    private static void ResolveNecromancerRaise(
        GameState state, Entity necromancer, Entity corpse, List<TurnEvent> events)
    {
        var necComp = necromancer.Get<NecromancerAiComponent>();
        var corpseComp = corpse.Get<CorpseComponent>();
        if (necComp == null || corpseComp == null || !corpseComp.CanBeRaised) return;

        string corpseId = corpseComp.CorpseId;
        string raisedFaction = necromancer.Get<AiComponent>()?.Faction ?? "neutral";

        RaiseDeadResolver.Raise(corpse, raisedFaction, state);

        // Plague necromancer: add plague_carrier tag + small stat boost to raised entity
        if (string.Equals(necromancer.Get<AiComponent>()?.AiType, "plague_necromancer",
                StringComparison.OrdinalIgnoreCase))
        {
            var raisedFighter = corpse.Get<Fighter>();
            if (raisedFighter != null)
            {
                // PoC plague_necromancer_ai.py: +25% HP, add plague_carrier to tags
                raisedFighter.Hp = (int)Math.Round(raisedFighter.Hp * 1.25);
            }
            var raisedAi = corpse.Get<AiComponent>();
            if (raisedAi != null && !raisedAi.Tags.Contains("plague_carrier"))
                raisedAi.Tags.Add("plague_carrier");
        }

        necComp.CooldownRemaining = necComp.RaiseCooldown;

        events.Add(new RaiseDeadEvent
        {
            ActorId = necromancer.Id,
            RaisedEntityId = corpse.Id,
            CorpseId = corpseId,
            AssignedFaction = raisedFaction,
        });
    }

    private static void ResolveMonsterAttack(GameState state, Entity monster, Entity target, List<TurnEvent> events, bool isBonusAttack)
    {
        // DisarmedEffect: weapon attack cancelled — emit failure event, do not resolve.
        // Does not prevent unarmed attacks (if no weapon equipped).
        var monEquip = monster.Get<Equipment>();
        bool monHasWeapon = monEquip?.MainHand != null;
        if (monster.Has<DisarmedEffect>() && monHasWeapon)
        {
            events.Add(new AttackEvent
            {
                ActorId = monster.Id,
                TargetId = target.Id,
                Hit = false,
                Damage = 0,
                IsCritical = false,
                IsFumble = false,
                TargetKilled = false,
                IsBonusAttack = isBonusAttack,
                FailReason = "disarmed",
            });
            return;
        }

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

        if (result.Hit)
        {
            // Wake sleeping target on attack damage (NOT DOT — PoC-verified).
            StatusEffectProcessor.OnDamageTaken(target, events);
        }

        if (result.TargetKilled)
        {
            events.Add(new DeathEvent { ActorId = target.Id, KillerId = monster.Id });
            // target here is the player — players don't have equipment to drop
        }
        else if (result.Hit)
        {
            // Corrosion check — acidic monsters (slimes) degrade metal weapons on hit
            var corrosion = monster.Get<CorrosionComponent>();
            if (corrosion != null)
                ResolveCorrosion(state, monster, corrosion.Chance, state.Rng, events);

            // On-hit status effect (cave_spider=poison, web_spider=slowed, fire_beetle=burning)
            var onHit = monster.Get<OnHitEffectComponent>();
            if (onHit != null)
                ResolveOnHitEffect(target, onHit, events);
        }

        // Ring of Teleportation: 20% on-hit, player teleports to a random open tile.
        // Cancels the bonus attack chain — returning here means no recursion.
        // Two teleportation rings each get an independent roll (36% effective chance).
        if (result.Hit && !result.TargetKilled && target.Id == state.Player.Id)
        {
            int teleportCount = CountRingEffect(state.Player.Get<Equipment>(), RingEffectKind.Teleportation);
            for (int t = 0; t < teleportCount; t++)
            {
                if (state.Rng.Next(0, 100) < 20)
                {
                    int fromX = target.X, fromY = target.Y;
                    var dest = FindRandomOpenTile(state, target);
                    if (dest.HasValue)
                    {
                        state.Map.UnregisterEntity(target);
                        target.X = dest.Value.x;
                        target.Y = dest.Value.y;
                        state.Map.RegisterEntity(target);
                        events.Add(new TeleportEvent
                        {
                            ActorId  = target.Id,
                            EntityId = target.Id,
                            FromX    = fromX,
                            FromY    = fromY,
                            ToX      = dest.Value.x,
                            ToY      = dest.Value.y,
                            Misfire  = false,
                            Reason   = "ring_of_teleportation",
                        });
                        return; // teleport cancels this monster's bonus attack chain
                    }
                    break; // no open tile found — skip remaining rolls
                }
            }
        }

        // Monster bonus attacks — recurse if triggered and target still alive
        if (result.BonusAttackTriggered && target.Require<Fighter>().IsAlive)
        {
            ResolveMonsterAttack(state, monster, target, events, isBonusAttack: true);
        }
    }

    /// <summary>
    /// Attempt to corrode the player's equipped metal main-hand weapon.
    /// Rolls against chance; if triggered, reduces DamageMax by 1, floored at BaseDamageMax/2.
    /// Emits CorrosionEvent for the presentation layer to display a toast.
    /// </summary>
    private static void ResolveCorrosion(GameState state, Entity attacker, double chance,
        SeededRandom rng, List<TurnEvent> events)
    {
        if (rng.NextDouble() >= chance) return;

        var equipment = state.Player.Get<Equipment>();
        var mainHandItem = equipment?.MainHand;
        if (mainHandItem == null) return;

        var equippable = mainHandItem.Get<Equippable>();
        if (equippable == null) return;

        // Only metal weapons corrode
        if (!string.Equals(equippable.Material, "metal", StringComparison.OrdinalIgnoreCase)) return;

        // Floor: weapon cannot be degraded below 50% of its base damage max
        int floor = Math.Max(1, equippable.BaseDamageMax / 2);
        if (equippable.DamageMax <= floor) return;

        equippable.DamageMax--;

        events.Add(new CorrosionEvent
        {
            ActorId = attacker.Id,
            WeaponId = mainHandItem.Id,
            WeaponName = mainHandItem.Name,
            NewDamageMax = equippable.DamageMax,
            BaseDamageMax = equippable.BaseDamageMax,
            MonsterName = attacker.Name,
        });
    }

    /// <summary>
    /// Apply the monster's on-hit status effect to the target.
    /// Uses the no-stack/refresh rule from StatusEffectProcessor.ApplyEffect.
    /// Emits StatusAppliedEvent for the presentation layer.
    /// </summary>
    private static void ResolveOnHitEffect(Entity target, OnHitEffectComponent onHit, List<TurnEvent> events)
    {
        switch (onHit.EffectType)
        {
            case "poison":
                StatusEffectProcessor.ApplyEffect<PoisonEffect>(target, onHit.Duration);
                break;
            case "slowed":
                StatusEffectProcessor.ApplyEffect<SlowedEffect>(target, onHit.Duration);
                break;
            case "burning":
                StatusEffectProcessor.ApplyEffect<BurningEffect>(target, onHit.Duration);
                break;
            default:
                return; // unknown effect type — no-op, no event
        }

        events.Add(new StatusAppliedEvent
        {
            ActorId = target.Id,
            TargetId = target.Id,
            EffectName = onHit.EffectType,
            Duration = onHit.Duration,
        });
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

    /// <summary>
    /// Transform a freshly-killed monster entity into a corpse in-place.
    /// Called after DropMonsterLoot at every monster DeathEvent site.
    ///
    /// If the monster definition has LeavesCorpse=false (e.g., slimes), the call is a no-op.
    /// When no factory is available the check is skipped and the corpse IS created — this is
    /// the safe default for test environments (no slimes in unit tests without a factory).
    ///
    /// Components stripped: Fighter, AiComponent, AlertedState, SplitTracker, CorrosionComponent,
    /// SpeedBonusTracker, DamageModifiers, and all IStatusEffect implementors.
    /// SpeciesTag is preserved for knowledge-system and lineage tracking.
    /// </summary>
    private static void TransformToCorpse(GameState state, Entity entity, List<TurnEvent> events,
        MonsterFactory? monsterFactory)
    {
        // Guard: already a corpse (defensive — shouldn't happen in normal flow)
        if (entity.Has<CorpseComponent>()) return;

        // Corpses require a SpeciesTag — anonymous entities (hand-crafted test fixtures
        // without a YAML origin) are not transformed.
        var speciesTag = entity.Get<SpeciesTag>();
        if (speciesTag == null) return;

        // Check leaves_corpse flag via factory definition lookup.
        if (monsterFactory != null)
        {
            var def = monsterFactory.GetDefinition(speciesTag.TypeId);
            if (def != null && !def.LeavesCorpse) return;
        }

        string originalMonsterId = speciesTag?.TypeId ?? "";
        string originalName = entity.Name;

        // Snapshot Fighter stats before stripping — used by RaiseDeadResolver
        var fighter = entity.Get<Fighter>();
        int snapHp         = fighter?.BaseMaxHp ?? 0;
        int snapDmgMin     = fighter?.DamageMin  ?? 0;
        int snapDmgMax     = fighter?.DamageMax  ?? 0;
        int snapStr        = fighter?.Strength   ?? 10;
        int snapDex        = fighter?.Dexterity  ?? 10;
        int snapCon        = fighter?.Constitution ?? 10;
        int snapDef        = fighter?.BaseDefense ?? 0;
        int snapAccuracy   = fighter?.Accuracy   ?? Combat.HitModel.DefaultAccuracy;
        int snapEvasion    = fighter?.Evasion    ?? Combat.HitModel.DefaultEvasion;

        // Strip combat/AI components
        entity.Remove<Fighter>();
        entity.Remove<AiComponent>();
        entity.Remove<AlertedState>();
        entity.Remove<SplitTracker>();
        entity.Remove<CorrosionComponent>();

        // Strip all status effects (any IStatusEffect implementation)
        foreach (var effect in entity.GetAllComponents().OfType<IStatusEffect>().ToList())
            entity.RemoveByType(effect.GetType());

        // SpeciesTag intentionally NOT stripped — preserved for knowledge system and lineage

        // Add corpse component
        string corpseId = $"corpse_{entity.X}_{entity.Y}_{state.TurnCount}";
        bool wasRaised = entity.Has<RaisedFromCorpseTag>();

        var corpse = new CorpseComponent
        {
            OriginalMonsterId = originalMonsterId,
            OriginalName = originalName,
            DeathTurn = state.TurnCount,
            State = wasRaised ? CorpseState.Spent : CorpseState.Fresh,
            CorpseId = corpseId,
            // Snapshot for RaiseDeadResolver
            BaseHp           = snapHp,
            BaseDamageMin    = snapDmgMin,
            BaseDamageMax    = snapDmgMax,
            BaseStrength     = snapStr,
            BaseDexterity    = snapDex,
            BaseConstitution = snapCon,
            BaseDefense      = snapDef,
            BaseAccuracy     = snapAccuracy,
            BaseEvasion      = snapEvasion,
        };
        entity.Add(corpse);
        entity.BlocksMovement = false;

        // Dual membership: entity stays in state.Monsters AND is added to state.Corpses
        state.Corpses.Add(entity);

        events.Add(new CorpseCreatedEvent
        {
            ActorId = entity.Id,
            CorpseEntityId = entity.Id,
            CorpseId = corpseId,
            OriginalMonsterId = originalMonsterId,
        });
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Ring system
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Apply or reverse a ring's stat effect on the player entity.
    /// equip=true: apply the bonus. equip=false: remove the bonus.
    ///
    /// Phase 2 ring kinds (Resistance, Clarity, Invisibility, Searching, Wizardry, Luck)
    /// do nothing here — their parent systems are not yet implemented. They are safely inert.
    /// </summary>
    private static void ApplyRingEffect(Entity player, RingEffectComponent ring, bool equip, List<TurnEvent> events)
    {
        int delta = equip ? ring.Strength : -ring.Strength;
        var fighter = player.Get<Fighter>();

        switch (ring.Kind)
        {
            case RingEffectKind.Protection:
                if (fighter != null) fighter.BaseDefense += delta;
                break;

            case RingEffectKind.Strength:
                if (fighter != null) fighter.Strength += delta;
                break;

            case RingEffectKind.Dexterity:
                if (fighter != null) fighter.Dexterity += delta;
                break;

            case RingEffectKind.Constitution:
                if (fighter != null)
                {
                    fighter.Constitution += delta;
                    // +20 HP bonus tracked separately so it cleanly reverses on unequip.
                    // The +2 CON from the delta above gives +1 MaxHp via ConstitutionMod.
                    // The +20 RingMaxHpBonus is the additional explicit HP the ring grants.
                    if (equip)
                    {
                        fighter.RingMaxHpBonus += 20;
                        fighter.Hp += 20; // immediate current HP boost on equip
                    }
                    else
                    {
                        fighter.RingMaxHpBonus -= 20;
                        // Clamp current HP to new (lower) MaxHp
                        fighter.Hp = Math.Min(fighter.Hp, fighter.MaxHp);
                    }
                }
                break;

            case RingEffectKind.Might:
                if (fighter != null)
                {
                    // Strength is effect_strength=4 → +1 DamageMin, +4 DamageMax (PoC: might ring adds both)
                    // Convention: DamageMin gets +1, DamageMax gets +strength
                    int minDelta = equip ? 1 : -1;
                    fighter.DamageMin += minDelta;
                    fighter.DamageMax += delta;
                }
                break;

            case RingEffectKind.Regeneration:
                // Passive tick — no stat mutation on equip/unequip.
                // The tick fires in ProcessTurn via CountRingEffect check.
                break;

            case RingEffectKind.Speed:
                // Adjust player's SpeedBonusTracker.RingRatio.
                // Ring of Speed = 0.10, Ring of Hummingbird = 0.25 (stored in SpeedRatio).
                {
                    var tracker = player.Get<SpeedBonusTracker>();
                    if (tracker == null && equip)
                    {
                        tracker = new SpeedBonusTracker();
                        player.Add(tracker);
                    }
                    if (tracker != null)
                        tracker.RingRatio += equip ? ring.SpeedRatio : -ring.SpeedRatio;
                }
                break;

            case RingEffectKind.FreeAction:
                if (equip)
                    player.Add(new FreeActionTag());
                else
                    player.Remove<FreeActionTag>();
                break;

            case RingEffectKind.Teleportation:
                // On-hit passive — no stat mutation. Checked in ResolveMonsterAttack.
                break;

            // Phase 2 stubs: Resistance, Clarity, Invisibility, Searching, Wizardry, Luck
            // No-op until parent systems land.
            default:
                break;
        }
    }

    /// <summary>
    /// Count how many of a given ring effect kind are equipped across both ring slots.
    /// Returns 0 if equipment is null or no ring slots are occupied with that effect.
    /// </summary>
    private static int CountRingEffect(Equipment? equipment, RingEffectKind kind)
    {
        if (equipment == null) return 0;
        int count = 0;
        if (equipment.LeftRing?.Get<RingEffectComponent>()?.Kind == kind) count++;
        if (equipment.RightRing?.Get<RingEffectComponent>()?.Kind == kind) count++;
        return count;
    }

    /// <summary>
    /// Returns true if the player has at least one ring of the given kind equipped.
    /// </summary>
    private static bool HasRingEffect(Equipment? equipment, RingEffectKind kind)
        => CountRingEffect(equipment, kind) > 0;

    /// <summary>
    /// Find a random walkable, unoccupied tile for teleportation.
    /// Returns null if no open tile is found within a reasonable scan.
    /// Excludes the entity's current position.
    /// </summary>
    private static (int x, int y)? FindRandomOpenTile(GameState state, Entity entity)
    {
        var map = state.Map;
        // Collect all walkable, unblocked tiles excluding the entity's current position.
        // In scenario arenas (20x20 = 400 tiles) this is cheap. In dungeons (120x80 = 9600)
        // it's still fast. We snapshot once rather than retrying random positions.
        var candidates = new List<(int x, int y)>();
        for (int x = 0; x < map.Width; x++)
        {
            for (int y = 0; y < map.Height; y++)
            {
                if (x == entity.X && y == entity.Y) continue;
                if (map.CanMoveTo(x, y))
                    candidates.Add((x, y));
            }
        }
        if (candidates.Count == 0) return null;
        return candidates[state.Rng.Next(candidates.Count)];
    }

    /// <summary>
    /// Re-apply all equipped ring stat effects to the player after a floor transition.
    ///
    /// PlayerCarryForward.Apply() creates a new Fighter with base stats only —
    /// ring bonuses (BaseDefense, Strength, etc.) are not in the Fighter constructor.
    /// This method must be called after Apply() to restore ring effects.
    ///
    /// Called from DungeonFloorBuilder (or wherever floor transitions happen) after
    /// PlayerCarryForward.Apply() returns the new player entity.
    ///
    /// Note: For carry-forward we create a new Fighter from the OLD fighter's base stats,
    /// but the OLD fighter already had ring bonuses applied. So if we just copy the stat
    /// values, the bonus is already baked in — we would double-apply if we called this.
    ///
    /// IMPORTANT: PlayerCarryForward.Apply() copies Strength, Dexterity, Constitution etc.
    /// from the live fighter (which already has ring bonuses). This means ring effects
    /// are already embedded in the carried-forward stats. This method should only be called
    /// when the fighter stats were reset to BASE values (not carried forward).
    ///
    /// For the current carry-forward strategy (copy live stats), call sites should NOT
    /// call this — the ring bonuses survive in the copied stats. However, RingMaxHpBonus,
    /// RingRatio, and FreeActionTag MUST be re-applied because they are not carried forward.
    /// </summary>
    public static void ReapplyRingEffects(Entity player)
    {
        var equipment = player.Get<Equipment>();
        if (equipment == null) return;

        var fighter = player.Get<Fighter>();

        // Re-apply ring effects that are NOT captured in Fighter stat fields:
        // - RingMaxHpBonus: new Fighter starts with 0, must be restored
        // - SpeedBonusTracker.RingRatio: tracker is not carried forward
        // - FreeActionTag: marker component, not carried forward

        foreach (var ringSlot in new[] { equipment.LeftRing, equipment.RightRing })
        {
            var ring = ringSlot?.Get<RingEffectComponent>();
            if (ring == null) continue;

            switch (ring.Kind)
            {
                case RingEffectKind.Constitution:
                    if (fighter != null)
                    {
                        // Only restore RingMaxHpBonus — Constitution stat was already carried forward
                        fighter.RingMaxHpBonus += 20;
                    }
                    break;

                case RingEffectKind.Speed:
                    {
                        var tracker = player.Get<SpeedBonusTracker>();
                        if (tracker == null)
                        {
                            tracker = new SpeedBonusTracker();
                            player.Add(tracker);
                        }
                        tracker.RingRatio += ring.SpeedRatio;
                    }
                    break;

                case RingEffectKind.FreeAction:
                    if (!player.Has<FreeActionTag>())
                        player.Add(new FreeActionTag());
                    break;
            }
        }
    }
}
