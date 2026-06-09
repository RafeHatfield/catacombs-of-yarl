# LLM Testing System — Overview

**Status:** Both plans locked. No code written. No-code hold in effect.
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

## Next Action When Work Resumes

1. **Confirm the minimal v1 rubric has landed from the design thread.** It
   should exist as `config/rubric/v1.yaml` (proposed location). Do not proceed
   without it.

2. **Begin Analyst Phase 0:** finalize the enriched transcript schema (defined
   in `shared-transcript-schema.md`) and validate the stub rubric structure
   against a real bot-run JSONL. No code yet — this phase is verification only.

3. **Begin Player Phase 0–2 in parallel** once Analyst Phase 1 (transcript
   enrichment, the format-defining phase) is complete and the Player has a
   validated transcript format to target.

---

## Two Invariants to Verify, Not Trust

Both must be verified during Analyst Phase 1, not assumed:

**1. Deterministic entity-ID assignment under a fixed seed**
The replay guarantee (game state reproducible from seed + action sequence) depends
on entity IDs being assigned deterministically. The existing bot regression
harness already assumes this; verify explicitly with a controlled test in Phase 1.

**2. Verbatim text reaching the transcript**
The schema addendum requires player-facing text to be embedded verbatim in the
event stream. Two known gaps exist as of the plan lock date (2026-06-09):

- `VoiceLineEvent` carries a `TriggerId` key only; the resolved line text is
  not in the event. The resolution happens in `Main.cs` presentation layer.
  **Fix required:** embed the resolved string in the event.
- Memos are queued into `PersistentState.UnderWarden.PendingMemos` with no
  `TurnEvent` emitted at delivery time. **Fix required:** add a
  `MemoDeliveredEvent` to the event stream, or include `PendingMemos` verbatim
  in `RunSummary`.

Both gaps are wiring work in Analyst Phase 1. Already known; verify and fix
then, not before.

Already greppable (no changes needed): `MuralExaminedEvent.Text`,
`SignpostReadEvent.Message`, `WeighingDialogueEvent.Pages[].Text`.

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
