# The five stall reports, routed

> **ACCEPTED (Rafe, 2026-09-03).** The routing stands, and **both register refusals are upheld**:
> the four-sided joint is the culled ring, and snapping value boundaries to the tile grid is
> staged wear. Neither is to be re-attempted on a critic note alone.

The five-round park fired on a **scene** defect, not a floor defect: every round's fatal items
were walls, wall-caps, props and filled void. This is the disposition of every item in the five
flip lists. Nothing is dropped; each line names where it goes.

---

## Floor lane — applied

| item | round | where |
|---|---|---|
| slab edges ramp over 2–3px, adjacent blocks merge | 4 | `CHIP_TAKES_JOINT` |
| large soft value-blobs, airbrush not material | 1, 5 | `DISH_QUANTISE` |
| cracks pure black inside the lamp pool | 4 | already landed — `e84db6ad` |
| cracks have no section | 4 | `CRACK_LIP` |
| cracks cross joints without registering them | 2, 4 | `CRACK_SPALL` (deflection is unavailable — see below) |
| scribble marks are an even noise field | 1 | `MARK_CLUSTER_*` |
| joint structure dissolved / joints washed out | 1, 5 | already landed — `SHELTER_LIFT_RUNGS` raised |
| joint depth varies along a single run | 5 | already landed — `CRACK_DEPTH_VARY`, shelter distribution |

See `docs/FLOOR-CONSOLIDATION-PASS.md`.

## Floor lane — tested for and not reproducible

**"The misaligned block … its pattern is one pixel out of phase with the floor around it"**
(round 3). Zero of eighteen tile boundaries in a composed field match their neighbour better when
shifted a pixel. There is no phase step in the floor's field; if one was on screen it is in the
**renderer** — a sprite placed a pixel off. Routed to the combined-scene lane.

## Floor lane — refused, with the law that refuses it

**"Restore a consistent dark joint on all four sides of every slab"** (round 5). This is the
ring — an outline around every stone — culled by ruling and by §8.3.1. A joint that is present and
equal on all four sides of every stone is the lattice the whole family is built not to draw. The
legitimate half of the note (joints must be legible, and must vary along a run) is applied above.

**"Snap them to the tile grid"** (round 5, of the soft blobs). The blobs are quantised to the
ladder, which is the half of the note that is right. They are **not** snapped to the tile grid:
any value boundary coinciding with a tile edge is staged wear, by the gate's own ruling.

---

## Wall session

- flat magenta wall tiles; per-tile corner swatch; saturation (rounds 1, 2 — these three rounds
  captured without the wall flags; the placeholders were read as the floor's lighting)
- delete the debug cell layer and draw the wall geometry it stood in for (round 2)
- **wall tiles need a top surface**: a lit cap edge on the sides facing the figure, a dark body,
  so the wall reads as having thickness (rounds 3, 4, 5)
- **cast shadow** from the wall onto the floor on the far side from the lamp (round 4)
- the passage below the figure has no sides (round 4)
- the boundary at the floor's edge is a cut into black, not a wall; it needs a top surface
  separated in value from the lit floor and a **contact line at its base** (round 5)
- hard-clipped floor boundary at y≈199 and x≈310 (rounds 1, 2) — the same boundary, same cause

## Tier-2 props pass

- the barrels' top edge against the floor's top edge (round 1, fatal)
- **the four hundred years of repair are not on screen**: driven pins in a cracked slab, a rope
  lashing, a hide patch over a hole, salvaged timber pinned across a gap. The lit area is empty
  floor (rounds 3, 4 — raised twice)

## Void / ground-material lane

- the mottled brown region has no structure at any scale and no relationship to the slab grid;
  give it a legible material — rubble at a stated size, packed earth with direction — or make it
  stone (round 4)
- the bottom band is a single mustard hue with uniform per-pixel noise, reads as static; replace
  with drawn rubble: distinct fragments with their own light and shadow sides, sized in a range,
  grouped into open and dense patches (round 5)
- the horizontal seam where the slab floor butts the mottled region needs a threshold, a lip, or
  scattered debris crossing the line so the two surfaces interlock (round 4)
- over half the canvas carries no information — raise the ambient floor so far architecture is
  faintly legible, or tighten the frame (round 4)

## Scene / level-generation

- isolated slabs floating in the void with nothing joining them to the room: connect them to
  walkable geometry or cull them from the render (round 5)
- no transition tiles anywhere; the water is a rectangle stopping at four hard 90° corners
  (round 5)
- differentiate the corridor from the chamber by **material**, not brightness: narrower stones, a
  worn centre track, a threshold line where the two floors meet (round 3) — needs the scene to
  declare a corridor/chamber distinction the floor can key off

## Sprite / rig

- the brightest region sits three-quarters of a tile *below* the figure, which reads as light from
  underneath — move it onto the sprite (round 1)
- mismatched sprite resolution; no light source on the figure; no contact shadow (rounds 1, 2)
