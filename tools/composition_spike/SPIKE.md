# THE COMPOSITION SPIKE — session report

**Returning under ruling trigger (a): a landing-gate-shaped judgment — Rafe's eye, §13.1's
scene, on the device — and under trigger (b), because the one objection every round converged
on cannot be answered without amending a LOCKED clause. Nothing lands. What is ruled on is a
road.**

Declared before the first tile was composed, not tuned after (LOOP-PROCESS §0.3, §8):

> **TASK** — composed two-plane wall segments built from the wall gauntlet's parts bin,
> rendered in the lit tier-0 corridor on the reference device, for one human question:
> **does a composed wall read as a wall, and does it read as HELD?**
>
> **METHOD** — parts off disk out of the gauntlet ledger; composition authored in a committed
> script; binding overlays authored as MOCKs and marked so; arms differing by one variable
> each; blind critic before Rafe.
>
> **BAR** — the composed bound arm passes the blind critic unhedged on the wall question and
> the held question. **BUDGET** — 8 critic rounds. Spent below the bar → report what the
> composition could and could not do, with the captures as evidence. Zero API calls; the bin is
> the ledger.

---

## 0. THE ANSWER, STATED FIRST

**Composition works. It fixes what the gauntlet could not fix, and it is not enough.**

Six rounds moved measurable things: the 32px stamp, the mirror, the interior fill, the value
collision, the sticker read, the mortar joint a strap crosses. Every one of those was a
*relationship between parts*, and every one of them yielded to being authored rather than
prompted. The thesis the gauntlet pointed at is sound.

And in six rounds, across every arm, the blind critic answered the thickness question **no**:

> *"none of them has a wall with a top and a side, so the whole set is a flat pattern with a
> path tinted through it."* — round 5, separator

That is not a defect in the composition. It is bible §3 meeting an orthogonal grid. §3 grants
walls exactly two planes — a front face and a top surface, **no side face** — and the renderer's
mask table only ever shows a front face where floor lies to the SOUTH. In a one-tile-wide
north–south corridor no wall cell has floor to its south, so the player walks between two
fields of wall-*top* with no face anywhere in sight. Composition cannot supply a plane the rule
forbids.

**The seat asked for that plane, unprompted, in every single round** — "no side face" (r1),
"rotate it 90° and add dedicated edge cells down the vertical corridor's flanks" (r2), "a top
you can see and a side that stops" (r3), "re-cut the corridor edge into a 3–4px return" (r4),
"no cap, no side, no base" (r5). It was never shown §3.

**The road ruling is yours, and it is a §3 ruling before it is a pipeline ruling.**

**And one thing this session did not go looking for.** The plant — boundB plus a baked key
light, §6.3's forbidden construction — was ranked **first by three of the six blind seats and
never below third of five**, while being correctly culled as `key-light` by two of them. §6.4
recorded that its ratification "is not a victory over a baked arm, because no baked arm existed
to beat" and that "the comparison §6.4 set out to run remains unrun". A baked arm exists now,
built as a control, and the first result on the depth axis is adverse. §5.1b states it in full,
with what it is and is not. §6.3 stands untouched by this session.

---

## 1. WHAT WAS BUILT

Five tile families of 49 tiles each — four arms and a plant — regenerated every round from a
committed script. Every pair differs by exactly one thing; the geometry, the rig, the tile size,
the resolution and the floors are identical across all five.

| arm | top plane | bindings | what it isolates |
|---|---|---|---|
| **boundA** | R4 slab stock (`r04_00` / `r04_08` / `r04_03`), native value | MOCK | the brief's primary |
| **boundB** | R6/R7 coursed material cropped for use as a top, luminance-matched — **DERIVED** | MOCK | the brief's own fallback |
| **ctrlA** | as boundA | **none** | held vs unheld |
| **ctrlB** | as boundB | **none** | held vs unheld |
| **plant** | as boundB | MOCK + a baked per-course key light | the critic's control |

### The parts, and what was discarded

