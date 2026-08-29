# Tier 1 — the Boundary's walls, and the void

**The round that retires the magenta mocks — and the round that found the rig is in the way.**

Nothing here lands. ART-BIBLE-v0 §13.1 gives the landing gate to Rafe, in-scene, on device.

---

## Read this first

`STACK-FINDING.md`. §6.5's value stack does not survive §6.2's falloff, the measurement is in
that file, and it is a **ruling trigger** returned under LOOP-PROCESS §1.1.4(b) rather than a
number this session picked its way around. Everything below was built with that finding open, as
**two arms**, because the ruling is Rafe's and a gate needs something to rule on.

---

## Running it

```bash
# --- the instruments, first. No pass counts until they have demonstrated they can fail. ---
python3 tools/tier1_walls/wall_laws.py --controls       # 6 planted defects, one per axis
python3 tools/tier1_walls/light_field.py --controls     # 4 photometric controls

# --- the measurements the art is derived FROM, not decorated with ---
python3 tools/tier1_walls/derive_stack.py               # the anchor, re-derived at consumption
zsh    tools/tier1_walls/capture_range_probes.sh        # flat-albedo probes at three albedos
python3 tools/tier1_walls/range_profile.py              # §6.2.1's owed item, answered

# --- composition. Generation supplies material; procedure supplies architecture (§13.7). ---
python3 tools/tier1_walls/compose_walls.py --arm material --grain-amp 1.0
python3 tools/tier1_walls/compose_walls.py --arm compensated --grain-amp 1.0
python3 tools/tier1_walls/compose_bindings.py --arm material
python3 tools/tier1_walls/compose_bindings.py --arm compensated
python3 tools/tier1_walls/plant_walls.py \
        --src src/Presentation/assets/tier1_walls_compensated \
        --out src/Presentation/assets/tier1_walls_plant

dotnet build CatacombsOfYarl.Presentation.csproj        # ⚠ THE ROOT ONE
/Applications/Godot_mono.app/Contents/MacOS/Godot --headless --path . --import   # ⚠ ROOT PATH

# --- in scene, lit, at device pixel size (LOOP-PROCESS §2.1). Every flag is load-bearing. ---
zsh tools/tier1_walls/capture.sh compensated \
    src/Presentation/assets/tier0_harness/scenes/tier1_wall_review.json r08_family

# --- §13.8's question, on the capture rather than on the source ---
python3 tools/tier1_walls/measure_wall_amplitude.py \
        --scene src/Presentation/assets/tier0_harness/scenes/tier1_wall_review.json \
        --png tools/tier1_walls/evidence/r08_family.png \
        --log tools/tier1_walls/evidence/r08_family.log \
        --assets src/Presentation/assets/tier1_walls_compensated --tag gate

# --- the blind seats. Round is VOID if the plant seat misses the plant. ---
python3 tools/tier1_walls/run_seats.py W1 W2 W3 W4 --round 2 \
        --family r08_family.png --plant r08_plant.png

# --- ON DEVICE. The only thing that decides anything. ---
TIER0_SCENE=res://src/Presentation/assets/tier0_harness/scenes/tier1_wall_review.json \
TIER0_THEME=res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml \
TIER1_OVERLAYS=res://src/Presentation/assets/tier1_floors/MANIFEST.json \
TIER1_ASHLAR=res://src/Presentation/assets/tier1_ashlar/MANIFEST.json \
TIER1_WALLS=res://src/Presentation/assets/tier1_walls_compensated/MANIFEST.json \
TIER1_BINDINGS=res://src/Presentation/assets/tier1_bindings_compensated/MANIFEST.json \
tools/tier0_harness/build_review_app.sh

tools/tier0_harness/verify_on_device.sh
```

A fresh worktree needs the build and the import before any capture renders, and **the import must
be re-run after any PNG is rewritten** — otherwise the engine draws the previous bytes and nothing
says so.

---

## The parts

| path | what |
|---|---|
| `STACK-FINDING.md` | **the session's first deliverable.** §6.2.1's owed measurement, answered. |
| `derive_stack.py` | the anchor, re-derived at consumption (§5.6), area-weighted at two field sizes (§5.7). |
| `make_photometric_probe.py` | paints the scene one flat albedo. The capture is then a picture of the rig's multiplier. |
| `light_field.py` | reads that multiplier, with four controls — and two masks, because translucent interface scales wrongly and clipped pixels do not scale at all. |
| `range_profile.py` | the compression at every range the lamp reaches, and what §6.5 would cost at each. |
| `mask_census.py` | which wall segments a scene actually contains — and the §3 violation the mask table was hiding. |
| `compose_walls.py` | the family. Two planes, edge-matched, two orientations, two arms. |
| `compose_bindings.py` | the orc layer. Placed per cell, never baked into a segment (§8.3.1). |
| `plant_walls.py` | LOOP-PROCESS §4's plant — a picturesquely ruined wall. Never lands, never shown to Rafe. |
| `wall_laws.py` | **the instrument.** Six geometric tests, six plants, and a legal family that must come back clean. |
| `measure_wall_amplitude.py` | §13.8 on the capture: is the material there loudly enough to exist, and where does it stop being so. |
| `rig_probe.sh` | what a different rig would buy and what it would spend. Evidence for a ruling, not a proposal. |
| `run_seats.py`, `seat_prompt.txt` | the blind seats and the plant control. |
| `REPORT.md` | what the round found. Read this one. |

Engine side: `Tier1BoundaryWall` (masks, rings, the void, edge-matched selection, the binding
planner), `ReviewRigPanel.AddVoidRow` (§13.1's choice, live), and one new line in `Main` —
`[Tier0] grid map:` — so an off-line measurement never has to guess the camera again.

---

## Rules this directory holds itself to

**No instrument scores a register clause** (§13.4). Every test in `wall_laws` is geometry — value
populations, row profiles, per-pixel variance across a set, edge continuity, joint pitch.
*Nothing is staged*, *the art plays it straight* and *nothing is ruined, things are used up* have
**NO INSTRUMENT** here and are carried at the human gate. There is no dread score.

**No pass counts until the instrument has failed** (§13.5). `wall_laws --controls` plants one
defect per axis and requires each to fire, *and* requires the legal family to come back clean.
Three of the six bounds were rewritten because their plants came back SILENT and one because it
failed the legal family — each correction is recorded in the code beside the test it fixed, since
an instrument that was quietly retuned until it agreed is not an instrument.

**A measurement of the source is not a measurement of the asset.** `measure_wall_amplitude` takes
the joint/block mask from the composer, which knows it exactly, and every value from the lit
capture. The two columns it prints are the finding: Weber contrast is flat with range because the
pipeline is multiplicative, and the delivered LEVELS fall from 30 to 2.5 over four tiles.

**The parts bin supplies a statistic, not pixels — and that was measured, not assumed.** The
first version of this family laid residual patches cut from the wall gauntlet's round-7 stock as
grain, and the assembled run came back as brick wallpaper: a box blur wide enough to remove a
joint does not remove a course, so the donor's own bond arrived inside every block as structure.
The donors' residual amplitude and its surviving periodicity are both in the manifest.

**Nothing here rules the void.** Three near-black candidates ship and the rig panel switches
between them. §13.1 gives that choice to Rafe, in the scene, on the device.
