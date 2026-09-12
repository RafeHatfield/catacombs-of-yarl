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


---
---

# ROUND TWO — the test fixed, the candidate Rafe named, five scenes for the handset

*Round one's package above stands as history. Rafe walked it (2026-09-11) and ruled the test
itself flawed; this round rebuilds the instrument and adds oblique. Session 2026-09-12, commit
`e0e383f2` and after.*

## ⚠ Rafe's round-one verdict, and what it did to the law

**§3's object clause is PROVISIONAL, not law.** *"Objects and walls present two planes"* was
drafted from the Oryx/SPD study before any object existed here; the 2026-09-09 ratification
walk was of WALLS, on a scene with no objects in it. So §3 is ratified for walls and this ruling
decides it for objects. Round one's package above cites the clause as settled and it is not;
nothing below does.

**The test was flawed three ways.** The standing stone was the same wrong object in every build;
C mixed projections within one scene; objects within a build disagreed with each other. So no
build could be judged for whole-scene feel — which is the entire question.

**The read that survives.** True isometric reads wrong on this floor. **W fits the floor best
and its barrel is the worst. A's objects look best as objects and don't sit on the floor; A's
barrel is much better.** The front+top chest fits the floor best. The tension is
*fits-the-ground* against *has-volume*, and the candidate that sits between them —
**oblique**: square front, top visible, side receding at 45° — was not on the list.

## The fix — one layout, one projection per scene

### Placement, measured

Round one's altar sat 2.0 tiles from the lamp and its rack 5.0. That is why the altar read as a
glowing slab and the rack as nothing: placement, not projection. Every archetype now stands
between **2.83 and 3.16 tiles** from the player at (7,14), the rack against the north wall at
(9,12) with (9,11) solid behind it, and nothing stacked on the room's pillar at (5,15) — the
first layout put the stone's base directly on it, and `check_layout()` now refuses that. The
GROUND scene (`tier1_projection2_ground.json`) carries a legibility probe on every archetype
cell, so the light each object stands in is a number in the capture log:

| archetype | cells | d (tiles) | delivered lum (`proj2_ground.log`) |
|---|---|---|---|
| stone (1×2) | (4,13) (4,14) | 3.16 / 3.00 | 0.364 / 0.386 |
| chest | (10,14) | 3.00 | 0.291 |
| barrel | (9,16) | 2.83 | 0.330 |
| altar (2×1) | (6,17) (7,17) | 3.16 / 3.00 | 0.247 / 0.282 |
| rack | (9,12) | 2.83 | 0.327 |

Worst cell 0.247 (the altar's west cell), best 0.386 (the stone's base): a **1.56× spread** from
floor albedo, against round one's ~13× (≈0.06 at the rack, ≈0.79 at the altar). All lit (bound
0.1004), none at the core, none at the edge. Same rig as every capture and every device build.

### Candidates, as geometry

A candidate is a **function** from world (x, depth, height) to the screen, applied to a small
3D model of each archetype — `tools/tier2_props/projection_mesh.py`. The template a generation
is handed is that function applied to that model, so the barrel's lid under oblique is the true
skewed ellipse and the rack's shelves recede exactly as its uprights do. Five candidates on
five archetypes: `gen/projection2/mesh/mesh_sheet.png`.

