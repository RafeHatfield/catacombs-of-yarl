# Next Session Priorities

## State as of 2026-03-30 session (Status Effects Phases 2–5 — Complete)

- 732 tests passing (was 659)
- **Status Effects Phases 2–5**: complete

### Phase 2 — Movement Effects
  - `EntangledEffect`: blocks move, attack still permitted adjacent
  - `ImmobilizedEffect`: gates ALL actions in ProcessTurnStart (skip turn)
  - `DisorientationEffect`: player movement randomized in ResolvePlayerMove; monster movement randomized in BasicMonsterAI.DecideRandomMove
  - `FearEffect`: flee AI in BasicMonsterAI.DecideFlee — maximize Manhattan distance from player; Wait if cornered; never attacks
  - Tests: `MovementEffectTests.cs` (21 tests)

### Phase 3 — Combat Effects
  - `DisarmedEffect`: blocks weapon attacks for player and monsters (AttackEvent with FailReason="disarmed")
  - `SilencedEffect`: blocks scroll/wand use before charge/consumable consumption
  - `BlindedEffect`: -4 accuracy in CombatResolver.ResolveAttack
  - `WeaknessEffect`: -2 damage (min 1) in CombatResolver.ResolveAttack
  - `ShieldEffect`/`ProtectionEffect`/`BarkskinEffect`: AC bonuses already wired in Phase 1
  - `InvisibilityEffect`: breaks on attack (pre-damage) and spell cast; monsters skip invisible targets
  - `FocusedEffect`: +accuracy bonus in CombatResolver
  - TurnEvent: `AttackEvent.FailReason` field added
  - Tests: `CombatEffectTests.cs` (26 tests)

### Phase 4 — AI Override Effects
  - `EnragedEffect.HostileToAll`: AI reads `monster.Has<EnragedEffect>()` directly; nearest entity targeting
  - `TauntedEffect`: forces player targeting, overrides EnragedEffect in ChooseTarget()
  - `SpeedEffect`/`SluggishEffect`/`AggravatedEffect`: apply/tick/expire lifecycle wired; behavior (speed multiplier) deferred as TODO
  - Tests: `AiEffectTests.cs` (18 tests)

### Phase 5 — UI Display
  - `StatusEffectBar` (`src/Presentation/UI/StatusEffectBar.cs`): colored badges (debuff=red, buff=green, neutral=gray); sorted debuffs first; 24 effect short names
  - HUD: `_statusEffectBar` field, refresh in `Refresh()`, instantiated in `BuildLayout()`
  - ToastLog: StatusAppliedEvent, StatusExpiredEvent, DotDamageEvent, HotHealEvent handlers added; `Capitalize()` helper
  - `EntitySpriteManager.UpdateStatusTints()`: tint monsters by debuff priority (poison=green, burning=orange, disorientation=purple, sleep=light blue, any other=gray); called after UpdateVisibility in both Main.cs call sites
  - Tests: `StatusEffectEventTests.cs` (8 tests)

### Testing YAML files
  - `config/testing/test_status_effects_dot.yaml` — DOT effects: scroll_of_dragon_fart + scroll_of_plague; orcs + zombies
  - `config/testing/test_status_effects_movement.yaml` — Movement: glue/fear/confusion scrolls; 3 orcs at range 5
  - `config/testing/test_status_effects_combat.yaml` — Combat: shield/invisibility/disarm/slow scrolls; 3 orcs
  - `config/testing/test_status_effects_buffs.yaml` — Buffs: haste/shield/rage scrolls; 4 orcs

---

## State as of 2026-03-30 session (Status Effects Phase 1 — Lifecycle Engine)

