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
if [ "$ARM" = "novoid" ]; then
  # THE §12.1 REMEDY UNDER TEST. Same material, same bindings, same cap — the ONLY difference is
  # `void_ring: 0` in the wall manifest, so nothing but the ring classification can explain a
  # change in the measurement. Composed by:
  #   compose_walls.py --arm material --void-ring 0 --out-suffix _novoid
  WALLDIR=src/Presentation/assets/tier1_walls_novoid
elif [ "$ARM" = "plant" ]; then
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
