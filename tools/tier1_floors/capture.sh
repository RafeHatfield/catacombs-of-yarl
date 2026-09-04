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
#   --boundary-wall     omit and the walls are the tier-0 MAGENTA MOCKS
#   --wall-bindings     omit and the walls are bare
#   --wall-cap          omit and the walls have no top surface
#
# ⚠ THE WALL FLAGS ARE NOT SOMEBODY ELSE'S PROBLEM. A whole-frame critic judges the WHOLE FRAME,
# and three consecutive floor rounds spent most of their flip list on the magenta placeholders —
# one of them reading them as the FLOOR's lighting ("lit to RGB 255,20,140... a coloured stage
# light"). A floor cannot be judged in a frame that is half debug colour, and the wall family has
# been on main since the merge. Capturing without these was the same class of mistake as omitting
# the theme: the picture looks like a picture, and it is the wrong one.
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
  --boundary-wall res://src/Presentation/assets/tier1_walls/MANIFEST.json \
  --wall-bindings res://src/Presentation/assets/tier1_bindings/MANIFEST.json \
  --wall-cap res://src/Presentation/assets/tier1_cap/MANIFEST.json \
  --log-out "tools/tier1_floors/evidence/${TAG}.log"
