# STALL REPORT — no-change

**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling trigger: this report is the evidence.

- **lane** `polish-198-halo`
- **surface** `combined`
- **guard** `no-change`
- **written** 2026-09-08T21:20:14

## Why it stopped

rounds 1 and 2 are the same picture — mean 0.004 and worst cell 1
luminance levels apart over the delivered frame, against floors of
0.25 and 4, and both FAIL. Whatever was changed between them did not
reach the capture.

## What was tried, round by round

`rank` is where the build placed in that round's blind shuffled deck, and `score` normalises it so decks of different sizes compare — 1.00 is first, 0.00 is last. `Δpic` is how far the delivered frame moved from the previous round: mean and worst cell, in luminance levels. `0.000 / 0` means the picture did not change at all.

| round | verdict | rank | score | best? | Δpic | build | the seat's own words |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 2/4 | 0.67 | **new best** | — | `af90d3467196` | Two cameras in one frame, and a floor that is a noise layer. The barrels at (112–142, 192–215) and (163–193, 192–215) are drawn in three-qua |
| 2 | FAIL | 2/4 | 0.67 |  | 0.004 / 1 | `8157a6a45b0b` | It is lit flat, everywhere, from nowhere. There is no carried light and no falloff — the cobble at bottom-left (x≈15,y≈215) and the cobble a |

## The flip lists, verbatim

Void rounds do not appear here. §4: the plant was missed, so those findings are not read — they are kept in the verdict under `flip_list_withheld` and are not evidence.

**round 1 (FAIL)**

- The figure carrying the only light is darker than the ground he stands on: his shield samples L≈139 and his face L≈127 against floor L≈207 immediately to his right. Invert that — the sprite must be the brightest thing in its own pool, above the floor value, not 70 below it.
- The lamp casts no light onto its bearer. At 8× the face (404–414, 472–482) is one solid brick-orange mass with a single lighter smudge and no rim. Restore the pale helmet rim and the cheek highlight so the light source is legible on the figure holding it.
- The shield at (414–425, 483–497) has collapsed from four tones to two — a flat brown slab with one 4px dark dash. Re-separate the boss, the ring and the face; a shield that reads as a disc of cardboard at play size is the player's own avatar failing.
- Boots, belt and torso have converged to near-identical mid-orange, so the legs merge into the body. Push the boots at least 30 luma below the tunic.
- The wall band at (200–440, 395–450) is built from the same flagstone rectangles at the same joint pitch as the floor at (200–440, 460–520), differing only in value. Give the wall a different block size or bond pattern, plus a top surface and a cast shadow onto the floor at its base, so it is architecture and not floor-in-shadow.
- The corridor mouth at (503–535, 400–455) has no wall across it: the pale corridor floor runs down into the pale room floor with a single 1px value step at y≈440. Draw the wall through the junction and let the doorway be a cut in it.
- The right-hand wall at (535–585, 240–440) is soft cloudy blobs with no joints, sitting 60px from floor tiles with crisp 1px joints. Match the level of finish — either the walls get joints or the floor loses them.

**round 2 (FAIL)**

- The upper half of the room's top wall (x≈185–500, y≈390–425) is a featureless brown smear with no stone joints, while the course directly below it (y≈428–450) has crisp black joints. Draw the upper course to match the lower one.
- The black void's lower boundary cuts the wall top with a dead-straight horizontal at y≈388 and a right-angle step at x≈500. That edge reads as an unpainted rectangle, not shadow. Break it against the wall's stones and let the darkness fall off across at least half a tile.
- The corridor mouth at (x≈440–560, y≈430–450) collapses to a 2–3px dark line with two isolated blocks stuck to it; the wall has no thickness where it is cut. Rebuild the cut end with stones that show their depth.
- A row of small dark dashes runs across the corridor at (x≈505–540, y≈390) with no object under them. Remove or resolve into an actual feature.
- The pale amorphous blob at (x≈425–465, y≈495–540) has a ragged edge, overlaps three tile joints, and is neither stone, stain nor crack. Replace with a defined feature or remove it.
- The figure's keyline has been tinted to mid-brown and the shield reduced to a flat tan disc with no rim — the player's silhouette is now within one value step of the floor. Restore a dark keyline on the sprite and put a rim value on the shield.
- The alcove at (x≈310–380, y≈645–710) is a hard-cornered black rectangle with a smeared interior. Give the interior readable structure or make the opening's edge irregular.

## Where to look

Captures and transcripts, per round:

- round 1 — deck `/Users/rafehatfield/.claude/frame-critic/deck-f6c9882c720d35fd`, transcript `.claude/skills/frame-critic/history/r001-polish-198-halo-transcript.txt`
- round 2 — deck `/Users/rafehatfield/.claude/frame-critic/deck-ae4a6237dd6c725f`, transcript `.claude/skills/frame-critic/history/r002-polish-198-halo-transcript-seat1.txt`

## What is being asked for

A ruling. Not another round — the guard fired precisely because another round is the wrong move. Nothing installs to the phone while this stands.
