# Tier one — the Boundary's walls, and the void

**The round that retired the magenta mocks, and found the rig standing where the walls need to
be.** Everything below was produced on the ratified rig (radius 5.0 / falloff 1.00 / ambient 0.70
/ energy 1.6, Ruling 56), passed explicitly and echoed into every capture log.

---

## 0. What this session is returning, in one page

**⚠ THIS SECTION IS THE STATE AT THE FIRST GATE. Two rounds of rulings have landed since —
§9 and §9d — and where they disagree with what follows, they win.** The original text is kept
because a report that overwrites itself is not a record: the findings below are what was true
before Rafe walked it, and reading them in order is how the reversals make sense.

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

**Where the two ruling sets have since taken it, in five lines:**

- §6.5 is **re-scoped to a standing-distance law**; the 1.11× came from a lightless screenshot and
  is not chased. Inversion past three tiles is physics, recorded as dark-by-design.
- The defect is **wall-versus-FLOOR, not wall-versus-void**, and the remedy is **the material
  arm** — wall stone as its own darker material. Wall-vs-floor now delivers **23.27 levels** at the
  standing case against an 8-level bar.
- **The walls have a history**: aging at the base courses, keyed to the floor's own traffic field.
- **The §3 mask collapse is fixed** as a correctness bug, in the logic layer, with tests.
- **Two review scenes were dead** — traffic field exactly zero — for a reason that is neither the
  scene nor the art.

`evidence/SESSION-before-after.png` is the session in one image: the magenta mocks on the left,
the walls and the void on the right. ⚠ **It is a before-and-after of the SESSION, not an A/B of a
single variable** — the scenes differ, because the wall gate needed a scene the floor gate did not
have. It is offered as a record of what changed, never as a comparison of two arms.

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

### ⚠ 2a. And a qualification that arrived from the floor session while this one ran

The concurrent floor session **voided its own Ruling 70 closure** for measuring a
player-carried-lamp signal on a static capture — *"the path signal is keyed to where the player
walks, and the player carries the lamp, so a static scene-wide capture measures the signal exactly
where its reader never is"* — and issued a standing design ruling: **the path is built for LIT
legibility, player-as-light-source is the normal case, and dark illegibility is accepted by
design.**

Every range in §2 was measured on a static capture. The correction is applied rather than argued
with, and it lands unevenly:

- **The amplitude rows past four tiles are a datum about the dark, not a charge against the
  asset.** A wall's joints, grain and bindings are near-field signal; the player walks up to the
  wall and at one to two tiles they deliver 30 levels. Under the standing ruling that is the
  design.
- **§1's finding is not dissolved by it.** `k_top` is a LOCAL ratio — a wall against the floor it
  faces, both in the same place — so it is not a number taken where the reader never is. At **two
  tiles**, standing beside the wall, it is 0.670 and no authorable value reaches §6.5's 1.11×.
- **And it sharpens what the walls are actually short of:** not texture in the dark, but the
  **mass read at a distance**. A seat measured wall and open passage at *identical* luminance 18
  at the same row. Telling you where you cannot go is a far-field job, and walking closer does not
  answer it, because by then you are already there.

⚠ This branch predates that ruling; it is cited from the sibling session's record (PR #163) and
should be re-checked against the merged text.

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

## 7b. Rounds 2 and 3 — two fixes bought something, measured

**The chokepoint, across three rounds and three seats:**

| round | build | verdict |
|---|---|---|
| 1 | before the bond stagger | *"a smear of light, not a passage … what makes a passage readable is its jambs, and the jambs here are at 5/255"* |
| 2 | after it | *"I read it as **a passage**, and the thing that made the difference was the block course: the face terminates cleanly at x=375 and resumes at x=440 with proper end-blocks. **That is a doorway.**"* |

A fix that moved a seat from *smear of light* to *that is a doorway* is a fix that
did what it claimed, and it was re-verified rather than assumed (LOOP-PROCESS §2:
fix rounds regress).

**The void, in two valid rounds, both saying the same thing:**

> *"beyond the walls is black. That black reads as empty screen, not as unlit stone."* (r1)
> *"More of the same stuff … it is wall, and it goes on. What it is NOT is dark."* (r2)

`void_ring` was 2. It is 1 now, and §8's state records what that changed.

