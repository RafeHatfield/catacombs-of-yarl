# STALL REPORT — five-round-park

**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling trigger: this report is the evidence.

- **lane** `worktree-tier1-floors`
- **surface** `floor`
- **guard** `five-round-park`
- **written** 2026-09-03T15:54:46

## Why it stopped

5 rounds on this lane with no PASS. The lane is parked; the next move is a ruling, not another round.

## What was tried, round by round

| round | verdict | build | capture | the seat's own words |
|---|---|---|---|---|
| 1 | FAIL | `42eabf326462` | `fc_standing.png` | Two things, either of which sinks it on its own. First, the barrels at approximately (120,196) and (170,196): the stone floor's top edge at y≈212 draws straight |
| 2 | FAIL | `404a664d4acc` | `fc_standing.png` | Two things, one of them shared with 2 and one of them 1's alone. Shared and fatal: roughly forty percent of the frame is not art. Everything outside the tan flo |
| 3 | FAIL | `f8745c18dc35` | `fc_standing.png` | There is no floor material in the frame. The entire lit area is a flat magenta field overlaid with black horizontal lines on an 8px period — the same lines, at  |
| 4 | FAIL | `24b492c1f163` | `fc_standing.png` | Nothing in it reads as architecture. Look at the vertical passage running down from the figure through the lower half: the strip of slabs continues downward, an |
| 5 | FAIL | `400da32af0a6` | `fc_standing.png` | There is not a single transition tile in the frame. The water is a rectangle: it runs x≈248–341, y≈0–191, and it stops at four hard 90° corners — the corner at  |

## The flip lists, verbatim

**round 1 (FAIL)**

- Same flat magenta wall tiles, same per-tile corner swatch, same saturation problem, same hard-clipped floor boundary at y≈199 and x≈310, same 45° hatch overlay, same mismatched sprite resolution, same missing light source on the figure, same missing contact shadow, same constant-width cracks — all as itemised for 2.
- The floor's joint structure has dissolved. In the region x 440–700, y 380–560 there is no legible slab edge anywhere: it is a soft brown gradient carrying scattered tally-marks and hatch. Raise the joint contrast until the floor reads as laid stone rather than as a wash.
- Large soft value-blobs sit across the floor that follow no geometry — the diagonal soft edge through (480,420)–(620,520) and the blur at (350,560). They read as airbrush, not as light or as material. Tie every value change to either a light falloff or a surface edge.
- The scribble marks — the small "T" shapes, dashes and tally clusters at (330,500)–(470,600) — are distributed as an even noise field across the whole floor. Place them deliberately in clusters where a hand would have made them, and leave stretches of floor with none.
- The brightest region sits roughly three-quarters of a tile *below* the figure, which reads as the light coming from underneath. Move it onto the sprite.

**round 2 (FAIL)**

- Delete the debug cell layer, as above. Same layer, same coordinates, same problem.
- Draw the wall geometry the deleted layer was standing in for.
- Open up the floor's value range. Every lit tile from x=320 to x=650 sits inside one narrow brown band, so slab, repair, hatched patch and ground-in dirt all read as the same material at the same distance. Separate at minimum the slab face from the joint and the repair patch from the slab.
- Break the hatched-slab repeat. The diagonal-hatch motif recurs on a visible rhythm across the lit area — vary the hatch angle, density, or omit it on a third of the slabs.
- Fix the cracks as in FLIP 1: they are the identical overlay, still uniform 1px black crossing joints without deflection.

**round 3 (FAIL)**

- Delete the horizontal stripe overlay entirely. It is not a floor texture; it is a scanline artifact, and it is the same on every surface in the frame.
- Replace it with an actual floor: cut slabs with joints that break bond between courses, varying joint depth along a single run, and per-stone value variation of at least 3 steps so no two adjacent stones match.
- Fix the misaligned block at x≈440–503, y≈325–395 — its pattern is one pixel out of phase with the floor around it. Whatever tile-placement or offset bug caused it, that seam is visible at a glance.
- Repitch the lit palette off saturated magenta. A carried lamp is warm and narrow-band; a floor lit to RGB ≈ (255,20,140) reads as a coloured stage light, not fire.
- Differentiate the corridor at x≈510–575 from the chamber by material, not brightness: narrower stones, a worn centre track, a threshold line where the two floors meet.
- Give the wall tiles a top surface. Right now they are black squares with a single dot; they need a lit cap edge on the sides facing the figure and a dark body, so the wall reads as having thickness.
- Put the four hundred years of repair on screen inside the lit radius: driven pins in a cracked slab, a rope lashing, a hide patch over a hole, salvaged timber pinned across a gap. The lit area is currently empty floor.

