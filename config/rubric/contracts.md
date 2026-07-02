# Guardian Tier Contracts - Recovered and Resolved

**Purpose:** the source-of-truth record for how each Weighing Guardian's tier is
determined, and the state of its instrumentation. Built from recovered design
docs plus CC's code investigation, so these decisions stop living only in old
chats. A living doc: update as each contract locks.
**Last updated:** 2026-06-11

---

## The lens (from CC's Q1 investigation): three states, not two

A mechanism is in one of three states from the detector's point of view:

- **DEAD** - set but never read; the consequence never fires. (faction-turning:
  `ChooseTarget` never consults `TargetFaction`.) Fix: wire the read.
- **MUTE** - fires correctly, but emits no observable event; the test is blind.
  (the Oathkeeper: rep flips and the tier scores, but no `TurnEvent`, and the
  tier resolves in endgame state the bot harness never reaches.) Fix: instrument.
- **LIVE** - fires and is observable; a detector can verify it. (the four
  predicate bug-categories.)

**DEAD and MUTE look identical in a transcript** - both read as "I can't see it
fired." Only a code read distinguishes them. This is exactly why silent_failure
detectors carry `scope: static` and "route, don't conclude": a missing event
could be either, and you cannot tell which without reading the source.

---

## Q1 - The Oathkeeper (orc faith) - RESOLVED

**Two "geas" things, untangled (do not fuse them):**

- **Thing A - the marker (`UnshrivenGeasData.MarkerPushed`):** a FAVOR, not a
  breach. Sasha pushes a boundary marker deeper for Borrek; the payoff is
  positive (floors 4-8 shift toward more orc / less undead). Currently DEAD
  (set-never-read; `DungeonFloorBuilder.cs` discards it behind a TODO; only
  tests set it). UNRELATED to the Oathkeeper. NOT a bug, NOT an Oathkeeper input.
  COMMITTED BUILD as of 2026-06-11 (Rafe): a crucial feature, must not fall off
  the roadmap. See "The marker favour - committed build" below.
- **Thing B - orc faith / reputation (`FactionsData`):** what the Oathkeeper
  actually reads. WIRED and WORKS.

**The contract (Thing B):**
- Metric: orc reputation, driven by `RunAggressionTally` unprovoked orc kills
  (per-run, the sticky-unprovoked definition: victim never attacked you).
- Breach: >= 3 unprovoked orc kills in a run -> `ApplyFactionRunEnd` flips rep
  to hostile (`HostileThreshold = 3`).
- Consequence: at the Weighing, `AuditScorer.ScoreOathkeeper(rep, unprovokedKills)`:
  hostile -> Savage, allied -> Allied, neutral splits Diminished/Neutral on
  whether any blood was spilled.
- Detector: flag if a breach occurred but rep did not go hostile, OR rep is
  hostile but the Oathkeeper did not score Savage.

**State: MUTE, not dead.** The chain fires correctly. But orc rep emits no
`TurnEvent` (`TranscriptRecorder`; `OrcRepChanged` fields defined, never set),
and the tier resolves in endgame state the bot harness never reaches. The
detector has nothing to read yet.

**Unblock:** instrument the Weighing-resolution events. Leading edge:
`orc_rep_changed` and `oathkeeper_tier_resolved`. Generalize to the family:
`guardian_tier_resolved` for every Guardian plus the ending - the whole Weighing
resolution is currently mute, and this is the same need as the "tier as a
structured field" dependency for `guardian_tier_correctness`. Once instrumented,
the Oathkeeper detector is a scripted / endgame-scope regression guard on a
currently-working chain.

**Confirmed clears:**
- The metric is rep + unprovoked orc kills (TWO inputs). Marker-faith is NOT an
  Oathkeeper input. Resolves the design-doc-vs-handoff drift in favor of the
  simpler version.
- "Unshriven" = the orc faction (same entities); killing any orc unprovoked
  counts toward the breach.
- `CumulativeUnprovokedKills` (the DEBT-014 dormancy whitelist entry) is NOT what
  the Oathkeeper reads (it uses `RunAggressionTally`, per-run). Whitelist stands;
  no collision.

**Resolved (Rafe, 2026-06-11):**
- The marker is correctly NOT an Oathkeeper input. Confirmed.
- Instrument the Weighing-resolution events: YES (see CC handoff).
- The marker favour: BUILD IT - committed, must not fall off the roadmap.

### The marker favour - committed build (not a bug, not dormant)

Reclassified from a deferred open contract to a committed feature. The positive
orc favour: Sasha pushes a boundary marker deeper for Borrek -> `MarkerPushed`
-> floors 4-8 shift toward more orc / less undead.

Current state: BOTH halves unbuilt -
1. The SET - the player-facing way to push the marker (the Borrek interaction).
   Design surface: story doc D-prime may or may not fully spec the player action.
   CC to check; flag back if there is a design gap that needs us first.
2. The READ - wire `DungeonFloorBuilder` (currently discards the flag behind a
   TODO) to apply the floors 4-8 composition shift.

NOT whitelisted as dormant - deliberately. The static dormancy lint keeps
flagging `MarkerPushed` as an unread field until it is wired. That is the
guarantee that this "can't fall off the roadmap": the lint nags until built.

Future detector (activates once built): `MarkerPushed` set -> floors 4-8
composition shifts toward orc -> flag if it does not. A trigger_consequence
entry, queued behind the build.

---

## Q2 - Past-Sasha - OPEN (worked next)

The question: does encountering a past-Sasha have a mechanical payload (choice,
stat effect, memory/unlock), or is it narrative only? If narrative-only it
leaves the bug taxonomy for the voice/coherence side.
Lead to chase: the "Hael catalog" appears tied to the past-Sashas catalog and to
Swap availability at the ending. Apply the DEAD / MUTE / LIVE lens.

---

## Q3 - The Assembly of the Lost - RECOVERED, pending confirm

- Metric: `CumulativeDeaths` + past-Sashas catalog size.
- Ally form (few deaths): a single past-self stands with Sasha.
- Savage form (many deaths): a horde of every fallen Sasha.
- For `guardian_tier_correctness`: this UNPARKS - keys on `CumulativeDeaths`
  (+ catalog size), direction standard (more deaths -> more savage).
- Pending: Rafe confirms metric; CC confirms DEAD/MUTE/LIVE state.

---

## Q4 - The Debt - RESOLVED

Does not scale. Cannot be allied. Full strength every run, for every player.
- For `guardian_tier_correctness`: the Debt is EXCLUDED. There is no tier to
  reconcile (`direction: n/a`). The detector must NOT attempt to reconcile a
  Debt tier.

---

## Bonus recovered (the other two Guardians, for completeness)

- **Warden-of-Wardens:** `hall_warden_possessions_total` + possession-tone track
  (polite / procedural_notice / formal_complaint).
- **Auditor's Own:** per-run excess rate (suffering beyond necessity). Scale is
  INVERTED (allied = bored/clean, savage = ecstatic/cruel).
