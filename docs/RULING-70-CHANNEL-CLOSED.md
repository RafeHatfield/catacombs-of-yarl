# Ruling 70 executes — the trodden channel closes, and the reason is not the one we predicted

**Step three of the pre-declared fallback ladder, fired 2026-08-29 after round 17.** The ladder
was frozen before rung one ran: *joints → #159 chroma → Ruling 70 accepts the channel as
expression-impossible, wear ships as ambience only.* All three rungs are now discharged with
measurements, and the third one changed what the ruling should say.

Round 17 is **VALID** — the plant seat culled the planted floor and hit the ruin vocabulary.

---

## The verdict

The blind seat, on the lit scene, to the standing question *"where would you walk — does the floor
already know?"*:

> **"The ground told me nothing. I routed entirely off the walls."**
> *"I compared the crossing at x 300 y 240 with the dead southeast corner at x 600 y 360 and the
> only difference is lantern falloff. If I lit them equally they'd be the same floor."*
> *"Judged on the ground alone I cannot tell you which door the garrison uses daily and which one
> has been shut for a century. That information is not on this floor."*

Three rounds, three levers, the same sentence. **The channel closes.**

## The three rungs, and what each one cost to learn

| rung | what it did | why it was not enough |
|---|---|---|
| **1. the joints** | packed trodden joints with grit, up to two rungs and 45% level with their stones; joint age spread 0.983 → 2.992 → **5.024 rungs** | **structural.** Joints are 21.85% of the surface. At the *physical ceiling* — every trodden joint level, every sheltered one at the deepest rung — the lever is worth 0.1253 Weber against §13.8's 0.1440. No setting reaches it. |
| **2. the palette** | two rungs below the donors' band, 48.56 and 61.79 — because the sheltered joint the bond authored at 47.8 had been clamping to 75.02 all along | it restored the joints' variation and made a wall face authorable. It lifted the ceiling 0.0745 → 0.1253. **It was never ruled to close the channel and it did not.** |
| **3. chroma** | a constant-luminance rotation toward cool grey-green on stone faces only, traffic-keyed; **11.25° of delivered hue shift** against 0.05° before it | the instrument says it clears the floor. The seat says the ground told it nothing. |

## Why rung three failed, which is not what rung three was expected to fail on

The chroma lever was chosen because **a ratio between channels survives a multiplication that an
authored value difference does not.** That reasoning is correct and the lever delivers: measured on
the raw capture, trodden stone sits 11.25° of hue from sheltered stone, where the pre-chroma build
measured 0.05°.

It does not survive **quantisation**. Measured on the shipped frame at the tiles the level's own
traffic field calls busiest:

| illumination | the whole nine-rung ladder becomes | the full chroma rotation moves |
|---|---|---|
| full | 8-bit 49 … 154 | rgb(115,115,114) → rgb(103,122,113), **ΔE 10.12** |
| mean trodden tile (24.3/255) | 8-bit 5 … 15 | rgb(11,11,11) → rgb(10,12,11), **ΔE 1.06** |
| **the busiest tile (7.1/255)** | **8-bit 1 … 4** | **rgb(3,3,3) → rgb(3,3,3), ΔE 0.00** |

**At the one tile the level walks most, the entire palette collapses to four 8-bit values and a
rotation worth ten ΔE at full light rounds to nothing.** 87% of the laid floor sits below luminance
70, and the trodden tiles are *darker* than the off-route ones — 24.3 against 30.7 — because
corridors are where traffic concentrates and corridors are where the lamp is not.

The seat found this independently and stated it as a flip: *"Add surface texture that survives the
lighting: it currently multiplies to zero past ~100px from the lantern (measured std 1.24)."*

## The ruling, amended by its own evidence

> **RULING 70 (executed).** The §8.2.1 trodden channel is **CLOSED**. Wear ships as ambience: it
> gives the floor its age, and it does not tell the player where to walk.
>
> **The reason is not "expression-impossible at 32px."** It is that no authored surface
> material — value, texture *or* colour — survives delivery at the illumination where this game
> draws its paths. Corridors carry the traffic and corridors are unlit; the rig multiplies every
> channel by the same falloff, and 3% of a palette is four values wide.

Recorded as bible **§13.9, the representable floor**: a signal is absent if the rig does not
deliver enough of it to be represented, and an instrument that measures the source has not measured
the asset.

## What is NOT closed

- **The keying.** Confirmed at the third walk and never in doubt since: wear is a property of
  traffic, derived from the level graph, weighted by structural importance, sealed rooms at zero.
  `TrafficField` and its seven tests stand. What closes is the *expression*, not the derivation.
- **The lever set.** Joints, chroma and the nine-rung ladder all ship. They give the floor
  differential age, which passed its own gate in kind, and they cost nothing.
- **The channel, at full illumination.** The same chroma rotation is worth ΔE 10.12 in the lit
  half of a room. §13.9's second consequence binds here: *a channel cannot be ruled impossible from
  one scene.* If a later region lights its corridors, this reopens on evidence.

## The successor, named so it is not rediscovered

If a floor must state its route, the signal cannot be surface material under this rig. It has to be
something the falloff does not multiply — geometry that breaks the silhouette, an object, a change
of plane — or the ambient floor has to rise. **Both are wall-and-rig questions, not floor
questions**, and the wall session is where they land.

---

## The measurement trail

| evidence | where |
|---|---|
| round 17 seats, both arms | `tools/tier1_floors/evidence/seats/SEATS-r17.json` |
| delivered path signal, ΔE2000 with plant, absorbed control and null | `tools/tier1_floors/evidence/PATH-SIGNAL.json` |
| the palette's reach and the joint lever's ceiling | `tools/tier1_floors/evidence/LADDER-REACH.json` |
| the field's twelve plants, all firing | `tools/tier1_floors/evidence/ASHLAR-FIELD.json` |
| shipped-path identity on three arms | `tools/tier1_floors/evidence/ATLAS-PATH.json` |
| the captures the seats judged | `scene_ashlar_r17.png`, `scene_ashlar_plant_r17.png` |

**Instrument controls at the close.** The plant (trodden tiles rotated 15% toward green) is caught,
6.756 → 13.744. The absorbed control (trodden tiles darkened 20%) is swallowed by the luminance
matching, as that design requires — if a lightness-only plant moved the number, every reading would
be part illumination. The null control **declined to vote**: two trodden tiles is below its minimum
of five, its draws span 8.57 to 15.45, and on a floor that genuinely carries a cast a rearranged
labelling resamples that signal rather than removing it. It is reported and not used.

**The instrument said CLEARS and the seat said no, and both are right.** ΔE2000 between
luminance-matched tiles measures whether two patches *differ*; it does not measure whether a viewer
can *follow* one across a room in the dark. §13.1 has always held that the human gate is final and
§13.4 that register conformance is never instrumented. This is the first time an instrument and a
seat have disagreed with the seat winning on a signal the instrument could see — and the reason,
found afterwards, is that the instrument was comparing tiles pairwise while the seat was being
asked to read a route.
