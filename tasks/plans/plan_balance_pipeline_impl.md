# Plan: Balance Pipeline Implementation (Production Build)

## Status: [x] Complete — all 5 phases implemented, 1838 tests pass

This plan ports the Python PoC's balance pipeline (`balance_suite.py`, `etp_config.yaml`, `analysis/depth_pressure_model.py`, `etp_sanity.py`) to C#. It is the highest-priority infrastructure work — without it, every other balance change is a guess.

**Parent plan:** `tasks/plans/plan_balance_pipeline.md`
**PoC reference:** `~/development/rlike/`

---

## Goal

A balance pipeline where:
1. A single command (`harness --suite`) emits a PASS/WARN/FAIL verdict against per-depth target bands.
2. A single command (`harness --baseline save|compare`) catches silent regressions.
3. ETP encounter budgeting is YAML-driven, validates at room/floor scope, has a sanity tool.
4. Depth pressure reports diagnose where each depth band sits relative to design intent and derive damage-multiplier recommendations.
5. Everything is deterministic at seed 1337 — running the suite twice produces byte-identical JSON.

**Non-goals (out of scope, deferred):**
- Pity system / loot regression. Covered by `plan_loot_policy.md`.
- Bot personas. Covered by `plan_bot_personas.md`.
- ETP-budgeted procedural room generation. Sanity tooling is in scope; engine-time enforcement is not (PoC tracks this in `services/encounter_budget_engine.py`; C# has stub `EtpCalculator` but no engine integration). Tracked separately once sanity coverage is green.

---

## Metrics Gap Analysis

PoC `AggregatedMetrics` (`tools/balance_suite.py:normalize_metrics`) and C# `AggregatedMetrics` (`src/Logic/Balance/RunMetrics.cs:148-258`) collect the same primitives. Gaps to close:

| PoC metric | PoC source | C# equivalent | Gap |
|------------|-----------|---------------|-----|
| `total_player_attacks` | `metrics.total_player_attacks` | `RunMetrics.PlayerAttacks` (sum across runs) | OK |
| `total_player_hits` | `metrics.total_player_hits` | `RunMetrics.PlayerHits` | OK |
| `total_monster_attacks` | `metrics.total_monster_attacks` | `RunMetrics.MonsterAttacks` | OK |
| `total_monster_hits` | `metrics.total_monster_hits` | `RunMetrics.MonsterHits` | OK |
| `total_player_damage_dealt` | (Phase 22.4) | `RunMetrics.PlayerDamageDealt` | OK |
| `total_monster_damage_dealt` | (Phase 22.4) | `RunMetrics.MonsterDamageDealt` | OK |
| `total_kills_by_source.PLAYER` | engine event | `RunMetrics.MonstersKilled` | OK (PoC distinguishes kill source; C# treats PLAYER kills as the only relevant bucket — fine for now) |
| `player_deaths` | engine | `runs.Count(PlayerDied)` aggregator | OK |
| `average_turns` | engine | `AggregatedMetrics.AvgTurns` | OK |
| `total_bonus_attacks_triggered` | engine | `RunMetrics.BonusAttacks` (player+monster combined) | **Partial** — PoC discriminates; C# does not. Acceptable for now; document in `RunMetrics.cs` comment. |
| `monster_hp_budget_per_run` | hardcoded in `KNOWN_SCENARIO_CONFIGS` | `RunMetrics.MonsterAvgMaxHp × spawn count` (derived at run-start) | **Improved** — C# derives from actual spawn, PoC hardcodes. Cleaner. |
| `player_hp` | hardcoded 54 | `RunMetrics.PlayerMaxHp` | OK |

**Verdict:** C# metrics are equivalent or superior. No new instrumentation needed for Phases 1-5. One missing capability worth noting: PoC's `pressure_index = avg_monster_attacks - avg_player_attacks` (an action-economy proxy) is not surfaced in C# `AggregatedMetrics`. Phase 1 derives it on the fly from existing data (`AvgMonsterAttacks - AvgPlayerAttacks`), no schema change needed.

---

## Master Build Order

```
Phase 0: Deterministic seeding helper (prereq for all phases)
   │
   ├── Phase 1: Acceptance Matrix (--suite)
   │     └── unblocks: CI integration, every balance change going forward
   │
   ├── Phase 3: Full ETP System (band config, calculator, behavior modifiers)
   │     └── unblocks: Phase 5 (sanity tool consumes ETP config)
   │
Phase 2: Baseline storage & regression (--baseline save|compare)
   │   depends on: Phase 1 (consumes the JSON shape Phase 1 produces)
   │   unblocks: silent-regression detection, PR-gating
   │
Phase 4: Depth pressure report (--depth-report)
   │   depends on: Phase 1 (consumes per-scenario AggregatedMetrics)
   │   unblocks: diagnostic recommendations, scaling-curve tuning
   │
Phase 5: ETP sanity tool (--etp-sanity)
    depends on: Phase 3 (consumes ETP config + calculator)
    depends on: dungeon worldgen (already built — DungeonFloorBuilder)
    unblocks: CI gate on encounter generation, room-budget enforcement work
```

**Critical path:** Phase 0 → Phase 1 → Phase 2 (the CI loop). Phases 3-5 can land in parallel after Phase 0.

---

## What Breaks Without Each Phase

| Phase | What is impossible without it |
|-------|-------------------------------|
| 0 | Reproducible harness runs. Without stable per-run seeding, two `--suite` runs produce different metrics — verdicts become noise. |
| 1 | "Did this PR regress balance?" cannot be answered. Builders ship changes blind; the existing `--all` flag prints results but has no pass/fail contract. |
| 2 | Regressions cannot be detected automatically. Drift accumulates across PRs; nobody notices depth 3 went from 12% deaths to 28% over six weeks. |
| 3 | Encounter generation is unbudgeted. Rooms spawn whatever fits geometrically; depth 6 floors might contain 4× the threat of depth 5 floors. ETP stub in `EtpCalculator.cs` returns `etp_base` but applies no band scaling. |
| 4 | "Why is depth 4 spiking?" requires manual data wrangling. The PoC's report tells you in 200 lines exactly which lever to pull; without it, the team interprets raw H_PM/H_MP by hand. |
| 5 | "Did the new dungeon templates blow the budget?" cannot be answered. Worldgen changes ship without per-room ETP validation. |

---

## CI Integration Notes

Target shape (post-Phase-2):

```yaml
# .github/workflows/balance.yml (sketch)
- name: Fast tests
  run: dotnet test --filter "Category!=Slow"

- name: Balance acceptance suite (compare against baseline)
  run: |
    dotnet run --project tools/Harness -- --suite \
      --baseline reports/baselines/balance_suite_baseline.json \
      --out-dir reports/balance_suite/ci_${{ github.sha }}
  # Exit code: 0 = PASS/WARN, 1 = FAIL → blocks PR

- name: ETP sanity (strict mode, post-Phase-5)
  run: |
    dotnet run --project tools/Harness -- --etp-sanity --strict
  # Exit code: 0 = no OVER violations in normal rooms, 1 = OVER detected
```

Runtime budget: 15 scenarios × 50 runs × ~0.5s/run ≈ 6 minutes. Acceptable for PR gates. Add `--fast` (subset matrix, 20 runs) for inner-loop local use.

PoC pattern (`balance_suite.py:301-479`) writes `verdict.json` with an `acceptance_status` field consumed by the workflow's failure step. Port this shape verbatim.

---

## Phase 0 — Deterministic Seeding Helper

### What it does
Adds `StableScenarioSeed(scenarioId, runIdx, seedBase)` — a SHA-256-derived 32-bit seed function. Today `ScenarioHarness.Run()` uses `baseSeed + i` (`ScenarioHarness.cs:46`), which is deterministic but not isolated per scenario — runs of `depth3_orc_brutal` and `depth3_orc_brutal_fine` at run index 5 use the same seed, so combat rolls overlap. Per-scenario derivation prevents accidental correlation across the matrix.

### PoC reference
- `~/development/rlike/engine/rng_config.py:88-121` — `stable_scenario_seed(scenario_id, run_idx, seed_base)`, SHA-256 hash, first 4 bytes as `int.from_bytes(byteorder='big')`.
- `~/development/rlike/tests/test_balance_suite_determinism.py:26-69` — determinism contract.

### C# design
New static class `src/Logic/Balance/SeedDerivation.cs`:

```csharp
public static class SeedDerivation
{
    /// <summary>
    /// Deterministic per-scenario, per-run seed. SHA-256(scenarioId:runIdx:seedBase),
    /// take first 4 bytes as unsigned big-endian int. Matches PoC stable_scenario_seed().
    /// </summary>
    public static int Stable(string scenarioId, int runIdx, int seedBase = 1337);
}
```

### PoC-verified values
- Hash: SHA-256 (NOT MD5 — PoC explicitly chose SHA-256 for cross-version stability).
- Byte order: big-endian.
- Bytes used: first 4.
- Key format: `f"{scenario_id}:{run_idx}:{seed_base}"` (colon-separated, no padding).

### Build order
Land first. Wire `ScenarioHarness.Run()` to call `SeedDerivation.Stable(scenario.ScenarioId, i, baseSeed)` instead of `baseSeed + i`. This will shift every existing scenario's results (different seeds → different rolls). That's fine — Phase 2 captures a fresh baseline post-cutover.

### C# port checklist
- [ ] `src/Logic/Balance/SeedDerivation.cs` — new file, `using System.Security.Cryptography;`
- [ ] `src/Logic/Balance/ScenarioHarness.cs:46` — replace `baseSeed + i` with `SeedDerivation.Stable(scenario.ScenarioId, i, baseSeed)`
- [ ] `tests/Balance/SeedDerivationTests.cs` — new file

### Test coverage
- Same inputs → same seed (10 calls, same args, all equal).
- Different `runIdx` → different seeds (50 calls, all unique).
- Different `scenarioId` → disjoint seed sets (`depth2_orc_baseline` vs `depth2_orc_baseline_fine`, 10 runs each, no overlap).
- Different `seedBase` → different seeds.
- Cross-language reference value: pick one fixed input (`"depth3_orc_brutal", 0, 1337`), capture PoC output, assert C# matches. Verifies SHA-256 + byte-order are byte-identical.

### Open questions / risks
- **Existing baselines (provisional bands) will shift.** `PressureModel.Provisional_H_PM` etc. (`PressureModel.cs:132-157`) were calibrated under `baseSeed + i`. After Phase 0, recalibrate by running the suite once with the new seeds, observing the band centers, and updating the comments + bounds. Tracked as part of Phase 1 baseline capture.

---

## Phase 1 — Balance Acceptance Matrix

### What it does
Adds a `--suite` mode to the harness CLI that runs a fixed scenario matrix, evaluates each scenario against per-depth target bands (`PressureModel.EvaluateProvisional`), and emits a single PASS/WARN/FAIL verdict plus per-scenario rows. Writes a markdown table for humans and a `verdict.json` for CI.

### PoC reference
- `~/development/rlike/tools/balance_suite.py:34-61` — `SCENARIO_MATRIX` (15 scenarios across depth 2/3/5 with weapon variants).
- `~/development/rlike/tools/balance_suite.py:64-70` — `THRESHOLDS` for WARN/FAIL classification.
- `~/development/rlike/tools/balance_suite.py:172-190` — `classify_verdict()`.
- `~/development/rlike/tools/balance_suite.py:193-298` — markdown + verdict-JSON formatters.
- `~/development/rlike/tools/balance_suite.py:301-479` — orchestrator.

### C# design

New file `tools/Harness/SuiteRunner.cs`:

```csharp
public static class SuiteRunner
{
    public record SuiteEntry(string ScenarioId, int Runs, int TurnLimit);
    public record SuiteResult(
        string ScenarioId,
        int Runs,
        AggregatedMetrics Metrics,
        PressureEvaluation Evaluation,
        string Verdict);  // "PASS" | "WARN" | "FAIL" | "PROBE"

    public static IReadOnlyList<SuiteEntry> Matrix { get; } = /* hardcoded — see PoC values below */;

    public static int Run(
        ScenarioRunner runner,
        DirectoryInfo outDir,
        int seedBase,
        bool fast,
        out List<SuiteResult> results);
}
```

CLI surface (extends `tools/Harness/Program.cs`):
- `--suite` — run matrix.
- `--suite --fast` — runs a curated 6-scenario subset (depth 1/2/3/4/5/6 calibration only, 20 runs each).
- `--suite --out-dir <path>` — override output dir. Default: `reports/balance_suite/<UTC timestamp>/`.
- `--suite --baseline <path>` — passed to Phase 2 (no-op in Phase 1; reserved for clean CLI surface).

Output files in `<out-dir>`:
- `balance_report.md` — human-readable per-scenario table + summary.
- `verdict.json` — machine-readable summary (see "PoC-verified values" below).
- `summary.json` — full normalized metrics per scenario (input for Phase 2 baseline).
- `metrics/raw/<scenario_id>.json` — per-scenario `AggregatedMetrics` JSON.

### PoC-verified values

**Calibration scenario matrix** (port verbatim from `balance_suite.py:34-61`):

```
depth3_orc_brutal               runs=50, turns=110
depth3_orc_brutal_keen          runs=50, turns=110
depth3_orc_brutal_vicious       runs=50, turns=110
depth3_orc_brutal_fine          runs=50, turns=110
depth3_orc_brutal_masterwork    runs=50, turns=110
depth5_zombie                   runs=50, turns=150
depth5_zombie_keen              runs=50, turns=150
depth5_zombie_vicious           runs=50, turns=150
depth5_zombie_fine              runs=50, turns=150
depth5_zombie_masterwork        runs=50, turns=150
depth2_orc_baseline             runs=40, turns=100
depth2_orc_baseline_keen        runs=40, turns=100
depth2_orc_baseline_vicious     runs=40, turns=100
depth2_orc_baseline_fine        runs=40, turns=100
depth2_orc_baseline_masterwork  runs=40, turns=100
```

C# coverage check: scenarios present in `config/levels/` today — `depth2_orc_baseline`, `depth2_orc_fine`, `depth2_orc_keen`, `depth2_orc_masterwork`, `depth2_orc_vicious`, `depth3_orc_brutal`, `depth5_zombie`. **Missing:** all depth-3 weapon variants (`_keen`, `_vicious`, `_fine`, `_masterwork`), depth-5 weapon variants, and `depth2_orc_baseline_*` weapon variants. Sub-task `TASK-105` creates these scenarios from the existing `depth3_orc_brutal.yaml` and `depth5_zombie.yaml` templates with only the player.weapon field swapped.

**Drift thresholds for verdict classification** (`balance_suite.py:64-70`):

| Metric | WARN at |Δ| ≥ | FAIL at |Δ| ≥ |
|--------|-------|-------|
| death_rate | 0.10 | 0.20 |
| player_hit_rate | 0.05 | 0.10 |
| monster_hit_rate | 0.05 | 0.10 |
| pressure_index | 5.0 | 10.0 |
| bonus_attacks_per_run | 2.0 | 4.0 |

**Verdict logic** (`balance_suite.py:172-190`): any metric crossing FAIL → FAIL; otherwise any crossing WARN → WARN; else PASS.

**Pre-baseline mode:** When no baseline exists, status = `NO_BASELINE`, acceptance_status = `PASS` (`balance_suite.py:264-271`). Suite must succeed on a fresh checkout with no baseline file — useful for bootstrapping.

**Probe handling:** Scenarios with `is_probe: true` in YAML (already wired in `ScenarioDefinition.cs:73`) are reported as `PROBE`, not PASS/FAIL. Match the existing `Program.cs:672-684` behavior.

### verdict.json schema (port from PoC verbatim)

```jsonc
{
  "status": "COMPLETED",             // or "NO_BASELINE"
  "acceptance_status": "PASS",       // PASS | WARN | FAIL — drives CI exit code
  "timestamp": "2026-05-20T14:32:11Z",
  "scenarios": 15,
  "verdicts": { "PASS": 12, "WARN": 2, "FAIL": 1 },
  "details": {
    "depth3_orc_brutal": {
      "verdict": "FAIL",
      "deltas": {
        "death_rate": 0.18,
        "player_hit_rate": 0.02,
        "monster_hit_rate": -0.01,
        "pressure_index": 2.1,
        "bonus_attacks_per_run": 0.3
      }
    }
  }
}
```

Exit codes (`balance_suite.py:464-479`):
- `0` — PASS, WARN, or NO_BASELINE
- `1` — FAIL

### Build order
1. Land Phase 0.
2. Create the 8 missing scenario YAML files (TASK-105).
3. Build `SuiteRunner` standalone — no baseline comparison yet.
4. Wire to `Program.cs` as `--suite`.
5. Verify output shape matches PoC `verdict.json` exactly (Phase 2 will read it).

### C# port checklist
- [ ] `config/levels/scenario_depth2_orc_baseline_keen.yaml` (new)
- [ ] `config/levels/scenario_depth2_orc_baseline_vicious.yaml` (new)
- [ ] `config/levels/scenario_depth2_orc_baseline_fine.yaml` (new)
- [ ] `config/levels/scenario_depth2_orc_baseline_masterwork.yaml` (new)
- [ ] `config/levels/scenario_depth3_orc_brutal_keen.yaml` (new)
- [ ] `config/levels/scenario_depth3_orc_brutal_vicious.yaml` (new)
- [ ] `config/levels/scenario_depth3_orc_brutal_fine.yaml` (new)
- [ ] `config/levels/scenario_depth3_orc_brutal_masterwork.yaml` (new)
- [ ] `config/levels/scenario_depth5_zombie_keen.yaml` (new)
- [ ] `config/levels/scenario_depth5_zombie_vicious.yaml` (new)
- [ ] `config/levels/scenario_depth5_zombie_fine.yaml` (new)
- [ ] `config/levels/scenario_depth5_zombie_masterwork.yaml` (new)
- [ ] `tools/Harness/SuiteRunner.cs` (new)
- [ ] `tools/Harness/Program.cs` — add `--suite`, `--fast`, `--out-dir`, `--baseline` arg parsing
- [ ] `tests/Balance/SuiteRunnerTests.cs` (new)

### Test coverage
- Matrix enumeration: `SuiteRunner.Matrix` has exactly 15 entries (when `--fast` is false) and 6 entries (when `--fast` is true).
- Determinism: two `Run()` calls with same seed produce byte-identical `summary.json`.
- Verdict classification: synthetic `SuiteResult` with `death_rate` delta of 0.21 → FAIL; 0.11 → WARN; 0.04 → PASS.
- NO_BASELINE path: missing baseline file → `status: NO_BASELINE`, exit code 0.
- Probe handling: scenario with `is_probe: true` reported as PROBE in `verdicts` dict.

### Open questions / risks
- **Runtime.** 15 scenarios × 50 runs ≈ 6 minutes on a dev machine. Acceptable for PRs; verify with one full run before merging. If slower than projected, parallelize at the scenario level (`Parallel.ForEach` over `Matrix`) — `ScenarioHarness.Run()` is stateless so this is safe.
- **`pressure_index` semantics.** PoC defines as `avg_monster_attacks_per_run - avg_player_attacks_per_run`. C# `AggregatedMetrics` does not expose this directly; compute on the fly in `SuiteRunner.Normalize()`. Document the formula in code comments.
- **Scenario authoring.** The 12 new YAML files differ only in `player.weapon`. Could be parameterized via a template + overrides — but `ScenarioRunner` reads flat YAML. Keep them as separate files for now; the PoC does the same. Revisit only if the matrix grows past 30 scenarios.

---

## Phase 2 — Baseline Storage & Regression Detection

### What it does
Adds `--baseline save` (writes current `summary.json` to a fixed path) and integrates baseline comparison into `--suite` (default behavior when baseline exists). Without an `--update-baseline` flag, the suite refuses to overwrite the baseline — silent baseline drift is the primary failure mode this prevents.

### PoC reference
- `~/development/rlike/tools/balance_suite.py:321-325` — `--update-baseline` flag semantics.
- `~/development/rlike/tools/balance_suite.py:154-169` — `compute_deltas()`.
- `~/development/rlike/tools/balance_suite.py:425-449` — baseline-update path.
- `~/development/rlike/reports/baselines/balance_suite_baseline.json` — current PoC baseline shape (port the schema, not the values — C# will produce its own numbers).

### C# design

Extends `SuiteRunner`:

```csharp
public static class SuiteRunner
{
    public static int Run(
        ScenarioRunner runner,
        DirectoryInfo outDir,
        int seedBase,
        bool fast,
        FileInfo? baselinePath,
        bool updateBaseline,
        out List<SuiteResult> results);

    // Computes per-metric deltas against baseline.
    public static Dictionary<string, double> ComputeDeltas(
        NormalizedMetrics current, NormalizedMetrics baseline);

    // PASS/WARN/FAIL given a delta dict.
    public static string ClassifyVerdict(Dictionary<string, double> deltas);
}
```

New record:
```csharp
public sealed record NormalizedMetrics(
    string ScenarioId,
    int Runs,
    int Deaths,
    double DeathRate,
    double PlayerHitRate,
    double MonsterHitRate,
    double PressureIndex,        // monster_attacks/run - player_attacks/run
    double BonusAttacksPerRun);
```

Why a separate record (vs. reusing `AggregatedMetrics`): the baseline JSON shape needs to be **stable across schema changes**. If `AggregatedMetrics` grows new fields (e.g., new ranged-combat counters), the baseline doesn't need to be regenerated. `NormalizedMetrics` is a frozen subset matching the PoC verbatim.

CLI surface:
- `harness --suite` (no flag) → compares against `reports/baselines/balance_suite_baseline.json`. If missing, runs in `NO_BASELINE` mode.
- `harness --suite --baseline <path>` → compare against custom baseline.
- `harness --suite --update-baseline` → writes new baseline, exits 0 regardless of FAIL count. PoC pattern from `balance_suite.py:425-449`.

### Baseline JSON schema (verbatim from `reports/baselines/balance_suite_baseline.json`)

```json
{
  "depth3_orc_brutal": {
    "scenario_id": "depth3_orc_brutal",
    "runs": 50,
    "deaths": 5,
    "death_rate": 0.1,
    "player_hit_rate": 0.7150610583446404,
    "monster_hit_rate": 0.37397260273972605,
    "pressure_index": -14.88,
    "bonus_attacks_per_run": 10.28
  }
}
```

Float precision: full IEEE 754 (PoC uses Python's default `json.dump` which serializes 15-17 digit floats). Match this in C# with `JsonSerializerOptions.NumberHandling = AllowNamedFloatingPointLiterals` and default precision.

### Approved-drift annotations (Phase 2.5)

The PoC has no approved-drift mechanism — every baseline change requires an explicit `--update-baseline` run. This is correct: silent updates defeat the purpose.

**Recommended C# extension** (deferrable, but design the schema now): support an optional `_approved_drift` sidecar file `reports/baselines/approved_drift.json`:

```jsonc
{
  "approvals": [
    {
      "scenario_id": "depth5_zombie",
      "metric": "death_rate",
      "delta_min": -0.05,
      "delta_max": 0.15,
      "reason": "Phase 24 v5 retuned zombie damage; expected +10% death drift.",
      "expires_after": "2026-06-01",
      "approved_by": "rafe"
    }
  ]
}
```

If a delta falls within an unexpired approval window, `ClassifyVerdict()` downgrades FAIL → WARN and includes the reason. Forces the reviewer to consciously sign off on the deviation. Add as `TASK-205` if time allows; mark as nice-to-have.

### Build order
1. Land Phase 1.
2. Bootstrap baseline: run `--suite --update-baseline` on the cleanest scenario set. Commit `reports/baselines/balance_suite_baseline.json`.
3. Wire `--baseline` comparison into Phase 1's `SuiteRunner.Run()`.
4. Update CI workflow to call `--suite` (no flags), depend on exit code.

### PoC-verified values
See Phase 1's drift thresholds table — same values apply here, used in `ComputeDeltas()` consumers.

### C# port checklist
- [ ] `src/Logic/Balance/NormalizedMetrics.cs` (new)
- [ ] `tools/Harness/SuiteRunner.cs` — extend with baseline-compare, baseline-save methods
- [ ] `tools/Harness/Program.cs` — add `--update-baseline` flag, baseline-comparison path
- [ ] `reports/baselines/balance_suite_baseline.json` (committed after bootstrap run)
- [ ] `tests/Balance/BaselineComparisonTests.cs` (new)

### Test coverage
- Round-trip: save baseline → read baseline → deltas all zero.
- Delta computation: synthetic current vs baseline, hand-verified deltas.
- FAIL classification: 0.21 death_rate drift → FAIL.
- WARN classification: 0.11 death_rate drift → WARN.
- Update mode: `--update-baseline` overwrites file, exits 0 even if PoC verdict was FAIL.
- No-baseline mode: missing file → status NO_BASELINE, exit 0.
- Field stability: baseline JSON with extra unrecognized field (forward compat) still deserializes.

### Open questions / risks
- **First baseline is sensitive to Phase-0 reseed.** Don't bootstrap the baseline until after Phase 0 has shipped and the provisional band targets in `PressureModel.cs` have been recalibrated. Otherwise the first comparison run will FAIL spuriously because Phase 0 shifted every seed.
- **Approved-drift YAML format.** Skip the spec until someone needs it; the PoC works fine without it. If we add it, lock the schema before the second baseline.

---

## Phase 3 — Full ETP System

### What it does
Replaces the stub `EtpCalculator` (`src/Logic/Balance/EtpCalculator.cs`, 21 lines) with a full YAML-driven ETP system: band config, behavior modifiers, monster-ETP calculation, room/floor budget queries, budget validation. Mirrors `~/development/rlike/balance/etp.py` (847 lines) but trims dead code (the lazy-load globals, the duplicate `_get_default_config()` fallback — C# loads at startup, no lazy state).

### PoC reference
- `~/development/rlike/config/etp_config.yaml` — full band config, behavior modifiers, spike settings, tolerances.
- `~/development/rlike/balance/etp.py:31-104` — `BandConfig` + `ETPConfig` dataclasses + YAML loader.
- `~/development/rlike/balance/etp.py:177-234` — band-for-depth lookup, behavior modifier lookup.
- `~/development/rlike/balance/etp.py:237-272` — `calculate_monster_dps`, `calculate_durability`.
- `~/development/rlike/balance/etp.py:280-310` — speed ETP multiplier tiers.
- `~/development/rlike/balance/etp.py:439-553` — `get_monster_etp()` — the canonical ETP formula. Read this carefully; it has elite multiplier + speed multiplier + band multiplier interactions.
- `~/development/rlike/balance/etp.py:617-673` — `check_room_budget()` — tolerance and warning logic.

### C# design

New files (replacing the existing `EtpCalculator.cs`):

```
src/Logic/Balance/Etp/
├── EtpConfig.cs              — YAML-mapped record (port of ETPConfig)
├── BandConfig.cs             — YAML-mapped record (port of BandConfig)
├── EtpCalculator.cs          — replaces existing; pure functions over EtpConfig
├── BehaviorModifier.cs       — enum + lookup table
├── EtpBudgetChecker.cs       — check_room_budget / check_floor_budget
└── EtpConfigLoader.cs        — YAML deserialization
```

API surface (port verbatim from PoC):

```csharp
public static class EtpCalculator
{
    // Returns "B1".."B5" for a depth.
    public static string BandForDepth(EtpConfig cfg, int depth);
    public static BandConfig BandConfigForDepth(EtpConfig cfg, int depth);

    // The canonical formula:
    //   ETP = (DPS × 6) × Durability × Behavior × Synergy × Elite × Speed
    public static double GetMonsterEtp(
        EtpConfig cfg,
        MonsterDefinition monster,
        int depth,
        double synergyBonus = 0.0,
        bool isElite = false);

    public static (double Min, double Max) GetRoomEtpBudget(
        EtpConfig cfg, int depth, bool allowSpike = false);

    public static (double Min, double Max) GetFloorEtpBudget(
        EtpConfig cfg, int depth);

    public static double DurabilityFactor(int hp, double baselinePlayerDamage = 6.5);
    public static double GetSpeedMultiplier(double speedRatio);
}

public static class EtpBudgetChecker
{
    public record RoomCheckResult(
        bool IsValid,
        string Status,           // "OK" | "UNDER" | "OVER"
        double TotalEtp,
        double BudgetMin,
        double BudgetMax,
        double DeviationPct,
        string Message);

    public static RoomCheckResult CheckRoom(
        EtpConfig cfg,
        double totalEtp,
        int depth,
        string roomId,
        bool allowSpike = false);
}
```

### PoC-verified values

**Band table** (port verbatim from `etp_config.yaml`):

| Band | Floor range | HP mult | Dmg mult | Room ETP min | Room ETP max | Floor ETP min | Floor ETP max | TTK | TTD | Perk unlock |
|------|-------------|---------|----------|--------------|--------------|---------------|---------------|-----|-----|-------------|
| B1 | 1-5 | 1.00 | 1.00 | 0 | 50 | 100 | 250 | 3 | 5 | false |
| B2 | 6-10 | 1.10 | 1.05 | 20 | 100 | 150 | 400 | 4 | 4 | false |
| B3 | 11-15 | 1.20 | 1.10 | 30 | 150 | 250 | 600 | 5 | 4 | true |
| B4 | 16-20 | 1.35 | 1.15 | 40 | 200 | 350 | 800 | 5 | 3 | false |
| B5 | 21-25 | 1.50 | 1.20 | 50 | 300 | 500 | 1200 | 6 | 3 | true |

**Behavior modifiers** (`etp_config.yaml:147-173`):

| Role | Modifier |
|------|----------|
| passive | 0.80 |
| basic_melee | 0.90 |
| basic_ranged | 1.00 |
| gap_closer | 1.05 |
| control | 1.10 |
| kiter | 1.10 |
| area_denial | 1.15 |
| summoner | 1.20 |
| boss | 1.30 |

**AI mapping** (`etp.py:225-231`):

```
"basic"          → "basic_melee"
"basic_monster"  → "basic_melee"
"slime"          → "control"
"boss"           → "boss"
"stationary"     → "passive"
(unknown)        → 1.0 (no modifier)
```

**Spike & tolerance** (`etp_config.yaml:180-208`):
- spike_multiplier: 1.5
- room_tolerance: 0.10 (±10%)
- floor_tolerance: 0.10
- warning_threshold: 0.15 (warn when deviation > 15%)
- error_threshold: 0.25 (error when deviation > 25%)

**Elite multiplier** (`etp.py:276`): `ELITE_ETP_MULTIPLIER = 1.5`

**Speed tiers** (`etp.py:280-285`):

```
speed_ratio ≥ 2.0  → 2.0×
speed_ratio ≥ 1.5  → 1.5×
speed_ratio ≥ 1.1  → 1.25×
speed_ratio < 1.1  → 1.0×
```

**Durability baseline** (`etp.py:267`): `baseline_player_damage = 6.5` (1d8 + 2 STR ≈ 4.5 + 2 = 6.5 avg).

**ETP formula expansion** (`etp.py:512-553`):

```
If monster has etp_base in YAML:
    band_multiplier = (hp_mult + dmg_mult) / 2
    etp = etp_base × band_multiplier × synergy × elite × speed
Else (derive from stats):
    scaled_hp     = base_hp × hp_mult
    scaled_dmg    = base_dmg × dmg_mult
    scaled_power  = base_power × dmg_mult
    dps           = (dmg_min + dmg_max)/2 + power
    durability    = scaled_hp / (6.5 × 3)    # normalized so 3 hits = 1.0
    behavior      = modifier_lookup(ai_type)
    etp = dps × 6 × durability × behavior × synergy × elite × speed
```

C# entities.yaml has 24 monsters with explicit `etp_base` already. The fallback derivation path is rare but must exist for the "fallback if YAML missing" branch.

### Build order
1. Create `config/etp_config.yaml` — copy from PoC verbatim.
2. Build `EtpConfigLoader` + records.
3. Replace `EtpCalculator.cs` (rename old to `.deprecated.cs` first, then delete after all callers migrated — the only existing caller is `EntityPlacerTests.cs`, a test).
4. Land `EtpBudgetChecker`.
5. Test coverage matching PoC's `test_etp_system.py` (band lookup, monster ETP, budgets, spike allowance).

### C# port checklist
- [ ] `config/etp_config.yaml` (new — verbatim copy from PoC, plus comment "Ported from ~/development/rlike/config/etp_config.yaml")
- [ ] `src/Logic/Balance/Etp/EtpConfig.cs`
- [ ] `src/Logic/Balance/Etp/BandConfig.cs`
- [ ] `src/Logic/Balance/Etp/EtpConfigLoader.cs`
- [ ] `src/Logic/Balance/Etp/EtpCalculator.cs` (replaces existing)
- [ ] `src/Logic/Balance/Etp/EtpBudgetChecker.cs`
- [ ] `src/Logic/Balance/EtpCalculator.cs` — DELETE (replaced by Etp/EtpCalculator.cs)
- [ ] `tests/Core/EntityPlacerTests.cs:87-119` — update existing tests (or move to `tests/Balance/EtpCalculatorTests.cs`)
- [ ] `tests/Balance/EtpCalculatorTests.cs` (new — full port of `test_etp_system.py`)
- [ ] `tests/Balance/EtpBudgetCheckerTests.cs` (new)
- [ ] `tests/Balance/EtpConfigLoaderTests.cs` (new — verifies YAML round-trip)

### Test coverage
Port verbatim from `~/development/rlike/tests/test_etp_system.py`:

- `BandForDepth_B1`: depths 1, 3, 5 → "B1"
- `BandForDepth_B2`: depths 6, 8, 10 → "B2"
- ... through B5
- `BandForDepth_Beyond25`: depths 26, 30 → "B5"
- `BandConfig_HasRequiredFields`: all 5 bands have hp_mult > 0, dmg_mult > 0, room_etp_min/max sane
- `DpsCalc_NoPower`: dps(4,6,0) = 5.0
- `DpsCalc_WithPower`: dps(4,6,2) = 7.0
- `Durability_HpScaling`: hp=20 → ~1.0, hp=40 → ~2.0
- `BehaviorModifier_BasicMelee`: 0.90
- `BehaviorModifier_Boss`: 1.30
- `BehaviorModifier_Unknown`: 1.0
- `MonsterEtp_OrcAtDepth1`: 20 < etp < 40 (around 27)
- `MonsterEtp_ScalesWithDepth`: orc B1 < orc B3 < orc B5
- `MonsterEtp_TrollHigherThanOrc`: troll_etp > orc_etp (etp_base 50 vs 27 — but C# entities.yaml has only `goblin_troll: 45`; adjust test to use this)
- `RoomBudget_IncreasesWithBand`
- `FloorBudget_IncreasesWithBand`
- `Spike_AllowsHigherMax`: spike_max == normal_max × 1.5
- `CheckRoom_Under`: totalEtp below min → "UNDER"
- `CheckRoom_Over`: totalEtp above max → "OVER"
- `CheckRoom_WithinTolerance`: deviation < 10% → IsValid=true
- `Elite_MultiplierApplied`: elite ETP == non-elite × 1.5
- `Speed_TierLookup`: speed_ratio 2.0 → 2.0×, 1.5 → 1.5×, 1.1 → 1.25×, 1.0 → 1.0×

### Open questions / risks
- **C# entity coverage gap.** PoC `etp_config.yaml` references monsters (`dragon_lord`, `zhyraxion_*`) that don't exist in C# yet. The config should be ported as-is; loaders must tolerate missing monster references at calc time (return default ETP 20.0, log warning — match PoC `etp.py:476-479`).
- **Behavior modifier source-of-truth.** PoC stores AI-type → role mapping in code (`etp.py:225-231`). For C#, prefer storing it in YAML as `behavior_aliases:` so designers can adjust without recompile. Add to `etp_config.yaml` as a new section (extending the PoC schema is fine — it's our YAML now).
- **Banding mismatch with `DepthScaling.cs`.** Existing `DepthScaling.cs:46` uses 2-floor bands (`(depth-1)/2`), giving 5 bands for depths 1-9+. PoC uses 5-floor bands (B1=1-5, B2=6-10, ...). These are different concepts: `DepthScaling` bands the stat multipliers, `EtpConfig` bands the encounter budgets. Document this in both files to prevent confusion. Do NOT unify — they serve different purposes.

---

## Phase 4 — Depth Pressure Reporting

### What it does
Adds `--depth-report` mode that consumes `summary.json` (or a directory of `metrics/raw/*.json`) and emits the PoC's full report stack: observed depth curve, target comparison, scaling diagnosis, damage-multiplier recommendations. Markdown output. Replicates `analysis/depth_pressure_model.py:print_pressure_report()`.

### PoC reference
- `~/development/rlike/analysis/depth_pressure_model.py:571-600` — `format_pressure_table()` — the main observed-curve table.
- `~/development/rlike/analysis/depth_pressure_model.py:603-680` — `format_target_comparison()` — observed vs target, with diagnosis section.
- `~/development/rlike/analysis/depth_pressure_model.py:683-714` — `format_multiplier_recommendations()` — derived damage-mult table.
- `~/development/rlike/analysis/depth_pressure_model.py:717-807` — `format_scaling_diagnosis()` — trend analysis (HP-heavy / balanced / spike / flat).
- `~/development/rlike/balance/target_bands.py:124-253` — `evaluate_depth()` + `diagnose()` (per-depth diagnostic text).
- `~/development/rlike/analysis/depth_pressure_curve.py` — markdown + PNG sparkline output (PNG optional — skip unless matplotlib equivalent surfaces).
- `~/development/rlike/analysis/depth_pressure_model.py:458-564` — `derive_required_damage_multiplier()` — the math for "what should the multiplier be to hit target H_MP?"

### C# design

```csharp
public static class DepthPressureReport
{
    public sealed record DepthCurvePoint(
        int Depth,
        string ScenarioId,
        double H_PM,
        double H_MP,
        double DPR_P,
        double DPR_M,
        double PlayerHitRate,
        double MonsterHitRate,
        double DmgPerEncounter,
        double TurnsPerKill,
        double DeathRate);

    public sealed record MultiplierRecommendation(
        int Depth,
        double ObservedHmp,
        double TargetMidpoint,
        double ObservedMonsterDpr,
        double RequiredMonsterDpr,
        double RecommendedDamageMultiplier,
        bool AdjustmentNeeded);

    public static string FormatPressureTable(IEnumerable<DepthCurvePoint> curve);
    public static string FormatTargetComparison(IEnumerable<DepthCurvePoint> curve);
    public static string FormatMultiplierRecommendations(IEnumerable<DepthCurvePoint> curve);
    public static string FormatScalingDiagnosis(IEnumerable<DepthCurvePoint> curve);
    public static string FormatFullReport(IEnumerable<DepthCurvePoint> curve);
}
```

`PressureModel.cs` already has `Evaluate()`, `EvaluateProvisional()`, `Diagnose()` — Phase 4 wraps them with the formatters above. No new math, just presentation.

CLI:
- `harness --depth-report --in <dir>` — reads `<dir>/metrics/raw/*.json` (the output of Phase 1).
- `harness --depth-report --in <suite-summary.json>` — also accepts the summary file.
- `harness --depth-report --out <file.md>` — write markdown. Default: stdout.

### PoC-verified values

**Target-band feel labels** (`target_bands.py:78-121`):

| Depth | Feel |
|-------|------|
| 1 | safe learning |
| 2 | warm-up |
| 3 | pressure begins |
| 4 | serious |
| 5 | dangerous |
| 6 | brutal but survivable |

These already exist as comments in `PressureModel.cs`. Expose them as data on a new `TargetBandMetadata` lookup so the report can print them in the comparison table.

**Damage multiplier derivation** (`depth_pressure_model.py:458-564`):

```
For each depth in curve:
    target_midpoint = (h_mp_min + h_mp_max) / 2.0
    If observed_h_mp already in [min, max]: multiplier = 1.0, adjustment_needed = false
    Else:
        required_dpr_m = player_hp / target_midpoint
        observed_avg_dmg = monster_dpr / monster_hit_rate
        required_avg_dmg = required_dpr_m / monster_hit_rate
        multiplier = required_avg_dmg / observed_avg_dmg  (if observed > 0)
```

**Scaling diagnosis categories** (`depth_pressure_model.py:717-807`):

| Δ H_PM (first→last depth) | Δ H_MP | Verdict |
|---|---|---|
| > +0.5 | between -1.0 and +1.0 | HP-HEAVY SCALING (attrition risk) |
| > +0.5 | < -1.0 | BALANCED SCALING (tougher AND deadlier) |
| < +0.3 | < -1.5 | SPIKE LETHALITY (unavoidable spike deaths) |
| ≈0 | ≈0 | FLAT SCALING (too timid) |
| other | other | MIXED SIGNALS |

**Attrition indicator** (`depth_pressure_model.py:797-803`): `ratio = H_PM / H_MP`. >0.6 = ATTRITION, <0.3 = LETHAL, between = BALANCED.

### Build order
1. Land Phase 1 (Phase 4 reads its `summary.json`).
2. Build the formatters one at a time:
   - `FormatPressureTable` → ports `format_pressure_table`. Verify against PoC output snapshot.
   - `FormatTargetComparison` → wraps existing `PressureModel.Evaluate()`.
   - `FormatMultiplierRecommendations` → port `derive_required_damage_multiplier`.
   - `FormatScalingDiagnosis` → port `format_scaling_diagnosis`.
3. Wire to `Program.cs` as `--depth-report`.

### C# port checklist
- [ ] `src/Logic/Balance/DepthPressureReport.cs` (new)
- [ ] `src/Logic/Balance/TargetBandMetadata.cs` — adds `Feel` strings (extracts from PressureModel comments)
- [ ] `src/Logic/Balance/PressureModel.cs` — add `DeriveRequiredDamageMultiplier()` static method (port of PoC function)
- [ ] `tools/Harness/Program.cs` — add `--depth-report`, `--in`, `--out`
- [ ] `tools/Harness/DepthReportLoader.cs` (new) — reads JSON files into `DepthCurvePoint[]`
- [ ] `tests/Balance/DepthPressureReportTests.cs` (new)

### Test coverage
- Snapshot test: feed known `AggregatedMetrics` JSON, assert markdown matches a golden file. Verifies column alignment, decimal precision, header rows.
- `DeriveRequiredDamageMultiplier`:
  - When observed in range → multiplier = 1.0, adjustment_needed=false
  - When observed H_MP = 30, target midpoint = 20 → required mult = ~1.5 (monsters need to hit 50% harder)
- `FormatScalingDiagnosis`: synthetic curve with H_PM Δ=+0.7, H_MP Δ=-2.0 → "BALANCED SCALING"
- `FormatScalingDiagnosis`: H_PM Δ=+0.6, H_MP Δ=+0.1 → "HP-HEAVY SCALING"
- Attrition indicator: H_PM=8, H_MP=12 → ratio 0.67 → "ATTRITION"

### Open questions / risks
- **PNG generation.** PoC's `depth_pressure_curve.py` writes PNGs with matplotlib. C# has no equivalent in the logic layer (no ImageSharp dependency, no Godot in harness). Skip PNG for now. The markdown table is sufficient. If visualization becomes critical, generate via a separate post-process Python script that reads the JSON output — keep the harness Godot-free.
- **HP budget derivation.** PoC hardcodes `monster_hp_budget_per_run` per scenario in `KNOWN_SCENARIO_CONFIGS` (`depth_pressure_model.py:860-945`). C# derives from `RunMetrics.MonsterAvgMaxHp × spawn count` automatically — already correct, no porting needed for the constants.

---

## Phase 5 — ETP Sanity Tool

### What it does
Adds `--etp-sanity` mode that generates representative dungeon floors (one per band), computes per-room ETP, validates against budget ranges. Outputs CSV + summary. Strict mode (`--strict`) fails if any normal room exceeds budget by more than tolerance. The CI gate for "did the new worldgen blow the budget?".

### PoC reference
- `~/development/rlike/etp_sanity.py:354-494` — `run_sanity_check()` — the orchestrator.
- `~/development/rlike/etp_sanity.py:107-185` — `analyze_room_etp()` — per-room ETP scoring with status classification.
- `~/development/rlike/etp_sanity.py:51-59` — status constants (OK / UNDER / OVER / EMPTY / BOSS / MINIBOSS / ENDBOSS / SPIKE / EXEMPT).
- `~/development/rlike/etp_sanity.py:233-333` — `analyze_level_etp()` — full level traversal.

### C# design

```csharp
public static class EtpSanityHarness
{
    public sealed record RoomEtpResult(
        int RoomIndex,
        int RoomX, int RoomY,
        double TotalEtp,
        IReadOnlyDictionary<string, int> MonsterCounts,
        IReadOnlyDictionary<string, double> EtpBreakdown,
        double BudgetMin, double BudgetMax,
        string Status,          // OK | UNDER | OVER | EMPTY | BOSS | MINIBOSS | ...
        string Role);

    public sealed record LevelEtpResult(
        int Depth,
        string Band,
        IReadOnlyList<RoomEtpResult> Rooms,
        double TotalFloorEtp,
        double FloorBudgetMin,
        double FloorBudgetMax,
        bool WithinFloorBudget);

    public static LevelEtpResult AnalyzeLevel(
        DungeonFloorBuilder builder,
        EtpConfig cfg,
        int depth,
        int seed);

    public static int RunSanity(
        DungeonFloorBuilder builder,
        EtpConfig cfg,
        int[] depths,           // default: [3, 8, 13, 18, 23] (one per band)
        bool strict,
        bool verbose,
        int runsPerDepth = 1,
        TextWriter? csvOut = null);
}
```

CLI:
- `harness --etp-sanity` — runs default depths [3, 8, 13, 18, 23], prints CSV to stdout.
- `harness --etp-sanity --strict` — fails (exit 1) on any OVER violation in normal rooms.
- `harness --etp-sanity --depth 6` — single depth.
- `harness --etp-sanity --runs 5` — multiple runs per depth for stability.
- `harness --etp-sanity --verbose` — per-monster ETP breakdown.

### PoC-verified values

**Status taxonomy** (`etp_sanity.py:51-63`):

```
OK         - Within [budget_min, budget_max]
UNDER      - total < budget_min (normal rooms only)
OVER       - total > budget_max (normal rooms only)
EMPTY      - No monsters (always valid)
BOSS       - Boss room (budget-exempt)
MINIBOSS   - Miniboss room (budget-exempt)
ENDBOSS    - End-boss room (budget-exempt)
SPIKE      - Vault/treasure room with allow_spike=true (1.5× budget OK)
EXEMPT     - Explicitly exempt via metadata
```

Non-violation set: `{OK, EMPTY, BOSS, MINIBOSS, ENDBOSS, SPIKE, EXEMPT}`.
Violation set: `{UNDER, OVER}`.
Strict-mode failure set: `{OVER}` only (UNDER is allowed — empty/sparse rooms are not a regression).

**CSV header** (`etp_sanity.py:345-351`):
```
depth,band,room_index,etp_total,budget_min,budget_max,status,role,monsters
```

`monsters` column format: `"orc_grunt:2,goblin:1"`.

**Representative depths** (`etp_sanity.py:376-378`): `[3, 8, 13, 18, 23]` — one per band.

### Build order
1. Phase 3 must be done (this consumes `EtpConfig`).
2. Build `AnalyzeLevel` against existing `DungeonFloorBuilder` — Phase 5 depends on the dungeon worldgen already in `DungeonRunHarness`.
3. Build orchestrator + CSV writer.
4. Wire to `Program.cs`.

### C# port checklist
- [ ] `src/Logic/Balance/Etp/EtpSanityHarness.cs` (new)
- [ ] `src/Logic/Balance/Etp/RoomEtpStatus.cs` — enum or string constants
- [ ] `tools/Harness/Program.cs` — add `--etp-sanity`, `--strict`, `--depth`, `--runs`, `--verbose`
- [ ] `tests/Balance/EtpSanityHarnessTests.cs` (new)
- [ ] `tools/ci-etp-sanity-check.sh` (optional — mirror of `tools/ci-soak-check.sh`)

### Test coverage
- `AnalyzeLevel_EmptyDungeon`: builder produces dungeon with no monsters → all rooms EMPTY, IsValid=true
- `AnalyzeLevel_NormalDistribution`: depth 3 dungeon → most rooms OK, average within band
- `Strict_PassesOnNoOverViolations`
- `Strict_FailsOnSingleOverViolation`
- `Strict_PassesOnUnderViolations`: UNDER doesn't fail strict (matches PoC)
- `CsvRoundtrip`: write CSV, parse back, fields match
- `BossRoomExempt`: room with role=boss never reports OVER, even with high ETP
- `SpikeRoomTolerance`: room with allow_spike=true tolerates up to 1.5× budget_max

### Open questions / risks
- **Room metadata source.** PoC reads `RoomMetadata.role` and `RoomMetadata.allow_spike` from level templates. C# `LevelTemplate` has `RoomMetadata` but it's lighter — needs audit. If templates don't yet carry role/spike data, Phase 5 falls back to treating every room as "normal" and the BOSS/SPIKE distinctions become trivially absent. That's still useful (catches OVER violations in non-boss rooms) but loses the empty-rooms-are-OK and boss-rooms-are-exempt subtlety. Track as `TASK-505` — audit LevelTemplate schema, add `role` and `allow_spike` fields if missing.
- **Deterministic worldgen.** `DungeonFloorBuilder` already accepts a seed. Verify two `--etp-sanity --depth 3` runs at the same seed produce byte-identical CSV. If not, isolate the non-determinism before merging.

---

## Risks & Decisions Needed

### Decisions
1. **Approved-drift schema (Phase 2.5).** Build now or defer? Recommend defer — let Phase 1+2 ship without it, add only when the first "false positive FAIL we want to ignore" appears.
2. **PNG visualization.** Defer indefinitely. The PoC PNGs were nice-to-have; markdown sparklines are sufficient. Revisit only if dashboard work surfaces.
3. **Behavior alias source (Phase 3).** Hardcoded `Dictionary<string, string>` in `EtpCalculator` vs. new YAML field. Recommend YAML — it's content. Adds 6 lines to `etp_config.yaml`.
4. **Probe vs calibration semantics.** PoC excludes probes from acceptance-pass count but includes them in the report. C# already does this (`ScenarioDefinition.IsProbe`, `Program.cs:672`). Mirror it in `SuiteRunner`.

### Risks
1. **Baseline drift on Phase 0 reseed.** The first post-Phase-0 baseline will look different from any pre-Phase-0 measurements. Phase 2 must bootstrap after Phase 0 lands. Don't commit a baseline before then.
2. **Scenario authoring effort.** 12 new weapon-variant YAML files. Each is ~30 lines. Mechanical work but easy to introduce typos. Recommend a single PR creating all 12 and verifying against `harness --all` before Phase 1 builds against them.
3. **ETP YAML compatibility.** C# `entities.yaml` field name is currently `etp_base` (matches PoC). Verify all 24 monsters' values are sane after Phase 3 lands — a stale value won't fail any test, it'll just produce subtly wrong budgets.
4. **Determinism leakage.** Any system that captures `DateTime.Now`, `Guid.NewGuid()`, or unseeded `Random` in a code path the harness can hit will break Phase 2. The harness should not depend on wall-clock. Audit `ScenarioHarness.RunOnce()` and called code for these. Existing C# harness is already deterministic in practice (1337 seed produces same results); just don't add new sources.

---

## Tasks

Tasks are grouped by phase. Each is sized for a single builder session.

### Phase 0 — Seeding

- [x] TASK-001: Implement `SeedDerivation.Stable(scenarioId, runIdx, seedBase)` + tests.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: none
  - Acceptance criteria:
    - SHA-256 + first-4-bytes big-endian matches PoC `stable_scenario_seed` for `("depth3_orc_brutal", 0, 1337)` reference value (capture from PoC, paste into test as expected int)
    - 50 different runIdx values → 50 unique seeds
    - `depth2_orc_baseline` and `depth2_orc_baseline_fine` produce disjoint seed sets

- [x] TASK-002: Wire `SeedDerivation.Stable` into `ScenarioHarness.Run()`.
  - Status: complete
  - Layer: logic
  - Type: refactor
  - Dependencies: TASK-001
  - Acceptance criteria:
    - `ScenarioHarness.cs:46` uses `SeedDerivation.Stable(scenario.ScenarioId, i, baseSeed)`
    - All existing `tests/Balance/*` tests still pass (numbers will shift but pass/fail status remains)
    - Run `harness --scenario depth1_tuned --runs 10` twice; outputs byte-identical

- [x] TASK-003: Recalibrate provisional bands in `PressureModel.cs` post-reseed.
  - Status: complete
  - Layer: logic
  - Type: balance
  - Dependencies: TASK-002
  - Acceptance criteria:
    - Run `harness --all --json > reports/post_reseed_baseline.json`
    - Update comments in `PressureModel.cs:132-157` with new observed values for the 6 calibrated scenarios
    - Verify `dotnet test --filter "Category!=Slow"` passes

### Phase 1 — Acceptance Matrix

- [x] TASK-101: Author 4 missing depth-2 weapon-variant scenarios.
  - Status: complete
  - Layer: scenario
  - Type: scenario
  - Dependencies: none
  - Acceptance criteria:
    - `scenario_depth2_orc_baseline_keen.yaml`, `_vicious`, `_fine`, `_masterwork` created
    - Each differs from `scenario_depth2_orc_baseline.yaml` only in `player.weapon`
    - `harness --scenario depth2_orc_baseline_keen` runs successfully

- [x] TASK-102: Author 4 missing depth-3 weapon-variant scenarios.
  - Status: complete
  - Layer: scenario
  - Type: scenario
  - Dependencies: none
  - Acceptance criteria:
    - `scenario_depth3_orc_brutal_keen.yaml`, `_vicious`, `_fine`, `_masterwork` created
    - `harness --scenario depth3_orc_brutal_fine` runs and reports H_PM/H_MP

- [x] TASK-103: Author 4 missing depth-5 weapon-variant scenarios.
  - Status: complete
  - Layer: scenario
  - Type: scenario
  - Dependencies: none
  - Acceptance criteria:
    - `scenario_depth5_zombie_keen.yaml`, `_vicious`, `_fine`, `_masterwork` created

- [x] TASK-104: Implement `NormalizedMetrics` record and `SuiteRunner.Normalize()`.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001
  - Acceptance criteria:
    - `NormalizedMetrics(scenario_id, runs, deaths, death_rate, player_hit_rate, monster_hit_rate, pressure_index, bonus_attacks_per_run)` matches PoC schema exactly
    - `SuiteRunner.Normalize(AggregatedMetrics)` returns the same shape PoC's `normalize_metrics()` produces

- [x] TASK-105: Implement `SuiteRunner.Run()` matrix execution (no baseline compare).
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-101, TASK-102, TASK-103, TASK-104
  - Acceptance criteria:
    - `Matrix` constant lists exactly 15 entries matching PoC
    - `--fast` mode lists 6 entries (depths 1-6, one each)
    - Writes `metrics/raw/<scenario>.json`, `summary.json`, `balance_report.md`, `verdict.json`
    - Two runs at same `--seed` produce byte-identical `summary.json`

- [x] TASK-106: Implement verdict markdown report formatter.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-105
  - Acceptance criteria:
    - Markdown matches PoC `generate_markdown_report` output structure
    - Per-scenario section with Runs, Deaths, Death Rate, Hit Rates, Pressure Index, Bonus Attacks
    - Verdict Summary section with PASS/WARN/FAIL counts

- [x] TASK-107: Wire `--suite` CLI flag into `Program.cs`.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-106
  - Acceptance criteria:
    - `harness --suite` runs full matrix, exits 0 (NO_BASELINE mode)
    - `harness --suite --fast` runs 6-scenario subset
    - `harness --suite --out-dir <path>` writes to custom dir
    - `--help` documents new flags

- [x] TASK-108: End-to-end harness verification.
  - Status: complete
  - Layer: logic
  - Type: test
  - Dependencies: TASK-107
  - Acceptance criteria:
    - Run `harness --suite --fast` from clean checkout
    - All 6 scenarios complete without errors
    - `verdict.json` parses as valid JSON
    - Total runtime under 3 minutes on dev hardware

### Phase 2 — Baseline & Regression

- [x] TASK-201: Implement `SuiteRunner.ComputeDeltas` and `ClassifyVerdict`.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-104
  - Acceptance criteria:
    - Drift thresholds match PoC table verbatim
    - Synthetic test: death_rate Δ=0.21 → FAIL; 0.11 → WARN; 0.04 → PASS
    - Cross-metric: if death_rate WARN and bonus_attacks FAIL → overall FAIL

- [x] TASK-202: Implement baseline read/write + `--update-baseline` flag.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-105, TASK-201
  - Acceptance criteria:
    - `--update-baseline` writes `reports/baselines/balance_suite_baseline.json`, exits 0 always
    - `--baseline <path>` reads from custom path
    - JSON shape matches PoC verbatim (`{ scenario_id: NormalizedMetrics, ... }`)

- [x] TASK-203: Wire baseline comparison into `SuiteRunner.Run()`.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-202
  - Acceptance criteria:
    - When baseline exists: verdict.json includes `details[scenario].verdict` and `details[scenario].deltas`
    - When baseline absent: verdict.json has `status: NO_BASELINE`, `acceptance_status: PASS`
    - Exit code 1 if any FAIL verdict; 0 otherwise

- [x] TASK-204: Bootstrap initial baseline.
  - Status: complete
  - Layer: balance
  - Type: balance
  - Dependencies: TASK-203, TASK-003
  - Acceptance criteria:
    - Run `harness --suite --update-baseline` on clean main branch
    - Commit `reports/baselines/balance_suite_baseline.json`
    - Verify subsequent `harness --suite` reports all PASS or PROBE (no FAIL)

- [x] TASK-205: CI workflow integration.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-204
  - Acceptance criteria:
    - `.github/workflows/balance.yml` runs `harness --suite` on PRs
    - PR fails when any scenario FAILs against baseline
    - Workflow uploads `verdict.json` and `balance_report.md` as artifacts

### Phase 3 — Full ETP

- [x] TASK-301: Port `etp_config.yaml` to C# config.
  - Status: complete
  - Layer: logic
  - Type: balance
  - Dependencies: none
  - Acceptance criteria:
    - `config/etp_config.yaml` exists; matches PoC byte-for-byte structurally
    - Comment block at top points to PoC source

- [x] TASK-302: Implement `EtpConfigLoader` + `EtpConfig`/`BandConfig` records.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-301
  - Acceptance criteria:
    - YAML round-trip: load + serialize matches input
    - All 5 bands deserialize with correct multipliers
    - All 9 behavior modifiers deserialize

- [x] TASK-303: Implement `EtpCalculator` (replacing stub).
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-302
  - Acceptance criteria:
    - Ports verbatim: `BandForDepth`, `BandConfigForDepth`, `GetMonsterEtp`, `GetRoomEtpBudget`, `GetFloorEtpBudget`, `DurabilityFactor`, `GetSpeedMultiplier`
    - Old `EtpCalculator.cs` deleted; existing test in `EntityPlacerTests.cs` migrated
    - Orc at depth 1 returns 20 < etp < 40
    - Speed tier lookup matches PoC table

- [x] TASK-304: Implement `EtpBudgetChecker.CheckRoom`.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-303
  - Acceptance criteria:
    - Returns OK status when within tolerance
    - Returns UNDER when below min × (1 - tolerance)
    - Returns OVER when above max × (1 + tolerance)
    - Spike allowance: max × 1.5 when `allowSpike=true`

- [x] TASK-305: Port ETP test suite from PoC.
  - Status: complete
  - Layer: logic
  - Type: test
  - Dependencies: TASK-304
  - Acceptance criteria:
    - `tests/Balance/EtpCalculatorTests.cs` covers all 21 cases enumerated in plan
    - All tests pass
    - `dotnet test --filter "Category!=Slow"` runtime unchanged (no new slow tests)

### Phase 4 — Depth Pressure Report

- [x] TASK-401: Implement `DepthCurvePoint` + `DepthReportLoader`.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-105
  - Acceptance criteria:
    - Loads `metrics/raw/*.json` directory or single `summary.json`
    - Returns `IReadOnlyList<DepthCurvePoint>` sorted by depth

- [x] TASK-402: Implement `FormatPressureTable` and `FormatTargetComparison`.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-401
  - Acceptance criteria:
    - Output matches PoC `format_pressure_table` column layout
    - Target comparison table includes Death%, H_PM, H_MP with target ranges and status
    - Diagnosis section includes per-depth findings from `PressureModel.Diagnose()`

- [x] TASK-403: Implement `DeriveRequiredDamageMultiplier` + formatter.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-402
  - Acceptance criteria:
    - Math matches PoC `derive_required_damage_multiplier`
    - Observed H_MP=30, target midpoint=20 → multiplier ≈ 1.5
    - When in range → multiplier=1.0, adjustment_needed=false

- [x] TASK-404: Implement `FormatScalingDiagnosis` (trend analysis).
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-401
  - Acceptance criteria:
    - HP-HEAVY / BALANCED / SPIKE LETHALITY / FLAT / MIXED categorization matches PoC table
    - Attrition indicator per depth (ATTRITION/LETHAL/BALANCED) computed correctly
    - Synthetic test: each category triggered by hand-crafted curve

- [x] TASK-405: Wire `--depth-report` CLI flag.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-404
  - Acceptance criteria:
    - `harness --depth-report --in <dir>` reads Phase 1 output, emits markdown
    - `--out <file>` writes to file; stdout otherwise

### Phase 5 — ETP Sanity Tool

- [x] TASK-501: Audit `LevelTemplate` for `role` and `allow_spike` fields.
  - Status: complete
  - Layer: logic
  - Type: analysis
  - Dependencies: none
  - Acceptance criteria:
    - Document which level templates carry role/spike metadata
    - If missing, add to `LevelTemplate` schema + at least one example template

- [x] TASK-502: Implement `AnalyzeLevel` against `DungeonFloorBuilder`.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-303, TASK-501
  - Acceptance criteria:
    - Returns `LevelEtpResult` with per-room status classification
    - Empty rooms → EMPTY status (always valid)
    - Boss rooms → BOSS status (always valid)
    - Two calls at same seed → identical result

- [x] TASK-503: Implement `RunSanity` orchestrator + CSV writer.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-502
  - Acceptance criteria:
    - Default depths `[3, 8, 13, 18, 23]` traversed
    - CSV header matches PoC format
    - `--strict` exits 1 only on OVER violations in normal rooms
    - Per-band summary printed after CSV

- [x] TASK-504: Wire `--etp-sanity` CLI flag.
  - Status: complete
  - Layer: logic
  - Type: system
  - Dependencies: TASK-503
  - Acceptance criteria:
    - `harness --etp-sanity` prints CSV to stdout
    - `--strict`, `--depth`, `--runs`, `--verbose` flags work
    - Exit codes correct (0 = pass strict, 1 = OVER detected in strict)

- [x] TASK-505: ETP sanity verification run.
  - Status: complete
  - Layer: logic
  - Type: test
  - Dependencies: TASK-504
  - Acceptance criteria:
    - Run `harness --etp-sanity --strict` on main
    - Document any OVER violations found
    - File follow-up tasks for each violation (or fix in this task if scope-appropriate)

---

## Closing Notes

This plan is sized at 5 phases over ~25 tasks. With Claude-driven implementation, expect each phase to land in 2-5 sessions depending on test coverage scope. Phases 1-2 unblock CI integration — get them done first; Phases 3-5 can interleave with content work.

The PoC is the source of truth for every value in this plan. When implementing, paste from PoC source rather than re-deriving — these numbers were calibrated over months of harness runs.

When a phase lands, mark its checkbox `[x]` at the top of this plan and update `tasks/plans/INDEX.md`. When all five phases are complete, mark `plan_balance_pipeline.md` as `[x]`.
