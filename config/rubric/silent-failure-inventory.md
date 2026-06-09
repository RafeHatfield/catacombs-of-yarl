# Silent-Failure Inventory — Rubric Design Record (Thread 1)

**Status:** Working design record. **NOT loaded by the Analyst.**
**Last updated:** 2026-06-09

---

## What this is

The `silent_failure` detector spec. These detectors use a **`trigger_consequence`**
mechanism that **v1's BugDetector does not implement** — v1 ships `predicate`
only, with `text_pattern` and `llm_judged` stubbed in the dispatcher.
`trigger_consequence` is a fourth mechanism that must be built (the Analyst
"mechanism expansion" phase) before anything here can run.

So this file does two jobs:

1. It is the **spec for the `trigger_consequence` evaluator** when CC builds it.
2. It is the **design-thread half of the Phase-1 cross-check**: the trigger
   events below must be present in the transcript, and that list reconciles
   against the stranded-mechanical-events list CC returns from its capture
   investigation.

**Do NOT paste these entries into `v1.yaml`.** An unknown `mechanism` is a fatal
load error by design.

---

## Why silent_failure is not a predicate

The v1 predicate checks test **present** state (HP outside [0,1], zero actions)
by reading one TurnRecord. Silent failure is the inverse: an event that **should
be present is missing**. "A faction flip should have followed that aggravated
attack" is a fact about a line that is *absent*, not about any line present.
That is a trigger → consequence → window shape, not a single predicate.

---

## Two sub-shapes (this is why faction-turning slipped)

- **Sub-shape A — trigger fired, consequence didn't.** It's in the transcript;
  the Analyst catches it. `scope: runtime`.
- **Sub-shape B — trigger never fired at all.** Invisible to every transcript —
  a thousand runs that never trip the trigger all look fine. Needs an instrument
  **outside** the Analyst: a static "is this field consumed anywhere" lint (no
  run required) and/or a scripted scenario that deliberately fires the trigger
  on the deterministic harness. `scope: static` / `scope: scripted`.

Faction-turning was **both**: consumption was dead *and* nothing exercised it.
The System Explorer raises the *probability* of tripping unknown systems but
cannot *guarantee* a named one — for a known-unknown, the reliable tool is a
scripted scenario, not the LLM.

---

## Detection styles

- **event_absence** — the consequence event should be in the stream; flag if
  missing. Needs the **consequence** event captured.
- **value_reconciliation** — reconstruct an expected value from qualifying acts
  already in the transcript and compare to a final tally. Needs the
  **qualifying-act** events plus the final value, and explicitly does **not**
  want a per-increment event cluttering the stream.

---

## Live detectors (`trigger_consequence` — pending the evaluator)

```yaml
silent_failure:
  mechanism: trigger_consequence
  detectors:

    faction_turning:
      detection: event_absence
      trigger:     "AggravatedEffect applied with non-null TargetFaction"
      consequence: "faction-change event for the affected entity"
      window: 2                      # turns
      scope: [runtime, static]       # static = is TargetFaction consumed anywhere
      status: known_dead             # restoring; consequence event TBD (see contracts)

    savage_warden_curse:
      detection: event_absence
      trigger:     "Warden defeated at Savage tier"
      consequence: "lingering-curse applied to next ally"
      window: 1
      scope: [scripted]              # Savage defeat too rare to trust organic absence
      status: recently_restored      # Option C — highest regression risk on the board

    possession_ability_grant:
      detection: event_absence
      trigger:     "possession entered"
      consequence: "possessed ability set granted"
      window: 1
      scope: [runtime]

    orc_rep_threshold:
      detection: event_absence
      trigger:     "orc reputation crosses a stance threshold"
      consequence: "stance-change event"
      window: 1
      scope: [runtime]

    memo_escalation:
      detection: event_absence
      trigger:     "memo escalation condition met"
      consequence: "next memo delivered"
      window: 1
      scope: [runtime]
      blocked_on: "MemoDeliveredEvent does not yet exist (CC current session)"

    corrosion_easter_egg:
      detection: event_absence
      trigger:     "slime-acid-troll combination occurs"
      consequence: "acid-buff applied"
      window: 1
      scope: [scripted]              # specific combo, won't occur organically
      note: "also the surface for the corrosion-penalty-vs-acid-buff tradeoff"

    aggression_tally_increment:
      detection: value_reconciliation
      trigger:   "qualifying aggression act"     # EXACT LIST TBD — see contracts
      reconcile: "count(qualifying_acts) == RunAggressionTally"   # final from RunSummary
      scope: [runtime]
      note: "deliberately NO per-increment event — reconstruct expected from acts"

    guardian_rose_with_no_tier:
      detection: event_absence
      trigger:     "Guardian rises at the Weighing"
      consequence: "a tier is assigned to that Guardian"
      window: 0
      scope: [runtime]
      note: >
        This owns ONLY the missing-tier case. Wrong-tier is a predicate
        (guardian_tier_correctness, in v1.yaml). Unearned-tier is coherence.
```

