# The grey walls — bisect against the build Rafe approved

**Gate verdict: FAIL.** *"Grey walls and ceiling; it looked better a few versions ago."*
Ruled cause: *"the same-quarry hue ruling was never built — the build carries the raw grey
material arm."*

Same discipline as the floor's keyline regression: name the approved build, list everything that
changed since, and say which change owns the defect and which are exonerated.

---

## The approved build

**`0c60bc50`** — *"the review scenes were dead for a reason the audit guessed wrong"*, 2026-08-30.
Verified on device, walked, and the walk is where the material arm was approved: *"walls read as
their own stone, wall-vs-floor separation confirmed by eye."* That build had **warm faces**.

## Everything that changed since, and who owns the grey

Three commits touch the renderer or the composers between that build and the failing one:

| commit | what it changed | owns the grey? |
|---|---|---|
| `bceb7446` | **the cap pass** — the cap became a synthesised luminance field, and gained `hue_shift = 0.18` authored to make it *"the COOLER, GREYER surface"* | **YES — this is the one** |
| `72c5bd3a` | `void_ring: 0`, the ring outline; seat gate made structural | no — placement and process, no colour path |
| `f3f5a207` | cap to rung 3; §12.1 occlusion anchored to ambient | **contributory** — it moved the cap's *value* down 114.70 → 88.24, which darkens a surface whose chroma was already gone |

### The mechanism, measured rather than inferred

Both composers synthesise a **luminance** field and colourise it with the floor material's `tint`:

```
floor material tint = (1.0013, 1.0068, 0.9918)      saturation 0.015 — NEUTRAL
```

**The wall family was never given the floor's chroma at all.** It was given a field that looks
like colour and is a grey multiplier. The floor's own colour lives in its tile pixels, which the
floor family keeps and the wall family — built from a ladder — throws away.

So `bceb7446` did not *introduce* greyness so much as make it unmissable: the cap is the largest
surface in frame, and it arrived both neutral **and** deliberately desaturated by `hue_shift`.
Before the cap pass the tops were the wall family's own tiles — equally neutral, but a smaller
share of the picture and never described as a ceiling.

Delivered, in the judgeable band, before the fix:

| surface | hue | sat | vs floor |
|---|---:|---:|---|
| floor | 29.5 | 0.507 | — |
| wall cap | 57.1 | 0.280 | **+27.6°, 55% of the floor's saturation** |
| wall face | 42.3 | 0.306 | **+12.8°, 60%** |

**Both surfaces, not just the cap** — which is why the verdict names walls *and* ceiling, and why
removing `hue_shift` alone would not have fixed it.

### What is exonerated

- **`void_ring: 0`** — no colour path. The ring work is placement only.
- **The material arm itself** — it is a *value* choice (rung 5 → 3) and was approved as one. It
  is not the source of the grey; it only made a colourless surface darker.
- **The ambient-anchored occlusion** — it darkens a floor edge and touches no chroma.

---

## The fix, and what it is anchored to

`derive_quarry_tint.py` reads the floor family's own pixels and returns a **luminance-preserving**
chroma ratio, derived at consumption. A wall taking it changes hue and saturation and **not**
value — so the value work already landed survives untouched.

```
quarry tint = (1.0568, 1.0239, 0.5957)      tint . W709 = 1.000000
```

Delivered after the fix:

| surface | hue delta vs floor | saturation ratio |
|---|---:|---:|
| wall cap | **+1.6°** | **1.078** |
| wall face | **+4.8°** | **1.136** |

Against +27.6° / 0.553 before. `hue_shift` ships at **0.0** — kept as a knob so the divergence can
be re-measured if anyone proposes it, never as a default.

### ⚠ One thing the fix cannot have both ways

**Albedo parity and delivered parity are different settings.** Giving the wall the floor's chroma
*exactly* is chroma 1.000 — literally the same quarry in the file — and it delivers the wall at
**1.52×** the floor's saturation, because this rig does not preserve chroma across values: an
additive lamp over a multiplicative ambient treats a surface at value 34 and one at value 72
differently. The measured curve:

```
chroma  0.000 -> 0.553   (the neutral tint the gate rejected)
chroma  0.284 -> 1.078   <- ships
chroma  0.378 -> 1.149
chroma  0.659 -> 1.335
chroma  1.000 -> 1.518   (albedo parity)
```

This ships **delivered** parity, because the gate judges the delivered frame and the complaint was
about what the phone showed. Albedo parity is one constant away. It is a §6.2 coupling fact, not
an authoring preference, and it is Rafe's to move.

---

## The cap texture: cloud, not grain — and it was 49.6% against the floor's 84.8%

Gate: *"the cap texture is arriving as grey cloud, not stone grain."*

Measured like-for-like, per 32px window, share of spectral power at half a tile or finer:

| | fine-power share |
|---|---:|
| floor ashlar tiles (120) | **84.8%** |
| cap, as the gate saw it | **49.6%** |
| cap, after the octave stack | **73.6%** |

⚠ **My first measurement of this was not a comparison.** It put the floor's 32px tiles against the
cap's 512px *field* — 15 radial rings against 255 — and reported the cap at 0.3%. A uniform
spectrum scores 93% on one and 88% on the other, so the ring counts moved the number more than the
texture did. Same window size, or it is not a comparison.

The grain is an octave stack now — 26 / 61 / 128 / 256 cells across 512px, so periods of 20, 8, 4
and 2 pixels — and the field-scale drift is reduced to 0.38 of its old weight, because a single
3-cell span was drowning every octave above it. All three cap instruments still pass: seamless
0.96×, 34.4 levels per window, drift sd 5.61 with no tile-pitch spike.

**Cost, reported rather than chased:** the retune raised the cap's delivered mean, so the room's
sides at 3–4 tiles fell from **5.95 to 4.58** levels. Both are under the 8-level bar, and that bar
is the open question Rafe's eye is ruling — so this is recorded, not corrected, because correcting
it means tuning against a number that has not been ruled.
