#!/bin/zsh
# THE RIG LADDER — Ruling 56 re-opened, on the corrected lamp (#174).
#
# Ruling 56 ratified radius 5.0 / falloff 1.00 / ambient 0.70 / energy 1.6 by Rafe walking the
# tier-one floor family on the reference device (§6.2.1). **Every one of those knobs was walked
# against a floor lit at energy 1.0 while the walls beside it ran at 1.6**, because
# tier1_polish.gdshader discarded LIGHT_ENERGY. The floor's delivered value has since moved by
# 1.6x. The rig was tuned against behaviour that no longer exists, so the ratification re-opens
# and this is the ladder it re-opens onto.
#
# ⚠ THESE STILLS ARE EVIDENCE, NOT THE GATE. §13.1: nothing is approved from a sheet of frames,
# and §6.2.1's whole point is that the pass happens at gameplay distance ON THE DEVICE. What is
# here is the record of what each knob does on the corrected lamp, so the walk starts informed
# rather than blind, and so the ratified values can be written back against something.
#
# ONE KNOB AT A TIME, bracketing the ratified value, everything else held at Ruling 56. A ladder
# that moved two knobs per rung could not attribute what the eye saw to either of them.
set -e
cd "$(dirname "$0")/../.."

SCENE=src/Presentation/assets/tier0_harness/scenes/tier1_combined_review.json
shot () { # $1 tag, rest: overrides
  local TAG=$1; shift
  python3 tools/tier0_harness/capture_corridor.py \
    --out "tools/tier1_floors/evidence/rig_${TAG}.png" \
    --theme-config res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml \
    --scene-spec "$SCENE" \
    --floor-overlays res://src/Presentation/assets/tier1_floors/MANIFEST.json \
    --ashlar-floor res://src/Presentation/assets/tier1_ashlar/MANIFEST.json \
    --boundary-wall res://src/Presentation/assets/tier1_walls/MANIFEST.json \
    --wall-bindings res://src/Presentation/assets/tier1_bindings/MANIFEST.json \
    --wall-cap res://src/Presentation/assets/tier1_cap/MANIFEST.json \
    --void-ring 1 "$@" \
    --log-out "tools/tier1_floors/evidence/rig_${TAG}.log"
}

shot ratified                                          # Ruling 56, unchanged, corrected lamp
shot energy_1.0  --light-energy 1.0                    # what the FLOOR was actually lit at
shot energy_1.3  --light-energy 1.3
shot energy_2.0  --light-energy 2.0
shot radius_4.0  --light-radius-tiles 4.0              # ~= the DELIVERED reach Ruling 56 recorded
shot radius_6.0  --light-radius-tiles 6.0
shot falloff_0.7 --light-falloff 0.7                   # below 1 carries light outward
shot falloff_1.5 --light-falloff 1.5                   # above 1 tightens the pool
shot ambient_0.5 --light-ambient-level 0.5
shot ambient_1.0 --light-ambient-level 1.0
