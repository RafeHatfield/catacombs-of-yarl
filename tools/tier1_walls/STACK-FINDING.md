# The stack does not survive the falloff — §6.2.1's owed measurement, answered

**Instrument:** `tools/tier1_walls/light_field.py`, `range_profile.py`, `solve_authored_stack.py`.
**Evidence:** `evidence/LIGHT-FIELD-CONTROLS.json`, `RANGE-PROFILE.json`, `AUTHORED-STACK.json`,
`STACK-DERIVATION.json`. **Rig:** the ratified one — radius 5.0 / falloff 1.00 / ambient 0.70 /
energy 1.6 (Ruling 56), passed explicitly, echoed into every capture log.

Ruling 56 ratified the Boundary's rig and recorded, inside the clause, the one thing its pass
could not answer:

> *"The §6.5 stack surviving the falloff across the lit radius — **NOT ANSWERED, and it could not
> be** … Whether the value stack survives this falloff is owed by the first round that puts real
> walls in the scene."*

This is that round, and the measurement was taken **before** a wall pixel was authored, because
the answer decides what there is to author.

---

## 1. What was measured, and why it can be believed

Godot's 2D pipeline is **exactly multiplicative in albedo** — measured, not assumed: the same
scene at albedo 101 and 202 returns a ratio of **0.5000** with a worst-cell error of **0.0006**
over 38 cells. So a capture of a scene painted one flat albedo *is a picture of the lighting
multiplier L*, and every compression factor in the wall recipe is an L-ratio between two
positions.

Four positive controls, all green, and the third exists specifically to show the second can fail:

| control | result |
|---|---|
| **LINEARITY** — albedo 101/202 must return 0.5 everywhere | **PASS** 0.5000, worst 0.0006 |
| **UNITY** — at energy 0 the two planes must not separate at all | **PASS** exactly 1.00000 over 81 wall cells |
| **UNITY-FAILS** — the same statistic with the lamp on | **1.43349**, worst 0.45 from 1.0 — the instrument discriminates |
| **DARK-CELL** — `DarkFloorModulate` on wall-adjacent floor | **PASS** 0.9280, divided out of every pairing |

Two traps were found by the controls going red rather than by inspection, and both are recorded
in the code: **clipped pixels** (the bright probe drives channels to 255 beside the lamp and the
ratio bends toward 1 — the first linearity run read 0.522 there) and **translucent interface**
(the zoom buttons, the RIG panel and the Msg button are drawn *inside* the dungeon view; a pixel
under a panel still moves with albedo and moves by the wrong proportion — the unity control
failed on exactly four cells, every one of them under a panel).

## 2. The compression field

Isolated wall blocks at rows 1–4 north of the player, each with floor on all four sides, each
paired against **the floor cell it faces**:

| row | L(top) | L(face) | L(floor faced) | **k_top** | **k_face** |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.9583 | 1.0542 | 1.1033 | **0.8686** | **0.9555** |
| 2 | 0.6709 | 0.8220 | 1.0018 | **0.6696** | **0.8204** |
| 3 | 0.3567 | 0.5084 | 0.7432 | **0.4799** | **0.6840** |
| 4 | 0.1290 | 0.2226 | 0.4307 | **0.2995** | **0.5169** |

Rows 5–7 return **no sample at any albedo** — past four tiles there is not enough signal left in
eight bits to form a ratio, which is the delivered-reach note in §6.2.1 arriving from a second
direction.

**k_top is below 1.0 at every range and cannot be otherwise.** The player carries the lamp, so
the floor a wall faces is always nearer the light than the wall's own top plane — by one tile
plus the half-tile the top band sits back inside its own cell.

## 3. The finding

**§6.5 makes two claims, and this rig keeps one of them.**

**The 2:1 plane separation survives.** Authored top 154.38 / face 75.02 delivers face ÷ top of
0.44 – 0.69 across the reach, mean ≈ 0.55 against §6.5's 0.53. The relationship between the
wall's own planes is deliverable and is not in question.

**"The floor sits BETWEEN the planes" does not survive.** For the wall top to deliver 1.11 × the
floor it faces, it must be authored at:

| range | authored value needed | on the nine-rung ladder? |
|---:|---:|---|
| 1 tile | 129 | yes — rung 6 (127.92) |
| 2 tiles | 168 | **no — above the top rung** |
| 3 tiles | 234 | **no — near the 8-bit ceiling** |
| 4 tiles | 375 | **no — not expressible** |

At the ladder's top rung the delivered top ÷ floor runs **1.33 / 1.02 / 0.73 / 0.46** by range.
At pure white it still fails by four tiles (0.755). **No authorable value puts the wall top above
the floor across the lit radius**, and the inversion arrives at three tiles — inside the room the
gate scene is built from.

§6.2.1's own words about the sighted round apply to §6.5 itself now: *"a value law that only
holds within two tiles of the lamp is not a value law, it is a vignette."*

## 4. The pairing is not the artefact — and it does change the size of the problem

Sampling the floor **at the wall's own range** instead of at its foot:

| row | k_top | k_face |
|---:|---:|---:|
| 1 | 0.9566 | 1.0522 |
| 2 | 0.9026 | 1.1059 |
| 3 | 0.8281 | 1.1802 |

Still below 1.0, for the residual half-tile — but only just, and under this reading §6.5 *is*
reachable: top ≈ 125 (rung 6, 127.92), face ≈ 55 (rung 0, 48.56).

**So the clause's status depends on which floor a wall is judged against, and the two readings
disagree by a factor of two in k_top.** The local pairing is the one the eye makes — you compare
a wall to the ground at its foot — and it is reported as the primary. The equal-range pairing is
the material reading, and it is reported because a measurement that supports only one reading of
a clause should say which reading it measured.

## 5. Status — RULING TRIGGER, and what this session did with it

This is a **§6.2 coupling finding, not a tuning task**, and it is returned under LOOP-PROCESS
§1.1.4(b) — an amendment to something frozen. Nothing here was tuned around, and no number was
picked to make the problem go away.

What the session did instead of stopping: **the two readings are built as two arms and taken to
the gate**, which is where §13.2 says the answer lives.

| arm | wall top | wall face | authored face ÷ top | reading |
|---|---:|---:|---:|---|
| **A — material** | 114.70 (rung 5) | 61.79 (rung 1) | 0.539 | §6.5's ratios as **albedo**. No rig baked in, best §6.3 hygiene. |
| **B — compensated** | 154.38 (rung 8) | 75.02 (rung 2) | 0.486 | §6.5's ratios as **delivered**, solved as far backwards as the ladder allows. |

Three honest remedies exist and none is this session's to choose — all three are named in §6.2
already:

1. **Restate §6.5 as an authored (albedo) law.** Its register derivation is material — *the floor
   is dark because it is used, the wall top is light because nothing has touched it* — and a
   material law has no business being stated in delivered luminance under a moving lamp.
2. **Move the rig.** §6.2.1's own instruction: *"the rig is one table of numbers and the corpus is
   every asset in the game. Tune the cheap thing."* A flatter falloff or a wider radius lifts
   k_top directly. Ruling 56 ratified the rig by eye on the device, so this is a re-gate.
3. **A light-response clamp on wall tiles in the renderer** — named in §6.2 as an honest option
   and never costed.