| role | part | ledger | rows used | discarded, and why |
|---|---|---|---|---|
| front face | `r07_00` | round 7 | 5–30 | 0–4 — its failed cap band. Ledger verdict: *"rows 0-4 use the identical greys as the face, so there is no top band at all"* |
| top (A) | `r04_00`, `r04_08`, `r04_03` | round 4 | 0–25, 0–28, 11–24 | `r04_08` rows 29–31, its baked floor shadow; `r04_03` rows 0–10, a centred motif the ledger critic said *"stamps identically every tile"* |
| top (B) | `r07_00`, `r07_08`, `r07_09` | round 7 | 5–30 | as above |
| floors | A-VAB, A-HEB, B-KAB, C-GAB | §6.4 survivors | whole | — |
| bindings | straps, pins, cramps, lashing, one tag | **MOCK — authored in `compose_walls.py`** | — | — |

**Zero API calls.** Every stone pixel is on disk in the gauntlet ledger with its round and
candidate id in `PARTS_MANIFEST.json`.

**Every composed pixel is a colour that exists in the parts bin.** `verify_palette.py` builds
the reference palette from exactly the stock the composer used and checks all 245 tiles:
83–103 distinct colours per arm, **0 outside the bin**. Occlusion, iron, rope and tag values
are all drawn from that set. §5 stays PLACEHOLDER; nothing here proposes a palette.

*That check failed before it passed.* When round 5 gave the face plane three parts and the
checker was still building its reference from one, it reported 175 colours "outside the bin" —
the checker was wrong, not the tiles. Recorded in the file, because a check that has never
failed is not evidence of anything (§13.5).

### The composition rule

`DungeonRenderer` computes a 4-bit cardinal mask (bit3=N, bit2=S, bit1=E, bit0=W, set when that
neighbour is wall) and collapses 7/11→3, 13/14→12. Bible §3 in that mask is one line:

```
SOUTH BIT CLEAR  ->  floor below  ->  top band + occlusion + FRONT FACE
SOUTH BIT SET    ->  wall below   ->  TOP SURFACE only
```

**This is the thing a single generated tile cannot do**, and it answers the gauntlet's round-10
objection structurally: its tile had to carry a cap band whether or not the wall below wanted
one, so an identical hard-edged cap "stripes the wall every 32 pixels when stacked". Composed
per mask, the band appears only where the wall actually stops.

Geometry is drawn by occlusion and never by highlight (§6.3). Nothing in any tile is
brightened.

---

## 2. THE HARNESS GAPS, AND THE SMALLEST FIXES

**Gap 1 — `wall_autotile` mapped one tile id per mask.** A corridor edge stamped a single tile
at every cell that mask occurred: a repeat every 32px, the defect the gauntlet's critic named
in every round it reached. A strap repeating on a 32px lattice reads as wallpaper — §7.3
inverted, ornament where structure was asked for.

**Gap 2 — and this one is the instructive failure, because it was MY fix that was incomplete.**
Making the masks list-valued left `wall_diagonal.interior_fill` a scalar, and interior_fill is
**267 of the ~300 wall cells** in this corridor. The fix varied the visible 6% of the mass and
left the other 94% stamping one PNG. Two full critic rounds were spent judging a single tile
before the blind seat found it: *"the solid field is one 32px tile stamped ~150 times with no
variation (median tile-to-mean correlation 0.94)."*

Both fixed at the smallest scope that answers them: `wall_autotile` and `wall_diagonal` roles
may declare a list, chosen by `PositionHash(x, y)` exactly as floor roles already are. A scalar
still resolves to itself, so every shipped theme loads unchanged.

**Verified by capture, not assertion** (§13.5, LOOP-PROCESS §4):

| control | plant | differing pixels |
|---|---|---:|
| 1 — the variants reach the renderer | every mask pinned to one tile id | 11.999% PASS |
| 2 — the mask-3 entry is the one being read | mask 3 pointed at the FLOOR tiles | 11.689% PASS |
| 3 — **interior_fill's variants reach it** | interior_fill pinned to one tile id | **32.641% PASS** |

**Control 3 exists because control 1 could not have failed for the bug that actually happened.**
Control 1's regex pins integer-keyed autotile entries; `interior_fill` is a word-keyed role in
a different block. That is precisely how the hole survived a passing control. A control that
cannot fail for the bug in front of it is not a control.

This harness has been bitten by this shape before: `--tile-size` was echoed into the log while
`TopDownRenderer` drew a hard-coded 24px grid regardless.

### The variant count is chosen against the hash, not picked round

`PositionHash` is `7919x + 104729y`. Three properties pull against each other:

- **Mirror.** The review corridor is deliberately symmetric about the player's column, so cells
  `x=c±d` collide when `2·7919·d ≡ 0 (mod N)`. At **N=4** that is every even `d` — **half the
  map an exact reflection of the other half**, which the seat measured at MAD 6.1 against a
  local texture std of 34.5 and spent a whole flip item on.
- **Diagonals.** If 7919 ≡ 104729 (mod N) the index depends only on `(x+y)` and the field bands
  along anti-diagonals. **N=7** has both ≡ 2 and does exactly that.
- **Neighbours.** Orthogonally adjacent cells must not share a variant.

**N=9**: 7919 ≡ 8, 104729 ≡ 5. Different, both non-zero, mirror collisions only every 9th cell.

⚠ **This is a harness finding, not a spike finding.** Every capture taken in this corridor —
**§6.4's included** — carries the mirror to whatever degree its variant pools allow.

---

## 3. THE FINDING THE FIRST CAPTURE FORCED

**Bible §3's two planes do not, on their own, separate wall from floor.**

`evidence/finding_before_edge_occlusion.png` (produced by commit `339ec10`, labelled with its
true producer per §2.3) is the composition with §3 and nothing else. A lit wall top at
luminance 96 sits beside a lit floor at 122 with **no boundary of any kind between them**.

The shipped Oryx placeholder tiles this renderer's mask table was fitted to already answer it:
184 carries a dark band along its bottom edge, 187 dark columns down both sides. The engine's
tile grammar assumes an **occluded edge wherever wall meets floor**, and §3 does not supply one.

⚠ **Flagged, not decided.** A dark edge on every wall/floor boundary is a second linear system
and §12.1 reserves that job for straps, bands and tags. It is occlusion rather than an outline —
on the wall's own edge, only where floor is adjacent, direction-agnostic under any azimuth — but
the tension is real and the ruling is yours.

---

## 4. WHAT THE CORRIDOR CAN AND CANNOT ASK

Stated because it bounds every verdict below, mine and the critic's.

| effective mask | cells | renders |
|---|---:|---|
| 15 + diagonals (interior) | 273 | top surface only |
| 12 (vertical run) | 28 | top surface only |
| 3 (horizontal run) | 22 | **top band + front face** |
| 5, 6, 9, 10 (junction corners) | 1 each | corner |

**~6% of the wall cells in the scene can show a front face at all**, confined to two rows either
side of the east–west branch. The corridor is an excellent floor instrument and a thin wall
instrument — it under-tests exactly the plane the gauntlet was failing to generate. If the road
is taken, the review scene needs an east–west emphasis or a chamber before a face verdict is
worth much.

---

## 5. THE BLIND CRITIC — six rounds

A fresh `claude -p` per round, cwd outside the repo, five lit captures under anonymous codes,
never the bible (LOOP-PROCESS §3). Transcripts and parsed verdicts in `evidence/critic/`.

**Blindness, stated precisely rather than claimed.** cwd is a scratch directory holding only the
five PNGs: no project `CLAUDE.md`, no memory, no ledger, no bible. It was launched with
`--allowedTools Read` but demonstrably wrote files (its own zooms, brightness passes, difference
images), so tool restriction did not hold and blindness rests on cwd and on the process having
no reason to look elsewhere — not on a sandbox. Recorded because the gauntlet's report claimed
the stronger version.

| round | plant | plant cull | passes | flips | commit | Q4 — thickness, on the bound arm |
|---|---|---|---:|---:|---|---|
| 1 | CAUGHT | none | 0 | 10 | `7c7f2b94` | *"the wall is coplanar with the floor..."* |
| 2 | CAUGHT | none | 0 | 7 | `fd8a995a` | *"the corridor meets the solid field across..."* |
| 3 | CAUGHT | **key-light** | 0 | 6 | `9be594d7` | *"Split — the east–west band's coursing implies..."* |
| 4 | CAUGHT | **key-light** | 0 | 11 | `910ceaca` | *"the corridor edge is a one-pixel dark seam..."* |
| 5 | CAUGHT | none | 0 | 7 | `02f7b797` | *"No thickness. There is no cap, no side, no base..."* |
| 6 | CAUGHT | none | 0 | 8 | `2650e8ee` | *"No thickness — wall meets floor at a 1–2px line..."* |

**No round was void.** Regenerate with `round_table.py`; no number above is typed by hand.

### 5.1 The plant, and the finding inside the control

