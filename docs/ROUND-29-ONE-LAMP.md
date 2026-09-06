# Round 29 — one lamp: #174 closed on the code, re-opened on the rig

**Branch** `art/one-lamp` · **Gate** issue #174 · **Predecessor** round 28 (PR #177, parked
composed-and-holding) · **Ends at** Rafe's device walk, which is the round's gate and has not
happened.

---

## 0. What this returns, in one page

1. **The lamp is one quantity now, and it is proved rather than asserted.** Before: 97.1% of
   floor pixels byte-identical across an energy sweep of 0 / 1.6 / 8.0. After: 49.6%, against the
   wall's 59.1%. With the specular nulled the floor now responds to a doubling of the lamp at
   1.989 / 2.005 / 1.917 by band, against the wall's 2.018 / 1.974 / 1.904 — **the same
   arithmetic, checked on the frame, not inferred from the source.**

2. **The fix is NOT the one the issue prescribes, and the issue's version is wrong.**
   `COLOR * LIGHT_COLOR * LIGHT_ENERGY` — the expression named in #174, in bible §6.2's asterisk
   and in §6.5's banner — measures a **quadratic** energy response on a floor whose walls are
   linear. `LIGHT_COLOR` is two quantities: `.rgb` is the tint alone and `.a` is the radial
   falloff, and the engine multiplies `LIGHT.rgb` by `LIGHT.a` in the blend, so scaling the vec4
   whole applies the energy twice. **Energy goes on the RGB only.** Engine semantics measured and
   banked: `tools/tier1_floors/SHADER-SEMANTICS.md`.

3. **A SECOND DEFECT, larger than #174 in what it says about the surface.** The shader's
   `delivered` scalar was `max(LIGHT_COLOR.rgb)` — the light's *tint*, measured constant at
   (1.002, 0.696, 0.423) across the entire lit field. It clamped to 1.0 at every lit fragment, so
   `pow(delivered, polish_exp)` computed `pow(1.0, 2) = 1.0` **from the day it was written** and
   **Ruling 70's superlinear light response has never run.** The polish was a flat
   `polish × gain` attenuated once by the blend — linear in delivered light, which is
   arithmetically the baked value-lift §8.2.1 bans and the shader's own header calls a lie. Fixed,
   with two controls.

4. **THE DITHER IS NOT THE POLISH MASK, and round 28's attribution of flip 1 does not survive a
   control.** Two independent instruments say so, and the connection fix made the polish term
   *quieter*, not louder — the opposite of this round's pre-registered expectation. **Nothing was
   exposed to fix.** §5.

5. **§6.5's void banner is over-broad and lifts, on proof, for most of what it covers.** The range
   profile that produced `0.87 / 0.67 / 0.48 / 0.30` and the *k_top cannot reach 1.0* argument
   were measured on **flat-albedo probe scenes that never carried the polish shader**. Re-captured
   on the corrected lamp, **every frame is byte-identical** and every number reproduces. What was
   genuinely void is the *composed-scene* table, and it is re-taken here. §6.

6. **Ruling 56 re-opens and the ladder is built.** The floor's delivered value at the standing
   case moved 105.74 → 152.34 (×1.44), **and near-max floor pixels at the lamp core went 72 →
   1220** — which a blind seat located unaided and I had excluded from my own measurement (§3).
   Ten one-knob rungs captured. **This is the round's device gate and it is Rafe's.** §7.

7. **TWO STOPS ARE STACKED AND THE BUILD IS NOT ON THE PHONE.** The no-change loop guard fired,
   and the install gate refuses a FAIL verdict. Both are working correctly and neither is
   overridden here. §8 item 5.

**Nothing in this round was ruled. Three items are printed in full in §8 awaiting Rafe.**

---

## 1. The defect, exactly, and it was two

`tier1_polish.gdshader`'s `light()` never mentioned `LIGHT_ENERGY`, under a comment asserting
that *"LIGHT_COLOR already carries the light's colour, its energy and the radial falloff
texture."* It carries the colour. It carries the falloff, in a channel the comment did not name.
It does not carry the energy — and the **default** light pass, which every wall, cap, binding and
prop runs because none of them carries a `ShaderMaterial`, applies it.

