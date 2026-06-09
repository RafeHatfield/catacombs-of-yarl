# Shared Transcript Schema

The enriched JSONL transcript format consumed by the Analyst and emitted by the
Player. Bot runs and LLM Player runs both produce this format; the LLM-specific
fields are null in bot runs and the Analyst handles their absence gracefully.

Schema version: 1 (bump when fields are added or types change).

---

## File Structure

One JSONL file per run. Each line is a JSON object with a `record_type` field
that identifies its structure. Four record types:

```
TranscriptHeader    (line 1 — always first)
TurnRecord          (one per turn)
RunSummary          (last line — appended after run ends)
```

---

## TranscriptHeader

```jsonc
{
  "record_type": "header",
  "schema_version": 1,
  "run_id": "uuid-string",
  "persona": "balanced",              // bot persona name OR llm persona name
  "player_type": "bot",               // "bot" | "llm"
  "llm_model": null,                  // null for bot; "claude-haiku-4-5" for llm
  "seed": 1337,
  "depth_reached": 18,
  "ending": "weighing_loss_debt",     // EndingType string; null if run interrupted
  "turn_count": 847,
  "floor_count": 18,
  "replay_available": true            // true iff all TurnRecords have full action_taken objects
}
```

---

## TurnRecord

```jsonc
{
  "record_type": "turn",
  "turn": 412,
  "floor": 9,
  "player_hp_pct": 0.72,
  "available_action_count": 4,

  "action_taken": {
    "kind": "Attack",                   // PlayerAction.ActionKind string
    "target_entity_id": 17,             // entity ID within this run (deterministic under seed)
    "target_entity_type": "orc_brute",  // species/item TypeId, for human readability
    "target_x": null,                   // for Move and location-targeted spells
    "target_y": null,
    "item_entity_id": null,             // entity ID of item used/dropped/thrown
    "item_type_id": null,               // stable type string ("healing_potion"), for readability
    "slot": null,                       // EquipmentSlot string if relevant
    "ability_id": null                  // for UseMonsterAbility
  },

  "events": [
    // The existing TurnEvent JSONL — all events that fired this turn.
    // Player-facing text events are detailed below under Verbatim Text Capture.
  ],

  // LLM Player only — null in bot runs:
  "decision_context": null,            // 1-2 sentence reasoning for the action taken
  "structural_assessment": null        // see Structural Assessment schema below; null when not warranted
}
```

### Replay guarantee

Game state at turn N is a deterministic function of (seed + the sequence of
`action_taken` objects for turns 0 through N-1). Replaying this sequence against
the original seed reproduces the exact game state, regardless of whether the
original run used a bot or an LLM brain. The only invariant: all game randomness
must flow through the seeded RNG (verified in Analyst Phase 1).

`replay_available` in the header is false only for transcripts written before
the full `action_taken` schema was wired (legacy compatibility).

### Structural Assessment schema (LLM Player only)

```jsonc
"structural_assessment": {
  "judgment": "dead_action_space",   // from rubric structural_judgment_schema
  "note": "All three visible actions were equivalent; outcome identical."
}
```

The LLM produces this only when warranted (system prompt criteria: one available
action, all options equivalent, novel encounter, or mechanic present but
inaccessible). Most turns: null. Vocabulary must match the
`structural_judgment_schema` from the rubric.

---

## Verbatim Text Capture

**All player-facing narrative text must be embedded verbatim in the event
stream, independent of persona and independent of bot-vs-LLM.** This is
required so the Analyst's voice/register bug detectors (including text-pattern
and LLM-judged checks) can operate on the actual as-fired strings in any run.
Bot runs are the bulk instrument; voice defects must be detectable in cheap
volume, not only in expensive LLM-Player runs.

### Status at plan lock date (2026-06-09)

Already greppable — no schema changes needed:
- `MuralExaminedEvent.Text` — full mural text at examination point ✓
- `SignpostReadEvent.Message` — full sign message at read point ✓
- `WeighingDialogueEvent.Pages[].Text` — full Guardian/Assembly/Lady dialogue ✓

Gaps requiring wiring (Analyst Phase 1):

**`VoiceLineEvent` — carries trigger ID only, not the resolved string.**
Currently: `{ "TriggerId": "possession_enter" }`
Required: `{ "TriggerId": "possession_enter", "ResolvedText": "You're inside it now, Boss. Don't let it wander." }`
The line is resolved in `Main.cs` via `_voiceLineRegistry.GetLine(...)`. That
resolution must either move to the logic layer (so the harness can capture it)
or the enriched event is written by the harness runner reading the resolved text.
Exact wiring is an Analyst Phase 1 decision.

**Memos — not in the event stream.**
Memos are queued into `PersistentState.UnderWarden.PendingMemos` at run end.
No `TurnEvent` fires at delivery time.
Required: either a `MemoDeliveredEvent { Subject, Body }` emitted when a memo is
queued, or PendingMemos included verbatim in `RunSummary`.
Exact wiring is an Analyst Phase 1 decision.

### Forward-compat note for CoherenceEvaluator

The condensed transcript fed to the CoherenceEvaluator (Analyst Phase 3) must
preserve verbatim voice text rather than summarizing it away. The design thread
may route register-checking through the coherence pass. Preserve the option;
the design thread decides.

---

## RunSummary

```jsonc
{
  "record_type": "summary",

  "hp_profile": [
    [1, 1.0], [2, 0.85], [3, 0.71]
    // [floor, player_hp_pct at floor entry]
  ],

  "system_triggers": {
    // Which systems were touched, and on which turn (null if never).
    // Full list defined by rubric SystemTriggerLog spec; minimal set:
    "possession_used": false,
    "possession_first_turn": null,
    "orc_rep_changed": false,
    "orc_rep_change_turn": null,
    "past_sasha_encountered": false,
    "mural_read": true,
    "mural_first_turn": 89,
    "weighing_reached": false,
    "weighing_guardian_allied_count": 0
  },

  // Pending memos as delivered this run (verbatim, for analyst text checks):
  "memos_delivered": [
    {
      "key": "unauthorized_descent",
      "subject": "Regarding Your Continued Presence",
      "body": "..."
    }
  ],

  // LLM Player only — null in bot runs:
  "structural_judgments": [],          // all non-null structural_assessments from TurnRecords
  "run_narrative": null                // end-of-run structural summary from LLM
}
```

---

## Schema Versioning

`schema_version` is on the `TranscriptHeader`. Bump when:
- A field is removed
- A field changes type or semantics
- A new required field is added

Do NOT bump when:
- An optional field with a sensible default is added (null in old records)

The Analyst validates `schema_version` at load time. Unknown future fields are
ignored (forward-compatible). Schema version mismatch for a mandatory field is
a fatal load error with a clear message.

---

## Rubric Dependency

The `system_triggers` key list in `RunSummary` is partially defined by the
rubric's `SystemTriggerLog` spec. The minimal set above is independent of the
rubric and wired in Analyst Phase 1. The rubric may extend it.

The `structural_judgment_schema` vocabulary (used in `structural_assessment.judgment`)
comes from the rubric. The Player system prompt must use this vocabulary exactly.
