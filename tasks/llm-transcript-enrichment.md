# Task: LLM Testing — Transcript Enrichment (Analyst Phase 0–1 engineering)

Scope: rubric-INDEPENDENT engineering only. No rubric content, no BugDetector
detection logic, no coherence pass. Schema is provisional-pending-rubric: the
mechanical-event capture set stays open for additions when the rubric's
silent_failure inventory lands.

Plan source: `docs/llm-testing/00-overview.md`, `shared-transcript-schema.md`,
`plan-analyst.md` (Phases 0–1).

## Current State

**Status: COMPLETE.** All sub-tasks done; 7 new tests + full fast suite (2059) green.
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
