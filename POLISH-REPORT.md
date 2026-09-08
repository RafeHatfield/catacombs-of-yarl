# The polish list — overnight run, 2026-09-07, and the rulings of 2026-09-08

> ## ⚠ THIRD PASS, 2026-09-08 — the precheck clears, the VOTE does not
>
> Both rulings are implemented, proved and banked (bible **§13.12** assertions derive; **§13.13**
> a binding term needs a measured noise floor). The ruled sequence ran as far as it could:
>
> | step | outcome |
> |---|---|
> | precheck on the window | **CLEAR** — 11/11 ruled fixes, the pin now measured on the build |
> | A+B+C build | **built** |
> | three-seat vote | **FAIL** — rank majority yes, flags no |
> | install | **not reached** |
>
> **The vote, `r001-polish-abc-install`:**
>
> | seat | build rank | reference | above ref | flagged the build | plant |
> |---|---|---|---|---|---|
> | 1 | 1 | 2 | **yes** | no | CAUGHT |
> | 2 | 3 | 1 | no | **yes** | CAUGHT |
> | 3 | 2 | 3 | **yes** | **yes** | CAUGHT |
>
> **2 of 3 above the reference — the majority holds.** But two of three seats flagged the build,
> and *"no unrouted flags from any"* is deliberately not a majority test. So the gate refuses, and
> the disposition is yours: **routing is the human gate's and the builder can never route.**
>
> **Rank's error bar, measured as ruled** (`docs/RANK-NOISE-FLOOR.json`): same bytes, five
> independent seats, ranks `1, 1, 1, 3, 3` — **a 40% flip rate**. The vote's own round showed 1 of
> 3 dissenting, consistent with it. That number now travels with the threshold.
>
> ⚠ **One flip asked to move the ratified rig on a disproved premise.** *"The falloff is not
> centred on the lamp … open floor at x=190,y=490 … x=630,y=490 … nothing occluding either."*
> **Both named points are WALL cells** (tiles (3,11) and (9,11), 27.7 and 40.4 — 12.7 levels
> apart, not near-black against pale cream). On actual floor the asymmetry near the lamp runs the
> *other way*: left of the figure is brighter at 1 tile (178.0 vs 159.4) and at 2 (124.9 vs
> 103.2). The mild right-side excess past three tiles is the room's geometry. Recorded against the
> round as an added note; the seat's own answer is untouched. **Third time this session a seat's
> explanation failed measurement while its percept stood.**
>
> ⚠ **The plants are correlated.** The axis-matched morgue set for `combined`/`tonal` has one
> member, so every seat in both runs drew the same plant. All eight caught it — but that is not
> eight independent observations. A second tonal cull would fix it.
>
> ---
>
> ## ⚠ SECOND HALF, 2026-09-08 — nothing installed, and two blockers say why
>
> Rafe's five rulings are implemented. **The phone was not flashed**, for two reasons, neither of
> which I was willing to route around:
>
> **1. The device gate's ruled-fix pin.** `GATE-CONDITIONS.json` pins
> `const:POLISH_LANE_GAIN==0.6`. B and C are stacked on A, whose round stays FAIL by ruling, so
> their builds carry the unratified 0.3 and the precheck refuses. **The critic gate OPENED for B**
> — that part worked — the device precheck is a separate gate and it closed.
> Editing the registry to pass my own build is LOOP-PROCESS §4.3's named failure, so it is
> untouched. ⚠ **And the pin now asserts something false:** its rule is *"wear modulates the same
> stones; it never replaces their identity"*, and at 0.6 the on-lane masonry measures **0.1338,
> below §13.8's 0.1440 floor.** §6.2's re-derivation rule fired under it when #174 corrected the
> lamp.
>
> **Unstacking does not help, and this was measured rather than assumed.** A committed negative
> control (`art/polish-bc-install`, round `r001-polish-bc`) builds B and C on the ruled 0.6 with
> A's levers nulled: it ranks **2 of 4, below the reference**, where A+B+C ranks **1 of 4, above
> it**. A's floor work is load-bearing for the frame's rank.
>
> **2. Rank is not stable across seats.** C's round was re-run on a frozen tree so its verdict
> would describe the exact bytes that would install. Same frame (`839fb12f`, "picture moved mean
> 0.000 / worst 0"), and it came back **2 of 4 where it had been 1 of 4** — the build and the
> reference swapped places with no pixel changing. Under the newly ratified PASS-INSTALL rule that
> is FAIL, so C does not install either. The rule is **held frozen and impeached in place**
> (SKILL.md), not re-tuned — LOOP-PROCESS §8.
>
> Done from the rulings: PASS-INSTALL implemented, banked with its reason, and proved (gate cases
> 15 → 19, three of them refusals); guards scoped to the item, cutting at the last PASS; #186
> closed with its premise disproved and re-filed as **#193**; C's flips routed to **#194** with the
> ruling quoted per item; #184's share re-derived and its "doubling" claim **retracted**.
>
> **The unblock is one line from you** — ratify the lane at 0.3 so the pin moves with it, or
> re-express the pin as the law rather than the value. Trees and verdicts are ready.

---

# The polish list — overnight run, 2026-09-07

Branch `art/polish-list`, off `main` at `ad19a72b`. Three items, strict order, one round each,
judged by the frame critic against the capture you approved on the room walk.

**Nothing went to the phone.** No item reached PASS, and PASS is what the install gate needs. The
handset still has whatever it had before this session. The short version of why: **every item's
own defect is fixed and measured, and every blind seat then declined to ship the frame for
reasons belonging to other lanes.** That is the situation PASS-WITH-ROUTED-ITEMS exists for, and
routing is yours — the builder can never route.

The one thing to read first, if you read nothing else, is **§5 — the judge was broken, and I
fixed it mid-run**. It threw a good round away, and correcting it changed how one historical
round should have been read.

---

## 1. Where each item landed

| item | issue | verdict | rank in deck | plant | its own exit | on the phone |
|---|---|---|---|---|---|---|
| **A** | #184 polish gain + wall-base occlusion | **FAIL** | 2 of 4 | CAUGHT | **met, measured** | nothing |
| **B** | #185 corridor-mouth face mask | **FAIL** | **1 of 4** | CAUGHT | **met, measured** | nothing |
| **C** | #183 hero light response | **FAIL** | **1 of 4** | CAUGHT | **met, measured** | nothing |

Items B and C both ranked **first of four — above the capture you approved** — and B had nothing
flagged in it at all. They still read FAIL because the seat put nothing in SHIP, and PASS is
SHIP ∧ rank.

Housekeeping, done up front as asked: all nine scenes that declared legibility points without
`bound_lum` now have them.

---

## 2. Item A — #184, the worn lane and the wall base

**Your verdict:** *"the worn lane is slightly too shiny and its shine washes out the wall-base
occlusion shadow, so walls lose mass where the lane meets them."*

### What was actually happening

The contact occlusion is **subtracted from the floor's albedo** in whole ladder rungs — five
rungs, 66 luminance units, at the seam's deepest row. The polish specular is **added in the
light pass**, and it had never heard of the occlusion. The seam was being taken out of the stone
and then handed back, with interest.

Measured on your approved capture, at the wall foot, north edges:

| | flank cells | the lane cell | lane/flank |
|---|---:|---:|---:|
| contact seam, Weber | 0.3085 | **0.0094** | **0.030** |

97% of the boundary gone exactly where the player walks, and below the perceptual floor. That is
not an inference: nulling the specular entirely takes the lane's seam to 0.4492, **above** the
flank's 0.3981. The specular was the whole cause.

### What changed

1. **The contact boundary now attenuates the specular**, keyed to the occlusion's own depth —
   the same rule this file already applies to a joint (shine in proportion to how filled it is)
   and to a crack. It cannot become an outline: it exists only where the boundary is drawn, only
   on the side a wall actually adjoins, and its profile is the shipped sprite's own alpha ramp.
2. **The lane's gain steps a fourth time**, 0.6 → 0.3. It has been stepped at a gate three times
   before for this same complaint (1.9 → 1.0 → 0.6).

| | before | after |
|---|---:|---:|
| specular's share of delivered floor value, ≤2 tiles | 22.4% | 18.8% |
| worst cell | 32.8% | 29.2% |
| on-lane masonry (floor 0.144) | 0.1295 — **out** | 0.1602 — **in** |
| lane-vs-flank | 0.2354 | 0.3732 |
| wall-base seam, lane/flank | 0.030 | **0.639** |

**A finding you should see: the share figure in #184 was badly stale.** The issue carries
10.8% / 12.6% / 0.0%. Re-measured on the ratified rig it is **22.4% / 13.5% / 0.0%** — the near
band had *doubled* since, because #174 fixed `delivered` being pinned at 1.0 (so Ruling 70's
superlinearity started running for the first time) and the rig was re-ratified after. The polish
at the standing case was carrying twice the share anyone believed.

