# Balance Pipeline Build — Task Tracker

## Current State
All 5 phases complete. 1838 tests pass. Baseline committed.

**Just completed:** All phases (0 through 5) implemented and verified.
**Next step:** Mark plan_balance_pipeline_impl.md as complete, update INDEX.md.

---

## Phase 0 — Deterministic Seeding

- [x] TASK-001: `src/Logic/Balance/SeedDerivation.cs` — new
  - SHA-256 + big-endian bytes, cross-language reference value verified (3699130415 for depth3_orc_brutal:0:1337)
  - 6 tests in `tests/Balance/SeedDerivationTests.cs`
- [x] TASK-002: Wire into `ScenarioHarness.cs:46` — `SeedDerivation.Stable(scenario.ScenarioId, i, baseSeed)`
- [x] TASK-003: Recalibrate provisional bands in `PressureModel.cs` — updated comments with post-reseed values

## Phase 1 — Acceptance Matrix

- [x] TASK-101: 4 depth-2 weapon-variant scenarios (keen, vicious, fine, masterwork)
- [x] TASK-102: 4 depth-3 weapon-variant scenarios (keen, vicious, fine, masterwork)
- [x] TASK-103: 4 depth-5 zombie weapon-variant scenarios (keen, vicious, fine, masterwork)
- [x] TASK-104: `NormalizedMetrics` record in `src/Logic/Balance/NormalizedMetrics.cs`
  - `AvgPlayerAttacksPerRun` + `AvgMonsterAttacksPerRun` added to `AggregatedMetrics`
- [x] TASK-105: `SuiteRunner` matrix execution — `tools/Harness/SuiteRunner.cs`
  - 15-entry full matrix, 6-entry fast matrix (verbatim from PoC)
  - `BalanceSuiteEvaluator.cs` extracted to Logic layer for testability
- [x] TASK-106: Markdown report formatter — `GenerateMarkdownReport()` in SuiteRunner
- [x] TASK-107: Wire `--suite`, `--fast`, `--out-dir`, `--baseline`, `--update-baseline` into Program.cs
- [x] TASK-108: End-to-end verification — `harness --suite --fast` completes, writes all files, exits 0

## Phase 2 — Baseline & Regression

- [x] TASK-201: `ComputeDeltas` + `ClassifyVerdict` in `BalanceSuiteEvaluator.cs`
  - Drift thresholds match PoC verbatim
  - 12+ tests in `tests/Balance/SuiteRunnerTests.cs`
- [x] TASK-202: Baseline read/write + `--update-baseline` flag
  - `SuiteRunner.SaveBaseline()` + `LoadBaseline()` with forward-compat
- [x] TASK-203: Wire baseline comparison into `SuiteRunner.Run()`
  - `verdict.json` includes deltas + per-scenario verdicts
  - Exit code 1 on FAIL, 0 on PASS/WARN/NO_BASELINE
- [x] TASK-204: Bootstrap initial baseline — `reports/baselines/balance_suite_baseline.json` committed
  - All 15 scenarios PASS on subsequent `harness --suite`
- [x] TASK-205: CI workflow — `.github/workflows/balance.yml`

## Phase 3 — Full ETP

- [x] TASK-301: `config/etp_config.yaml` — verbatim from PoC + behavior_aliases extension
- [x] TASK-302: `EtpConfigLoader` + `EtpConfig`/`BandConfig` records in `src/Logic/Balance/Etp/`
- [x] TASK-303: `EtpCalculator` (full, replaces stub stub kept as legacy facade)
  - Band lookup, DPS, durability, behavior modifier, speed tiers, GetMonsterEtp, budgets
- [x] TASK-304: `EtpBudgetChecker.CheckRoom` with tolerance, spike allowance
- [x] TASK-305: 25+ ETP tests in `tests/Balance/EtpCalculatorTests.cs`

## Phase 4 — Depth Pressure Report

- [x] TASK-401: `DepthCurvePoint` + `DepthReportLoader` (`tools/Harness/DepthReportLoader.cs`)
- [x] TASK-402: `FormatPressureTable` + `FormatTargetComparison`
- [x] TASK-403: `DeriveRequiredDamageMultiplier` + `FormatMultiplierRecommendations`
- [x] TASK-404: `FormatScalingDiagnosis` with HP-HEAVY/BALANCED/SPIKE/FLAT/MIXED categorization
- [x] TASK-405: Wire `--depth-report --in <dir/file> --out <file>` CLI flag

## Phase 5 — ETP Sanity Tool

- [x] TASK-501: Audit LevelTemplate — `EncounterBudget.AllowSpike` already exists in LevelOverride
- [x] TASK-502: `AnalyzeLevel` in `src/Logic/Balance/Etp/EtpSanityHarness.cs`
  - `GameState.Rooms` added; DungeonFloorBuilder populates it
- [x] TASK-503: `RunSanity` orchestrator + CSV writer
- [x] TASK-504: Wire `--etp-sanity`, `--strict`, `--depth`, `--runs`, `--verbose` CLI flags
- [x] TASK-505: Verification run — no OVER violations at depth 3 (all rooms OK or EMPTY)

## Files Changed (new)

- `src/Logic/Balance/SeedDerivation.cs`
- `src/Logic/Balance/NormalizedMetrics.cs`
- `src/Logic/Balance/BalanceSuiteEvaluator.cs`
- `src/Logic/Balance/DepthPressureReport.cs`
- `src/Logic/Balance/Etp/BandConfig.cs`
- `src/Logic/Balance/Etp/EtpConfig.cs`
- `src/Logic/Balance/Etp/EtpConfigLoader.cs`
- `src/Logic/Balance/Etp/EtpCalculator.cs`
- `src/Logic/Balance/Etp/EtpBudgetChecker.cs`
- `src/Logic/Balance/Etp/EtpSanityHarness.cs`
- `config/etp_config.yaml`
- `config/levels/scenario_depth2_orc_baseline_{keen,vicious,fine,masterwork}.yaml` (4 files)
- `config/levels/scenario_depth3_orc_brutal_{keen,vicious,fine,masterwork}.yaml` (4 files)
- `config/levels/scenario_depth5_zombie_{keen,vicious,fine,masterwork}.yaml` (4 files)
- `tools/Harness/SuiteRunner.cs`
- `tools/Harness/DepthReportLoader.cs`
- `reports/baselines/balance_suite_baseline.json`
- `.github/workflows/balance.yml`
- `tests/Balance/SeedDerivationTests.cs`
- `tests/Balance/SuiteRunnerTests.cs`
- `tests/Balance/EtpCalculatorTests.cs`
- `tests/Balance/DepthPressureReportTests.cs`
- `tasks/balance_pipeline_build.md`

## Files Changed (modified)

- `src/Logic/Balance/ScenarioHarness.cs` — SeedDerivation.Stable wiring
- `src/Logic/Balance/ScenarioRunner.cs` — RunFromFileWithOverrides method
- `src/Logic/Balance/RunMetrics.cs` — AvgPlayerAttacksPerRun + AvgMonsterAttacksPerRun
- `src/Logic/Balance/EtpCalculator.cs` — legacy facade comment
- `src/Logic/Balance/PressureModel.cs` — provisional band comments updated
- `src/Logic/Core/GameState.cs` — Rooms property
- `src/Logic/Core/DungeonFloorBuilder.cs` — wire Rooms to GameState
- `tools/Harness/Program.cs` — --suite, --depth-report, --etp-sanity modes
- `.gitignore` — reports/balance_suite/ ignored, reports/baselines/ committed
