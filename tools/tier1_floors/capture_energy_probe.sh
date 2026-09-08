#!/bin/zsh
# THE CONNECTION TEST'S CAPTURE — an energy sweep on the instrument scene.
#
#   capture_energy_probe.sh <tag-prefix> <energy> [energy...]
#
# WHY THE PROBE SCENE AND NOT THE REVIEW SCENE. `tier1_combined_review.json` REFUSES to write a
# PNG when a declared lit point comes back dark, which is correct and must not be weakened — but
# an energy sweep has to include energy 0, where every point is dark by construction. So the
# sweep runs through `tier1_combined_probe.json`, the legibility-free instrument scene round 28
# introduced for the null-polish control. NOTHING IS EVER JUDGED THROUGH IT (see its own comment).
#
# WHY A SWEEP AT ALL. Issue #174: `tier1_polish.gdshader` never read LIGHT_ENERGY, so every floor
# pixel was byte-identical at energy 0, 1.6 and 8.0 while 15% of the frame moved. This script is
# the measurement that says whether the lamp is connected — run it before the fix and after, and
# compare with measure_energy_response.py. A LOUDER frame is not the pass; a RESPONDING floor is.
#
# Every other flag matches capture_combined.sh exactly, and for the same reasons: a control frame
# that differed from the build in anything but the one variable would not be a control (§4.2).
set -e
cd "$(dirname "$0")/../.."

PREFIX=${1:?usage: capture_energy_probe.sh <tag-prefix> <energy> [energy...]}
shift

for E in "$@"; do
  TAG="${PREFIX}_e${E}"
  echo "== ${TAG} (energy ${E}) =="
  python3 tools/tier0_harness/capture_corridor.py \
    --out "tools/tier1_floors/evidence/${TAG}.png" \
    --theme-config res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml \
    --scene-spec src/Presentation/assets/tier0_harness/scenes/tier1_combined_probe.json \
    --floor-overlays res://src/Presentation/assets/tier1_floors/MANIFEST.json \
    --ashlar-floor res://src/Presentation/assets/tier1_ashlar/MANIFEST.json \
    --boundary-wall res://src/Presentation/assets/tier1_walls/MANIFEST.json \
    --wall-bindings res://src/Presentation/assets/tier1_bindings/MANIFEST.json \
    --wall-cap res://src/Presentation/assets/tier1_cap/MANIFEST.json \
    --void-ring 1 \
    --light-energy "$E" \
    --log-out "tools/tier1_floors/evidence/${TAG}.log"
done
