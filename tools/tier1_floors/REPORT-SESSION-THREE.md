# Tier one, floor session three — the ashlar rebuild, and the ruling on K

**Branch** `worktree-tier1-floors` · **generation budget spent: 0 of 80.** Not one PixelLab call
was made. Session two's measured finding — *generation cannot supply architecture; 0 of 40 base
candidates were clean* — held, and everything below is composition across surfaces from the
material the donor manifest already carries. The budget is untouched and available.

---

## 1. K IS RUNTIME. The tile set stays at 81 and no K is authored at all.

The question on the record: *can the stone class live at compose/shader time as a per-stone value
remap keyed on shared coordinates — tile set stays small, K becomes runtime — or does §6.3's
authored occlusion fail to survive a remap, so K must be authored?*

**§6.3 was never the blocker.** Measured on the crossing-joint geometry and unchanged by topology:

| remap form | authored joint-to-stone contrast retained |
|---|---:|
| **additive offset** | **100.0%** |
| flat replacement | 0.0% |

The contrast *is* the occlusion — §6.5 derives the joint as dark **because enclosed** — so an
additive offset preserves every internal difference and a replacement destroys the plane. The
remap must be additive, and additive is available at no cost.

**The blocker was the KEY, and it is a theorem about the corner.** Four tiles meet at a grid
corner. Tile (x,r) shares one boundary family with its eastern neighbour, one with its southern,
and **nothing with its diagonal**. A stone covering a corner is therefore seen by four tiles with
no common data and cannot be addressed by any scheme.

> **Authoring K does not dodge this.** Corner classes as an index dimension make the same
> assumption — that a tile's regions map to its four corners. On the crossing-joint geometry 27 of
> 77 stones (19.9% of stone pixels) spanned a boundary with no shared key, and they would have
> failed identically either way. **The geometry decides, not the K.** That is why K could not be
> sized until the rebuild existed.

Re-measured against the ashlar geometry, and re-measured again after every later change to it:

```
wholly inside one tile          -> the tile's own address    : 114
spans exactly ONE vertical bdy  -> that boundary's family    : 112
---- everything below has no shared key and must be zero ----
contains a grid corner                                       :   0
spans a horizontal boundary                                  :   0
spans more than one vertical boundary                        :   0
UNADDRESSABLE                                                :   0   (0.0% of stone px)
crossing-joint geometry, for comparison                      :  27   (19.9%)
```

Cost of the authored alternative, measured and on the record anyway: 457 B/tile, 3 ms/tile —
K=2 → 2,592 tiles / 1.2 MB; K=3 → 13,122 / 6.0 MB; K=4 → 41,472 / 19.0 MB. Cost was never the
discriminator.

---

## 2. Rulings (1) and (2), discharged as one rebuild

### The value step, superseded by construction

| | boundary-to-interior value step |
|---|---:|
| crossing-joint geometry | **7.44×** |
| blended (session two) | 2.95× |
| **course-aligned ashlar** | **0.59×** |

Below 1.00 — a tile boundary is now *quieter* than the material around it. With the grain switched
off it measures **exactly 0.000**, and that is what named the remaining culprit: the residue was
never value, it was texture. Two structural fixes followed rather than a tuning pass.

- **Grain belongs to the stone, not the tile.** `wrap_noise` wraps against *itself*, so two
  adjacent tiles drew unrelated material. A per-tile crossfade between family-keyed fields reached
  0.771 and left tile interiors measurably rougher than tile edges — a smaller lattice, still a
  lattice. Each stone now draws a grain patch chosen by its address and samples it in
  **stone-local coordinates measured from its boundary**, so both tiles either side sample
  consecutive columns of the same patch.
- **So the tiles carry the bond and nothing else.** Value and grain are both painted at compose
  time from the world address. There is no reach, no falloff, no whole-tile renormalisation.
- **And so there is no channel tile set.** Wear is a property of the stone, so the trodden channel
  needs no second 81 tiles and no longer has a straight edge on the tile lattice — it ends where a
  stone ends, which is what §8.2.1 asked for and a per-cell channel could never give.

