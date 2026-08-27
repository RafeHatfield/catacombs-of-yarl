# WALL-RECIPE — measured from the asset bar, derived from the register

**STEP 1 of the sighted round.** Every wall round on this project so far ran blind. This is the
first one with sight, and bible §13.3's origination rule governs what it is allowed to take:

> **The bar may *occasion* a law; only the register may *justify* one.** A proposed rule whose
> only justification is "the bar does it" is conformance and is refused.

So every number below carries two provenances: **the measurement** (what the bar does, cited to
its source) and **the derivation** (why the register says it is true for Yarl). A number with a
measurement and no derivation is **FLAGGED, not adopted** — three are.

**Measurements leave; pixels never do.** `measure_bar.py` reads a licensed local library, emits
`bar_measurements.json`, and writes nothing but numbers. No source pixel is in this repo, in any
composite, in any reference, or in the corpus (§1.3).

**Source:** Oryx Ultimate Fantasy 1.2 — the asset bar under §13.3 — five example room maps with
their Tiled `.tmx`, so structure is read from map data rather than guessed off a screenshot.
548 wall tiles classified, 152 face tiles, 166 shadow placements.

> ⚠ **The brief named "SPD screenshots" as a second source. There are none on this machine** —
> `find` across the repo, `~/development`, `~/Downloads`, `~/Documents` and `~/Desktop` returns
> nothing for Shattered Pixel Dungeon. **Every number below is single-sourced from the asset
> bar.** SPD is the *structure* bar under §13.3 and would have been the better source for
> layout-and-readability questions; its absence is a real gap in this recipe and is not
> papered over. What survives single-sourcing is the value and proportion work, because that is
> what was measured across 23 independent face tiles rather than read off one screenshot.

---

## 0. THE HEADLINE — YARL'S TWO PLANES ARE INVERTED

Measured, same statistic, both corpora, floor-relative albedo:

| | wall TOP | floor | wall FACE | face ÷ top |
|---|---:|---:|---:|---:|
| **the bar** | **1.11 × floor** | 1.00 | **0.59 × floor** | **0.53** |
| **Yarl, composition spike `before` arm** | **0.49 × floor** | 1.00 | **0.65 × floor** | **1.30** |

Read the last column. **In the bar the face is half the value of the top. In Yarl the face is
brighter than the top, by 30%.** The relationship is not weak or mistuned — it is inverted.

And the middle column matters as much. The bar puts the wall top **above** the floor and the
face **below** it, so the floor sits between the two planes and each is separated from it in a
different direction. Yarl puts *both* planes below the floor, 0.49 and 0.65, where they are 0.16
apart and the floor is the brightest thing in frame.

**This is the whole of the eight-round "no thickness" finding, and no side face is required to
explain it.** A blind seat asked to find a top and a face in Yarl's walls was being asked to
read a plane relationship that the values contradict.

⚠ **And the spike's own sweep pointed the wrong way for a structural reason worth recording.**
It tested wall-top albedo at 0.62 and 0.76 of floor, found 0.62 ranked higher, and reasoned
toward darker. Both samples sat on the *same side* of the floor's value; the answer is on the
other side, above 1.0. **A two-point sweep entirely on one side of the true value will point
confidently in the wrong direction, and it will look like clean evidence while doing it.**

---

## 1. THE VALUE STACK — ADOPTED

### 1.1 Wall top is LIGHTER than the floor. Target **1.15 × floor albedo**.

**Measurement.** Aggregate across all five maps and every tileset they cite: wall-top mean
luminance 123.9 against floor mean 111.4 → **1.11×**. Within the dungeon-grey + dirt-floor
combination that the room mockups actually use: top 89.5, floor 69.6 → **1.29×**.
`bar_measurements.json: value_stack.top_over_floor`.

**Register derivation — §8.1 / §8.2, wear, not light.** *"Grime walked into a surface until it
is part of it."* The floor is walked on for four hundred years; the wall top is not walked on at
all. Under one ambient, the walked surface is the darker one and the untouched surface is the
lighter one. **The floor is dark because it is used. The wall top is light because nothing has
ever touched it.** This is a material-value derivation and it therefore survives §6.3: it
declares no light direction, and it is true from every angle.

**Adopted at 1.15**, between the two measurements, because the aggregate spans stone families
Yarl does not use and the room-specific 1.29 is one material pairing. Stated as a target to test,
not a constant — §5's values remain PLACEHOLDER.