## 7c. ROUND 3 IS VOID, and the reason is not an unrelated accident

Round 3's plant seat culled — *"walls are half-resolution art with duplicated decals, invisible at
play brightness — the subject isn't rendered"* — and **named nothing on the plant's own axis**.
Under LOOP-PROCESS §4 that is not a soft catch to be weighed at reduced strength; the round is
**VOID and its findings are not read.** They are not read here, and a reading of the island that
had already been written into `STACK-FINDING.md` was withdrawn rather than downgraded.

**Why it went void matters more than that it did.** The plant is a *picturesquely ruined* wall —
collapse, cobweb, moss, a forked crack. At the range the gate scene's walls occupy, the whole wall
delivers 2–3 levels of 255, and **the ruin is as invisible as the material it was drawn over.**
The seat's own cull says exactly that: *the subject isn't rendered.*

> **So the plant control is marginal on this rig rather than sound.** It caught on axis in rounds
> 1 and 2 and missed in round 3, and the miss is the same rig property as every other finding in
> this session, arriving in the one place that is supposed to be independent of them.

This is reported as a **LOOP-PROCESS §1.1.4(c) condition — an instrument that cannot reliably
demonstrate the thing it exists to demonstrate.** It does not invalidate rounds 1 and 2, whose
plants were caught. It does mean **no wall round can be relied on to validate itself until the
rig question is answered**, and that is one more reason the answer belongs at the gate rather
than in another round of authoring.

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

## 7d. Round 4 — the build offered to the gate, and it is VALID

`r12`, `void_ring` 1, the `compensated` arm. **The plant was caught on axis** (`stamped`), so
§1.1.1 is satisfied for the thing actually being presented rather than for an ancestor of it.
Three of the four rounds are valid; the void one is §7c.

The plant seat's own cull, incidentally, is the finding stated more sharply than any instrument
managed: *"walls receive no light — **0% of standing pixels above 128/255**; every crack, course
and repair is dark-on-dark."*

The family seat's cull is **the fifth independent statement of the same sentence**, across four
builds:

> *"Walls sit at 4–7% of floor luminance — at 1:1 the room has no visible structure, only
> darkness."*

Two things did move, and both are the round's own fixes reporting back:

- **The void now reads as a distinct thing.** *"Above y≈195 the pixels are exactly (1,1,2) with
  zero variance. Not dark — **empty**. Authored void. Everywhere else is more of the same place,
  simply unlit."* At `void_ring` 2 the same seat class read the beyond as *"wall, and it goes on"*.
- **The passage is still found**, though this seat found it by the void behind it rather than by
  the jambs: *"I read it as a passage — barely, and for the wrong reason."*

And Q4 is still **NOTHING**, after the ink fix. At 4–7% of floor luminance the orc layer is
present, correct, world-placed, and unrepresentable — which is the same law as everything else in
this report, arriving on the one clause (§7.1) that was supposed to be carried by *linear
elements that still read at 1×*.

## 9. THE GATE'S RULINGS, AND WHAT WAS DONE WITH EACH

Rafe walked it on the SE. Five items came back. Four were executed; the fifth is a document.

### (1) *"South faces workable in kind — but walls have opted out of history."* — DONE

Aging at the base courses, keyed to `TrafficField`: the floor's own accumulated-traversal field,
in which vaults and shrines sit at **exactly zero**, so a wall beside a route ages and a sealed
room's wall stays sharp — and sharpness then MEANS something. **A wall's traffic is not its own:**
nobody walks on a wall, so the age of a reveal is read from the floor cell it faces, which is the
same cell §6.5 measures it against.

Patina, scuff and arris-rounding. **The polish half is expressed as FORM, not as a pale value
lift** — §8.2.1 banned that for the floor's channel and the floor session paid for the lesson
twice, so four hundred years of shoulders arrive as a rounded arris and the grime arrives as
darkening. Neither asks the lamp for permission. Bible §8.2.2.

Measured as an **A/B against an ageless build of the same family**, so every lighting term cancels
rather than being modelled:

| age | n | Weber | levels | delivered course value | vs the 0.1440 reference |
|---:|---:|---:|---:|---:|---|
| 1 | 4 | 0.048 | 0.75 | 16.5 | below — *deliberately* |
| 2 | 3 | 0.134 | 7.52 | 51.1 | just below |
| 3 | 3 | **0.181** | **12.23** | 46.9 | **above** |

