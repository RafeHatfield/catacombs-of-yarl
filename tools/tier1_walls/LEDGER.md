# Ledger — tier one, the Boundary's walls

Every wave, every count, every capture that was taken and what it was taken through. LOOP-PROCESS
§2.3: evidence carries its producer's hash, and a hash mismatch at a ruling invalidates it.

**Generations: 0 of a declared budget of 60.** The budget was not opened. §13.7 records the wall
road as composition, and §6 below is the measurement taken this session that says the parts bin
had nothing left to give that composition could not — so the honest spend was zero rather than a
token batch to show willing.

---

## 1. The waves

| wave | what | count | outcome |
|---|---|---:|---|
| — | photometric probes (flat albedo, 3 levels × 3 scenes) | 12 captures | the rig's multiplier, characterised |
| — | range probes (isolated blocks at rows 1–7, 2 specs × 3 albedos) | 6 captures | the compression profile; rows 5–7 past the instrument's 8-bit domain |
| 1 | `material` arm composed | 81 tiles + 3 void | instruments clean |
| 1 | `compensated` arm composed | 81 tiles + 3 void | instruments clean |
| 1 | binding family | 30 overlays, 5 kinds × 2 planes × 3 variants | placed per cell, never baked |
| 1 | plant (ruined wall) | 84 tiles | never lands, never shown to Rafe |
| 1 | blind seats | 4 (W1, W2, W3, W4) | VALID — plant caught on axis |
| 2 | rebuild after the grain fix | — | round superseded by the round-1 flip list |
| 3 | rebuild after bond / ink / two-scale grain | — | seats W1, W2 |

## 2. The captures

Every one taken through `capture.sh`, which passes all five load-bearing flags. A capture missing
`--ashlar-floor` shows a magenta floor; missing `--boundary-wall` shows the tier-0 magenta mocks;
missing `--wall-bindings` shows bare walls, and that one is **not loud** — §7.1's *show me what
holds this together* would be answered with nothing and the answer would look deliberate.

| capture | build | what it is for |
|---|---|---|
| `baseline_floorscene.png` | landed floor, magenta mocks | the before. The mocks, screaming, for the last time. |
| `probe_a{051,101,202}*.png` | flat albedo | the rig's multiplier; the linearity, unity and dark-cell controls |
| `range_{a,b}_a{051,101,202}.png` | flat albedo, isolated blocks | k_top and k_face at rows 1–4 |
| `r01_material.png` / `r01_compensated.png` | first composed walls | the two arms, side by side |
| `r03_choke.png` | corridor, one top plane | **kept as evidence.** The palisade: head joints running across a wall that runs the other way. |
| `r04_choke.png` | corridor, `top_h` / `top_v` | the same corridor after the orientation fix |
| `r05_gate_*.png` | first gate scene | superseded — the scene contained no void in view |
| `r07_{family,plant}.png` | round 1 | what the four seats judged |
| `r08_*.png` | after the boundary-grain fix | `r08_void{1,2}` are the void candidates |
| `r09_family.png` | after the six-deep mass | the first capture with the void actually in frame |
| `r10_{family,plant}.png` | after the bond stagger | round 2 |
| `r11_{family,plant}.png` | after ink + two-scale grain | **the build offered to the gate**, round 3 |
| `rig_{ratified,f070,f050,r065,r080}.png` | rig probe | evidence for a ruling, not a proposal |

## 3. The instruments, and the four bounds that were wrong

`wall_laws.py --controls`: six tests, six plants, every plant fires, legal family clean.

| test | bound | legal family (compensated) | its plant |
|---|---|---:|---:|
| `two_planes` | ≥1.5 rungs between the bands | 4.17 min / 5.42 mean | 0.39 → FIRES |
| `flat_top` | zero joint rows in the top band | 0 | 3 → FIRES |
| `incident_free_top` | no frozen region >2px across the set | 0 | 4 → FIRES |
| `no_ring` | no tile with all four borders deviating >12% | 0.008 | 0.35 → FIRES |
| `edge_agreement` | seam ≤1.35× an interior step | **0.11** | 2.39 → FIRES |
| `constant_pitch` | ≤60% of darkest columns on a boundary | 0.067 | 1.00 → FIRES |

