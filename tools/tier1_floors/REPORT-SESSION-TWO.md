# FLOOR SESSION TWO — edge-matching, and the lattice underneath the lattice

**Status: FINDING REPORT, not a gate handoff.** §1.1.4's trigger: the blind critic culls the
family, so nothing goes to the landing gate (§1.1.1). What follows is what was built, what was
measured, and the one defect that is named and only half-closed.

---

## 0. THE HEADLINE

**Session one's terminal finding is answered.** Joints now enclose:

| | session one | session two |
|---|---:|---:|
| largest single region, share of floor | **99.1%** | **3.9%** |
| enclosed regions | 2 of meaningful size | **147** — median 177 px, 77 ≥ 64 px |
| crossing offsets, distinct per orientation | n/a | 3–4, modal share **0.375** (≈ 1/3) |

**And the family still fails, on a lattice nobody had looked for.** A blind seat, given the
edge-matched build:

> **CULL:** *"Hard 64px tile-tint squares cut straight across the crack network; the grid reads
> before the floor does."*
> *"axis-aligned value blocks on an exact 64-pixel lattice … the worst at x=503, y=209–239: a
> luminance step of exactly −25 held dead constant for 31 consecutive rows."*

**Edge matching fixed WHERE the joints cross. It said nothing about what the stone either side of
the crossing is worth** — and a stone is not one stone if its two halves are different colours.
Measured across an assembled field: value steps at cell boundaries averaged **8.72** against
**1.17** inside a tile, **7.4×**, max 39.9.

Half-closed, and the residue is carried as a named limitation rather than a rounding error — §4.

---

## 1. PRECONDITIONS

| # | state | evidence |
|---|---|---|
| 1 · PositionHash proven | **MET** | `controls/CENSUS-CONTROL.json` |
| 2 · Floor legibility guard | **MET** | `controls/LEGIBILITY-CONTROL.json`, `LEGIBILITY-SWEEP.json` |
| 3 · Rig flags required | **MET** | last two default fallbacks removed |
| 4 · Device read-back | **BLOCKED** | the SE is locked; `devicectl` refuses the launch |

### 1.1 The census, and two defects in it that its own control found

`FloorVariantCensus` reads the texture of every sprite the renderer placed — not the theme, not
the hash — so it censuses the end of the pipeline and cannot agree with a broken picker by sharing
its logic. On the current family: **50 distinct across 74 cells**, against an arithmetic
expectation of 51.8 for a 96-tile pool.

The control restores session one's linear hash verbatim and requires the census to notice:

```
fixed    cells=74 distinct=50  step_top2 row=0.086 col=0.086 diag=0.106 anti=0.087
linear   cells=74 distinct=57  step_top2 row=1.000 col=1.000 diag=1.000 anti=1.000
```

**It failed twice first, and both failures were real defects in the instrument.**

- **It measured `repeat@3`** — the period a linear hash produces on a *24*-id pool. The pool is
  now 96, where the same hash has period 12, so the planted defect measured **0.000** and the
  census would have certified it fixed. *The defect is linearity; the period is a symptom whose
  value depends on N.*
- **Replaced with step-difference constancy, it indexed the OBSERVED set** rather than the true
  ids. `PickVariant` computes `hash % N` over the full list, so a constant difference in id space
  is not constant once compressed onto the ~50 ids that happened to appear. Measured 0.43 on the
  plant instead of 1.00.

Now it reads the real id from the filename and asks what fraction of steps fall in the **two**
commonest difference buckets — under `hash % N` a linear hash gives exactly two, `d` and `d−N`,
so it saturates at any pool size and the census never needs to know N.

### 1.2 The legibility guard, and two defects in *it*

`ProbeJunctionLuminance` guards a junction; a floor scene has none, so it reported `junction=NO`,
no-opped, and floor captures had **no legibility check of any kind**. The scene now declares the
points it must be able to show and the points it must leave dark, and the probe refuses the
capture if any fails.

**Both directions, because the second is the one that is easy to omit.** §6.2.1 rules the pass
*"not a licence to flood the Boundary with light"* — a guard that only asked *is it bright enough*
is blind to a drowned arc by construction.

Control **9/9**, each arm failing for the right reason:

| arm | verdict | fails on | image written |
|---|---|---|---|
| ratified rig | PASS | — | yes |
| radius 4.0 | FAIL | **lit** points; dark still pass | **no** |
| ambient 2.0 | FAIL | **dark** points; lit still pass | **no** |

Bounds derived by sweep, not chosen: lit ≥ 0.12, dark ≤ 0.10, against a measured ambient floor of
**0.058**.

