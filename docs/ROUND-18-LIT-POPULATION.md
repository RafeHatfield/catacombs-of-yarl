# Round 18 — the corrected population, the polish lever, and what the seat found instead

**Outcome: REPORT, not closure.** The ruling froze that: *failure at budget → report; any future
closure must name the lit illumination it failed at.* This one is named in §5 below.

Ruling 70's execution was voided at the gate by §13.9's own second consequence — the closure named
the wrong illumination. §13.9's physics stands; the closure drawn from it is retracted. What
follows is the channel re-tested on the population it should always have been tested on.

---

## 1. What was corrected

**The capture protocol.** Three player-centered traversal stations, the player standing *on* the
route with the route inside the lamp's delivered pool, plus the lit-room capture. Geometry, carve
list and mocked walls identical to `tier1_floor_review.json`, so every comparison through that spec
stays valid.

| station | player | what it poses |
|---|---|---|
| `approach` | (8,8) | room A's south end, chokepoint mouth two tiles ahead |
| `chokepoint` | (8,12) | one tile wide — §8.2.1's "polished wall to wall" |
| `roomb` | (8,16) | where the route arrives; ground §8.2.1 itself notes "exists for the walked device review, not for the headless one" |

**The measurement.** Tiles compared only where the lamp reaches (delivered ≥ 60), pooled across
stations, matched in luminance pairs — the lamp controlled by *matching* rather than by a division
that could swallow the lane.

**The design ruling recorded with it:** the path is built for **lit legibility**.
Player-as-light-source is the normal case, some corridors will carry fixed light later, and **dark
illegibility is accepted by design.** The seat is now told not to judge ground beyond the light.

## 2. The new lever: polish as light response

A trodden stone reflects more, and reflection is a response to light rather than a property of
pigment. The distinction the ruling drew is enforced in code, not asserted in prose:

- **Banned, still (§8.2.1): baked value-lift.** Under a multiplicative rig, `(albedo + d) × (ambient
  + light)` spends its delta at every illumination in the room — including the dark, where nobody
  is — and reads as wear that was drawn on.
- **Legal: engine response modulation.** A new `canvas_item` shader — the first in this codebase —
  touches **only** the `light()` pass. A polished stone and a rough one are the same stone in the
  dark, and the difference grows *faster than linearly* with the light actually delivered.

The engine **refuses to lay the floor if `polish_exp ≤ 1.0`**, because at exactly 1.0 the specular
term is linear in delivered light and the lever *is* the banned one wearing this one's name.

**Measured — it is a light response, not a coat of paint.** Plant: null the reflectivity table and
recapture. 49,257 pixels differ, max channel delta 113, and the delta lands where the lamp does:

| delivered value at the pixel | mean delta |
|---|---:|
| 0 … 20 | 0.22 |
| 20 … 40 | 4.83 |
| 40 … 70 | 4.89 |
| 70 … 110 | **7.85** |

**36× more delta in the lit band than in the dark one.** A baked lift would be flat across every row.

## 3. The instrument, on the corrected population: it clears

| | |
|---|---:|
| pairs | 6, matched to 2.59 luminance |
| lightness alone | 0.961 ΔE2000 |
| **lightness + colour** | **13.414 ΔE2000** |
| the ruled floor (§13.8 converted) | 4.767 → **clears by 2.8×** |
| the null control, median of 4 draws | 3.199 → **passes condition 2** |

Both conditions pass, and the sample now meets the null's minimum of five, so the control
**adjudicates** rather than declining as it did on the wrong population. Plant caught (13.414 →
22.591); the absorbed control is swallowed by the matching, as its design requires.

For comparison, the scene-wide capture that closed the channel read **5.512 against a floor of
6.981** and failed both conditions. The correction is worth 2.4× on its own.

**Attribution of the polish lever, measured rather than claimed:**

| | with polish | without |
|---|---:|---:|
| trodden tiles' median delivered luminance (approach) | **21.6** | 15.1 |
| trodden tiles inside the readable band (≥60) | 1 of 8 | **0 of 8** |

