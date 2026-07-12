# Plan: LLM Analyst (Thread 2)

_Last verified: 2026-07-12 against commit 86b6f10_

**Status:** Locked. No code written. No-code hold in effect.
**Date locked:** 2026-06-09

## Context

This plan is part of the three-thread LLM testing system. See
`00-overview.md` for the full decomposition. Thread 1 (evaluation rubric) is
design-owned and upstream. This plan covers Thread 2 only.

The Analyst is the cheap, high-volume instrument: it reads enriched bot-run
transcripts and evaluates them against an external rubric spec. It never plays
the game. The Analyst also reads LLM Player transcripts (Thread 3), which are
richer input to the same pipeline — no special handling required.

---

## Goals

1. Evaluate enriched run transcripts against a rubric spec and produce structured
   per-run reports.
2. Aggregate across N runs to surface bug candidates, coherence patterns, and
   structural signals.
3. Treat the rubric as an external interface — no evaluation criteria invented
   internally.
4. Run as a CLI command against existing bot infrastructure, with no changes to
   game logic.

## Non-Goals

- Inventing evaluation criteria (design thread owns the rubric)
- Real-time analysis (post-run only)
- Automated feedback loops (later feature)
- Value-correctness checks inside the LLM coherence prompt (constraint B)

---

## §1. Rubric Interface

The Analyst loads a rubric YAML spec at runtime. It never hard-codes categories
or dimensions. The rubric file location is `config/rubric/v1.yaml` (proposed).

### Constraint A — mechanism-typed bug_categories

Every entry in `bug_categories` carries a `mechanism` field. BugDetector
dispatches on this field, not on the category name. New categories (including
voice/register checks from the design thread) are added by editing the YAML;
BugDetector's dispatch loop is unchanged. This is a non-negotiable schema
requirement: the design thread must include `mechanism` when authoring new
categories.

Mechanism types:
- `predicate` — deterministic check against transcript fields (v1: implemented)
- `text_pattern` — regex against verbatim surfaced text (v1: stub)
- `llm_judged` — LLM evaluates a candidate match (v1: stub)

```yaml
schema_version: 1

bug_categories:
  soft_lock:
    mechanism: predicate
    description: "Player cannot act; game not flagged as over"
    predicate: "available_action_count == 0 and not IsGameOver"

  impossible_state:
    mechanism: predicate
    description: "Value outside valid range"
    predicate: "player_hp_pct < 0 or > 1"

  silent_failure:
    mechanism: predicate
    description: "System should have triggered based on conditions but no event emitted"
    # detection expression specified per-system by design thread

  # Future categories from design thread use mechanism: text_pattern or llm_judged
  # Example (not yet authored):
  # register_violation:
  #   mechanism: llm_judged
  #   description: "Line violates the character's established register"
  #   judge_prompt: "..."
  # disallowed_character:
  #   mechanism: text_pattern
  #   description: "Em dash in surfaced text (house style prohibits it)"
  #   pattern: "—"

coherence_dimensions:
  record_reflects_choices:
    description: "Guardian tiers feel earned by the arc that led to them"
    # NOTE: the value-correctness half of this dimension (are tiers computed
    # correctly from run metrics) will relocate to bug_categories per the design
    # thread. Only the experiential/earned half lives here.

structural_judgment_schema:
  - dead_action_space
  - forced_move
  - novel_encounter
  - system_unreachable
```

### Constraint B — BugDetector and CoherenceEvaluator are strictly separate

Value-correctness checks (is this computed correctly from these inputs?) belong
in BugDetector, dispatched via the predicate or llm_judged mechanism.
Experiential checks (does this feel earned? does this feel right?) belong in
CoherenceEvaluator, fed from `coherence_dimensions`.

The `record_reflects_choices` dimension will split per the design thread. When
it does: the value-correctness half moves to `bug_categories`; the experiential
half stays in `coherence_dimensions`. No code change required — both passes are
config-driven. The invariant to enforce: no value-correctness predicate may
appear in the LLM coherence prompt.

