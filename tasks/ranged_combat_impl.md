# Ranged Combat Implementation

## Current State
- Status: complete
- Last action: All 5 milestones complete. 1741 fast tests pass (up from 1708).
- All 37 ranged combat tests pass (33 fast + 4 slow scenario tests).

## Notes on Design Decisions
- `can_retaliate` uses `SleepEffect` and `ImmobilizedEffect` — C# has no `StunnedEffect` or `StaggeredEffect` yet (load-bearing spec: EntangledEffect does NOT block retaliation)
- `BurningEffect.DamagePerTurn` for fire_arrow = 1 (flat, not 3), duration 3 (not 5) — PoC test authoritative
- `EntangleMoveBlockedEvent` emitted from:
  - TurnController.ResolvePlayerMove (when player is entangled)
  - TurnController.ResolveMonsterTurns (when skirmisher is entangled, in leap range, and returns Wait)
- `RangedNetArrowBot.Decide` at d=1: always shoots (not back off) — exercises retaliation mechanic
- `RangedNetArrowBot.Decide` at d>8: attempts shot (gets denied by service) for denial test
- `ContentLoader.LoadItems` cannot parse full entities.yaml directly — `floor_item_pool` is a sequence; use `LoadAllFromFile` which strips it first
- Quiver auto-unequip: when ammo exhausted, item returned to inventory if possible, else dropped on floor
- Adjacent punish scenario: player at (3,6), orc at (4,6), bot=ranged_net_arrow — bot shoots at d=1 triggering retaliation

## Milestones

### Milestone 1: Infrastructure
- [x] KnockbackService (src/Logic/Combat/KnockbackService.cs)
- [x] TwoHanded flag + IsRangedWeapon + IsSpecialAmmo on Equippable
- [x] Quiver slot on Equipment
- [x] Build passes

### Milestone 2: YAML + Events + Metrics
- [x] shortbow, longbow, fire_arrow, net_arrow in config/entities.yaml
- [x] ItemDefinition + ItemFactory updated for new fields
- [x] 4 new TurnEvents in TurnEvent.cs
- [x] ActionKind.RangedAttack + PlayerAction.ShootAt()
- [x] 9 metrics in RunMetrics + AggregatedMetrics
- [x] ScenarioDefinition.PlayerBot + ScenarioPlayer.Quiver fields
- [x] Build passes

### Milestone 3: RangedCombatService + TurnController wiring
- [x] RangedCombatService.AttemptRangedAttack() (src/Logic/Combat/RangedCombatService.cs)
- [x] TurnController.ResolveRangedAttack() dispatch
- [x] TurnController.ResolveEquip() — TwoHanded clears OffHand + Quiver slot validation
- [x] EntangleMoveBlockedEvent from player move path
- [x] EntangleMoveBlockedEvent from skirmisher leap (TurnController.ResolveMonsterTurns)
- [x] GameStateFactory supports Quiver field
- [x] Build passes

### Milestone 4: Bot + Harness wiring
- [x] RangedNetArrowBot (src/Logic/Balance/RangedNetArrowBot.cs)
- [x] ScenarioHarness bot dispatch (player_bot == "ranged_net_arrow" → RangedNetArrowBot.Decide)
- [x] Build passes

### Milestone 5: Scenarios + Tests
- [x] scenario_ranged_viability_arena.yaml
- [x] scenario_ranged_adjacent_punish_arena.yaml  
- [x] scenario_ranged_max_range_denial_arena.yaml
- [x] scenario_skirmisher_vs_ranged_net_identity.yaml
- [x] RangedCombatTests.cs (37 tests: 33 fast + 4 slow)
- [x] All tests pass (1741 fast, all 37 ranged tests)

## Files Changed
- src/Logic/Combat/Equippable.cs — IsRangedWeapon, TwoHanded, IsSpecialAmmo flags; EquipmentSlot.Quiver
- src/Logic/Combat/Equipment.cs — Quiver property; AllEquipped + GetSlot + SetSlot updated
- src/Logic/Combat/KnockbackService.cs — NEW
- src/Logic/Combat/RangedCombatService.cs — NEW
- src/Logic/Core/TurnEvent.cs — 4 new events
- src/Logic/Core/PlayerAction.cs — ActionKind.RangedAttack + PlayerAction.ShootAt()
- src/Logic/Core/TurnController.cs — RangedAttack dispatch, EntangleMoveBlockedEvent, TwoHanded clearing
- src/Logic/Core/GameStateFactory.cs — Quiver equip at scenario start
- src/Logic/Balance/RunMetrics.cs — 9 ranged metrics + AggregatedMetrics fields
- src/Logic/Balance/ScenarioDefinition.cs — PlayerBot + Quiver on ScenarioPlayer
- src/Logic/Balance/ScenarioHarness.cs — bot dispatch
- src/Logic/Balance/RangedNetArrowBot.cs — NEW
- src/Logic/Content/ItemDefinition.cs — IsRangedWeapon, TwoHanded, IsSpecialAmmo, StackSize
- src/Logic/Content/ItemFactory.cs — parse new fields, ParseSlot "quiver", attach Consumable for ammo
- config/entities.yaml — shortbow, longbow, fire_arrow, net_arrow definitions
- config/levels/scenario_ranged_viability_arena.yaml — NEW
- config/levels/scenario_ranged_adjacent_punish_arena.yaml — NEW
- config/levels/scenario_ranged_max_range_denial_arena.yaml — NEW
- config/levels/scenario_skirmisher_vs_ranged_net_identity.yaml — NEW
- tests/Combat/RangedCombatTests.cs — NEW (37 tests)
