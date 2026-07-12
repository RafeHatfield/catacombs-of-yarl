# Balance Pipeline Playbook

_Last verified: 2026-07-12 against commit 86b6f10_

Operational guide for the YARL balance pipeline. Theory lives in `balance_system_overview.md`
and `combat_metrics_guide.md`. This document is the day-to-day workflow reference.

---

## The Three Commands You Actually Use

```bash
# 1. Quick check before committing (2 min)
dotnet run --project tools/Harness -- --suite --fast

# 2. Full acceptance gate (6 min — same as CI)
dotnet run --project tools/Harness -- --suite

# 3. Diagnose a specific depth ("why is depth 3 spiking?")
dotnet run --project tools/Harness -- --suite --out-dir reports/my_run
dotnet run --project tools/Harness -- --depth-report --in reports/my_run
```

Everything else is for specific situations. Start here.

---

## Interpreting `--suite` Output

```
  depth2_orc_baseline           PASS
  depth3_orc_brutal             WARN   ← death_rate +0.12 (threshold 0.10)
  depth5_zombie                 PASS
  ...
  Results: 12 PASS  2 WARN  1 FAIL  0 PROBE
```

**PASS** — all metrics within drift thresholds of baseline. Ship it.

**WARN** — at least one metric drifted past the warn threshold. Not a blocker but worth understanding. Run `--depth-report` to see which lever to pull.

**FAIL** — at least one metric crossed the fail threshold. CI will block the PR. Investigate before merging.

**PROBE** — scenario tagged `is_probe: true` (identity tests, not calibration scenarios). Not counted in PASS/WARN/FAIL.

### Drift Thresholds (from PoC `balance_suite.py`)

| Metric | WARN | FAIL |
|--------|------|------|
| `death_rate` | ±0.10 | ±0.20 |
| `player_hit_rate` | ±0.05 | ±0.10 |
| `monster_hit_rate` | ±0.05 | ±0.10 |
| `pressure_index` | ±5.0 | ±10.0 |
| `bonus_attacks_per_run` | ±2.0 | ±4.0 |

`pressure_index = avg_monster_attacks_per_run − avg_player_attacks_per_run`. Negative = player acts more (usually healthy). Positive = monsters apply heavy pressure.

---

## Diagnosing a WARN or FAIL

### Step 1 — Read the deltas

```bash
cat reports/my_run/verdict.json
```

The `details` section shows per-metric deltas for every scenario. Find the largest delta and which scenario it's on.

### Step 2 — Run the depth report

```bash
dotnet run --project tools/Harness -- --depth-report --in reports/my_run
```

This produces:
- **Pressure table** — observed H_PM / H_MP / DPR / death_rate per depth
- **Target comparison** — observed vs band targets with status flags
- **Multiplier recommendations** — "depth 4 H_MP = 30, target midpoint = 42 → reduce monster DPR by 29%"
- **Scaling diagnosis** — HP-HEAVY / BALANCED / SPIKE LETHALITY / FLAT / MIXED

### Step 3 — Map diagnosis to action

| Diagnosis | Meaning | Fix |
|-----------|---------|-----|
| HP-HEAVY SCALING | Monsters get tougher but not deadlier — attrition grind | Reduce monster HP or increase player DPR |
| BALANCED SCALING | Encounters get harder in both axes | No action needed |
| SPIKE LETHALITY | Some depths have sudden death spikes | Review encounter composition at spiking depth |
| FLAT SCALING | Difficulty barely changes across depths | Increase stat multipliers for mid/late bands |
| MIXED SIGNALS | Inconsistent across depths | Review individual scenarios at outlier depths |

**Attrition indicator per depth:**
- `H_PM / H_MP > 0.6` = ATTRITION (player grinds too long, enemies barely threaten)
- `H_PM / H_MP < 0.3` = LETHAL (enemies kill faster than player can)
- Between = BALANCED

### Step 4 — Pull the lever