- 659 tests passing (was 635)
- **Status Effects Phase 1 (Lifecycle Engine)**: complete
  - `IStatusEffect` interface (`src/Logic/ECS/IStatusEffect.cs`) — EffectName, RemainingTurns, IsPermanent
  - All existing status effect stubs updated to implement `IStatusEffect` (SlowedEffect, ImmobilizedEffect, EnragedEffect, DisarmedEffect, PlagueEffect, TauntedEffect, FearEffect, InvisibilityEffect, ShieldEffect, SilencedEffect, DisorientationEffect, AggravatedEffect)
  - `ConfusedEffect` and `HasteEffect` removed — DisorientationEffect is canonical; HasteEffect maps to SpeedEffect
  - 12 new effect components: PoisonEffect, BurningEffect, BlindedEffect, SleepEffect, WeaknessEffect, ProtectionEffect, RegenerationEffect, SpeedEffect, SluggishEffect, BarkskinEffect, FocusedEffect, EntangledEffect
  - 4 new TurnEvents: StatusExpiredEvent, DotDamageEvent, HotHealEvent, SkipTurnEvent
  - `StatusEffectProcessor` (`src/Logic/Combat/StatusEffects/StatusEffectProcessor.cs`) — ApplyEffect<T>, ProcessTurnStart, ProcessTurnEnd, OnDamageTaken, ClearAllEffects, RemoveEffect dispatch
  - TurnController wired: ProcessTurnStart/End per entity per turn (END-based timing); OnDamageTaken on attack hits
  - CombatResolver: ShieldEffect, ProtectionEffect, BarkskinEffect AC bonuses read at resolution time
  - DungeonFloorBuilder: ClearAllEffects on player before carry-forward on floor descent
  - SpellResolver: confusion→DisorientationEffect, haste→SpeedEffect (updated)
  - Tags already present on all monsters in entities.yaml; AotObjectFactory already registers List<string>
  - Tests: StatusEffectLifecycleTests.cs (24 tests — all passing)
  - Timing model: END-based (ProcessTurnStart before action, ProcessTurnEnd after action); effects applied to a monster mid-player-turn get one decrement from the monster's ProcessTurnEnd in the same round
  - **Next**: Status Effects Phase 2 (movement effects: Disorientation, Entangled, Immobilized, Fear flee AI) OR Phase 3 (combat effects: DisarmedEffect, SilencedEffect, WeaknessEffect, BlindedEffect, InvisibilityEffect)

---

# Next Session Priorities (post 2026-03-29 — Monster Knowledge + Inspect)

## State as of 2026-03-30 session (Monster Knowledge + Inspect System)

- 635 tests passing (was 608)
- **Monster Knowledge + Inspect System**: complete (Phases 1 + 2 + 3 logic; Phase 3 presentation wired)
  - `SpeciesTag` component (`src/Logic/ECS/SpeciesTag.cs`) — attached at spawn by MonsterFactory.Create
  - `MonsterKnowledgeEntry` + `KnowledgeTier` enum (`src/Logic/Knowledge/MonsterKnowledgeEntry.cs`)
  - `MonsterInfoView` record (`src/Logic/Knowledge/MonsterInfoView.cs`) — tier-gated pure data view
  - `MonsterKnowledgeSystem` (`src/Logic/Knowledge/MonsterKnowledgeSystem.cs`) — RecordSeen/Engaged/Killed/Trait; GetInfoView with label computation matching PoC thresholds exactly
  - `ItemInspectView` (`src/Logic/Knowledge/ItemInspectView.cs`) — static From(Entity) builder for weapons/armor/wands/scrolls/potions
  - `GameState.Knowledge` property — single system instance per run, reset on new game
  - `TurnController.UpdateKnowledge` — hooks into ProcessTurn after turn resolution; drives RecordEngaged from AttackEvent, RecordKilled from DeathEvent, RecordSeen from FOV scan
  - Presentation: `LongPressDetector` node (`src/Presentation/Input/LongPressDetector.cs`) — touch + hover
  - Presentation: `InspectPanel` control (`src/Presentation/UI/InspectPanel.cs`) — ShowMonster/ShowItem/Hide/PositionNear
  - `GameController`: _longPress + _inspectPanel fields; LongPressDetected wired to OnLongPress; HandleTap dismisses panel
  - Tests: `MonsterKnowledgeTests.cs` (20 tests), `ItemInspectTests.cs` (8 tests)
  - PoC tier thresholds matched exactly: seen≥1→Observed, engaged≥3→Battled, killed≥5 OR major_trait→Understood

---

# Next Session Priorities (post 2026-03-28)

## State as of 2026-03-29 session (end, scroll/wand Phase 5 — Portal Wand)

