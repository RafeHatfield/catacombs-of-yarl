# STALL REPORT — stall

**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling trigger: this report is the evidence.

- **lane** `combined`
- **surface** `combined`
- **guard** `stall`
- **written** 2026-09-07T13:07:34

## Why it stopped

3 readable rounds with no new best rank. The best is 1.00, set at round
1, and nothing since has beaten it. The lane is not converging.

## What was tried, round by round

`rank` is where the build placed in that round's blind shuffled deck, and `score` normalises it so decks of different sizes compare — 1.00 is first, 0.00 is last. `Δpic` is how far the delivered frame moved from the previous round: mean and worst cell, in luminance levels. `0.000 / 0` means the picture did not change at all.

| round | verdict | rank | score | best? | Δpic | build | the seat's own words |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 1/3 | 1.00 | **new best** | — | `6e4f980012c4` | The dirt field is one 16×16 tile repeated across roughly 150 cells with no variation whatsoever. Crop x 100–244, y 20–164 and the same dark- |
| 2 | FAIL | 1/3 | 1.00 |  | 0.000 / 0 | `08be3c7e6e32` | The construction is wrong, not just thin. The body of water (x 248–343, y 0–191) is an axis-aligned rectangle with 90° corners and a one-pix |
| 3 | FAIL | 2/3 | 0.50 |  | 12.147 / 56 | `ce139378b2ec` | Three separate failures, any one of which is disqualifying. *The dirt is stamped on a visible lattice.* Hashing the frame at 16 px shows the |
| 4 | VOID | 2/3 | 0.50 |  | 0.688 / 36 | `100cb8206eb7` | Three things, any one of which is disqualifying. First, there are no walls. The dirt field, the grey flagstone at left and right, and the wa |
| 5 | FAIL | 1/3 | 1.00 |  | 0.000 / 0 | `d361e4f08430` | The flagstone floor is a flat fill with a grid drawn on top. The band at (40–340, 230–258) contains 7 unique colours total, and one of them  |

## The flip lists, verbatim

Void rounds do not appear here. §4: the plant was missed, so those findings are not read — they are kept in the verdict under `flip_list_withheld` and are not evidence.

**round 1 (FAIL)**

- The figure is rendered at a ~2px hard pixel grid; the environment is soft and resampled with no fixed pixel size. Quantise the environment to the same pixel grid as the sprite so stone edges land on hard pixel boundaries instead of gradients.
- A diagonal streak/hatch band runs down-left at ~45° across the lit pool around (430,470)–(560,560). A point lamp cannot produce a directional band. Delete the overlay.
- The incised double-tick "//" marks on the stones right of the figure (roughly x 565–620, y 480–580) recur at identical angle and identical length about fifteen times. Vary angle and length per instance, or cut their count by two thirds.
- The block at approx (494,520)–(558,550) is flat and untextured, brighter than every stone around it, and further from the lamp than the figure. Give it the same joint and wear treatment as its neighbours and drop it to the value its distance from the lamp implies.
- Four cracks radiate from a single point at ~(314,600) in a near-symmetric X. Stone does not fracture radially from a point. Break it into two crossing fractures with offset origins, or remove two of the four arms.
- The wall band at y 385–440 is mottled brown noise with no legible courses. Draw actual stone runs into it with joint lines at the same weight as the floor's.
- Nothing anywhere in the frame shows a repair. The fiction specifies rope, driven pins, hide and salvaged timber holding this floor together for four hundred years. Add at least two: a timber baulk pinned across a gap in the paving, and a stone lashed back into a course.

**round 2 (FAIL)**

- The lamp core is clipped: 12,874 non-UI pixels sit at luminance ≥246 in a contiguous patch at x 285–504, y 457–601, where the floor loses every joint and slab edge into flat cream. Pull the light curve's white point down so no floor pixel exceeds ~232, and let the falloff reach that ceiling asymptotically instead of saturating.
- The area at x 130–430, y 65–133 is structureless soft blob-noise — no joints, no block edges, no coursing, just 6–10px mottle. Draw masonry there at the same slab logic as the south floor and let the darkness dim it.
- The corridor floor at x 440–503, y 300–460 is the same failure in the lit zone: mottled tan cloud with no joints, directly adjacent to fully-jointed floor. Cut slabs into it.
- The plated objects at x 505–570, y 290–400 are outlined in a salmon-pink that appears nowhere else in the frame's palette. Re-key those outlines to the warm brown already used for joints in the adjacent stone.
- The crack lines (the long curve entering at x 150, y 780 and the one crossing x 430–620, y 520–560) are anti-aliased smooth splines with soft grey edges over hard-pixel art — they are the only lines in the frame without jaggies. Redraw them on the pixel grid using the existing joint colours.
- The same 3–4 stroke diagonal hatch decal is stamped at identical angle and length on slabs at roughly (350,800), (480,805), (850,795), (920,890). Build three or four hatch variants and vary the rotation, or hand-vary the worst repeats.
- The dotted stipple fringe along the lower edge of the slabs at y 148–158 runs unbroken across the full width at constant density. Break it up so it appears on some slabs and not others.

