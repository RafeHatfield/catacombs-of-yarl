# Harness Parity Milestone

## Context

We've built the C# balance pipeline in a single sprint: ECS, combat, equipment, healing, positioning, depth scaling, momentum, YAML loading, pressure model. 17 commits, 145 tests, all green.

But the pressure model is telling us the numbers don't match the prototype's target bands:
- **H_PM observed: 6-12** (target 3.5-4.5) — player kills too slowly
- **H_MP observed: 22-28** (target 10-14) — monsters don't threaten enough

Root cause: missing damage modifiers on both sides. Orcs fight barehanded (prototype gives 75% weapons). No weapon affixes. No damage resistance/vulnerability. Crit threshold hardcoded to 20.

**Goal:** The C# harness produces trustworthy balance data for depths 1-6, with H_PM and H_MP trending toward target bands. Not pixel-perfect prototype match, but data-trustworthy — every gap has a diagnosed reason.

## Phase 1: Combat Modifier Wiring (balance-critical)

These close the DPR gap. Each is independently testable.

### Task 1.1: Wire CritThreshold from weapon into CombatResolver
- `Equippable.CritThreshold` exists (default 20) but CombatResolver hardcodes `d20 == 20`
- Change: read weapon's CritThreshold, crit when `d20 >= threshold`
- **Files:** `src/Logic/Combat/CombatResolver.cs`
- **Test:** keen weapon (threshold 19) crits on 19 and 20; default only on 20
- **Acceptance:** keen doubles crit rate from 5% to 10%

### Task 1.2: Damage resistance/vulnerability system
- MonsterDefinition parses `damage_resistance`/`damage_vulnerability` but nothing enforces it
- New `DamageModifiers` component: resistance type halves damage, vulnerability doubles it
- Wire into CombatResolver after damage calc, check defender's modifiers vs weapon DamageType
- **Files:** new `src/Logic/Combat/DamageModifiers.cs`, modify `CombatResolver.cs`, `MonsterFactory.cs`
- **Test:** zombie takes half from piercing dagger, double from bludgeoning club
- **Acceptance:** damage type correctly modifies final damage in harness runs

### Task 1.3: Affix weapon definitions in YAML
- Add `keen_dagger` (crit 19), `vicious_shortsword` (2-7 dmg), `fine_longsword` (+1 hit), `masterwork_longsword` (+1 hit, +1 dmg)
- Wire `crit_threshold` through ItemDefinition → ItemFactory → Equippable
- **Files:** `config/entities.yaml`, `src/Logic/Content/ItemDefinition.cs`, `src/Logic/Content/ItemFactory.cs`
- **Test:** load keen_dagger, verify CritThreshold == 19
- **Acceptance:** all four affix types loadable and functional
- **Depends on:** 1.1

### Task 1.4: Wire speed_bonus on weapon items
- `ItemDefinition` needs `speed_bonus` field (Python: quickfang_dagger has 0.18)
- ItemFactory creates/updates SpeedBonusTracker.EquipmentRatio when equipping speed weapons
- **Files:** `src/Logic/Content/ItemDefinition.cs`, `src/Logic/Content/ItemFactory.cs`, `config/entities.yaml`
- **Test:** equip quickfang_dagger, verify SpeedBonusTracker.EquipmentRatio == 0.18
- **Acceptance:** weapon speed_bonus flows through to entity's momentum system

## Phase 2: Monster Equipment Spawning (balance-critical)

The single biggest H_MP lever. Armed orcs hit harder.

