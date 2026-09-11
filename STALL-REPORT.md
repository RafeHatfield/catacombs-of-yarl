# STALL REPORT — broken-judge

**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling trigger: this report is the evidence.

- **lane** `art/autonomy-amendment`
- **surface** `combined`
- **guard** `broken-judge`
- **written** 2026-09-11T15:46:05

## Why it stopped

the picture-plant was missed 2 rounds running. The judging layer is broken; no round past it is readable and nothing ships past it.

## What was tried, round by round

`rank` is where the build placed in that round's blind shuffled deck, and `score` normalises it so decks of different sizes compare — 1.00 is first, 0.00 is last. `Δpic` is how far the delivered frame moved from the previous round: mean and worst cell, in luminance levels. `0.000 / 0` means the picture did not change at all.

| round | verdict | rank | score | best? | Δpic | build | the seat's own words |
|---|---|---|---|---|---|---|---|
| 1 | INSTALL-LATEST | 2/4 | 0.67 | **new best** | — | `f5081c3138d9` | Two things a person sees before they see anything else. First, **the barrels are cut in half by the floor.** Both barrels at y≈190–217 termi |
| 2 | INSTALL-LATEST | 1/4 | 1.00 | **new best** | 0.000 / 0 | `f5081c3138d9` | Four things, any one of which is disqualifying. The mud field is one 48×48px block stamped across the entire 190×288px area. I measured it:  |
| 3 | VOID | 2/4 | 0.67 |  | 0.855 / 57 | `275a62a30ac1` | The pool at (248–343, 0–192) is a hard-edged rectangle of hex-pattern green with a 1px lighter border and no bank, lip, shadow or wet edge w |
| 4 | VOID | 2/4 | 0.67 |  | 0.538 / 10 | `44986fe8eaa9` | It is assembled, not made. There is no light source at all — the orc at (220,10) carries nothing and the frame is the same value edge to edg |

## The flip lists, verbatim

Void rounds do not appear here. §4: the plant was missed, so those findings are not read — they are kept in the verdict under `flip_list_withheld` and are not evidence.

**round 1 (INSTALL-LATEST)**

- **Every fire in this frame subtracts light.** I compared identical regions against 2 (global exposure matched within 1 luma across four control patches). Floor left of the firepit: −9.5. Floor right of it: −10.7. Floor below it: −13.8. Floor around the burning stick pile: −15.8. There is a lit flame in a ring of hearthstones at (596, 548) and the stones of its own ring are darker than the bare floor was before the fire was placed there. Make each fire prop a light emitter: warm falloff of 2–3 tiles, brightest on the hearthstones themselves, and remove the darkening halo the placement pass is currently applying.
- The lantern at (330–360, 535–570) is illegible at play size. Its left edge has a hard outline, its right edge has none — the pixels just stop into the floor. Close the silhouette on all four sides with the same outline weight, and give the top face a distinct value so it reads as an object seen from above rather than a front panel.
- That lantern and the firepit ring are drawn in near-elevation — you see a front face and a grate — inside a strictly overhead frame. Redraw both to the same camera as the floor.
- The same two-crossed-sticks motif appears three times inside four tiles: dark brown at (275, 612), saturated red-orange at (405, 612), and as a parallel pair at (530, 618). Cut it to one, and vary the remaining timber by length and angle rather than by hue.
- The crossed sticks at (405, 612) sample (158, 49, 20) — a saturated red that appears nowhere else in the set, on stone that samples (127, 93, 64). Bring the props onto the environment ramp; they currently read as a different artist's layer dropped on top.
- None of the five floor props has a contact shadow. They sit on the stone with no anchor. Add a one-to-two-pixel occlusion darkening on the side facing away from the carried light.

**round 2 (INSTALL-LATEST)**

- The middle prop at x≈408, y≈613 is not readable as an object. At native resolution it is a lumpy heart-shaped mass of saturated red-orange with loose yellow pixels along its lower edge — no straight plank edges, no consistent light direction, and it is the highest-chroma element in the entire frame. Redraw it with the same two-plank construction and the same silhouette discipline as the prop at x≈285, or cut it.
- Those three props sit at y≈612, 613, 613, spaced 125px and 125px apart, and are three different sizes and three different colour temperatures of the same crossed-plank object. Break the row: move at least one off that y, and settle on one plank width and one wood hue across all three.
- The round object at x≈597, y≈548 contains a lit flame and emits no light. The cobbles of its own ring, 1–2px from the flame, sit at the same value as unlit stones 30px away. Either give it a local falloff that brightens the surrounding four or five flagstones, or take the flame out.
- That same object's interior is near-pure black with a hard edge; every other dark in the lit floor is a warm brown. Re-key the hole interior to the frame's darkest warm brown.
- Its ring cobbles read brighter than floor stones that are closer to the player's lamp. Re-light the prop through the same distance falloff as the floor instead of drawing it at fixed value.
- The flame inside it is four flat colour steps at ~10px tall — an interface-icon rendering. Redraw at the scene's material fidelity or remove.

## Where to look

Captures and transcripts, per round:

- round 1 — deck `/Users/rafehatfield/.claude/frame-critic/deck-30196a27487ba42b`, transcript `.claude/skills/frame-critic/history/r001-art_autonomy-amendment-transcript.txt`
- round 2 — deck `/Users/rafehatfield/.claude/frame-critic/deck-7c1ae7154dd3a4bb`, transcript `.claude/skills/frame-critic/history/r002-art_autonomy-amendment-transcript-seat1.txt`
- round 3 — deck `/Users/rafehatfield/.claude/frame-critic/deck-7b01b7c7c285d280`, transcript `.claude/skills/frame-critic/history/r003-art_autonomy-amendment-transcript-seat1.txt`
- round 4 — deck `/Users/rafehatfield/.claude/frame-critic/deck-fff24b0496b478af`, transcript `.claude/skills/frame-critic/history/r004-art_autonomy-amendment-transcript-seat1.txt`

## What is being asked for

A ruling. Not another round — the guard fired precisely because another round is the wrong move. Nothing installs to the phone while this stands.