### The bond, and what each family does

Every one of the four does real work. `fW`/`fE` place the head joints — and because tile x-1's
east family *is* tile x's west family, both tiles agree where their shared stone begins. `fN`/`fS`
carry the arris profile of the bed joint **on** their boundary, built to return to zero at both
ends of a span so a profile change at a vertical boundary is invisible.

Stones are 9–23 px wide against courses of 9–20 px. A tile may **sand one head joint away**,
merging two stones — exactly one, never both, because dropping both leaves a stone spanning two
vertical boundaries, which is unaddressable. The constraint decides it, not taste.

---

## 3. The measurements

| | ordinary | with channel |
|---|---:|---:|
| largest connected region (session one: **99.1%**) | **1.3%** | 1.3% |
| stones ≥64px | 226 | 226 |
| boundary step ratio | **0.59** | 0.42 |
| continuity — lines crossing a vertical boundary | **1.00** (224/224) | 1.00 |
| grid hiding — boundary bed vs mid bed, density / value | **1.00 / 1.00** | 1.00 / 1.00 |
| boundary column vs other columns | 0.56 | 0.56 |
| course heights | **5 distinct** [10,12,15,18,20], modal 0.25 | same |
| lattice score | 0.273 | 0.280 |

**Channel legibility**, measured against *the same stones unpolished* (1.000 = delivered nothing):

| texture | variety | arris |
|---:|---:|---:|
| **0.350** | **0.578** | **0.775** |

Every wear term is a **subtraction**. §8.2.1 is binding — polish signals by absence, never
brightness, because under a carried lamp brightness is what the light is saying.

---

## 4. Instruments, and the eight defects their own plants found

No instrument's pass counts until it has demonstrated it can fail (§4, bible §13.5). Six plants
fire; building them found eight real defects, five of them in the instruments themselves.

| plant | fires | on the clean field |
|---|---:|---:|
| `per_tile_value` — stones addressed by the tile that sees them | 52× | 0.59 |
| `value_lattice` — a value ramp on the tile grid | 53× | 0.59 |
| `boundary_frame` — a joint along the tile's own edge | 4.48 | 0.56 |
| `broken_courses` — coursing that does not travel | 0.00 | 1.00 |
| `uniform_courses` — one course height everywhere | 1 spacing | 5 |
| `flat_channel` — wear that takes nothing away | 1.000 exactly | 0.35 |

**What the plants caught:**

1. **A continuity test that counted head joints as failed lines** and read 0.4978 on a sound
   field. A joint that was never travelling cannot fail to travel.
2. **`0.0 or 1.0` is `1.0`.** The plant that severed *every* course scored a perfect failure and
   was reported as a pass. Explicit `is not None`, never truthiness, on any value whose legitimate
   range includes zero.
3. **A class mask split at the nominal joint position while the joint wandered**, leaving 1px
   slivers of a neighbour's value with no joint between them — the very seam the construction
   exists to prevent, reintroduced beside every head joint.
4. **Every spanning stone exactly 16px wide.** Constant extent is constant position.
5. **An atlas plant aimed at a family combination the field never lays** — nothing read it, and
   the check reported itself decorative. Correct verdict, wrong reason: the instrument was fine
   and the plant was pointed at nothing.
6. **The three wear constants do not share a null.** Grain and spread are multipliers on what a
   stone keeps (null 1.0); arris is a fraction of the way the joint rises (null 0.0). Setting all
   three to 1.0 built the most worn floor the system can make; the instrument correctly reported a
   visible channel; the plant read that as the instrument failing. Two mistakes agreeing.
7. **"Texture" was measuring joint contrast and calling it grain** — a 3×3 window straddling a
   joint reports the joint.
8. **The channel ratio was mostly the band's own content.** On a field with *no* channel, the
   inside/outside ratio for a 2-cell band runs 0.74–1.39 across the seven bands of an 8×8 field —
   wider than the effect being looked for. The band is now differenced against itself.