- 608 tests passing
- **Scroll/Wand Phase 5 (Portal Wand)**: complete
  - PortalComponent at `src/Logic/Combat/PortalComponent.cs` — portal entity component with Type, LinkedPortalId, UsedThisTurn
  - PortalSystem at `src/Logic/Core/PortalSystem.cs` — PlacePortals, CheckPortalCollision, ClearPortals, ClearPortalUsedFlags
  - New TurnEvents: PortalPlacedEvent, PortalTeleportEvent, PortalRemovedEvent
  - GameState.Portals list added
  - PlayerAction.TargetX2/TargetY2 + CastSpellPortal factory method
  - TurnController: optional EntityFactory parameter; portal spell branch in ResolveSpellAction; portal collision after player/monster moves; ClearPortalUsedFlags at turn end
  - PortalSystemTests.cs: 31 tests (placement, bidirectional teleport, no-chaining, recycling, YAML loading, TurnController integration, floor transition)
  - config/testing/test_portal_wand.yaml: smoke test scenario
  - Presentation layer deferred: two-step targeting UI (InputHandler + GameController) — the logic layer is complete and tested
  - Pending: GameController needs to call PortalSystem.ClearPortals(state) on DescendEvent handling; also spawn/despawn portal sprites on PortalPlacedEvent/PortalRemovedEvent
- **Next up**: status effects behavioral tick system (plan_status_effects) OR presentation layer portal targeting

## State as of 2026-03-29 session (end, scroll/wand Phase 4 + harness tests)

- 577 tests passing
- **Scroll/Wand Phase 4 (harness tests + DisorientationEffect)**: complete
  - DisorientationEffect component added; applied on teleport misfire (3 turns)
  - wand_of_dragon_farts added to entities.yaml (stub, single-target, depth 4+)
  - ScenarioHarness/ScenarioRunner/GameStateFactory extended to accept SpellItemFactory; scenario item lists now resolve scrolls/wands by ID
  - 3 scenario YAML files added: test_scrolls_auto.yaml, test_scrolls_targeted.yaml, test_wands.yaml
  - SpellScenarioTests.cs: 21 new tests (lightning auto-target, earthquake AoE, fireball AoE+radius check, fear AoE, teleport clean+misfire, DisorientationEffect on misfire, raise_dead stub, wand charge consumption, wand recharge via pickup, all YAML wand/scroll definitions load without error, depth scaling)

## State as of 2026-03-29 session (end, scroll/wand Phases 1+2+3+4)

- 556 tests passing
- **Scroll/Wand Phase 4 (location targeting)**: complete — wand_of_fireball (depth 5+, weight 7) and wand_of_teleportation (depth 6+, weight 6) added to entities.yaml; scroll_of_raise_dead stub added (no-op until plan_monster_specials corpse system lands); ResolveRaiseDead handler stub in SpellResolver; 4 new Blink tests + RaiseDead_NoCorpse test (556 total)
- **Scroll/Wand Phases 1+2+3**: complete — all infrastructure from Phase 1 plus:
  - **Phase 2 (wand depth scaling)**: `SpellItemFactory.CreateWand(depth)` now applies PoC formula: `rand(min, max) + (depth - 1)`, capped at `charge_cap`; EntityPlacer passes depth to CreateWand; WandTests (13) verify formula + cap + recharge behavior
  - **Phase 3 (single-target status effects)**: 8 status effect components (ConfusedEffect, SlowedEffect, ImmobilizedEffect, EnragedEffect, DisarmedEffect, PlagueEffect, TauntedEffect, AggravatedEffect); 4 deferred-phase stub components (InvisibilityEffect, ShieldEffect, HasteEffect, SilencedEffect, FearEffect); 8 Phase 3 scrolls + 5 matching wands in entities.yaml; SpellResolver handlers for all 8 scrolls; SingleTargetSpellTests (15 tests) verify all status effects + range validation + corporeal check; AiComponent extended with Faction + Tags fields; MonsterFactory populates both; SpellEvent gains StatusApplied + StatusDuration fields
  - **Phase 3 Presentation**: GamePhase.Targeting added; TargetingState.cs; InputHandler extended with EnterTargetingMode/CancelTargeting/TargetChosen/LocationChosen/TargetingCancelled; GameController.HandleInventoryTap routes scrolls/wands to CastSpell or targeting mode; HandleScrollOrWandUse dispatches based on TargetingMode; GameController.CancelTargeting public API for cancel button
  - Additional scrolls from PoC ported: fear, teleport, blink, invisibility, shield, haste, fireball, silence, dragon_fart (all in entities.yaml; stubs in SpellResolver for Phase 4+ spells)

