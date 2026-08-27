# TIER ONE, SESSION ONE — the Boundary's floors, and the rig they are judged through

**Status: round evidence, not gate evidence.** Nothing here lands. ART-BIBLE-v0 §13.1 gives the
landing gate to Rafe, in-scene, on device, and this document is what the run produced on the way
to it.

---

## 0. THE HEADLINE

**A floor family exists, it is the first real candidate art this project has composed, and the
thing that made it possible was not generation.** Forty generations conditioned on C-GAB at the
measured levers returned **0 of 40** tiles that pass the incident-free bar §8.3 sets for a base
tile. That is the fifth consecutive campaign on this surface to return zero architecturally
conformant tiles, and bible §13.7 already records the general form as a measured platform fact:
*architecture and conditioning do not exist on the same surface; any pipeline needing both
composes across surfaces.* So the wave was spent on **material** — palette, value ladder, grain —
and the **architecture** was laid procedurally against it.

**Four engine defects were found, and three of them were silently destroying the very law this
session exists to satisfy.**

| # | defect | consequence |
|---|---|---|
| 1 | `TileThemeConfig.PositionHash` is **linear** | variant choice is periodic along *every* line. With 24 floor variants the same tile recurred **every third cell diagonally**. A 24-tile family was delivering 3. |
| 2 | The carried light **never followed the player** | every device walk since tier zero was walked through a lamp anchored to the spawn tile. §6.5's derivation rests on *"the player is the lamp"*; it was not true anywhere but at spawn. |
| 3 | Base variants differed in **mean value** by 6.4 points | the 32px grid drew itself across the room in flat brightness — §8.3.1's law with no feature at the constant position at all, only the cell's own average. |
| 4 | The trodden route was derived as the **graph diameter** | the farthest cell from anywhere is always the end of a dead end, so the route ran *into* the cul-de-sac built to be the neglected passage. |

**A blind seat found #1 before the arithmetic was checked**, and its measurement was exact:
*"eight pairs at exactly (+3 rows, +3 cols) … that is a lattice."* Confirmed independently:
`h(x+1,y+1) − h(x,y) = 112648`, and `112648 mod 24 = 16`, whose additive order mod 24 is **3**.

**Round 1 of the seats was VOID** under LOOP-PROCESS §4 — the plant was not caught. The diagnosis
is that the plant was under-built, not that the seat was soft, and it is recorded in §10.

---

## 1. WHAT WAS DECLARED, AND WHAT RAN

Declared before the first call (`generate.py`, gauntlet clause §1.1.3):

| | declared | spent | outcome |
|---|---:|---:|---|
| base wave | 40 | **40** | 0 clean. Material harvested from 8 donors. |
| overlay wave | 32 | **32** | **0 used.** Culled in full — §7. |
| reserve | 48 | **0** | not needed; the round did not re-generate |
| **session** | **120** | **72** | 48 unspent |

Pool: 2822 → 2750 generations. Ledger: `gen/ledger.jsonl`, 78 rows, every call including its
redacted payload.

**Refusals held.** Conditioned on **C-GAB only**. Not A-HEB (UNMEASURED as a parent, §8.2.1
item 4 — this session declined both to spend 20 generations measuring it and to use it under an
unknown-rate marker). Not B-KAB (retired). Not A-VAB (prop stock). No constant in
`ring_instrument.py` was altered. No rig number was tuned by this session — §9.

---

## 2. A PROCESS VIOLATION, NAMED

**LOOP-PROCESS §3.6 was broken, and it was caught by a mid-flight status check rather than by
this session.**

> *The critic runs every round, not at the end. A session that batches N candidates and presents
> them uncritiqued has not run the loop; it has run a generator with a delivery step.*

Both waves completed — 72 generations — and this session screened them **mechanically only** and
carried straight on into composition and C# with **zero seats run**. The mechanical culls were
legitimate (§1.1.1 culls disqualifiers without ceremony) but they are not the critic, and the
composed family, which is the thing that would actually have reached the human gate, had been
seen by nobody.