### The wrong lever, and how one round found it

The first arm cut the **global** `polish_gain` 1.0 → 0.55. It cleared the window, and the seat
caught what it cost immediately: the global gain also scales ordinary stone, so the lamp pool's
core fell 174.0 → 163.0 and the seat read *"the pool does not localise on the figure … the light
reads as room ambient."* Your verdict named the **lane**. `polish_lane` is the lane. The global
gain is back at its ratified 1.0.

### Why it stopped at FAIL

The third round's seat asked for two things I refused, and the refusals are on the record:

- *"Restore a distinct core … the floor within one tile of the figure should not be within 10
  levels of the floor three tiles out."* **Measured: it is 102.3 levels apart**, against your
  approved frame's 109.2. The falloff is intact to within 7%. The seat's percept (a flattening)
  is real; its explanation (a lost radial peak) is false, and the banked law says explanations
  are measured before anything is built on them. The remedy would have been the shine you ruled
  down, or the rig.
- *"Hold the joints darker than the stone through the light pass."* **§13.4.1 already ruled this
  REFUSED**, twice. This is the third asking. Recorded as a make-it-read item; the clause is not
  reopened.

---

## 3. Item B — #185, and #186 is a different bug

**This was a real correctness bug, and it was not where the brief expected it.** `WallMaskPolicy`
is correct — its exhaustive 16-mask test still passes. The mask was right; the **placement** was
wrong.