Monotonic, correctly signed everywhere, and sealed cells flat to **0.0000**. Ages 1 and 2 sitting
under the reference is not a shortfall: light traffic on a remote branch should be almost nothing,
and a wall that is visibly grimy everywhere has stopped saying where people walk.

⚠ **The first version of this instrument was wrong and its own numbers said so.** It compared the
base band against the course above it in the same cell, claiming they were illumination-matched
"because they are the same cell". They are not — the base is the SOUTHERN half and the lamp is to
the south — and it returned Weber values scattered from −0.57 to +0.31 with the sign flipping
between neighbours. It would have been read as *the aging does not work*. The A/B replaced it.

### (2) Void gate DEFERRED; the comb/spike marks — DONE

**They were bindings on top planes.** `lash` is an iron strap with three rope turns across it,
which at 32 px is a comb; `strap` is the plain bar, the spike; `patch` is four sawn-grain strokes,
a second comb. Three blind seats had described the first without being told anything was there —
*"a vertical post with three horizontal crossbars"*, *"a stake or rack"* — and all three said it
was holding nothing. Removed; bindings are face-only. Bible §8.3.1a, with what it costs: **a wall
mass seen from above now shows no orc work at all.**

The new requirement — *wall mass beats void by a readable margin* — is measured in
`MASS-READ-REMEDIES.md` §0, and the measurement disagrees with the diagnosis in a way worth
reading before ruling: **wall-versus-void is 0.89 Weber, and wall-versus-FLOOR is 0.05.**

### (3) §6.5 re-scoped — RECORDED

Written into the bible as a standing-distance law, with the original clause kept beneath it in
full. `no authored chase past the ladder` is now a line in the composer, not an intention.

### (4) The §3 mask collapse — FIXED, as a correctness bug

`WallMaskPolicy` in the **logic** layer, where the suite can assert the invariant across all
sixteen masks at once. It was presentation-only arithmetic, which is exactly why nothing could
reach it and why it broke silently. Four tests, exhaustive over the mask space rather than over
the two values that happened to be wrong, and **shown to fail against the old value before being
believed**.

### (5) Mass-read at distance — `MASS-READ-REMEDIES.md`

Three remedies, delivered numbers at the standing case and at 3–4 tiles, costs, laws touched. The
headline: **the rig cannot fix it** (the pipeline is multiplicative, so the lamp scales wall and
floor together — measured at five thousandths of Weber across a falloff change from 1.00 to 0.50),
and **the remedy that can is free and already on disk.**

## 9c. THE POST-RULING BUILD HAS NO VALID ROUND BEHIND IT, and the reason is structural

Plant catches across six rounds: **1, 2, 4, 5 CAUGHT on axis. 3 and 6 MISSED — void.**

Round 6 is the round for the build this report offers, and **its findings are not read.** The
family seat ran, its record is on disk, and its answers were withheld by the harness before anyone
could see them — which is the fix this session made after round 3 doing its job.

**The two misses share a cause and it is not luck.** In both, the plant seat culled — and both
times it culled on something the FAMILY carries rather than on the plant's ruin:

> round 3: *"invisible at play brightness — the subject isn't rendered."*
> round 6: *"walls and floor render on one flat plane at equal value."*

**A plant control is uninformative whenever the candidate carries a defect louder than the plant's.**
The seat spends its cull on the loudest thing in the frame and never reaches the ruin, and §4's
test — *did it catch the plant on the plant's axis* — then returns no on a seat that was reading
carefully and reporting something true.

The defect doing the outshouting is **the mass-read one**, which is item (5). So:

> **The plant control becomes reliable again only after (5) rules.** The process finding and the
> design finding are the same finding, and neither can be closed from inside this session.

⚠ **What was NOT done about it.** Round 6 was not re-run. Running the same round again on the same
build until the plant is caught is exactly the laundering §4 exists to forbid, and it would have
been easy — rounds 1, 2, 4 and 5 all caught, so a re-roll had good odds. Three misses out of six on
one structural cause is evidence; four rolls until a green one is not.

## 9d. THE SECOND SET OF RULINGS (Rafe, 2026-08-30) — five more, four executed

