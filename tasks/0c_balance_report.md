# Task: 0c — Whole-Game Balance Report (role-aware health)

## Current State
- **Just done (2026-06-09):** Steps 1–3 COMPLETE under the corrected multi-signal frame, all tests green
  (fast suite 2102 pass / 0 fail; capture tests Slow, real-engine, green).
  - Step 1 — `FloorRunMetrics` gains DamageTakenThisFloor / CombatTurns / AvgHitsToKill / EscalatorPresent
    / EscalatorNeutralized(+AtTurn) / `Death` (PlayerDeathRecord: the 6 lever signals + AttackFrequency).
    Captured live in RunSingle via a private `FloorCombatTracker` over the turn-event stream.
  - Step 2 — `config/balance/target_table.yaml` (B1–B5, HITS, B1-placeholder) + `TargetTable.cs` (ForDepth
    resolver, edge-clamped) + `TargetTableLoader.cs` (Etp pattern). Loader tests green incl. shipped config.
  - Step 3 — `threat_archetype` on MonsterDefinition (+Merge inherit) + `ThreatArchetypeTag` (Balance) +
    MonsterFactory attaches it; 15 monsters authored per §2, rest inherit. Tagging tests green (34).
  - Also: classifier honesty rename `TurnsToDown`→`HitsToDown`, `TargetTtd`→`TargetHitsToDown` (12 tests
    still green, values unchanged).
