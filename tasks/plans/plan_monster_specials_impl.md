# Monster Specials — Implementation Plan

## Status: planning

## Scope

This plan covers the *remaining* monster special mechanics from the design doc at
`tasks/plans/plan_monster_specials.md` that have not been picked up by other plans.

**Already shipped under other plans (do not re-implement):**

| Mechanic | Plan | Files |
|----------|------|-------|
| Corpse / necromancer lifecycle | `plan_corpse_necromancer.md` | `src/Logic/AI/NecromancerAI.cs`, `src/Logic/Core/RaiseDeadResolver.cs`, `CorpseComponent.cs` |
| Slime split-under-pressure | `slime_monsters.md` | `src/Logic/ECS/SplitTracker.cs`, `TurnController.ResolveSplit` |
| Slime weapon corrosion | `slime_monsters.md` | `src/Logic/ECS/CorrosionComponent.cs`, `TurnController.ResolveCorrosion` |
| Skirmisher leap + hit-and-run | (none — overnight build) | `src/Logic/AI/SkirmisherAI.cs`, harness validated |
| Plague spread / plague zombie | `plan_status_effects_impl.md` | `PlagueEffect.cs`, `plague_necromancer`, `plague_zombie` in YAML |
| Crippling Hex (basic) | (Wave 1 orc variants) | `src/Logic/AI/OrcShamanAI.cs`, `OrcShamanComponent.cs`, `CrippledEffect.cs` |
| Rally Cry (basic) + Sonic Bellow | (Wave 1 orc variants) | `src/Logic/AI/OrcChieftainAI.cs`, `OrcChieftainComponent.cs`, `RallyEffect.cs` |
| Innate troll regen + **acid** suppression | `plan_interactive_props_traps.md` | `src/Logic/ECS/InnateRegenComponent.cs`, `AcidEffect.cs`, `StatusEffectProcessor.ProcessTurnStart` |

**What this plan adds:**

1. **Orc Shaman — Chant of Dissonance** (channeled, interruptible ability). Hex is shipped; chant is missing entirely.
2. **Orc Chieftain — Rally-on-damage cleanup** (rally ends when chieftain is hit). Rally fires but never ends.
3. **Troll regen — fire suppression** (acid works; fire does not). Adds the second half of the PoC's regen-suppression rule.
4. **Slime Engulf** — `EngulfedEffect` applied on slime hit; movement penalty while adjacent to any slime; decays on break-contact.

That's the *entire* remaining scope from the design doc. Everything else listed in the
design checklist is either already done or already covered by another plan.

---

## Reference

- Design doc: `tasks/plans/plan_monster_specials.md`
- PoC files:
  - `~/development/rlike/components/ai/orc_shaman_ai.py` (lines 233–365 — chant + interrupt)
  - `~/development/rlike/components/ai/orc_chieftain_ai.py` (lines 108–202 — rally lifecycle)
  - `~/development/rlike/components/fighter.py` lines 540–622 (chant interrupt + rally end on damage)
  - `~/development/rlike/components/fighter.py` lines 553–570 (regen suppression: `damage_type in ['acid', 'fire']`)
  - `~/development/rlike/engine/systems/ai_system.py` lines 600–645 (`regeneration_suppressed_until_turn`)
  - `~/development/rlike/tests/test_engulf_mechanics.py` (engulf adjacency, refresh, decay)
  - `~/development/rlike/config/levels/scenario_monster_orc_shaman_identity.yaml`
  - `~/development/rlike/config/levels/scenario_silence_orc_shaman_identity.yaml`
- Existing C# scenarios:
  - `config/levels/scenario_orc_shaman_identity.yaml`
  - `config/levels/scenario_orc_chieftain_identity.yaml`
  - `config/levels/scenario_troll_identity.yaml`
- Tests already in place: `tests/Core/OrcVariantTests.cs` (hex + rally + bellow); `tests/Logic/Features/WeaponAcidCoatingTests.cs` (acid regen suppression); `tests/Core/Wave2MonsterTests.cs` (troll regen baseline)

---

## Current State (verified by reading source)

### Orc Shaman (`src/Logic/AI/OrcShamanAI.cs`, `OrcShamanComponent.cs`)

**Shipped:**
- Crippling Hex: cooldown=10, range=6, duration=5, applies `CrippledEffect(ToHitPenalty=1, AcPenalty=1)`.
- Hang-back positioning (PreferredDistance 4–7), DangerRadius panic retreat at ≤2.
- Status overrides: Fear, Disorientation, Entangled.
- Falls through to melee attack when adjacent.