### The gap nobody was watching: between the tool and the game

Every number above was measured on a field the composer built in memory. What **ships** is 81
atlases and a grain bank, read by the engine. `verify_atlas_path.py` walks the shipped path and
compares:

```
first run     331 of 65536 pixels differed — the composer recovered luminance from its own
              colourised output while the atlas stores an exact ladder rung
after that     50 differed — the bank ships as one byte per sample at 1/64, and the composer
              was composing against the unquantised float
now             0 differ, on BOTH arms (no channel, and channel declared)
              and a single altered ladder index in live data is CAUGHT
```

The channel arm was added later and matters: the first version ran with no channel declared, so
every wear term could have been wrong in both directions and the check would still have said
IDENTICAL.

---

## 5. Two things that would have shipped the wrong picture

**There are two files named `CatacombsOfYarl.Presentation.csproj`** — one at the repo root and one
at `src/Presentation/`. **Godot loads the root one.** Building the other succeeds, prints
`Build succeeded.`, and changes nothing Godot will run. The symptom was a `Report(...)` line that
plainly exists in `Main.cs` producing no output at all, twice, while the scene rendered happily
with the previous assembly. The same trap applies to `--import --path src/Presentation`, which
prints *"Can't run project: no main scene defined"* and imports nothing; the new atlases then
failed at load with *"No loader found for resource"*, which reads as a bad asset rather than an
un-run import. In that state the floor overlays reported `drawn(grit=0 event=0 channel=0
occlusion=0)` and the capture still looked plausible.

**The family had no way to reach the device.** `build_review_app.sh` has knobs for the scene, the
theme and the overlays and had none for the floor family — so every device build since the
edge-matched family was written showed whatever the theme picked, under the family's name, at the
one gate that decides anything (§13.1). `TIER1_ASHLAR` added. The family cannot ride in on
`TIER0_THEME` because it is not a tile role: the theme's floor entry is a **magenta placeholder**
that exists only so a sprite is present to repaint. Magenta on purpose (LOOP-PROCESS §4.2) — a
theme fallback that looked like stone would mean a capture of the wrong floor reviews as the right
one.

---

## 6. What the blind seat found that four instruments passed

The first round on the ashlar (transcript: `evidence/seats/r7pre_F1_transcript.txt`) **culled it**,
and named three things nothing in this session was measuring.

> **Q1: "Cut stone blocks — rectangular sandstone-brown pavers laid in a running bond, mortared."**

That is the first time in three sessions the material has been named correctly. Session one drew
*brickwork* and then *dried mud*; session two's family read as flagstone but carried a tint
lattice. Ruling (2) delivered its objective.

> **Q5: Repeated.** — and **CULL: "Four hundred years of heavy use and endless crude repair, and
> the floor is unmarked, uncracked, unpatched, unworn."**

The three findings, all answered in this branch:

1. **"The floor reads as a stack of horizontal stripes before it reads as stone."** Enclosure,
   boundary step, continuity and grid hiding all passed that floor, because a regular course
   rhythm is not a tile artefact — it is a property of the material, and it was the first thing a
   human eye reported. The interior bed joint now moves per tile row: **1 course height → 5**,
   lattice 0.378 → 0.273. New instrument `banding`, with its plant.
2. **"It is the same shape every time, which converts it from irregularity into a motif."** The
   head-joint wander was seeded per tile index, so every tile sharing four families drew the
   identical jog everywhere on the map. That is §8.3.1 in its own words — a wander is an
   *incident*, a tile is a *parent*, and there is no amplitude of it that is safe. Head joints now
   run true; the irregularity comes only from world-addressed things that cannot repeat on the
   grid.
3. **"No wear lane, no scuff, no stain, nothing that says traffic went one way."** The channel was
   there — 20 cells — and three rounds of seats have failed to see it. Wear pushed to its
   subtractive limit: grain kept 0.38 → 0.08, spread 0.45 → 0.20, plus a new arris pass.

