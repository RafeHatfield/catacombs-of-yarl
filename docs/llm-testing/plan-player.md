# Plan: LLM Player (Thread 3)

**Status:** Locked. No code written. No-code hold in effect.
**Date locked:** 2026-06-09

## Context

This plan is part of the three-thread LLM testing system. See
`00-overview.md` for the full decomposition. Thread 1 (evaluation rubric) is
design-owned and upstream. This plan covers Thread 3 only.

The LLM Player is the expensive, high-signal instrument. Its unique value is
turn-by-turn reasoning and structural self-report — things the Analyst cannot
do from a bot transcript alone. It plays the game using Claude Haiku, producing
structural self-assessments about decision quality, and emits transcripts in
the same enriched format the Analyst reads (Thread 2's pipeline is the consumer).

---

## Goals

1. Play the game using Claude Haiku to make turn-by-turn decisions.
2. Emit transcripts in the Analyst's enriched format with full action records
   (enabling deterministic replay — see `shared-transcript-schema.md`).
3. Produce structural self-assessments using the rubric vocabulary as first-class
   output, not logging noise.
4. Support exactly two personas: The Reader and The System Explorer.

## Non-Goals

- Affective self-report of any kind — structural and decision-traceable only
- "Fair" as a judgment category — removed; see §5 for rationale
- Optimal play or high win-rate (survival is the means, not the goal)
- Automated feedback loop to the Analyst (shared interface now; loop later)
- Replacing the existing bot harness for volume testing (bots remain the bulk
  instrument; the Player is targeted)

---

## §1. Rubric Dependency

The Player needs exactly one rubric field to start:

```yaml
structural_judgment_schema:
  - dead_action_space    # all available options were equivalent/arbitrary
  - forced_move          # only one action existed
  - novel_encounter      # first time interacting with this entity or mechanic
  - system_unreachable   # mechanic was present but had no accessible entry point
```

This vocabulary is injected into the system prompt so the LLM produces
assessments using defined terms rather than free-form language. The Analyst
reads these terms; they must match exactly. Player Phases 0–3 can build before
any other rubric content lands.

---

## §2. GameStateDescriber

Converts `GameState` to the text description the LLM reasons about. This is the
most critical component for output quality.

### Principles

- Decision-relevant only. No entity IDs, internal state details, tile coordinates.
- Consistent structure. LLM can predict where to find each piece of information.
- Token-lean. Every line must earn its place.
- Persona-aware. The Reader receives verbatim voice text; the Explorer receives
  compressed form.

### Signature

```csharp
public static string Describe(GameState state, LlmPersona persona) → string
// or equivalently:
public static string Describe(GameState state, bool verbatimVoice) → string
```

**This is not a single-mode implementation.** The CONTEXT and FEATURES sections
render differently per persona. This changes Phase 1 scope (see §8).

### Template (base structure, both modes)

```
=== TURN {N} | FLOOR {D} | {HP}/{MAX_HP} HP ({HP_PCT}%) ===

SITUATION
{1–2 sentence spatial summary: where you are, what's immediately visible}

THREATS  (nearest 5, sorted by threat level)
- {species}: {distance} tiles {direction}, {threat_level: low/med/high}

ITEMS ON FLOOR  (nearest 3)
- {item_type} at {distance} tiles {direction}

FEATURES
{persona-aware rendering — see below}

RECENT EVENTS (last 3 turns)
- T{N-2}: {1-line summary}
- T{N-1}: {1-line summary}
- T{N}:   {1-line summary}

{CONTEXT BLOCK — persona-aware rendering; omit if nothing relevant}

AVAILABLE ACTIONS
1. {action description}
2. {action description}
...

{PERSONA INSTRUCTION — see §3}
```

### Persona-aware rendering

**The Reader (verbatim voice mode):**

CONTEXT block:
```
Hollowmark (turn 89): "Boss. Don't read it aloud. He doesn't know we saw."
```
The actual fired line, verbatim, attributed to the turn it fired. Not a paraphrase.

FEATURES block (mural/sign present):
```
MURAL (north wall): "A woman's name, in a careful hand, carved between the
standard Warden inscriptions. Below it, a date eighty years past. Below that,
in smaller script, in the same hand: 'I did not ask. I am not asking.'"
```
Actual mural text verbatim, not "Ancient inscription (readable)".

**Rationale:** The Reader's evaluative value is detecting whether the writing
lands — whether register variation is functional, whether voice-bearing content
creates actionable choices. A paraphrase launders out exactly that signal.
Compressing Hollowmark's lines to one-sentence summaries makes The Reader grade
the describer's prose, not the game's prose.

**The System Explorer (compressed mode):**

CONTEXT block:
```
Hollowmark: commented on the mural (turn 89, floor 4)
```

FEATURES block:
```
- Mural: Ancient inscription (readable)
```

No surcharge for the Explorer. Murals are interaction-surface signals, not text
signals, for this persona.

### Token budget

- Base (both modes): 600–800 tokens
- Reader surcharge on floors with Hollowmark/mural: +100–400 tokens
- Hard ceiling for verbatim blocks: 500 tokens, truncated with `[...]` if exceeded
- Empirical calibration in Phase 5 against real run data

---

## §3. Persona System

Two personas on a voice-engagement axis. Expressed as the `PERSONA INSTRUCTION`
section of every state description. The base description is shared.

### The Reader

```
PERSONA: The Reader

Your priority is engaging with the game's narrative. Read signs, murals, and all
Hollowmark lines. Honor relationships: if you made a commitment to the orcs,
honor it. Decide based on story logic, not expected value. Play as if choices
have consequences beyond the mechanical — because in this game, they do.

You receive Hollowmark's actual words and actual mural/sign text verbatim. Read
them. They are the primary signal for your structural assessment: when the
writing is present and decision-relevant, your job is to notice whether it could
actually influence a choice, or whether it arrived with no corresponding action
surface.

When making a structural assessment, focus on: was narrative information present
but impossible to act on? Did a story beat occur without giving you a choice?
```

### The System Explorer

```
PERSONA: The System Explorer

Your priority is triggering mechanics you haven't seen yet. Use possession when
you haven't tried it recently. Engage the orc faction. Try throwing items. Use
wands. Explore features. You are mapping the game's interaction surface, not
optimizing survival. Survive long enough to see more, but don't play
conservatively if it means missing a system.

When making a structural assessment, focus on: was this mechanic accessible but
opaque? Was the interaction surface clear or hidden? Did you find yourself
reaching for a mechanic and unable to access it?
```

---

## §4. LlmBotBrain

Implements the bot brain interface. Calls Haiku API, parses structured output,
logs full action details, falls back gracefully on failure.

### Structured output schema

```jsonc
{
  "action_index": 3,
  "action_label": "Move north toward the staircase",
  "reasoning": "The orc is already dead; the stair is my best path forward.",
  "structural_assessment": {
    "judgment": "forced_move",
    "note": "Only the move action was available; combat was resolved."
  }
}
// structural_assessment is null when no assessment is warranted (most turns)
```

### Structural assessment trigger (in system prompt)

```
Produce a structural_assessment only when:
- available_action_count was 1 (forced_move)
- All available actions had equivalent expected outcomes (dead_action_space)
- You encountered an entity or mechanic for the first time (novel_encounter)
- A mechanic was present but you had no clear way to interact with it (system_unreachable)

Otherwise, structural_assessment is null. Assessment vocabulary must exactly
match: {structural_judgment_schema from rubric}.
```

### Safety fallback

On API error, timeout (>10s), or parse failure: take the default balanced-bot
decision for that turn. Log the fallback as a `FallbackEvent` in the transcript.
The run never soft-locks due to API issues.

### System prompt caching

Static sections (game rules, structural judgment vocabulary, output format,
persona instruction) — ~2650 tokens total — are cacheable. Per-turn state
description — ~700 tokens — is non-cacheable. Effective per-turn input with
Haiku caching: ~965 tokens.

### Cost estimate

- ~$1.00 per 1000-turn run (25-floor game)
- Reader persona: +$0.10–0.40 on floors with Hollowmark/murals (verbatim surcharge)
- 50 runs/day: ~$50–60/day sustained

---

## §5. Self-Assessment Hooks

**Structural only. No affective vocabulary. No "fair".**

"Fair" is an affective judgment that a no-stakes agent will confabulate,
especially on death (the highest-affect moment). "Traceable-to-a-decision" and
"arrived-without-a-decision-point" are structural facts verifiable against the
transcript. The hook vocabulary is chosen accordingly.

### Per-turn (conditional)

Standard output schema always includes `structural_assessment` (null when not
warranted). The system prompt instructs on when to populate it. No additional
API call; this is part of the standard turn response.

### Per-floor hook

On descent event, insert before the next turn's state description:

```
FLOOR {D-1} COMPLETE — briefly answer before acting:
- Primary interaction type this floor (move / fight / explore / use-system):
- Interesting decisions made (count + 1-sentence description, or "none"):
- Systems encountered for the first time:
```

Captured as a `floor_summary` entry in `RunSummary.structural_judgments`.
Adds ~50 tokens to that turn's output.

### Per-significant-event hooks

Each event appends a brief reflection prompt to the state description for that
turn (~100 tokens). Defined event list (configurable in YAML):

**Near-death** (`player_hp_pct < 0.2`):
```
REFLECTION (near-death):
Was this expected given the decisions you made in the last 5 turns,
or did it arrive from a direction you had no way to anticipate?
(expected | unexpected-but-navigable | arrived-without-decision-point)
```

**First possession use:**
```
REFLECTION (first possession):
Was the entry point into this mechanic clear, or did you discover it
by accident or from text rather than from mechanical affordance?
(clear-affordance | discovered-via-text | found-by-accident | system-unreachable-until-now)
```

**First orc interaction:**
```
REFLECTION (first orc interaction):
Was the decision surface here clear — did you understand what was at stake
and what your options were?
(clear | opaque | no-real-choice)
```

**Death:**
```
REFLECTION (death):
Can you trace this death to a specific earlier decision you could have
played differently? Or did it arrive with no decision point you could
have acted on?

If traceable: which turn and action?
If not traceable: describe the moment it became unavoidable.

(traceable-to-decision | arrived-without-decision-point)
```

**Mural read (Reader persona only):**
```
REFLECTION (mural):
Was the content of this mural decision-relevant — did it create or
foreclose an option you could act on? Or was it atmospheric only?
(decision-relevant | atmospheric | unclear-how-to-act)
```

### End-of-run summary (one additional API call after run ends)

```
You just completed a run (ending: {ending}). In 3–5 sentences:
1. What was the structural character of this run? (Were decisions alive or
   mostly forced?)
2. What systems were present but had no accessible entry point?
3. Did your choices accumulate into a coherent story?

Use the structural_judgment vocabulary: {schema list}.
Do not use the word "fair" or describe outcomes as frustrating, satisfying,
or surprising. Structural observations only.
```

Output → `RunSummary.run_narrative`. Highest-signal item in the transcript for
the Analyst's coherence pass.

---

## §6. Transcript Emission

The Player emits transcripts in the enriched format defined in
`shared-transcript-schema.md`. It populates the LLM-specific fields bots leave null:

- `TurnRecord.decision_context`: the `reasoning` field from structured output
- `TurnRecord.structural_assessment`: when not null
- `RunSummary.structural_judgments`: all non-null structural assessments with turn refs
- `RunSummary.run_narrative`: end-of-run summary

The full `action_taken` object (not a bare ActionKind string) is emitted for
every turn, enabling deterministic replay.

### Replay guarantee

Given `TranscriptHeader.seed` and the sequence of `action_taken` objects, the
exact game state at any turn is reproducible. The LLM's non-determinism is
irrelevant — replay re-feeds recorded actions rather than re-deciding them. Any
bug found in an LLM Player run can be isolated and reproduced against the same
seed without the LLM present.

---

## §7. Configuration

```yaml
# config/llm_player/reader.yaml
persona: reader                    # "reader" | "system_explorer"
model: claude-haiku-4-5
max_turns: 1500                    # safety limit
fallback_persona: balanced         # on API errors: use this bot persona for the turn
structural_assessment_threshold: 1 # available_action_count ≤ threshold auto-flags forced_move
significant_event_hooks:
  - near_death
  - first_possession
  - death
  - first_orc_interaction
  - mural_read                     # Reader only; filtered by persona in hook logic
run_seed: null                     # null = random game RNG; LLM decisions always non-deterministic
```

---

## §8. Implementation Phases

| Phase | Sessions | Description |
|-------|----------|-------------|
| **0: Interface alignment** | 0.5 | Finalize enriched transcript schema with Analyst plan. Agree on `structural_judgment_schema` vocabulary. Write v1 system prompt draft for both personas. No code. |
| **1: GameStateDescriber** | 1.5 | **Expanded from initial estimate (was 1 session) due to persona-aware verbatim mode.** Pure logic, no API. Two rendering modes: verbatim-voice (Reader) and compressed (System Explorer). Signature takes persona. Tests: base token budget <850 for both modes; verbatim surcharge measured against real GameState snapshots with Hollowmark lines; mural text rendered verbatim for Reader, compressed for Explorer; hard ceiling (500 tokens) enforced on verbatim blocks. |
| **2: LlmBotBrain core** | 1 | API integration. Structured output including full `action_taken` serialization. Safety fallback. Single-turn test: known state → valid PlayerAction with full parameters; validate parse; validate fallback fires on injected failure. |
| **3: Harness integration** | 1 | Wire into harness (`--player llm --persona reader`). Transcript emission with full action records. Validate: complete run; transcript passes Analyst schema validation; replay of action sequence against seed reproduces floor state at turn 50. |
| **4: Self-assessment hooks** | 1 | Per-turn structural assessments (no "fair" anywhere), per-floor hook, event hooks with death-traceability prompt, end-of-run summary. Validate: death reflection produces only `traceable-to-decision` or `arrived-without-decision-point`; hooks fire at correct triggers; vocabulary matches `structural_judgment_schema`. |
| **5: Persona calibration** | 1 | Run Reader and System Explorer on same seeds. Confirm: Reader receives verbatim Hollowmark/mural; Explorer receives compressed. Transcripts differ measurably in structural judgment distribution. Tune system prompts against empirical output. |

**Total to useful v1:** ~6 sessions.
**Sequencing dependency:** wait for Analyst Phase 1 before Player Phase 3, so
the Player targets a validated transcript format.

---

## §9. Open Issues

**Reproducibility (resolved):** Deterministic replay from transcript + seed is
the design. Entity IDs are deterministic within a seeded run; the full
`action_taken` field provides what's needed. Verify in Analyst Phase 1 rather
than trusting the assumption.

**Per-floor hook timing:** The hook fires before the next turn's decision, but
the descent event fires at the end of the previous turn. Needs a one-turn delay
mechanism or a pre-turn hook site in the harness event loop. Design decision
deferred to implementation.

**Mural text availability in GameState:** The describer needs mural/sign text
for features in the LOS range. Confirm at Phase 1 that this is accessible from
the feature entity's `MuralComponent`/`SignpostComponent` at the time of
description. If it requires registry lookup, the describer needs the registries
at construction time.

**Verbatim surcharge calibration:** The 100–400 token estimate is approximate.
Measure against real snapshots in Phase 1 against actual Hollowmark line lengths
and mural text density by floor band.