| Problem | Lever | Where |
|---------|-------|-------|
| Death rate too high | Lower monster HP or damage | `config/entities.yaml` |
| Death rate too low | Raise monster damage or HP | `config/entities.yaml` |
| H_PM too high (player deals too little damage) | Lower monster HP or raise player accuracy | `config/entities.yaml`, scenario YAML |
| H_PM too low (player one-shots) | Raise monster HP | `config/entities.yaml` |
| H_MP too high (player survives too easily) | Raise monster damage | `config/entities.yaml` |
| H_MP too low (player dies too fast) | Lower monster damage or raise player HP | Scenario YAML |
| Pressure index too high (monster action advantage) | Reduce monster count or lower speed_bonus | Scenario YAML or `config/entities.yaml` |

After each change: re-run `--suite --fast` to confirm the metric moved in the right direction before running the full suite.

---

## Updating the Baseline

The baseline is the canonical "current good state." Update it when you intentionally change balance — not to paper over a regression.

```bash
# Verify the suite is actually clean first
dotnet run --project tools/Harness -- --suite

# If PASS (or WARN for intended drift), bless the new baseline
dotnet run --project tools/Harness -- --suite --update-baseline

# Commit it — this is a deliberate balance decision
git add reports/baselines/balance_suite_baseline.json
git commit -m "balance: update baseline after [reason]"
```

**Never run `--update-baseline` to silence a FAIL you don't understand.** Investigate first.

The baseline is committed at `reports/baselines/balance_suite_baseline.json`. It ships with the repo so CI always has something to compare against.

---

## ETP Sanity Check

Validates that dungeon room ETP is within band budgets. Run when you change:
- Monster HP/damage stats
- Spawn weights / encounter composition
- Level template room roles
- ETP config bands or budgets

```bash
# Normal check (reports violations, doesn't fail)
dotnet run --project tools/Harness -- --etp-sanity

# Strict mode (fails on any OVER in normal rooms — same as CI)
dotnet run --project tools/Harness -- --etp-sanity --strict

# Single depth
dotnet run --project tools/Harness -- --etp-sanity --depth 3

# Multiple samples per depth for stability
dotnet run --project tools/Harness -- --etp-sanity --depth 3 --runs 5

# Per-monster breakdown
dotnet run --project tools/Harness -- --etp-sanity --verbose
```

**Status codes:**

| Code | Meaning | Action |
|------|---------|--------|
| OK | Within budget | None |
| UNDER | Below minimum | Normal — sparse rooms are fine |
| OVER | Exceeds maximum | Investigate. Fails `--strict`. |
| EMPTY | No monsters | Fine |
| BOSS / MINIBOSS | Budget-exempt boss room | Fine |
| SPIKE | Treasure/vault room (1.5× budget allowed) | Fine if intentional |
| EXEMPT | Explicitly exempt | Fine |

Only `OVER` in normal rooms is a problem. A few `UNDER` per band is expected and healthy.

---

## Full CLI Reference

### `--suite` flags

| Flag | Effect |
|------|--------|
| `--suite` | Run full 15-scenario matrix |
| `--suite --fast` | Run 6-scenario subset (one per depth group), 20 runs each |
| `--suite --out-dir <path>` | Custom output directory (default: `reports/balance_suite/<timestamp>/`) |
| `--suite --baseline <path>` | Compare against custom baseline file |
| `--suite --update-baseline` | Write new baseline, exit 0 regardless of FAIL count |
| `--suite --seed <n>` | Override base seed (default: 1337) |

### `--depth-report` flags

| Flag | Effect |
|------|--------|
| `--depth-report --in <dir>` | Read Phase 1 output directory |
| `--depth-report --in <file>` | Read summary.json directly |
| `--depth-report --out <file>` | Write markdown to file (default: stdout) |

### `--etp-sanity` flags

| Flag | Effect |
|------|--------|
| `--etp-sanity` | Run all bands (depths 3, 8, 13, 18, 23) |
| `--etp-sanity --strict` | Exit 1 on any OVER violation |
| `--etp-sanity --depth <n>` | Single depth only |
| `--etp-sanity --runs <n>` | Samples per depth (default: 1) |
| `--etp-sanity --verbose` | Per-monster ETP breakdown |

### Other useful commands

```bash
# Run a single scenario
dotnet run --project tools/Harness -- --scenario depth3_orc_brutal --runs 50 --json

# Run all scenarios (without suite verdict)
dotnet run --project tools/Harness -- --all --json

# Dungeon soak run (full 6-floor bot campaign)
dotnet run --project tools/Harness -- --dungeon --floors 6 --runs 50 --report

# Run fast tests (default dev workflow)
dotnet test tests/ --filter "Category!=Slow"
```

