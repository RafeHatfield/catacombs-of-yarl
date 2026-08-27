# THE SIGHTED ROUND — session report

**Every wall round on this project ran blind: builder, critic and seats deriving a top-down wall
grammar from first principles, with no one ever shown a correct answer. This round had sight.**

Declared before the first measurement:

> **TASK** — measure the bars' wall construction, rebuild the composite per the measured recipe,
> judge comparatively against the bars in a fair scene.
> **BAR** — seats rank the candidate at or near the bar → §3 ratification evidence. Depth failed
> at budget → the §3-reopening report.
> **BUDGET** — 6 rounds.
> **REFUSALS** — composites no bar pixel; adopts no underived number without flagging it; does
> not rule on §3.

---

## 0. THE ANSWER, STATED FIRST

**Yarl's two planes were inverted, and no side face is needed to explain eight rounds of "no
thickness."**

| | wall TOP | floor | wall FACE | face ÷ top |
|---|---:|---:|---:|---:|
| **the bar** (measured, 23 face tiles) | 1.11 × floor | 1.00 | 0.59 × floor | **0.53** |
| **Yarl, spike `before` arm** | 0.49 × floor | 1.00 | 0.65 × floor | **1.30** |
| **this round, delivered on screen** | **1.11 × floor** | 1.00 | — | **0.52** |

The bar puts the floor **between** its two planes. Yarl put both below it, 0.16 apart, with the
face *brighter* than the top. A blind seat asked to find a top and a face in Yarl's walls was
being asked to read a relationship the values contradicted.

**Three things the round established that no blind round could have:**

1. **The value stack, and its register derivation.** The floor is dark because it is walked
   (§8.1); the wall top is light because nothing has ever touched it; the face is darkest
   because a vertical plane is self-occluded under a top ambient (§6.4 arm B). The bar
   occasioned it; the register justifies it (§13.3).
2. **The top plane must be FLAT.** Not the face's material re-toned. Both round-1 seats culled
   both Yarl arms `wrong-projection` for this, independently.
3. **THE BAR'S VALUE STACK IS NOT DIRECTLY TRANSFERABLE, AND THE REASON IS THE LIGHT.** Measured:
   the engine compresses an authored 0.52 to a delivered 0.77, and an authored 1.15 top to a
   delivered 0.72. The bar's scene has no run-time light, so **the bar cannot supply this
   number** — it had to be measured on Yarl's own rig and solved backwards.

---

## 1. STEP 1 — MEASURE

`tools/sighted_round/measure_bar.py`. Reads a licensed local copy of the asset bar, emits
`bar_measurements.json`, **writes nothing but numbers**. No bar pixel is in this repo, in any
composite, in any reference, or in the corpus (§1.3, and the round's own refusal).

Five example room maps, read from their Tiled `.tmx` so structure is map data rather than a
guess off a screenshot: **548 wall tiles classified, 152 face tiles, 166 shadow placements.**

`WALL-RECIPE.md` carries every number twice — **the measurement** and **the register
derivation** — per §13.3's origination rule. **Three carry a measurement and no derivation and
are FLAGGED, not adopted:** the bright cap at the top-to-face turn (it is §12.1's coping ribbon
unless a wear system modulates it), the bar's autotile placement convention (copying it is
conformance), and the light-falloff compensation (it ties the art to a PLACEHOLDER rig).

> ⚠ **The brief named SPD screenshots as a second source. There are none on this machine.** The
> recipe is single-sourced from the asset bar. SPD is the *structure* bar and would have been
> the better source for layout and readability; its absence is a real gap and is recorded in
> the recipe rather than papered over.

**The structural find:** the bar's occlusion is not in the wall sprite at all. It is a separate
tile on the **floor cell** south of the wall, on its own map layer — 149 of 166 placements sit
directly south of a wall — pure black on a stepped alpha ladder (255 / 64 / 38 / 13), 0.29 tile
deep. §12.1 already ruled that occlusion *"is not on the object at all"*; the bar shows what
that means in implementation.