**round 3 (FAIL)**

- The lit floor is blown out. Excluding UI and sprite, 12,159 pixels sit above luma 190, against 289 in the comparable frame; the floor around the figure reaches ≈(240,235,215). Pull the peak floor value down until the brightest stone is well clear of the sprite's lightest pixels.
- Consequence of the above, and the reason it matters: the sprite stops reading. The shield's cream face and the sword blade's interior land at the same value as the floor beside them, so only the dark outline holds the figure together. Fix the exposure and check the read again at 1:1.
- Restore joints in the blown region. At x 430–700, y 470–560 there is a flat pale block roughly 110×28 px with no interior texture and a dark line on only two of its four edges. Every block in that pool needs its joints back.
- Unify the detail scale in that same region: adjacent blocks alternate between crisp 1 px diagonal hatch triplets and completely blank gradients. Pick one density and hold it.
- Remove or attach the free-floating dark bars — roughly 3×20 px verticals at around (505,505) and (525,505) — that sit mid-block, joined to no joint and no timber.
- The block edges there are soft, anti-aliased gradients roughly 4 px wide while the sprite is hard 1 px. Snap the floor art back to the pixel grid; as it stands the frame carries two rendering resolutions.
- Strip the mottled cloud-blotch layer off the wall tops at y≈390–455. The dark green-brown blobs cross stone divisions and ignore every joint underneath them — it reads as a grunge texture multiplied over the tiles rather than as stained stone. If the stain stays, cut it to the block boundaries.
- Give the wall's top surface a value separation from the lit floor. In the lit span they sit close enough that the wall does not read as raised.
- The grey patch at roughly x 120–200, y 55–133 is an axis-aligned rectangle sitting inside the black unexplored area with hard straight sides. Either texture it or let it go to the same black as its surround.

**round 5 (FAIL)**

- The figure at (385–430, 460–510) carries sword and shield and no light source, while the only light in the frame originates at its feet. Put a hooded lamp in the shield hand or hung at the belt, and move the light origin to the lamp.
- That sprite is the only object in the frame with an outline — a black inner line plus a cream outer line, visible all around the helmet and boots — and the only one using saturated cyan (~#8FD8D8) and pure orange. Nothing in the environment uses an outline or either hue. Repaint it onto the environment's tan/umber/soot ramp and drop to a single dark outline or none.
- At (450–530, 380–470) the wall's top surface and the lit corridor floor both sit at L≈190–210 and carry the same speckle; only a 1–2px dark line separates them. Drop the wall top ~25 values and give it a coarser, larger-scale grain than the floor.
- The wall tops at (390–490, 70–190) and (620–750, 70–190) have no joints at all — they are soft airbrushed cloud. Draw the same block courses used at (430–750, 400–450) and let value, not blur, take them into the dark.
- The object at (275–380, 640–710) reads as nothing: soft rim on all four sides, an interior of four arbitrary lighter and darker rectangles, no top plane, no side plane, and its left edge lands mid-tile. Resolve it into a named object — hatch, crate, grating — with a hard top edge and one visible side face, or delete it.
- The crack descending from (330, 600) stops dead at that object's top-left corner and a different crack restarts at its right edge. Run one continuous crack under it, or terminate it into something.
- 23.4% of the frame sits below L=8 — flat void carrying no information. Raise the ambient floor to L≈14–18 so the unlit rooms at (0–180, 150–640) and (620–750, 150–300) still show block courses in silhouette.
- The place is described as held by orc-soldiers repairing with rope, pins, hide and salvaged timber. One timber and two pins appear, all in the same wall run at (600–710, 400). Nothing in the other 90% of the frame has been touched by anyone. Carry the repair vocabulary into the floor and the far walls.

## Where to look

Captures and transcripts, per round:

- round 1 — deck `/Users/rafehatfield/.claude/frame-critic/deck-d3a75aa4363e50e7`, transcript `.claude/skills/frame-critic/history/r001-combined-transcript.txt`
- round 2 — deck `/Users/rafehatfield/.claude/frame-critic/deck-bfc3fb231fce4c52`, transcript `.claude/skills/frame-critic/history/r002-combined-transcript.txt`
- round 3 — deck `/Users/rafehatfield/.claude/frame-critic/deck-5c9a8cb6b18a6c2e`, transcript `.claude/skills/frame-critic/history/r003-combined-transcript.txt`
- round 4 — deck `/Users/rafehatfield/.claude/frame-critic/deck-9deedbff73d7e8a6`, transcript `.claude/skills/frame-critic/history/r004-combined-transcript.txt`
- round 5 — deck `/Users/rafehatfield/.claude/frame-critic/deck-eaf7a092e3e795cb`, transcript `.claude/skills/frame-critic/history/r005-combined-transcript.txt`

## What is being asked for

A ruling. Not another round — the guard fired precisely because another round is the wrong move. Nothing installs to the phone while this stands.
