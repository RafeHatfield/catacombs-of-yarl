# The object projection — a §1.1.4 one-way-door gate

**Rafe walks three candidates on the handset and rules ONE as the game's object law.** No seat
rules this (§13.2, the eye rules on device); the instruments below order and expose, they do not
decide.

---

## ⚠ The door is wider than it looked, and §3 already has an opinion

The session exists because approving the marker alone would have silently ruled the 3D
orientation of every object in the game. Reading §3 sharpens that:

> **§3, RATIFIED 2026-09-09:** *"Objects and walls present exactly two visible planes: a **front
> face** and a **top surface**. The floor stays flat."*

That clause already covers **objects**, not just walls. And the marker's current projection shows
**three** planes — a skewed top, a front face, and a dark right side.

So approving it would not merely have picked a projection. **It would have ruled a three-plane
object grammar against a two-plane wall grammar**, inside a clause that says two.

### What that does to the candidate list

| | as briefed | planes | §3 |
|---|---|---|---|
| **A** | oblique-south, top and one side sheared back | 3 | ⚠ against |
| **B** | low dimetric-south, top + face + a sliver of side | 3 | ⚠ against |
| **C** | the marker's current — the control | 3 | ⚠ against |
| **W** | *(added)* top + south face, no side | **2** | ✅ the only one it permits |

The brief's own prior — *"its top shares the floor's plane; its visible side is the same
south-facing reveal the walls use"* — is literally **W**, and W was missing from the list. It is
added rather than substituted: A and C are still built and walked, flagged against-§3, because a
ratified clause can still be the wrong call and the walk is where that gets tested.

### B is collapsed into C, by measurement

Generated at the tall archetype, B and C are both *"three planes at a modest angle"*. They are
distinguishable as pictures and **identical as a law** — they would produce the same clause text.
Two candidates that rule the same thing are the *"two plants that look alike"* failure in another
costume. B's generation is kept as evidence (ids 9871/9872) and is not given a scene.

---

## The five archetypes

Identical placements across all three candidates, so the projection is the only variable. All
inside the lit radius, because §13.8 refuses an object below the perceptual floor and an object
nobody can see cannot decide anything.

| archetype | object | cell | what it stresses |
|---|---|---|---|
| tall vertical | standing stone | (4,13) 1×2 | does its side read against the wall's, or fight it |
| low horizontal | chest | (10,12) | the classic oblique case; top-to-face ratio |
| **round** | **barrel** | **(9,14)** | **no flat face to hide behind — cheats show** |
| wide flat | altar slab | (6,14) 2×1 | mostly-top; does the top really share the floor plane |
| **against a wall** | **rack** | **(11,12)** | **Rafe's "bookcase" instinct, asked directly** |

The chest is at (10,12) and **not** at the corridor mouth (8,12): blocking that cell seals the
trunk, and the scene builder's own guard refused the first version of these scenes for exactly
that. The rack's north neighbour (11,11) is solid, so the wall's south face is directly behind it.

---

## What the two decisive archetypes showed

**AGAINST A WALL — the clearest discriminator.** W's rack has a flat top that runs **parallel to
the wall's courses**; it agrees with the masonry behind it. A and C both tilt their top up to the
right, **across** the horizontal coursing. That is the "bookcase against the wall" tension
arriving as geometry rather than as a feeling: two projections in one frame, the wall's and the
object's, disagreeing.

**ROUND — the honest one.** A barrel has no square face to fake with, so the amount of **lid** you
see states the camera angle outright. W shows the most lid (steepest camera, most top-down); A
and C show more body and less lid. Whatever is ruled, this archetype will say so plainly, and it
is the one to look at if the others feel close.

---

## The instrument, and its own failure

`tools/tier2_props/measure_projection.py` reads the plane count three ways.

```
class          archetype   symmetry  top-shear  seam-tilt   reads as
W  two-plane   stone         0.982      0.018      0.789   2 planes
W  two-plane   crate         0.995      0.000      0.000   2 planes
W  two-plane   barrel        0.947      0.000      0.062   2 planes
W  two-plane   altar         0.961      0.000      0.037   2 planes
W  two-plane   rack          0.885      0.000      0.000   3 planes
A  oblique     stone         1.000      0.000      0.000   2 planes
A  oblique     crate         0.900      0.073      0.073   3 planes
A  oblique     barrel        0.911      0.071      0.107   3 planes
A  oblique     altar         0.511      0.120      0.026   3 planes
A  oblique     rack          0.850      0.083      0.021   3 planes
C  current     stone         0.931      0.079      0.381   3 planes
C  current     crate         1.000      0.000      0.040   2 planes
C  current     barrel        0.917      0.056      0.111   3 planes
C  current     altar         0.628      0.069      0.004   3 planes
C  current     rack          0.480      0.318      0.348   3 planes

W  4 of 5 read as TWO planes   (symmetry 0.954, shear 0.004)
A  1 of 5                      (symmetry 0.835, shear 0.070)
C  2 of 5                      (symmetry 0.791, shear 0.104)
```

⚠ **The seam measure is not trustworthy and does not order the candidates.** It put the
two-plane stone at 0.789 — a worse tilt than anything in the oblique row — and the oblique stone
at 0.000, the opposite of what the contact sheet plainly shows. On textured stone the strongest
luminance step is a **joint**, not the top/front seam. It is reported with the failure attached
rather than tuned until it agrees, because a measure that disagrees with the picture is evidence
about the measure.

Symmetry and top-shear read the silhouette honestly and match the sheet. **Neither rules.**

---

## On the handset now

| candidate | bundle | scene | verified |
|---|---|---|---|
| W two-plane | `…catacombsofyarl.projW` | `tier1_projection_W` | ✅ booted, rig live |
| A oblique | `…catacombsofyarl.projA` | `tier1_projection_A` | ✅ booted, rig live |
| C current | `…catacombsofyarl.projC` | `tier1_projection_C` | ✅ booted, rig live |

⚠ All three stamp **SKIPPED-REVIEW**, deliberately and visibly. No frame-critic verdict covers
them and none should: §13.2 gives this ruling to the eye on device, and a critic verdict here
would be a second opinion on a question seats are not allowed to answer. The phone says what
these are.

---

## What is asked

**Walk the three and name ONE projection as the game's object law**, citing which archetypes
decided it — especially the round one and the against-a-wall one. That ruling becomes a §3-level
clause every future object cites.

If none of them is right, that is also a ruling, and the archetype that made it obvious is the
thing to say.

### Not this session

The marker and props are re-authored at the ruled projection; the props-pass §12 walk resumes on
projection-correct objects; the ruling is written into the bible as object-projection law.

⚠ **Nothing here entered the game's prop set.** Ids 9850–9872 are a reserved review block
referenced by these three scenes and nothing else — no props manifest lists them, no placer
places them, no game scene names them.
