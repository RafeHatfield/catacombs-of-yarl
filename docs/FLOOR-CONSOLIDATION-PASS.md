# The floor consolidation pass

**Ruled:** the floor lane's solo gate is closed. The floor is judged only in the combined scene.
The floor-only items extracted from the five stall reports are applied here as **one pass, no
critic gate**, feeding the combined build. Everything else in those reports — walls, caps, wall
thickness, cast shadow, props, void legibility — is routed elsewhere.

This is not a round. There is no seat, no plant declared in advance, and no verdict. What it owes
instead is that every change is mirrored across all three painters and every existing check is
still green — plus an honest account of the one that is not.

---

## What was applied

### 1. The floor steps, it does not ramp

Two of the critic's items were the same defect wearing two descriptions:

> the slab edges ramp over two to three pixels and adjacent blocks merge until the joint vanishes

> large soft value-blobs sit across the floor that follow no geometry … they read as airbrush,
> not as light or as material

Both were **continuous terms on a quantised surface**. The chip pass subtracted a *fraction* of a
rung from the pixels beside an open joint; the lane dish subtracted a smooth radial. Neither
landed on the ladder, so both manufactured the intermediate values §4.3 exists to forbid — at
paint time, after every other pass had been careful not to.

The fix is not removal. It is landing each on a rung:

- `CHIP_TAKES_JOINT` — a chipped arris **is joint**. The stone that broke away is gone, so the
  pixel takes the adjacent joint's own value instead of a blend on the way to one.
- `DISH_QUANTISE` — the lane dish steps in whole rungs. Depth, not airbrush.

### 2. A crack has a section

> a uniform 1px black stroke has no depth

`CRACK_LIP = 0.55` rungs. One pixel of stone beside the channel is a **lip** — the broken edge,
lighter than the flat face it came from, on the side the crack's own world position chooses so it
stays consistent along a run instead of alternating pixel to pixel. It is applied **before** the
quantise, like everything else that moves a stone's value.

### 3. The cracks register the joints they cross

> a crack that crosses six slabs in one smooth curve without registering a single joint reads as a
> line drawn over the floor, not damage in it. Break them at joints, or run them along one.

**True deflection is not available, and the reason is a standing constraint rather than a
shortcut.** A crack must be a pure function of world position — that is what makes every tile it
crosses compute the identical line, the same discipline the corner theorem imposes on the stones.
The bond is *not* a world function: a tile's course splits, drop pattern and stone origins come
from the atlas **variant** the map picks for that cell at runtime. A crack that deflected on the
real joints would be a different crack depending on which tile drew it, and the disagreement would
land exactly on the tile boundaries — §8.3.1's grid tell, reintroduced by the fix for a different
defect.

What *is* available from purely local information, in every painter: `CRACK_SPALL`. Where the
crack passes through a joint, the arrises either side of the crossing break away — wide at the
bond, narrow across the slab, which is how a fracture actually crosses one. Computed from the
original crack set (so it is order-free) and from the joint mask (which both tiles either side of
a boundary already agree about by edge-family construction).

### 4. The scribble marks cluster

> distributed as an even noise field across the whole floor. Place them deliberately in clusters
> where a hand would have made them, and leave stretches of floor with none.

Bare-vs-marked was a per-stone coin flip, which is an even field *by construction* however low the
rate. The coin is now biased by a coarse world field (`MARK_CLUSTER_PERIOD = 5` tiles,
`MARK_CLUSTER_SWING = 0.30`), so working ran in one part of a room and not another — and the field
is world-keyed, so a cluster crosses tile boundaries the way a hand would.

---

## What was tested for and not found

**The one-pixel phase step.** The critic reported a misaligned block whose "pattern is one pixel
out of phase with the floor around it". A pattern continuous in world space cannot step at a tile
edge; one computed per tile can. Every tile boundary in a composed 10×10 field was compared
against its neighbour directly and shifted by one pixel:

    0 of 18 tile boundaries match their neighbour better when shifted a pixel.

There is no phase step in the field. If the critic saw one it is in the **renderer** — a sprite
placed a pixel off, not a pattern computed a pixel off — which makes it a combined-scene item, not
a floor-family one.

---

## The check that is not green, and why the threshold was not moved

`no_erosion → erosion_read` is **SILENT**, and this pass did not cause it.

The plant nulls form-as-erosion entirely and demands two things of the floor: it must lose its
directional grain, and it must lose its ground-down look (face spread ≥ 1.20× the live floor's).

| | grain, live → nulled | face spread ratio |
|---|---|---|
| HEAD's own code, measured | 0.84 → 0.01 | **1.162** |
| this pass, before the instrument narrowing | 1.17 → −0.01 | 1.057 |
| this pass, crown population | 1.17 → −0.01 | **1.143** |

Two separate facts sit in that table.

**It was already silent at HEAD** (1.162 against a 1.20 bar). The directional half of the plant is
untouched and total — the grain goes to zero. The *spread* half is diluted because the crown now
carries several erosion-independent value layers the 1.20 threshold predates: the lane dish, the
margin grit, the tool marks, each with plants of their own.

**The chip ruling made it worse, and that part is an instrument bug this pass fixed.** If a chipped
arris *is* joint — this pass's own ruling — then the instrument cannot go on counting it as face.
`erosion_read` now measures the **crown**: stone that is neither joint, crack, nor dressed. The
exclusion is arm-symmetric (the same 10,313 pixels in both arms), so it narrows what is measured
without tilting the comparison, and it recovers 1.057 → 1.143.

**The 1.20 threshold has not been touched.** Moving a bar to clear one's own change is the failure
this process is built to catch, and the gap is a finding for the human gate: *the flattening
lever's spread signal no longer clears a bar written before the floor had this many layers.*
Restoring `DEFORM_FLATTEN` to its old strength would clear it and would re-open the value-blob
defect the critic culled — which is why it was cut.

---

## Verification

- shipped path **IDENTICAL on all four arms** (direct, trodden channel, traffic spine, declared
  route); the route arm is not vacuous — it changes 43.5% of the floor
- `ATLAS-PATH` plant **CAUGHT** (one altered ladder index, 1 pixel)
- engine reproduces the composer's finished pixels: **`paint_check=96/OK`**, with
  `edge_check=128/OK stone_check=144/OK laid=74 missing=0 lines=1 mouths=13 polished=74`
- `UNADDRESSABLE 0`, `VERDICT: K is RUNTIME`
- plants **14 of 15 fire**; `no_erosion` silent as above, run completes 15 of 15
- fast suite **2518 passed / 0 failed**

Three bugs the checks caught during the pass, recorded because each was silent by nature:

1. the engine's crack-lip pass was written *inside* the per-pixel loop, so it applied the lip once
   per stone pixel rather than once per tile — caught by `paint_check` disagreeing by one rung;
2. the mirror applied the lip *after* the quantise, where the reference painter applies it before —
   `quantise(x) + w` is not `quantise(x + w)`, 553 pixels;
3. `crack_spall` indexed neighbours without a bounds check — a negative index wraps silently in
   numpy and a positive one raises, and the first version did both on the same line.