## State as of 2026-03-29 session (end, scroll/wand Phase 1)

- 514 tests passing
- **Scroll/Wand Phase 1**: complete — SpellEffect + WandComponent components; SpellResolver (lightning, earthquake, light, magic_mapping, detect_monsters, enhance_weapon, enhance_armor); SpellDefinition YAML + SpellItemFactory; ContentBundle/ContentLoader updated; 7 scrolls + 2 wands in entities.yaml with floor_item_pool entries; wand auto-recharge on scroll pickup; wand_of_portals granted at run start (Wand of Portals spell not yet implemented — deferred to Phase 5); DungeonFloorBuilder + EntityPlacer extended for scroll/wand floor drops; 40 new tests passing.

## State as of 2026-03-29 session (end)

- 472 tests passing
- **Slime monsters**: complete — `slime` and `large_slime` added to entities.yaml; split-under-pressure mechanic (SplitTracker component, ResolveSplit in TurnController); corrosion mechanic (CorrosionComponent, ResolveCorrosion); weapon material field on ItemDefinition/Equippable; BaseDamageMax baseline; SplitEvent + CorrosionEvent TurnEvents; GameController handles both; 15 new tests all passing.

## State as of 2026-03-29 session (start)

- 457 tests passing
- **Depth-scaling spawn weights**: complete — `from_dungeon_level` pattern ported from PoC; `orc_brute` and `zombie` now use `depth_weights` tables; `orc_grunt` explicitly zeroed from procedural pool; `EncounterBudget` wired through `DungeonFloorBuilder` → `EntityPlacer.FillRooms`; `SpawnWeight` nullable; ContentLoader validates sort order at load time.

## State as of end of extended 2026-03-28 session

- 454 tests passing
- Equipment/inventory UX: complete (quickbar + equipment panel with body map)
- Entity ID collision bug: fixed via ReIdMonsterEquipment
- Floor item pool pipeline: live (13 new items, 40% flat spawn rate)
- Monster drops: fixed — ItemSpriteManager creates sprites on DropEvent
- Auto-explore: stair interrupt removed — stairs never interrupt exploration
- Equipment panel: shows HP/ATK/HIT/AC stats line
- DungeonFloorBuilder no-guaranteed-spawns path: fixed to pass items+floorItemPool
- **Item pickup bug**: fixed — FindMonsterAt now bypasses stale AliveMonsters cache
- **Grey screen on floor transition**: fixed — PlayerCamera.Update kills tween before snapping
- **Monster naming**: fixed — orc and zombie both have name: fields in entities.yaml
- **Zombie spawn depth**: fixed — min_depth: 10 in entities.yaml matches PoC
- **Weighted spawn system**: live — SpawnWeight field + weighted FillRooms selection

---

## Priority 1 — More PoC monsters

### 1a. Add missing monster types
PoC has monsters that don't exist yet in C#. Port in depth order:
- **slime**: DONE (2026-03-29) — depth 2+, split-under-pressure, corrosion
- **large_slime**: DONE (2026-03-29) — depth 3+, splits into 2-3 slimes at 40% HP
- **giant_spider**: depth 8+, weight 15→30→45 at depths 8/11/14.
- **troll** (= orc_brute analogue): currently orc_brute has fixed weight 15. PoC troll goes 15→30→60 at depths 3/5/7.

### 1b. Depth-scaling weights — DONE (2026-03-29)
`depth_weights` YAML field + `SpawnUtils.FromDungeonLevel` live. `orc_brute` and `zombie` converted. New monster types (slime, large_slime, giant_spider) should use the same `depth_weights` pattern.