### Minimal v1 rubric required to start

Analyst Phase 2 (BugDetector) requires `bug_categories` with mechanism fields.
Analyst Phase 3 (CoherenceEvaluator) additionally requires `coherence_dimensions`.
Both require `structural_judgment_schema`.

The Analyst validates the rubric at load time. Unknown mechanism values are a
fatal error. Unknown field names within a known mechanism are warnings (skipped
gracefully). Missing required fields are fatal errors with clear messages.

---

## §2. Components

### TranscriptLoader

Reads enriched JSONL, validates `schema_version` against supported versions.
Produces in-memory `RunTranscript` object. Handles partial transcripts (bot runs
without LLM fields) — absent optional fields default to null. Schema version
mismatch on required fields is fatal; unknown optional fields are ignored.

Validates the full `action_taken` object schema. On old-format transcripts (bare
ActionKind string), logs a warning and sets `replay_available = false` for that
run rather than failing.

### RubricLoader

Reads rubric YAML, validates against the Analyst's expected interface (mechanism
field required on all bug_categories entries). Produces in-memory `Rubric`
object. Versioned separately from transcript schema.

### BugDetector (constraint A)

Mechanism-based dispatcher. Each mechanism type is a separate implementation;
the category name is irrelevant to dispatch.

```
BugDetector
  ├── PredicateEvaluator     (v1: implemented)
  │     reads "predicate" field
  │     evaluates against TurnRecord fields and RunSummary fields
  │     no LLM call
  ├── TextPatternEvaluator   (v1: stub — logs "mechanism not implemented" and skips)
  │     reads "pattern" field
  │     applies regex to verbatim text fields in event stream
  └── LlmJudgedEvaluator     (v1: stub — logs "mechanism not implemented" and skips)
        reads "judge_prompt" field
        calls LLM with candidate match + judge_prompt
        returns boolean + evidence string
```

When the design thread adds a `register_violation` category with
`mechanism: llm_judged`, only the `LlmJudgedEvaluator` stub needs implementing.
The dispatch loop does not change.

**Output:** `List<BugCandidate>` with:
```jsonc
{
  "turn": 412,            // null for run-level checks
  "category": "soft_lock",
  "mechanism": "predicate",
  "description": "...",
  "evidence_snippet": "available_action_count=0, IsGameOver=false at turn 412"
}
```

### CoherenceEvaluator (constraint B)

LLM-based. Receives condensed transcript + rubric `coherence_dimensions` only.
Does NOT receive `bug_categories`. The prompt is built solely from
`coherence_dimensions` entries.

**Condensed transcript input** (~3K tokens): system_triggers, HP profile,
RunSummary, key events (near-death, system firsts, Weighing outcome), and
verbatim voice text (preserved, not summarized — see forward-compat note in
schema doc).

**Model selection:** Haiku by default; configurable per-run with `--coherence-model`
flag (use Sonnet/Opus for targeted deep-review runs).

**Output per dimension:**
```jsonc
{
  "dimension": "record_reflects_choices",
  "score": 4,
  "evidence": "Orc rep was Allied; Oathkeeper came up Allied at the Weighing. Consistent."
}
```

### StructuralJudgmentAggregator

Reads `structural_judgments` from RunSummary (LLM Player runs only; no-op for
bot runs). Groups by judgment type, surfaces patterns. Passed to
CoherenceEvaluator as additional context when present.

### EvaluationReport (per-run output)

```jsonc
{
  "run_id": "...",
  "persona": "balanced",
  "player_type": "bot",
  "replay_available": true,
  "bug_candidates": [
    { "turn": 412, "category": "silent_failure", "mechanism": "predicate",
      "description": "...", "evidence_snippet": "..." }
  ],
  "coherence": {
    "record_reflects_choices": { "score": 4, "evidence": "..." }
  },
  "system_coverage": {
    "possession_used": false,
    "commentary": "Possession available from floor 3; never used. Coherent with direct-combat play style."
  },
  "structural_summary": null,   // LLM Player runs only
  "analyst_note": "..."         // 1–2 sentence LLM summary of the run
}
```