- **Also done:** the **lever-attribution classifier** — `LeverAttributionClassifier` (pure) + `BalanceLever`
  enum + `LeverExpectation`/`LeverFinding`/`LeverConfig`. Attributes a flagged death among the 5 actionable
  levers (monster-damage / armor / weapon-speed / density / frequency) from the signals; ranked, worst-first.
  hits-to-down stays the upstream role-fastness trigger (FloorHealth), not re-evaluated here. Outcome tests
  green (9): high-dmg⇒MonsterDamage, normal-dmg+high-hit-rate⇒Armor, normal-dmg+high-freq⇒AttackFrequency
  (proves freq/damage don't bleed). `tests/Balance/LeverAttributionClassifierTests.cs`.
- **Step 6 DONE + GREEN + COMMITTED:** Role-aware `Floor Health` section in
  `DungeonSoakReport` — OBSERVED death% / TARGET band / Δ / Verdict per floor, survival-rate framing, lever
  attribution line beneath too-hard floors. Inline death% math retired via shared `DeathPctFraction`/
  `GroupByDepth` helpers. `SpikePresent` added to capture (FloorHealth needs HasSpike). `lever_expectations`
  block added to target_table.yaml (placeholders) + `TargetRegion.LeverExpectation` + loader + `ForDepth`.
  CLI `--report` wired to load the table. New `Generate(summary, targets, ...)` overload; old `Generate(summary)`
  back-compat (omits the section). Read-level tests (FloorHealthReportTests, 5) + TargetTableLoaderTests (9)
  GREEN — incl. the two proof-tests at the REPORT level: TooHard+normal-dmg+high-hit-rate→"Armor"
  (not MonsterDamage); TooHard+normal-dmg+high-freq→"AttackFrequency" (not MonsterDamage).
- **Landed (2026-06-09) in two green commits** once the transcript/Analyst thread finished (it never
  committed, so this session landed both): A = transcript-enrichment + Analyst rubric (Thread 2/3) carrying
  the shared `DungeonRunHarness.cs` incl. `SpikePresent`; B = the 0c step-6 Floor Health report on top.
  Both compile in isolation (A verified via stash). The target-table slice landed earlier as `142af2e`.
- **Step 7 DONE + GREEN + COMMITTED:** `SoakBaseline` + `SoakBaselineEvaluator` + `SoakBaselineDeltaReport`
  + CLI `--update-baseline`/diff. Same-seed re-run shows all-`+0.0pp`/PASS (deterministic), verified e2e.
- **Next step:** step 8 staged-start — `RunSoakStaged(startDepth, gearProfile)` on `DungeonRunHarness` +
  parameterized gear-player via `DungeonFloorBuilder.Build(existingPlayer)` seam + `config/balance/
  gear_profiles.yaml` + CLI `--start-floor/--gear`. Produces the escalator alive-vs-killed comparison the
  capture already records the neutralized-when half of → lights up the classifier's escalator branch. Last
  step before B1 tuning (first tuned number, ascending by region).
- **Open issues / FLAGS for Rafe:**
  - `target_table.yaml` numbers are B1 placeholders (HITS), authored for real *during* B1 tuning.
  - Escalator alive-vs-killed comparison still only PRODUCED once staged-start (step 8) exists; the
    capture records neutralized-when, which step 8 will pair with the staged comparison.
  - **Archetype assignments RESOLVED (2026-06-09):** all Baseline — fire_beetle, cave_spider/web_spider,
    giant_spider (reclassified from Spike), orc_skirmisher, plague_zombie. Per the TIGHTENED SPIKE PRINCIPLE
    (spike = can't-tank-must-change-approach; status-on-weak-beast = texture; high-dmg-alone = hard baseline).
    Spike roster now troll/troll_ancient/wraith + lich(Fused). Reflected in entities.yaml + §2 + memory.

## Diagnostic design (LOCKED 2026-06-09) — see memory project_0c_diagnostic_design
- **Balance verdict = SURVIVAL RATE vs band** (multivariate by construction). ttd is NOT the balance
  metric — it's a subordinate diagnostic, consulted only AFTER survival rate flags a floor, to attribute
  WHICH lever. Make this split explicit in code + report.
- **Diagnostic = 6 bounded signals, one per lever** (per death): hits-to-down→role-fastness ·
  damage-per-hit→monster-damage · **killer hit-rate (landed/attempted)→armor/AC lever** (NOT
  damage-absorbed — combat is AC/avoidance, no soak exists) · counterattacks-landed→weapon-speed/control ·
  distinct-attacker count→density · **hits÷engagement-turns→attack-frequency (the wraith lever)**.
- **ttd unit = hits-to-down** (not turns). Rename `TurnsToDown`→`HitsToDown`, `TargetTtd`→`TargetHitsToDown`
  (honesty, not logic — 12 tests survive as-is in value). Lever signals are an ADDITIVE layer beside
  FloorHealth; zero existing tests change.
- **Attack-speed finding:** SpeedBonusTracker bonus-attacks is the sole frequency mechanism; spread is
  non-uniform (wraith 2.0 outlier, zombie 0.5 baseline, mid-cluster conditional, core baselines/lich/
  troll-base/necro flat 0) → frequency is its own parameter-free lever (hits÷turns), not folded into ttd.
- **Archetype assignment flags (need Rafe):** fire_beetle (NOT in §2 — left untagged) · orc_skirmisher
  (standalone, not orc-extending; tagged Baseline) · cave_spider/web_spider (§2 names only giant_spider but
  prose says ≡; tagged Spike) · plague_zombie (inherits Baseline from zombie).

## Hard requirement (non-negotiable, from Rafe)
0c's health classifications must be tested at the **OUTCOME** level, not attachment. A known-broken
composition must make the report SAY broken; a healthy one read healthy; an unfair escalator read UNFAIR.
The report is the instrument of truth — it cannot drift green while broken (the exact bug the audit exposed).

## Build order (each step compiles + tests green before the next)
1. ✅ **Metrics data-model** — `FloorRunMetrics` + `PlayerDeathRecord` (6 lever signals) captured in
   `RunSingle` via `FloorCombatTracker`. `tests/Balance/FloorMetricsCaptureTests.cs` (Slow, green).
2. ✅ **Target table** — `config/balance/target_table.yaml` + `TargetTable.cs` + `TargetTableLoader.cs`.
   `tests/Balance/TargetTableLoaderTests.cs` (green).
3. ✅ **Archetype tagging** — `threat_archetype` on MonsterDefinition + `ThreatArchetypeTag` + MonsterFactory.
   `tests/Balance/ThreatArchetypeTaggingTests.cs` (green, 34). FLAGS in Current State.
4. ✅ **FloorHealthClassifier (pure)** — `src/Logic/Balance/FloorHealthClassifier.cs`, sibling to
   `OutcomeClassifier`/`BalanceSuiteEvaluator`. Returns the seven verdicts; both refinements folded in.
5. ✅ **Outcome tests** — `tests/Balance/FloorHealthClassifierTests.cs`: 12 synthetic (observed, target,
   deaths) → assert verdict enum. Incl. the refinement proofs (fast-to-spike=Healthy; escalator-killed-
   early-but-still-lost=BaselineBroken). **All green.**
6. ✅ **Report columns** — role-aware `Floor Health` section in `DungeonSoakReport` (OBSERVED/TARGET/Δ/
   Verdict + lever line); verdicts from FloorHealthClassifier + LeverAttributionClassifier; inline deathPct
   math retired into shared helpers. `tests/Balance/FloorHealthReportTests.cs` (read-level, green).
7. ✅ **Delta baseline** — `SoakBaseline` (snapshot + JSON I/O), `SoakBaselineEvaluator` (per-depth deltas +
   PASS/WARN/FAIL on death-rate drift, mirrors `BalanceSuiteEvaluator`), `SoakBaselineDeltaReport` (read-level
   section). CLI: `--update-baseline` writes `reports/baselines/soak_baseline.json`, else diffs against it.
   `tests/Balance/SoakBaselineTests.cs` (8, green). Real baseline authored from a B1 soak during tuning.
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
