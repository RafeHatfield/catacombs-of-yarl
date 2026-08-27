# `/create-tiles-pro` — THE COLUMNS

Every row is one real call or one real refusal against our own account. Nothing here is a
verdict from documentation. Where a schema line and a measurement disagree, **the measurement
is the row and the schema line is the footnote.**

Legend: **[API]** measured here · **[SCHEMA]** read from the live OpenAPI document (free) ·
**[PRIOR]** measured on this account by an earlier session, cited with its evidence path.

Evidence: `columns/`, `yield/`, `levers/`, `arm3/` — ledgers, payloads, and every tile.

---

## 1 — CANVAS AND TILE SIZE

### `tile_size` is not the canvas, and it is not the cell

| `tile_size` | emitted sprite canvas | floor cell | `stack_stride_px` | cell ratio |
|---:|---|---|---:|---:|
| 17 | 25 × 43 | 17 × 13 | 12 | 0.765 |
| 20 | 32 × 54 | 20 × 15 | 15 | 0.750 |
| 32 | 52 × 87 | **32 × 24** | 24 | 0.750 |
| 32, `tile_view_angle: 90` | 52 × 116 | **32 × 32** | 32 | **1.000** |

**The floor cell is `tile_size` wide by 0.75 × `tile_size` tall by default** — a 4:3 cell, not
the square one bible §3 asks for. The sprite canvas is much larger than either, because it
carries the wall storeys above the cell.

⭐ **A square cell IS available, and the parameter that buys it is not the one the repo ruled
out.** `tile_view` is measured **[PRIOR]** silently ignored on building kits and fully charged
(`PIXELLAB-INTEGRATION-AUDIT` §9.3, which concluded *"Do not plan around `tile_view` here"*).
`tile_view_angle` is a different parameter — continuous degrees, documented to override
`tile_view` — and it is **[API] fully live**: at 90 it moves the canvas, the floor bounding
box, the cell, the stride, and echoes itself back as `view_angle: 90.0` in the returned
grammar. §9.3's conclusion is correct about `tile_view` and does not transfer to
`tile_view_angle`. ⚠ **The cost of the square cell is the top surface** — 90 is straight
top-down, zero ground pitch, and the wall pieces come back with no cap band at all. §3 asks for
both halves and this parameter trades one for the other. `building_wall_angle` is documented to
decouple them; see `arm3/`.

### Enforced ranges — all free, all named by the server

| Probe | Result | Verbatim |
|---|---|---|
| `tile_size: 15` | REFUSED, free | `Input should be greater than or equal to 16` |
| `tile_size: 129` | REFUSED, free | `Input should be less than or equal to 128` |
| `tile_size: 17` | ⚠ **ACCEPTED, billed 20** | 80 tiles, canvas 25×43 |
| `tile_size: 20` | ⚠ **ACCEPTED, billed 20** | 80 tiles, canvas 32×54 |
| `building_wall_tiles: 4` / `: 0` | REFUSED, free | `less than or equal to 3` / `greater than or equal to 1` |
| `tile_feature: roads`, `tile_size: 24` | REFUSED, free | `Roads need tile_size 32-32 for square_topdown.` |
| `building_layout: "swatches"` | REFUSED, free | `Input should be 'grid' or 'materials'` |
| `outline_mode: "none"` | REFUSED, free | `Input should be 'outline' or 'segmentation'` |
| `building_wall_angle: 100` | REFUSED, free | `less than or equal to 90` |
| `tile_depth_ratio: 2.0` | REFUSED, free | `less than or equal to 1` |
| `tile_view_angle: 120` | REFUSED, free | `less than or equal to 90` |
| `building_wall_description` × 501 chars | REFUSED, free | `String should have at most 500 characters` |

**There is no hard 32 floor and no coarse per-shape range for square_topdown building kits.**
`tile_size: 17` — odd, and as far from a power of two as this endpoint allows — returned a
complete 80-tile kit with a full grammar. The schema's *"connectable sets have tighter
per-shape ranges"* is real but it is about **roads**, which name their own range in the refusal.

⚠ **Two of the fourteen probes were designed to be free and were not.** They were billed 20
generations each, they are on disk, and they are read as canvas-column data rather than
discarded. Recorded as a method error: *a probe is only free if the server refuses it, and
which values a server refuses is exactly what the probe is asking.*

---

## 2 — CONDITIONING

> **[API] `style_images` cannot be used with a building kit at all.** Free refusal, verbatim:
>
> ```
> Connectable features (roads/tileset/building) cannot be combined with style tiles
> — remove style_images or set tile_feature to null.
> ```

This is the column's whole answer and it is architectural, not a tuning limit. **The kit and
the style reference are mutually exclusive on this endpoint.**