### 1.2 Wall face is DARKER than the floor. Target **0.60 × floor albedo**.

**Measurement.** Face mean 66.1 against floor 111.4 → **0.59×**, across 23 face tiles.

**Register derivation — §6.4 arm B and the §12.1 occlusion law.** *"Joints, recesses and
undercuts sit darker because they are enclosed."* A vertical plane under a top-down ambient is
enclosed relative to a horizontal one — it faces the wall opposite, not the ceiling. Enclosure
is direction-free by construction: dark from every angle, so a torch arriving from anywhere does
not contradict it. This is the clause's own reasoning applied to the largest recess in the
scene.

### 1.3 The two planes separate by **2:1**. Face ÷ top = **0.53**.

**Measurement.** Per-tile, not aggregate — 0.499, 0.504, 0.538, 0.537, 0.526 on the main
dungeon-grey family; 0.44–0.54 across all 23. The tightest number in the whole recipe.

**Register derivation — §12's value floor and §4.1's names-itself-at-1×.** §12 requires value
separation to do the work that §12.1 forbids an outline from doing. Two planes of one material,
lit by one ambient, must be told apart by value alone; 2:1 is the separation that survives the
light arc, because at the deep floors where §6.2 takes the ambient toward black a smaller ratio
collapses into one mass first. **The ratio is what remains legible when the light leaves.**

---

## 2. THE PROPORTIONS — ADOPTED

### 2.1 The face occupies the **lower 0.50** of its tile. The top band is the upper 0.48.

**Measurement.** Turn row 23 of 48 in 19 of 23 face tiles; face 24 px of 48 = **0.500**;
outliers 0.479 (2), 0.542, 0.604. `bar_measurements.json: face_geometry`.

**Register derivation — §4.1, "names itself at 1×", applied to a plane.** A plane that must be
identified as a plane has the same burden as an asset that must be identified as an object: it
has to be read at true display size. At Yarl's 32 px tile, half a tile is **16 px** — a surface.
The composition spike's reveal was 3–5 px, which is a *line*, and its seats read it as one every
round: *"a rim, not a thickness"*, *"a shadow gap rather than a cap"*. **A face thin enough to
be mistaken for an edge will be.**

**Consequence for Yarl at 32 px: face = 16 px, top band = 15 px, turn at row 16.**

### 2.3 The top plane is FLAT. One value, broken only by joints. **ADDED IN ROUND 2 — the seats found this, not the tape measure.**

Round 1 built the top plane by re-toning the same coursed masonry the face uses. **Both blind
seats culled both Yarl arms `wrong-projection`, independently, for the same reason** — and
neither was shown the other's verdict:

> *"A top surface does not show five courses of face-brick."* — S1, on the recipe arm
> *"the brick coursing above it has the same pitch, proportion and orientation as below, so it
> is not a top surface — **it is more face**."* — S2, on the composition spike's control arm

**Measurement, taken by those same seats off the bar and matching the tileset numbers.** S2:
*"top plane y0–29 held at exactly 90 — **91.5% of those pixels are literally 90** — with 2px
vertical joints at x=60, 108, 158, 206, 252, 300"*; S1: *"one plane, 30px deep, with only
cross-joints in it."* Joint pitch 48 screen px at 2× = 24 px native = **half a tile**. Joint
value 70.4 against a plane of 89.5 = **0.79**.

**Register derivation.** §12: *"interior detail not at all."* §4.2: centres stay open, events sit
at the edges. And the wear derivation that already carries §1.1 carries this too — **§8.1's decay
is traffic-driven, and nothing walks on a wall top.** A surface nothing has ever touched has
accumulated no incident, so it has nothing on it but the joints between the blocks it is made
of. The face is coursed because you are looking at courses; the top is not, because you are
looking at the tops of stones.

**This is the clause that costs the projection cull, and no value change reaches it.** Round 1
had §1's values correct — S1 measured the bar at *"face at 0.49× the top"* and independently
proposed §1.3's own number back as its flip list — and still culled the arm, because a plane
textured like elevation reads as elevation whatever its value.

**Adopted: plane flat at the target value, 2 px joints on a 16 px grid at 0.78 of the plane,
phase-offset per variant.**

### 2.2 Wall mass is at least **2 tiles** deep wherever a room wraps.

