# Bot Analysis (the Analyst) - Definition of Production

_Last verified: 2026-07-12 against commit 86b6f10_

**Naming note:** in the project docs and CC's numbering this is the ANALYST
(originally "Thread 2"). To avoid a numbering collision with the rubric (the
original Thread 1), this doc uses the instrument's NAME, not a number.

**Purpose:** make "is it production?" a checkable state, not a feeling.
Production for a measuring instrument is NOT "measures everything." It is
"measures its scope reliably, runs on a cadence, and states its own blind spots."
By that definition, bot analysis is production-capable now; what remains is short
and mostly operational.

---

## What the instrument IS

A bulk bug-detector and blind-spot mapper over organic bot runs (floors 1-10).
Generate N bot transcripts, analyze them, get findings.md. The cheap,
high-volume instrument. It is NOT the silent-failure detector, NOT the coherence
evaluator, NOT the endgame tester - those are sibling instruments (see Roadmap).

---

## v1 Production scope (the line)

**IN:**
- 4 predicate bug-categories: `soft_lock`, `hp_out_of_range`,
  `aggression_tally_negative`, `possession_body_inconsistent`. Each validated to
  fire on a violation fixture and stay clean otherwise.
- Audit trail: turns-evaluated per category, so "0 candidates" is provably "ran
  and found nothing," not "never ran."
- System-trigger heatmap + 0x blind-spot list: routes-not-concludes on
  unexercised mechanisms.
- Organic floors 1-10, parallel batch, findings.md output.

**OUT (by design, not by gap):**
- Silent-failure / dead-lever detection (`trigger_consequence`). The bot batch
  ROUTES (the blind-spot list); it does not detect. Detection lives in the static
  lint + scripted scenarios.
- Coherence evaluation. Mostly the LLM player's strength; the N/A slot is ready.
- Endgame / Weighing. Bots cap at floor 10; the Weighing is floor 25. Scripted
  scenarios test that.

---

## What v1 catches, and what it does NOT (read honestly)

**CATCHES:** crashes-as-impossible-state, soft-locks, out-of-range values,
possession-state inconsistency - at high volume, cheaply, with a trustworthy
audit trail. Plus a map of which mechanisms the bulk instrument never touches.

**DOES NOT CATCH:** the silent-failure class that motivated this project
(faction-turning, the orc-kill MISFED). That class is caught by the sibling
instruments (static lint for dead fields; scripted scenarios for
trigger-consequence chains), which depend on the open contracts and missing
events. v1-production is real and useful, but it does not yet catch the
dead-lever class. Knowing that is part of using the instrument correctly.

---

## Readiness checklist (the path to "in production")

- [x] **Scope line declared**: 4 predicates + audit trail + blind-spot mapping,
  organic floors 1-10. Locked by Rafe, 2026-06-11.
- [x] **One-shot run:** `./scripts/bot-analysis.sh` (CC, 2026-06-11). Defaults
  300 runs / seed 1337 / floors 10; `--explore` for varied seeds; exit code 2 on
  candidates.
- [x] **Baseline run, self-report checks:** 300-run batch reviewed. Zero
  false-positive fires; audit trail healthy (447,029 turns/category, 0 skipped);
  blind-spot list as expected (possession_used, orc_rep_changed, Weighing 0x).
- [~] **Fidelity confirmation:** LARGELY CONFIRMED 2026-06-11 by reading a raw
  transcript (run-1636). The gameplay is real and faithful - real coordinates,
  door events, a real kill (entity 138), a legible poison death with per-turn DoT
  and multi-enemy melee. Remaining sub-item: confirm the harness logic is
  literally the Godot client's logic (architectural, CC) - not yet answered.
- [~] **Liveness / efficacy gate:** the agent must actually PLAY, not freeze.
  FREEZE FIXED + CONFIRMED 2026-06-11 by reading the post-fix run-1636: 797 turns
  (was 2157), 4.3% no-op (was 71%), real stair Descend events (cause "player") at
  turns 58/641 instead of cap-flips, max stuck streak 4 (was 992). Diagnosis was
  100% bot-logic (every blocked move had >= 2 available actions), not
  unreachable-stairs. Batch-wide: blocked moves 56% -> 2.9%, floors-by-descent
  68 -> 331. The bot now plays for real. The liveness question is answered: yes.
- [~] **no_progress detector recalibration:** LANDED 2026-06-11. Recalibrated to
  drop productive non-move events (door-opens) and only flag streaks beyond the
  4-turn recovery window. Result: 6,359 instances / 300-of-300 runs -> 35
  instances / 5-of-300 runs. False-positive side VERIFIED on run-1636 (now 0
  flags: its two 4-turn recoveries are below threshold, its 23 door-opens
  excluded). Remaining before sign-off: (a) confirm the POSITIVE half of the
  two-sided canary - the recalibrated detector must still FIRE on a genuine freeze
  (e.g. the pre-fix 992-turn run-1636); a quiet detector and a dead one look
  identical on healthy data, so the positive test is mandatory. (b) eyeball one of
  the 5 flagged runs to confirm a genuine stall, not a new false-positive class.
  If both hold, the liveness gate closes and bot analysis is signed off. [CC + Rafe]
- [x] **Scope documented** (this file).
- [ ] **Cadence + triage decided:** when it runs, and what happens to findings.md
  when it surfaces a candidate. [Rafe, process]

---

## Roadmap - after production, in priority order

1. **trigger_consequence + scripted scenarios** - the dead-lever detector class,
   the thing that catches what motivated the project. Blocked on the open
   contracts (Q2 past-Sasha, Q3 Assembly, Q4 Debt; Q1 resolved) and the missing
   game events (faction-change, possession ability-grant, per-turn memo
   delivery). Highest-value expansion. NOTE the orc-kill MISFED fix is a
   prerequisite for the Oathkeeper chain being correct at all.
2. **Scripted Weighing scenario harness** - construct endgame state, drive
   `BeginFromPersistence`, assert tiers. CC's 11 instrumentation tests are the
   seed. Unblocks `guardian_tier_correctness` against real transcripts.
3. **Coherence pass** - blocked on `coherence_dimensions` (design thread). Lower
   priority for bot analysis; it is the LLM player's strength.
