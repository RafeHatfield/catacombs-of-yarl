# Round 26 — the sheltered joint draws its depth

**The merge gate is green on the laid field.** The keyline is gone, #161's spread is kept, and the
two-tier discrimination test did its job on its first outing — which is how it exposed something
about the seats that invalidates the last four rounds' verdicts about *specific ground*.

---

## 1. Targets declared before the round, then hit

| metric | shipped | pre-#161 | **target** | **measured** |
|---|---:|---:|---:|---:|
| p50 — the mode | 0.5457 | 0.2952 | **< 0.144** | **0.1072** |
| mean Weber | 0.5099 | 0.2722 | ≤ 0.28 | **0.1421** |
| share above the floor | 96.2% | 89.6% | ≤ 45% | **41.5%** |
| bottom-two-rung share | 92.7% | — | ≤ 30% | **17.2%** |
| joint spread | 5.02 | — | ≥ 4.5 | **5.02** |

**On the standing laid field** — the merge condition: `joint_contrast` share **66.6% → 20.3%**, mean
**0.2448 → 0.0515**; `constant_pitch` contrast **0.2653 → 0.0991**, `over_perceptual_floor: **False**`;
joint spread **5.024 rungs**, #161's exactly.

## 2. The lever

A sheltered joint no longer takes the one value handed to every joint in the world. It **draws** its
depth from four rungs — packed shut, the mode, a middle, and a deep tail — on a **coarse world
block**, so the depth varies *along* a joint's run rather than being constant on it. Per pixel would
be noise; per run would be the same defect at a smaller scale; a block is mortar. World-keyed, so
both tiles either side of a boundary draw the identical depth for the identical pixel —
`UNADDRESSABLE` stays 0. Route joints compact lighter on top, exactly as built.

**Two things the round found on its way, both by measurement:**

- **A joint brighter than its stone.** Lift plus fill, uncapped, put **2%** of joints *above* the
  stone they lie between — a joint that emits light, the inversion of *dark because enclosed*. Both
  are packings; both are now capped at the stone's own level. 0.00% remain.
- **The spread went, then came back.** The first table hit four of five targets and lost the spread
  (3.997 vs 5.024) because the cap cut off the tail carrying the width. Recovering it at the **light**
  end — a share packed shut — widens the distribution while *lowering* the mean and the share.

## 3. An instrument broke under the fix and said the wrong thing

`erosion_read` divided one depth-below-stone by the other — well-behaved only while every joint is
dark. The moment a share of joints packed shut, the denominator crossed zero, the metric reported a
grain of **−7,896,677**, and two plants went **SILENT** — which reads as *"the lever stopped
working"* rather than *"the instrument stopped being defined"*. It is a difference in rungs now.

New plant **`flat_joint_depth`** — every sheltered joint handed the same depth again, #161's defect
restored — **fires**. Fifteen of fifteen plants, the run asserting its count.

## 4. The law, recorded in the instrument itself

> **An instrument asks the ban's question, never the ban's last known form.** Four ring instruments
> were green while every stone was outlined, because all four asked about the *tile grid* — the
> shape the ring had the last time it was caught.

And `joint_contrast` reports a **distribution**, not a mean: a floor whose joints all sit just over
the floor and a floor with a shallow mode and a deep minority can share a mean and look nothing
alike.

## 5. The wall-scene candidate: **not confirmed**

`tier1_wall_review` does not exist in this worktree — it is on that session's branch. The nearest
wall scene here, `wall_face_review`, **has traffic**: `lines=1`, `spine:16/routes:5`. So *"its floor
reads right because zero traffic means the wear pass never fires"* **cannot be confirmed from here
and is not claimed.**

What *is* measured is the mechanism behind it: with no route model the wear scalar falls back to
noise and the joints keep its spread — share above the floor **66.6% against 96.2%**, mean **0.245
against 0.510**. A floor with no traffic model was always going to look better than one carrying the
wear pass as it was tuned. Whether that is what the wall session sees needs their scene.

## 6. ⚠ The discrimination test worked — and it caught the seats

Tier one produced exactly what it was built for: an **honest refusal** instead of an unfalsifiable
negative.

> **Q8B: NO BASIS.** *"I cannot mark it… Confidence: high that the signal genuinely isn't there,
> rather than that I failed to find it. I checked value, hue, saturation, joint width, and
> high-frequency texture separately, and all four are flat."*

**But it surveyed the wrong part of the frame, and so has every seat since round 23.** It reports
working *"across the whole lit room, x 310–750, y 0–272"* and places the corridor mouth at
**x 502–566, y 272–340**. Measured from the engine's own log, at this station:

| | the seat says | the frame actually has |
|---|---|---|
| corridor mouth (8,10) | x 502–566, y 272–340 | **x 343–407, y 635–699** |
| the lit route | — | (7,8) (7,9) (8,10) at x 279–407, **y 507–699** |
| the region it surveyed | x 310–750, **y 0–272** | above the lit floor entirely |

The offsets are not a uniform scale — up *and* right, by different factors — so this is not simply a
resized view. **Four valid rounds (23, 24, 26) have now returned confident, specific, measured
statements about ground that is not where they say it is.**

**Consequence, stated plainly: no seat verdict in those rounds is admissible as evidence about
specific ground.** Their *global* readings ("I checked value, hue, saturation and texture and all
four are flat") may still hold; their coordinates do not.

**The fix is an anchor, and it is cheap:** stop asking for pixel coordinates. Ask the seat to
describe positions **relative to the figure, in tiles** — *"two tiles south of the figure"* — which
is unambiguous under any internal rescaling, and score it against the route the same way. Proposed,
not implemented; the round was bounded.

## 7. State

- **Merge gate: green** — `joint_contrast` and `constant_pitch` both under §13.8's floor on the laid field
- shipped path identical on four arms, `paint_check=96/OK`, `UNADDRESSABLE 0`, fast suite **2510/0**
- device build **installed** under its own bundle id, **not verified** — the handset was locked
- round 26 **VALID**, plant caught