---

## 2. STEP 2 — REBUILD

`compose_recipe.py`, from the existing parts bin. **The mask table is unchanged** — copying the
bar's autotile convention would be conformance, not a lesson crossing (recipe §4.2).

**Preconditions (`preconditions.py`), any failure a STOP, and shown able to fail:** #149 merged
and §5.5's roles present; the scene's floors sanctioned — **C-GAB and A-HEB only**; the ring
instrument's own control suite passing. Its self-test shows the corpus check go red on an
unsanctioned floor, on an unknown id, and on an empty floor set, and green on the sanctioned
pair.

**The fair scene (§2.2):** `mixed_distribution.json` — a room with **seven** consecutive
south-facing reveals, corners, **and** a one-wide N–S chokepoint that shows no face at all,
because the grammar must work everywhere but is judged on the distribution it ships in. Room B
sits outside the lit radius on purpose: the light arc is part of the distribution too.

---

## 3. STEP 3 — THE COMPARATIVE SEATS

Fresh `claude -p`, cwd outside the repo, no bible, no memory. Each seat gets two images, coded,
and is never told which is which. Pairings: **S1** recipe vs bar, **S2** `before` vs bar (the
control on the comparison itself), **S3** recipe vs `before`, **S4** plant vs bar.

### Round 1 — the projection cull, found twice, independently

**Both seats ranked the bar above Yarl and culled BOTH Yarl arms `wrong-projection`**, for the
same reason, neither having seen the other's verdict:

> *"A top surface does not show five courses of face-brick."* — S1, on the recipe arm
> *"the brick coursing above it has the same pitch, proportion and orientation as below, so it
> is not a top surface — **it is more face**."* — S2, on the composition spike's control arm

**And the seats confirmed §1's value stack without being told it.** S1, measuring the bar:
*"face at 0.49× the top, and the ratio is identical at x=8 and x=320"*, and its own flip list
proposed the recipe's number back: *"paint the face texture at ~0.5× the top texture's base
value."* S2, independently: *"target A's ratio — top ≈90, face ≈47."*

**S3, the direct A/B, went to the recipe even in round 1:**

> *"B breaks the wall into a top plane and a face plane separated by a hard 2-px shadow line at
> rows 85–86; **A is one continuous coursed field from the top of the frame to the floor with no
> plane change anywhere**."* — recipe ranked above `before`; `before` culled `cannot-read`.

### Round 2 — VOID (its plant seat waved the plant through; §3a). Read for context only.

The top plane was rebuilt flat, per the clause the seats occasioned (recipe §2.3). The
`wrong-projection` cull **cleared** — a result that does not count from this round, and does
not need to: rounds 3, 4 and 5 all carry it. What replaced it was a different objection, and it is
entirely the light:

> *"A's face sits at 0.65–0.81 of its top and **its wall top is darker than its floor**."*
> — cull `cannot-read`

Both halves true on screen and neither true in the art.

### Round 3 — author to deliver

Measured delivery through this rig: authored top/floor 1.15 → delivered 0.718 (×0.624);
authored face/top 0.52 → delivered 0.77 (×1.48). So the recipe's numbers were re-read as
**delivery targets** and the albedo solved backwards. Result, in scene:

| | target | delivered |
|---|---:|---:|
| lit face ÷ top | 0.52 | **0.520** |
| lit top ÷ floor | 1.15 | **1.110** |

The bar measures 0.53 and 1.11.

### Round 4 — the cap goes on, and the candidate is ranked ABOVE the bar

Three seats across three rounds, none shown the others', had named the same missing element —
and it was the number §4.1 flagged and switched off: *"rows 30–31 jump to L≈125 (a 2px lip
catch)"*, *"a 2px cap course at y30–31 at 124–147"*, *"B has a top plane, a **chamfered near
edge** and a front face at three separated values; A has one flat band."*