So every floor tile in the game was lit at energy **1.0** while the wall beside it ran at Ruling
56's **1.6**.

### The measurement that shows it, and it is sharper than the issue recorded

`measure_energy_response.py` on `tier1_combined_probe.json` — the legibility-free instrument
scene, because an energy sweep must include energy 0 and the review scene correctly refuses to
write a frame whose declared lit points are dark.

| | floor pixels byte-identical across E ∈ {0, 1.6, 8.0} | wall |
|---|---:|---:|
| **before** | **0.9708** | 0.5914 |
| after | 0.4959 | 0.5914 |

The wall column is **byte-identical between the two runs** — 614081/1038336 both times — so
nothing but the floor moved.

And the band table found something #174 did not record:

| band | floor E=0 | floor E=1.6 | wall E=0 | wall E=1.6 |
|---|---:|---:|---:|---:|
| ≤2 tiles, **before** | **70.07** | 70.31 | 1.00 | 11.43 |

**At energy 0 — the "lighting is live" positive control — the floor at the lamp still read
70.07 where the wall beside it read 1.00.** The control that proves the lighting is live was
being passed by a surface that could not see it.

> **The instrument's demonstrated failure is the before-run itself** (§13.5, LOOP-PROCESS §4).
> `measure_energy_response.py` prints `identical_share = 0.9708` on real captures — NO CONNECTION,
> on data, not on a plant. Its pass counts because that failure is on record beside it.

---

## 2. The fix is not the one the issue prescribes

The first attempt wrote exactly what #174, bible §6.2's asterisk and §6.5's banner all name:
`COLOR * LIGHT_COLOR * LIGHT_ENERGY`. It measured, with the specular nulled:

| plane | lit contribution ratio per doubling of energy |
|---|---:|
| floor | **3.915** |
| wall | 2.018 |

A **quadratic** floor against linear walls — the same class of error as the defect, in the other
direction. Eight one-line shader probes settled why, and the semantics are banked in
`tools/tier1_floors/SHADER-SEMANTICS.md` so nobody buys them a third time:

```
LIGHT_COLOR.rgb   the light's tint. CONSTANT over the light's quad — measured (1.002, 0.696,
                  0.423) at 2.2, 3.2 and 4.5 tiles alike — and zero outside it.
LIGHT_COLOR.a     the radial falloff texture. This is where attenuation lives.
LIGHT_ENERGY      the energy, exactly: 0.400 at energy 0.4, 0.815 at 0.8.
the blend         contribution = LIGHT.rgb * LIGHT.a, added.
```

So a vec4 scaled whole is scaled twice. The correct diffuse — the one a wall with no
`ShaderMaterial` runs — is

```glsl
vec4 diffuse = vec4(COLOR.rgb * LIGHT_COLOR.rgb * LIGHT_ENERGY, COLOR.a * LIGHT_COLOR.a);
```

### One arithmetic, checked rather than claimed

With `polish_gain: 0.0` the floor's `light()` reduces to exactly the default pass, so **the two
planes must respond to a doubling of the lamp by the same factor.** That is the test, and it is
the only honest statement of "one arithmetic":

| band | floor, nulled polish | wall |
|---|---:|---:|
| ≤2 tiles | **1.989** | 2.018 |
| 2–4 | **2.005** | 1.974 |
| >4 | **1.917** | 1.904 |

---

## 3. The second defect — Ruling 70's response has never run

`float delivered = clamp(max(max(LIGHT_COLOR.r, LIGHT_COLOR.g), LIGHT_COLOR.b), 0.0, 1.0);`

`LIGHT_COLOR.rgb` is the tint. The Boundary's `ffb066` has a **saturated red**. So this expression
returns **1.002, clamped to 1.0, at every lit fragment in the room**, and `pow(delivered, 2)` has
been computing 1.0 since the line was written.

**The specular was therefore `polish × polish_gain`, flat, attenuated exactly once by the blend.**
Linear in delivered light. That is arithmetically an albedo change — the baked value-lift §8.2.1
bans, and the thing the shader's own header says would make the file a lie.

Measured from the other side, before the fix:

- the floor's energy exponent with the polish **live** was indistinguishable from **nulled** —
  1.992 against 1.989. A superlinear term would have separated them.
