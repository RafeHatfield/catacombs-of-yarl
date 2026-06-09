# Task: LLM Testing — Transcript Enrichment (Analyst Phase 0–1 engineering)

Scope: rubric-INDEPENDENT engineering only. No rubric content, no BugDetector
detection logic, no coherence pass. Schema is provisional-pending-rubric: the
mechanical-event capture set stays open for additions when the rubric's
silent_failure inventory lands.

Plan source: `docs/llm-testing/00-overview.md`, `shared-transcript-schema.md`,
`plan-analyst.md` (Phases 0–1).

## Current State (Analyst Phase 4 — DONE)

**Status: Analyst Phase 4 COMPLETE.** Batch pipeline in `tools/Analyst/`: BatchAnalyzer (parallel,
deterministic, resilient to bad files) + AggregateReport (JSON) + findings.md. 30 Analyst tests +
full fast suite (2140) green.
- **Audit-trail invariant holds at aggregate:** per-category total turns evaluated + runs ran +
  runs skipped roll up; "0 candidates" always travels with its ran-count. Missing field → SKIP rollup.
- **Heatmap = neutral fire rates + coverage_semantics interpretation.** 0× MECHANISM triggers
  ROUTE as UNVERIFIED blind spots ("does NOT mean broken"); CONTENT 0× never flagged; unmatched →
  unclassified (neutral). Classification bridges rubric example-names ↔ transcript keys by stem.
- **Real 50-run bot batch:** 0 candidates, each predicate evaluated 82,442 turns × 50 runs, 0
  skipped; blind spots = `possession_used`, `orc_rep_changed` (the canonical bulk-instrument gaps).
- Bug-candidate confidence = "N of M runs" frequency (resolves plan open issue). Coherence +
  structural-judgment = present-but-N/A slots (not faked).
- CLI: `--batch <dir> --rubric config/rubric/v1.yaml [--aggregate findings.md] [--aggregate-json <json>] [--concurrency N]`.
- No project-ref/shared-config changes; NUnit 4.5.1 pin untouched (reason inline at pin site).
- Next: Phase 3 coherence (needs coherence_dimensions) OR trigger_consequence evaluator+events
  (needs the four open contracts). The 0× blind-spot list feeds the scripted-scenario backlog.

---
## (Earlier) Analyst Phase 2

**Status: Analyst Phase 2 COMPLETE.** BugDetector (predicate mechanism) + single-run
EvaluationReport in `tools/Analyst/`. 21 Analyst tests + full fast suite (2132) green.
- Components: TranscriptLoader, RubricLoader (strict — all malformed/unknown cases fatal),
  PredicateExpression (self-contained evaluator), BugDetector (mechanism dispatch, predicate
  implemented; text_pattern/llm_judged/trigger_consequence log-and-skip), EvaluationReport.
- **Acceptance gate met:** all four runnable predicates demonstrated FIRING on engineered
  violation fixtures (permanent regression tests in tests/Balance/AnalystBugDetectorTests.cs) +
  end-to-end CLI. Clean runs auditable (predicate_coverage shows each ran); missing field → SKIP,
  not silent clean.