> ⚠ **Twice, the guard measured the interface.** The first dark points landed at x = −9 and
> y = 1371 on a 750×1334 capture; `PatchLuminance` clips, so they read the HUD and the letterbox —
> 0.059 and 0.160, one "dark" point brighter than a "lit" one, which is what exposed it. Image
> bounds alone were not enough: the replacements sat inside the image and inside the HUD's button
> row, reading 0.796 and getting *darker* as ambient rose. The probe now requires points inside
> `UILayer/ViewportOverlay` — the game's own dungeon view, measured at (0,90)..(750,1001).

> ⚠ **A measurement about Ruling 56, reported and not acted on.** At the ratified rig a point at
> the nominal 5.0-tile radius reads **0.060** against an ambient floor of **0.058** —
> indistinguishable from ground declared dark. **The lamp's delivered reach is about four tiles.**
> The rig was ratified on the device by eye and §13.2 makes the eye final; a luminance ratio has
> never been calibrated against *legible to a person holding a phone in a dark room*. The narrow
> claim the measurement supports is that **nominal radius and delivered reach are different
> quantities**, which scene design needs to know. The radius-edge point was withdrawn from the
> declared set rather than asserted either way.

> ⚠ **Room B is never in a static capture.** The dungeon view spans about map rows 0–12 at this
> camera; room B is at y16–18. It exists for the walked device review, and no still is evidence
> about it.

### 1.3 Rig flags — the last fallbacks removed

`ReviewBuildMarker` defaulted `falloff`/`ambientLevel` to the identity so pre-ruling markers would
still boot, and `ReviewLighting.Params` carried C# defaults. Both are gone. A pre-ruling marker
now fails loudly, and the compiler requires all six values at every construction site.

*I wrote that fallback in session one, in the same session whose commit message warned that a
ratified value which can be silently defaulted is one that can silently drift.*

---

## 2. THE EDGE-MATCHED FAMILY

**The edge owns its family, not the tile** — which is what removes the solver. Every boundary is
assigned a family by hashing its own coordinates, so two neighbours reading the same boundary
agree by construction:

```
N = H(x, y)     S = H(x, y+1)     W = V(x, y)     E = V(x+1, y)
```

No scan order, no dead ends, deterministic from the map alone. The cost is a tile per combination
— 3⁴ = **81**, plus 81 channel renderings — which is why ≥3 families per orientation is
affordable rather than aspirational.

**The channel is the same bond drawn worn**: fewer joints, shallower, tighter grain. It signals by
**absence**, never brightness — §6.3 at design time, which session one learned when three rounds
of seats read its value lift as the torch. Same edge families, so a channel cell still matches its
ordinary neighbours and the enclosure survives the transition.

> ⚠ **The hash exists twice**, in the Python that drew the tiles and the C# that lays them — the
> copy-that-drifts hazard this project has been bitten by. Tolerated only because it is
> **enforced**: the manifest carries a 128-sample cross-check vector and the engine refuses to lay
> the floor unless it reproduces every value. Visible in every capture log as `cross_check=128/OK`.

> ⚠ **The first assembled field measured 100% single region — worse than session one.** The joint
> walk sampled once per pixel of the longer axis, so wobble left gaps and the joints rendered
> **dashed**. The network looked right and leaked at every hole. Oversampled 4×. *A joint with
> holes in it encloses nothing*, which is session one's finding arriving through the drawing
> rather than through the tiling.

**Anchor constant, landed in §6.5:** the family's median luminance, as authored and unlit, is
**114.5** — §6.5's 1.00 for the Boundary. Measured on the tiles rather than a capture, so no rig
is folded into it. `WALL-RECIPE.md`'s face ÷ top ≈ 0.35 is marked stale.

---

## 3. THE SEATS — round 6, valid, and it FAILS

Plant caught (*moss, overgrown*): **"Reads as outdoor mud and grass, not a made, used,
administered underworld floor."** So the round stands.

**What the edge matching bought, in the seat's own words:**

> **Q5:** *"**Made.** The crack network is authored across the whole room, not tiled. I checked
> every 64px cell against every other and the median correlation is 0.035; the polygons cross cell
> boundaries freely, the junction placement is irregular, and no cell-to-cell pattern emerges.
> **That is real work and it is the best thing on this floor.**"*

**What it culled:**

> **CULL:** *"Hard 64px tile-tint squares cut straight across the crack network; the grid reads
> before the floor does."*
> **Q6:** *"Merely competent. The crack network is good work by itself. But it is carrying a tint
> layer that contradicts it."*