**(1) The material arm is the remedy, run as a bounded round.** Done. `tier1_walls` is the family
the walk carries; the wall stone is now its own darker material rather than the floor's at a
different brightness.

**(2) The perceptual-floor law reads in DELIVERED LEVELS.** The bar is **8 levels**, ruled at
"barely met" — a human verdict on a measured quantity, which is the only way §13.8 lets a floor
exist. Both separations, both arms, at the standing station:

| band | arm | L(wall, void) | L(wall, floor) |
|---|---|---:|---:|
| standing ≤2 | compensated | 80.63 | 14.31 |
| standing ≤2 | **material** | 61.64 | **23.27** |
| 3–4 tiles | **material** | 19.77 | 7.62 |
| beyond 4 | **material** | 7.39 | 1.65 |

**Wall-vs-floor at the standing case is 23.27 levels — 2.9× the bar, and 1.6× the arm it
replaces.** Wall-vs-void drops to 61.64 and still clears by 7.7×. At 3–4 tiles wall-vs-floor is
**7.62, just under** — reported, not chased: a further step down the ladder exists and was not
taken, because the ruling names this arm and the band beyond it is already dark-by-design.

**(3) The review scenes — fixed, and the audit's own diagnosis was wrong.** See §9e.

**(4) Round 6 stands VOID, correctly not re-rolled.** Round 7 on the material build is the fresh
valid round.

**(5) Aging and the binding relocation approved as built.** The no-orc-work-from-above cost is
logged as **issue #167** for the prop/overlay pass — the fix there is world-placed *objects*
standing on a wall top, which are objects rather than tile incident and so are outside §8.3.1,
not a return to baked overlays.

**And the walk's third subject is not available.** The floor session's additive round is **not
merged** — PRs #162, #163, #165 and #166 are all open — so the trail cannot be in the scene. The
walk covers walls-vs-floor separation and the aged bases.

## 9e. The review scenes were dead, and not for the reason yesterday's report gave

Audited across the whole set rather than assumed, because the first dead scene was found by
accident:

| spec | spine | routes | worn cells | |
|---|---:|---:|---:|---|
| `corridor_junction` | 0 | 0 | **0** | **dead** |
| `wall_face_review` | 0 | 0 | **0** | **dead** |
| `tier1_corridor_traffic` | 16 | 14 | 55 / 66 | live — **new** |
| `mixed_distribution`, `tier1_floor_review`, `tier1_wall_review`, `tier1_wall_standing` | | | | live |

**The cause is not the missing rooms.** An empty one-wide cross accumulates traffic perfectly
well. It is the PLAYER, and the mechanism is two pathfinders disagreeing: `FarthestWalkable` picks
the spine's endpoints with a Dijkstra map that **walks through a blocking entity** — measured, all
forty cells still "reachable" with the figure in place — and the spine itself is an A* that does
not. Every route between the halves of a one-wide corridor runs through the figure, A* returns
null, and the field goes to **exactly zero**. A cliff, not a degradation: 40 cells → 0, 5 routes →
0, from one person standing still.

⚠ **Not fixed here.** `TrafficField` is the floor session's live surface (four open PRs on it), and
a concurrent edit would collide with work in flight. Pinned by four logic-layer tests instead.

`tier1_corridor_traffic` carries destinations, a dead end, **and a loop**, so no single figure can
sever it — the right scene design however the disagreement is settled. The two dead specs are left
untouched: both are cited by evidence on disk, and the repo's own rule is that a scene swap
silently invalidates every comparison against that record.

**Re-checkable under the fixed scene:** any verdict about wear, aging or route legibility taken
through those two since the traffic pass landed. The art was there; the field that drives it was
not.

⚠ **And the new scene declares no dark point**, which is a scope statement rather than an omission:
its furthest in-frame floor cell is 5.8 tiles and reads 0.212 against a 0.10 bound. **This scene
fits inside the delivered reach and cannot test the arc.** The arc is tested by `tier1_wall_review`,
which holds two dark points.

## 9a. Two defects the instruments found, both mine, both after they were built

- **The scuff reached 1.83 rungs** and pushed some faces brighter than their own top planes.
  `two_planes` reported a minimum separation of **−0.329 rungs** and named the tile.
