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
- **Step 8 DONE + GREEN:** staged-start (see build order #8). 0c FOUNDATION COMPLETE — all 8 steps done.
- **Open follow-up (now UNBLOCKED, needs a design call):** the escalator alive-vs-killed comparison
  (EscalatorComparison, the classifier's 3rd escalator signal) is still null in the report → the escalator
  branch stays moot. Staged-start was its prerequisite and is now met. Two ways to PRODUCE it: (a) partition
  a soak's runs by EscalatorNeutralizedAtTurn (early vs not) — cheap, uses existing capture, but carries
  selection bias; (b) a controlled experiment (bot target-priority knob to force kill-early vs leave-alive)
  — unbiased, needs a bot-policy feature. DECIDE before wiring; don't bake in the biased one silently.
- **PIVOT (2026-06-09) — two balance layers, see memory project_balance_two_layers:** the first B1 full-soak
  reading conflated Layer 1 (engagement: does a composition resolve fairly in isolation — controlled
  scenarios) with Layer 2 (economy: does the run string fair engagements together — full soak). The "Density"
  flag smeared engagement-density + bot-pulled-rooms + economy-attrition. ENGAGEMENT BALANCE FIRST, in
  controlled `ScenarioHarness` scenarios (PoC method), THEN soak = Layer-2 economy test.
- **DONE — bridge + orc ladder + first controlled reading (2026-06-10):** see below.
  It exists (`ScenarioHarness`/`ScenarioDefinition` + 59 YAMLs in config/levels/) but produces PoC
  PressureMetrics (`RunMetrics`), NOT FloorHealthClassifier/LeverAttribution. Bridge = derive a per-death
  PlayerDeathRecord from each PlayerDied run's RunMetrics aggregates + the KNOWN composition (DistinctAttackers
  = composition size; archetype from tags), then run the (unchanged, pure) classifiers → a scenario role-aware
  report. Read-level tested.
- **Bridge:** `EngagementTracker` (extracted standalone from `DungeonRunHarness.FloorCombatTracker`; both
  harnesses share the single source of truth). `RunMetrics` gains `KillerId`/`HadSpike`/`HadEscalator`/
  `EngagementDeath`; `RecordTurn` captures killerId from player DeathEvent. `AggregatedMetrics` gains
  `Deaths`/`HasSpike`/`HasEscalator`. `ScenarioHarness.RunOnce` wires `EngagementTracker` per run. True
  per-death capture (not derive-from-aggregates) so mixed compositions (spike/escalator/half-the-threat-model)
  work faithfully from day one. `ScenarioEngagementReport.Format` renders the role-aware section + levers.
  Scenario `--report` flag wired in the CLI.
- **Orc ladder:** 4 scenarios (`scenario_b1_orc_2/3/4/5.yaml`, `config/levels/`), 100 runs each, B1 player
  (dagger+leather, accuracy 3), 1 healing potion. Intended verdicts: 2=Comfortable, 3=Tough/Winnable,
  4=The Flip (~35-50% death target), 5=Too-Much. Tests: `ScenarioEngagementReportTests` (7, green incl. Slow
  real-engine archetype-attribution proof).
- **FIRST CONTROLLED B1 READING (2026-06-10):**
    b1_orc_2: Death% 0.0% | Δ -5.0pp | Verdict: TooEasy  (H_PM 6.0, H_MP 8.9, monster hit 35%)
    b1_orc_3: Death% 0.0% | Δ -5.0pp | Verdict: TooEasy  (H_PM 6.0, H_MP 9.0, monster hit 37%)
    b1_orc_4: Death% 5.0% | Δ —      | Verdict: BaselineBroken  └─ levers: Density ×3 · Armor ×1 · MonsterDamage ×1
    b1_orc_5: Death% 12.0%| Δ —      | Verdict: BaselineBroken  └─ levers: Density ×9 · Armor ×2 · MonsterDamage ×1
  Signal: the bot crushes 2-3 orcs (0% death), the 4-orc flip barely nicks it (5%), 5 orcs starts to hurt
  (12%, both readings BaselineBroken). The target band (5-15%) is dramatically too permissive for B1 at the
  low end — 0% death for 3 orcs means the control and "tough" scenarios both read TooEasy. Target band needs
  rethinking for controlled scenarios (see next step note).
- **NEXT: recalibrate the B1 engagement target bands** before tuning. The current band (5-15%) is the global
  soak rate; for a one-room controlled scenario with 1 healing potion, the bot zero-deaths 2 and 3 orcs
  clean. The engagement band should be per-composition, decided on merits (0% comfortable, 0-15% tough,
  35-50% the flip). Then tune the orc count / player stats / potion supply until each scenario reads its
  intended verdict. One lever at a time.
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
8. ✅ **Staged-start** — `DungeonFloorBuilder.CreateGearedPlayer(profile)` + `GearProfile`/`GearProfileLoader`
   + `config/balance/gear_profiles.yaml` (b1–b5 placeholders) + `RunSoakStaged(startDepth, gearProfile)` on
   `DungeonRunHarness` (RunSingle parameterized with startDepth + geared initial player; absolute seed-per-
   depth = same geometry as a full run at depth N) + CLI `--start-floor/--gear`. Tests: `GearProfileTests`
   (fast), `StagedStartTests` (Slow). Verified e2e (b3 gear, MaxHp 82 vs default 56, depths 3–5).

## Key facts (from harness map)
- Soak engine is in `src/Logic/Balance/` (NOT tools/Harness — that's just CLI). `DungeonRunHarness.cs`,
  `DungeonSoakRunResult.cs`, `DungeonSoakSummary.cs`, `OutcomeClassifier.cs` (pure precedent),
  `DungeonSoakReport.cs`, `BalanceSuiteEvaluator.cs` (delta precedent).
- Death+killer captured `DungeonRunHarness.cs:405-413` (killer = display-name string only).
- YAML→typed loader pattern: `Etp/EtpConfigLoader.cs:11`.
- Harness test pattern: `tests/Balance/DungeonSoakReportTests.cs` (synthetic results, no engine).
- Staged-start is a small NEW build (Weighing gives nothing reusable); only seam is `Build(existingPlayer)`.