---

## 7. On the record for ruling

### (a) The corner theorem constrains the ART, permanently, and should be written down

Runtime K is bought with a geometric constraint that no later floor family can escape: **no stone
may span a horizontal tile boundary**, therefore a joint runs along every one, therefore the floor
is coursed at a pitch dividing the tile — for ever, in every region. The course *rhythm* can be
varied (5 heights, per row) and the boundary line can be made indistinguishable from the mid-tile
line (density and value both 1.00), but **the coursing itself is not a style choice**. A future
region wanting crazy paving, cobbles, or any bond without continuous horizontal joints cannot have
runtime stone addressing, and would pay for it in the value domain instead.

This is offered as a candidate clause rather than assumed.

### (b) §8.2.1's "signals by absence" has a floor, and it has now been located

Absence is bounded: subtract enough and there is nothing left to subtract. Three seat rounds
missed the channel at grain 0.38 / spread 0.45. It now measures 0.350 / 0.578 / 0.775 against the
same stones unpolished — most of what there is to take. **If a seat still cannot find it, absence
alone cannot carry the channel and §8.2.1 needs a ruling**, because the alternative the clause
forbids (brightness) is the only lever left.

### (c) The cull axis is §8.1 damage and repair, which the FLOOR FAMILY cannot supply

*"No cracks. Not one. Across ~140 visible blocks."* — while the overlay system reported
`drawn(grit=45 event=44 occlusion=64)` in the same capture. §8.3 puts incident in the **overlay**,
not the tile, and correctly so: incident baked into a parent is the motif trap. So the family
cannot answer this cull by itself.

**The gap is measurable, and it is not a matter of taste.** The same scene captured with and
without the overlay system, differenced over the lit ground:

| | |
|---|---:|
| pixels the overlays change at all | 48.72% |
| changed by **≥ 1 ladder step** (13.23) | **7.21%** |
| changed by ≥ 2 ladder steps | 1.09% |
| mean delta where changed | 8.18 luminance — *below one rung* |
| connected marks of ≥ 1 step | 127 |
| **median mark size** | **4 px** |
| marks larger than 20 px | 26 |

So the incident is overwhelmingly **sub-rung noise at a median of four pixels** — at the review
build's 2× display, a two-by-two speck. That is not a crack; it is the "pepper" an earlier seat
named (*"~1,250 single-art-pixel dark dots spread evenly over the entire floor... at phone size
the floor reads as static before it reads as stone"*). A system emitting 127 marks of which 101
are smaller than a fingernail clipping is not depicting four centuries of use, and no amount of
work on the FLOOR FAMILY will change that number.

Named here rather than absorbed: this is the overlay system's finding, not the family's, and it
is the live half of the cull the family cannot answer.

---

## 8. State

- `K` — **RULED RUNTIME**, on 0 unaddressable stones, re-measured after every geometry change.
- Rulings (1) and (2) — **discharged by construction**; the value step is 0.000 before grain and
  0.59 after it.
- Preconditions 1–4 — carried forward from session two, precondition 4 closed at commit
  `416f105c`.
- Round 7 seats — running on `scene_ashlar_r7.png` (sha `69008da5…`) and
  `scene_ashlar_plant_r7.png` (sha `aa878a77…`).
- Device — `TIER1_ASHLAR` knob exists and the family has **not** yet been verified on the handset.
  Nothing here has been to the device, and nothing here is claimed to have passed a gate.

**A round's evidence must not move under it.** Round 3 was left running while the family was
rebuilt and its capture overwritten in place, so the seats still queued would have judged a
different build than the first seat saw — four opinions of one floor, and nothing would have
failed. That round is stopped and kept at its first seat only. `run_seats` now hashes every
capture before the first seat, re-checks before each one after it, and refuses on a change; and
captures are round-scoped so a later round cannot need to overwrite an earlier round's evidence
at all. A rule that removes the hazard beats a check that catches it.
