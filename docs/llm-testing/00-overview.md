# LLM Testing System — Overview

**Status:** Both plans locked. **Analyst Phase 0–1 engineering (rubric-independent) is COMPLETE** (2026-06-09).
Rubric-dependent work (BugDetector logic, coherence pass) still on hold pending the Thread 1 handoff.
**Last updated:** 2026-06-09

This directory contains the engineering plans for the LLM-based testing system.
Read this document first when resuming. All plans are self-contained and assume
no prior conversation history.

---

## Three-Thread Decomposition

This system was designed across three parallel threads:

**Thread 1 — Evaluation Rubric** (design-owned, external to this directory)
The bug taxonomy, observability invariants, and game-specific fun framework.
Owned by the design process and developed in a separate session. These plans
consume the rubric as an external interface — they do not author it. The rubric
arrives as a handoff YAML file. Do not write rubric content here.

**Thread 2 — The Analyst** (plan: `plan-analyst.md`)
A post-run evaluation pipeline. Reads enriched bot-run transcripts, evaluates
them against the rubric spec, and produces structured per-run and aggregate
reports. The cheap, high-volume instrument. Operates headlessly on transcripts;
never plays the game.

**Thread 3 — The Player** (plan: `plan-player.md`)
An LLM brain (Claude Haiku) that plays the game turn-by-turn, produces
structural self-assessments about decision quality, and emits transcripts in the
same enriched format the Analyst reads. The expensive, high-signal instrument.
Its unique value is turn-by-turn reasoning and structural self-report — the
things the analyst cannot do from a bot transcript.

These plans cover Threads 2 and 3. Thread 1 is upstream.

---

## What Is Settled

**Shared transcript schema** (see `shared-transcript-schema.md`)
- `TurnRecord.action_taken` carries the full resolved `PlayerAction` including
  all parameters — not just the ActionKind string. This enables deterministic
  replay: game state at any turn N is reproducible from (seed + action sequence).
- Verbatim player-facing text is embedded in the event stream, not referenced by
  ID. Every run (bot and LLM) captures this regardless of persona. See the
  "Verbatim Text Capture" section of the schema document.

**Constraint A — BugDetector is fully data-driven**
Bug categories are defined in the rubric YAML. New categories are added by
editing config, not C# code. Each category carries a `mechanism` field
(predicate | text_pattern | llm_judged) that selects the detection implementation.
v1 ships the predicate mechanism implemented; text_pattern and llm_judged are
stubs. See `plan-analyst.md §2 BugDetector`.

**Constraint B — BugDetector and CoherenceEvaluator are strictly separate**
Value-correctness checks (is this computed correctly?) belong in BugDetector.
Experiential checks (does this feel earned?) belong in CoherenceEvaluator. The
`record_reflects_choices` dimension will split across both passes per the design
thread — no code change needed when that happens, as both passes are
config-driven. No value-correctness logic may migrate into the LLM coherence
prompt.

**No "fair" in self-assessment vocabulary**
Structural judgments only in the Player's self-assessments. Death events use
decision-traceability framing ("traceable-to-decision" or
"arrived-without-decision-point"), not fairness judgments.

**Two personas, voice-engagement axis**
The Reader and The System Explorer. No other personas until these two teach us
something. GameStateDescriber is persona-aware: The Reader receives verbatim
Hollowmark lines and mural/sign text; The System Explorer receives compressed
form.

---

## Upstream Dependency: Minimal v1 Rubric

The following is the minimum the design thread must deliver before Analyst
Phase 2 and Player Phase 0 can begin. Do not author this content here — it
arrives as a handoff.

```yaml
structural_judgment_schema:
  - dead_action_space
  - forced_move
  - novel_encounter
  - system_unreachable

bug_categories:
  [entries, each with mechanism: predicate|text_pattern|llm_judged]
  [v1 entries use mechanism: predicate only]

# Constraint: coherence_dimensions entries are experiential only.
# Value-correctness checks belong in bug_categories, not here.
coherence_dimensions:
  [entries from design thread]
```

The `structural_judgment_schema` unblocks both plans. The `bug_categories`
structure unblocks Analyst Phase 2. Coherence dimensions can arrive later
(Analyst Phase 3).

---

## What Was Built (Analyst Phase 0–1 engineering)