**Missing:**
- **Chant of Dissonance.** The PoC's second shaman ability — channeled for 3 turns, applies a movement-energy tax to the player (player moves cost 2 actions instead of 1), interruptible if the shaman takes damage. Cooldown 15. Range 5.
- Channeling state in `OrcShamanComponent` (no `IsChanneling`, no `ChantCooldownRemaining`, no `ChantTurnsRemaining`).
- Damage-interrupt hook on the shaman (no place currently breaks the chant).

### Orc Chieftain (`src/Logic/AI/OrcChieftainAI.cs`, `OrcChieftainComponent.cs`)

**Shipped:**
- Rally Cry: fires once when ≥2 orc allies in range 5. Applies `RallyEffect(ToHitBonus=1, DamageBonus=1, RemainingTurns=1000)` to chieftain and all qualifying orc allies.
- Sonic Bellow: fires once when chieftain HP < 50%. Applies `CrippledEffect(duration=2)` to player.
- Hang-back, panic retreat, status overrides — all identical pattern to shaman.

**Missing:**
- **Rally never ends.** PoC ends rally immediately for all rallied orcs when the chieftain takes any damage. C# rally has RemainingTurns=1000 and only expires when those 1000 turns elapse (i.e. never within a real fight). This is a functional gap, not cosmetic — players cannot break rally by "tagging" the chieftain.
- **Rally cleanse.** PoC cleanses fear/morale-debuff effects from rallied orcs at rally time. C# does not.

### Troll Regen (`InnateRegenComponent`, `AcidEffect`, `StatusEffectProcessor`)

**Shipped:**
- `InnateRegenComponent` attached at spawn for any monster with `regeneration_amount > 0` in YAML (`troll`, `troll_ancient`).
- `ProcessTurnStart` heals `HealPerTurn` each turn.
- `AcidEffect` on the entity → suppresses regen for that turn; emits `RegenSuppressedEvent`.

**Missing:**
- **Fire suppression.** PoC suppresses regen on *either* acid or fire damage (`damage_type.lower() in ['acid', 'fire']`). C# only checks `AcidEffect`. A burning troll currently regenerates normally — which makes fire arrows less rewarding than the design promises ("creates strong incentive to carry fire arrows").
- The fix is symmetric to acid: suppress when `BurningEffect` is present.

### Engulf

**Not implemented at all.** There is no `EngulfedEffect`, no `EngulfComponent`, no slime-adjacency check. Was explicitly deferred in `tasks/plans/deferred_slime_abilities.md` §2. This plan picks it up.

---

## PoC-verified values

### Chant of Dissonance (PoC `orc_shaman_ai.py` lines 233–313 + `entities.yaml` shaman config)

| Field | Value | Source |
|-------|-------|--------|
| `chant_radius` | 5 | `getattr(self.owner, 'chant_radius', 5)` |
| `chant_duration_turns` | 3 | `getattr(self.owner, 'chant_duration_turns', 3)` |
| `chant_cooldown_turns` | 15 | `getattr(self.owner, 'chant_cooldown_turns', 15)` |
| `chant_move_energy_tax` | 1 | `getattr(self.owner, 'chant_move_energy_tax', 1)` |
| Cast priority | Chant > Hex > positioning | shaman AI flow |
| Interrupt rule | Any damage > 0 (post-resistance) breaks channel | `fighter.py` line 595, 616–621 |
| Turn cost | Channel start consumes turn; each continuation consumes turn | `_try_start_chant` returns after applying effect |
| Effect on player | +1 movement energy cost (player move costs 2 turns instead of 1) | `chant_move_energy_tax` |

### Rally lifecycle (PoC `orc_chieftain_ai.py` + `fighter.py` lines 593–611)

| Aspect | PoC | C# now | Decision |
|--------|-----|--------|----------|
| Rally duration | "until chieftain damaged" — buff carries `chieftain_id` | `RemainingTurns=1000` | Add `ChieftainId` field to `RallyEffect`; remove from all carriers when chieftain takes damage > 0 |
| Rally cleanse tags | `['fear', 'morale_debuff']` | none | Cleanse `FearEffect` from rallied allies at rally time |
| Rally directive | rallied orcs target chieftain's chosen target | (no AI directive yet) | **Defer.** Faction system already handles target selection adequately for current scope. |

### Fire suppression (PoC `fighter.py` 553–570 + `ai_system.py` 609–638)