- the polish contributed **11.0 levels at ENERGY ZERO** (18.72 against the nulled 7.72). *"A
  polished stone and a rough one are the same stone in the dark"* was false.

Rebuilt from the two things that actually carry delivery:

```glsl
float delivered = clamp(LIGHT_COLOR.a * LIGHT_ENERGY, 0.0, 1.0);
```

**Two controls, each on its own axis** (LOOP-PROCESS §4.1):

| control | before | after |
|---|---|---|
| same stone in the dark — floor at energy 0, polish live vs nulled | 18.72 vs 7.72 | **7.72 vs 7.72** |
| superlinear — energy exponent, polish live vs nulled | 1.992 vs 1.989 | **2.070 vs 1.989** |

Beyond four tiles both arms read 1.917 and the term contributes nothing, which is §13.9 doing what
§13.9 predicts.

### The null-polish control at the ratified energy — successor to round 28 §5

| band | floor ON | floor NULLED | **specular share** | round 28's share | wall ON | wall NULLED |
|---|---:|---:|---:|---:|---:|---:|
| ≤2 tiles | 101.07 | 90.19 | **10.8%** | ~30% | 11.43 | 11.43 |
| 2–4 | 57.33 | 50.08 | **12.6%** | ~27% | 20.15 | 20.15 |
| >4 | 9.00 | 9.00 | **0.0%** | ~0% | 5.05 | 5.05 |

Wall values byte-identical across both arms. Round 28's *"43% of the cross-plane separation runs
through that term"* is now **10.8–12.6% of the floor's own value**.

### And #174's clipping premise — I got this wrong the first time, and a blind seat caught it

#174 reads: *"the corrected floor clips to 255 near the lamp at 1.6."* My first pass reported
**0.07% of floor pixels**, and called the premise dead. **That number excluded the region the
premise is about.** It was taken at threshold `== 255`, on the probe scene, **excluding the player
cell and its eight neighbours** — a filter added to keep the player sprite out of a floor
measurement, which removed the lamp core with it. Round 29's blind seat then flagged exactly that
region unaided:

> *"The lamp core is clipped: 12,874 non-UI pixels sit at luminance ≥246 in a contiguous patch at
> x 285–504, y 457–601, where the floor loses every joint and slab edge into flat cream. Pull the
> light curve's white point down so no floor pixel exceeds ~232."*

Re-measured on the delivered frame the seat actually judged, over the whole dungeon view, nothing
excluded:

| frame | pixels ≥246 | pixels = 255 |
|---|---:|---:|
| round 28, **pre-fix** | **72** | 0 |
| round 29, **ratified rig** | **1220** | **0** |
| round 29, energy 1.0 — what the floor *was* lit at | **0** | 0 |

**The seat's localisation is exactly right and mine was the number that hid.** All 1220 pixels
fall inside the box it named; the patch reads mean 167.7, max **249.9**. Its count is ~10× high
and nothing in the frame reaches 255 — so the literal *"clips to 255"* is still not met — but
**the fix raised near-max floor pixels seventeenfold at the lamp core**, and an independent eye
read the result as losing joint detail there.

> **So the honest statement is the opposite of the one I first filed.** Ruling 56 re-opens on the
> 1.44× *and* on the lamp core, the seat has proposed a white point (~232) as a starting position
> for the walk, and **the rig ladder's `energy_1.0` rung is the control that isolates it** — at
> the energy the floor was actually lit at, the count is zero.
>
> **The bible-memory lesson this violated is already written down:** *never summarise to the band
> that agrees with you; report the worst cell, every band.* An exclusion added for one good reason
> silently answered a different question.

---

## 4. What is on disk

```
src/Presentation/assets/shaders/tier1_polish.gdshader   the two fixes, one commit each
tools/tier1_floors/SHADER-SEMANTICS.md                  the engine, measured, with the probes
tools/tier1_floors/measure_energy_response.py           the connection test
tools/tier1_floors/measure_polish_dither.py             the dither instrument (see §5)
tools/tier1_floors/capture_energy_probe.sh              the sweep
tools/tier1_floors/capture_rig_ladder.sh                Ruling 56's ladder
```

The floor family **rebuilds byte-identical** across both fixes — `rebuild_ashlar.sh` moved only
the producer-hash stamps (LOOP-PROCESS §2.3). No authored material changed in this round.