**Measurement.** Vertical wall-run lengths across the five maps: 1 tile ×30, 2 ×68, 3 ×40, and a
tail to 10. The 1-tile runs are door jambs and pillars; **every room boundary is 2 or more.**

**Register derivation — §7.4, the Boundary is *held*.** A wall one cell thick is a partition; the
orcs' work is *"heavy, over-built and competent"*. A held line is thick because thickness is what
holding costs. This also gives the face somewhere to sit: a 1-tile wall seen from above has no
room for a top band and a face both.

---

## 3. THE OCCLUSION — ADOPTED, AND IT IS NOT WHERE WE PUT IT

### 3.1 The seam lives on the FLOOR cell, not on the wall sprite. **This is the structural find.**

**Measurement.** Every example map carries a dedicated `shadows` layer, separate from `walls`.
166 shadow placements across five maps; **149 of them sit on a cell whose northern neighbour is
a wall.** The wall sprites themselves carry no cast seam at all. The shadow tiles are pure black
(0,0,0) at partial alpha and nothing else.

**Register derivation — §12.1, RULED, verbatim.** *"It does not compete with §7.1's linear
elements — **it is not on the object at all**. Straps, bands and tags still carry the read across
a sprite; occlusion carries the read across a boundary."* The bible already ruled that occlusion
belongs to the boundary rather than to the object. The bar shows what that means in
implementation: **put it on the other cell.** Occlusion authored into the wall sprite is
occlusion that has to guess what adjoins it; occlusion on the floor cell answers to what
actually does.

**This also settles a §12.1 exposure.** A seam baked into the wall tile is present on every side
the tile is used, which is the definition of a ring the ring instrument exists to catch. A seam
placed on the adjoining cell cannot be a ring, because it is not around anything.

### 3.2 The ramp is **stepped, black, and 0.29 tile deep**: alpha **64 / 38 / 13**.

**Measurement.** The primary ramp (gid 35): α64 for 8 px, α38 for 3 px, α13 for 3 px, then
nothing — 14 px of 48 = **0.292 tile**. A half-strength variant runs α32/19/6 over the same
extent. A hard-contact variant (gid 236/237) prefixes α255 for 3 px. A short variant (gid 289)
is α38/13 over 6 px. **It is a family, selected per situation, on one alpha ladder:
255 / 64 / 38 / 13 / 0** — that is 1.00 / 0.25 / 0.15 / 0.05 of black.

**Register derivation — §5.1's palette discipline and §12.1's "answers to the geometry".** A
stepped ramp is a palette decision, not a gradient: the same discrete-step discipline §5 applies
to material applies to shadow. And the *family* is the point — a single seam applied everywhere
is the uniform ribbon §12.1's worked example culled; a ladder with a hard variant for contact
and a short variant for a shallow reveal is a treatment that answers to the geometry it sits on.

**Consequence for Yarl at 32 px: 0.29 tile ≈ 9 px**, as α64 ×5, α38 ×2, α13 ×2.

⚠ Yarl's spike ran occlusion at 3 px and 5 px and its best-ranked arm used 5. **9 px is nearly
double the deepest it has tried**, and the seat that ranked that arm first still called the
result *"a shadow gap rather than a cap."*

---

## 4. FLAGGED — MEASURED, NOT ADOPTED

### 4.1 ⚠ The bright cap at the top-to-face turn. **FLAGGED.**

**Measurement.** On the dungeon-grey family a single 1 px row at the turn runs **1.27–1.47 ×**
the top band's value (129.8 against 89.5). But across all 23 face tiles it is not universal:
9 tiles measure below 1.0 at the same row. It is a treatment of one stone family, not a
structural law.

**Why it is not adopted.** The only register derivation available is §8.1 polish-where-touched —
a worn arris, pale because four hundred years of shoulders and gear have rubbed it. That
derivation is real but it carries a condition: **wear is traffic-modulated**, so a worn arris
must be pale where traffic passes and absent where it does not. A pale line of constant value on
every turn is precisely the coping course §12.1's worked example culled — *"a flat, featureless
ribbon at floor value applied to every wall edge for its entire length"* — and the spike already
paid for that lesson once.