The plant is boundB with a baked per-course key light — §6.3's forbidden construction, and the
one the gauntlet's own round 8 manufactured by accident. **It was caught in every round. No
round was void.** But *how* it was caught moved, and that is worth more than the control:

| round | plant cull | what the seat called it |
|---|---|---|
| 1 | none | *"dead-straight, unbroken horizontal lines ... a ruled stripe, not a ledger"* — **timber** |
| 2 | none | *"coursing has collapsed into continuous horizontal stripes"* — **material** |
| 3 | **key-light** | *"still present in the far-left corner at 6× exposure where the engine pool never reaches; that is a south light painted into the stone"* |
| 4 | **key-light** | *"+8.7/−6.2 top/bottom split against +2.3/−1.0 for every other image in the set"* |
| 5 | none | *"perfectly straight full-width ruled course lines"* — **material** |

**The key-light cull is reachable at 32px — but only when the field around it is legible.** In
rounds 1, 2 and 5 the wall mass was stamped or structureless and the same baked light read as
hardware or as bad masonry. In rounds 3 and 4, with the field varied and the coursing intact,
two independent seats named it as lighting and measured it.

This sharpens the gauntlet's §5 hazard into something operational. The gauntlet found that at
32px *describe geometry with value* and *bake a key light* are the same vocabulary. Add: **so is
*draw a timber band*, and which one a viewer reads depends on the surface around it.** An
instrument for §6.3 cannot be a critic looking at a noisy field.

### 5.1b THE PLANT OUTRANKED THE ARMS — and §6.4 said this comparison had never been run

This was not designed and it is the most consequential thing in the report.

The plant is boundB **plus** a baked per-course key light: identical stones, identical rig,
identical geometry, one forbidden construction added. Six independent blind seats ranked the
five captures best-to-worst:

| round | ranking, best → worst | plant | plant cull |
|---|---|---|---|
| 1 | **plant** > boundB > ctrlB > boundA > ctrlA | **1 of 5** | none |
| 2 | boundB > ctrlB > **plant** > boundA > ctrlA | 3 of 5 | none |
| 3 | boundB > boundA > **plant** > ctrlB > ctrlA | 3 of 5 | key-light |
| 4 | ctrlB > boundB > **plant** > boundA > ctrlA | 3 of 5 | key-light |
| 5 | **plant** > boundB > ctrlB > boundA > ctrlA | **1 of 5** | none |
| 6 | **plant** > boundB > ctrlB > boundA > ctrlA | **1 of 5** | none |

**First in three rounds of six. Never below third of five. Not once last.**

Round 6 named the mechanism: *"a depth cue applied on one axis only is worse than no depth cue
— it asserts a viewing direction the rest of the frame contradicts."* It read as depth. In six
rounds it is **the only thing that produced any depth read at all**, in a set where the
thickness question was otherwise answered no every single time.

**Why this matters more than a ranking usually would.** §6.3 is RATIFIED, and §6.4 states its
own limit in as many words:

> *"Stage 1 produced no arm A — no candidate in any arm depicted a directional key light, so the
> three arms never separated on the lighting axis. This ratifies the treatment under light. It
> is not a victory over a baked arm, because no baked arm existed to beat ... The comparison
> §6.4 set out to run remains unrun, and nothing in this ratification should be cited as having
> run it."*

**A baked arm now exists.** This session built one because LOOP-PROCESS §4 requires a plant, and
it is in one respect a *cleaner* comparison than §6.4's design: the plant and boundB are the
same stones under the same rig, differing by exactly the baked light, so it is a within-arm A/B
rather than three separately-generated arms.

**What this is NOT.** It is not a ruling and not a candidate for one:

- **The plant never passed.** It failed in all six rounds and was culled `key-light` in two,
  with a method — *"still present in the far-left corner at 6× exposure where the engine pool
  never reaches"* — and a measurement, *"+8.7/−6.2 top/bottom split against +2.3/−1.0 for every
  other image in the set."* The clause's own instrument works.
- **A ranking is not the gate.** §13.1 gives the verdict to Rafe on the device, and a seat
  preferring a still image is exactly the "wrong instrument in the wrong context" §6.3 warns
  about — except that these are lit in-scene captures, which is the *right* context, which is
  why it is being reported rather than dismissed.
- **The arms it beat are mocks.** A better-composed wall might beat it. Six rounds did not
  produce one.
- **It was built to be caught**, which biases it toward being conspicuous, not toward being
  liked.

