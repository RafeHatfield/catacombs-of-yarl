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
- **Next step:** step 6 report — wire FloorHealthClassifier + LeverAttributionClassifier into
  `DungeonSoakReport` (OBSERVED/TARGET/FLAG/Δ; survival-rate=balance verdict, levers=attribution), retire
  inline deathPct math, and hydrate `LeverExpectation` per region (extend target_table.yaml with a
  `lever_expectations` block, placeholders). Then step 7 baseline, step 8 staged-start.
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