- **And that tile was an ID COLLISION.** The aged face set is 108 tiles and the id blocks were
  spaced 100, so face ids ran into `top_h` and **eight face tiles were drawing top-plane files** —
  a top plane's material laid where a reveal should be. The count was right, `missing=0` was
  right, the edge check was right, and the picture looked like a wall. Nothing else in the
  apparatus would have said so.

## 9b. And a scene that cannot exercise the thing it is used to test

**The corridor review scene's traffic field is exactly zero.** A symmetric cross of one-wide
corridors with no rooms and no dead ends gives `TrafficField` nothing to accumulate, so no
traffic-keyed system can be exercised there — not the wall's aging, and **not the floor's wear
either**. That reaches backwards into every round that used it. `tier1_wall_standing` is the gate
geometry with the player at the chokepoint mouth, so a number about the standing case is taken
standing.

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
- **The void — three candidates, unruled, on the panel, AND the measurement says the choice may
  not be the interesting one.** Delivered, on the gate build:

  | candidate | authored | delivered | |
  |---|---:|---:|---|
  | choice 0 | 18 | **1.073** | |
  | choice 1 | 10 | **1.000** | |
  | choice 2 | 0 | **0.001** | |
  | *unlit wall top past six tiles* | 154.38 | **10.445** | for comparison |

  **The three candidates span 1.07 luminance. The unlit wall sits 10.44 above the darkest of
  them.** So the void is an order of magnitude darker than the stone beside it and the three
  choices are within a level of each other — which means the question at the gate is probably not
  *which near-black*, it is *should the void be darker than unlit stone at all, or should unlit
  stone fall toward it*. The panel still switches all three, because §13.2 makes the eye final and
  a luminance figure has never been calibrated against a person holding a phone in a dark room.

  A blind seat separated them unaided and then said the thing that matters: *"Above y≈195 the
  pixels are exactly (1,1,2) with zero variance. Not dark — **empty**. Authored void. Everywhere
  else is more of the same place, simply unlit. **The image gives you no way to tell them apart at
  1:1.**"*
- **Instruments.** Six, all proven failable, legal family clean, both arms clean.
- **Generations spent: 0 of 60.**
- **Device — VERIFIED, twice.** The gate build was `7e64cdb`. **The post-ruling build is
  `ea9eedf5`**, all eight checks green on the handset, and it carries the `material` arm because
  that is what `MASS-READ-REMEDIES.md` recommends:

  ```
  [Tier1] BUILD IDENTITY: commit=ea9eedf5b78e7986921568c1d1b22b5bff5bd7cf built=2026-08-30T07:03:53Z
  [Tier1] boundary wall: family=boundary_wall_material_v1 face=24 top=63
          void=129(choice=0,ring>1) missing=0 face_suppressed=63
          planes(top=114.7 face=61.79) edge_check=46/OK
          bindings=11(cramp:2,lash:3,patch:1,pin:3,strap:2)
          age0..3=2/11/7/4 traffic=spine:18/routes:25
  ```

  The other arm is one environment variable away — `TIER1_WALLS` / `TIER1_BINDINGS` pointed at
  `tier1_walls_compensated`.

- ⚠ **The post-ruling walk build is INSTALLED, NOT VERIFIED.** It exported, built and installed
  cleanly onto the SE, and then `verify_on_device.sh` could not launch it:

  ```
  Unable to launch com.rafehatfield.catacombsofyarl.tier0 because the device was not,
  or could not be, unlocked.
  ```

  **Installed and verified are different things on this project and the distinction is not
  cosmetic** — a session once reported a build "verified on device" on the strength of an export
  exiting 0, and it had not been installed at all. So this one says what it is. One command with
  the phone unlocked closes it:

  ```
  TIER0_EXPECT_SCENE=tier1_wall_review TIER0_EXPECT_WALLS=1 \
  tools/tier0_harness/verify_on_device.sh
  ```

  It must come back with all eight checks green and the wall line reading
  `family=boundary_wall_material_v1 … missing=0 … edge_check=46/OK … age0..3=…`.

  `verify_on_device.sh` named `tier1_floor_review` literally and returned MISS on a correct wall
  build; the scene is a parameter now, and the wall checks are opt-in so a floor build is not
  failed for lacking walls. Both new checks were shown able to fail against the floor gate's own
  log before either was believed (§13.5).

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