### Task 2.1: Equipment spawn config in MonsterDefinition
- Add `equipment` YAML section: `spawn_chances` (per slot), `equipment_pool` (weighted item lists)
- Match Python prototype format exactly
- Also update ContentLoader merge logic to handle equipment block inheritance (currently only merges `stats` specially — equipment needs similar deep-merge so orc_grunt inherits orc's pools)
- **Files:** `src/Logic/Content/MonsterDefinition.cs`, `src/Logic/Content/ContentLoader.cs`
- **Test:** parse orc equipment config, verify 0.75 weapon chance, weighted pool; verify orc_grunt inherits equipment via extends
- **Acceptance:** MonsterDefinition correctly deserializes and inherits equipment spawn config

### Task 2.2: MonsterEquipmentSpawner service
- Takes equipment config + ItemFactory + SeededRandom
- Rolls per slot, selects from weighted pool, creates and equips item
- Must be deterministic
- **Files:** new `src/Logic/Content/MonsterEquipmentSpawner.cs`
- **Test:** with seed 1337, verify deterministic results; verify ~75% weapon rate over 1000 spawns
- **Depends on:** 2.1

### Task 2.3: Wire spawner into MonsterFactory + harness
- MonsterFactory calls spawner when equipment config present
- Harness passes ItemFactory to MonsterFactory
- **Files:** `src/Logic/Content/MonsterFactory.cs`, `src/Logic/Balance/ScenarioHarness.cs`
- **Test:** run depth 2 baseline, verify H_MP decreases (armed monsters hit harder)
- **Depends on:** 2.2
- **This is the inflection point** — H_MP starts moving toward target band

### Task 2.4: Orc equipment pools in entities.yaml
- Add to `orc`: 75% weapon (40% club, 30% dagger, 30% shortsword), 50% armor (100% leather)
- Verify orc_grunt inherits via `extends`
- **Files:** `config/entities.yaml`
- **Depends on:** 2.1

### Task 2.5: Measure armed-orc impact on H_PM and H_MP
- **Risk identified in review:** orc armor (+2 AC) makes player hit LESS often, pushing H_PM up (wrong direction). Weapon damage helps H_MP but armor hurts H_PM.
- Run depth 2 baseline with: (a) weapons only, (b) weapons + armor, (c) compare against unarmed baseline
- If armor causes H_PM regression: reduce armor spawn chance or defer armor to later milestone
- This is a measurement checkpoint, not a code task
- **Depends on:** 2.3
- **Decision gate:** results determine whether orc armor stays in the baseline scenarios

## Phase 3: Scenario Coverage (high-value)

Expand from 6 scenarios to depth 1-6 baseline coverage.

### Task 3.1: Depth 1, 3, 4, 6 baseline scenarios
- Python prototype uses dagger as baseline weapon through depth 5, longsword at depth 6
- Depth 1: 2 orcs, dagger, leather, 1 potion (safe learning)
- Depth 3: 3 orcs + 1 brute, dagger, leather, 2 potions (pressure begins)
- Depth 4: mixed orcs + zombies, dagger, leather, 2 potions (tests resistance)
- Depth 6: 4 orcs + 1 brute (armed), longsword, leather, 3 potions (brutal)
- **Files:** 4 new YAML files in `config/levels/`
- **Depends on:** Phase 2 (armed monsters needed for realistic data)
- **Note:** weapon progression revised to match Python — dagger is the consistent baseline, gear probes (Task 3.2) test better weapons as variants

### Task 3.2: Affix probe scenarios
- Depth 2 and 5 variants: keen, vicious, fine, masterwork
- Isolate each affix's impact at two depth bands
- **Files:** 8 new YAML files in `config/levels/`
- **Depends on:** 1.3 + Phase 2

## Phase 4: Target Band Validation (high-value)

### Task 4.1: Full target band evaluation
- Port death_rate targets per depth alongside existing H_PM/H_MP bands
- Add `Evaluate()` + `Diagnose()` — given metrics, return OK/LOW/HIGH + actionable text
- **Files:** expand `src/Logic/Balance/PressureModel.cs`
- **Test:** feed known out-of-band metrics, verify correct diagnosis

### Task 4.2: Depth 1-6 validation test suite
- Runs all baseline scenarios, computes pressure metrics, evaluates against bands
- Formatted report: depth, death%, H_PM, H_MP, status
- Tagged `[Category("Slow")]`
- **Files:** new `tests/Balance/TargetBandValidationTests.cs`
- **Depends on:** Phase 3 + 4.1

## Phase 5: Quality (nice-to-have, after parity)

- Bot persona framework (cautious, aggressive at minimum)
- Auto-compute H_PM/H_MP in AggregatedMetrics (remove manual avgMonsterHp param)
- Monster equipment tracking in RunMetrics
- Balance suite runner CLI tool (run all scenarios, output report)

## Deferred: Awareness & Surprise Attacks

Surprise attacks (auto-crit on unaware enemies) are an **opt-in skill ceiling** mechanic. They're powerful but situational — most encounters start with both sides aware.

**Design decision:** Baseline scenarios use `state: "aware"` for all monsters. Target bands are calibrated against aware-state combat. This ensures the difficulty curve is fair for players who don't use stealth/positioning for surprise openers.

Surprise attacks get their own scenario family later:
- Same encounters, with and without surprise opener
- Measures the delta: how much easier does surprise make things?
- If surprise is "nice bonus" → good. If surprise is "required to survive" → encounter is overtuned.

This prevents the trap of balancing around the assumption that players always get a free crit opener, which would make non-surprise combat feel unfairly hard.

## Build Order

Parallel group A (independent, do first):
- **1.1** crit threshold wiring
- **1.2** damage resistance/vulnerability
- **2.1** equipment YAML parsing

Then sequential:
- **1.3** affix weapons (needs 1.1)
- **1.4** weapon speed_bonus (independent but logical after 1.3)
- **2.2** equipment spawner (needs 2.1)
- **2.4** orc equipment pools in YAML (needs 2.1)
- **2.3** wire spawner into factory + harness (needs 2.2) ← **inflection point**
- **2.5** measure armed-orc impact ← **decision gate** (armor yes/no)
- **4.1** target band evaluation
- **3.1** depth 1/3/4/6 scenarios (needs Phase 2 + 2.5 decision)
- **3.2** affix probes (needs 1.3 + Phase 2)
- **4.2** validation suite (needs Phase 3 + 4.1)

## Verification

After all phases complete:
```bash
dotnet test --filter "Category!=Slow"    # fast suite passes
dotnet test                               # full suite including slow validation
```

The validation suite (4.2) prints a depth 1-6 report showing death%, H_PM, H_MP vs target bands. "Done" means every metric is either in-band or has a diagnosed, understood reason for deviation.

## Critical Files

| File | Changes |
|------|---------|
| `src/Logic/Combat/CombatResolver.cs` | Crit threshold + resistance |
| `src/Logic/Content/MonsterFactory.cs` | Equipment spawning |
| `src/Logic/Content/MonsterDefinition.cs` | Equipment YAML config |
| `src/Logic/Balance/ScenarioHarness.cs` | Pass ItemFactory for monster equipment |
| `config/entities.yaml` | Affixes, orc equipment pools |
| `src/Logic/Balance/PressureModel.cs` | Target band evaluation |
