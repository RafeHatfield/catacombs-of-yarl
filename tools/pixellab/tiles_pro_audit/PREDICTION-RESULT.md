# `tile_depth_ratio` — THE RESULT, SCORED AGAINST THE PREDICTION

`PREDICTION.md` is **unedited** and was committed at `069aff5`, before `run_depth.py` was ever
executed. `git log -p PREDICTION.md` is the proof; this file is written afterwards and does not
touch it.

**Score: 4 of 5. The one that mattered held. The one that missed, missed clean.**

| # | predicted | measured | |
|---|---|---|---|
| 1 | `tile_depth_ratio` is live; the readout moves | `floor_bbox` and `floor_cell` moved | **HIT** |
| 2 | floor cell gets **shorter**, ~32×16 | it got **taller**: 32×24 → **32×35** | **MISS** |
| 3 | **clause 1 still 0 of 38** | **0 of 38** | **HIT** |
| 4 | the seat again reports face-on drawing where a top plane belongs | it did, on four pieces, unprompted | **HIT** |
| 5 | clause 3 (§6.3) degrades below kit A's 38/38 | **36/38** | **HIT** |

---

## Prediction 2 — where my model of the parameter was simply wrong

I predicted the cell would foreshorten. It did the opposite: **32×24 → 32×35**, taller than the
tile is wide, on an unchanged 52×87 canvas with `stack_stride_px` unchanged at 24.

The reasoning behind the miss is worth stating, because it was a real inference and it was
backwards. I read *"controls how much vertical depth the tile has"* as *ground pitch* — more
depth means the camera tips toward top-down, so the ground compresses. It is not that. **The
extra depth is extruded downward as visible thickness below the cell**, and the stride stays at
24 because the tiling pitch is unchanged; the sprite simply hangs 11 more pixels of side below
its footprint. On the floor tile that arrives as a timber sill strip along the bottom edge.

**So `tile_depth_ratio` adds thickness in the one place bible §3 does not want it — under the
floor, not on top of the wall.** That is a sharper answer than the prediction I wrote, and I got
it by being wrong out loud first.

## Prediction 3 — the claim on the line, and it held

`PREDICTION.md` named its own falsifier:

> "If **any** candidate clears clause 1 here, the finding's central claim — *the top surface is
> not modelled, and no camera parameter adds a plane that was never painted* — is wrong, and it
> will be corrected in `FINDING.md` in place rather than softened."

**None did.** Zero of 38, from a fourth blind seat that caught both its plants.

And prediction 4 is the reason, in the seat's own words, unprompted:

> *"This is the piece that should be the cap, and it is drawn as the same masonry elevation as
> the face."*
> *"The cap is drawn face-on with no top surface; **you would be setting the lantern on a
> drawing of a cap.**"*
> *"The post head at the top is drawn face-on, no cap plane."*

That is the fourth independent seat, on the fourth kit, in the third distinct projection,
reaching the same mechanism. Its flip-list item 1 also re-detects the compositor from pixels
alone — *"The set is one painting with rectangles masked out of it"* — which is now four seats
for four kits on that too.

**All three camera parameters have now been spent** — `tile_view_angle`, `building_wall_angle`,
`tile_depth_ratio` — and all three are live, and none of them reaches clause 1. The parameter
space this endpoint exposes for geometry is exhausted.

## Prediction 5 — the weakest one fired, and it cost more than predicted

Kit A and kit B were 38/38 clean on §6.3. Depth 0.5 came back **36/38**, and it also produced
**the audit's first mechanical culls: 2 × `noise`** — 152 candidates in, across four seats, the
first time anything was culled before the questions were even asked.

I flagged 5 as weakest on the grounds that arm 3 moved two parameters at once, so its §6.3 loss
was not cleanly attributed. **This call moved one parameter and lost §6.3 anyway**, which
removes that caveat: the degradation is attributable to asking this canvas for more
depth-by-value, on its own.

> Two surfaces, three mechanisms — a prompt (gauntlet round 8), a paired parameter (arm 3), and
> now a single parameter. **At 32 pixels, asking for geometric depth manufactures directional
> light.** This is no longer an anecdote about one tool.

## What this does and does not change

- **The finding's central claim stands unchanged and needs no correction.** It was put at risk
  properly, by a named falsifier on file before the call, and it survived.
- **`tile_depth_ratio` joins the platform record as a register lever with a cost**, alongside
  `tile_size` (§9.2): it makes the masonry chunkier and larger-scaled, and it charges §6.3 for
  it.
- **Nothing here changes the ruling.** tiles-pro is a parts supplier; the wall road is
  composition. This call was the last cheap thing that could have argued otherwise, and it
  argued the other way.
