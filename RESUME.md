# RESUME — Catacombs balance Step-0 thread

**Branch:** `balance/0c-foundation` (committed + pushed for session handoff)
**Last updated:** 2026-06-09

## Current state (one line)
0b LOCKED; `FloorHealthClassifier` built + **12 outcome tests GREEN**; classifier verdict logic blessed
(gate cleared). Ready to wire the classifier to live soak data.

## Canonical docs (read these to reload context)
- `docs/balance/threat_archetypes.md` — **0b, LOCKED.** The definition of "balanced": 3-archetype model
  (durable baseline / intrinsic spikes / escalators / fused), composition-as-the-unit-of-balance, the
  assertion table, the five fix/drop calls, the resolved slime decisions.
- `docs/balance/migration_loss_audit.md` — PoC→C# loss triage (restore-now / later / drop-superseded).
- `docs/balance/balance_strategy.md` — Parts 1–4 (the durable-vs-lethal binary in Part 2 is superseded).
- `tasks/0c_balance_report.md` — 0c file list + 8-step build order + per-step status.

## NEXT ACTION (exact) — 0c steps 1–3: wire the classifier to live soak data
1. **Per-floor metrics capture** — add `DamageTakenThisFloor`, per-floor ttk/ttd, killer **archetype**,
   AND **whether/when the escalator was neutralized** to `FloorRunMetrics` (`DungeonRunHarness.cs:13`);
   populate in the `RunSingle` event loop (~`:391`; death/killer captured at `:405-413`).
2. **Target table** — `config/balance/target_table.yaml` + `TargetTable.cs` + `TargetTableLoader.cs`
   (follow `src/Logic/Balance/Etp/EtpConfigLoader.cs` verbatim). Numbers are placeholders; real per-region
   numbers are authored DURING B1 tuning (decided on merits, then measured).
3. **Archetype tagging** — `threat_archetype` field on monster defs (`config/entities.yaml` +
   `MonsterDefinition.cs`); attribute each death to an archetype. **Must capture neutralized-when** — the
   third escalator signal is uncomputable without it.

## QUEUED AFTER
- **0c step 6** — report formatting: Floor Efficiency table with OBSERVED/TARGET/FLAG/Δ columns, verdicts
  sourced from `FloorHealthClassifier`; retire the inline deathPct math (`DungeonSoakReport.cs:188`).
- **0c step 7** — soak delta baseline (`reports/baselines/soak_baseline.json`), mirror
  `SuiteRunner`/`BalanceSuiteEvaluator.ComputeDeltas`.
- **0c step 8** — staged-start (`RunSoakStaged` + `config/balance/gear_profiles.yaml` +
  `DungeonFloorBuilder.Build(existingPlayer)` seam + CLI `--start-floor/--gear`). This is what PRODUCES the
  escalator-alive-vs-killed comparison the classifier already consumes/tests.
- **THEN** — the first tuned number on B1, ascending by region, every health reading trusted because the
  report's own verdicts are outcome-tested.

## OPEN TRACK-2 (parallel; none block B1–B2; scheduled by when each region/need arrives)
- Aggravation rewire (RESTORE, ~25–40 lines in `ChooseTarget`) — before B4/B5.
- Hazard-avoidance restore (general, weighted-cost A*) — before B3+.
- Chest quality tiers — before loot-curve work.
- Binary→graded resistances — before elemental bosses/rings.
- Cheap ring restores (Clarity, Invisibility — reuse existing effects).
- Speed/Sluggish (haste/tar) restore — necessary-but-not-sufficient (bot needs a non-healing use-policy).
- Author deep-region compositions (slime swarms, lich court, ancient troll, wraith — ZERO scenarios today).
- `cultist_blademaster` needs a real role (live-but-orphaned hot baseline).

## OPEN DECISIONS
None blocking. All §7 slime decisions resolved; classifier verdict logic blessed; B1–B2 gate cleared.

## RULE (do not re-litigate)
Every restore ships with a scenario that exercises its **OUTCOME** — the lost wires were all
harness-invisible because tests asserted attachment, not outcome. Decide each archetype profile on its
merits, then measure reality against it — never ratify the grind.