Rubric-independent. Code:
- `src/Logic/Balance/Transcript/EnrichedTranscript.cs` — schema models (header / turn /
  summary / action_taken / system-triggers / memo).
- `src/Logic/Balance/Transcript/TurnEventJsonConverter.cs` — extensible polymorphic event
  serializer (the open seam).
- `src/Logic/Balance/Transcript/ActionTakenBuilder.cs` — resolved PlayerAction → ids+types.
- `src/Logic/Balance/Transcript/TranscriptRecorder.cs` — accumulate, resolve voice, build
  summary, write JSONL.
- `DungeonRunHarness.RunWithTranscript(...)` + recorder hooks (non-invasive).
- `VoiceLineEvent.ResolvedText`; `PersistentRunState.CreateEmpty()`.
- CLI: `dotnet run --project tools/Harness -- --dungeon --llm-transcript <dir> --floors N --runs M --seed S`
  (fresh harness per run; loads voice + memo registries).
- Tests: `tests/Balance/EnrichedTranscriptTests.cs` (7, all green).

Validated on 10 real bot runs (seed 1337, 10 floors); schema round-trips; verbatim memo
text and (via targeted test) voice ResolvedText are greppable; seed reproduces
byte-identical output.

**Provisional-pending-rubric:** the mechanical-event capture set is OPEN (see the trigger
inventory above). Do not treat the schema as fully locked — settled parts are action
serialization, the two narrative fixes, RunSummary/HP profile; the trigger-event set may grow.

## Next Action When Work Resumes

1. **Confirm the minimal v1 rubric has landed from the design thread.** It
   should exist as `config/rubric/v1.yaml` (proposed location). Do not proceed
   with Phase 2 without it.

2. **Reconcile the trigger inventory** (above) against the rubric's silent_failure list —
   wire any newly-required mechanical events (notably orc-rep and aggravation-faction).

3. **Begin Analyst Phase 2** (BugDetector + single-run report) once the rubric lands.

4. **Begin Player Phase 0–2 in parallel** — the transcript format is now validated and
   ready to target.

---

## Two Invariants — VERIFIED (2026-06-09)

Both verified with controlled tests in `tests/Balance/EnrichedTranscriptTests.cs`
and a real-run check, not assumed.

**1. Deterministic entity-ID assignment under a fixed seed — PASS, with one caveat.**
- Player is always ID 0; gear + map entities are allocated sequentially from a
  seeded-RNG-driven `EntityFactory`/`EntityIdAllocator` (`DungeonFloorBuilder`).
  Given a FRESH factory, the same seed yields the same IDs — `SameSeed_ProducesIdenticalTranscript`
  and `SameSeed_IdenticalActionTargetEntityIds` pass; a fresh re-run of seed 1337
  reproduces a byte-identical transcript (modulo the per-run `run_id` GUID).
- **Caveat (important for replay):** the factory counter is process-shared mutable
  state and is NOT reset per run. A *reused* harness drifts absolute IDs across runs
  (~+1 per entity created). Gameplay outcomes are unaffected — IDs feed no game logic
  or RNG, confirmed by `TranscriptCapture_DoesNotAlterGameOutcome` and the existing
  soak determinism test — but transcript IDs would no longer match a fresh replay.
  **Resolution:** the `--llm-transcript` CLI builds a FRESH harness per run, so every
  transcript corresponds to what replaying (seed + actions) in a fresh harness produces.
  A future optimization could reset the factory at run start instead of rebuilding.

**2. Verbatim text reaching the transcript — PASS (both gaps fixed).**
- `VoiceLineEvent` now carries a `ResolvedText` field. The harness recorder resolves
  `TriggerId` against `VoiceLineRegistry` (logic layer) using a DEDICATED rng — never
  the game rng — so capture cannot perturb the replay stream. Verified by
  `VoiceLineEvent_ResolvedTextReachesTranscript`. **Note:** all `VoiceLineEvent`s are
  possession-gated (every emit site is in `PossessionSystem`), so standard *bot* runs
  never fire one — the bulk instrument will not surface voice/register defects
  organically. The Reader/System-Explorer LLM personas (or a possession-capable bot)
  are required to exercise voice resolution at volume.