---

## 5. THE DITHER — the premise is disproved, and this round did not touch it

This round was briefed on a pre-registered expectation:

> *"Restoring LIGHT_ENERGY raises `delivered`; `pow(delivered, 2)` amplifies the four-way
> reflectivity noise mask; that dither is the artefact the combine's seat already culled. So the
> first corrected capture will look WORSE, by design."*

**It does not hold, and the reason is §3.** `delivered` was not a falloff quantity that the fix
raises — it was the constant 1.0. Correcting it makes the specular *fall off*, and the diffuse
got 1.6× brighter beside it, so **the polish term's share dropped from ~30% to 10.8%** and its
amplitude in the lit band from **12.01 to 7.70 delivered levels**. The frame is brighter and the
polish term is fainter. Reported rather than quietly delivered.

### And the artefact is not the polish mask at all

Round 28 attributed flip 1 — *"a uniform ~45° hatch overlay runs across the entire lit floor …
it is screen-space, not surface texture"* — to `refl = PolishByAge[fa]` picking one of four
discrete reflectivities per pixel. **That attribution was reasoned from the code and never
controlled.** Nulling the polish, same scene, same station, one variable:

| arm | high-pass residual RMS | mean luminance | **residual / mean** |
|---|---:|---:|---:|
| pre-fix, polish ON | 3.842 | 49.51 | **0.0776** |
| pre-fix, polish NULL | 2.873 | 37.50 | **0.0766** |
| post-fix, polish ON | 4.898 | 62.80 | **0.0780** |
| post-fix, polish NULL | 4.300 | 55.10 | **0.0781** |

**The relative high-frequency content is constant to three decimals across all four arms.**
Nulling the polish removes 25% of the absolute residual because it removes 24% of the brightness,
and removes none of the weave.

A second, independent instrument agrees. `measure_polish_dither.py` isolates the polish term
exactly as `lum(gain 1.0) − lum(gain 0.0)` and asks how often it changes value from pixel to
pixel — which is what a dither *is*, and which does not depend on orientation, the axis that
misled round 28's first two instruments:

| | flip rate, polish term | flip rate, the diffuse floor beneath it | ratio |
|---|---:|---:|---:|
| pre-fix | 0.1320 | 0.1786 | **0.739×** |
| post-fix | 0.0987 | 0.2586 | **0.382×** |

**The polish term flips less often than the stone it sits on, before and after.** It is smoother
than its own material; it is not the high-frequency source.

> **§13.10 applies to me here.** I am contradicting a written attribution, which is the stronger
> claim and carries the heavier burden. The burden is discharged with a control round 28 did not
> run — it explicitly declined to, on the grounds that the term *"sits on top of #174's wrong
> `delivered` quantity"* — and with two instruments that disagree about method and agree about
> the answer.

### A THIRD SEAT SAW IT, THIS ROUND, ON THE CORRECTED FRAME — and it is still not located

This round's own critic, blind, flagged it again with a box:

> *"A diagonal streak/hatch band runs down-left at ~45° across the lit pool around
> (430,470)–(560,560). A point lamp cannot produce a directional band. Delete the overlay."*

**That is round 28 and round 29 — two seats, two decks.** So the instruments got one more
chance, on the seat's own coordinates.

> ⚠ **AND IT IS TWO ARTEFACTS, NOT ONE. I CONFLATED THEM AND THE CONFLATION IS CORRECTED HERE.**
>
> Round 27's flip 6 — *"vary the 45° hatch; same angle and spacing on a dozen slabs"* — is **not
> this**. Round 27 located it, in `stone_marks`, and ruled it *"a §8.3 motif trap … and its own
> logical change"*. **This round's seat reported that one separately and in the same breath:**
> *"The incised double-tick `//` marks on the stones right of the figure (roughly x 565–620,
> y 480–580) recur at identical angle and identical length about fifteen times."*
>
> | | seats | where it is |
> |---|---|---|
> | **repeated `//` incised marks** | round 27 flip 6, round 29 flip 3 | **`stone_marks`. Located, §8.3 motif trap, handed forward twice and never filed.** |
> | **a diagonal band across the lit pool** | round 28 flip 1, round 29 flip 2 | **unlocated.** Attributed by round 28 to the polish mask; that does not survive its own control. |
>
> Everything below is about the **band**. Counting round 27 toward it inflated the seat count and
> would have put a wrong provenance on the issue filed from this round. The two above are high-pass
measures and **a broad directional band is LOW frequency: they would miss it by construction.**
That gap is closed here, on the smoothed field, inside the seat's box:

