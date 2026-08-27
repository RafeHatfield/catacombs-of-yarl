# PARENT RING-RATE — was the ring B-KAB's, or the surface's?

**Ruling trigger: REPORT ONLY. Nothing here is a ruling, nothing landed, nothing was promoted,
no corpus file changed, and no constant in any instrument was altered.** §13.1 governs landing
and nothing in this run satisfies it.

> **RULED ON THIS REPORT (Rafe, 2026-08-27).** Four rulings, recorded here and carried in the
> documents they belong to. The body below is the evidence they were ruled on and is left as
> written, except where a ruling corrects it and says so.
>
> 1. **C-GAB RETAINS primary-parent status.** The 2–1 seat split is recorded in bible §5.5 as
>    **flagged, unresolved by instrument**, and per §13.2 the deadlock **routes to the human
>    gate** as one question — *crack through the stone, or frame around the tile?* Rafe's answer
>    settles the §5.5 note. **Screening remains the operative guard regardless**, at the measured
>    child rate rather than at B-KAB's. Exhibit: `exhibit_cgab/`.
> 2. **The instrument is relabelled**: *measured error in both directions; orders attention,
>    rules nothing.* §5 of this document is the evidence. `REPORT.md` §6 carries it, and ruling 3
>    there is superseded in part — the *no further tuning* half stands.
> 3. **The rig defect is logged** in LOOP-PROCESS §4.2 as the week's **second measured-harmless
>    silent-success catch**, alongside the MOCK no-op. The clause generalises from *a
>    remediation* to *any step asserting an invariant*.
> 4. **Tier-one gains a precondition** (bible §8.2.1, item 4): **A-HEB is unmeasured as a
>    parent** — twenty generations, or an explicit unknown-rate marker, before anything
>    conditions on it.

Declared before the first call, not tuned after:

> **QUESTION** — `REPORT.md` §4 measured 22 of 24 children ringed from B-KAB, and concluded the
> ring cannot be prompted away. B-KAB is itself a ringed tile, so that result is equally
> consistent with two worlds: the ring was **the parent's**, faithfully carried down the
> conditioning channel; or the ring is **the surface's**, drawn on 32px floor tiles whatever the
> generator is shown. Conditioning on a ring-clean parent tells them apart.
>
> **BUDGET** — 20 generations, two cells of 10, **both spent in full whatever cell P showed**.
> **LEVERS** — held at wave 1's setting: `style_strength` 50, no ring refusal. Neither lever the
> B-KAB run moved is touched. This is a measurement, not a search.
> **SCREEN** — `ring_instrument.py` on every child, mechanically. *(Labelled "a floor, not a
> verdict" when this was declared. §5 below disproved the one-directional claim in that label,
> and Rafe relabelled it on this evidence: **measured error in both directions; orders
> attention, rules nothing.** `REPORT.md` §6.)*
> **SEAT** — a blind spot-check on the borderline, at a cut declared before the data.
> **REFUSALS** — no promotion in any state; nothing written to `remediated/`; the corpus, the
> survivors and `MANIFEST.json` untouched; no lever tuned toward a nicer number.

---

## 0. THE ANSWER, STATED FIRST

**The ring was substantially the parent's.** Conditioned on C-GAB — the RULED primary style
parent, instrument-CLEAN at every value — the ring rate is **5 of 20** mechanically and **9 of
20** at the seat-adjusted upper bound, against B-KAB's **22 of 24**, and **8 of 8** on the wave
whose levers and prompt this run holds identical. The gap survives both readings and every
comparison basis:

| | ringed | vs B-KAB wave 1 | vs B-KAB pooled |
|---|---:|---:|---:|
| B-KAB pooled, mixed levers | 22 of 24 | — | — |
| B-KAB wave 1, *these* levers | 8 of 8 | — | — |
| **C-GAB cell P, instrument** | **3 of 10** | p = 0.0038 | p = 0.00065 |
| **C-GAB pooled, instrument** | **5 of 20** | p = 0.00041 | p = 6.4e-06 |
| **C-GAB pooled, seat-adjusted** | **9 of 20** | p = 0.0078 | p = 0.00095 |

One-sided exact Fisher, computed in `parent_rate_summary.py`, not asserted. Every number in this
document comes out of that file.

**Per the brief's own fork, this is the branch that says record it and stop.** A-HEB's twenty
are **not** run, and screening is **not** recorded as permanent tier-one infrastructure — that
was the *comparable* branch, and it did not fire.

Three findings, in order of what they cost if they stay unknown:

1. **The reference, not the channel, was carrying the ring.** §4's sentence *"it will recur on
   every floor generated from this surface"* is too strong and is corrected here: it recurs on
   every floor generated **from that reference**. The two levers §4 tried could not move the
   rate because neither lever addressed what was actually driving it.

