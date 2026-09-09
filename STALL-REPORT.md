# STALL REPORT — no-change

**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling trigger: this report is the evidence.

- **lane** `polish-abc-install`
- **surface** `combined`
- **guard** `no-change`
- **written** 2026-09-08T17:15:41

## Why it stopped

rounds 1 and 3 are the same picture — mean 0.000 and worst cell 0
luminance levels apart over the delivered frame, byte-identical, against floors of
0.25 and 4, and both FAIL. Whatever was changed between them did not
reach the capture.

## What was tried, round by round

`rank` is where the build placed in that round's blind shuffled deck, and `score` normalises it so decks of different sizes compare — 1.00 is first, 0.00 is last. `Δpic` is how far the delivered frame moved from the previous round: mean and worst cell, in luminance levels. `0.000 / 0` means the picture did not change at all.

| round | verdict | rank | score | best? | Δpic | build | the seat's own words |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 1/4 | 1.00 | **new best** | — | `13364f377c55` | Three things, any one of which stops it. The two barrels at x 113–145 and x 161–193 are flat-cut by the stone floor edge at y=216. Their sta |
| 2 | VOID | 1/4 | 1.00 |  | 0.000 / 0 | `5685187cfba1` | There is no light model at all. The mud directly beneath the figure (x 218–232, y 30–45) averages luminance 66.1; the mud 170px away at bott |
| 3 | FAIL | 1/4 | 1.00 |  | 0.000 / 0 | `d96639d4f3aa` | The props are stamped, not placed. The two barrels at (115–149, 188–216) and (163–197, 188–216) are the same sprite offset 48px — 68.2% pixe |

## The flip lists, verbatim

Void rounds do not appear here. §4: the plant was missed, so those findings are not read — they are kept in the verdict under `flip_list_withheld` and are not evidence.

**round 1 (FAIL)**

- The slab at x 495–560, y 520–548 is a flat fill — one value, two stray specks, no grain — while every block touching it carries diagonal scratch hatch. Texture it to match its neighbours.
- That same slab's outline changes weight without cause: hard black for the leftmost ~15px of its top edge, then a pale 1px brown for the rest; its bottom edge is a broken dashed line of unequal darks; its left edge is black only in the lower half. Pick one joint weight and run it around the whole block.
- The falloff is not centred on the lamp. At equal radius (150–250px) the floor left of the figure averages luminance 47 and right of it averages 68. Concretely: open floor at x≈190, y≈490 — two tiles from the light — is near-black, while the same tileset at x≈630, y≈490 — seven tiles out — is pale cream, with nothing occluding either. Re-centre the attenuation on the figure or introduce the second emitter the image is already implying.
- The wall's top surface at y 395–420 is structureless airbrushed mottle — no courses, no joints, no block edges anywhere across x 200–500. It is the widest single element in the frame and it is the only one with no drawn information in it. Give it coursing consistent with the band below it.
- The background is rendered in soft blurred noise with razor-hard 1px black rectangles laid on top (clearest at the wall/floor line y=455 and around the hatch). Two mark languages in one image. Either soften the joint lines to sit in the same material or sharpen the fills.

**round 3 (FAIL)**

- The vertical wall tops at (120–180, 390–660) and (440–505, 240–380) are blurred mottle while the floor beside them is pixel-crisp. Half the picture is drawn at a lower resolution than the other half — this is the frame's single biggest fault. Redraw both at floor resolution.
- The wall/floor junction at y≈447 is a constant-value 2px near-black rule running the full width. Vary its depth along the run and let it lift where the light strikes it; right now it reads as an ink outline, not contact.
- The soot on the wall top between x=200 and x=430 is soft airbrush with no edges anywhere. Cut it to hard-edged staining that follows the joints and pools at the beam.
- The pin brace at x≈300 in the wall band is the only repair in a run of ~230px of wall. Carry the vocabulary — driven pins, lashings, salvaged timber — across the rest of the run, or the one brace reads as an accident rather than a company that has been holding this line for four hundred years.
- The floor blotch at (427–465, 520–560): draw it as a specific object or remove it.

## Where to look

Captures and transcripts, per round:

- round 1 — deck `/Users/rafehatfield/.claude/frame-critic/deck-1bfe6a153eb28b2e`, transcript `.claude/skills/frame-critic/history/r001-polish-abc-install-transcript-seat1.txt`
- round 2 — deck `/Users/rafehatfield/.claude/frame-critic/deck-842c9de81aba11d9`, transcript `.claude/skills/frame-critic/history/r002-polish-abc-install-transcript-seat1.txt`
- round 3 — deck `/Users/rafehatfield/.claude/frame-critic/deck-ec6b9f8627ea24b1`, transcript `.claude/skills/frame-critic/history/r003-polish-abc-install-transcript-seat1.txt`

## What is being asked for

A ruling. Not another round — the guard fired precisely because another round is the wrong move. Nothing installs to the phone while this stands.
