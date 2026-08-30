# Round 23 — the additive layer

**Instrument: PASS, with every control binding.** **Seat: negative — and it examined ground the
route does not touch.** Success required both, so **no device build**.

The axis is named in §5, it is a scene finding rather than a lever finding, and **no lever was
retuned** — the ruling forbids retuning off a seat's explanation, and nothing here justified it.

---

## 1. Built — three levers, all keyed to distance-from-line and tangent

| lever | what it is |
|---|---|
| **the specular lane** | the polish shader re-keyed off the **line** instead of the noise-frayed field. Width from line distance, so the lane runs continuous down the centre; streaks laid in a coordinate perpendicular to the tangent, so they run *along* it, floored to whole pixels (§4.3 forbids the anti-aliasing a smooth stripe needs) |
| **dishing along the line** | shallow, deepest on the centre-line, gone by the shoulder, with the rim shadow a real recess implies. The threshold hollows are untouched and compose on top |
| **margin grit** *(new)* | debris swept off the centre and left at the flanks. Keyed on world position and line distance, never on a tile — §8.3.1-legal by construction, field-scale like the crack network. **The contrast between swept and unswept is the signal, not the grit** |

The unfrayed width is the point of the first one: the wear scalar is traffic *frayed by noise*,
which is right for age — a path's edges should break up rather than end on a pixel — and wrong for
a lane. A specular streak chopped into noise cannot be followed.

## 2. The instrument passes, and every control binds

| | round 22 | round 23 |
|---|---:|---:|
| **ΔE2000, pooled and matched** | 7.567 | **16.118** |
| ruled floor | 5.132 | 6.055 |
| null, median of four | 14.271 | 9.596 |
| condition 1 — big enough to see | PASS | **PASS** (2.7×) |
| condition 2 — it is the path | FAIL | **PASS** |
| controls | **FAILED** | **all pass** |

**Three instrument defects fixed to get there, and none of them by loosening a threshold:**

- **The pairing is now fixed once, on the shipped arm, and reused by every other arm.** Both
  controls broke at once when the signal got large, for one reason: a plant *changes* the tiles and
  matching-on-luminance then *re-pairs* them. A control must perturb one thing; re-deriving the
  pairing under the plant perturbs two.
- **The absorbed control became an exposure control.** Its premise — that a lightness-only plant
  is swallowed by the matcher — was only true *because* the matcher re-paired. Its purpose
  (*prove these readings are not illumination*) is preserved by dimming the **whole frame**, which
  changes the light and nothing else.
- **Membership is fixed on the unplanted frame.** The lit mask already was; the pool filter was
  not, so dimming pushed tiles out of the sample and the exposure control reported a leak that was
  its own doing.

## 3. The additive layer reaches the delivered frame, emphatically

Same station, three levers nulled, differenced, lamp-lit tiles only:

| route strength | tiles | pixels changed | mean delta | max |
|---|---:|---:|---:|---:|
| **on the line 7–9** | 4 | **66.0%** | **65.2** | 96 |
| shoulder 3–6 | 4 | 64.2% | 74.3 | 118 |
| off-route 0–2 | 10 | 3.9% | 15.1 | 28 |

Two thirds of the on-line pixels move, by a mean of **a quarter of the 8-bit range**, and off-route
ground is almost untouched. Whatever else is true, the treatments are there and they are where the
line is.

## 4. The seat: valid, negative

> *"**No. The ground told me nothing.** I read the corridor off the walls… Same slab module, same
> joint value, same blank faces, same absence of dirt or polish. I ran the mark-density measure on
> the corridor thinking I'd found something at 9.7% — magnifying and brightening it showed that
> number was the lamp falloff gradient, not marks."*

## 5. The axis: **the seat examined ground the route does not touch**

The banked law says a seat's percept is evidence and its explanation is a hypothesis. So before
naming anything, the route was mapped to screen pixels at the station the seat judged:

| tile | strength | screen box | median lum |
|---|---|---|---:|
| (5,4) (5,5) (5,6) | *** %%% @@@ | x 151–215, y 251–443 | 6.6 / 7.4 / 10.5 |
| **(6,7) (6,8) (6,9)** | **@@@ %%% *** ** | **x 215–279, y 443–635** | **89.5 / 111.0 / 92.8** |
| **(7,9)** | **%%%** | **x 279–343, y 571–635** | **201.9** |
| **(8,10)** | **\*\*\*** | **x 343–407, y 635–699** | **143.2** |
| (8,11) … (8,14) | %%% *** %%% +++ | x 343–407, y 699–955 | 63.0 → 7.4 |

**The seat cited its route as x 370–440, y 250–430.** At those coordinates the route strength is
**zero** — the route at that height is over at x 151–279. It described the room's centre-north,
called it "the corridor", and correctly found nothing on it, because there is nothing on it.

The route's *lit* portion at this station is a **five-tile diagonal** running (6,7) → (6,8) →
(6,9) → (7,9) → (8,10), in the room's west-centre. The corridor the seat's eye was drawn to — the
one the walls announce — runs down the frame's bottom edge, where the lamp has already fallen to
63 and then to 7.

**So this is a scene finding, not a lever finding.** And it is the second station to be wrong for
the question it was asked: round 18's chokepoint is one tile wide and has no flank to contrast
against; round 23's approach puts the route's lit run off to one side while the wall-legible
corridor sits at the frame's edge in the dark.

## 6. What follows, and what does not

**Does not:** any retune. The levers are not shown weak — they are shown large, correctly placed,
and unexamined. Retuning off this seat's report would be exactly the move the standing law forbids.

**Does:** a station whose **lit** route runs through the frame's centre, so the ground the question
is about is the ground the eye lands on. Every capture so far has been composed around the player's
position rather than around the route's visible portion, and those are not the same thing when the
lamp is carried and the route is diagonal.

## Evidence

| | |
|---|---|
| round 23 seats, both arms, VALID | `evidence/seats/SEATS-r23.json` |
| pooled path signal, controls binding | `evidence/PATH-SIGNAL.json` |
| the no-additive attribution arm | `evidence/r23_approach_noadd.png` |
| fourteen field plants, all firing | `evidence/ASHLAR-FIELD.json` |

Shipped path identical on four arms; `paint_check=96/OK`, `lines=1`, `mouths=13`, `polished=74`,
`UNADDRESSABLE 0`, fast suite 2510/0.

**Two order bugs were caught by the checks and not by me.** The route arm caught the additive layer
placed *before* the flatten in the mirror instead of after it — 2079 pixels, both arithmetically
correct — and the paint check caught the manifest emitted through the pre-fix mirror. Flatten is a
proportional pull; dish and grit are fixed subtractions; sequence is load-bearing. A third was a
crash rather than a disagreement: the `uniform_wear` plant skips the block where the line geometry
was defined, and the plant run died after eleven of fourteen, which read as *"three plants went
silent"* until the traceback was found. **A plant runner that crashes is not a plant runner that
failed.**