2. **A ring-clean parent is not a ring-free channel.** 9 of 20 is not 0 of 20. Roughly half the
   children of a compositionally neutral, instrument-clean parent still carry a keyline by the
   union of instrument and seat. **Screening is still required; what this run removes is the
   claim that it is required at B-KAB's rate.** Nothing here argues for retiring the screen.

3. **The blind seat disagrees with itself about the primary style parent, on byte-identical
   pixels.** Three blind seats have now judged the same C-GAB capture: `cull: none` (round A),
   `cull: none` (round CP), `cull: keyline` (round CS). That is 2–1, not a settled cull, and it
   is reported because it lands on a RULED corpus assignment. §5.5 is not challenged by it; it
   is put on notice. Detail in §4.

---

## 1. THE DESIGN — TWO CELLS, AND WHY THE CAVEAT IS SMALLER THAN EXPECTED

"Same prompt shape as the B-KAB run" has two faithful readings that come apart once the parent
changes. The B-KAB run was `subject_floor + arm_B` conditioned on B-KAB — and B-KAB is an arm-B
tile, so it was *simultaneously* the parent's own prompt and arm B's text. C-GAB is an arm-C
tile. Both readings were run, ten each:

| cell | prompt | what differs from the B-KAB run | its weakness |
|---|---|---|---|
| **P** — prompt-matched | `subject_floor + arm_B` | **nothing but the reference image** | C-GAB is a flat arm-C tile shown under an arm-B prompt; parent and prompt are no longer coherent the way B-KAB's were |
| **S** — structure-matched | `subject_floor + arm_C` | the reference, **plus** `description` and `shading` | two things differ at once, so a difference here cannot be pinned on the parent alone |

**Each cell's weakness is the other's control**, which is why 20 bought two tens rather than one
twenty.

**The caveat, exact and asserted rather than claimed.** `parent_ring_rate._declare_diff`
reconstructs the B-KAB wave-1 payload, diffs it key by key against each cell, and **hard-stops
on any unexpected difference** before a credit is spent. It ran clean:

```
cell P (arm_B): differs in NOTHING - only the reference
cell S (arm_C): differs in ['description', 'shading']
```

`subject_floor.json` is identical across every arm, and it is the file carrying `outline:
lineless` and the negatives `border, frame, outline`. **Those ring refusals were in play for
B-KAB and are in play here, unchanged, in both cells.** So cell P is a genuine single-variable
comparison: same description, same negatives, same parameters, same `style_strength`, different
reference image.

**The arm-block confound tests null.** Cell P 3/10 vs cell S 2/10, p = 0.5. The cells differ
only in the arm block; a p at 0.5 says the arm block is not doing the work, and cell S
corroborates cell P rather than competing with it.

---

## 2. THE MEASUREMENT

Pool 2842 → 2822. Twenty of twenty spent, no refusals, no errors. Parent verified by sha256
against the survivor manifest before the first call; instrument CLEAN, near-ring 0.791.

| cell | instrument | seat-adjusted | plant | parent control |
|---|---:|---:|---|---|
| P (arm_B) | **3 of 10** | 4 of 10 | CAUGHT | `cull: none` |
| S (arm_C) | **2 of 10** | 5 of 10 | CAUGHT | `cull: keyline` |
| **pooled** | **5 of 20** | **9 of 20** | | |

**Both seat rounds are valid**: each carried the raw B-KAB as a plant and each culled it
`keyline`, matching its verdict in rounds A and B.

### The two rates are reported separately and are never merged

- **instrument** — the mechanical verdict. **It is a floor.** §6 of `REPORT.md` measured that
  the instrument does not catch every construction a human calls a keyline, so this number can
  only be too low.
- **seat-adjusted** — a child counts as ringed if the instrument called it RING **or** a blind
  seat culled it `keyline`. Only the borderline went to a seat and the triage cut sits below the
  published overlap band, so this is the honest **upper bound** on what the instrument missed.
  It does not revise the instrument's number and the instrument was not tuned to approach it.

**The conclusion does not depend on which one you read.** That was the point of computing both.

---

## 3. THE SEAT TRIAGE — DECLARED BEFORE THE DATA, AND DELIBERATELY GENEROUS

`REPORT.md` §6 published the overlap: the seat called a tile scoring 0.654 a keyline and tiles
scoring 0.688 and 0.791 clean. **No threshold separates the classes**, and ruling 3 closed the
question of tuning one. So the rule declared here was:

> every child the instrument calls CLEAN whose near-ring score is **≥ 0.60** goes to the seat.

