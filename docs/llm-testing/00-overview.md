# LLM Testing System — Overview

**Status:** Both plans locked. **Analyst Phases 0–2 + 4 COMPLETE** (2026-06-09): transcript
enrichment, Phase-1 cross-check, BugDetector (predicate mechanism) + single-run report, and the
**batch pipeline (BatchAnalyzer + AggregateReport + findings.md)**. All four RUNNABLE-NOW
predicates demonstrated firing on engineered violation fixtures; the audit trail (turns evaluated
per category) survives aggregation; 0× mechanism triggers route as UNVERIFIED blind spots, never
"broken". `text_pattern` / `llm_judged` / `trigger_consequence` recognized by dispatch and
log-and-skip. **Phase 3 (coherence) intentionally skipped** — needs `coherence_dimensions`; the
aggregate carries an N/A slot for it (not faked). `trigger_consequence` evaluator unbuilt (needs
evaluator + the four open contracts).
**Rubric landed:** `config/rubric/v1.yaml` + `config/rubric/silent-failure-inventory.md`.
**Tool:** `tools/Analyst/` — single: `--transcript <jsonl> --rubric config/rubric/v1.yaml [--report <json>]`; batch: `--batch <dir> --rubric config/rubric/v1.yaml [--aggregate findings.md] [--aggregate-json <json>] [--concurrency N]`.
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

Findings on mechanical triggers — status as of 2026-06-11 (after Weighing instrumentation):

- **AggravatedEffect / TargetFaction — captured, but parameter-incomplete.** Application
  is NOT stranded in presentation: it fires a `SpellEvent` in the logic event stream with
  `StatusApplied="aggravated"` (`SpellResolver.ResolveAggravation`). However, the
  `TargetFaction` VALUE (e.g. "orc") is NOT on the event. A window-check detector
  ("aggravated → expect faction-change within 2 turns") needs that faction to know what to
  watch — so the trigger is greppable but the parameter is missing. **Deeper gap:** the
  *consequence* side is itself unimplemented — `BasicMonsterAI.ChooseTarget` does not yet
  consult `TargetFaction` (see `AggravatedEffect.cs` doc + `migration_loss_audit.md`), so
  no faction-change event can ever fire. That detector would always flag until both are wired.
- **Orc reputation changes — WIRED (2026-06-11).** `OrcRepChangedEvent` now fires at the
  kill turn where the orc tally crosses `HostileThreshold`, predicting the run-end mutation.
  `RunSummary.OrcRepChanged`/`OrcRepChangeTurn` are now set by the transcript recorder.
  Implementation note: the event fires from `ResolvePlayerAttack` (before `TransformToCorpse`
  strips `AiComponent`) using a peek count. Verified by `OrcRepChangedEvent_FiresAtThresholdTurn`.
  Pre-existing gap discovered and noted: `UpdateKnowledge` was recording orc kills under
  faction `"neutral"` (because `AiComponent` is stripped before `UpdateKnowledge` runs) — this
  is a bug in the tally accuracy, separate from the instrumentation, and not fixed here.
- **Weighing guardian tier resolution — WIRED (2026-06-11).** `GuardianTierResolvedEvent` now
  fires for all four faction Guardians on `BeginFromPersistence`, carrying BOTH the resolved
  tier AND the raw input metrics the scorer read (independence invariant). The `WeighingResolvedEvent`
  now carries the full audit record + aggregate inputs. `RunSummary.weighing_guardian_allied_count`
  is still not wired (would require counting allies through the Weighing gauntlet, which the bot
  harness never reaches; deferred).
- **Weighing guardian allied count — not reachable by bot harness.** Lives in endgame
  (floor-25 Weighing) state the bot never reaches; `weighing_guardian_allied_count` stays 0.
  Wiring deferred until scripted Weighing scenarios exist.
- **Possession / mural / past-Sasha / Weighing-reached — wired and working.** Derived from
  `PossessionEnteredEvent`, `MuralExaminedEvent`, `VoiceLineEvent` (`past_sasha*` prefix),
  and `WeighingDialogueEvent` respectively. (Bot runs rarely trip these — see voice note above.)