**The ring instrument adjudicated the flag rather than a comment doing it: with the cap on,
0 of 10 tiles carry a ring.** It sits only at the top-to-face turn, which exists only on a tile
with floor to its south, so it answers to the geometry — unlike §12.1's coping ribbon, which ran
every edge for its full length.

> **Q1: A** (the candidate). **CULL_A: none. CULL_B: key-light. RANK: A.**
> *"A puts three distinct planes in a legible stack — bright top, black seam, dark face, then
> floor — and hangs hardware across the seam; B has the value split but nothing on either plane
> to prove it is a plane."*
> *"The face is ~45% of the top and darker than the floor — it is the darkest plane in frame,
> **which is what makes it vertical rather than just shaded**."*
> *"A also changes masonry grain across the join… **Different grain per plane is a second,
> independent depth cue B does not use.**"*
> *"A's face carries fixtures… **Occlusion crossing the join is the strongest statement either
> image makes.**"*
> On the bar: *"Nothing. … the wall is held up by the assertion that it is a wall."* (Q4)

### Round 5 — replicated by a fresh seat

Same build, new process. **Q1: A. CULL_A: none. RANK: A.**

> *"A holds three separated planes — top ≈165, face ≈55, floor ≈120 — with a one-row hard step
> and a different masonry module above and below it… the face is darker than the floor below it,
> so the wall reads **top > floor > face**, which is what puts the face in shadow rather than on
> the same plane."*

**And the control question, answered by both seats, measuring pixels:** Q3 **NEITHER**, every
round. Neither image shows a side face — and the bar does not either:

> *"B's north–south wall (x=0–13) is flat 90-gray for all 240 rows with a single 71 seam at x=14
> and no face anywhere — **a vertical wall in B has literally zero thickness**."* — r5
> *"its entire east flank is one native pixel of joint line, while its north-facing sibling gets
> 24 native px of face"* — r3

**The bar carries the identical §3 limitation.** A north–south wall shows no face in the asset
bar either, and two independent seats measured it without being asked to defend §3.

---

## 3a. ⚠ THE PLANT CONTROL IS MIXED, AND THAT QUALIFIES EVERYTHING ABOVE

LOOP-PROCESS §4: if the critic does not catch the plant, the round is **void** — not discounted,
void. §4.1: the plant must be caught **on the axis it plants.** Full tally, nothing selected:

| round | plant seat's verdict on the plant | status |
|---|---|---|
| 1 | culled **`key-light`**, ranked bar first | **CAUGHT on-axis** |
| 2 | **no cull, ranked the plant FIRST** | **MISSED → ROUND 2 IS VOID** |
| 3 | culled `wrong-projection`, ranked bar first | rejected, **off-axis** |
| 5 | culled `cannot-read`, ranked bar first | rejected, **off-axis** |
| 6 | culled `wrong-projection`, ranked bar first | rejected, **off-axis** |

**Round 2's verdicts do not count and are not read** — which costs nothing, because round 2's
finding (the flat top plane clears the projection cull) is corroborated by rounds 3–5 anyway.

**But the honest position on rounds 4 and 5 is weaker than their verdicts look.** The plant was
rejected by **4 of the 5** seats that saw it and waved through by 1, and named on its own axis
exactly **once**. Under §4.1 that is a control that discriminates but does not reliably
identify, so **the favourable comparative result is reported as evidence, not as a validated
pass.** Rafe's ruling should weigh it at that strength and no higher.

> **RULED (Rafe, 2026-08-27), on both halves, and the section stands exactly as written.**
>
> **Round 2 stays VOID per §4.** Not discounted, not partially read, not rehabilitated by the
> fact that its finding was corroborated elsewhere. A round whose plant seat waved the plant
> through is void, and the corroboration from rounds 3–5 is what makes that cost nothing — it
> is not a reason to reopen it.
>
> **The comparative result is weighed at 4-of-5-seat strength, exactly as marked.** The round
> asked for that reading and it gets it: evidence, not a validated pass. §3's status trail
> carries the qualification at full strength rather than quoting the favourable verdicts alone.
>
> *Recorded because the round proposed its own discount and was right to. A session that grades
> its best result down, unprompted, is doing the job — and the ruling's only work here is to
> hold that grading rather than let a later reader promote it.*

