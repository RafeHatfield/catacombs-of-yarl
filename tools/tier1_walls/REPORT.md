# Tier one — the Boundary's walls, and the void

**The round that retired the magenta mocks, and found the rig standing where the walls need to
be.** Everything below was produced on the ratified rig (radius 5.0 / falloff 1.00 / ambient 0.70
/ energy 1.6, Ruling 56), passed explicitly and echoed into every capture log.

---

## 0. What this session is returning, in one page

**Three findings, one ruling trigger, two arms and a scene.**

1. **§6.5's value stack does not survive §6.2's falloff.** The wall top cannot be made brighter
   than the floor it faces at any authorable value beyond two tiles. This is the item Ruling 56
   recorded as owed and could not answer, and it is a **§6.2 coupling finding** returned under
   LOOP-PROCESS §1.1.4(b). `STACK-FINDING.md`.
2. **The wall's own material is delivered below the representable floor at the range walls
   actually sit at.** Weber contrast is flat with range because the pipeline is multiplicative;
   delivered *levels* fall **30.05 → 28.96 → 14.08 → 4.85 → 2.46** over one to five tiles. A blind
   seat put the same measurement in words: *"the wall is 87% below 20/255 and one pixel thick — at
   1:1 there is no wall."*
3. **The mask table draws a front face where §3 forbids one**, on 13 in-map cells per review
   scene — every one of them a room's south wall. It could not have been seen before now: the
   walls were magenta.

The walls were built anyway, as two arms, because the ruling in (1) is Rafe's and a gate needs
something to rule on. Six instruments were built and all six have demonstrated they can fail.

---

## 1. §6.2.1's owed item, answered

> *"The §6.5 stack surviving the falloff across the lit radius — NOT ANSWERED, and it could not
> be … owed by the first round that puts real walls in the scene."* — Ruling 56

**It does not survive.** `STACK-FINDING.md` carries the measurement in full; the short form:

| range | k_top | k_face | authored value needed for §6.5's 1.11× | on the nine-rung ladder? |
|---:|---:|---:|---:|---|
| 1 | 0.869 | 0.956 | 129 | yes |
| 2 | 0.670 | 0.820 | 168 | **no** |
| 3 | 0.480 | 0.684 | 234 | **no** |
| 4 | 0.300 | 0.517 | 375 | **not expressible** |

k_top cannot exceed 1.0 at any range and the reason is structural rather than tunable: **the
player carries the lamp, so the floor a wall faces is always nearer the light than the wall's own
top plane.** §6.5's 2:1 plane separation survives (delivered 0.44–0.69, mean ≈0.55 against the
clause's 0.53). *"The floor sits between the planes"* does not, and inverts at three tiles.

**The measurement can be believed because the pipeline was characterised first.** Godot's 2D
rendering is exactly multiplicative in albedo — 0.5000 from a 101/202 pair with a worst-cell error
of 0.0006 — so a flat-albedo capture is a picture of the rig's multiplier. Four controls, all
green, including one that exists to show another can fail: at energy 0 the two planes separate by
exactly 1.00000, with the lamp on by 1.43349.

Two traps were found by controls going red rather than by inspection, and both are in the code:
**clipped pixels** (the bright probe drives channels to 255 beside the lamp; the first linearity
run read 0.522 there) and **translucent interface** (the zoom buttons, the RIG panel and the Msg
button are drawn *inside* the dungeon view; a pixel under a panel still moves with albedo and
moves by the wrong proportion — the unity control failed on exactly four cells, every one under a
panel).

---

## 2. The second finding, which is the same law from the other side

`measure_wall_amplitude.py` asks §13.8's question on the **capture**, using the source only to
know which pixels are joints — §13.9's distinction, *an instrument that measures the source has
not measured the asset*.

| range | Weber contrast | delivered levels (of 255) |
|---:|---:|---:|
| 1 | 0.191 | **30.05** |
| 2 | 0.344 | **28.96** |
| 3 | 0.319 | **14.08** |
| 4 | 0.270 | **4.85** |
| 5 | 0.275 | **2.46** |
| 6–7 | ~0.25 | **~2.5** |

**The ratio column is flat and the levels column falls twelvefold.** The material is completely
present beside the player and quantised out of existence at the range a room's own walls sit at.
Nothing about the authoring changes that: a ratio survives a multiplication, and eight bits do
not.