- Pinned NUnit to 4.5.1 (4.6.1 broke the suite's lambda assertions). Documented.
- Stopped before coherence pass (Phase 3) and trigger_consequence (needs evaluator + contracts).
- Next: Phase 3 coherence (needs full rubric coherence_dimensions) OR Phase 4 batch, OR the
  trigger_consequence events (faction-change, orc-rep, possession-grant, MemoDeliveredEvent).

---
## (Earlier) Transcript enrichment + cross-check

**Status: Phase-0/1 engineering + Phase-1 rubric cross-check COMPLETE.** 8 transcript tests +
full fast suite (2113) green.

**Rubric landed (config/rubric/v1.yaml + silent-failure-inventory.md). Cross-check done:**
- All four RUNNABLE-NOW predicates now executable — added 5 per-turn TurnRecord fields
  (`is_game_over`, `run_aggression_tally`, `possession_active`, `controlled_entity_id`,
  `player_entity_id`) + `run_aggression_tally` (final) in RunSummary. `possession_active`
  derived from PossessionEffect existence (non-circular). See 00-overview.md "Phase-1 Cross-Check".
- `trigger_consequence` spine NOT built (later mechanism). Needs new events: faction-change,
  orc-rep stance-change, possession ability-grant, and a per-turn memo-delivery decision +
  MemoDeliveredEvent. Reported, not wired.
- 4 open contracts flagged for Rafe (geas, past-Sasha payload, Assembly metric, Debt scaling).

**Next step:** Build Phase 2 (BugDetector predicate dispatch + single-run report) — needs no
new game code, only the rubric (now present). Then decide on the trigger_consequence events.

---
## (Historical) Phase-0/1 engineering — COMPLETE; 7 new tests + fast suite (2059) green.
**Just done:** Phase 0–1 engineering shipped. Both invariants verified (results in
00-overview.md). Two narrative gaps fixed (voice ResolvedText, memos in RunSummary).
Stranded mechanical signals reported (orc-rep has no event; aggravation SpellEvent lacks
TargetFaction value). Relaxed JSON encoder added for verbatim greppability. CLI builds a
fresh harness per run for replay fidelity.
**Next step (next session, rubric-gated):** reconcile trigger inventory vs rubric
silent_failure list; begin Analyst Phase 2.
**Open issues:** none blocking. Capture set left OPEN per instructions.

## Findings from investigation

- **Entity-ID determinism (Invariant 1):** Player is always ID 0; gear + map
  entities allocated sequentially from a seeded-RNG-driven `EntityFactory` /
  `EntityIdAllocator` (`DungeonFloorBuilder` L182–228). Deterministic under seed
  by construction. → verify with controlled test.
- **VoiceLineEvent (Invariant 2, gap A):** carries `TriggerId` only; resolved in
  `Main.cs` presentation via `VoiceLineRegistry.GetLine(...)` using the GAME rng.
  `VoiceLineRegistry` lives in the LOGIC layer (`src/Logic/Content`), so the
  harness can resolve. Fix: add `ResolvedText` to the event; recorder resolves
  with a DEDICATED per-run rng (never `state.Rng`) so replay determinism is
  preserved.
- **Memos (Invariant 2, gap B):** queued to `PersistentState.UnderWarden.PendingMemos`
  at run end by `MemoDeliveryEvaluator.EvaluateRunEnd`; no TurnEvent emitted. Bot
  harness never invokes the evaluator. Fix (RunSummary approach per §5): the
  transcript harness runs the evaluator at run end against a fresh PersistentState
  and captures memos delivered this run into `RunSummary.memos_delivered`.
- **AggravatedEffect / TargetFaction (mechanical trigger):** NOT stranded in
  presentation. Application IS in the logic event stream — but as a `SpellEvent`
  with `StatusApplied="aggravated"`; the `TargetFaction` VALUE is not in the
  event. Window-check detectors will need the faction param. Report, don't fix.
  (Also: the consequence side — `ChooseTarget` consulting `TargetFaction` — is
  itself unimplemented per AggravatedEffect.cs doc; separate game-logic gap.)
- **Extensibility:** ALL TurnEvents already flow through `turnResult.Events` in
  the logic layer (serializable, ID-based). Capture layer serializes events
  generically by reflection → new event types drop in with no capture rewrite.

## Sub-tasks

- ✅ Investigate codebase, settle approach
- ✅ Add `ResolvedText` to `VoiceLineEvent`
- ✅ Enriched transcript models (header/turn/summary/action_taken/system-triggers/memo)
- ✅ Extensible polymorphic TurnEvent JSON converter
- ✅ ActionTaken builder (resolved PlayerAction → entity IDs + type IDs)
- ✅ TranscriptRecorder (accumulate, resolve voice, build summary, write JSONL)
- ✅ Hook into DungeonRunHarness (optional, non-invasive)
- ✅ CLI flag `--llm-transcript <dir>` in tools/Harness/Program.cs
- ✅ Tests: entity-id determinism, schema round-trip, voice+memo greppable
- ✅ Validate on 10 real bot runs; grep verbatim text end-to-end
- ✅ Replay-determinism check on one known run
- ✅ Update 00-overview.md with results + stranded-event report

## Do NOT

- Author rubric content / config/rubric/v1.yaml
- Implement BugDetector predicate/text/llm logic
- Fix AggravatedEffect faction param or ChooseTarget hook (report only)
- Treat the mechanical-event capture set as locked