**The honest statement: on the depth axis, in the lit scene, at the ruled canvas, the forbidden
construction outperformed every receive-light arm this session could build, six times out of
six — while remaining correctly detectable as forbidden.** §6.4's unrun comparison has run
incidentally and its first result is adverse. That is a finding for the record and a ruling for
Rafe; it is not this session's to resolve, and §6.3 stands untouched by it.

### 5.2 What the rounds actually fixed, and what never moved

Every round was a real change with a measured effect:

| round | change, and the charge that drove it | measured effect |
|---|---|---|
| 1→2 | keyline removed (*"stickers ... inside a hard black keyline"*), elements moved onto joints found in the stone, pins chip the brick, N 4→7, slab x-roll dropped, top part swapped | sticker read named as fixed by r3 on the face band |
| 2→3 | `interior_fill` variants (*"one 32px tile stamped ~150 times"*), N 7→9 against the hash | tile-to-mean correlation 0.94 → 0.441 |
| 3→4 | top plane from **three parts** rather than nine offsets of one | rendered-field block correlation 0.772 → **0.555**; ranking flipped, R7-coursed top took the top two places |
| 4→5 | face plane from three parts (*"re-laid patches ... a different brick module"*) | **REGRESSED** — R4 arms `cannot-read` → `noise` |
| 5→6 | round 5's face change reverted; its overlay fixes kept | — |

**And in all six rounds the thickness answer was no.** Not once, on any arm, in any round.

### 5.3 The general result, which is worth more than the revert

**Mixing parts works on the top plane and not on the face.** The top plane's material has no
period, so more parts buys variation for free. The face plane's entire legibility *is* its
course period, so three parts with three different course rows destroyed it —
*"vertical autocorrelation shows no course period at all."*

"Compose from parts" is not one technique. It is two, and which applies depends on whether the
material carries a period. That is a transferable rule for any future composition work and it
was not visible before this session.

### 5.4 Flip-list items REFUSED, and why that matters

- *"drop a 2px hard-edged occlusion shadow from that cap onto the adjoining floor tile"* — a
  baked drop shadow in the asset. §6.3 forbids it outright: *the asset never grounds itself.*
  `FloorComposer` Pass 2 already darkens wall-adjacent floor.
- *"a cap band one step lighter and one step desaturated"* — a highlight.
- *"add dedicated edge cells down the vertical corridor's flanks"* / *"a top you can see and a
  side that stops"* — **a side face, which §3 forbids.** Asked for in all six rounds.

**Three critic loops in this project have now asked for a §6.3 or §3 violation.** The gauntlet's
round-7 flip list asked for a 1px chamfer per course and its own round 8 then culled three
candidates for `key-light`. A flip list is a reaction, not a spec, and executing one literally
is how the last loop manufactured the defect it was trying to avoid.

### 5.5 Incidental findings about things this session did not build

Reported rather than acted on; they are not this spike's to change.

1. **The §6.4 survivor floors carry a baked dark ring.** *"The inset floor slabs carry a uniform
   3px near-black ring on all four sides."* **§12.1 is LOCKED: nothing in Yarl carries a baked
   dark ring.** A blind seat found this in the STOP-1 survivors, unprompted, having never been
   shown §12.1.
2. **They do not read as one floor.** *"the corridor paving changes hue family across hard tile
   seams — salmon, grey-brown and olive tiles abut with no transition ... three tilesets pushed
   together."* Three separate seats raised it.
3. **Their vegetation is the only high-chroma content in the scene**, and a seat rejected it on
   register grounds it was never given: *"overgrowth in a place that has no light and no
   weather."*
4. **A pin arrangement made a face.** *"Two pale dots above a dark bar ... at played size that
   reads as two eyes over a mouth."* Bible §1.3's named trap arriving by accident in a mock,
   caught by a seat that was never shown §1.3.

---

## 6. WHAT I WOULD NOT CLAIM

- **Not that composition fails.** It fixed every relationship defect it was pointed at. What it
  cannot do is supply a plane §3 forbids.
- **Not that six rounds exhausts the flip lists.** The budget was eight and two are unspent. The
  session returns under a ruling trigger, not on empty — the residue needs a §3 ruling, and
  spending the last two rounds on items I would have to refuse is not a round.