**AND IT SEPARATES THE TWO ARMS ON AN AXIS NOBODY EXPECTED.** On the gate scene:

| range | `material` arm (top 114.70) | `compensated` arm (top 154.38) |
|---:|---:|---:|
| 3 | **−1.37 levels** (sign is noise) | **18.23** |
| 4 | 1.96 | **8.62** |
| 5 | 0.28 | **3.08** |

The brighter arm is not merely closer to §6.5's delivered targets. It is **the arm whose material
is still representable two ranges further out**, which is a different and stronger argument than
the one it was built for.

---

## 3. The §3 violation the mocks were hiding

`DungeonRenderer` collapses cardinal masks **7 and 11 both to 3**. Mask 11 has floor to its south
and wants a face; **mask 7 has WALL to its south** and must not have one. One tile served both, so
the table drew a front face into the middle of a solid mass.

Measured across all four existing review specs: **13 in-map cells per scene**, plus the whole top
border row. Every one of the 13 is a room's south wall — the most-looked-at wall in any of them.

The collapse is not a bug in the renderer; its own comment says it was fitted to the old sandstone
tileset, where masks 194–197 drew directional T-junctions that looked wrong on plain room edges.
It is a bug *under §3*, and it was invisible while the walls were flat magenta blocks with no
planes in them. `Tier1BoundaryWall` computes the mask itself and reports `face_suppressed` on
every capture, so a regression is loud.

---

## 4. What was built

**The family.** Two planes at 32px — top band rows 0–15, face rows 16–31, turn at row 16
(`WALL-RECIPE.md` §2.1's measured 0.50 tile, and its warning that *a face thin enough to be
mistaken for an edge will be*). The turn is drawn by **occlusion only**: the top plane is never
brightened, the first two rows of the face are darkened, because a face under an overhang is
occluded from every azimuth and declares no direction (§6.3).

**No contact seam is drawn on the wall.** §12.1 makes plane-boundary occlusion mandatory and
`WALL-RECIPE.md` §3.1 measured where the bar puts it — on the **floor** cell, which is the one
that knows what adjoins it. The landed floor family already draws it per edge (ids 9630–9633, 8
native px, peak alpha 183). A second copy on the wall side would double the darkening and would
be present on every side the tile is used, which is a ring.

**Edge-matched, with the corner theorem's price paid in the same coin the floor paid it.** Tiles
are chosen by the two **boundary keys** they share with their neighbours (§8.3.2 — *matching is
agreement, not constancy*), so a block crossing a boundary is drawn the same on both sides of it.
A bed joint sits on every tile boundary across the run, because §8.3.3's corner theorem is a
platform theorem and forbids a block from covering a grid corner. Measured: seam step **0.09×** an
ordinary interior step; **6.7%** of the field's darkest columns on a tile boundary.

**Courses run along the wall.** `top_h` and `top_v` are the same material laid the two ways a
mason lays it. The first version had one top plane and the north–south corridor came back as **a
palisade** — head joints at ten-pixel pitch running across a wall that runs the other way. The
capture is kept: `evidence/r03_choke.png`.

**The orc layer is placed, never baked.** Five kinds — strap, pin, cramp, patch, lash — each
required to grip something nameable (a strap crosses a joint and wraps the arris; a pin sits *in*
a head joint; a lash only ever goes over a strap that is already there, which is §7.3's *repaired
on top of prior repairs* made literal). Placed per cell from a world address at rates that are a
property of the world (§7.3), on a salt independent of the tile keys so a binding never correlates
with the tile it lands on.

**The void is three candidates on a live toggle.** Wall cells are laid in rings — ring 1 is the
wall a room has, ring 2 is its thickness (`WALL-RECIPE.md` §2.2, register in §7.4), and past that
is the dark. The three near-blacks are switched by the rig panel rather than by rebuilding,
because three rebuilt candidates are three walks and the question is a comparison. **Nothing here
rules it. §13.1 gives that to Rafe, in the scene, on the device.**

---

## 5. The instruments

Six geometric tests, six plants, every plant firing on the axis its test claims, and the legal
family clean. `wall_laws.py --controls`.