`Tier1BoundaryWall` builds the wall's front face as a *child* of the tile sprite so the cap can
keep the cell's base. The child was `Centered = true`. The tile sprite is `Centered = false`,
anchored at the cell's **top-left**. A centred child at local (0,0) therefore draws its texture
centred on the cell's **corner** — half a tile up and half a tile left. **Every reveal in the
game was a half-cell out of place.** The binding sprites had the identical defect, which matters
more: §7.1's straps and pins are what carry the read at 1×.

It was invisible while the neighbour was also wall. At a corridor mouth the neighbour is *floor*,
so the face landed on walkable ground — which is why you found it at the bottom of the hallway
and nowhere else.

**Bisected without changing a line of code**, using a flag that already existed (the face only
becomes a child when the cap is present). Corridor mouth (8,11), the floor cell in the doorway:

| arm | left half | right half | biggest column step |
|---|---:|---:|---|
| with the cap | 135.6 | 59.3 | **52.8 at column 32 — the exact half-tile** |
| `--wall-cap` omitted | 135.6 | 82.2 | 30.1 at column 4 (the west occlusion, correctly on the edge) |

After the fix that cell is **identical to the arm that never had the defect**.

The engine now checks it. `Contained` is the fourth cross-check in this class and it **refuses**
like the other three — `edge_check` says the engine agrees with the composer about the bond,
`stone_check` about the material, `occlusion_check` about the rungs, and **none of them asked
where**, which is how a half-cell error survived all of them, every unit test, and a device gate.
Demonstrated firing on the old behaviour:

```
boundary wall: REFUSED — the face at (3,1) is drawn outside its own cell:
child rect (-16, -16)+(32, 32) against the cell's (0, 0)+(32, 32)
(centred=True under a parent centred=False).
```

### #186 — checked against #185 as the issue asks, and it is NOT the same thing

Across this fix, #186's box (275–380, 640–710) is **byte-identical — zero pixels changed** —
while the fix moved 4.52% of the frame elsewhere.

**Both of #186's narrowing properties are false:**

- *"its left edge lands mid-tile, which no tile-laid family can produce."* The ashlar family is
  not tile-laid in that sense. `stone_origin` measures a **spanning stone from the tile boundary
  it crosses**, so a stone beginning back in the previous tile is the bond working as specified.
  Mid-tile stone edges are the design.
- *"the crack layer terminates on it."* It does not. A single connected component runs
  x 240 → 429 straight through the box, entering and leaving well past both edges.

What is actually there is **floor** — a run of pale spanning ashlar stones with their joints
visible. So #186 is a legibility finding, not a placement one, and its written exit ("resolve it
into a named object with a hard top edge and one side face, or delete it") **cannot be satisfied
as stated, because there is no object.** Re-scoping it is yours.

⚠ **Three independent blind seats have now named that patch**, including one tonight that had
never seen the issue. Under §13.4.1's shape that is not a vote — it is a report that the
treatment is not reading as intentional. It is the strongest make-it-read signal on the list.

---

## 4. Item C — #183, the hero

**Your ruling:** *"warmest is never brightest"*, delivered as a light-response term on the sprite
— not a rig change, not an albedo repaint. That is what shipped.

**The defect was worse than the issue records.** #183 has his p95 within a level of the floor. On
his own pixels he read **p95 249.13, max 249.98** against lit floor at p95 203.51 / max 207.51 —
forty levels above the ground and the brightest thing in the picture.