0.60 sits **below the floor of the published overlap band**, so the triage cannot miss a child
in the zone where instrument and seat are known to disagree. It over-refers rather than
under-refers, which is the right direction for a bound. Ten of the fifteen instrument-CLEAN
children qualified.

The near-ring score itself is **not a second threshold and renders no verdict** — it is triage.
`near_ring.py` computes it by mirroring the instrument's candidate enumeration with criterion 1
recorded instead of applied, and it **self-checks against `REPORT.md` §6's published table**,
reproducing all four survivor figures exactly (1.000 / 0.992 / 0.791 / 0.688) before it is
allowed to triage anything.

### The rig was verified identical, not assumed identical

Both controls were **re-captured** rather than reused. The fresh captures came back
**byte-identical** to the ones stored from the remediation session at a different commit
(`884d0fd5…` plant, `6b358533…` parent). The published prior verdicts therefore transfer
directly instead of by assumption, and the capture path is incidentally shown deterministic
across commits.

`ring_instrument.py --controls` was re-run before any of this: **PASS, 7 red and 3 green**,
including the four one-property discrimination pairs. §13.5 satisfied before its passes counted.

### A DEFECT IN THIS RUN'S OWN TOOLING — LOOP-PROCESS §4.2's family, found and recorded

`capture_children.py` staged children from `ID_BASE = 9200`. **Tile 9200 is `wall_autotile: 0`
in the spike's theme.** Every capture therefore silently made the child floor tile double as a
wall tile — in a rig whose entire claim is *the walls are held constant and the floor is the only
variable*. Nothing went red; the captures rendered and the manifests reported success. That is
§4.2's shape exactly: a step reporting success while not doing what it says.

**It did no damage, and that is measured rather than argued.** Three runs staged three
*different* tiles into `fr_9200` — B-KAB, then `P_seed9709`, then `S_seed9807` — and the plant
and parent captures came out byte-identical every time, and identical to the survivor captures
made before this module existed. Mask 0 does not fire in a one-wide corridor.

The constant is corrected to 9400, clear of the spike's sparse wall ids (9200…9343), and **all
sixteen captures were re-taken under the corrected block and reproduce byte-for-byte** — same
sha256, every image, both rounds. The seats therefore judged evidence the defect did not touch,
and no round needed re-running. `evidence/children_P|S/` hold the corrected-id captures; the
manifests record 9400+.

The correction is written into the constant's own comment rather than tidied away, because the
next person to pick an id block needs to know the wall ids are sparse and reach past 9300.

---

## 4. THE FINDING I DID NOT GO LOOKING FOR — THE SEAT SPLIT ON THE PARENT

Round CS culled the raw C-GAB `keyline`. Round CP, on the same bytes, called it `cull: none` and
ranked it *"the best surface here by a distance"*. Round A had also returned `cull: none`.

> **CS:** *"Inside every cell, in the identical position, a dark rectangle runs down col 9 and
> col 23 from row 12 to row 20, closes along row 20 and dashes across row 9 — four sides, one
> value, returning on itself, with the same tone inside and outside it, so it divides no stone
> from any other stone; the dashed top does not save it."*

**The claim is geometric, so it was checked rather than weighed.** Measured on the tile:

| claimed side | dark pixels | verdict |
|---|---:|---|
| col 23, rows 12–20 | 9 of 9 | continuous |
| row 20, cols 9–23 | 15 of 15 | continuous |
| row 9, cols 9–23 | 15 of 15 | continuous |
| **col 9, rows 12–20** | **4 of 9** | **not a side** |

**The instrument is right about the geometry and the CS seat over-read one side.** Three sides
close; the fourth is less than half present. The instrument measures that same construction at
side-coverage **0.791** against a 0.90 requirement — which is exactly the shape of the thing:
a nearly-closed rectangle with one broken side.

**But that does not settle it**, and this is why the finding is reported rather than resolved.
§12.1's own text says gaps do not excuse a keyline — *"a border with a bite out of one corner,
or one drawn as a dashed run of ticks, is still a keyline"* — and `REPORT.md` §1 records the
instrument's KNOWN LIMIT as precisely this case, along with the decision **not** to lower the
threshold because C-GAB's 0.791 was taken to be a mortar joint network. **One of three blind
seats says it is not.** Whether a side present at 4-of-9 is a broken keyline or an absent one is
a judgement §13.2 assigns to the eye, not to a number, and there is no number that will settle
it — attempting one is the move §13.4 forbids.

**For Rafe, plainly:** §5.5 rules C-GAB the primary style parent partly on *"carries no ring, at
any value"*. That clause rests on the instrument, and the instrument's own published blind spot
is the one construction a seat has now named in this tile. The ruling stands 2–1 on the
evidence available and this run does not move it. It is flagged because a corpus assignment
should know when its supporting clause has been contested, and because **every generation from
here inherits whatever C-GAB is**.

