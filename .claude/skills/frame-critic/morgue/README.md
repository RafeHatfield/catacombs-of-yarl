# The morgue

Frames **Rafe personally culled at the device gate**, kept as pictures.

One of these is shuffled into every round's deck as the **picture-plant**. The seat must land it
worst-or-flagged and must not ship it; otherwise the round is VOID and its findings are not read
(`ART-LOOP-PROCESS-v0.md` §4, §1.2.1).

## Why these are pictures and not a generator

Every plant this project built before now was **composed** — `plant_ashlar.py`, `plant_walls.py`,
`plant_family.py` — a ruined family built by the same composer from the same material. That shape
failed four times in the recorded ledger, always the same way: **the plant was downstream of the
engine, so an engine change neutralised it silently.**

The sharpest instance is wall round 10. Since the cap pass, a cell's base is a cap window and the
wall family's top tiles are never drawn — so a plant that ruined only the wall tiles differed from
the family in **0.54% of pixels, across 21 cells.** The round voided. Nothing had gone wrong with
the plant's *code*; the picture it produced had simply stopped containing the defect.

**A picture cannot be neutralised by an engine change.** These bytes are fixed, and the defect in
them is fixed. `MORGUE.json` records a sha256 per entry and the runner refuses to start if any of
them has moved — a plant that can be edited is a plant that can be softened.

## What goes in here

A frame Rafe culled, with:

- **his verbatim words** — the cull as he put it, not a paraphrase
- **the commit whose build produced the frame**, so the picture can be reproduced
- **the surface tag** — `floor`, `wall`. The deck draws a plant of the round's own surface, because
  a floor plant in a wall round gets flagged for its magenta wall mocks: the right image caught for
  the wrong reason, which is not a control.
- **its sha256**

Not a frame an instrument disliked. Not a frame I thought was weak. **The morgue is a record of
human culls**, and adding to it is the correct response to any device-gate cull.

## What is in here now

| file | surface | Rafe's words |
| --- | --- | --- |
| `keyline-floor.png` | floor | *"outlined chips"* |
| `washed-slab-lane.png` | floor | *"it looks like all the tiles on the walked path have been replaced."* |
| `tile-quantized-wear.png` | floor | *"one tile worn, the one next to it not — that's not how it works."* |
| `grey-walls.png` | wall | *"Grey walls and ceiling; it looked better a few versions ago."* |

**Known limit, stated rather than discovered later: the `wall` lane holds one entry**, so wall
rounds draw the same plant every round. That is safe against the seat, which is fresh each round
and cannot remember one. It is **not** safe against a builder who learns to compose around a
single picture. Add wall entries as wall culls happen.

## ⚠ AND THAT LIMIT HAS NOW COST A ROUND — a plant must be culled on the axis the seat is asked about

The first wall round under the progress guards went **VOID**: the seat put `grey-walls.png`
**first in the deck and flagged nothing in it** (`../evidence/void-round-2026-09-03/`).

The seat was not being soft. `grey-walls.png` was culled for **chroma** — the wall family was
never given the floor's colour, and the delivered cap sat +27.6° of hue off the floor at 55% of
its saturation. The frame critic asks a seat to rank **craft**. That frame is well constructed and
the wrong colour, and it was only ever the wrong colour, so a competent seat can rank it first
without having failed at anything.

> **A plant controls for softness on the axis its cull was made on.** A colour cull cannot control
> a craft question. When adding an entry, record which axis the cull was about, and do not expect
> it to catch a seat asked about a different one.

**The wall lane needs a plant culled on construction.** Morgue entries are Rafe's culls, so that
one is his to supply — and until it exists, a wall round voiding on this plant is the mechanism
reporting a gap in the morgue rather than a fault in the seat.