⚠ **The obvious measurement is the wrong one, and it would have told you nothing.** His *cell*
reads p95 207.51 at every setting, because the sprite is smaller than the tile and the block's
high tail is the floor around him. His pixels are isolated against the null arm instead: the 950
that move when the material is enabled are exactly the ones it lights — and that doubles as the
scope control, since **every one of them is inside his cell and nothing else in the frame moves.**

The lever is §6.2's ruled shoulder curve with the ceiling set below the lit ground's peak, applied
hue-preserving and post-attenuation.

| ceiling | sprite p95 | sprite max | vs floor max | vs floor p95 |
|---|---:|---:|---:|---:|
| null | 249.13 | 249.98 | +42.47 | +46.47 |
| 0.78 | 187.00 | 212.78 | +5.26 | +9.26 |
| 0.74 | 179.74 | 207.00 | −0.51 | +3.49 |
| **0.70** | **172.18** | **200.23** | **−7.28** | **−3.28** |
| 0.66 | 164.33 | 192.28 | −15.24 | −11.24 |

0.70 is the first setting where his brightest pixel is below **both** the ground's peak and its
p95. A tie is not an answer to "never the brightest".

**On "warmest" the two readings disagree and both are here.** On his warmest pixels he is clearly
warmest in view — p95 of (r−b) 194.0 against the floor's 126.0. On the **mean** he is not: 94.96
against 107.44, because his palette carries cool metal and a dark outline the floor has no
equivalent of. That clause is carried eye-side; it is a note for your walk, not a score.

Applied to the **player only** — §10 rules the player unit, nothing rules a monster's response,
and giving every entity a hero law would legislate for a population that walk never looked at.

No flip in the round says the hero is washed out or bright. The item's own defect is gone from
the seat's reading of the frame.

---

## 5. ⚠ The judge was broken, and fixing it changed how a past round should have been read

**Item A's first round went VOID on a judge that was working.** The seat answered
`FLAGGED: 1, 2, 3, 4` — the plant among them, flagged explicitly and at length — and shipped
nothing. That is a clean catch. The runner recorded `flagged: false` and threw the round away.

The parser searched the **whole body** for `NONE`, and the seat's reasoning contained *"the
biggest object in the room carries **none** of it."* One word of prose ate the answer.

It is bible §13.11 again, in the review layer's own parser: **an instrument's input must be no
wider than the thing it measures.** And the failure direction is the unsafe one — a caught plant
reads as missed, and two of those fire the broken-judge guard and stop a line over a judge that
never failed.

**I made the fix twice, and the second half is the important one.** Reading the *numbers* from
the whole body was no better: on the next round the seat answered `FLAGGED: 1, 3` and wrote
*"the mortar grid plainly visible in 2 and 4 is gone"*, and the parser returned `[1, 2, 3, 4]`.
Harmless there — the plant was in the real answer — but the failure it can produce is **a plant
recorded as flagged that the seat never flagged**, which is a soft critic passing its own
self-test. Both the sentinel and the numbers now come from the answer line.

`prove_sentinel.py` drives the real parser through both directions (a genuine `NONE` still
returns nothing, so it has demonstrated it can fail) and re-parses **every transcript ever
committed**. Nothing is rewritten. Two recorded rounds read differently under the correction and
both are printed rather than absorbed:

| round | recorded | corrected | its verdict |
|---|---|---|---|
| `r001-polish-a-184` | plant MISSED | CAUGHT | VOID — the round that found the bug |
| `r002-worktree-session-2026-08-29` | plant CAUGHT | **MISSED** | FAIL |

**The second one is a wall-lane round from 2026-08-29 that a correct judge would have VOIDed.**
It shipped nothing and opened no gate, so nothing walked on it — but its findings *were* read,
and they should not have been. That is the impeachment, not a repair.

`r005-combined` — the PASS that seeded `approved_capture` — recomputes **CAUGHT**. The reference
you approved stands.

A second defect of the same family fell out of the same reading: `every_frame_flagged` compares
`len(flagged) == len(rank)`, and seats repeat their numbers when they elaborate per frame, so
**that signal had never once been able to fire.** It is recorded and never scored, so this
corrects a report rather than a verdict. It fired for the first time tonight, twice.

---

## 6. ⚠ The stall guard on lane `combined` is arithmetically dead

Its best is already `(rank 1.00, shipped, 0 unresolved)` — the maximum a four-frame deck can
produce. No future round can beat that on any of the three terms, so **three more readable rounds
on that lane would STOP the line regardless of the art.**

That is §13.11 a fourth time, inside the guard §13.11 was written into: `rank_score` was fixed for
saturating, and the tuple that replaced it saturates too.