**Status: adoptable only in a traffic-modulated form. The uniform version is refused.** This
round does not have a wear system to modulate it with (§8.2.1's tier-one requirement), so it is
built with the cap OFF and the flag stands.

### 4.2 ⚠ The bar's autotile placement convention. **FLAGGED — measured, deliberately not copied.**

**Measurement.** The bar's face tiles are *not* simply "the wall cell north of a floor cell" —
only 31 of 152 sit there. Its wall masses use half-tile-offset sprites and its own mask
convention, which the map data shows plainly.

**Why it is not adopted.** This is Oryx's tiling convention, and copying a convention is
conformance under §13.3, not a lesson crossing. Yarl already has a mask table that implements
§3's rule — front face where floor lies south — and it is fitted to this renderer. **The recipe
changes what the tiles look like, not where the engine puts them.** Nothing in this round
touches the mask table.

### 4.3 ⚠ Wall-top albedo above 1.0 may fight the light pool. **FLAGGED AS A PREDICTED RISK.**

The spike's round-8 seat, on the 0.76 arm: *"the ambient lift kills the light pool's edge and
drains the joint contrast that was the only thing making the wall read as stacked stone."* §1.1
adopts a value **above** the floor, which is further in the direction that seat objected to.
**The prediction is that §1.1 and that objection collide, and this round is the test.** Recorded
before the rebuild so it cannot be discovered afterwards and called a finding.

---

### 4.4 ⚠ THE ENGINE COMPRESSES THE AUTHORED RATIO, AND BY HOW MUCH IS NOW MEASURED.

**§4.3 predicted a collision with the light pool. What actually happened is worse and more
useful, and it is a fact about receive-light assets under a carried point light rather than
about this recipe.**

Measured in the mixed scene, room A's north wall, same rows in every arm
(`tools/sighted_round/checks.py`):

| | authored face/top | **delivered lit** | delivered unlit |
|---|---:|---:|---:|
| recipe arm | 0.52 | **0.77** | 0.60 |

**The light source is the player, and the player stands SOUTH of a north wall. The wall's face
is nearer the lamp than its own top, always, everywhere, by exactly one tile.** So the engine
brightens the face relative to the top and compresses the authored separation — here by a factor
of **1.48**. An authored 0.52 arrives as 0.77, and 0.77 is close enough to 1.0 that the plane
relationship is weak at the frame centre and gone at its edges. S1 measured the consequence
without being told any of this: *"at x=40 that step is 42→28, only 14 points, and at x=400 it is
56→21 — A's corner therefore exists only where the light happens to land."*

**The bar does not have this problem and cannot teach us the answer to it**, because its scene
is uniformly lit and has no run-time light at all. This is the first number in the recipe that
the bar could not have supplied.

**Consequence: the authored ratio must be lower than the delivered target by the compression
factor.** To deliver the bar's 0.52 through this rig: author **0.52 ÷ 1.48 ≈ 0.35**.

⚠ **And this is flagged, not adopted quietly, because it ties the art to a rig whose values are
PLACEHOLDER (§6.2).** Compensating for a measured falloff is a material decision and does not
depict a light direction, so it survives §6.3 — but if the rig's energy or radius changes, the
compensation is wrong and the walls flatten again. **A recipe number that depends on an
underived rig value is a number with a fuse in it.** The honest options are to derive the rig
before freezing the ratio, or to give wall tiles a light-response clamp in the renderer; both
are outside this round.

---

## 5. THE RECIPE, AS BUILT — Yarl at 32 px

| quantity | value | §2 |
|---|---|---|
| wall-top albedo | **1.15 × floor** | 1.1 |
| wall-face albedo | **0.60 × floor** | 1.2 |
| face ÷ top | **0.52** | 1.3 |
| face height | **16 px** (0.50 tile) | 2.1 |
| top band height | **15 px** (0.47 tile) | 2.1 |
| turn row | **16** | 2.1 |
| minimum wall mass | **2 tiles** | 2.2 |
| occlusion location | **the floor cell, not the wall sprite** | 3.1 |
| occlusion ramp | **α64 ×5, α38 ×2, α13 ×2** of black, 9 px | 3.2 |
| bright cap at turn | **OFF** — flagged, needs a wear system | 4.1 |
| mask table | **unchanged** | 4.2 |

**Standing checks the rebuild must pass:** the §12.1 ring instrument
(`tools/floor_remediation/ring_instrument.py`) on every composed tile, and the round-8
differencing check — authored occlusion must persist with the engine light off, and anything
that only exists with the light on is a cull.