Pooled over two stations the unpolished arm has *no* trodden ground inside the pool at all, so the
comparison cannot even be formed — the attribution result in its strongest form: **the polish lever
is what puts trodden ground into the band where anything can be read.**

## 4. The seat: the ground still told it nothing

Round 18 is **VALID** — the plant seat culled the planted floor (`hole`, `crater`).

> **Q9** — *"The route runs north–south, and **I read it entirely off the walls.** The ground told me
> nothing."*

And the reason it gives is not amplitude. It is **form**:

> *"There is no directional grain, no lengthwise slab, no kerb, no drain line, no centre track,
> nothing that runs* with *the corridor. The one place the ground had an obvious job to do is the
> mouth at (370–445, 395–415): the floor crosses from one-tile passage into open room and does not
> change by a single pixel. Same stone, same course height, same joint colour, no sill, no lip, no
> threshold slab."*

**This is a different complaint from every previous round.** Rounds 11–17 were told the signal was
too small. This one is told the signal is the wrong *kind*: every lever tried — joint travel,
palette reach, chroma, polish — is a **per-pixel modulation of the same stones**. None of them
changes the floor's **form**. A path is read from directional geometry: coursing that turns to run
with the corridor, a threshold slab at a mouth, a kerb, a narrowing. The floor has no such
vocabulary, and no amount of modulating the stones it does have will supply one.

## 5. The lit illumination this round measured at — named, as the ruling requires

| station | trodden ground compared, median delivered | off-route |
|---|---:|---:|
| approach | 89.7 / 255 (35%) | 84.2 |
| room | 100.3 / 255 (39%) | 79.0 |
| roomb | 89.1 / 255 (35%) | 69.0 |
| **pooled** | **92.5 / 255 — 36% of full** | |

The capture that closed the channel compared trodden ground at **7.1 / 255**. This round's
population is thirteen times better lit, and the seat's answer did not change.

**So the finding is stated at its illumination:** at 36% of full light, on ground the reader is
standing on, with joint travel, chroma and polish all live and all measurable, **the floor does not
state its route** — and the reason the seat gives is the absence of directional form, not the size
of the material signal.

## 6. A process defect, recorded because it nearly cost the round

Round 19 (`roomb` station) is **VOID** — its plant seat did not catch the plant, so its findings are
not read and are not used anywhere in this document.

**I read that round's family transcript before its plant verdict returned.** The seats run in one
job, family first, control second; nothing stopped me looking at the first while the second was
still running, and nothing in the transcript says "not yet admissible". §4 exists precisely to stop
a finding entering the record before its control clears, and reading early defeats it whatever I do
afterwards.

**Correction owed:** `run_seats.py` should withhold every transcript until the plant verdict is in,
and stamp VOID rounds' transcripts so a later reader cannot mistake them for evidence. Filed here
rather than fixed inside a round that is already reporting.

## 7. What this leaves

- **The channel is not closed.** The ruling withheld that, correctly: this is a report.
- **The levers ship and are not wasted.** Joint travel, the nine-rung ladder, chroma and polish are
  all live, all measured, all above the floor at lit illumination. They give the floor differential
  age, which passed its own gate three walks ago.
- **The successor is named by the seat, not by me:** directional form. Coursing that runs with a
  corridor, a threshold slab where a passage meets a room, a kerb, a narrowing — geometry rather
  than material. That is a change to the *bond*, which is the one thing every round so far has held
  frozen.
- **No device build.** Success was defined as the combined signal reading on the corrected captures
  *and* the seat reading the path. The instrument cleared; the seat did not.

## Evidence

| | |
|---|---|
| round 18 seats, both arms | `evidence/seats/SEATS-r18.json` |
| round 19, VOID | `evidence/seats/SEATS-r19.json` |
| pooled path signal, plant + absorbed + null | `evidence/PATH-SIGNAL.json` |
| the four corrected captures | `evidence/r18_approach.png`, `r18_choke.png`, `r18_roomb.png`, `r18_room.png` |
| the polish attribution arm | `evidence/r18_*_nopolish.png` |
| the shader | `src/Presentation/assets/shaders/tier1_polish.gdshader` |