- Memos: captured verbatim in `RunSummary.memos_delivered` (RunSummary approach, per
  §5). The transcript harness runs `MemoDeliveryEvaluator` at run end against a fresh
  `PersistentRunState`. Verified greppable end-to-end on a real death run
  (`DeathRun_CapturesVerbatimMemos`; the full memo body appears in `run-*.jsonl`).
- **Serialization fix:** the transcript uses `UnsafeRelaxedJsonEscaping` so verbatim
  text (apostrophes, em dashes, `<`, `&`) stays greppable rather than `\uXXXX`-escaped
  — otherwise text-pattern checks (e.g. a house-style em-dash rule) would silently miss.

Already greppable (no changes needed): `MuralExaminedEvent.Text`,
`SignpostReadEvent.Message`, `WeighingDialogueEvent.Pages[].Text`.

---

## Mechanical Trigger Capture — Inventory & Stranded Signals

The capture layer (`TurnEventJsonConverter`) serializes EVERY `TurnEvent` subtype
generically by reflection into each turn's `events` array, with an `event_type`
discriminator. **New event types are captured automatically — no capture-layer change
when the rubric's silent_failure inventory adds trigger events.** This is the open seam.

Findings on mechanical triggers the rubric thread asked about (verified, NOT fixed —
fixes await the full trigger inventory):

- **AggravatedEffect / TargetFaction — captured, but parameter-incomplete.** Application
  is NOT stranded in presentation: it fires a `SpellEvent` in the logic event stream with
  `StatusApplied="aggravated"` (`SpellResolver.ResolveAggravation`). However, the
  `TargetFaction` VALUE (e.g. "orc") is NOT on the event. A window-check detector
  ("aggravated → expect faction-change within 2 turns") needs that faction to know what to
  watch — so the trigger is greppable but the parameter is missing. **Deeper gap:** the
  *consequence* side is itself unimplemented — `BasicMonsterAI.ChooseTarget` does not yet
  consult `TargetFaction` (see `AggravatedEffect.cs` doc + `migration_loss_audit.md`), so
  no faction-change event can ever fire. That detector would always flag until both are wired.
- **Orc reputation changes — fully stranded (no event at all).** There is no `TurnEvent`
  representing an orc-rep change anywhere in the logic layer. `RunSummary.system_triggers`
  leaves `orc_rep_changed`/`orc_rep_change_turn` at defaults because nothing emits the
  signal. This needs a new mechanical event when the rubric thread defines the rep system's
  observability.
- **Weighing guardian allied count — not reachable by bot harness.** Lives in endgame
  (floor-25 Weighing) state the bot never reaches; `weighing_guardian_allied_count` stays 0.
  Wiring deferred until the Weighing-outcome capture is specified.
- **Possession / mural / past-Sasha / Weighing-reached — wired and working.** Derived from
  `PossessionEnteredEvent`, `MuralExaminedEvent`, `VoiceLineEvent` (`past_sasha*` prefix),
  and `WeighingDialogueEvent` respectively. (Bot runs rarely trip these — see voice note above.)

The `RunSummary.system_triggers` set is **provisional-pending-rubric**: the minimal set is
wired; the rubric may extend it (and should add the orc-rep + aggravation-faction events
above to make their silent_failure detectors implementable).

---

## Cost Estimates (reference)

**LLM Player — Haiku with caching:**
- ~$1.00 per 1000-turn run (25-floor game)
- System prompt (~2650 tokens) is cacheable; effective per-turn input ~965 tokens
- Reader persona adds 100–400 token surcharge on floors with Hollowmark/murals
- 50 runs/day sustained testing: ~$50–60/day

**Analyst — Haiku per run:**
- ~$0.01–0.02 per run for bug detection + coherence pass
- 500 runs/batch: ~$5–10
- Upgrade to Sonnet/Opus for nuanced coherence: ~$0.20–0.40/run

---

## File Index

| File | Contents |
|------|----------|
| `00-overview.md` | This file. Status, settled decisions, next actions. |
| `shared-transcript-schema.md` | The enriched JSONL transcript format both plans share. |
| `plan-analyst.md` | Thread 2 plan: post-run LLM evaluation pipeline. |
| `plan-player.md` | Thread 3 plan: LLM bot brain + self-assessment hooks. |