---

## `known_inert` — dormancy is not failure

A write-only-never-read field is the faction-turning **signature**, so a static
lint *will* flag these — and it must not. The rule: an unread field flags as
`silent_failure` **unless whitelisted**, and whitelisting is a **design act with
a reason string**. This draws the silent-*failure* vs silent-*dormancy* line in
config. It is also the cleanest demonstration of why this category is
design-owned: the identical static signal is a bug for faction-turning and a
feature for DEBT-014, and only design knows which.

```yaml
known_inert:
  - field: CumulativeUnprovokedKills
    reason: "DEBT-014 — parked Under-Warden career-cruelty hook. Inert by design."
```

(Consumed by the **static lint** of sub-shape B, not by the runtime Analyst —
which is why it lives here, not in `v1.yaml`.)

---

## Open contracts — NEED RAFE'S INPUT before these rows can be written

A detector built on a guessed contract is itself a named-capability-that-
silently-doesn't-work. So these stay unwritten until the contract is known.

1. **Orc geas.** When a commitment is made, what state is set, and what is
   *supposed* to enforce it / what is the consequence of breaking it?
   (Suspected set-never-read — the faction-turning shape — but the intended
   contract is needed to know what "should have fired" means.)
2. **Past-Sasha.** What is the mechanical payload of an encounter — a choice, a
   stat effect, a memory unlock, dialogue only? If purely narrative, it **leaves
   this category** for coherence / voice.
3. **Assembly tier.** What metric does the Assembly key on at the Weighing?
   (Needed to complete `guardian_tier_correctness`.)
4. **The Debt.** Is it metric-scaled at all, or does it rise as an unscaled
   *claim* regardless of play? The narrative framing suggests `direction: n/a`
   may be the actual contract rather than a gap — confirm, don't infer.

---

## Phase-1 cross-check punch list (reconcile against CC's capture report)

When CC returns the stranded-mechanical-events list from its current session,
cross-check it against the triggers above. Known items:

- **MemoDeliveredEvent** — `memo_escalation` is hard-blocked until it exists.
  In flight in CC's current session.
- **Faction consequence event** — may not exist anywhere. **Defining it is part
  of fixing faction-turning** — the detector and the fix are coupled.
- **AggravatedEffect-with-TargetFaction as a TurnEvent** — confirm it reaches
  the stream (the *trigger* side of `faction_turning`). If stranded in
  presentation like `VoiceLineEvent` was, that's a gap.
- **Tier table as readable config** + **assigned-tier as a structured transcript
  field** — both needed for `guardian_tier_correctness` (lives in `v1.yaml`,
  pending). Mirrors how `memo_escalation` depends on `MemoDeliveredEvent`.
- **aggression_tally increment is value_reconciliation** → tell CC it does **not**
  need a per-increment event; it needs the qualifying-act events + the final
  `RunAggressionTally` in `RunSummary`.
- **Reconcile CC's full stranded-events list** against every trigger above;
  gaps on either side are the real Phase-1 punch list.

---

## What's left in the rubric after this

- **Post-CC-report:** fill the four open contracts (geas, past-Sasha, Assembly,
  Debt), then `silent_failure` is complete and `guardian_tier_correctness`
  unparks.
- **Later-mechanism:** build the `trigger_consequence` evaluator so this spine
  can run; build the `text_pattern` + `llm_judged` evaluators for the
  voice/register categories.
- **Buildable now (needs neither CC's report nor the contracts):** the
  voice/register bug taxonomy — the genuinely novel third of the rubric.
