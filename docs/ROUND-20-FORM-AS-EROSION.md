# Round 20 — form as erosion, and the axis that could not hold a line

**Outcome: REPORT.** The ruling froze it: *any failure names the illumination and the axis.* Both
are named in §6, and the axis is not the one anyone expected.

Two valid seat rounds ran, on either side of a defect the round found in its own lever.

---

## 1. What was built

Under the ruling: the route is **worn, never built** — the Boundary is found-and-annexed,
administration is thin at this depth, so traffic carved what it needed and nobody laid a path.

**The travel axis** is derived from the traffic field rather than carried beside it: one field, one
source of truth, both painters reaching the same answer from the same numbers.

| lever | what it does | measured |
|---|---|---|
| **stones ground flatter** | a walked stone's value collapses toward the material median — symmetric, so contrast goes without anything darkening | face spread on trodden ground **22.31 → 12.84** |
| **directional compaction** | feet cross the joints lying *across* a route and pack them shut; a joint running *with* it stays open and dark | N-S route: head joints 59.88 below the stone, bed 21.45 — **ratio 2.79**; E-W route: **0.38**; off-route **1.00** |
| **threshold hollows** | dished basins at mouths, genuinely lower with a rim that shadows; mouths derived from the map's own shape, salted so no two are the same dish | **13 mouths** on the review scene |
| **joint compaction** | composes unchanged | — |

The **arris-rounding** version of the directional lever was tried first and **measured worse** —
bed/head 1.111 where it should have fallen below 1.00. The reason is worth keeping: on trodden
ground the joint has already been packed *up* toward the stone, so darkening the face pixel beside
it moves that pixel *away* from the joint's value. The two levers were fighting. `DEFORM_ROUND` is
retired at its null with the reason recorded rather than deleted.

## 2. The seat runner can no longer be read early

Fixed first, as ruled. The **plant seat now runs first**, so a void round costs one seat instead of
two and there is nothing to read early; candidate transcripts are **withheld** under a
`.WITHHELD.txt` name until the control catches the plant. A void round's transcript keeps that name
and gains a banner saying its findings are not evidence. Round 19's is stamped retroactively.

*A rule that depends on my restraint is not a rule. This one depends on the filenames.*

## 3. The defect the round found in its own lever

Round 20 (**VALID**) reported:

> *"The corridor floor doesn't run its courses along the direction of travel; it runs them across,
> exactly as the room does."*

That sent me to map the derived axis over the scene, and the map was wrong:

```
   #####|-|//-/#####        the chokepoint column, which plainly runs
   ######-#///|#####        NORTH-SOUTH, was labelled  -  E-W
   ##|/#|./#|||#####        down its whole length
```

**The first `travel_axis` took the perpendicular of the traffic gradient**, and that is undefined
in exactly the place the floor most needed it. In a one-tile corridor both across-neighbours are
wall, so the across-gradient is *identically zero* and cannot be measured; the only signal left is
the variation *along* the route, which the perpendicular then reads as a route running the other
way.

**No plant would have caught this.** The plants ask whether direction is *expressed* — `no_erosion`
and `isotropic_erosion` both fired correctly throughout. They cannot ask whether it is the *right*
direction. The lever was live, measured, plant-tested, and aimed ninety degrees away from the truth.

Rebuilt on continuation instead of gradient — *the route runs where the traffic continues*, summing
the two neighbours along each of the four axes a pixel grid allows. The corridor now reads `|` down
its whole length.

## 4. Round 21, with the axis corrected

**VALID.** And the answer did not change:

> *"The ground told me nothing. I read the route entirely off the walls. Inside the lamp, the floor
> is directionless. It is a flat field of identical blocks in every direction from the figure."*

## 5. The instrument, both times: it clears

| | round 20 | round 21 (axis fixed) |
|---|---:|---:|
| pairs | 6 | 6 |
| lightness alone | 0.903 | — |
| **lightness + colour** | **13.007** | **12.996** |
| ruled floor | 4.777 | 4.780 |
| null (median of 4) | 3.606 | 3.657 |
| both conditions | **PASS** | **PASS** |

Plant caught (→ 22.891); the absorbed control swallowed by the luminance matching, as its design
requires.

## 6. The illumination and the axis, named

**Illumination: 92.5 / 255 — 36% of full**, pooled over the three stations, the same population
round 18 established. Not a dark-delivery failure; §13.9 is not implicated.

**Axis: the spatial coherence of the derived direction.** This is the number that explains
everything above, and it was not measured until the seat's third refusal:

| | |
|---|---:|
| adjacent walkable tile pairs sharing a travel axis | **24 of 70 — 34%** |
| the chokepoint column, tiles 11–15 | 3 of 3 — **100%** |

**The axis flips two times in three between neighbouring tiles.** A route reads because it is a
*continuous line*; a grain whose direction changes from tile to tile cannot accumulate into one,
however strong the treatment keyed to it is and however well it measures per tile. And the one
place the axis *is* coherent is a one-tile corridor — where the walls have already told the player
everything.

So the failure is not amplitude (the instrument clears by 2.7×), not illumination (36% of full),
and not the levers (all four fire, all four measure on their own axis). **It is that a per-tile
field cannot draw a line.**

## 7. What that implies, stated once and not acted on

A route is a *path-scale* object and every lever in this session has been keyed to a *tile-scale*
scalar. Wear derived per tile from an accumulated field is the right physics and the wrong
granularity for drawing something a viewer follows. Two shapes could supply it — a route polyline
carried from the level graph and drawn *as a line* across tiles the way the crack network already
is (which is the one field-scale system on this floor that seats have consistently praised), or a
coherence pass that smooths the axis field until neighbours agree before anything keys to it.

Both are changes to what the traffic system *emits*, not to the floor's material. Neither is
started; the round is bounded and this is the report.

## Evidence

| | |
|---|---|
| round 20 seats (pre-fix), VALID | `evidence/seats/SEATS-r20.json` |
| round 21 seats (post-fix), VALID | `evidence/seats/SEATS-r21.json` |
| pooled path signal, both rounds | `evidence/PATH-SIGNAL.json` |
| fourteen field plants, all firing | `evidence/ASHLAR-FIELD.json` |
| the captures | `evidence/r18_approach.png`, `r18_choke.png`, `r18_roomb.png`, `r18_room.png` |

Shipped path identical on three arms; `paint_check=96/OK`, `mouths=13`, `polished=74`;
`UNADDRESSABLE` 0; fast suite 2510/0.

**The paint check earned its keep again**, refusing a capture at cell (2,7): composer
rgb(90,107,100) against engine rgb(102,121,113), one rung apart, both arithmetically correct.
Order is load-bearing — flatten is a *proportional* pull toward the median and chipping is a
*fixed* subtraction, so running them in the other order gives a different pixel with no error
anywhere to point at.
