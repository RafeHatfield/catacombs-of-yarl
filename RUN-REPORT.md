# The long run — started 2026-09-08

One autonomous cycle: the autonomy amendment, then the remaining surface work, then props.
Appended per item. **Nothing here needs a reply** unless it names one of §1.1.4's three triggers.

**On the phone right now:** nothing from this run yet.

---

## Item 0 — the autonomy amendment (PR #200, stacked on #196)

LOOP-PROCESS §1.1.4 amended and **narrowed** to three triggers; §1.1.5 added; SKILL.md §4b records
it and supersedes the routing rule **in place** rather than leaving the file contradicting itself.

The loop now returns to you for: **a one-way door**, **a genuine ruling gap (quoted)**, or **a
broken judge / exhausted budget**. Nothing else.

**What the old list let through.** It read: landing; amendment to anything frozen; an instrument
shown unable to fail; *a precondition fail*; budget. Two were open doors — *precondition fail* got
read as every gate mechanic, *amendment to anything frozen* as every flip touching a ruled clause.
Between them the previous run stopped for **a hash exclusion, a value pin and a routing decision**.

**Routing's guard is now a machine.** `critic_gate` refuses a `ROUTED` whose citation does not
resolve. That is stronger than the signature it replaced: a routing nobody can look up is refused
by the gate rather than by someone remembering. `CLOSED` and `PARKED` still need your words —
routing says *this belongs over there* (checkable); closing says *a human decided not to chase it*
(not checkable).

**Proved:** `prove_gate` 27 → **32** cases. **J1 is the amendment working** — a flip citing a
resolvable clause, disposed by the builder, gate open, no human in it. **J2–J5 all refuse**: an
unresolvable clause, a bare assertion, a missing destination, a `CLOSED` attempted by citation.
`prove_panel` (12), `prove_sentinel`, `prove_build_id` green.

### The first mechanic fixed under the new rule, rather than escalated

`RUN-REPORT.md` and `POLISH-REPORT.md` are now excluded from the build id. A report describes the
build and is not in it — the exclusion list's own words, and *a historical report never gates* is
settled law. Writing the required morning report after a round used to move the id, break the
round's verdict, and refuse the install, over a file that reaches no pixel.

⚠ **Named files, never a pattern.** `*.md` at the root would swallow anything dropped there.
`prove_build_id` case 6 holds both directions: **6a** the run's report does not move the id,
**6b** an *unnamed* root file still does.

---

## Item 1 — install the polish stack: **FAIL, nothing installed**

The previous session's re-vote never completed, and its verdict didn't describe this tree, so the
round was re-taken. It took three rounds and the first two were about the judge, not the art.

| round | outcome | why |
|---|---|---|
| r002 | **VOID** | seat 1 missed its plant |
| r003 | **FAIL** | rank majority lost, 1 of 3 above the reference |

**The VOID was a defect in my own implementation.** *"Each seat its own axis-matched plant"* was
built as an **independent draw**, which delivers it only probabilistically — measured over 900
simulated rounds with two plants and three seats, **all three draw the same plant 24.8% of the
time** (chance is exactly 25%, so the draw was sound; the *design* fell short). r002 hit that case,
all three drew the weaker plant, one missed it, and a round two seats had passed was void. Plants
are now **dealt without replacement**: two plants across three seats exercise both every round, so
a seat missing one is visible against another catching the other. The correlation note also
asserted an unchecked *cause* — *"the axis-matched set has one member"* — on a round where the set
had two; it now reports the observation and the count.

**Then r003 failed honestly, and the noise floor is why.** On **identical bytes** (`picture moved
mean 0.000 / worst 0`):

| round | above the reference |
|---|---|
| r002 | **3 of 3** |
| r003 | **1 of 3** |

That is §13.13's 40% flip rate arriving in the gate itself. **A structural finding, not a
complaint:** PASS-INSTALL requires beating the seeded reference, and the polish stack's changes —
a lane-gain step, a half-cell placement fix, a hero cap — are small next to seat-to-seat noise on
the *same scene*. An incremental improvement over its own reference may simply not be able to hold
a stable majority. Recorded for your eye; the gate was not touched.

Four of r003's five flips route to existing issues (#194 ×2, #167, #193). The fifth measured
false: *"the wall/floor junction is a constant-value 2px near-black rule"* — along that run the
darkest value has **sd 27.2 over a 118.6-level range** and its row position wanders with **sd
7.49px across 14 distinct rows**. Not constant, not a rule at one y.

**On the phone: still nothing.** Continuing to the next item rather than grinding, per §1.1.5.

---

## Item 2 — #199: **closed, no defect.** Both readings were my instrument

The issue existed because of a measurement error of mine, and the surviving claim turned out to be
two more.

**The retraction.** I had claimed *"E and S carry a flat ~0.05 wash and no boundary"*. False — all
four sprites are symmetric with the same 0.72 ramp; E's is at its **last columns**, S's at its
**last rows**, and my reading printed only the first four of each. `build_occlusion` builds all
four from one expression and always did. The false claim was also sitting in the instrument's
header as justification; corrected in place, not deleted.

**Artefact 1 — the reference sat across a lamp gradient.** The contact band was compared against
the cell's *middle*, 24–48px away. At the corridor mouth (8,11) the west edge faces the lamp:
contact 103.4, mid-cell 109.4, **strip just inside the edge 161.2**. Seam 0.0546 against the
middle, **0.3582** against its own neighbourhood.

**Artefact 2 — a sprite stands in the player's cell.** At (6,12) the hero occupies the north
contact band, lifting it to 131.5 against neighbours' 113.3 and 126.3.

**And the hypothesis I reached for first was wrong** — I suspected the seam was authored in
absolute rungs and dying in Weber terms where the lamp is brightest, the same mechanism as #193.
Measured: **seam levels correlate +0.49 with reference luminance.** The seam *grows* with the lamp.
Tested before anything was built on it.

**Corrected, every band clears the floor** (worst cell 0.2869, twice §13.8's 0.1440). §13.5 both
directions on real captures — a control with the overlays omitted collapses it to
**0.0177 / 0.1038 / 0.1797 / −0.0410**, six of eight bands below the floor.

The instrument now reads all four sides with a local reference and excludes the player's cell —
this issue's stated exit, reached by disproving the issue.

