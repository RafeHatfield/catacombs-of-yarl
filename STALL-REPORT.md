# STALL REPORT — five-round-park

**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling trigger: this report is the evidence.

- **lane** `worktree-session-2026-08-29`
- **surface** `wall`
- **guard** `five-round-park`
- **written** 2026-09-03T19:29:13

## Why it stopped

5 JUDGED rounds on this lane with no PASS (voids excluded — they are not evidence). The lane is parked; the next move is a ruling, not another round.

## What was tried, round by round

| round | verdict | build | capture | the seat's own words |
|---|---|---|---|---|
| 1 | FAIL | `155429056b4e` | `fc_standing.png` | Nothing in it is shaped; everything is a rectangle laid over a rectangle. The water is an axis-aligned block, x≈248–343 by y≈0–191, with four dead-straight edge |
| 2 | FAIL | `ce716ac1eb96` | `fc_standing.png` | Three separate projections in one frame, and terrain painted as rectangles. The pond occupies x≈246–342, y≈0–188 as an exact axis-aligned rectangle with a hard  |
| 3 | FAIL | `494912d713af` | `fc_standing.png` | The two barrels at (110–150, 185–210) and (155–195, 185–210) are **guillotined dead flat** by the dirt/stone boundary at y=205. The left barrel's staves simply  |
| 4 | FAIL | `4e8f175be9ce` | `fc_standing.png` | Two-thirds of the frame contains no drawn architecture. The chambers flanking the corridor — x20–300 and x460–740, y60–380 — are mottled brown noise crossed by  |
| 5 | VOID | `6890b826c375` | `fc_standing.png` | The pond is a rectangle. Water occupies exactly x248–343, y0–191; at row 100 it starts at x=248 and stops at x=343 on a dead-straight vertical pixel line, and a |
| 6 | FAIL | `30054521159b` | `fc_standing.png` | It has no light model at all. Grey flagstone directly beside the figure at (355,20) is RGB(90,90,90); grey flagstone at the far edge at (10,90) is RGB(90,90,90) |

## The flip lists, verbatim

**round 1 (FAIL)**

- A grain filter has been run over the entire frame — the speckle is visible in the near-black at the bottom-left corner around x≈50–150, y≈780–880, where there is nothing to be textured. Remove the global noise pass.
- The upper wall masses at x≈60–370 and x≈440–700, y≈90–390 are dense sponge speckle that reads as loose gravel, not a surface. Replace with drawn courses at the frame's own pixel size.
- The region left of the figure, x≈230–400, y≈445–560, carries one continuous 45° hatch at a single pitch that runs straight across every slab joint without breaking. That is a texture overlay sitting on top of the masonry, not stone tooling. Clip the hatch to each slab and change its angle per slab.
- The cluster at x≈330–430, y≈555–605 is a group of dark smears and half-erased marks that resolve into no object. Either draw the thing that is there — a repair, a fitting, a grate — or clear the floor.
- Small unattached pale squares float free of any slab boundary, e.g. x≈330,y≈495 and x≈345,y≈505. Delete them or seat them in the bond.
- The corridor floor between y≈300 and y≈440 has lost its joints entirely and dissolves into undifferentiated dither. Restore the slab grid through the full length of the corridor so the doorway and the floor stay the same construction.
- The lamp's peak, x≈300–470, y≈460–560, clips to flat white. Lower the ceiling on the falloff so stone detail survives at the brightest point.

**round 2 (FAIL)**

- The floor from x≈150 to x≈400, y≈450–560 carries one unbroken 45° hatch that runs straight through every place a joint should be. There are no tile boundaries in that region at all. Delete the hatch overlay, draw the courses first, then reapply wear per-stone clipped to each stone's bounds.
- The corridor at x 380–435 has zero masonry seams from y≈200 down to y≈460 — 260px of continuous noise where paving should be. Give it joints on the same course spacing as the lit floor.
- Same fix in the lower-right floor, x≈450–700, y≈600–830: nearly every tile carries an identical `\\ \\` stroke pair plus the same vertical tick cluster. That is a stamp, and at this density it is obvious.
- Brightness down the corridor centre at x=405 swings 102→169→114→184→110 pixel to pixel. The noise is louder than the light gradient carrying it. Cut its amplitude to under about 15 levels and bind the variation to stone boundaries so it reads as different stones rather than static.
- Same brighten-test failure as 1 — the dark upper region is fine mottle with no architecture under it. Draw the stone through it.
- Same missing-repairs problem as 1: nothing rigged, lashed or pinned anywhere in the lit radius.

**round 3 (FAIL)**