| in the seat's box | peak gradient orientation | share | 45° bins | 90° bins |
|---|---|---:|---:|---:|
| the polish term, isolated | 90–105° | 0.222 | **0.067** | 0.380 |
| the diffuse floor beneath it | 75–90° | 0.223 | **0.052** | 0.426 |

*(uniform would be 0.083 per bin.)* Both planes are organised at **90° — the bond** — and the 45°
bins sit **at or below uniform in both.** The polish term in that box is not small (mean 22.33
levels, sd 31.28), so this is not a null for want of signal.

> ### ⚠ AND THE HONEST READING OF THAT IS NOT "THE SEATS ARE WRONG". §13.10.
>
> **Two seats have reported the band and six instruments across two rounds have failed to
> find it** — round 28's lag autocorrelation and structure tensor, and this round's high-pass
> residual, flip rate, and two orientation histograms. §13.10 is explicit about which side that
> leaves carrying the burden: *"an instrument that says a seat did not see what it says it saw is
> making the stronger claim."* **Six failures to find a thing are not a finding that it is absent.**
> Round 24's seat was right and the instrument contradicting it was wrong, and that seat spent two
> rounds discredited for it.
>
> **What this round establishes is narrower than round 28's attribution and firmer than it:**
> whatever the seats are seeing, **it is not the polish mask.** Nulling the polish leaves the
> relative high-frequency content unchanged to three decimals and leaves the orientation
> statistics in the seat's own box unchanged. Round 28's *"the artefact is the polish mask"* does
> not survive its own control. **Where it IS remains open, and it is not closed by my failing to
> find it.**

**So there was nothing for step 2 to fix.** Step 2 was briefed to fix a dither the connection
exposed; the connection exposed nothing, and the one candidate the brief named is excluded by
control. Chasing the unlocated artefact here would have been re-authoring the tier-one floor
inside a round whose refusals forbid bundling — and on a premise measurement had already killed.
**Filed as the successor, unattributed, with a box and the two seat quotes to start from.**

**The delivered palette is clean and was never the issue.** `measure_delivered_palette.py`:
albedo 31 delivered against 33 authored, **0 off-palette**, control binds at 634 blended against
31 snapped. The delivered *frame* count rose 113.9 → 124.4 colours/cell, which is round 27's
ruling operating exactly as written — **a lit frame's colour count is the rig's number, not the
palette's**, and the rig just got 1.6× brighter on the floor.

---

## 6. §6.5 RE-DERIVED — and the void banner is over-broad

Bible §6.5 carries: *"Every measured figure in this clause is VOID rather than provisional, and is
re-measured after #174 lands — not adjusted. That includes the re-scoping's own range profile
(0.87 / 0.67 / 0.48 / 0.30), the k_top cannot reach 1.0 argument, and the 2:1 plane separation."*

**Most of that is not void, and the proof is byte-identity.**

`range_profile.py` runs on `wall_range_a/b.json` through `tile_themes_probe.yaml` — **flat-albedo
photometric probe scenes with no `--ashlar-floor` and no `--floor-overlays`.** Their floor is a
plain theme sprite carrying **no `ShaderMaterial` at all**, so it ran the default light pass, with
the energy, the whole time. Re-captured on the corrected lamp:

> **Every one of the six probe PNGs is byte-identical to the committed pre-fix evidence.** Only
> the logs moved, and only in the worktree path and the timestamps.

And the engine says so itself, independently of the byte-identity, in every one of those logs:

```
[Tier1] floor overlays: none declared (no --floor-overlays, no marker floorOverlays) — base tiles only
[Tier1] wang floor:     none declared (no --wang-floor, no marker wangFloor)
[Tier1] ashlar floor:   none declared (no --ashlar-floor, no marker ashlarFloor)
```

Two independent confirmations, and the second is the engine's own answer rather than mine —
§13.10's standard for a measurement that overturns a written finding.

