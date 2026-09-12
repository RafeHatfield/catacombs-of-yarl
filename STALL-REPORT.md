# STALL REPORT — broken-judge

**The line has stopped and is not restarting itself.** LOOP-PROCESS §1.1.4 ruling trigger: this report is the evidence.

- **lane** `art/object-projection`
- **surface** `combined`
- **guard** `broken-judge`
- **written** 2026-09-12T13:25:38

## Why it stopped

the seat-level plant term tripped: slot 1 missed a live plant and its RE-DRAW missed too ({'file': 'cement-cap.png', 'surface': ['wall', 'combined'], 'axis': ['construction'], 'sha256': '3fd8223295d2f92e59f8c24f9d84163ed3223381939a554d1f6398130c3a4f0a', 'source': 'tools/tier1_walls/evidence/r22_standing.png @ 431c140f', 'culled_by': 'Rafe, device walk, 2026-09-03', 'verbatim': 'caps are still grey and read as cement, not stone', 'defect': "the found-rock cap with no architecture in it. The cap is one smooth field: no slabs, no fractures, no tooling, so the largest surface in frame is a value with noise on it. Measured, its wall cells carry a 4.6% hard-edge share against the 10.7% of the last approved build - the cap pass more than halved the wall's drawn edges. This is the CONSTRUCTION plant: it is wrong about whether a mass is made of anything, and it is deliberately RIGHT about chroma, so a round judged on construction cannot pass by fixing colour.", 'provenance': 'tools/tier1_walls/CRITIC-STOP.md and STALL-REPORT.md; the frame the critic itself ranked below the grey plant in rounds r001 and r002.', 'combined_eligibility': 'Serves `combined` too: no magenta anywhere in it, and it was captured with the real tier-one floor laid under the walls, so it is already a whole-scene frame.'}, then {'file': 'cement-cap.png', 'surface': ['wall', 'combined'], 'axis': ['construction'], 'sha256': '3fd8223295d2f92e59f8c24f9d84163ed3223381939a554d1f6398130c3a4f0a', 'source': 'tools/tier1_walls/evidence/r22_standing.png @ 431c140f', 'culled_by': 'Rafe, device walk, 2026-09-03', 'verbatim': 'caps are still grey and read as cement, not stone', 'defect': "the found-rock cap with no architecture in it. The cap is one smooth field: no slabs, no fractures, no tooling, so the largest surface in frame is a value with noise on it. Measured, its wall cells carry a 4.6% hard-edge share against the 10.7% of the last approved build - the cap pass more than halved the wall's drawn edges. This is the CONSTRUCTION plant: it is wrong about whether a mass is made of anything, and it is deliberately RIGHT about chroma, so a round judged on construction cannot pass by fixing colour.", 'provenance': 'tools/tier1_walls/CRITIC-STOP.md and STALL-REPORT.md; the frame the critic itself ranked below the grey plant in rounds r001 and r002.', 'combined_eligibility': 'Serves `combined` too: no magenta anywhere in it, and it was captured with the real tier-one floor laid under the walls, so it is already a whole-scene frame.'}). A slot that misses twice is the judge, not the draw.
Ruled 2026-09-11: a live-plant miss voids the SEAT and the slot is re-drawn once. This is the case that outruns the re-draw.

## What was tried, round by round

`rank` is where the build placed in that round's blind shuffled deck, and `score` normalises it so decks of different sizes compare — 1.00 is first, 0.00 is last. `Δpic` is how far the delivered frame moved from the previous round: mean and worst cell, in luminance levels. `0.000 / 0` means the picture did not change at all.

| round | verdict | rank | score | best? | Δpic | build | the seat's own words |
|---|---|---|---|---|---|---|---|
| 1 | VOID | 2/4 | 0.67 |  | — | `42ba626386e2` | There is no light source in the frame — the figure at (215–245, 0–25) illuminates nothing and the whole 384×288 is lit flat, so the one thin |

## The flip lists, verbatim

Void rounds do not appear here. §4: the plant was missed, so those findings are not read — they are kept in the verdict under `flip_list_withheld` and are not evidence.

## Where to look

Captures and transcripts, per round:

- round 1 — deck `/Users/rafehatfield/.claude/frame-critic/deck-8f47012cd90f5da0`, transcript `.claude/skills/frame-critic/history/r001-art_object-projection-transcript.txt`

## What is being asked for

A ruling. Not another round — the guard fired precisely because another round is the wrong move. Nothing installs to the phone while this stands.
