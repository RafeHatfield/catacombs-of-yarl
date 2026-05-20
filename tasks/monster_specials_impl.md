# Monster Specials Implementation

## Current State

**Completed:** 2026-05-20
**Status:** All 9 tasks complete, needs-review

**Just done:** All tasks complete. 1771 tests passing (was 1741).
**Next step:** Reviewer pass.
**Open issues:** None.

---

## Task Progress

- ✅ TASK-001: Troll fire suppression (BurningEffect suppresses InnateRegen)
  - Status: complete
  - Files changed: `BurningEffect.cs` (doc), `AcidEffect.cs` (doc), `StatusEffectProcessor.cs` (extend check to `|| entity.Has<BurningEffect>()`)
  - Tests: `tests/Core/TrollFireSuppressionTests.cs` (4 tests)

- ✅ TASK-002: Slime Engulf system
  - Status: complete
  - Files changed: new `EngulfedEffect.cs`, new `EngulfsOnHitTag.cs`, `StatusEffectProcessor.cs` (adjacency refresh + unified skip gate), `TurnController.cs` (on-hit application), `MonsterDefinition.cs` (EngulfsOnHit field), `ContentLoader.cs` (merge rule), `MonsterFactory.cs` (tag attachment), `config/entities.yaml` (engulfs_on_hit: true on slime)
  - Tests: `tests/Core/EngulfMechanicsTests.cs` (9 tests)
  - Notable: used `state.Monsters` directly instead of `state.AliveMonsters` in ProcessTurnStart to avoid poisoning the AliveMonsters cache (would cause Fighter-missing crash in same-turn death path)

- ✅ TASK-003: Rally ends on chieftain damage
  - Status: complete
  - Files changed: `RallyEffect.cs` (ChieftainId field), `OrcChieftainAI.cs` (set ChieftainId, cleanse FearEffect), `TurnController.cs` (OnAttackDamageTaken helper), `StatusEffectProcessor.cs` (RemoveEffect<T> public helper)
  - Tests: `tests/Core/ChieftainRallyLifecycleTests.cs` (5 tests)
  - Notable: fear cleanse at rally time is silent (no StatusExpiredEvent) because AI.Decide has no events list

- ✅ TASK-004: Chant of Dissonance
  - Status: complete
  - Files changed: new `DissonantChantEffect.cs`, `OrcShamanComponent.cs` (channeling fields), `OrcShamanAI.cs` (chant decision + channel continuation), `StatusEffectProcessor.cs` (DissonantChantEffect in skip gate), `TurnController.cs` (interrupt on hit, death cleanup), `OrcVariantTests.cs` (updated 2 hex tests for chant priority at distance 5)
  - Tests: `tests/Core/OrcShamanChantTests.cs` (12 tests, including R4 death cleanup)
  - Notable: chant priority > hex per PoC; existing hex tests moved to distance 6 to avoid chant interference

- ✅ TASK-005: YAML wiring
  - Status: complete
  - Files changed: `config/entities.yaml` (engulfs_on_hit: true on slime)
  - Notes: shaman chant fields hardcoded in OrcShamanComponent defaults per plan recommendation

- ✅ TASK-006: scenario_silence_orc_shaman_identity.yaml
  - Status: complete
  - Files added: `config/levels/scenario_silence_orc_shaman_identity.yaml`
  - Metrics (30 runs, seed 1337): death=0%, H_PM=58.7, H_MP=1.0, hit%=59%. No crashes.
  - Notes: is_probe=true; bot doesn't use silence scroll (R3 per plan); scenario validates chant fires

- ✅ TASK-007: scenario_slime_engulf_identity.yaml
  - Status: complete
  - Files added: `config/levels/scenario_slime_engulf_identity.yaml`
  - Metrics (3 runs, seed 1337): death=0%, H_PM=6.4, H_MP=121. No crashes.
  - Notes: is_probe=true; slimes are weak so H_MP is high; death rate low is expected for 2 plain slimes

- ✅ TASK-008: Existing scenario refresh
  - Status: complete
  - orc_shaman_identity: death=0%, H_PM=17.3 (HIGH), H_MP=39.4 (PASS). H_PM above band due to shaman now spending turns channeling instead of attacking. Scenario not recalibrated (is_probe behavior).
  - orc_chieftain_identity: death=13.3% (PASS), H_PM=30.9 (HIGH), H_MP=54.0 (borderline HIGH). No dramatic drift from rally-end-on-damage. No scenario update needed.
  - troll_identity: death=6.7% (PASS), H_PM=8.5 (PASS), H_MP=18.2 (LOW). Metrics unchanged from fire suppression (no fire in scenario). 

- ✅ TASK-009: Harness verification
  - Status: complete
  - All scenarios run without crashes post-change.
  - AliveMonsters cache bug: discovered and fixed — calling state.AliveMonsters during player turn phase (ProcessTurnStart) poisoned the cache, causing Fighter-missing crash in ResolveMonsterTurns on same-turn deaths. Fixed by using state.Monsters directly with live filter.

---

## Key Design Decisions

1. **Unified skip gate (R2):** SlowedEffect, EngulfedEffect, DissonantChantEffect share one alternating-skip slot. Exactly one SkipTurnEvent per odd turn regardless of how many skip-class effects are active.

2. **Chant cleanup on death (R4):** `ResolveChannelCleanupOnDeath` called from both player-kill and monster-vs-monster kill paths. No scenario where a channeling shaman dies can leave a permanent slow on the player.

3. **DOT does NOT interrupt:** Both rally-broken and chant-interrupted are gated on `result.Damage > 0` inside `if (result.Hit)` block in TurnController. ProcessTurnStart DOT ticks do not call these paths.

4. **AliveMonsters cache safety:** Any code called during the player's turn phase that needs to iterate alive monsters must use `state.Monsters.Where(m => m.Get<Fighter>()?.IsAlive == true)` directly to avoid poisoning the cache with pre-death data.

5. **Fear cleanse silent:** OrcChieftainAI.Decide removes FearEffect silently at rally time (no StatusExpiredEvent) because AI.Decide doesn't accept an events list. Documented in test.

---

## Test Count

- Before: 1741 tests passing
- After: 1771 tests passing (+30 new tests)
  - TrollFireSuppressionTests: 4 tests
  - EngulfMechanicsTests: 9 tests
  - ChieftainRallyLifecycleTests: 5 tests
  - OrcShamanChantTests: 12 tests