The `RunSummary.system_triggers` set is **provisional-pending-rubric**: the minimal set is
wired; the rubric may extend it.

---

## Weighing Instrumentation — event set (2026-06-11)

These events are now in the logic-layer event stream, captured by `TurnEventJsonConverter`
automatically (the open seam). They only fire in runs that REACH the Weighing (floor 25).

**What currently reaches the Weighing:**
- The test suite: `tests/Endgame/Weighing*Tests.cs` drives `WeighingOrchestrator.Begin()` and
  `BeginFromPersistence()` directly, with a real `WeighingArenaDefinition`. 11 instrumentation
  tests confirm all three events fire with correct data.
- **The bot harness NEVER reaches the Weighing.** `DungeonRunHarness` caps at configurable
  floors (default 10, never 25). These events are therefore `scope: scripted/endgame` — the
  `guardian_tier_correctness` detector and `ending_resolved` detector only fire on scripted runs
  that drive to floor 25, not organic bot batches. This is the **necessary-but-not-sufficient**
  flag from the task: instrumented ≠ exercised at scale.

**New events:**

| event | fires when | key fields | verified |
|---|---|---|---|
| `GuardianTierResolvedEvent` | `BeginFromPersistence()` — 4×, once per Guardian | `Guardian`, `Tier`, `WasScored`, plus raw scorer inputs per-guardian (`OrcRepState`, `UnprovokedOrcKillsThisRun`, etc.) | ✅ inputs match scorer independently |
| `WeighingResolvedEvent` (enhanced) | `Resolve()` — on any Weighing end | `Ending`, all 4 tiers, `AnySavage`, `IsHeavyRecord`, `OrcRepState`, `CumulativeDeaths`, `SwapChosen`/`SwapAvailable` | ✅ all 6 endings verified |
| `OrcRepChangedEvent` | kill turn where orc tally crosses `HostileThreshold` | `FactionId="orc"`, `ToState="hostile"`, `KillsThisRun` | ✅ fires at correct turn, not before |

**Independence invariant verified:** capturing the inputs before `AuditScorer.Score()` runs and
recording them alongside the tier means a detector can re-run the scorer from the captured inputs
and compare — an event that merely echoes the scorer's output would not enable this.

**Endgame scope note for detectors:** `guardian_tier_correctness` and `ending_resolved`
predicates should be tagged `scope: scripted` in the rubric, not `scope: runtime`. A standard
bot run will never contain these events; looking for them in a bot-batch report will always be
zero, which is healthy-unexercised not clean. The `trigger_consequence` detector for
`possession_ability_grant` and `faction_turning` have the same profile.

---

## Phase-1 Cross-Check vs Rubric v1 (2026-06-09)

Reconciles `config/rubric/v1.yaml` (RUNNABLE-NOW predicates) and
`config/rubric/silent-failure-inventory.md` (the `trigger_consequence` punch list) against
what the transcript actually captures. This is the CC half of the cross-check the inventory
asks for.

### RUNNABLE-NOW predicates — ALL FOUR now executable ✅

The four `predicate`-mechanism categories reference five per-turn fields that did not exist
in the Phase-0/1 transcript. All are now captured as top-level `TurnRecord` fields (post-action),
verified by `TurnRecord_CarriesRubricV1PredicateFields`:

| predicate | fields it reads | status |
|---|---|---|
| `soft_lock` | `available_action_count`, `is_game_over` | ✅ both present |
| `hp_out_of_range` | `player_hp_pct` | ✅ (already present) |
| `aggression_tally_negative` | `run_aggression_tally` | ✅ added (`RunAggressionTally.Total()`) |
| `possession_body_inconsistent` | `possession_active`, `controlled_entity_id`, `player_entity_id` | ✅ added; `possession_active` derived from the PossessionEffect's existence, NOT from `ControlledEntity`, so the predicate is non-circular |