**Four of the six bounds were wrong, and the plants found them.** Recorded because an instrument
quietly retuned until it agreed is not an instrument:

| test | what was wrong | what it measures now |
|---|---|---|
| `flat_top` | compared peak-to-mean power; a smooth profile with grain is also dominated by one frequency, so it failed the legal family at 4.8 | counts bed-joint rows in the top band — what §3.1 actually forbids |
| `incident_free_top` | bounded a *share*; a four-pixel tick in every tile is 0.4% and invisible to it | the largest connected frozen region across the whole set |
| `constant_pitch` | thresholded at a quartile; the degenerate case flattens the interior, drags the quartile onto it, and passes | thresholds in ladder rungs |
| `edge_agreement` | averaged the jointed edge family in with the crossing ones | tests only the families where a block actually crosses |

**And one of them found a real defect in the art.** `edge_agreement` came back at **4.22×**: a
crossing block's *value* agreed across a boundary and its *grain* did not, because the grain was
indexed from the tile's own left edge instead of from the shared boundary. Fixed the way the floor
family does it (`stone_origin`), and re-measured at **0.09×**.

**No instrument here scores a register clause** (§13.4). *Nothing is staged*, *the art plays it
straight* and *nothing is ruined, things are used up* have **NO INSTRUMENT** and are carried at
the human gate.

---

## 6. The parts bin supplied a statistic, not pixels — and that was measured

The first version of the family laid residual patches cut from the wall gauntlet's round-7 stock
as grain. The assembled run came back as **brick wallpaper**: a box blur wide enough to remove a
joint does not remove a *course*, so the donor's own bond arrived inside every block as structure.
That is §13.7's *"BitForge produced architecture 0/100 … generation supplies materials and parts
only"* reaching the tile through the back door.

The donors' residual amplitude and the periodicity still present in it are both in the manifest,
with each donor's gauntlet verdict beside it. **Zero generations were spent this session**; the
declared budget of 60 was not opened, because the measurement said the surface had nothing left to
supply that composition could not.

---

## 7. Round 1's seats — VALID, and they say *flat pattern*

Run on the pre-fix build (`r07_family.png` / `r07_plant.png`), transcripts in `evidence/seats/`.

**W1, on the family, unprompted and measuring as it went:**

> *"**Flat pattern.** Not a judgement call — magnified, the north edge is literally three
> continuous horizontal rules with ticks between them … two courses of rectangles of **identical
> height, unstaggered, running the full width with no bond and no break**. It is a ladder diagram
> of a wall."*
>
> *"**CULL:** The wall is 87% below 20/255 and one pixel thick — at 1:1 there is no wall."*
>
> *"beyond the walls is black. That black reads as **empty screen**, not as unlit stone."*
>
> On the chokepoint: *"I read it as **a smear of light, not a passage** … what makes a passage
> readable is its jambs, and the jambs here are at 5/255."*

**Two of those were acted on inside the session and re-verified:**

- *no bond* — the boundary offsets did not depend on the course, so both courses of the face broke
  at the same x at every tile boundary. Staggered by course; agreement is untouched because both
  neighbours still read the same key and the same course index.
- *no beyond* — two causes, both real. The gate scene contained **66 void cells and none inside
  the dungeon view**, because a three-deep mass is two rings of stone and nothing else; the mass
  is six deep now. And the seat's crop trimmed 60px off the top *to exclude the HUD* and trimmed
  the void away with it — a crop that removes the subject is the review scene's own §2.2 failure
  moved into the review harness.

**Two of them are not this session's to act on**, and are the ruling above: *give the wall a lit
face* and *draw the east and west edges*. The second is a request for the plane §3 forbids, and it
is now the **seventh independent blind seat to ask for it unprompted**.

### The plant control, and why it was tightened mid-round

W2 culled the plant — for *"walls render at 4% luminance, invisible at play size"*, **which is a
defect the family shares**. A control that counts a shared cull as a catch has not discriminated
between the arm and the plant; it has established that the seat culls things. That is §4.1's named
failure — *a control that only asks "did anything change?" certifies connectivity and reports it
as efficacy*.

The plant **was** caught, on its own axis, in Q11:

> *"cracked, uniformly and decoratively, and otherwise untouched … Nothing has **happened** to it.
> Cracks were **applied** to it."*

