# The keyline regression — diagnosis

**No new art. The finding is the joint's contrast against its stone, and the instrument set was
blind to it because every instrument built for the ring looked at the tile grid instead.**

---

## 1. Did the instrument fire? **No. It was blind to its own ban.**

Every ring instrument this campaign built asks the same question — *does a treatment sit at a
constant grid position* — and answers it about the **tile grid**:

| instrument | what it asks | on this build |
|---|---|---|
| `grid_hiding` | does the boundary line look different from the mid-tile line | 1.00 / 1.0012 — clean |
| `constant_pitch` | how many full-width joints sit at the tile pitch | 0.52 — unchanged for eleven rounds |
| `boundary_step` | is there a value step at the boundary | 0.48 — clean |
| `lattice` | is anything periodic with the grid | 0.118 — clean |

**None of them asks the question a person asks first: is every stone outlined.** The complaint is
*"outlined chips"* — the **stone**, not the tile. Eleven rounds of green instruments and a floor
that reads as a wireframe are both true at once, because nothing measured the joint.

**Added: `joint_contrast`** — the joint's median against the stone's, gated on §13.8's 0.144. It
discriminates cleanly:

| | joint | stone | Weber | × the floor |
|---|---:|---:|---:|---:|
| **shipped** | 75.0 | 114.0 | **0.342** | **2.38×** |
| before PR #161 | 101.0 | 114.0 | 0.114 | 0.79× |

With a route present, where more of the floor is off-route and joints sit deepest, the same
measurement reads **0.579 against 0.342** — 4.0× the floor against 2.4×.

`constant_pitch` also gained the amplitude term it never had: same count both ways (0.52), contrast
**0.1011 → 0.2006**. The count was blind; the amplitude is the discriminating term.

## 2. The bisect

**It is not the §12.1 overlay.** Captured the same scene with overlays on and off and asked where
the overlay's pixels land relative to the tile boundary:

| distance from tile edge | 0–1px | 1–2px | 2–4px | 4–8px | 8–16px | 16–32px |
|---|---:|---:|---:|---:|---:|---:|
| share of band changed | 27.1% | 27.2% | 27.9% | 28.1% | 29.2% | 27.3% |

Flat across every band, and only **15.1%** of its changes darken at all, by a mean of **6.7**. A
treatment at a constant grid position concentrates at the boundary and falls away. This does not.
The overlay is real geometry and is exonerated.

**It is the joint amplitude, driven globally.** The mechanism is the palette:

> PR #161 (`4e177b46`, *"two rungs below the donors — RULED"*) added rungs at **48.56** and
> **61.79**. It was ruled to give the sheltered joints somewhere to go, because they had all been
> clamping to one value — gate two's *"all the gaps look standardized"*.
>
> They went. A sheltered joint with somewhere darker to go gets **26 units darker**, and *off-route
> is most of a floor*. Measured: **87–91% of joint pixels now sit on the bottom two rungs.**

Round 22's polyline keying makes it slightly worse (87% → 91% of joints on the bottom rungs, grid
line 0.3038 → 0.3774) because a single line leaves more of the floor off-route than a smoothed
field did. **Round 23's additive layer contributes nothing to it** (0.3774 → 0.3749 with it off).

## 3. The honest gap in this diagnosis

**The known-good does not fully behave as the theory predicts, and I am not going to paper over
it.** The wall session's build (`e95e4246`) ships an *identical* nine-rung manifest — same ladder,
same bottom rung, same family:

```
wall session (e95e4246)    9 rungs, bottom  48.56, top 154.38
this worktree (HEAD)       9 rungs, bottom  48.56, top 154.38
```

So the ladder alone does not explain why that floor reads correctly and this one does not. What
*does* differ: it contains **neither round 22 nor round 23**, and it runs a different scene whose
traffic coverage puts a different share of its floor off-route. Round 22's contribution is measured
above and is real but small.

**Two candidates remain untested**, and both are cheap: whether `tier1_wall_review`'s traffic
coverage leaves materially less of its floor at the deepest joint state, and whether the comparison
is against that build or against an earlier memory. Neither changes what the joint contrast is; both
change how much of the difference PR #161 owns.

## 4. Five hypotheses, four discarded by measurement

Recorded because the discarded ones were each convincing enough to have been built on:

1. ~~the §12.1 overlay lands at tile boundaries~~ — flat across all bands, exonerated
2. ~~the additive layer leaks off the polyline~~ — 0.3774 vs 0.3749 with it off
3. ~~raising the authored joint depth fixes it~~ — costed at 0.55/0.62/0.70: **0.1980 / 0.1954 / 0.1953**, no
4. ~~the polish shader rings each tile through mask edge-sampling~~ — the border measures *brighter*
   than the interior on polished builds (−2.9%, −4.9%), the opposite signature
5. **the joints are simply too dark, everywhere the route is not** — 0.342 → 0.579 Weber

I mis-scoped this for four of those five: I searched for a **tile-grid** keyline because that is
what the campaign has banned, and the aggregate grid metrics kept coming back at ~1.00. The frame
settled it in one look — every *stone* is ringed. The metric that finally moved was the one nobody
had written.

## 5. Options, costed — none applied

| option | grid line | joint spread | verdict |
|---|---:|---:|---|
| **A. as shipped** | 0.2006 | 4.01 | KEYLINE |
| **B. revert the two rungs** | **0.1011** | 1.97 | **clean** |
| C. keep 9 rungs, raise authored joint depth to 0.70 | 0.1953 | 4.01 | KEYLINE |
| D. keep 9 rungs, clamp joints off the bottom two | 0.1780 | 2.95 | KEYLINE |

**Only B clears, and B costs exactly what the rungs were ruled to buy** — joint variation falls
4.01 → 1.97 rungs, and gate two's *"all the gaps look standardized"* comes back with it.

That tension is the ruling, and it is not mine to make. The two rungs were also bought for §6.5's
**wall face**, which needs 48.56–61.79 and cannot be authored without them — so B costs the wall
session something too, unless the rungs stay in the palette and leave the joints alone, which is D,
which does not clear.

## Evidence

Instruments added: `joint_contrast`, and the amplitude term on `constant_pitch_lines`. Fourteen of
fourteen plants still firing and the run asserting it. Nothing else changed; no lever retuned, no
art regenerated.