`value_reconciliation` (`aggression_tally_increment`): `RunSummary.run_aggression_tally`
(final) is added. Confirmed per the inventory note — **no per-increment event is needed**;
the analyst reconstructs the expected count from qualifying-act events and compares.
**Remaining gap:** the qualifying acts (unprovoked cross-faction kills) are not yet
classifiable from the stream — `DeathEvent` carries killer/victim ids but not the
victim faction or the "unprovoked" flag the tally keys on. Reconstruction needs those
attributes on the kill event (or a marker), AND the exact qualifying-act list is itself an
open contract. Report only; not wired.

### `trigger_consequence` detectors — punch list reconciled

The `trigger_consequence` evaluator does NOT exist in v1 (it is a later mechanism), so none
of these run yet. The cross-check is about whether the TRIGGER and CONSEQUENCE events are in
the stream when it is built:

| detector | trigger event | consequence event | gap |
|---|---|---|---|
| `faction_turning` | `SpellEvent`(aggravated) — present but **missing `TargetFaction` value** | **faction-change event — does not exist anywhere** | trigger needs the faction param; consequence event must be defined (coupled to the faction-turning fix) |
| `possession_ability_grant` | `PossessionEnteredEvent` ✅ | ability-set-granted event — **none found** (grant is silent on possession) | needs a grant event |
| `orc_rep_threshold` | **no event** (orc-rep change is fully stranded) | **no event** | needs both trigger + consequence events |
| `memo_escalation` | escalation condition — n/a | `MemoDeliveredEvent` — **not added** | memos deliver as an END-OF-RUN BATCH, captured in `RunSummary.memos_delivered`; a windowed per-turn check needs the memo system to deliver per-turn AND a `MemoDeliveredEvent`. That is a design decision (when do memos deliver?), not just an event class. Left for the design thread + the evaluator |
| `guardian_rose_with_no_tier` / `guardian_tier_correctness` | Weighing rise | assigned-tier as a **structured field** + **tier table as readable config** | endgame; bot never reaches; deferred |
| `savage_warden_curse`, `corrosion_easter_egg` | scoped `[scripted]` | — | need scripted scenarios, not organic bot runs; out of scope |

**Net:** the predicate spine is fully unblocked for Phase 2. The `trigger_consequence` spine
needs new mechanical EVENTS before its evaluator can be built — chiefly a **faction-change
event**, an **orc-rep stance-change event**, a **possession ability-grant event**, and a
decision on **per-turn memo delivery + `MemoDeliveredEvent`**. None are wired this session
(they need the evaluator and, in several cases, the open contracts below).

### Open contracts — still need Rafe's input (from the inventory)

These block writing the corresponding detectors; do not infer them:
1. **Orc geas** — what state is set on commitment, what enforces it, what is the break consequence?
2. **Past-Sasha** — mechanical payload of an encounter, or purely narrative? (If narrative, it leaves silent_failure for coherence/voice.)
3. **Assembly tier** — what metric does the Assembly key on at the Weighing?
4. **The Debt** — metric-scaled, or an unscaled claim (`direction: n/a`)?

---

## Analyst Phase 2 — BugDetector + single-run report (COMPLETE, 2026-06-09)

Pure tooling in `tools/Analyst/` — no game-logic changes. Components:
- `TranscriptLoader` — reads enriched JSONL as generic JSON, lifts top-level scalar fields into
  a name→value map (forward-compatible; new scalar fields auto-available). Schema-version
  mismatch on a mandatory field is fatal.
- `RubricLoader` — loads `v1.yaml`, validates strictly. Missing mechanism, unknown mechanism,
  missing predicate, malformed predicate, schema mismatch are ALL fatal at load — never a silent
  never-fire. Unknown top-level keys (coherence_dimensions, coverage_semantics) ignored gracefully.
- `PredicateExpression` — self-contained parser/evaluator for the rubric's expression language
  (`and`/`or`/`not`, `== != < <= > >=`, identifiers, literals, parens). Parsed once at load.
- `BugDetector` — dispatches on `mechanism`, NOT category name (Constraint A). `predicate`
  implemented; `text_pattern` / `llm_judged` / `trigger_consequence` recognized and log-and-skip.
