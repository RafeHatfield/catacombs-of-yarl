# Round 22 — the route polyline

**Outcome: REPORT.** Instrument **not adjudicated** (its own controls failed); seat **valid and
negative**. Success required both, so no device build.

The ruling's stop-condition — *if the polyline can't key totally under the corner theorem, stop and
report before falling back to axis-smoothing* — **was not triggered.** It keys totally.

---

## 1. Built

`RoutePolyline` (Logic) and its Python twin. Routes come out of the level graph as **lines**:
Chaikin-smoothed to walking curvature, jittered perpendicular to the tangent and refused any push
that leaves walkable ground — discovered, not surveyed.

**Every existing lever re-keys to it.** Strength from distance-to-line, direction from the line's
tangent. No new visual treatment: the age layer ships as it was and concentrates along the line.
Worn, not built — the polyline is keying, never paving.

**It keys totally.** Distance to a polyline and its tangent are pure functions of a *world*
position, so two tiles sharing a stone compute the identical answer for the identical pixel.
`UNADDRESSABLE 0`, K still RUNTIME — the corner theorem is satisfied with no keying table, because
nothing per-tile is left to disagree about.

## 2. The number the ruling asked for

| | |
|---|---:|
| round 21, per-tile field | **34%** |
| round 22, straight synthetic control | **100%** (51 of 51) |
| round 22, the review scene | **79%** (26 of 33) |

The scene's residual 21% is where the route **genuinely turns** — room A's fan into the chokepoint,
and the chokepoint's arrival in room B. A route that turns must change axis at the turn; that is
not incoherence.

The engine now logs the axis map and its coherence every boot, and the route-strength map beside
it. Round 21's finding was a number nobody had measured; it is on the log now so the next reader
does not have to think of it first.

**One correction inside the round:** nineteen lines flooded the scene — every remote leaf became a
line, every tile was near *some* route, adjacent tiles were nearest to *different* routes, and
coherence read 70%. Restricted to spine and real routes, as the ruling specifies (portal-to-portal
plus spine), the map shows one channel with ordinary floor flanking it — which is what §8.2.1 asks
for and what the field never gave.

## 3. Two defects the instrument exposed in itself

**A null draw that scored zero was being given a free pass.** A rearrangement can pair a tile with
itself; ΔE comes back 0.000 and drags the median down, handing the real reading a win. Zero-draws
are now discarded — the same rule as the draws that raise, wearing a number instead of an
exception.

**The verdict did not respect the controls.** `MATCHING LEAKS` was printed and then `THE SIGNAL
CLEARS THE FLOOR` was printed under it. The controls now bind the verdict, which is why this round
reports `NOT ADJUDICATED — CONTROLS FAILED` instead of a pass.

**And the measurement was bucketing by the wrong population.** The keying moved to the line; the
instrument was still bucketing by the per-tile field. Aligning it — the engine logs route strength,
the instrument prefers it — is what made the honest failure visible:

```
  1. big enough to see:   ΔE  7.567  vs floor  5.132      PASS
  2. it is the PATH:      ΔE  7.567  vs null  14.271      FAIL
  CONTROLS FAILED — the verdict below is withheld, whatever the numbers say.
```

Measure what is keyed, or measure nothing.

## 4. The seat: valid, and negative

Plant caught. The answer:

> *"I read it off the walls and off the shape of the lit area — **the ground surface told me
> nothing.** I want that recorded clearly, because the question is asking whether ground that is
> walked daily looks walked, and the answer is no. The corridor floor is the blankest ground in
> the image."*

And, specifically: *"No polish down the centre. No grit pushed to the walls. No dishing where feet
land."*

## 5. A claim I tested and could not support

The seat's cull reads as a structural indictment: *"The floor is blank exactly where the lamp
lights it; all its detail hides in the dark."* If true it would be the finding of the session —
every lever built here is **subtractive** (flattening, compaction, smoothing all remove), the
player carries the lamp and stands on the route, so the lamp would always be over the emptiest
ground.

**Measured across the three stations, inside the lamp's pool, it is false at tile scale:**

| route strength | tiles | illumination | detail energy |
|---|---:|---:|---:|
| off-route 0–1 | 31 | 84.5 | 7.275 |
| shoulder 2–4 | 6 | 105.2 | 11.859 |
| near line 5–6 | 5 | 89.6 | 8.080 |
| **on the line 7–9** | 8 | 87.5 | **8.912** |

Detail on the line is **1.22× the off-route detail** — *more*, not less. And the correlation between
illumination and detail energy inside the pool is **+0.772**: the better lit a tile is, the *more*
there is on it.

The seat's own numbers (0.051 and 0.038 against a chamber mean of 0.15) are for two specific slab
faces, not the floor. Its perception is real and its structural explanation does not hold, and the
distinction matters because the explanation is what a next round would have been built on.

## 6. The illumination and the axis, named

**Illumination: 36% of full**, the population round 18 established and this round did not change.

**Axis: amplitude, on a signal that is now present and coherent.** This is a different failure from
every round before it, and the difference is the round's result:

- the signal *is* keyed to a real line (79% coherent, 100% where the route is straight);
- the signal *is* present on that line (1.22× the off-route detail, in the right direction);
- the signal *is not* large enough for a viewer to route by, and the instrument cannot certify what
  size it is because its controls fail at this sample.

The seat names three treatments it expects and does not find, and all three are **additive** —
polish down the centre, grit driven to the wall edges, dishing where feet land. Two of them exist
in the build (the polish shader, and hollows at thirteen mouths) and neither reached the ground the
seat was standing on. That is the first concrete, unexplored gap this session has produced that is
neither amplitude-of-an-existing-lever nor a keying problem.

## Evidence

| | |
|---|---|
| round 22 seats, both arms, VALID | `evidence/seats/SEATS-r22.json` |
| pooled path signal, not adjudicated | `evidence/PATH-SIGNAL.json` |
| axis map, coherence and route strength | `evidence/r18_approach.log` |
| fourteen field plants, all firing | `evidence/ASHLAR-FIELD.json` |

Shipped path identical on **four** arms — a route arm was added, and it is not vacuous: the declared
route changes 61.5% of the floor. `paint_check=96/OK`, `lines=1`, `mouths=13`, `polished=74`,
`UNADDRESSABLE 0`, fast suite 2510/0.
