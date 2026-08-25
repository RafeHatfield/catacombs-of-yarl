# Tier 0 — the review harness

**The apparatus that judges art. Not art.**

`ART-BIBLE-v0.md` §13.1: *no candidate is ever approved from a contact sheet. Verdicts come from
the production renderer, in the lit scene, at true display size, on device.*

§6.3: *assets are authored to **receive** light, not to depict it* — and a receive-light asset
"looks flat and slightly disappointing on a contact sheet". A capture taken without a light rig
therefore judges a candidate with the wrong instrument. That is why lighting is part of this
harness and not a later addition, and why nothing else in the pipeline could start before it.

---

## What it does

Assembles arbitrary candidate floor and wall tiles into a **lit corridor with a junction**,
renders it through the **production renderer**, and captures it at the reference device's exact
pixel size (750×1334, iPhone SE, portrait — §4.1).

The junction is load-bearing. The blind critic is asked *which way would you walk*, and a
straight corridor cannot answer that.

## Running it

```bash
# one capture
python3 tools/tier0_harness/capture_corridor.py --out /tmp/corridor.png

# the positive controls — the harness proving it can fail
python3 tools/tier0_harness/run_controls.py

# the §6.4 three-arm receive-light probe, side by side under one identical rig
python3 tools/tier0_harness/capture_probe_arms.py

# put the corridor on the actual device, side by side with the real game
tools/tier0_harness/build_review_app.sh
```

## The parts

| Path | What |
|---|---|
| `harness_config.yaml` | Resolution, tile size, light rig. Every value labelled **RULED** or **UNDERIVED**. |
| `capture_corridor.py` | Invokes the engine, captures, prints the evidence trail. |
| `run_controls.py` | The four positive controls. |
| `capture_probe_arms.py` | §6.4 arms A/B/C under one identical rig + side-by-side sheet. |
| `make_stub_tiles.py` | Obviously-fake programmer-art fixtures. Not art, not a palette. |
| `build_review_app.sh` | Bakes the review marker, builds, installs under its own bundle id. |
| `src/Logic/Core/CorridorReviewSceneBuilder.cs` | Corridor geometry from authored JSON. No Godot. |
| `src/Presentation/Map/ReviewLighting.cs` | Ambient darkness + carried warm point light. |
| `src/Presentation/Map/ReviewBuildMarker.cs` | Makes the corridor bootable on device. |
| `src/Presentation/assets/tier0_harness/scenes/corridor_junction.json` | The authored corridor. |

## Rules this harness holds itself to

**No number here is law unless the bible derived it.** `harness_config.yaml` labels every value.
The engine **refuses to default any light value** (`Main.ReadLightParams` throws), so no capture
can be produced by an undeclared rig, and every capture logs the rig that made it.

**Tile size is a parameter, never a constant** (§4.3 marks canvas sizes PLACEHOLDER). It is
declared in config and passed through. *Known limit:* `TopDownRenderer.TileWidth` is still a
hard-coded `24`, so changing the parameter today produces tiles the renderer still draws on a
24px grid. Making that a genuine engine parameter is separate work.

**No instrument's pass counts until it has demonstrated it can fail** (§13.5, LOOP-PROCESS §4).
`run_controls.py` plants a real defect for each control and asserts the harness notices.

**Candidates are injected by config, never by overwriting files.** Pointing
`--tile-theme-config` at a different `tile_root` is the whole seam. The retired Oryx review path
overwrote live sprite files and reverted afterwards; nothing here has to be reverted.

## Two traps this harness fell into, kept as warnings

**A three-wide corridor is a room.** The first capture carved a 3-tile-wide trunk. Every cell in
it has three or more open neighbours, so the junction check reported `junction=YES at (8,4)` —
the top of a straight corridor. `HasJunction` now also requires all four diagonals solid, and
`CorridorReviewSceneBuilderTests` locks the false positive.

**A one-wide corridor renders exactly one floor role.** `FloorComposer` Pass 2 marks any
wall-adjacent tile `Dark` and never overrides it. In a one-wide corridor *every* floor cell is
wall-adjacent, so `floor_primary`, `floor_accent` and `floor_worn` are never drawn. The
scene-is-real control initially swapped only `floor_primary`, planted its defect in a dead role,
and passed a swap through with **0.0000%** of pixels changed. **This is an open ruling, not a
solved problem** — see the session report: a Tier 1 floor candidate reviewed in this corridor is
only ever seen through its `floor_dark` variant.

## What this harness deliberately does NOT do

- It does not generate art, derive a palette, or propose one.
- It does not lint, score, or census anything. `tools/art_lint/` is untouched.
- It does not instrument any register clause (§13.4). There is no dread score.
- It does not decide anything. It produces evidence; §13.2 gives the verdict to Rafe, in-scene,
  on device.