⚠ **It closes a re-plan option the wall gauntlet left open.** That report named
*"conditioning-first once a corpus exists"* as the strongest remaining path, on the strength of
a 12-of-12 material-DNA propagation measured on BitForge. That path is real — **on BitForge**,
which is measured unable to produce architecture. It is unavailable on the endpoint that can.
**The two capabilities do not sit on the same surface**, and no amount of corpus changes that.

Also measured:

- ⚠ **`style_images: []` is ACCEPTED and billed 20 generations.** An empty reference list is
  neither refused nor honoured. That is the **third** silent billed no-op measured on this
  platform, after `create_character_state`'s structural edits and `tile_view` on building kits
  (§9.1, §9.3). The pattern is now firm enough to state as a rule: **parameters that do not
  apply are silently accepted and fully charged, with no `ignored_parameters` field and no
  warning.**
- **[SCHEMA]** `TilesProStyleImage` is `{base64, width, height}` — width and height **required**,
  and no `type` or `format` field. It is **not** `Base64Image`, which every other endpoint on
  this platform takes. Carrying the neighbour's wire shape here is the enum mistake of §8.9 in a
  new costume, and it is banked so nobody rediscovers it.
- **[SCHEMA]** When style images are supplied at all, *"tile_type, tile_size, tile_view,
  tile_view_angle and tile_depth_ratio are ignored — the style tiles define the shape."* Moot
  for building kits, which cannot take them.

---

## 3 — LEVERS: PRESENCE, AND MEASURABILITY

### ⚠ The pixel channel is NO INSTRUMENT on this endpoint

Four byte-identical calls at seed 1337. Every visible pixel differs between every pair: each
tile's raw diff equals its own opaque fraction, so **normalised against the visible area the
noise floor is 1.0000.** There is no headroom, and a lever pixdiff read against that floor
would repeat the §6.4 audit's own first mistake, where MCP `pro` measured its lever at 1.0000
against a noise floor of 1.0000 and the honest output was `NO INSTRUMENT`.

The pixdiff is still computed and still ledgered, labelled `pixdiff_BLIND`, and it is never a
verdict.

### The instrument that does have headroom

The **structural readout** — canvas, floor bounding box, floor cell, `stack_stride_px`,
`wall_tiles`, `arity`, `rule_type`, `view_angle`, the `painted` list, the part table. Grammar
and geometry; never pixels.

Its control was free and is the hardest available: **10 of 10 fields are identical across five
kits whose every visible pixel differs** (`columns/structural_readout.json`). A field that
moves under a lever has moved something the generative noise cannot fake.

| Lever | Verdict | What moved |
|---|---|---|
| `building_layout: "grid"` | **READOUT MOVED** | `roof`, `slopes`, `slopes_east` gone from the grammar; **80 tiles → 58**; `painted` list byte-identical |
| `tile_view_angle: 90` | **READOUT MOVED** | canvas 52×87 → 52×116; floor cell 32×24 → **32×32**; stride 24 → 32; `view_angle` null → **90.0** |
| `style_images` × 2 | **REFUSED, free** | see column 2 |
| `outline_mode: "segmentation"` | **NOT SPENT** | guards §12.1, and no baseline kit carries a dark ring — the lever protects a defect that is not present. A gap, named. |
| `building_wall_angle` alone | **NOT SPENT** | tested only in combination, in `arm3/`. Its solo effect is unmeasured. |

⭐ **`building_layout: "grid"` is the roof suppressor**, and that answers an open question.
`PIXELLAB-INTEGRATION-AUDIT` §8.7 recorded *"A quarter of it is roof — 20 of 80 tiles are gable
roof, useless for a top-down dungeon interior, and we paid for them. No parameter appears to
suppress them."* One does. **It does not reduce the price** — still 20 generations — so it buys
cleanliness, not value.

⚠ **What `building_layout: "grid"` does NOT do, despite its description.** The schema says grid
*"paints each shaped piece individually (richer)"* against materials' *"flat swatches"*. On
`square_topdown` the returned `painted` list is **byte-identical** under both: the same 20
indices. Whatever grid changes here, it is not which pieces get painted.

⚠ **`READOUT UNMOVED` would not prove a silent no-op.** A lever could change every pixel and no
field, and on this endpoint that case is **unmeasurable**, because the pixel channel has no
headroom. The honest word is *unmeasurable*, not *unchanged*.

⚠ **HONOURED / MOVED is not an aesthetic claim** (bible §13.4). It answers one mechanical
question — did the parameter do anything — never whether it moved the art in the intended
direction. That is an eye question and it belongs to the human gate.

---

## 4 — DETERMINISM

