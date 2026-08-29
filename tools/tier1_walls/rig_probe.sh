#!/bin/zsh
# WHAT A DIFFERENT RIG WOULD COST — evidence for a ruling, not a proposal.
#
# The stack finding says §6.5's "floor between the planes" is unreachable on the ratified rig at
# any authorable value, and §6.2.1's own reasoning points at the rig rather than the art: *"the
# rig is one table of numbers and the corpus is every asset in the game. Tune the cheap thing."*
# Ruling 56 ratified the rig ON THE DEVICE, BY EYE, so moving it is a re-gate and not a builder's
# decision. What a builder can honestly do is show what each setting buys and what it spends.
#
# THE SCENE'S OWN GUARD IS THE SECOND HALF OF THE MEASUREMENT. `tier1_wall_review.json` declares
# two points that must stay DARK, because §6.2.1 rules the pass *"not a licence to flood the
# Boundary with light"* and *you begin as the only thing here that burns* is register. A rig that
# lights the walls by drowning the arc fails the capture rather than passing it, and the log says
# which point it drowned.
set -e
cd "$(dirname "$0")/../.."

SCENE=src/Presentation/assets/tier0_harness/scenes/tier1_wall_review.json
EV=tools/tier1_walls/evidence

probe () {
  local tag=$1 falloff=$2 radius=$3
  local extra=()
  [ -n "$falloff" ] && extra+=(--light-falloff "$falloff")
  [ -n "$radius" ] && extra+=(--light-radius-tiles "$radius")
  echo "-- $tag  falloff=${falloff:-ratified} radius=${radius:-ratified}"
  python3 tools/tier0_harness/capture_corridor.py \
    --out $EV/rig_$tag.png \
    --theme-config res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml \
    --scene-spec $SCENE \
    --floor-overlays res://src/Presentation/assets/tier1_floors/MANIFEST.json \
    --ashlar-floor res://src/Presentation/assets/tier1_ashlar/MANIFEST.json \
    --boundary-wall res://src/Presentation/assets/tier1_walls_compensated/MANIFEST.json \
    --wall-bindings res://src/Presentation/assets/tier1_bindings_compensated/MANIFEST.json \
    "${extra[@]}" \
    --log-out $EV/rig_$tag.log 2>&1 | grep -aE "Captured|REFUSED" || true
  grep -a "legibility(" $EV/rig_$tag.log | grep -v DIAG \
    | sed -E 's/.*legibility\(([0-9,]+)\) expect=([a-z]+) +ratio=([0-9.]+).*(OK|FAIL).*/     (\1) \2 \3 \4/' || true
}

probe ratified   ""     ""
probe f070       0.70   ""
probe f050       0.50   ""
probe r065       0.65   6.5
probe r080       0.45   8.0