### BatchAnalyzer

Parallel evaluation of N transcripts. Configurable concurrency.

**AggregateReport** output:
- Bug candidates appearing in ≥N runs (configurable confidence threshold)
- Coherence score distribution per persona
- System-trigger coverage heatmap (% of runs touching each system)
- Structural judgment frequency patterns (LLM Player runs)
- Human-readable `findings.md` for session handoff

---

## §3. CLI Interface

```bash
# Single run
dotnet run --project tools/Analyst -- \
  --transcript run-1234.jsonl \
  --rubric config/rubric/v1.yaml \
  --model haiku \
  --report reports/run-1234.json

# Batch
dotnet run --project tools/Analyst -- \
  --batch runs/ \
  --rubric config/rubric/v1.yaml \
  --concurrency 4 \
  --aggregate reports/batch-2026-06-09.md
```

---

## §4. Implementation Phases

| Phase | Sessions | Description |
|-------|----------|-------------|
| **0: Schema + stub rubric** | 0.5 | Finalize the enriched transcript schema (defined in `shared-transcript-schema.md`). Write stub rubric with mechanism-typed `bug_categories` and `structural_judgment_schema`. **Verify, don't trust:** deterministic entity-ID assignment under a fixed seed; verbatim text reaching the transcript (two known gaps: `VoiceLineEvent` and memo delivery). Validate schema design against a real bot JSONL before writing code. No code yet. |
| **1: Transcript enrichment (harness)** | 1 | Modify harness to emit enriched format. **Includes:** full `action_taken` object serialization; `SystemTriggerLog`; `RunSummary` with HP profile; `MemoDeliveredEvent` or PendingMemos verbatim in RunSummary; `VoiceLineEvent` with resolved text embedded. Validate: 10 bot runs; inspect verbatim text fields; confirm replay of action sequence against seed reproduces state deterministically for one known run. |
| **2: BugDetector + single-run report** | 1 | `TranscriptLoader`, `RubricLoader`, `BugDetector` with mechanism-dispatch structure. Predicate mechanism implemented; text_pattern and llm_judged are stubs that log and skip. `EvaluationReport` structure. CLI single-run. Validate: known-broken scenario triggers expected predicate candidates; stub mechanisms skip gracefully with logged warnings. |
| **3: CoherenceEvaluator** | 1 | LLM coherence pass. Condensed transcript format. Verbatim voice text preserved in condensed form. Constraint B enforced (only `coherence_dimensions` in prompt, never `bug_categories`). Validate: consistent scoring across 3 runs of same persona; Haiku and Opus produce directionally consistent scores. |
| **4: Batch pipeline** | 1 | `BatchAnalyzer`, `AggregateReport`, `findings.md`. Parallel execution. Validate: overnight batch of 50 bot runs; inspect aggregate. |
| **5: Mechanism expansion** | as needed | When design thread delivers text_pattern or llm_judged categories, implement the corresponding evaluator. No BugDetector dispatch changes. |

---

## §5. Open Issues

- **Rubric file location:** `config/rubric/v1.yaml` proposed. Should it be
  versioned in the repo (recommended) or loaded from a path flag only?
- **VoiceLineEvent resolved-text wiring:** two options — move resolution to the
  logic layer (harness can capture it directly) or have the harness runner read
  the registry post-event. Exact approach decided in Phase 1.
- **Memo delivery event:** two options — `MemoDeliveredEvent` in the turn event
  stream, or PendingMemos verbatim in RunSummary. RunSummary approach is simpler;
  event-stream approach captures delivery turn. Decide in Phase 1.
- **Bug candidate confidence:** frequency-across-runs is implicit. Should the
  aggregate report expose a numeric confidence field, or leave it to human
  judgment?
- **`record_reflects_choices` split:** dimension will migrate partially to
  `bug_categories` per the design thread. No code change needed when it arrives.