PoC stores `regeneration_suppressed_until_turn` on the entity, set to `turn_number + 1` whenever the entity takes acid OR fire damage. Regen check reads this each turn.

For C# we already use a different abstraction: `AcidEffect` (duration-based status) gates regen. The cleanest port is to extend the existing gate to also check for `BurningEffect`. This keeps the rule co-located in `StatusEffectProcessor.ProcessTurnStart` instead of scattering "suppressed_until_turn" fields across components.

### Engulf (PoC `tests/test_engulf_mechanics.py` + `entities.yaml` slime entries)

| Field | Value | Source |
|-------|-------|--------|
| Trigger | On any successful slime hit (damage > 0) | `test_engulf_applies_on_hit` |
| Effect duration | 3 turns | `EngulfedEffect(duration=3, ...)` |
| Refresh on adjacency | If any slime adjacent at turn start, refresh duration to 3 | `process_turn_start` adjacency check |
| Decay on break-contact | If no slime adjacent, duration ticks down normally | `test_engulf_decay_when_not_adjacent` |
| Movement penalty | Skip every other movement turn (1 of every 2 attempts) | `test_engulf_movement_penalty` — counter=1 skip, counter=2 act, counter=3 skip |
| Determinism | No RNG — always applies on hit | `test_engulf_no_rng_always_applies` |
| Applies to | Any monster with `engulf` in `special_abilities` (PoC) | C#: any monster tagged `acidic` AND `amorphous` (i.e. all 3 slime types: `slime`, `large_slime`, `greater_slime`) |

**Movement penalty interpretation for C#.** The PoC counts process_turn_start calls and skips odd turns. In C# we already have the `SlowedEffect` pattern (`turnCount % 2 == 1` skip). The simplest port is to make `EngulfedEffect` behave like a self-refreshing `SlowedEffect` while a slime is adjacent — every other player turn becomes a skip. This reuses the existing slow-skip pipeline, avoiding a new movement-cost abstraction.

---

## Build Order / Dependency Graph

```
TASK-001  Fire suppression for troll regen           ──┐
                                                       │  independent
TASK-002  Engulf: EngulfedEffect + slime hit + adj.   ──┘

TASK-003  Rally lifecycle: end-on-damage + cleanse  ─┐
                                                     │  share interrupt hook
TASK-004  Chant of Dissonance + channel interrupt   ─┘

TASK-005  YAML: shaman chant fields, slime engulf tag    (depends on 002, 004)

TASK-006  Scenario: scenario_silence_orc_shaman_identity (depends on 004, requires silence_scroll)
TASK-007  Scenario: scenario_slime_engulf_identity       (depends on 002)
TASK-008  Scenario adjustments: refresh existing 3       (depends on all logic tasks)

TASK-009  Harness verification + metric snapshots        (depends on 005–008)
```

Suggested execution order:
1. TASK-001 (fast, contained change to one file)
2. TASK-002 (new effect, only touches slime entries)
3. TASK-003 (uses existing damage-taken hook)
4. TASK-004 (largest; reuses TASK-003 interrupt scaffolding)
5. TASK-005 (YAML wiring once code is in)
6. TASK-006/007 (scenarios)
7. TASK-008 (sweep)
8. TASK-009 (final harness pass)

---

## C# Port Checklist

### TASK-001 — Burning suppresses InnateRegen

**Layer:** logic
**Type:** balance / bug fix
**Acceptance:**
- Burning troll does not regenerate.
- Acid-only troll still does not regenerate (no regression).
- Troll with neither effect regenerates normally.
- `RegenSuppressedEvent` fires for both acid and fire cases (presentation already keys off this).
- Fast-test suite passes.

**Files to modify:**
- `src/Logic/Combat/StatusEffects/StatusEffectProcessor.cs` — extend the `InnateRegenComponent` block (lines ~181–202): suppress when `AcidEffect` OR `BurningEffect` is present.
- `src/Logic/Combat/StatusEffects/AcidEffect.cs` — update doc comment to mention burning-symmetric behavior.
- `src/Logic/Combat/StatusEffects/BurningEffect.cs` — add doc note: "While active, also suppresses `InnateRegenComponent`."

**Files to add (tests):**
- `tests/Core/TrollFireSuppressionTests.cs` — three tests:
  - `Troll_WithBurningEffect_DoesNotRegenerate`
  - `Troll_WithAcidEffect_DoesNotRegenerate` (regression)
  - `Troll_WithBothBurningAndAcid_StaysSuppressed`