- **Not that the seat's numbers are all sound.** Round 3's central charge — *"the same 32px
  stamp repeated identically ... without a single variation"* — was **false**;
  `measure_field.py` recovered the tile grid phase from edge periodicity and measured the
  rendered field at 0.772 median block correlation with **zero** identical pairs out of 300.
  The perception behind it was right and the measurement was not, which is why it was checked
  before it was acted on.
- **Not that the corridor tested the face.** ~6% of its wall cells can show one.
- **Nothing here is art, a palette, or a landing candidate.**

---

## 7. WHAT IS IN FRONT OF YOU

**On the device** (both installed, iPhone SE 3rd gen, `5DB969FF`):

| app | bundle | shows |
|---|---|---|
| **YARL Held** | `com.rafehatfield.catacombsofyarl.tier0` | boundB — composed wall, MOCK bindings |
| **YARL Unheld** | `com.rafehatfield.catacombsofyarl.tier0u` | ctrlB — the same stones, overlays omitted |

Flip between them. The delta between the two IS the held question, with nothing else able to
explain it.

To put a different arm on device:
`TIER0_THEME=res://src/Presentation/assets/composition_spike/tile_themes_boundA.yaml tools/tier0_harness/build_review_app.sh`

**Side by side**, `evidence/sheets/`: `held_vs_unheld_A`, `held_vs_unheld_B`,
`top_plane_A_vs_B`, `lit_vs_unlit_B`, `solofloor_pair`.

**The questions, in the order they matter:**

1. **§3 — does a wall get a side?** Six seats asked for one, none having seen §3. Without it a
   north–south corridor shows two fields of wall-top and no face, and the thickness answer stays
   no however good the material is. This is a one-way door and it is the road ruling.
2. **§6.3 — the baked arm exists now, and it outranked everything.** §6.4 recorded that its own
   ratification "is not a victory over a baked arm, because no baked arm existed to beat" and
   that "the comparison §6.4 set out to run remains unrun". This session built one as its plant
   and six blind seats ranked it first three times and never below third of five — while two of
   them culled it correctly as `key-light`. §5.1b. Evidence, not a ruling, and adverse.
3. **§12.1 — is an occluded wall/floor edge an outline?** Without it the corridor was unreadable.
   With it, it is a second linear system where §12.1 reserves one.
4. **Is the composed material worth continuing with at all**, given that it took six rounds to
   reach "flat pattern with a path tinted through it"?
5. **The §6.4 survivors carry a baked dark ring** (§5.5). §12.1 is LOCKED. A blind seat found it
   unprompted.

**Taken with the tiles-pro audit beside this report.** This session does not conclude.

---

## 8. EVIDENCE

| what | where |
|---|---|
| the composite script | `compose_walls.py` |
| parts manifest — every provenance, or its MOCK label | `PARTS_MANIFEST.json` |
| 12 captures per round, each with its rig log | `evidence/*.png`, `evidence/*.log` |
| capture manifest, commit + per-capture sha256 | `evidence/manifest.json` |
| the pre-fix capture that forced §3 | `evidence/finding_before_edge_occlusion.png` + `.txt` |
| positive controls for both variant fixes | `evidence/controls/` |
| six blind critic transcripts + parsed verdicts | `evidence/critic/` |
| the rounds in one table | `round_table.py` |
| the repetition charge, measured on the capture | `measure_field.py` |
| the palette honesty claim, checked | `verify_palette.py` |
| side-by-side pairs for the eye | `evidence/sheets/` |
| segments assembled outside the engine | `segments/` |

Every capture ran under one identical rig, echoed by the engine into its own log:
`ambient=1a1a22 light=ffb066 energy=1.6 radius_tiles=5.5 tile=32x32` — **all values UNDERIVED,
§6.2 and §4.3 PLACEHOLDER**, carried in every log so no capture can circulate without them.

---

## 9. REFUSALS HELD

- **Did not generate.** Zero API calls; the bin is the ledger.
- **Did not promote anything to corpus.** `MOCK` is in every composed filename.
- **Did not polish the overlays beyond the held question.** Every overlay change this session
  made was driven by a named critic charge, not by taste.
- **Did not instrument a register clause** (§13.4). There is no held-ness score. Everything
  measured here is mechanical — repetition, luminance, palette membership — and the register
  questions went to a prose seat and from there to you.
- **Did not execute a flip list that violated a locked clause**, three times.
- **Did not conclude.** The road ruling is yours.
