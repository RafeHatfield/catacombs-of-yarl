#!/bin/zsh
# One floor capture, with every load-bearing flag present.
#
#   capture.sh <scene> <out-tag>
#
# EVERY FLAG HERE IS LOAD-BEARING and the failure modes differ, which is why this is a script and
# not a line in a README. All three of these have cost a device gate in this session:
#   --ashlar-floor      omit and the floor is the MAGENTA placeholder
#   --floor-overlays    omit and §12.1's plane-boundary occlusion silently disappears
#   --theme-config      omit and the tier-1 family lays under the tier-0 STUB THEME, which looks
#                       entirely plausible in a screenshot and was caught only by the device check
set -e
cd "$(dirname "$0")/../.."

SCENE=${1:-src/Presentation/assets/tier0_harness/scenes/tier1_floor_route_onroute.json}
TAG=${2:-fc_standing}

python3 tools/tier0_harness/capture_corridor.py \
  --out "tools/tier1_floors/evidence/${TAG}.png" \
  --theme-config res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml \
  --scene-spec "$SCENE" \
  --floor-overlays res://src/Presentation/assets/tier1_floors/MANIFEST.json \
  --ashlar-floor res://src/Presentation/assets/tier1_ashlar/MANIFEST.json \
  --log-out "tools/tier1_floors/evidence/${TAG}.log"
