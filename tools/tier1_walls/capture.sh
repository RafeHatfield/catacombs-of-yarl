#!/bin/zsh
# One wall capture, with every load-bearing flag present.
#
#   capture.sh <arm> <scene> <out-tag> [void-choice]
#
# EVERY FLAG HERE IS LOAD-BEARING and the failure modes differ, which is why this is a script and
# not a line in a README:
#   --ashlar-floor      omit and the floor is a MAGENTA placeholder
#   --floor-overlays    omit and the plane-boundary occlusion disappears (bible 12.1's form)
#   --boundary-wall     omit and the walls are the tier-0 magenta mocks
#   --wall-bindings     omit and the walls are bare - section 7.1's "show me what holds this"
#                       answered with nothing, silently
set -e
cd "$(dirname "$0")/../.."

ARM=${1:-material}
SCENE=${2:-src/Presentation/assets/tier0_harness/scenes/tier1_floor_review.json}
TAG=${3:-wall}
VOID=${4:-0}

WALLDIR=src/Presentation/assets/tier1_walls
BINDDIR=src/Presentation/assets/tier1_bindings
CAPDIR=src/Presentation/assets/tier1_cap
# `novoid` WAS AN ARM HERE AND IS NOT ANY MORE. The §12.1 remedy was tested as a side-by-side
# variant (`--out-suffix _novoid`) and then RULED, so `void_ring: 0` is what the material arm is
# composed at — the two directories were byte-identical across all 165 PNGs, and keeping both
# would have been two sources of truth for one family. `r22_novoid.png` reproduces from
# `capture.sh material` now.
if [ "$ARM" = "plant" ]; then
  # LOOP-PROCESS §4: the plant must differ from the family in THE RUIN AND NOTHING ELSE, or a
  # seat that culls it has not told us it can see the register — only that it can see a
  # difference. So the plant swaps the wall faces and keeps the family's own bindings and its own
  # cap, byte for byte. Rounds 3 and 6 went void because the plant was culled for something the
  # family shared; the way to stop paying for that is to hold every other variable here.
  WALLDIR=src/Presentation/assets/tier1_walls_plant
elif [ "$ARM" != "material" ]; then
  WALLDIR=${WALLDIR}_${ARM}
  BINDDIR=${BINDDIR}_${ARM}
  CAPDIR=${CAPDIR}_${ARM}
fi

python3 tools/tier0_harness/capture_corridor.py \
  --out tools/tier1_walls/evidence/${TAG}.png \
  --theme-config res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml \
  --scene-spec "$SCENE" \
  --floor-overlays res://src/Presentation/assets/tier1_floors/MANIFEST.json \
  --ashlar-floor res://src/Presentation/assets/tier1_ashlar/MANIFEST.json \
  --boundary-wall res://$WALLDIR/MANIFEST.json \
  --wall-bindings res://$BINDDIR/MANIFEST.json \
  --wall-cap res://$CAPDIR/MANIFEST.json \
  --void-choice "$VOID" \
  --log-out tools/tier1_walls/evidence/${TAG}.log