---

### TASK-002 — Slime Engulf

**Layer:** logic
**Type:** system
**Acceptance:**
- Slime, large_slime, greater_slime apply `EngulfedEffect(duration=3)` to the player on any successful hit.
- While engulfed AND adjacent to any slime at turn start, duration refreshes to 3.
- While engulfed AND no slime adjacent, duration decays normally via `ProcessTurnEnd`.
- Engulfed player skips every other movement turn (same skip pipeline as `SlowedEffect`).
- Effect is purely deterministic — no RNG roll.
- `StatusAppliedEvent` and `StatusExpiredEvent` emit so presentation can badge it.
- Engulf does not apply to monsters (slime-vs-slime doesn't engulf).
- Fast-test suite passes.

**Files to add:**
- `src/Logic/Combat/StatusEffects/EngulfedEffect.cs` — `IStatusEffect` implementation; `EffectName = "engulfed"`; `RemainingTurns = 3` default.
- `src/Logic/ECS/EngulfsOnHitTag.cs` — empty tag component attached at spawn for monsters with `engulfs_on_hit: true` in YAML. Avoids name-string matching at runtime.
- `tests/Core/EngulfMechanicsTests.cs` — port the PoC engulf tests:
  - `Engulf_AppliedOnSlimeHit`
  - `Engulf_NotAppliedOnMiss`
  - `Engulf_NotAppliedByNonEngulfer`
  - `Engulf_RefreshesDurationWhileAdjacent`
  - `Engulf_DecaysWhenNotAdjacent`
  - `Engulf_RefreshFromMultipleSlimes`
  - `Engulf_SkipsEveryOtherTurn`
  - `Engulf_AppliedToPlayerOnly`

**Files to modify:**
- `src/Logic/Combat/StatusEffects/StatusEffectProcessor.cs`:
  - Add `EngulfedEffect` to the `EffectName` dictionary at line ~32.
  - In `ProcessTurnStart`, before the slowed-skip branch: if entity has `EngulfedEffect`, check adjacency against any alive monster with `EngulfsOnHitTag`; if found, set `RemainingTurns = 3` (refresh — no event spam since duration didn't expire).
  - In the slow-skip block: also skip if entity has `EngulfedEffect` AND `turnCount % 2 == 1` (FreeAction still bypasses). Emit `SkipTurnEvent { EffectName = "engulfed" }`.
- `src/Logic/Core/TurnController.cs`:
  - In `ResolveMonsterAttack` after `result.Hit && result.Damage > 0`: if attacker has `EngulfsOnHitTag` and target is player, call `StatusEffectProcessor.ApplyEffect<EngulfedEffect>(target, 3)`.
- `src/Logic/Content/MonsterDefinition.cs` — add `[YamlMember(Alias = "engulfs_on_hit")] public bool EngulfsOnHit { get; set; } = false;`.
- `src/Logic/Content/ContentLoader.cs` — `Merge` rule: child `true` wins, else parent (default false).
- `src/Logic/Content/MonsterFactory.cs` — if `def.EngulfsOnHit`, attach `EngulfsOnHitTag`.

**Movement penalty design note.** The PoC uses a custom counter on the effect; reusing the global `turnCount` (already threaded through `ProcessTurnStart`) gives the same alternating-skip pattern with zero new state. `SlowedEffect` already does this. The only reason not to literally apply `SlowedEffect` is that the engulf badge is its own visual identity and the refresh-on-adjacency rule is unique.

---

### TASK-003 — Rally ends on chieftain damage

**Layer:** logic
**Type:** balance / bug fix
**Acceptance:**
- When the chieftain takes any attack damage > 0, `RallyEffect` is removed from the chieftain itself and from every monster whose `RallyEffect.ChieftainId` matches the chieftain.
- `StatusExpiredEvent { Reason = "rally_broken" }` emitted for each removal.
- Rally cannot re-fire (chieftain's `RallyCried` stays true).
- DOT damage does not break rally (matches PoC — only attack damage interrupts).
- `FearEffect` on rallied allies is cleansed at rally time.
- Fast-test suite passes.

**Files to modify:**
- `src/Logic/Combat/StatusEffects/RallyEffect.cs` — add `public int ChieftainId { get; set; }`.
- `src/Logic/AI/OrcChieftainAI.cs` — at rally time (lines 86–88):
  - Set `ChieftainId = monster.Id` on each `RallyEffect` instance applied.
  - For each ally: if ally has `FearEffect`, remove it and emit `StatusExpiredEvent { Reason = "rally_cleanse" }`.
- `src/Logic/Combat/StatusEffects/StatusEffectProcessor.cs` — add new public helper `OnAttackDamageTaken(Entity attacker, Entity defender, GameState state, List<TurnEvent> events)`:
  - If `defender` has `OrcChieftainComponent`:
    - For each alive monster (including defender itself): if `RallyEffect.ChieftainId == defender.Id`, remove it + emit `StatusExpiredEvent { Reason = "rally_broken" }`.
  - This is a new helper because the existing `OnDamageTaken(entity, events)` doesn't know who the attacker is and doesn't need GameState.
- `src/Logic/Core/TurnController.cs`:
  - `ResolvePlayerAttack` — after `if (result.Hit && result.Damage > 0)` block: call the new `OnAttackDamageTaken` (defender = monster). This is the only attack path that targets chieftains in single-faction games; later, monster-vs-monster chieftain hits will route through the same helper.
  - `ResolveMonsterAttack` — symmetric call when defender is a chieftain (covers monster-vs-monster faction combat).

**Files to add (tests):**
- `tests/Core/ChieftainRallyLifecycleTests.cs`:
  - `Rally_EndsOnChieftainAttackDamage`
  - `Rally_DoesNotEndOnDotDamage` (apply burning to chieftain; rally persists through DOT ticks)
  - `Rally_CleansesFearFromAllies`
  - `Rally_DoesNotRefireAfterEnding`
  - `Rally_DoesNotEndOnAllyDamage` (damaging a rallied orc doesn't break rally)

---

### TASK-004 — Chant of Dissonance

**Layer:** logic
**Type:** system
**Acceptance:**
- Shaman casts `Chant of Dissonance` when in range 5 AND `ChantCooldownRemaining == 0` AND not already channeling, **before** considering Hex (PoC priority: Chant > Hex).
- Channel lasts 3 turns; each channel turn consumes the shaman's action (no attack, no move) — same skip pipeline as `SleepEffect`.
- During channel: player has `DissonantChantEffect` — moves cost 2 turns instead of 1 (player movement skips every other turn).
- Channel ends naturally at 3 turns → `ChantCooldownRemaining = 15`, effect removed from player.
- Channel interrupted by ANY attack damage > 0 on the shaman → `IsChanneling = false`, cooldown set to 15, effect removed from player, `StatusExpiredEvent { Reason = "chant_interrupted" }` emitted.
- DOT damage does NOT interrupt (matches PoC).
- Silenced shaman cannot start chant — `SilencedEffect` blocks it at the decision point; emit `SilencedCastBlockedEvent` (same gate as scroll/wand use).
- Active channel persists through hex cooldown ticks; both abilities track independent cooldowns.
- Fast-test suite passes.

**Files to add:**
- `src/Logic/Combat/StatusEffects/DissonantChantEffect.cs`:
  - `IStatusEffect`; `EffectName = "dissonant_chant"`; default `RemainingTurns = 3`.
  - Carries `int MoveEnergyTax { get; set; } = 1` (default — currently only the +1 form is used).
  - Carries `int ChantingShamanId { get; set; }` so the effect can be removed when the shaman's channel ends.
- `tests/Core/OrcShamanChantTests.cs`:
  - `Chant_StartsWhenInRangeAndOffCooldown`
  - `Chant_AppliesDissonantChantEffectToPlayer`
  - `Chant_ConsumesShamanTurn` (shaman waits/skips while channeling)
  - `Chant_ContinuesForThreeTurns`
  - `Chant_EndsNaturallyAfterThreeTurns_SetsCooldown15`
  - `Chant_InterruptedByAttackDamage_EndsImmediately`
  - `Chant_NotInterruptedByDotDamage`
  - `Chant_SilencedShamanCannotStart` (emits SilencedCastBlocked)
  - `Chant_BlockedByDisorientation` (PoC override: status overrides take priority)
  - `Chant_PlayerMovementCostsExtraTurn` (player tries to move on odd turn → skip)
  - `Chant_HexAndChantCooldownsIndependent`

**Files to modify:**
- `src/Logic/ECS/OrcShamanComponent.cs` — add:
  - `bool IsChanneling { get; set; } = false;`
  - `int ChantTurnsRemaining { get; set; } = 0;`
  - `int ChantCooldownRemaining { get; set; } = 0;`
  - `int ChantCooldownTurns { get; set; } = 15;` (PoC)
  - `int ChantRange { get; set; } = 5;` (PoC)
  - `int ChantDuration { get; set; } = 3;` (PoC)
  - `int? ChantTargetEntityId { get; set; } = null;`
- `src/Logic/AI/OrcShamanAI.cs` — rewrite the decision block (priorities preserved):
  1. Dead / not alerted / status overrides — unchanged.
  2. **If `IsChanneling`** — decrement `ChantTurnsRemaining`; if 0, end channel naturally (set cooldown=15, remove effect from player). Return `MonsterAction.Wait()` regardless (channeling consumes the turn).
  3. Tick `HexCooldownRemaining` and `ChantCooldownRemaining`.
  4. Panic retreat (DangerRadius) — unchanged.
  5. **Try start chant**: if silenced → emit blocked event + skip; else if in range + off cooldown → apply `DissonantChantEffect` to player, set `IsChanneling=true`, `ChantTurnsRemaining=3`, return `Wait()`.
  6. Try hex — unchanged.
  7. Positioning + melee fallback — unchanged.
- `src/Logic/Combat/StatusEffects/StatusEffectProcessor.cs`:
  - Add `DissonantChantEffect` to the name dictionary.
  - In `ProcessTurnStart` for the entity carrying `DissonantChantEffect`: behave like `SlowedEffect` — skip on `turnCount % 2 == 1` (unless FreeAction). Emit `SkipTurnEvent { EffectName = "dissonant_chant" }`.
  - **Important:** `DissonantChantEffect` does NOT decrement its own duration on the player; it's removed by the shaman when the channel ends (natural expiry or interrupt). Add it to the `IsPermanent`-like guarded set OR set `RemainingTurns` to a large sentinel and explicitly remove via `RemoveEffect` from the shaman AI. **Recommendation:** sentinel approach — set RemainingTurns=999 when applied, let the shaman remove it explicitly. Simpler than introducing a new "managed effect" concept. If the shaman dies while channeling, add a death-time cleanup pass that removes any `DissonantChantEffect` whose `ChantingShamanId` matches the dead entity.
- `src/Logic/Core/TurnController.cs`:
  - In the same place TASK-003 hooks `OnAttackDamageTaken` (after damage > 0 hit on a monster): if defender has `OrcShamanComponent { IsChanneling: true }`, end the channel:
    - Set `IsChanneling = false`, `ChantTurnsRemaining = 0`, `ChantCooldownRemaining = 15`.
    - Remove `DissonantChantEffect` from the player (`StatusEffectProcessor.RemoveEffect`), emit `StatusExpiredEvent { Reason = "chant_interrupted" }`.
  - In `DropMonsterLoot` / death path for shamans: if `IsChanneling`, clean up player's `DissonantChantEffect`.

**Notable design call.** PoC tracks chant via separate `is_channeling`/`chant_turns_remaining` fields on the AI object, plus a `DissonantChantEffect` on the player. We mirror that exactly — the shaman owns the channel state, the player owns the effect, and the connection is by entity ID. Avoids tying the effect's lifetime to its own RemainingTurns, which would let the effect outlive the shaman in edge cases.

---

### TASK-005 — YAML wiring

**Layer:** content
**Type:** scenario / data
**Acceptance:**
- `orc_shaman` entry in `config/entities.yaml` gains chant fields with PoC values.
- `slime`, `large_slime`, `greater_slime` entries gain `engulfs_on_hit: true`.
- Loaders accept the new fields without errors.
- Existing tests continue to pass.

**Files to modify:**
- `config/entities.yaml`:
  - `orc_shaman` (lines 122–142): add
    ```yaml
    chant_radius: 5
    chant_cooldown_turns: 15
    chant_duration_turns: 3
    chant_enabled: true
    ```
    **Note:** The chant config is currently hard-coded in the component via PoC values. The YAML fields are forward-compatible but not strictly required for v1 — `OrcShamanComponent` defaults already match PoC. Add them to YAML so designers can tune without recompiling, but don't block on loader support if it adds scope. **Decision needed:** ship with hardcoded defaults in `OrcShamanComponent` (no YAML changes), OR add YAML fields + loader/factory plumbing. Recommend hardcoded for v1; YAML when a tuning pass needs it.
  - `slime` (line 412): add `engulfs_on_hit: true` under the existing fields.
  - `large_slime` (line 448): inherits via `extends: slime`, no change needed.
  - `greater_slime` (line 526): inherits via `extends: large_slime`, no change needed.
- `src/Logic/Content/MonsterDefinition.cs` — add `EngulfsOnHit` field (covered in TASK-002).
- `src/Logic/Content/ContentLoader.cs` — merge rule for `EngulfsOnHit`.

---

### TASK-006 — Silence vs Shaman identity scenario

**Layer:** content + test
**Type:** scenario
**Acceptance:**
- New scenario file `config/levels/scenario_silence_orc_shaman_identity.yaml` matches PoC structure.
- Bot policy uses or can use silence scrolls (check `Logic/Balance/BotBrain.cs` for existing scroll-use logic; if none, this scenario uses the same `tactical_fighter` bot and we just place a silence scroll in inventory, accepting that the bot may not use it — and downgrade the test to "shaman attempts to cast, scenario completes without crash").
- Harness run yields:
  - At least 5 chant attempts across 30 runs (proves chant logic fires)
  - If bot uses silence: `silenced_casts_blocked > 0`
- File loads without errors.

**Files to add:**
- `config/levels/scenario_silence_orc_shaman_identity.yaml` — port of PoC scenario with C# field names.

**Files to inspect (no modification expected):**
- `src/Logic/Balance/BotBrain.cs` — confirm whether silence scroll is in the bot's repertoire. If not, note as deferred (we add the scenario as a fixture; full bot policy port is out of scope here).

---

### TASK-007 — Slime engulf identity scenario

**Layer:** content + test
**Type:** scenario
**Acceptance:**
- New scenario `config/levels/scenario_slime_engulf_identity.yaml`:
  - Depth 3.
  - 2–3 slimes positioned adjacent to player start.
  - Player has decent weapon + 2 healing potions.
  - 30 runs, 200 turn limit.
- Harness shows:
  - Engulfed effect applied on player at least once per run.
  - Player movement skip events > 0.
  - Death rate within band (slimes are weak; deaths should be rare).
- File loads without errors.

**Files to add:**
- `config/levels/scenario_slime_engulf_identity.yaml`.

---

### TASK-008 — Existing scenario refresh

**Layer:** content
**Type:** scenario / harness
**Acceptance:**
- After all logic changes land, re-run existing identity scenarios and confirm:
  - `scenario_orc_shaman_identity` — still passes (H_PM, H_MP, Death% within band). Chant should now appear in transcripts.
  - `scenario_orc_chieftain_identity` — Death% may drop slightly because rally now ends when chieftain is hit. If drop is > 15 pts, flag as composition issue.
  - `scenario_troll_identity` — fire suppression should not affect this scenario (no fire source), so metrics should be identical.
- Update YAML expected-metric comments if drift exceeds 10%.

**Files to modify (only if drift):**
- `config/levels/scenario_orc_chieftain_identity.yaml` — update expected metrics comment.
- `config/levels/scenario_orc_shaman_identity.yaml` — update expected metrics comment.

---

### TASK-009 — Harness verification + report

**Layer:** test
**Type:** analysis
**Acceptance:**
- Run `dotnet test --filter "Category!=Slow"` — all green.
- Run scenario harness for each affected scenario:
  ```bash
  dotnet run --project tools/Harness -- --scenario orc_shaman_identity --runs 30 --seed 1337 --json
  dotnet run --project tools/Harness -- --scenario orc_chieftain_identity --runs 30 --seed 1337 --json
  dotnet run --project tools/Harness -- --scenario troll_identity --runs 30 --seed 1337 --json
  dotnet run --project tools/Harness -- --scenario slime_engulf_identity --runs 30 --seed 1337 --json
  dotnet run --project tools/Harness -- --scenario silence_orc_shaman_identity --runs 30 --seed 1337 --json
  ```
- Snapshot JSON outputs to `reports/monster_specials_<date>/`.
- Compare H_PM / H_MP / Death% against pre-change baseline. Flag any depth-3/4 scenario where Death% shifts > 10 pts.
- Confirm dungeon-soak run (`--dungeon --floors 6 --runs 50`) still completes without crashes.
- Write findings into a brief comment block in `plan_monster_specials_impl.md` (close-out summary).

---

## Scenario Coverage Matrix

| Mechanic | Existing scenario | New scenario | What it proves |
|----------|-------------------|--------------|----------------|
| Fire suppresses troll regen | (none) | (none — extend existing troll scenario in TASK-008 if metrics shift) | Unit tests cover the rule; harness will show fire-arrow users finishing trolls faster once ranged plan lands. **Not a blocker.** |
| Engulf | (none) | `scenario_slime_engulf_identity.yaml` | Effect applies, refreshes, skips alternating turns; player adjacency tracking works in arena. |
| Rally ends on damage | `scenario_orc_chieftain_identity.yaml` | (none) | Existing scenario will show Death% drop and player win rate up after change; unit tests cover the rule. |
| Chant of Dissonance | `scenario_orc_shaman_identity.yaml` | `scenario_silence_orc_shaman_identity.yaml` | Existing scenario shows chant fires + interrupts; silence scenario proves silence gate works. |

---

## Risks & Open Questions

### R1 — Rally end-on-damage may over-buff the player at depth 3
Death% in `scenario_orc_chieftain_identity` was 36.7% in the PoC reference run. Removing the rally permanence makes the chieftain's signature ability much weaker; players who hit the chieftain once shut off the +1/+1 on three orcs forever. Real impact could push that scenario well below band. **Mitigation:** if depth-3 Death% drops below 20% post-change, consider keeping rally for N turns after chieftain damage (PoC uses 0; we could use 2–3) before removal. **Decision after harness data — do not pre-emptively diverge from PoC.**

### R2 — Chant + slime engulf both produce "every other turn skip"
Player who is chanted AND engulfed: do they skip twice (both effects apply on the same turn) or once (effects share the alternating-skip slot)? PoC has no overlap test. **Recommendation:** single skip slot — `ProcessTurnStart` checks `(SlowedEffect | EngulfedEffect | DissonantChantEffect) && turnCount % 2 == 1` as a unified gate. Stacking these would be brutal and unfun. Add a test `MultipleSkipEffects_OnlySkipsOnce`.

### R3 — Silence scroll bot policy may not exist in C# yet
PoC has `SilenceScrollUserPolicy`. C# `BotBrain` likely does not. If we ship `scenario_silence_orc_shaman_identity.yaml` without a bot that uses silence, the metric `silenced_casts_blocked` will be zero — the scenario becomes proof-of-existence only. **Acceptable** — scenario lands as a fixture; bot policy can be added in a separate plan when needed.

### R4 — Chant state on shaman is fragile
`OrcShamanComponent.IsChanneling` is mutable state that lives between turns. If the shaman dies mid-channel and we forget to clean up `DissonantChantEffect` on the player, the player is locked into a permanent move-cost penalty. The death-cleanup pass in TASK-004 mitigates this, but it's an easy thing to miss in future refactors. Add a test `Chant_PlayerEffectClearedWhenShamanDies`.

### R5 — Engulf adjacency check cost
`StatusEffectProcessor.ProcessTurnStart` runs for every entity every turn. Adding an "iterate alive monsters and check adjacency" inside the player's turn-start adds O(M) work per turn, where M = monster count. At typical floor counts (~30 monsters), this is trivial. At stress (~150), still well under 1ms. **Not a concern.**

### R6 — Chant blocks shaman from doing anything else
PoC's shaman, while channeling, only channels — no attack, no movement, no hex. If three turns of pure channel feels too punishing for the shaman (he becomes a free kill), we may want to allow movement during channel. PoC does not, so we mirror it. **Watch in harness:** if shaman survival rate in `scenario_orc_shaman_identity` collapses post-change, revisit.

### R7 — Decision needed: shaman chant YAML fields (TASK-005)
Whether to expose chant cooldown/range as YAML fields now or hardcode. Recommend hardcode in `OrcShamanComponent` defaults for v1 — same as how hex is currently configured. Loader/factory plumbing for new fields is busywork that can wait until a tuning pass needs it.

---

## Deferred (out of scope for this pass)

- **Rally directive** — PoC rallied orcs prioritize the chieftain's chosen target. C# faction system already provides reasonable targeting; not blocking.
- **Plague spread polish** — covered under `plan_status_effects_impl.md`; any remaining gaps belong there, not here.
- **Skirmisher hit-and-run leap-away** — `SkirmisherAI.cs` already implements leap-toward. Leap-away after attacking is the PoC `hit-and-run` variant; not currently wired. Defer until a "kiting AI" pass exists.
- **Silence scroll bot policy** — TASK-006 ships scenario only; bot AI is separate work.
- **`scenario_chant_interrupt_test`** — implicit in `scenario_silence_orc_shaman_identity`; explicit scenario only useful if we want to measure interrupts/run.
- **Hostile-all faction for slimes** — listed in `deferred_slime_abilities.md`. Not part of this plan.