**Q1 is still wrong too** — *"dried mud or clay, a shrunk cracked pan. Not stone, not masonry"* —
which session one had briefly fixed with the ashlar bond and this construction has lost again. The
Voronoi-like polygon network reads as desiccation whatever its enclosure.

### 3.1 Two wrong diagnoses before the right one, recorded

The seat's measurement reproduced exactly: **−25.9 at x=502→503**, a cell boundary. I then guessed
twice and was wrong twice:

1. **Fog of war.** `UpdateVisibility` dims explored-but-unseen cells by 0.4 at whole-cell
   granularity — a real per-cell lattice. But the review scene already calls `RevealAll()`, so it
   was never active. *Checked, not assumed, and the hypothesis died.*
2. **The channel wash.** Session one's alpha-lift channel overlay was still drawing on top of the
   new worn tiles — genuinely wrong, genuinely a per-cell flat lift, and genuinely contrary to
   this session's refusal list. Suppressed (`channel=0` in the log). **The seam did not move.**

The actual cause, found by measuring instead: **each tile draws its regions with independent
random values, so a stone spanning a boundary gets two.** Unlit, channel and base tiles differ by
only −0.32, so the art was never the source of a 26-point step; the source was that two adjacent
tiles never agreed what the shared stone was worth.

---

## 4. THE FIX, AND WHAT IT DOES NOT DO

Every boundary now carries a value derived from **its own family** — data both neighbours already
share — and each tile's material is blended toward that value as it approaches the edge. At the
seam the blend is complete, so both tiles compute the identical value.

| | boundary steps | interior | ratio |
|---|---:|---:|---:|
| before | mean **8.72**, max 39.9 | 1.17 | **7.44×** |
| after | mean **3.99**, max 26.3 | 1.35 | **2.95×** |

**It is not closed.** A 2.95× residue remains, and it is reported rather than rounded away.

**An alternative was tried and measured worse**, which is why the residue stands rather than being
tuned at: normalising only the tile's *interior* — to leave the edge band exactly as the shared
value set it — gave boundary steps **4.93** and a per-tile mean spread of **8.40**, past the 6.4 a
seat culled in session one as *"the grid draws itself onto the ground"*. Two lattices are not
better than one.

**The residue's source is named:** the whole-tile mean normalisation adds a per-tile constant
after the blend. Removing it re-opens session one's defect. **Closing both at once needs the
normalisation to be unnecessary — a construction whose mean is stable by design rather than by
correction — and that is the next session's problem, not a number to nudge.**

---

## 5. WHAT IS OWED

- **The device read-back.** Precondition 4 is unmet: the handset is locked and `devicectl` refuses
  the launch. One command with the phone unlocked: `tools/tier0_harness/verify_on_device.sh`.
- **#153 merged three commits early**, at `48699b3b`. **Main still carries the pre-ruling rig**
  (`radius_tiles: 5.5`, `status: UNDERIVED`), no `verify_on_device.sh`, and no Ruling 56 in the
  bible. This branch carries them; anyone branching from main today gets the old rig.
- **Q1 regressed to "mud".** The ashlar bond that fixed the material read in session one is not
  in this construction. Edge matching and angular slab shapes are not in conflict — the crossings
  can be joined by straight segments rather than wandering ones — but that was not attempted here.
- **The boundary-value residue**, §4.
- **The channel edge is still cell-quantised.** A shoulder rendering (a third worn level) would
  widen the transition to two cells; not built.
- **No generations were spent.** The 80-generation budget is untouched: the material came from
  session one's measured donors and this session's work was architectural. BitForge stayed frozen.

---

## 6. EVIDENCE

| what | where |
|---|---|
| census control (plant = the shipped linear hash) | `controls/CENSUS-CONTROL.json` |
| legibility control, 9/9 both axes | `controls/LEGIBILITY-CONTROL.json` |
| legibility bound derivation | `controls/LEGIBILITY-SWEEP.json` |
| enclosure + crossing variance | `evidence/WANG-FIELD.json`, `evidence/wang_*.png` |
| the family | `src/Presentation/assets/tier1_wang/MANIFEST.json` |
| in-scene capture, lit, rig flags echoed | `evidence/scene_wang.png` + `.log` |
| seat transcripts, round 6, paired with the build they gated | `evidence/seats/r6_*`, `SEATS-r6.json` |
| the clarified law | `docs/ART-BIBLE-v0.md` §8.3.2 |
| the anchor constant | `docs/ART-BIBLE-v0.md` §6.5 |