Corrected in-flight: all further work stopped, the seat apparatus was built, and rounds 1 and 2
ran before anything else. The cost is real and is not hidden — the engine defects in §8 were
found *after* the composition was built rather than before, and two of them (#1, #3) were found
by the seat rather than by the builder.

---

## 3. THE BASE WAVE — 0 of 40, and why that is not a surprise

`SCREEN-base.json`. Every child screened by `ring_instrument.py` (unchanged, untuned) and this
session's `field_laws.py`:

| code | children |
|---|---:|
| INCIDENT (a component contained inside one cell) | **40** |
| FRAME (a contained component that encloses) | 12 |
| GRID (structure on an exact fixed pitch) | 8 |
| SEAM (the tile does not meet itself) | 7 |
| RING (`ring_instrument`, unchanged) | 4 |
| **survived every screen** | **0** |

Consistent with every prior campaign on this surface: the wall gauntlet's 100/0, the composition
spike's 8 rounds/0, §6.4 Stage 1's 1-usable-in-60 on walls, tiles-pro's 0/114 two-plane, and
§13.7's measured **architecture 0/100**.

**This is not a reason to lower the screen.** It is the condition LOOP-PROCESS §1.1.6 legislates
for: *when any asset class stalls, the next session is a measurement pass, not another blind
batch.* The measurement pass is §4.

---

## 4. THE MEASUREMENT PASS — what a shipping floor set actually does

`calibrate_against_bar.py`, `bar_calibration.json`. 29 floor tiles across the asset bar's six
shipped example maps, **431 laid floor cells**. Statistics only; **no bar pixel enters this repo**
(§13.3).

- **55.2% of the floor cells those maps actually lay carry ZERO contained components.**
  Cell-weighted p90 of the largest contained component: **0.046 of the tile**.
- **Seam ratio never exceeds 1.64** across all 29 tiles. Zero would be called SEAMED at the
  threshold of 2.0. Median 1.09.

So the incident-free bar is **reachable**, not utopian: more than half of a shipped commercial
floor set already meets it. And the seam threshold is corroborated by the accepted corpus with
22% of margin, which is what §13.6 asks for.

⚠ **The bar is used to show the bar is reachable, never to set it.** About 40% of the bar's laid
cells would fail Yarl's incident threshold, and the same corpus carries FRAMEs on 7 tiles and
GRIDs on 3 — constructions §12.1 and §8.3.1 forbid outright here. §13.3's origination rule: *a
rule whose only justification is "the bar does it" is conformance and is refused.*

### 4.1 Two bugs this pass surfaced, one of them in a neighbouring module's blast radius

**Mine, and it produced a confident wrong answer.** The first run dropped the alpha channel and
read 4 of 7 tiles as SEAMED with ratios to 8.23 — it would have retired a correct criterion as
unreachable. It was reading transparent sheet padding as material. What sent it back for a look
was an asymmetry that could not be true of a deliberate tileset: five of seven tiles edge-matched
*exactly* in x while every one was wildly mismatched in y.

**Underneath it, a latent trap in shared code.** `measure_bar.Tiles` keys its tileset table on
`firstgid` alone, and this library has **two sheets at firstgid 1** — `uf_terrain.png` in five
maps and `uf_map.png` in the sixth. A table accumulated across maps silently resolves every gid
below 1651 against whichever was written last.

> ⚠ **CHECKED, because it would have been the more serious finding: `measure_bar.py` DOES NOT
> have this bug and `bar_measurements.json` is unaffected. §6.5's value stack — the bible's
> load-bearing law — stands exactly as measured.** It `continue`s past any map with no walls
> layer *before* accumulating that map's tilesets, so the overworld never enters its table.
>
> **But the guard that saved it is incidental**, and that is its own finding under
> LOOP-PROCESS §4.2. It skips that map because *"it cannot answer a wall question"* — a reason
> about layers, not about gid resolution. Nothing in `Tiles` goes red when two sheets share a
> firstgid. Any future reuse that does not happen to need a walls layer inherits the
> mis-resolution silently. `calibrate_against_bar.py` therefore resolves per-map and never builds
> a shared table, *and* asserts the collision explicitly.

Probes kept: `bar_sheet_probe.py`, `bar_resolver_probe.py`.

---

## 5. THE INSTRUMENT — `field_laws.py`

`ring_instrument.py` reads **one 32×32 tile**, and §12.1 rules its limit **structural**: *a ring
is judged AS LAID; a single tile cannot answer this clause.* `field_laws` is not a better
threshold — it is a different **input**. Every test runs on the **3×3 tiling** of the candidate,
where the centre cell has neighbours to continue into, which is what lets one mechanical test
separate the two things §8.3.1's mirror requires separating:

| | | |
|---|---|---|
| a property of the material | a joint between two stones | runs off the edge, joins its copy next door, one component spanning cells |
| a thing that happened to it | a crack through one stone | terminates inside the cell — so it sits at the same offset in **every** cell |

Four tests: **incident**, **frame** (C-GAB's measured failure, invisible at tile scale),
**seam**, **grid**. All four are geometry. **No register clause is instrumented** — §13.4 is
LOCKED, there is no dread score and no staging detector, and *nothing is staged* / *nothing is
ruined, things are used up* are carried eye-side.

### 5.1 Positive controls — §13.5 / LOOP-PROCESS §4

`controls/CONTROLS.json`. **5 of 5 pass**: a legal construction returns CLEAN, and each of the
four defects fires on its own planted axis (§4.1's law: the plant carries the defect on the axis
the lever claims).

### 5.2 Two corrections, both surfaced by a check rather than by review

- **`grid` measured run STARTS, and reflection moves them.** With runs of unequal length, flipping
  a tile can create or destroy an exact arithmetic progression. Base variant 9601 screened CLEAN
  and **four of its eight orientations then screened GRID**, with nothing about the tile changed.
  A criterion whose verdict depends on which way up you hold the tile is not measuring the tile.
  Corrected to run **centres**, which are reflection-invariant. Caught only because the oriented
  variants are re-screened rather than assumed to inherit their parent's verdict (§4.2).
  The corrected criterion is also strictly better: its first act was to red this module's own
  clean fixture, whose courses of 11/10/11 put the stone bands at centres 5.5/16.0/26.5 — an
  exact progression. **That fixture was the same construction the first composed field rendered
  as plain brickwork.**
- **The incident threshold was absolute, not fractional.** 12 px is 1.17% of Yarl's 32px tile and
  0.52% of the bar's 48px one — so the corpus calibrating the threshold was being held to less
  than half the strictness of the work being checked.

---

## 6. THE FAMILY

`src/Presentation/assets/tier1_floors/`, `MANIFEST.json`.

**Base — 3 material tiles, all `field_laws` CLEAN.** A wrapping irregular flagstone bond, laid as
a **Voronoi partition of the torus** with a per-seed rotated superellipse metric. Filled with the
wave's measured material: pooled ladder, tint and grain amplitude from 8 donors, grain applied as
**wrapping value noise at two spatial scales**.

> The first bond was a running brick bond and it **read as brickwork** — uniform coursing, bed
> joints every ten pixels at one angle. That is §3.1's finding arriving on the ground plane: *a
> plane textured like elevation reads as elevation.* Coursed masonry is what a wall is a picture
> of; a found-stone floor (§7.4) is not laid in courses at all.

**Oriented — 24 ids.** 3 tiles × 8 orientations of the square, emitted as real assets and each
**re-screened**. This is §6.3 paying out: an asset authored to *receive* light carries no
direction, so there is nothing in it to break by turning it. A tile with a baked key light could
not be rotated at all, and this variety would cost eight times the art.

**Incident overlays — 27, authored (§7).** crack ×6, chip ×5, wear ×6, grit ×5, debris ×5.

**Channel — 4, §8.2.1.** An alpha wash at the family's own polished value: it lifts the joints
more than the stone, which delivers the seat's *"erase the joint detail inside it so joints fade
where feet cross them"* without needing to know where any joint is.

### 6.1 The field, measured — `evidence/FIELD-LATTICE.json`

`lattice = 1 − mean(variance at each intra-cell position) / variance of the field`. 1.0 is a
clone field; 0.0 is position carrying no information.

| | lattice |
|---|---:|
| **anchor — clone field** (one tile, one orientation: what five seats culled) | **1.0000** |
| the family, base tiles only | 0.046 |
| **the family, as the renderer lays it** (24 oriented variants + incident) | **0.039** |
| **anchor — independent limit** (every cell its own composed tile, own seed, own bond) | **0.014** |

Before the `PositionHash` fix (§8.1) and the mean normalisation (§8.3) the same field measured
**0.31** — a third of its variance predictable from position alone, with a 24-tile pool. The
family is now within a whisker of the limit a field of 64 individually-composed tiles reaches.

⚠ **No threshold is declared and none should be read in.** §13.6 forbids calibrating one on the
work seeking acceptance, and no accepted floor *field* exists to calibrate on. This is an
ordering, and per Rafe's 2026-08-27 relabelling of the ring instrument, an ordering **rules
nothing**.

---

## 7. THE OVERLAY WAVE — 32 generated, 0 used

`prompts/incident_overlay.json` asked for cracks, wear marks, debris and grit as transparent
decals, **unconditioned**, and it declared its reason before the wave ran: conditioning a decal
on C-GAB would hand down the tile-ness and the frame (§5.5's 12/12 propagation).

**That risk was real and the opposite one landed.** With no reference the generator has no idea
what material it is marking, so it does not draw a mark on a surface — **it draws a thing**. The
crack family came back as small centred maroon blobs. They are objects: closed, centred,
off-palette, pictures of nothing on this floor.

**The declared screen was also too weak, and its gap is named rather than patched over.** It
tested alpha coverage and edge contact — whether the object was *decal-shaped* — and never
whether it was **made of this stone**. §5.1's zero-mercy palette gate is the clause that catches
it and it was not in the band the prompt declared. Added: mean chroma > 12 culls. **31 of 32
culled on that check alone**, at chroma 12.2 to 36.5 against a family whose measured tint is
within 1% of neutral. The one survivor is a debris tile and is not used either — the family is
authored end to end.

The incident is therefore **authored from the family's own measured ladder and tint** — the same
move the channel already makes, and for the same reason. §8.1 is a claim about the *surface*:
*grime walked into a surface until it is part of it.* An incident is a modulation of the
material, not an object resting on it.

**What generation did buy is real and is not discarded:** the ladder, tint and grain amplitude
every authored mark is drawn with came off the base wave's donors.

---

## 8. ENGINE FINDINGS

### 8.1 `TileThemeConfig.PositionHash` was linear — it drew a lattice at every variant count

The old hash was `|(x*7919 + y*104729) & 0x7FFFFFFF|`. A linear function has a **constant
difference along any straight line**, so modulo a variant count the choice advances by a fixed
additive step and cycles with period `N / gcd(step, N)` along every row, column and diagonal. Not
a weak hash — **periodic by construction, at every N**.

With 24 floor variants: diagonal step `112648 mod 24 = 16`, additive order 3. **Every third cell
down the diagonal is the same tile, out of a pool of twenty-four.**

It breaks §8.3 in the worst possible place: the variant system is the *only* mechanism the bible
gives for keeping a tiled field off the motif trap, and this function was quietly undoing it.

Fixed with a bit-mixing finalizer. Verified: repeats at distance 3 fall to chance level in all
four line families (60/75/78/66 against a chance expectation of 67 per 1600 cells).

⚠ **It changes which variant lands on which cell for every existing theme.** Nothing looks worse
for it, but captures taken before this commit will not reproduce byte-for-byte.

### 8.2 The carried light never followed the player

`ReviewLighting.Attach` positioned the light on the spawn tile and the instance was dropped —
no reference kept, no update anywhere. **Every headless capture is taken on the spawn frame, so
nothing ever went red.** The device *walk* was not: walking moved the figure out of a stationary
pool of light.

It is a precondition failure for §6.2.1, not a nicety. §6.5's derivation rests on *"the player IS
the lamp, and stands south of a north wall — so the face is always one tile nearer the light than
its own top."* A lamp anchored to spawn does not deliver that relationship anywhere but at spawn,
and §6.2.1's pass — legibility **across** the lit radius at gameplay distance — cannot be run
through it at all.

### 8.3 Base variants differed in mean value — the grid drew itself in flat brightness

Means 106.1 / 112.5 / 109.5, a **6.4-point spread**, against a crack-to-stone contrast of ~35. A
seat measured the steps at +9.0, −6.1 and +6.0 and said the obvious thing: *"the grid draws
itself onto the ground."*

**It is §8.3.1's law in its purest form and the easiest instance to miss, because there is no
feature at the constant position at all** — the treatment sitting at the same place in every cell
is the cell's own average brightness. Each tile's mean is now normalised to the family's;
stone-to-stone variation stays inside the tile. Spread: **0.56**.

### 8.4 The trodden route ran into the passage built to be neglected

§8.2.1's channel *"leads somewhere: stairs down, or rooms that matter."* The first derivation took
the graph **diameter**, which is structurally wrong in a way no tuning reaches: **the farthest
cell from anywhere is always the end of a dead end**, and a dead end is precisely where traffic
does not go. From the engine's own channel map:

```
##MM#.......      the four-cell stub built to be the NEGLECTED passage came out as the
##.MFMMMMR..      most trodden ground in the scene, and room A's north row came out
#####.xxxxxx      neglected instead
```

The scene was authored with this risk named in its own comment and it fired anyway. Rooms are the
endpoints; corridors are what the route passes *through*. Corrected to route between the two
largest rooms; a room cell is one whose whole 3×3 is walkable, which under-reports rooms rather
than over-reporting them — the safe direction, because the whole point is that the route must not
terminate in something that is not a room. Now:

```
#####xxxxxxx      channel down room A's middle, wall-to-wall through the chokepoint,
##xxx...MR..      into room B; the west stub neglected; all four §8.2.1 contexts present
########F###
```

⚠ **In the shipping game the stairs override this and the clause names them first.** The review
scene has no stairs at all — tier zero removed every losable state from it — so "the two largest
rooms" stands in. They are not the same rule, and the one that ships is the one with stairs.

### 8.5 The channel's shoulders

The first planner added one shoulder or the other by hash, reasoning that a constant-width band
is §12.1's *"uniform ribbon … answers to nothing"*. The reasoning was right and the mechanism was
wrong: **dropping a shoulder does not make an edge wander, it makes the band end on a cell
boundary** — a straight 32px line, which is §8.3.1's lattice arriving through the one feature
meant to read as wear. Visible in the capture as square steps down the side of the polished path.
The wander belongs *inside* the shoulder tile, and now lives there.

### 8.6 A silent no-op, caught by the move §4.2 prescribes

The first capture with `--floor-overlays` produced a PNG **byte-identical** to the run without it
(`sha256 0110aa69…` both ways). A whitespace-sensitive patch to `capture_corridor.py` had not
matched, so the flag was never passed. Caught by comparing bytes already on disk — *"ask of any
fix: what goes red if it silently does nothing?"* The engine now reports which branch it took on
every boot, so a capture missing the incident system cannot be mistaken for a floor that has none.

---

## 9. THE RIG LADDER — §6.2.1

`ReviewRigPanel`, `ReviewLighting`. Live on-device knobs for **radius**, **falloff** and
**ambient level**, current value on screen, every change and every `MARK WALK` written to `Diag`
(pullable off the phone — there is no console on iOS).

- **Falloff** is a new parameter: an exponent on the smoothstep, shaping the ramp without moving
  the reach. It is the knob the gate's own diagnosis is about — *"the pool is narrow, the falloff
  is steep, and §6.5's stack is legible in a band around the player and gone outside it."*
- **Ambient** scales brightness and holds hue, deliberately. §6.2.1's third bullet: this is a
  readability tuning, not a licence to flood the Boundary with light.

**Every default reproduces the previous rig exactly** — falloff 1.0 is the plain smoothstep this
class always drew, ambient level 1.0 is the marker's colour unscaled. **This session did not tune
a single rig number.** §6.2.1 gives the pass to the human gate, and a builder who shipped a
"better" starting point would have ratified the rig by the back door and re-fired §6.2's
re-derivation rule without anybody deciding to.

The panel **starts collapsed**: the first capture through it had it open and it covered the left
third of the scene and half its height — the floor it exists to make judgeable.

---

## 10. THE SEATS

`evidence/seats/`. Fresh `claude -p`, cwd outside the repo, never given the bible (§3.1, §3.2).
Questions ask what the rules exist to make answerable — *which way would you walk* — never whether
a rule was followed (§3.3).

### 10.1 ROUND 1 — VOID

**LOOP-PROCESS §4: the plant was not caught, so the round is void and its findings are not read.**
Not discounted — void.

The plant seat culled, but for **repetition** — *"A three-tile strip of floor is duplicated
pixel-for-pixel twice on the same screen"* — a defect the real family shared. It never separated
plant from candidate.

**The diagnosis is that the plant was under-built, not that the seat was soft.** The first plant
put a 4px collapse hole, a moss tint on joint pixels, and a 9×9 dithered cobweb in one corner.
All three rendered; none read. The seat described *"~55 dark round pits … the same 14px diameter
everywhere"* (the holes), and crack lines *"hue-shifted toward olive"* (the moss). §4 asks for *a
picturesquely RUINED floor* and picturesque is the operative word — the first attempt was a
texture with small dark circles in it. §4.1's law binds the plant's amplitude as well as its axis.

**The seat's rigour is not in doubt**, which is why the void is charged to the plant. It found the
`PositionHash` lattice mathematically — *"eight pairs at exactly (+3 rows, +3 cols), six at
(+4 rows, −4 cols)"* — before the arithmetic had been checked, and the arithmetic confirms it
exactly. Two findings from that round were verified **independently, from first principles**, and
acted on as code defects rather than as critic findings: §8.1 and §8.3.

**A second defect in the round-1 apparatus, recorded because the two agreed by coincidence.** The
transcript parser matched `^LABEL:\s*(.*)$` on a single line, and the seat writes its labels as
markdown headings with the answer on the line *below* — so every field held the restated question,
and the plant check was grepping text that could not contain the vocabulary it looked for. It
returned VOID, which was the right verdict from the wrong input. A check that is right by
coincidence is not a check.

**And the plant check itself was wrong in a way that would have made it decorative.** Its word
list included *crack*, *cracked* and *damage* — and §8.3 puts **cracks in the legal incident
set**; the shipping family carries a crack overlay family at rate 0.11. A control that greens on
the thing it is controlling for is worse than no control. Tightened to vocabulary exclusive to
the plant (collapse, cobwebbing, moss, rubble, ruined), and given both controls: it does not fire
on either round-1 transcript, and does fire on text naming the ruin.

### 10.2 ROUND 2

*(filled in below from `evidence/seats/SEATS-r2.json`)*

---

## 11. WHAT IS OWED, AND WHAT THIS BUILD CANNOT ANSWER

- **§6.5's value stack cannot be read in this scene.** The walls are the tier-0 programmer-art
  stubs — the honest mock, because the sighted round's walls are *known-culled* and seating the
  floors beside art the bible has already struck would contaminate any verdict. The cost is that
  the stack is a relationship between the wall's two planes and the floor, and a stub wall has no
  meaningful value. This build answers *is the floor legible, and does the rig make it legible
  across the lit radius*. It does not answer *does the floor sit between the planes*. The floor's
  measured albedo is in the manifest so the wall round that comes next can derive its planes from
  a floor that exists — the right order, and the one §6.5 was denied when it had to invent the
  floor.
- **The magenta stub walls dominate the frame** and are a known contaminant on any seat's
  reaction. Declared in the seat prompt's scope block rather than worked around.
- **`HasJunction` reports NO on this scene.** It is a corridor-junction assertion; the *which way
  would you walk* choice here is posed by the channel and the neglected passage instead. The
  harness prints its ABORT line and still writes the capture; not fixed, recorded.
- **The unspent 48 generations.** The round did not need them: the yield problem was not solved
  by more samples on a surface measured at architecture 0/100.
- **A-HEB is still unmeasured.** This session refused it rather than spend 20 generations; §8.2.1
  item 4 remains open.

---

## 12. EVIDENCE

| what | where |
|---|---|
| generation ledger, 78 rows, every call | `gen/ledger.jsonl` |
| base wave screen, 40 children | `SCREEN-base.json` |
| overlay wave, geometric screen | `SCREEN-overlay.json` — *not* the operative screen for a decal; the declared band + palette check in `compose_family.screen_overlay` is |
| instrument controls, 5/5 | `controls/CONTROLS.json` |
| bar calibration, 29 tiles / 431 cells | `bar_calibration.json` |
| field lattice + anchors | `evidence/FIELD-LATTICE.json`, `evidence/field_*.png` |
| the family | `src/Presentation/assets/tier1_floors/MANIFEST.json` |
| in-scene captures, lit, device pixel size | `evidence/scene_family.png`, `evidence/scene_plant.png` + `.log` |
| seat transcripts, verbatim | `evidence/seats/` |
| bar-resolver probes | `bar_sheet_probe.py`, `bar_resolver_probe.py` |