---

## The Acceptance Matrix

The 15 scenarios the suite always runs. Each tests a specific depth + weapon tier combination.

| Scenario | Runs | Turn Limit | Purpose |
|----------|------|------------|---------|
| `depth2_orc_baseline` | 40 | 100 | Depth 2 baseline (no weapon) |
| `depth2_orc_baseline_keen` | 40 | 100 | Depth 2 with keen_dagger |
| `depth2_orc_baseline_vicious` | 40 | 100 | Depth 2 with vicious_shortsword |
| `depth2_orc_baseline_fine` | 40 | 100 | Depth 2 with fine_longsword |
| `depth2_orc_baseline_masterwork` | 40 | 100 | Depth 2 with masterwork_longsword |
| `depth3_orc_brutal` | 50 | 110 | Depth 3 pressure (no weapon) |
| `depth3_orc_brutal_keen` | 50 | 110 | Depth 3 with keen_dagger |
| `depth3_orc_brutal_vicious` | 50 | 110 | Depth 3 with vicious_shortsword |
| `depth3_orc_brutal_fine` | 50 | 110 | Depth 3 with fine_longsword |
| `depth3_orc_brutal_masterwork` | 50 | 110 | Depth 3 with masterwork_longsword |
| `depth5_zombie` | 50 | 150 | Depth 5 baseline (no weapon) |
| `depth5_zombie_keen` | 50 | 150 | Depth 5 with keen_dagger |
| `depth5_zombie_vicious` | 50 | 150 | Depth 5 with vicious_shortsword |
| `depth5_zombie_fine` | 50 | 150 | Depth 5 with fine_longsword |
| `depth5_zombie_masterwork` | 50 | 150 | Depth 5 with masterwork_longsword |

**Fast mode** (--fast) runs only: `depth2_orc_baseline`, `depth3_orc_brutal`, `depth5_zombie`, `depth2_orc_baseline_fine`, `depth3_orc_brutal_fine`, `depth5_zombie_fine` — 20 runs each.

---

## CI Behavior

The CI workflow (`.github/workflows/balance.yml`) runs on every PR:

1. Fast tests (`dotnet test --filter "Category!=Slow"`)
2. `harness --suite` against the committed baseline
3. Uploads `verdict.json` + `balance_report.md` as build artifacts

**Exit codes:**
- `0` — PASS, WARN, or NO_BASELINE → PR proceeds
- `1` — FAIL → PR blocked

A PR that shifts death_rate by +0.21 at depth 3 will block. The artifact shows exactly which metric failed and by how much.

---

## Seeding

All harness runs use SHA-256-derived per-scenario seeds:
```
seed = SHA-256("{scenario_id}:{run_index}:{base_seed}") → first 4 bytes big-endian
```

This means two scenarios at the same run index get independent RNG states — no accidental correlation when running the matrix. Base seed default: `1337`. Override with `--seed`.

The reference value for `depth3_orc_brutal:0:1337` is `3699130415` — verified cross-language against the PoC.

---

## Adding a New Scenario to the Matrix

1. Create the scenario YAML in `config/levels/`
2. Add the entry to `SuiteRunner.Matrix` in `tools/Harness/SuiteRunner.cs`
3. Run `harness --suite --update-baseline` to capture the new scenario in the baseline
4. Commit both the YAML and the updated baseline

Don't add scenarios that are `is_probe: true` to the matrix — probes are excluded from PASS/FAIL and add noise.

---

## Common Scenarios and What They Mean

| Situation | Action |
|-----------|--------|
| Added a new monster | Run `--suite` to check depth-band impact; run `--etp-sanity` to verify room budgets |
| Changed monster stats | Run `--suite --fast` first, then `--suite` if clean |
| Changed player progression | Run `--suite` (weapon variants will show gear-scaling drift) |
| Changed depth scaling curves | Run `--suite` + `--depth-report` to see full curve shift |
| Added new level templates | Run `--etp-sanity --strict` to verify room budgets |
| Pre-release balance pass | Run `--suite` + `--depth-report --out balance_review.md` and review the report |