**round 4 (FAIL)**

- Build a wall that reads. Give wall tiles a distinct top surface value clearly separated from the lit floor, add visible thickness at the edge, and cast a shadow from the wall onto the floor on the far side from the lamp. Right now the passage below the figure has no sides.
- Sharpen the floor. The slab edges ramp over two to three pixels and adjacent blocks merge until the joint vanishes; step them at a hard boundary so the floor sits at the same resolution as the sprite.
- Take the cracks off the top of the lighting. They are pure black inside the brightest part of the lamp pool, which makes them the darkest thing in the frame; they need to be lit along with the surface they're in.
- Deflect the cracks at joints. A crack that crosses six slabs in one smooth curve without registering a single joint reads as a line drawn over the floor, not damage in it. Break them at joints, or run them along one.
- Give the cracks a section — a lighter lip on the lamp-facing side, dark in the channel. A uniform 1px black stroke has no depth.
- Fix the horizontal seam where the slab floor meets the mottled brown region. Add a threshold, a lip, or scattered debris crossing the line so the two surfaces interlock rather than butt.
- The mottled brown region has no structure at any scale and no relationship to the slab grid. Give it a legible material — rubble at a stated size, packed earth with direction, something with an edge — or make it stone.
- Over half the canvas carries no information. Either raise the ambient floor so the far architecture is faintly legible, or tighten the frame so the picture isn't mostly empty black.
- Same note as the other frame: the stated content is four hundred years of continuous repair with rope, pins, hide and salvaged timber. There is none of it in the floor. The falloff is the only thing doing work here.

**round 5 (FAIL)**

- The slab joints are washed out. Compare the region x=430–610, y=300–430 against the same coordinates in the other dark frame: here whole rows of slabs merge into one beige field with no mortar line between them — the run at (490,320)–(600,320) has no separation at all. Restore a consistent dark joint on all four sides of every slab, and vary its depth along a single run so the stones read as cut rather than stamped.
- Large soft blotches sit over the pixel art off-grid: the vertical smear at x≈450–470, y=300–430, and the diagonal shadow running from the figure down to (560,570). They are smooth gradients on hard-edged art and read as a filter pass. Quantise them to the palette's value steps and snap them to the tile grid.
- Isolated slabs float in the void with nothing joining them to the room: a dim bar at x=90–215, y=265–290, and another at x=280–430, y=138–165. Either connect them to walkable geometry or cull them from the render.
- The bottom-left and bottom ground (x=0–310, y=440–600, and the band below y=590) is a single mustard hue with uniform per-pixel noise — no stones, no clumps, no forms, no value grouping. It reads as static. Replace with drawn rubble: distinct fragments with their own light and shadow sides, sized in a range, grouped so there are open patches and dense patches.
- Same missing wall as the other dark frame: the floor edge at y=205 and the step at x=310 are cuts into black, not walls. Give the boundary a top surface separated in value from the lit floor and a contact line at its base.
- The two identical plus-shaped marks at roughly (590,405) and (590,480) are the same stamp at the same x. Offset, rotate, or vary them; a repeated glyph on a vertical line reads as a registration artefact.
- The whole frame's midtones sit in a narrow band — the floor at (430,330) and at (620,300) are close in value despite very different distance from the lamp. Widen the falloff range so the light has a shape, and let the far floor go genuinely dark rather than muddy.

## Where to look

Captures and transcripts, per round:

- round 1 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-tier1-floors-r1`, transcript `.claude/skills/frame-critic/history/r001-worktree-tier1-floors-transcript.txt`
- round 2 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-tier1-floors-r2`, transcript `.claude/skills/frame-critic/history/r002-worktree-tier1-floors-transcript.txt`
- round 3 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-tier1-floors-r3`, transcript `.claude/skills/frame-critic/history/r003-worktree-tier1-floors-transcript.txt`
- round 4 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-tier1-floors-r4`, transcript `.claude/skills/frame-critic/history/r004-worktree-tier1-floors-transcript.txt`
- round 5 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-tier1-floors-r5`, transcript `.claude/skills/frame-critic/history/r005-worktree-tier1-floors-transcript.txt`

## What is being asked for

A ruling. Not another round — the guard fired precisely because another round is the wrong move. Nothing installs to the phone while this stands.