---

## Priority 2 — Deferred loot systems

See `memory/project_deferred_loot_systems.md` for full detail.

### 2a. Pity system (floor item spawning)
Replace flat 40% in `EntityPlacer.FillRooms` with PoC band-density scaling (B1=0.35x, B2=0.45x, B3+=1.0x).
Add rolling window of floor outcomes to GameState for pity bias.
**TODO comment already in place** in `EntityPlacer.FillRooms`.

### 2b. Rarity tiers (monster drops)
Implement `RarityRoller` in `TurnController.DropMonsterLoot`.
Tiers: Common/Uncommon/Rare/Legendary — stat bonuses based on monster ETP + depth.
**TODO comment already in place** in `TurnController.DropMonsterLoot`.

---

## Priority 3 — Visual polish

### 3a. Tile variety
Current floors all look the same gray. Check if Oryx has floor variants for variation.

### 3b. HUD enemy label truncation
Name might render truncated in HUD. Check label width / clip settings.

---

## Priority 4 — Balance validation

Run scenario harness at depths 1-3 with monster equipment drops live.
Confirm Death% stays in target bands. Monster gear drops are now visible to the player —
may affect encounter feel (orcs drop club/dagger/leather armor).

---

## Priority 5 — Gameplay depth

### 5a. Multiple monsters per room
`max_monsters_per_room` is still TEMP:1 in level_templates.yaml — restore to 2-3.
Run harness to confirm Death% after change.

### 5b. Unified consumable + equipment pool
TODO in EntityPlacer.FillRooms — merge the separate consumable and equipment passes
into a single depth-filtered pool once band-density scaling is in.

---

## State as of 2026-03-29 session (scroll/wand Phase 3)

- 552 tests passing (was 527 before Phase 3)
- **Scroll/wand Phase 3**: complete.
  - Status effect components: FearEffect, InvisibilityEffect, ShieldEffect, HasteEffect, SilencedEffect (new)
  - SpellResolver handlers: fear, invisibility, shield, haste, silence, teleport, blink, fireball, dragon_fart (stub)
  - New TurnEvents: StatusAppliedEvent, TeleportEvent
  - SpellEffect.MisfireChance field added
  - YAML: 9 new Phase 3 scrolls (fear, teleport, blink, invisibility, shield, haste, fireball, silence, dragon_fart) in entities.yaml with floor_item_pool entries
  - Presentation: TargetingState.cs (already existed), InputHandler targeting mode (already existed), GameController routing (already existed), TargetingOverlay.cs (new)
  - Tests: SingleTargetSpellTests.cs extended with 25 new tests
  - plan_spell_wand_scroll_system.md: Phase 3 [→x]
  - Phase 4 (Location targeting scrolls: raise_dead) and Phase 5 (Portal Wand) remain pending

## State as of 2026-03-29 session (scroll/wand audit)

- 527 tests passing (was 472 at session start)
- **Scroll/wand Phase 1 + 2**: complete and verified. All acceptance criteria covered.
  - 7 Phase 1 scrolls in entities.yaml (scroll_of_lightning, earthquake, light, magic_mapping, detect_monsters, enchant_weapon, enchant_armor)
  - 2 wands (wand_of_lightning, wand_of_portals)
  - Tests: SpellResolverTests.cs (17 tests), SpellCastTests.cs (10 tests), SpellItemFactoryTests.cs (12 tests), WandTests.cs (13 tests)
  - SpellResolver handles all 7 spell IDs
  - WandComponent: TryConsume, depth-scaling charge formula, auto-recharge on scroll pickup
  - plan_spell_wand_scroll_system.md: Phase 1 [~→x], Phase 2 [~→x]
  - Phase 3 (SingleTarget targeting UI) and Phase 5 (Portal Wand) remain pending

---

## Known deferred

- Character sheet / XP / leveling
- Item identification system
- Wand charges (Phase 3+ scrolls that need status effects or targeting UI)
- Partial stack drops
- GUT-based full UI E2E tests
- Monster CanUseItems=true for specific types (once balance validated)
- Pop-up confirm before pathing to stairs ("Descend to depth N?")
- large_slime split-on-death mechanic
