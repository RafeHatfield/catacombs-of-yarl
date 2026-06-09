# Task: 0c — Whole-Game Balance Report (role-aware health)

## Current State
- **Just done:** Steps 4+5 COMPLETE — `FloorHealthClassifier` (pure, both refinements folded in) +
  `FloorHealthClassifierTests` (12 outcome tests, **all green**). This is the reviewable spec; the verdict
  logic is pinned by the tests. Reused canonical `TargetBand` (added Below/Above). Refinements: fast-death
  anchors to the killer's archetype ttd; escalator has 3 signals (not-escalating=EscalatorBroken,
  no-window=EscalatorUnfair, killing-it-doesn't-help=BaselineBroken).
- **Awaiting:** Rafe reviews the classifier by reading the test verdicts (the gate before steps 6–8).
- **Next step:** steps 1–3 — the WIRING that feeds the classifier from live runs (metrics capture →
  target_table.yaml + loader → archetype tagging on monster defs + death-archetype attribution).
- **Open issues:** `target_table.yaml` needs real per-region NUMBERS — authored *during* B1 tuning
  (decided on merits, then measured). Refinement-2's third signal (escalator-alive vs killed-early
  comparison) can only be PRODUCED live once staged-start (step 8) exists; the classifier already consumes
  + is tested on it. Step 3 must capture WHETHER/WHEN the escalator was neutralized, not just the killer.

## Hard requirement (non-negotiable, from Rafe)
0c's health classifications must be tested at the **OUTCOME** level, not attachment. A known-broken
composition must make the report SAY broken; a healthy one read healthy; an unfair escalator read UNFAIR.
The report is the instrument of truth — it cannot drift green while broken (the exact bug the audit exposed).

## Build order (each step compiles + tests green before the next)
1. ⬜ **Metrics data-model** — add `DamageTakenThisFloor`, combat-turn count, and per-floor ttk/ttd capture
   to `FloorRunMetrics` (`DungeonRunHarness.cs:13`); populate in the `RunSingle` event loop (~:391).
2. ⬜ **Target table** — `config/balance/target_table.yaml` (schema + B1 placeholder), `TargetTable.cs` +
   `TargetTableLoader.cs` (follow `Etp/EtpConfigLoader.cs` pattern).
3. ⬜ **Archetype tagging** — `threat_archetype` field on monster defs (`config/entities.yaml` +
   `MonsterDefinition.cs`); archetype-tag deaths from killer id.
4. ✅ **FloorHealthClassifier (pure)** — `src/Logic/Balance/FloorHealthClassifier.cs`, sibling to
   `OutcomeClassifier`/`BalanceSuiteEvaluator`. Returns the seven verdicts; both refinements folded in.
5. ✅ **Outcome tests** — `tests/Balance/FloorHealthClassifierTests.cs`: 12 synthetic (observed, target,
   deaths) → assert verdict enum. Incl. the refinement proofs (fast-to-spike=Healthy; escalator-killed-
   early-but-still-lost=BaselineBroken). **All green.**
6. ⬜ **Report columns** — `DungeonSoakReport.cs:145` Floor Efficiency: OBSERVED/TARGET/FLAG/Δ; source
   verdicts from the classifier; retire inline deathPct math (`:188`).
7. ⬜ **Delta baseline** — `reports/baselines/soak_baseline.json` + diff (mirror `SuiteRunner`/
   `BalanceSuiteEvaluator.ComputeDeltas`); CLI `--update-baseline` for soak.
8. ⬜ **Staged-start** — `RunSoakStaged(startDepth, gearProfile)` on `DungeonRunHarness` (loop init :293) +
   parameterized gear-player in `DungeonFloorBuilder.Build(existingPlayer)` seam + `config/balance/
   gear_profiles.yaml` + CLI `--start-floor/--gear`.

## Key facts (from harness map)
- Soak engine is in `src/Logic/Balance/` (NOT tools/Harness — that's just CLI). `DungeonRunHarness.cs`,
  `DungeonSoakRunResult.cs`, `DungeonSoakSummary.cs`, `OutcomeClassifier.cs` (pure precedent),
  `DungeonSoakReport.cs`, `BalanceSuiteEvaluator.cs` (delta precedent).
- Death+killer captured `DungeonRunHarness.cs:405-413` (killer = display-name string only).
- YAML→typed loader pattern: `Etp/EtpConfigLoader.cs:11`.
- Harness test pattern: `tests/Balance/DungeonSoakReportTests.cs` (synthetic results, no engine).
- Staged-start is a small NEW build (Weighing gives nothing reusable); only seam is `Build(existingPlayer)`.