- `EvaluationReport` — per-run JSON: bug_candidates, **predicate_coverage** (turns evaluated +
  hits per category), **skipped_mechanisms** (what didn't run and why), system_coverage echo,
  deterministic analyst_note. Coherence empty (Phase 3), structural_summary null (bot runs).

### Acceptance gate — each predicate demonstrated FIRING (not just "clean")

Per the gate (a never-fired check is indistinguishable from a cannot-fire check), each of the
four RUNNABLE-NOW predicates has a permanent violation-fixture regression test
(`tests/Balance/AnalystBugDetectorTests.cs`) proving it fires, plus end-to-end CLI confirmation:

| predicate | violation that fires it | evidence snippet |
|---|---|---|
| `soft_lock` | `available_action_count=0, is_game_over=false` | `available_action_count=0, is_game_over=false at turn 42` |
| `hp_out_of_range` | `player_hp_pct=1.4` (and `-0.2`) | `player_hp_pct=1.4 at turn 42` |
| `aggression_tally_negative` | `run_aggression_tally=-2` | `run_aggression_tally=-2 at turn 42` |
| `possession_body_inconsistent` | `possession_active=true, controlled_entity_id==player_entity_id==0` | `possession_active=true, controlled_entity_id=0, player_entity_id=0 at turn 42` |

Each fixture also includes CLEAN turns that must NOT fire (specificity). Two further gate tests:
a complete clean transcript yields 0 candidates with all four categories shown evaluated; a
transcript MISSING a predicate's field surfaces that category as a SKIP (with reason), never as a
clean pass. Real bot run (seed 1337, 2403 turns): 0 candidates, all four categories evaluated
2403× — auditably clean. 21 Analyst tests green; full fast suite 2132 green.

### EvaluationReport shape (real transcript)

```jsonc
{
  "run_id": "...", "persona": "balanced", "player_type": "bot", "replay_available": true,
  "bug_candidates": [ /* { turn, category, mechanism, description, evidence_snippet } */ ],
  "predicate_coverage": [ { "category": "soft_lock", "turns_evaluated": 2403, "candidates_found": 0 }, ... ],
  "skipped_mechanisms": [ /* { category, mechanism, reason } — empty when all categories ran */ ],
  "coherence": {},                         // Phase 3
  "system_coverage": { /* RunSummary.system_triggers echoed */ },
  "structural_summary": null,              // LLM Player runs only
  "analyst_note": "Predicate scan: 4 predicate categories evaluated across 2403 turns; 0 bug candidates. No categories skipped."
}
```

### NUnit pin (incidental)

Referencing the Analyst project from the test project triggered a restore that floated NUnit
`4.*` from 4.5.1 → 4.6.1; 4.6.1's new Func/Action assertion overloads make the suite's existing
lambda-based `Assert.That`/`DoesNotThrow`/`Throws` calls ambiguous. Pinned NUnit to `4.5.1` (the
version the suite was written against) rather than churn 30+ pre-existing files. Migrating those
call sites to disambiguate is a separate cleanup if we later want to unpin.

### Stop line

Stopped before the coherence pass (Phase 3 — needs full rubric `coherence_dimensions`) and
before any `trigger_consequence` work (needs the evaluator + the open contracts above).

---

## Analyst Phase 4 — batch pipeline (COMPLETE, 2026-06-09)

`BatchAnalyzer` evaluates a directory of transcripts in parallel (shared reentrant `BugDetector`;
one bad file is recorded as a load failure and never aborts the batch) → `AggregateReport`
(JSON) + `findings.md`. Deterministic regardless of concurrency (results sorted by run_id).
CLI: `--batch <dir> --rubric config/rubric/v1.yaml [--aggregate findings.md] [--aggregate-json <json>] [--concurrency N]`.

### Standing invariant: silence travels with its ran-count

The per-run audit trail (predicate_coverage + skipped_mechanisms) is rolled up, NOT discarded.
The aggregate reports, per predicate category: **total turns evaluated across the batch**, **runs
ran**, **runs skipped**. "0 candidates across 50 runs" is always accompanied by "each category
evaluated N total times, K skipped" — so silent-clean cannot re-emerge at the aggregate level.
A run missing a predicate's field rolls up as a SKIP with its reason, never as a clean pass.

### Heatmap = neutral data + semantic interpretation

The system-trigger heatmap is emitted as raw per-trigger fire rates (% of runs that fired each) —
no judgment baked in. `coverage_semantics` (v1.yaml, zero-threshold model) is then applied:
- **CONTENT** triggers (mural_read…): any rate incl. zero is fine — never flagged.
- **MECHANISM** triggers: low-but-nonzero is coherent playstyle; **0× across the batch =
  UNVERIFIED**, surfaced as a blind spot that **ROUTES, not concludes**: "exercise with a
  targeted/scripted run (or LLM persona); if the consequence fires it's healthy-but-unexercised,
  if not it's dead. 0× from a bot batch does NOT mean broken."
- Classification bridges the rubric's detector-named examples (possession_ability_grant) to the
  transcript's system_triggers keys (possession_used) by stem; unmatched → `unclassified`,
  reported neutrally. (This naming bridge is a seam to tighten as the rubric classification completes.)

### The blind-spot list IS the value (real 50-run bot batch)

On a real 50-run bot batch: 0 bug candidates, every predicate category evaluated **82,442 turns
across 50 runs, 0 skipped** (auditably clean). Mechanism blind spots at 0×: **`possession_used`**
and **`orc_rep_changed`** — the canonical cases. This list = the things the bulk (bot) instrument
never exercises (sub-shape B made visible in aggregate). possession is the canonical example —
voice lines are possession-gated and bots never possess, so that whole surface is a known blind
spot. This feeds the scripted-scenario backlog and the case for the LLM personas. Content
(`mural_read`, 0×) and unclassified (`past_sasha_encountered`, `weighing_reached`) are NOT flagged.

### Smaller decisions

- **Bug-candidate confidence:** reported as "appeared in N of M runs" (frequency, human-judgeable),
  not a synthesized score. Resolves the plan's open issue.
- **LLM-Player-only fields** (structural_judgment frequency) + **coherence**: present-but-N/A slots
  in the aggregate, built for slot-in, NOT faked.

### AggregateReport shape (real bot batch)

```jsonc
{
  "batch_dir": "...", "runs_evaluated": 50, "runs_failed_to_load": 0, "failed_files": [],
  "bug_candidates": [ /* { category, mechanism, description, runs_with_candidate, total_runs, total_instances, example_evidence } */ ],
  "predicate_coverage": [ { "category": "soft_lock", "total_turns_evaluated": 82442, "runs_evaluated": 50, "runs_skipped": 0, "total_candidates": 0 }, ... ],
  "skipped_mechanisms": [ /* { category, mechanism, runs_skipped, reasons[] } */ ],
  "system_trigger_heatmap": [ { "trigger": "possession_used", "fired_in_runs": 0, "total_runs": 50, "fire_rate": 0.0, "trigger_class": "mechanism" }, ... ],
  "mechanism_blind_spots": [ { "trigger": "possession_used", "route": "unverified — exercise … 0× from a bot batch does NOT mean broken." }, ... ],
  "coherence_status": "N/A — coherence pass not run (rubric coherence_dimensions empty; Analyst Phase 3).",
  "structural_judgment_status": "N/A — bot-only batch (structural judgments are emitted by LLM Player runs).",
  "note": "50 runs evaluated; 0 bug candidate instances …; 4 predicate categories in the audit trail, none skipped; 2 mechanism blind-spots (0× — unverified)."
}
```

### Stop line (Phase 4)

No coherence pass (needs `coherence_dimensions`); no `trigger_consequence` work (needs the
evaluator + the four open contracts). The NUnit 4.5.1 pin (added in Phase 2, reason inline at the
pin site) was not touched — Phase 4 added no project references or shared-config changes.

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