Four bounds were rewritten because their plants came back SILENT or because they failed the legal
family. Each correction is recorded in the code beside the test it fixed. See `REPORT.md` §5.

`light_field.py --controls`: LINEARITY 0.5000 (worst cell 0.0006, n=38) · UNITY 1.00000 exactly
(n=81) · UNITY-FAILS 1.43349 with the lamp on · DARK-CELL 0.9280.

## 4. The morgue

**Nothing was generated, so there is no generation morgue.** What was discarded is construction,
and it is listed because a discarded construction is the cheapest thing a later session can buy:

| discarded | why | evidence |
|---|---|---|
| donor residual patches as grain | a box blur wide enough to remove a joint does not remove a course; the donor's bond arrived inside every block | the run came back as brick wallpaper |
| one top-plane orientation | a wall running north–south got head joints running across it | `r03_choke.png` |
| grain indexed from the tile's left edge | value agreed across a boundary and texture did not | `edge_agreement` 4.22× → 0.09× |
| course-independent boundary offsets | both courses broke at the same x at every boundary — no bond | seat W1, round 1 |
| one ink set for both planes | iron at rung 1 vanishes on a face §6.5 has already darkened | seat W3, round 1 |
| a three-deep mass in the gate scene | two rings of stone and no void — the scene did not contain its own subject | 66 void cells, 0 in view |
| a seat crop that trimmed the HUD | it trimmed the void with it | seat W1: *"the image contains no beyond"* |
| radius 8.0 / falloff 0.45 rig arm | returned an all-zero capture; not chased, because falloff at the ratified radius already answered the question | `rig_r080.log` |

## 5. The rig probe

Against the gate scene's own legibility guard, which requires two declared points to stay DARK
(§6.2.1: *not a licence to flood the Boundary with light*).

| arm | 4-tile point | dark points | verdict |
|---|---:|---:|---|
| ratified (falloff 1.00, radius 5.0) | 0.156 | 0.060 / 0.080 | capture written |
| falloff 0.70 | 0.241 | 0.058 / 0.078 | capture written |
| falloff 0.50 | 0.338 | 0.056 / 0.076 | capture written |
| falloff 0.65, radius 6.5 | 0.474 | **0.151** | **REFUSED — drowned the arc** |

**The falloff exponent buys mid-range legibility and does not spend the arc; the radius spends
it.** The dark points get *darker* as the falloff flattens. That is a fact about the rig, offered
to whoever rules on it, and this session rules nothing about it.

## 6. What the parts bin actually supplied

Round 7 of the wall gauntlet, three candidates, every one a FAIL in its own ledger — which is the
point: they failed on relationships, which composition supplies, and succeeded as material.

| donor | rows used | residual sd | its gauntlet verdict |
|---|---|---:|---|
| `r07_00` | 6–30 | see manifest | *"flat brick wallpaper with zero thickness"* |
| `r07_08` | 6–30 | see manifest | FAIL (ledger) |
| `r07_09` | 6–30 | see manifest | FAIL (ledger) |

**Amplitude only.** The residual still carries the donors' own course pitch, measured and recorded
in the manifest as `donor_residual_periodicity`, so its pixels cannot be laid as grain without
laying its bond with them. No generated pixel is in a shipped tile.

## 7. Seats

| round | seat | build | verdict |
|---|---|---|---|
| 1 | W1 family | r07 | CULL: *"the wall is 87% below 20/255 and one pixel thick — at 1:1 there is no wall"* |
| 1 | W2 **plant** | r07 | **CAUGHT ON AXIS** (Q11: *"Nothing has happened to it. Cracks were applied to it."*) — the cull it gave was one the family shares and does not count |
| 1 | W3 family | r07 | CULL: *"a black band with a 4px outline — no mass, no shadow, no thickness, no damage, no repairs"*; Q4 **NOTHING** holds it |
| 1 | W4 comparative | r07 vs the asset bar | **RANK: B — Yarl.** *"on the face band … genuinely good"*; CULL: wall tops carry zero texture |
| 3 | W1 family | r11 | see `evidence/seats/r3_W1.json` |
| 3 | W2 **plant** | r11 | see `evidence/seats/r3_W2.json` |

Round 2 (r10) was superseded inside the session by round 1's flip list and is not read.
