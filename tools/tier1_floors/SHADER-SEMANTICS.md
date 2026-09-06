# What Godot's canvas `light()` pass actually gives you — MEASURED, not read off a doc page

**Why this file exists.** Issue #174 was caused by a comment that asserted engine semantics
instead of measuring them: *"LIGHT_COLOR already carries the light's colour, its energy and the
radial falloff texture."* Two thirds of that sentence are wrong, and the wrong third cost this
project every cross-plane number it had taken (bible §6.5, VOIDED). The first attempt at the fix
then repeated the error in the other direction — it wrote `COLOR * LIGHT_COLOR * LIGHT_ENERGY`,
which is what the issue itself prescribes, and produced a floor whose response to the lamp was
**quadratic** where every wall beside it was linear.

So the semantics are measured here, once, on this engine and this rig, and cited rather than
re-derived. Bible §13.10's asymmetry applies: an instrument that contradicts a claim carries the
heavier burden, and every row below is a capture on disk.

## Method

One floor cell, `(4, 13)` of `tier1_combined_probe.json` — 2.2 tiles from the lamp, no wall in its
eight neighbours, sampled with a 6px inset. The floor's `light()` body is replaced with a one-line
probe, the project re-imported, and the scene captured at two energies. Ambient at that cell,
measured with the light pass nulled, is **7.27**; an 8-bit reading of `v` therefore implies a
shader output of `(v − 7.27) / 255`.

Probes: `tools/tier1_floors/evidence/probe{A2,C,D,E,F,G,H,I}_e*.png`.

## Results

| probe | `light()` body | E=0.4 (red) | E=0.8 (red) | what it establishes |
|---|---|---:|---:|---|
| C | `LIGHT = vec4(0.25)` | 71.23 | 71.23 | **The engine does not scale LIGHT by energy.** A constant output is constant. And `(71.23−7.27)/255 = 0.2508` — LIGHT is added at face value. |
| D | `LIGHT = vec3(LIGHT_ENERGY*0.1)` | 17.39 | 28.06 | **`LIGHT_ENERGY` is the energy, exactly.** Implies 0.397 and 0.815. |
| E | `LIGHT = LIGHT_COLOR.rgb*0.5` | 135.06 | 135.06 | **`LIGHT_COLOR.rgb` is the TINT alone** — `(1.002, 0.696, 0.423)` = `ffb066`. No energy in it. |
| F | `LIGHT = COLOR.rgb*0.5` | 59.31 | 59.31 | `COLOR` is the albedo. Constant, as expected. |
| I | `LIGHT = vec4(COLOR.rgb*LIGHT_COLOR.rgb, 1.0)` | 111.12 | 111.12 | albedo × tint, **unattenuated**: 0.407. |
| A2 | `LIGHT = COLOR * LIGHT_COLOR` | 66.87 | 66.87 | Same rgb as I, but alpha = `COLOR.a*LIGHT_COLOR.a` → 0.234. **The engine multiplies LIGHT.rgb by LIGHT.a**, and `LIGHT_COLOR.a` = 0.574 here is the radial falloff. |
| G | `LIGHT = COLOR*LIGHT_COLOR*0.4` | 16.93 | — | Scaling the **vec4** scales rgb *and* alpha: 0.234 × 0.4² = 0.0379. |
| B | `LIGHT = COLOR*LIGHT_COLOR*LIGHT_ENERGY` | 16.93 | 45.48 | **Identical to G at E=0.4.** The issue's own prescription, and it applies the energy twice. |
| H | `LIGHT = vec4(COLOR.rgb*LIGHT_COLOR.rgb*LIGHT_ENERGY, 1.0)` | 49.04 | — | rgb-only scaling is linear: 0.407 × 0.4 = 0.163. |

### `LIGHT_COLOR.rgb` carries no falloff either — it is flat across the whole lit field

Probe E, same capture, sampled by distance:

| distance from the lamp | implied `LIGHT_COLOR.rgb` |
|---:|---|
| 2.2 tiles | (1.002, 0.696, 0.423) |
| 3.2 | (1.008, 0.695, 0.427) |
| 4.5 | (0.998, 0.693, 0.420) |
| 6.3 — outside the light's quad | (−0.007, 0.003, 0.016) |

## The semantics, stated

```
LIGHT_COLOR.rgb   the light's tint. CONSTANT over the light's quad; zero outside it.
LIGHT_COLOR.a     the radial falloff texture — this is where attenuation lives.
LIGHT_ENERGY      the Light2D's energy, exactly.
the blend         contribution = LIGHT.rgb * LIGHT.a, added.
```

## The two consequences that cost this project rounds

1. **Energy goes on the RGB only.** `COLOR * LIGHT_COLOR * LIGHT_ENERGY` scales the alpha too and
   squares the energy. The correct diffuse — the one a wall with no ShaderMaterial runs — is
   `vec4(COLOR.rgb * LIGHT_COLOR.rgb * LIGHT_ENERGY, COLOR.a * LIGHT_COLOR.a)`.

2. **`max(LIGHT_COLOR.rgb)` IS NOT A DELIVERED-LIGHT SCALAR.** It is the tint's largest channel —
   `1.002` at every lit fragment in this rig, because the Boundary's `ffb066` has a saturated red.
   `tier1_polish.gdshader` used it as its `delivered` quantity, so `pow(delivered, polish_exp)`
   computed `pow(1.0, 2) = 1.0` everywhere and **Ruling 70's superlinear light response never
   ran.** A delivered-light scalar must be built from `LIGHT_COLOR.a * LIGHT_ENERGY`.