- The corridor floor (378–432, 220–460) is a column of 1px vertical streaks with no slab boundaries, while the room floor 20px to either side is cut slabs. It is the brightest, most central surface in the frame and has no structure. Redraw it as slabs on the room's module, coursed across the corridor.
- The ceiling masses at (60–370, 70–380) and (440–740, 70–380) are soft blotches 12–20px across — softer and larger than any other feature. The 1px crack lines are hard but sit on mush. Replace the blotch fill with value noise at the floor's granularity.
- The wall run at y 385–435 has a flat black top surface, so the wall reads as an absence rather than a mass with thickness. Give the top face its own lit value, separated from both the floor and from black.
- The figure at (390–430, 460–510) has no contact: the slab under its feet is the same value as one a tile away. Add a cast shadow and one extra brightness step on the two tiles it stands on.
- The chisel hatch is a single 45° angle across every slab in the frame. Vary the angle per slab.
- Nothing in the frame is an object. Four hundred years of rope, driven pins, hide and salvaged timber, and not one piece of it is visible — the frame is floor, ceiling, and one wall strip. Put the salvage in.

**round 4 (FAIL)**

- Remove the blur/resample pass. The floor art already exists intact in 2 and 4 at the same coordinates; render it at 1:1 so slab joints are hard 1px edges again.
- Replace the noise fill in x20–300 and x460–740, y60–380 with the laid stone courses used in the lit floor, then dim them. Do not substitute texture for architecture.
- Redraw every crack as a hard 1px run on the grid, the way the crack at x120–340 / y490–560 already is. The polygon outlines in the flanking chambers are anti-aliased curves sitting between pixels — delete them.
- Restore tile detail in the corridor at x380–420 / y230–450 and apply distance falloff as a value ramp over intact art, not as a vertical smear.
- Resolve the wall band mortar at y≈390–430 from 4px soft bands to 1px hard lines, and put a value step between the wall's top surface and the lit floor below it.
- The figure is stated to carry the only light and is holding a sword and a shield. Give it a lamp or a torch, or move the light origin onto something the player can see.

**round 5 (VOID)**

- Joints in the lit floor (x240–560, y520–640) have been blurred out — edge energy 2.44/2.86 against 3.40/3.60 for the identical region in the other frames. Restore the 1px joint darks at native resolution; do not resample the tile layer before compositing light.
- The upper rooms at x0–370, y75–390 are a Voronoi cell field — irregular polygons with thin dark borders and soft blotch fill. There is no brick, no course line, no straight architectural edge anywhere in it. Replace with the masonry already drawn elsewhere in this same frame.
- A pale wedge runs from about (90,470) diagonally down to the figure, ignoring the slab grid and with no emitter anywhere along it. Delete it, or give it a source.
- The cluster at roughly x340–450, y570–620 is smeared dark noise that reads as no object. Redraw it as a readable prop or clear it.
- Then everything in FLIP 2.

**round 6 (FAIL)**

- The entire rock mass outside the corridor (x 0–370 and x 440–750, y 90–450) is continuous-tone mottled cloud noise — soft round blobs at 8–12px with no edges and no repeat. Replace it with drawn material at the same texel size as the floor, or make it flat unlit fill. It currently reads as a noise layer, not stone.
- Long unbroken straight lines cut through that noise — one from approx (37,170) to (140,95), another running from (280,80) down to (375,390) — forming a fan of wedges radiating from the corridor mouth. Rock does not fracture in 300px straight segments. Remove them or replace with breaks that step and change direction.
- Light is passing through solid rock. At y=340 the rock at x=300 is (63,45,25) against the corridor floor at (410,300) = (82,64,41) — the unexcavated mass is 77% as bright as the walked surface. Occlude the lamp against the corridor walls so the glow terminates at the passage edge.
- Floor joints break down right of the figure (x 480–700, y 470–620): many slabs carry only a 6–10px vertical dark tick where an edge should be and no perimeter at all — see the isolated strokes at approx (505,560) and (575,505). Close the perimeters so the slabs read as cut blocks instead of tonal patches.
- The timber run at y≈390–420 left of x≈300 sits within about 3 values of the wall behind it and reads as a smear. Separate the boards from the wall by at least one clear step and restore the individual board ends.
- The whole frame carries a soft continuous-tone mottle over the pixel work (5763 unique colours against 2's 3414 for the same scene). Drop that layer; it's the single thing making the image read as filtered.

## Where to look

Captures and transcripts, per round:

- round 1 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-session-2026-08-29-r1`, transcript `.claude/skills/frame-critic/history/r001-worktree-session-2026-08-29-transcript.txt`
- round 2 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-session-2026-08-29-r2`, transcript `.claude/skills/frame-critic/history/r002-worktree-session-2026-08-29-transcript.txt`
- round 3 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-session-2026-08-29-r3`, transcript `.claude/skills/frame-critic/history/r003-worktree-session-2026-08-29-transcript.txt`
- round 4 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-session-2026-08-29-r4`, transcript `.claude/skills/frame-critic/history/r004-worktree-session-2026-08-29-transcript.txt`
- round 5 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-session-2026-08-29-r5`, transcript `.claude/skills/frame-critic/history/r005-worktree-session-2026-08-29-transcript.txt`
- round 6 — deck `/Users/rafehatfield/.claude/frame-critic/worktree-session-2026-08-29-r6`, transcript `.claude/skills/frame-critic/history/r006-worktree-session-2026-08-29-transcript.txt`

## What is being asked for

A ruling. Not another round — the guard fired precisely because another round is the wrong move. Nothing installs to the phone while this stands.