Recomputed from them:

| range | k_top, recorded (void) | k_top, corrected lamp |
|---:|---:|---:|
| 1 tile | 0.87 | **0.8686** |
| 2 | 0.67 | **0.6696** |
| 3 | 0.48 | **0.4799** |
| 4 | 0.30 | **0.2995** |

**BANNER LIFT, PROPOSED (Rafe's, §8):** the range profile, the *k_top cannot reach 1.0* argument
and the 2:1 plane separation were never taken across the defect. They are re-affirmed on the
corrected lamp from unchanged frames, not adjusted.

### What WAS void, re-taken

Round 28 §5's composed-scene table is the figure that genuinely crossed the defect, because that
scene lays the real ashlar floor and every tile of it carries the shader. Re-measured on
`onelamp_r1.png`, **one method applied to both frames** so the columns are comparable:

**Illumination, stated because §13.9 requires it:** the ratified rig — energy 1.6, radius 5.0
tiles, falloff 1.00, ambient `1a1a22` × 0.70 = `#121218`, light `ffb066`, `void_ring 1` (the
flat-dark fallback, §12.1a's occluder still outstanding).

| band | n floor | n wall | floor, r28 | **floor, one lamp** | wall, r28 | wall, one lamp | f/w r28 | **f/w one lamp** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ≤2 tiles | 9 | 4 | 118.62 | **152.34** | 58.40 | 58.40 | 2.031 | **2.609** |
| 2–4 | 21 | 15 | 46.54 | **57.33** | 20.15 | 20.15 | 2.310 | **2.846** |
| >4 | 43 | 48 | 8.63 | **9.00** | 5.05 | 5.05 | 1.708 | **1.781** |

Wall values byte-identical. **The worst cell in every band**, because a mean hides the cell that
decides whether a band reads:

| band | floor min / max | wall min / max |
|---|---|---|
| ≤2 | 91.92 / 200.52 | 11.43 / 81.00 |
| 2–4 | **19.14** / 119.85 | 2.60 / 59.26 |
| >4 | 6.15 / 19.03 | 1.00 / 20.27 |

### The cap against the floor — `measure_mass_read`, same frame

| band | n | L(cap, floor), round 28 | **L(cap, floor), one lamp** | vs the 8-level bar |
|---|---:|---:|---:|---|
| standing ≤2 | 3 | 50.22 | **72.56** | CLEARS |
| 3–4 tiles | 19 | 16.88 | **17.79** | CLEARS |
| beyond 4 | 35 | 4.26 | **4.27** | under |

Sign negative throughout: the cap is **darker** than the floor.

> ⚠ **AND THAT IS A FINDING, NOT A RESULT.** §6.5 row 1 wants the wall top **lighter** than the
> floor. The corrected lamp brightens the floor and leaves the cap where it was, so the delivered
> gap in the wrong direction **widened by 1.44×**. §6.5's re-scoping already ruled the planes
> invert past three tiles as physics; this says the standing case moved further from row 1 too.
> **It is a value-law question and it is Rafe's.** Printed in §8.

---

## 7. THE RIG LADDER — Ruling 56 re-opened. This is the gate.

Every knob Ruling 56 ratified was walked against a floor lit at energy 1.0 while its walls ran at
1.6. The floor's delivered value at the standing case has since moved **105.74 → 152.34 (×1.44)**.

`tools/tier1_floors/capture_rig_ladder.sh` — one knob per rung, everything else held at Ruling 56,
on `tier1_combined_review.json` (the guarded scene: it refuses to write a frame whose declared lit
points come back dark, and no rung was refused).

| rung | ≤2 tiles | 2–4 | >4 | worst 2–4 cell | floor clipped |
|---|---:|---:|---:|---:|---:|
| **ratified** (r 5.0 / f 1.00 / a 0.70 / E 1.6) | **152.34** | **57.33** | **9.00** | 19.14 | **1220 px ≥246** |
| energy 1.0 — *what the floor was actually lit at* | 105.74 | 37.09 | 8.46 | 14.68 | **0** |
| energy 1.3 | 133.77 | 47.11 | 8.73 | 16.87 | — |
| energy 2.0 | 173.12 | 69.62 | 9.35 | 22.09 | — |
| radius 4.0 — *≈ Ruling 56's own delivered reach* | 137.46 | 31.63 | 7.55 | **7.48** | — |
| radius 6.0 | 160.52 | 79.76 | 13.94 | 36.68 | — |
| falloff 0.7 | 160.47 | 76.22 | 10.92 | 30.46 | — |
| falloff 1.5 | 139.60 | 37.90 | 7.93 | 11.19 | — |
| ambient 0.5 | 150.24 | 55.11 | 6.97 | 17.05 | — |
| ambient 1.0 | 155.55 | 60.57 | 12.29 | 22.28 | — |

⚠ **THESE STILLS GATE NOTHING** (§13.1, §6.2.1). No rig value is ratified from a sheet of frames;
§6.2.1 exists precisely because the sighted round read its captures at 2× on a desktop. **The
ratification is Rafe's eye, on the reference device, at gameplay distance, across the lit
radius.** The table is here so the walk starts informed.

**When values are ratified they are written back to `harness_config.yaml` and bible §6.2 as
REQUIRED FLAGS**, on the standing discipline that a ratified value which can be silently defaulted
is a ratified value that can silently drift. The current §6.2.1 values are then annotated
**superseded-by-re-ratification**, with the date.

---

## 8. Anything awaiting a ruling, printed in full (§9)

1. **§6.5's void banner is over-broad — lift it for the probe-measured figures.** The range
   profile (`0.87 / 0.67 / 0.48 / 0.30`), the *k_top cannot reach 1.0* argument and the 2:1 plane
   separation come from flat-albedo probe scenes that carry no `ShaderMaterial`. Their frames are
   **byte-identical** across the fix and every number reproduces. Proposed: the banner narrows to
   figures measured on the **composed scene with the real ashlar floor** — round 28 §5's table and
   PR #151's status-trail measurements, if those used it. **Not applied. Bible §6.5 and §6.2's
   asterisk still read as they did.**

2. **The cap sits further below the floor than it did, at the standing case.** `L(cap, floor)`
   50.22 → **72.56** levels, sign negative, because the floor gained 1.44× and the cap gained
   nothing. §6.5 row 1 asks for the wall top to be *lighter* than the floor. This is a value-law
   question — whether row 1 is reachable at the standing case on the corrected lamp, or whether
   the re-scoping's *dark-by-design* now extends inward — and it is **Rafe's, at the gate, not
   an instrument's.**

3. **THE DIAGONAL BAND: TWO SEATS, SIX INSTRUMENTS, NO LOCATION — and §13.10 says the
   instruments are the ones short.** Rounds 28 and 29 have each had a blind seat report it;
   this round's gave a box, (430,470)–(560,560). **Round 27's flip 6 is a DIFFERENT artefact** —
   the repeated `//` marks in `stone_marks`, located, ruled a §8.3 motif trap, reported again by
   this round's seat as its own flip, and **never filed in two rounds of being handed forward.** Round 28's attribution to the polish mask **does
   not survive its own control** — nulled, the relative high-frequency residual is
   0.0776 / 0.0766 / 0.0780 / 0.0781 and the orientation statistics inside the seat's box are
   unchanged (45° bins 0.067 polish, 0.052 diffuse, against 0.083 uniform). But six failures to
   find a thing are not a finding that it is absent, and §13.10 puts the heavier burden on the
   party making the accusation. Proposed: round 28's §7 attribution is annotated as unproven, the
   item is filed **unattributed** with the box and the two quotes, and it does not ride on #174.
   The `stone_marks` motif trap is a separate item and is not folded into it.
   **Not applied to round 28's document.**

4. **Bible §5.6 says nine rungs; the code and the manifest ship eleven.** Still true, still not
   this round's. Carried forward from round 28 §9.5.

5. **THE DEVICE BUILD FOR THE RIG WALK IS BLOCKED, BY TWO GUARDS, AND NEITHER IS OVERRIDDEN.**

   **(a) The no-change guard STOPPED the line.** Rounds 1 and 2 are byte-identical pictures, mean
   0.000 / worst cell 0, both FAIL. **The cause is procedural, not a stalled lane:** round 1's
   verdict went stale when doc commits moved the build id, so round 2 was run on an unchanged
   picture purely to refresh it. The guard cannot tell those apart and should not have to.
   `STALL-REPORT.md`. **No further round was run** — LOOP-PROCESS §1.1.4 and CLAUDE.md both say
   the line escalates and never grinds past a STOP.

   **(b) The install gate refuses, because the verdict is FAIL.** Not because it is stale — it is
   current for build `08be3c7e6e32`. A FAIL verdict does not satisfy §1.2.2. The only override is
   `YARL_SKIP_CRITIC=1`, which installs a build stamped **SKIPPED-REVIEW**, and CLAUDE.md is
   explicit that *nothing walked on one is a gate verdict*.

   **That is the bind, and it is Rafe's to cut, because it decides what Ruling 56 is worth.** The
   walk is a RIG ratification under §6.2.1, not an asset acceptance — but Ruling 56 is itself a
   gate ruling, so a ratification taken on a SKIPPED-REVIEW build may not be a ratification at
   all. **Not decided here.** The three options, stated without a recommendation because the
   ruling is not mine:

   - rule that a rig-ratification walk may run on a SKIPPED-REVIEW build, since the rig is not
     the artefact being judged;
   - clear enough of the seat's flip list for a PASS first — but most of it is floor-material
     work (blob-noise, unjointed corridor, anti-aliased cracks, the repeated hatch decal) that is
     a different lane, and the STOP forbids this round grinding on it;
   - walk the ladder on the captured frames and defer the device pass — which §6.2.1 exists
     specifically to refuse.

   ⚠ **The seat's flip 1 is a rig request and belongs to this walk either way:** *"Pull the light
   curve's white point down so no floor pixel exceeds ~232."*

---

## 9. Reproducing

```bash
dotnet build CatacombsOfYarl.Presentation.csproj
/Applications/Godot_mono.app/Contents/MacOS/Godot --headless --path . --import

# the connection test — the sweep, then the measurement
tools/tier1_floors/capture_energy_probe.sh conn 0 1.6 8.0
python3 tools/tier1_floors/measure_energy_response.py \
  --scene src/Presentation/assets/tier0_harness/scenes/tier1_combined_probe.json \
  --arm 0:tools/tier1_floors/evidence/conn_e0.png:tools/tier1_floors/evidence/conn_e0.log \
  --arm 1.6:tools/tier1_floors/evidence/conn_e1.6.png:tools/tier1_floors/evidence/conn_e1.6.log \
  --arm 8.0:tools/tier1_floors/evidence/conn_e8.0.png:tools/tier1_floors/evidence/conn_e8.0.log \
  --tag conn

# the one-arithmetic check needs the null-polish arm. TEXT SUBSTITUTION, NEVER A JSON
# ROUND-TRIP (round 28's trap), and RESTORE afterwards:
cp src/Presentation/assets/tier1_ashlar/MANIFEST.json /tmp/M.json
sed -i '' 's/"polish_gain": 1.0/"polish_gain": 0.0/' src/Presentation/assets/tier1_ashlar/MANIFEST.json
tools/tier1_floors/capture_energy_probe.sh gain0 0 0.4 0.8
cp /tmp/M.json src/Presentation/assets/tier1_ashlar/MANIFEST.json

# the room, the palette, the planes
tools/tier1_floors/capture_combined.sh onelamp_r1 1
python3 tools/tier1_floors/measure_delivered_palette.py --controls --ladder-delta \
  --capture tools/tier1_floors/evidence/onelamp_r1.png tools/tier1_floors/evidence/onelamp_r1.log \
  --scene src/Presentation/assets/tier0_harness/scenes/tier1_combined_review.json
python3 tools/tier1_walls/measure_mass_read.py \
  --scene src/Presentation/assets/tier0_harness/scenes/tier1_combined_review.json \
  --png tools/tier1_floors/evidence/onelamp_r1.png \
  --log tools/tier1_floors/evidence/onelamp_r1.log \
  --assets src/Presentation/assets/tier1_walls --tag onelamp_r1

# §6.5's probe figures — the byte-identity proof
tools/tier1_walls/capture_range_probes.sh && git status --short tools/tier1_walls/evidence/
python3 tools/tier1_walls/range_profile.py

# the ladder for the walk
tools/tier1_floors/capture_rig_ladder.sh
```