---

## 5. THE REVERSE DIRECTION FIRED TOO — THE INSTRUMENT ALSO OVER-COUNTS

Each round carried, beyond the two published-prior controls, **one of this run's own
instrument-RING children**. The plant proves a seat culls B-KAB's keyline; this asks whether it
culls *this* run's keylines on *this* run's material. It is the direction `REPORT.md` §6 never
measured.

- **Round CP** — `CONTROL_ring_P_seed9706` (near-ring 1.000): seat culled `keyline`. Agreement.
- **Round CS** — `CONTROL_ring_S_seed9809` (near-ring 1.000): seat returned **`cull: none`**,
  and called it *"the only one that reads as stone… the only candidate here whose surface has
  genuine masonry logic."*

So the disagreement runs **both ways**: the instrument misses constructions a seat culls, and it
calls RING on at least one tile a seat reads as honest masonry. §6's characterisation — a floor
that under-counts — is incomplete, and the fuller statement is that instrument and seat are
**imperfectly correlated in both directions**. This does not weaken the headline: the same
instrument, unchanged, was applied to B-KAB's 24 and C-GAB's 20, so whatever bias it carries is
carried equally on both sides of the comparison.

---

## 6. WHAT ELSE THE SEATS SAID — THE SAME TIER-ONE FINDING, ON NEW MATERIAL

**All sixteen captures across the two rounds FAILED — the ten children and every control,
the parent included.** Almost none of it was about rings.
The culls and the flip lists reproduce, on twenty freshly generated children, exactly the three
requirements ruling 2 banked in bible §8.2.1:

> *"Author four to six distinct floor tiles plus 90-degree rotations and randomise placement…
> every image in this set is one tile repeated verbatim with zero variation."*
> *"Add traffic wear that ignores the grid: a lighter, slightly dished, polished channel… and
> darker accumulated grime in the two-pixel strip where the floor meets each wall, both cutting
> straight across stone joints rather than stopping at them."*
> *"Add orc repair to roughly one cell in eight: a cracked flag with a wedge driven into the
> crack, a missing flag backfilled with rammed rubble, a plank of salvaged timber pinned flat
> across a hole."*

A variant system, the wear system, and a floor-repair vocabulary — named again, unprompted, by
two seats that had never seen the bible or ruling 2. **This is corroboration of §8.2.1, not new
work**, and it is not this run's to act on. The review corridor remains one tile wide, so the
wear question still cannot be properly posed (§8.2.1's harness debt, unchanged).

One register cull worth recording, because it names the failure in the fiction's own terms:
*"nothing the orcs lay exists to be looked at, so a centred decorative frieze in every cell
contradicts the fiction before any craft question arises."*

---

## 7. WHAT I WOULD NOT CLAIM

- **Not that the channel is clean.** 9 of 20 children of a ring-clean parent still carry a
  keyline at the upper bound. Screening remains necessary.
- **Not that C-GAB is ring-free.** The instrument says CLEAN and one of three blind seats says
  otherwise, in a construction sitting inside the instrument's published blind spot.
- **Not that any child is good.** Every non-control capture failed both seats. Nothing was
  promoted, nothing landed, and the corpus is exactly as it was before this run.
- **Not that the seat is a stable instrument.** Two rounds, same bytes, opposite verdicts on the
  parent. That is measured here, not assumed away.
- **Not that A-HEB would behave like C-GAB.** It was not run, by the brief's own fork.

---

## FILES

```
tools/floor_remediation/
  parent_ring_rate.py       the declared 20-generation measurement; --dry-run, --rescreen,
                            --seat-tiles. Refuses to run twice over the same RESULT.json.
  near_ring.py              the triage score; self-checks against REPORT.md §6's table
  capture_children.py       lit in-scene captures of arbitrary candidate tiles, same rig
  run_child_seat.py         the blind spot-check rounds, plant- and parent-controlled
  parent_rate_summary.py    the final table; every number in this document
  parent_rate_cgab/         20 children, ledger.jsonl, RESULT.json. NONE PROMOTED.
  evidence/children_P/      round CP captures + manifest
  evidence/children_S/      round CS captures + manifest
  evidence/child_seat/      roundCP/roundCS transcripts and results, verbatim
```

`capture_floors.py` gained two pure extractions — `lay_walls` and `write_theme_for` — so this
run's captures share the wall and theme construction with the survivors' captures by *calling*
the same code rather than copying it. No behaviour changed; the byte-identical control captures
are the evidence of that.

**The originals in `tools/pixellab/probe_6_4/survivors/` were not touched, and
`remediated/MANIFEST.json` is unchanged.**