I ran each item on its own lane (`polish-a-184`, `polish-b-185-186`, `polish-c-183`) rather than
on `combined`. **This is a judgement call and I want you to see it as one.** My reasoning: three
different defects, three different axes, three different exits are three lines of rounds, and
inheriting a saturated counter across them would have handed you a STOP that was about the
instrument rather than about the work. No guard was firing on `combined` when I started, nothing
was deleted, and its history is untouched. If you'd rather these had been one lane, the verdicts
are all on disk and re-lane-ing them is a rename.

---

## 7. Housekeeping — nine scenes now carry `bound_lum`

Since the §13.11 ruling, legibility is an absolute delivered-luminance bound with **no default**,
and `CorridorReviewSceneBuilder` throws without one. Only `tier1_combined_review` had been
converted, so the other nine scenes were unusable — any round reaching for a second station would
have died at parse time.

Derived by the ruled formula applied verbatim (nulled shoulder, ratified rig, retired ratios),
with the provenance written into each point.

⚠ **Five points across four scenes now read FAIL, and nothing was tuned to stop them:**
`tier1_floor_review` (8,12) and (3,7), `tier1_floor_traverse_roomb` (8,10), `tier1_wall_review`
(13,12), `tier1_wall_standing` (3,17). Every one is a point declared *dark* against the **old**
rig, on ground the re-ratified rig now reaches — the same finding round 30 recorded for the
combined scene's (11,13), where the answer was to move the probe to ground genuinely past the
delivered reach. I have not moved these: moving a declaration is a judgement about what the scene
is asking, and it belongs to the round that needs the scene.

---

## 8. Captures

Everything below is in `tools/tier1_floors/evidence/`.

| what | file |
|---|---|
| the seeded reference, reproduced byte-for-byte at `ad19a72b` | `baseline_r0.png` (sha `8745c556`) |
| item A null control — byte-identical to the reference | `a_null.png` |
| item A, polish nulled (the control #184 asks for) | `a_nopolish.png` |
| item A gain sweep | `a_g040/055/070/085.png` |
| item A lane sweep | `b_l030/040/045/060.png` |
| item B bisect, cap omitted | `c_nocap.png` |
| item B, after the placement fix | `c_postfix.png` |
| item B refusal demonstration (log only; the frame is a refused build) | `c_refusaldemo.log` |
| item C null control — byte-identical to `c_postfix` | `h_null.png` |
| item C ceiling sweep | `h_c066/070/074/078/085.png` |
| **the frame item C was judged on** | `combined.png` (sha `839fb12f`) |

Verdicts: `.claude/skills/frame-critic/history/r00*-polish-*.json`, with transcripts beside them.

Instruments added (they gate nothing): `measure_wall_base_occlusion.py`,
`measure_specular_share.py`.

---

## 9. What I did not do

- **Did not install.** No PASS, and the gate needs one for this exact build.
- **Did not route.** Three rounds' flip lists are dominated by items belonging to the wall lane,
  the floor lane, and to #186. Routing needs your quoted ruling and a named destination.
- **Did not touch the ratified rig**, and refused two seat flips that asked me to.
- **Did not reopen §13.4.1** when a third seat asked for joint contrast at full light.
- **Did not move a legibility bound** to make a capture pass.
- **Did not re-run B or C** after their FAILs: the builds had not changed, so a second round would
  have tripped the no-change guard on the same picture.
- **Did not re-scope #186**, though its stated exit is now known to be unsatisfiable.

## 9a. CI — read, not badge-checked

Every PR in the stack shows **balance: fail**, and that is the inherited red CLAUDE.md documents,
not something this branch introduced. Confirmed by reading the log rather than the badge, as the
rule requires:

- **Fast tests pass** on the base PR: `Passed! - Failed: 0, Passed: 2518, Skipped: 1`.
- The red step is **Balance acceptance suite**, and its failing set is
  `depth3_orc_brutal` ×5 FAIL, `depth2_orc_baseline` + `_keen` FAIL, three `_vicious/_fine/
  _masterwork` WARN.
- **`main`'s own run at `ad19a72b` (run 34184047703) has that identical set.** No new failure.

Nothing in this branch touches balance, scenarios or the logic layer — it is presentation,
shaders, scene legibility declarations and the review layer.

## 10. What I would put in front of you first

1. **The `r002-worktree-session-2026-08-29` impeachment** (§5). A round was read that should have
   been void.
2. **#186's re-scoping** (§3). Its exit cannot be met as written, and three seats keep naming it.
3. **Routing**, so items B and C can close — both ranked above your approved frame.
4. **The dead stall guard on `combined`** (§6), before the next lane inherits it.