| | rule | side | depth k |
|---|---|---|---|
| **W** | front + top, no side; top depth 0.31 (the walls' cap:face proportion) | — | — |
| **O-L** | oblique: square front, side receding up-LEFT at 45° | left | ⅓ |
| **O-R** | oblique: square front, side receding up-RIGHT at 45° | right | ⅓ |
| **O-deep** | oblique, right, at cavalier depth | right | ½ |
| **A** | 2:1 dimetric, turned 45° in plan: two foreshortened vertical faces, rhombus top — the volume control | — | — |

*Depth k* is the receding run on each screen axis as a fraction of true depth — how a pixel
artist steps a 45° edge. **O-deep's side is RIGHT, chosen before O-L/O-R were seen** so the
depth walk is not conditioned on the side walk; if the side ruling goes left, O-deep is one
constant in `projection_mesh.SIDE` and a rebuild.

### Materials held

One description per archetype, verbatim across every candidate (`projection_round2.MATERIALS`),
the same three seeds per cell, no candidate given a nicer wood. Whether they held is measured
below (ΔE vs W, every cell ≤ 5.7).

## ⚠ Generation cannot be told a projection — measured, and it changed the method

**Pro ignores a projection reference and a projection instruction.** Two probe calls, 16
candidates each, the template box passed as a labelled reference *and* the projection spelled
out in the prompt (`gen/projection2/sets/`):

- **chest, O-L:** 16 of 16 came back in the model's own ¾ view receding **RIGHT** — signed
  shear +0.034 to +0.053 against a template of −0.028. Not one leaned left.
- **barrel, O-L:** 16 of 16 straight-on, symmetric (0.999–1.000), shear 0.000.

Its view prior wins, every time, silently. This is the §6.4 pattern — *arms indistinguishable
at generation* — arriving at projection.

**img2img holds geometry and adds nothing.** pixflux from a flat painted box at strength
250 / 150 / 90 (`gen/projection2/probes/pixflux_probe_sheet.png`): the side face holds at ≥150
and is gone at 90; at 150 a box stays a box — a band, no lock.

**So the structure is authored and generation supplies surface** — bible §13.7's division of
labour, now at prop scale. Every band, hoop, plate and shelf is in the projected template; the
generator is asked for material at strength 150. From that template the chest holds its left
side and draws its lock (`probes/mesh_probe_sheet.png`).

**⚠ And a lit frame's palette is the rig.** The first full matrix used the landed frame's crop
as a forced palette, to condition on the frame. Every material came back the same tan —
limestone read as pine (`matrix_sheet_palette.png`, `raw_palette/`). That is the floor-mottle
finding (PR #173: *a lit frame's colour count measures the rig, not the palette*) arriving at
props, and it was already on record. The matrix that landed is un-paletted; the frame
conditioning this round is the template's proportions (§12.2 readability scale, 2× canvas) and
the ratified room the objects are captured in, not a palette read off a lit frame.

**And the remover eats featureless objects.** The W stone — a flat grey slab — came back
0.195 of itself twice: `no_background` took it for background. ±6 of grain in the template's
fill removed the trigger.

Spend: probes 46 (2 × Pro at 20, 6 × pixflux at 1), palette matrix 74, landed matrix 76 —
**196 of the 1,100 declared** (pool 2,698 → 2,503, unsettled bracket). Ledgers:
`gen/projection2/raw/ledger.jsonl`, `raw_palette/ledger.jsonl`, every call with its redacted
payload.

## The matrix — picks by hold, then by eye

Three seeds per cell; the pick is the seed whose silhouette best holds the template's
(IoU), then confirmed nameable on `gen/projection2/matrix_sheet.png`, where every seed is shown
and the pick is boxed. No override was needed. *seed / hold*:

| | stone | chest | barrel | altar | rack |
|---|---|---|---|---|---|
| **W** | 1337 / 1.000 | 1338 / 0.988 | 1337 / 1.000 | 1338 / 1.000 | 1338 / 0.859 |
| **O-L** | 1337 / 1.000 | 1337 / 1.000 | 1339 / 0.990 | 1338 / 1.000 | 1338 / 0.995 |
| **O-R** | 1337 / 1.000 | 1337 / 1.000 | 1339 / 0.990 | 1337 / 1.000 | 1338 / 0.998 |
| **O-deep** | 1337 / 1.000 | 1337 / 1.000 | 1337 / 0.987 | 1338 / 1.000 | 1337 / 0.999 |
| **A** | 1337 / 1.000 | 1337 / 0.997 | 1337 / 0.992 | 1339 / 1.000 | 1337 / 0.997 |

The W rack at 0.859 and the losses among the unpicked seeds (W altar 0.480/0.462, W rack
0.577/0.525) are the remover again, on the flattest objects; the picks are whole.

### The instrument, on the landed 32px tiles (`projection_round2.py measure`)

Round one's symmetry and top-shear, the shear now SIGNED (which side recedes), plus the
material match. Seam-tilt is gone: round one showed it measures joints. **Orders; never rules.**

```
cand   arch     symmetry     shear       side   reads
W      stone       1.000    +0.000       none   2 planes
W      chest       1.000    +0.000       none   2 planes
W      barrel      0.996    +0.000       none   2 planes
W      altar       1.000    +0.000       none   2 planes
W      rack        1.000    +0.000       none   2 planes
OL     stone       0.955    -0.111       left   3 planes
OL     chest       0.882    -0.025       none   3 planes
OL     barrel      0.899    -0.121       left   3 planes
OL     altar       0.900    -0.002       none   2 planes
OL     rack        0.971    -0.009       none   2 planes
OR     stone       0.955    +0.111      right   3 planes
OR     chest       0.882    +0.025       none   3 planes
OR     barrel      0.907    +0.106      right   3 planes
OR     altar       0.900    +0.002       none   2 planes
OR     rack        0.969    +0.009       none   2 planes
Odeep  stone       0.937    +0.158      right   3 planes
Odeep  chest       0.813    +0.081      right   3 planes
Odeep  barrel      0.834    +0.115      right   3 planes
Odeep  altar       0.837    +0.010       none   3 planes
Odeep  rack        0.935    +0.025       none   2 planes
A      stone       0.929    +0.111      right   3 planes
A      chest       0.739    +0.100      right   3 planes
A      barrel      1.000    +0.000       none   2 planes
A      altar       0.342    +0.221      right   3 planes
A      rack        0.804    +0.096      right   3 planes

MATERIAL MATCH — mean-colour ΔE (CIE76) against candidate W
arch          W      OL      OR   Odeep       A
stone       0.0     3.0     3.5     2.3     5.7
chest       0.0     1.2     3.9     2.9     3.4
barrel      0.0     1.1     1.2     1.7     1.5
altar       0.0     1.4     0.9     3.8     4.4
rack        0.0     4.1     4.6     4.2     2.4
```

Two honest limits of the numbers. The oblique **altar and rack read "2 planes"** because
top-shear measures the sloped ends over the whole width, and on a wide or shelf-fronted object
the sheared ends are a small fraction of it — the side is there in the picture. And **A's
barrel reads "2 planes"** because a cylinder turned 45° is still a cylinder from the front: the
instrument is right and the archetype is why. Those are the silhouette's limits, reported, not
tuned away.

Landing: 2:1 by sampling (§4.3), 2×2-uniform share 61.6% (O-R rack, worst) to 100%.

## What each projection does to each archetype

Geometry, not verdicts — what the sheet shows (`proj2_rooms_side_by_side.png`,
`proj2_rooms_stacked.png`, and the five full captures `proj2_<cand>.png`).

- **stone (tall).** W: a flat slab with a thin cap; it stands in the wall's grammar. O-L / O-R:
  a dark side arrives and the slab becomes a block; the side reads as mass. O-deep: the side is
  nearly as wide as the face and the block reads turned. A: a diamond-capped post, the narrowest
  silhouette of the five.
- **chest (low).** W: front + lid; a panel with bands. Oblique: the lid becomes a parallelogram
  and the bands wrap over the visible side — the object gains a back. O-deep: boxier, deeper.
  A: the classic ¾ chest, round one's "looks best as an object".
- **barrel (round — the honest one).** W: front + elliptical lid, which is what every Pro
  barrel came back as unasked — it is the generator's prior and the pixel-art default. Oblique:
  the lid slides sideways and the body leans; a cylinder has no square face to anchor the front,
  so the projection shows as a lean rather than a side. O-deep: more so. A: the same barrel as W
  with a rounder lid — a cylinder in dimetric is a cylinder.
- **altar (wide, flat).** W: the top is a plane in the floor's plane, with a front lip.
  Oblique: an end face appears and the slab gains thickness. O-deep: the top skews strongly.
  A: a long diamond, the most floor-fighting shape in the set (symmetry 0.342).
- **rack (against a wall — the discriminator).** W: shelves parallel to the wall's courses; it
  agrees with the masonry. O-L / O-R: the rack's side recedes while the wall behind it shows
  none — two projections in one frame, the wall's and the object's. O-deep: the disagreement at
  its widest. A: turned relative to the wall it stands against — the "bookcase" tension made
  explicit.

## On the handset

Five builds, one bundle id each, **all SKIPPED-REVIEW by design** (§13.2 — this ruling is
Rafe's eye, never a seat's) and stamped so on screen. `projW` and `projA` replace round one's
builds of those names; round one's `projC` is superseded and should be ignored or removed.

| candidate | bundle | scene | built (UTC) | on device |
|---|---|---|---|---|
| W | `…catacombsofyarl.projW` | `tier1_projection2_W` | 16:05:33 | ✅ booted, rig live |
| O-L | `…catacombsofyarl.projOL` | `tier1_projection2_OL` | 16:09:03 | ✅ booted, rig live |
| O-R | `…catacombsofyarl.projOR` | `tier1_projection2_OR` | 16:10:26 | ✅ booted, rig live |
| O-deep | `…catacombsofyarl.projOdeep` | `tier1_projection2_Odeep` | 16:11:56 | ✅ booted, rig live |
| A | `…catacombsofyarl.projA` | `tier1_projection2_A` | 16:13:34 | ✅ booted, rig live |

All five at commit `e0e383f2` (+dirty: the build script's per-candidate output dir; nothing
shipped differs from HEAD, and the verifier says so). Each `proj2_verify_<cand>.log` carries the
three identifiers off the handset — bundle id as the device reports it, commit + built time +
`review=SKIPPED-REVIEW` from the app's own boot line — and the scene, overlays, rig panel and
floor family checks green.

**The install did not go smoothly, and the record says how.** The handset dropped to
*unavailable* between the captures and the first install (CoreDeviceError 1011, three attempts
per build, `proj2_install_<cand>.log`); all five builds completed and were stamped, and were
pushed later without rebuilding (`projection_round2_build.sh push`), so the gate run and the
stamp are the build's own. Then the verifier died silently on every one of them: on the
*ancestor-of-HEAD, nothing-shipped-changed* path — the ordinary case — `grep -v` exits 1 on an
empty diff and `pipefail` killed the script at the assignment, so its `OK*` line had never once
been reachable. Fixed in `verify_on_device.sh` this session; the five green logs are from the
fixed verifier.

Round one's `projC` is still installed and superseded — ignore it, or delete it from the phone.

## What is asked

**Walk the five and rule ONE projection as the game's object law** — and for oblique, the side
(L/R is a whole-game constant; no fixed light motivates it) and the depth (⅓ or ½). The barrel
and the rack are the ones to look at if the others feel close: the round one states the camera
plainly, the against-a-wall one states the disagreement with the walls.

Seats may order the five and name which archetype breaks in each; no seat rules.

### Not this session

The ruling goes into §3 as object law (side + depth if oblique); the marker and props are
re-authored at the ruled projection with `projection_mesh.py` as the geometric authority; the
§12 cold-naming walk resumes on projection-correct objects.

⚠ **Nothing here entered the game's prop set.** Ids 9850–9884 are the reserved review block —
round one's 9850–9872 overwritten (superseded; their generations remain in `gen/projection/`
and in git history) and extended to 9884 because five candidates need 35 cells. No props
manifest lists them, no placer places them, no game scene names them.