> **[API] `/create-tiles-pro` is NOT deterministic under `seed`, and this contradicts a prior
> [API] claim in this repo.**

Four calls, byte-identical payloads, `seed: 1337`, three minutes apart:

| pair | mean raw pixdiff | tiles moved |
|---|---:|---|
| A0/A1 | 0.304189 | 80 of 80 |
| A0/A2, A0/A3, A1/A2, A1/A3, A2/A3 | 0.307935 | 80 of 80 |

Each tile's figure equals that tile's opaque fraction: **every visible pixel differs.**

**The seed does nothing measurable.** A0 against kit B — a *different* seed — is 0.307935,
indistinguishable from the same-seed pairs.

`PIXELLAB-INTEGRATION-AUDIT` §9.3 recorded the opposite as **[API]**: *"Same seed and same
effective parameters produced 80/80 pixel-identical tiles… Regeneration is reproducible."* Both
readings are on this account and I cannot reconcile them from here. Two candidate explanations,
neither verified, both stated rather than one chosen:

1. The endpoint changed between 2026-08-25 and 2026-08-26.
2. §9.3's pair was served from a cache — its two calls differed only in `tile_view`, which the
   same section proved the server ignores, so the two requests may have been the *same request*
   as far as the backend was concerned. That would make §9.3 a measurement of a cache, not of a
   seed.

**What IS reproducible is the geometry and the grammar** — all 10 structural fields, across all
five kits. So:

> **Geometry is re-derivable from a ledger row. Art is not.** The ledger must store the images,
> exactly as the §6.4 probe concluded for BitForge. A parameter row is not evidence here either.

⚠ **This reaches back.** Any plan that assumed a kit could be re-derived from its ledger row
instead of stored — §9.3 explicitly floated it — does not hold on this measurement.

---

## 5 — LATENCY AND COST

**20 generations per building-kit call. Invariant.** Measured across `tile_size` 17, 20 and 32,
`building_wall_tiles: 2`, `building_layout: grid`, and `tile_view_angle: 90` — every completed
call reported `usage: {generations: 20.0}`, including the one that returned 58 tiles instead of
80. **You pay for the kit, not for the tiles.**

| call | polls | wall clock to tiles-in-hand | tiles |
|---|---:|---:|---:|
| yield A0 / A1 / A2 / A3 / B | 13 / 13 / 12 / 14 / 12 | 128.8 / 131.0 / 119.4 / 139.9 / 118.9 s | 80 each |
| `building_layout: grid` | 20 | 204.4 s | 58 |
| `tile_view_angle: 90` | 13 | 129.1 s | 80 |
| the three constraint kits | 1 each | 0.7–0.8 s | 80 each |

The three at 0.7 s are not fast calls — they had completed during the phase that created them
and were fetched afterwards. **The honest figure is roughly two to three and a half minutes per
kit**, ~10 s per poll.

⚠ **`usage` is now null on the 202 and arrives on the completion GET.**
`PIXELLAB-INTEGRATION-AUDIT` §8.7 recorded the 202 reporting `usage` exactly. It does not now.
**The balance moves when the job completes, not when the call returns** — which is why the
constraints phase closed its bracket at delta 0.0 with three billed calls in flight. A cost
taken from a bracket that closes before the jobs do is not a measurement.

`GET /tiles-pro/{id}` returns **423** while generating, with
`{"detail":"Tiles are still being generated"}`. It is a retry signal, not a refusal, and it is
free. Confirmed **[API]** here, as §8.6 recorded.

---

## 6 — WHAT ONE KIT ACTUALLY CONTAINS

80 tiles for 20 generations is the headline. The content is thinner than the count.

- **20 of 80 tiles are individually `painted`.** The other 60 are composed from those swatches
  — `building_layout: "materials"`, the default for `square_topdown`.
- Of the 38 **wall** pieces (excluding floor, doors, stairs, slopes and the whole gable roof),
  **112 of 694 overlapping pairs are ≥90% identical**, three pairs are 100% identical over
  their shared opaque region, and `tile_13`/`tile_31` — a partition hub and a pillar — are the
  same 684 pixels.
- ⭐ **A blind critic with no repo access found this from pixels alone**, and put a number on
  it: *"105 of 715 overlapping pairs are 90%+ identical… stop re-cropping one master
  painting."* Measured independently here: **112 of 694**, same order, and its byte-identical
  pair maps exactly. **The seat is reliable on facts, not only on taste** — which is worth
  recording, because it is the ground under every other verdict it gave.
- **20 of 80 tiles are gable roof**, useless for a top-down dungeon interior, and they are paid
  for unless `building_layout: "grid"` drops them — which does not reduce the price.