which is §8.1's *nothing is ruined, things are used up* arrived at from the pixels by a seat that
has never seen the clause. The check now decides on the axis and records the cull separately.

---

## 7a. The clause that had to be read carefully, because two of them pull against each other

LOOP-PROCESS §1.1.1: **nothing reaches the human gate that the blind critic would kill.**

Three independent seats, on three different builds, culled on the same thing:

> *"the wall is 87% below 20/255 — at 1:1 there is no wall"* (W1, round 1)
> *"a black band with a 4px outline — no mass, no shadow, no thickness"* (W3, round 1)
> *"No wall pixel in this frame exceeds 35/255. The material is invisible at play size."* (W2, round 2)

**The reason they kill is a property of the rig, and the rig is ratified.** A builder cannot fix
it; moving it is Ruling 56 re-opened, which is §1.1.4(b) and Rafe's.

So the two clauses meet, and the reading this session took is the narrow one: **§1.1.1 forbids
presenting something a critic would kill for a reason the builder could have fixed.** Everything
in that class was fixed and re-verified inside the session — the bond, the ink, the grain, the
orientation, the scene, the crop. What is left is a cull that is *itself the ruling trigger*, and
carrying it to the gate with the seats' words attached is the opposite of concealing it.

The alternative reading — hold the round until the critic passes — would mean iterating art
against a constraint the art cannot reach, which is exactly the failure §6.2.1 named when it said
*the rig is one table of numbers and the corpus is every asset in the game.*

## 8. State

- **§6.5 vs the ratified rig — RULING TRIGGER, open.** Three remedies named in `STACK-FINDING.md`,
  none of them this session's to choose.
- **§3 — NOT RATIFIED, and this round does not ratify it.** The evidence is mixed and it is
  reported as mixed: the island at (5,15) reads as a solid block with a top and a face at two
  tiles, and the same construction reads as *flat pattern* at five. Whether that is §3 failing or
  the rig failing §3 is exactly the question the gate has to answer, and it cannot be answered
  from a still.
- **The two arms.** `material` (top 114.70 / face 61.79) and `compensated` (154.38 / 75.02). The
  measurement in §2 favours `compensated`; the §6.3 hygiene argument favours `material`.
- **The void.** Three candidates, unruled, on the panel.
- **Instruments.** Six, all proven failable, legal family clean, both arms clean.
- **Generations spent: 0 of 60.**
- **Device.** Built and installed with `TIER1_WALLS` / `TIER1_BINDINGS` / `TIER1_VOID`. Read the
  painter's line back off the log before believing anything: it must say
  `missing=0 edge_check=46/OK`.

### `git diff --stat` against `origin/main` (ec16108)

```
755 files changed, 59779 insertions(+), 1 deletion(-)
```

of which the engine and harness are 660 lines across 8 files:

```
 src/Presentation/Main.cs                             |  62 ++
 src/Presentation/Map/ReviewBuildMarker.cs            |  29 ++
 src/Presentation/Map/ReviewRigPanel.cs               |  20 ++
 src/Presentation/Map/Tier1BoundaryWall.cs            | 364 +++++
 src/Presentation/assets/.../tier1_wall_review.json   |  94 ++
 tools/tier0_harness/build_review_app.sh              |  51 ++
 tools/tier0_harness/capture_corridor.py              |  40 +-
```

The remaining 747 files are composed tile PNGs and their `.import` sidecars (two arms, the
bindings for each, and the plant), the probe fixtures, and the evidence. **One deletion**, and it
is the point of the session: the wall mocks are no longer what the review scene draws.

### The gate, and what to look for

Real floor, real walls, void on a toggle, no magenta anywhere.

1. Do the walls read as **solid mass** at a glance — and does the answer change as you walk toward
   them? (The measurement says it will change at about three tiles. That prediction is written
   down before the walk so it cannot be discovered afterwards and called a finding.)
2. Does the chokepoint read as **a passage between masses**, or as a notch?
3. Does §6.5's stack deliver — is the floor between the planes anywhere, and where does it stop?
4. Do the south reveals read as **faces**, with no side face anywhere?
5. **Which void**, of the three on the panel.
6. And the register one: **does the room feel HELD.**
