# STALL REPORT — no-change

**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling trigger: this report is the evidence.

- **lane** `combined`
- **surface** `combined`
- **guard** `no-change`
- **written** 2026-09-06T09:30:48

## Why it stopped

rounds 1 and 2 are the same picture — mean 0.000 and worst cell 0
luminance levels apart over the delivered frame, byte-identical, against floors of
0.25 and 4, and both FAIL. Whatever was changed between them did not
reach the capture.

## What was tried, round by round

`rank` is where the build placed in that round's blind shuffled deck, and `score` normalises it so decks of different sizes compare — 1.00 is first, 0.00 is last. `Δpic` is how far the delivered frame moved from the previous round: mean and worst cell, in luminance levels. `0.000 / 0` means the picture did not change at all.

| round | verdict | rank | score | best? | Δpic | build | the seat's own words |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 1/3 | 1.00 | **new best** | — | `6e4f980012c4` | The dirt field is one 16×16 tile repeated across roughly 150 cells with no variation whatsoever. Crop x 100–244, y 20–164 and the same dark- |
| 2 | FAIL | 1/3 | 1.00 |  | 0.000 / 0 | `08be3c7e6e32` | The construction is wrong, not just thin. The body of water (x 248–343, y 0–191) is an axis-aligned rectangle with 90° corners and a one-pix |

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

## Where to look

Captures and transcripts, per round:

- round 1 — deck `/Users/rafehatfield/.claude/frame-critic/deck-d3a75aa4363e50e7`, transcript `.claude/skills/frame-critic/history/r001-combined-transcript.txt`
- round 2 — deck `/Users/rafehatfield/.claude/frame-critic/deck-bfc3fb231fce4c52`, transcript `.claude/skills/frame-critic/history/r002-combined-transcript.txt`

## What is being asked for

A ruling. Not another round — the guard fired precisely because another round is the wrong move. Nothing installs to the phone while this stands.