---

## 4. THE CHECKS, BOTH SHOWN ABLE TO FAIL

`checks.py --prove` — LOOP-PROCESS §4.

**DIFFERENCING** — authored occlusion must survive the engine light going out. Proven red on a
synthetic pair whose separation exists only lit, and green on one where it is material.

| arm | unlit face ÷ top | verdict |
|---|---:|---|
| **recipe** | **0.40** | **PERSISTS** |
| **spike `before`** | **1.22** | **DISAPPEARS — CULL** |

> **The composition spike's `before` arm has no authored plane separation at all.** Unlit, its
> face is *brighter* than its top. Whatever plane structure it appeared to have was the engine's
> light drawing it, not the art. That is the arm the spike's round-8 seat ranked **first of
> five**, and it is the arm eight rounds of "no thickness" were measured against.

**RING (§12.1)** — 0 of 18 composed tiles carry a ring, through the value-agnostic instrument
whose own 10-case control suite passes first.

**THE PLANT (LOOP-PROCESS §4)** — an arm with §6.3's baked key light: one edge of every course
lit, the opposite darkened, a lit left edge and a dark right, in a pattern that survives the
engine light going out. **CAUGHT, cull `key-light`.** The seats' verdicts on the real arms
therefore count; a round whose seats pass the plant is void.

---

## 4a. TWO GAPS IN THIS ROUND'S EVIDENCE, NAMED

1. **No SPD source.** §1's caveat: the recipe is single-sourced from the asset bar. SPD is the
   structure bar and is not on this machine.

   > **RULED (Rafe, 2026-08-27): THE SPD GAP IS THE PROMPT'S ERROR, NOT THE SESSION'S.** The
   > brief named a source that was not on the machine. Searching for it, failing to find it,
   > and reporting the absence as a gap in the recipe was the correct behaviour — the failure
   > mode to avoid was substituting a nearby source and calling the recipe two-sourced.
   >
   > **Rafe will supply SPD captures.** They feed an **optional measurement addendum** to
   > `WALL-RECIPE.md`, not a re-run: the value and proportion work stands on 23 independent face
   > tiles and does not need re-deriving. SPD is the *structure* bar (§13.3) and what it can add
   > is layout-and-readability, which is where single-sourcing actually costs something.
   >
   > **The full Oryx library lives at `~/development/assets/oryx`**, recorded here so future
   > measurement does not re-hunt for it. **Pixels never cross, per §13.3** — `measure_bar.py`
   > reads a licensed local library and emits numbers only. No bar pixel is in this repo, in any
   > composite, reference, or corpus, and that refusal is not relaxed by the library having a
   > known path.
2. **Captures are at the reference device's pixel size through the production renderer, not on
   the handset.** §2.1 is LOCKED on in-scene, lit, on device. This round's iteration captures
   run headless at 750×1334 — the same path every prior round used for its rounds — and **no
   device build was made.** The composition spike built a device app for its gate, not for its
   rounds, and the same split applies here: **these captures are round evidence, not gate
   evidence.** A §3 ratification would need the device build first.

---

## 5. WHAT I WOULD NOT CLAIM

- **Not that the recipe is finished.** It is single-sourced, and three of its numbers are
  flagged rather than adopted.
- **Not that the bar's numbers transfer.** §4.4 is the round's most consequential finding and it
  says the opposite: the bar's scene has no run-time light, Yarl's is lit by the player standing
  south of the wall, and the falloff between a wall top and the floor one tile away eats the
  separation. The delivered numbers had to be solved on Yarl's own rig.
- **Not that this rules on §3.** That is Rafe's, on this report.
