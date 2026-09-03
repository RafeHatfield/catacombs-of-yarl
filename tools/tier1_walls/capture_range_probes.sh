#!/bin/zsh
# Capture the range-probe scenes at three albedos.
#
# THREE, BECAUSE ONE ALBEDO CANNOT MEASURE THE WHOLE REACH. At eight bits the bright end clips
# and the dark end quantises, and both failures are silent: a clipped sample reports the sensor's
# ceiling as the scene's value, and a sample reading 8 against one reading 16 carries a rounding
# error larger than every effect being measured. So the near ranges are read off the LOW pair and
# the far ranges off the HIGH pair, and `range_profile.py` takes each range from the pair whose
# domain it is actually inside rather than averaging a good sample with a bad one.
set -e
cd "$(dirname "$0")/../.."

GODOT=/Applications/Godot_mono.app/Contents/MacOS/Godot
THEME=res://src/Presentation/assets/tier1_walls_probe/tile_themes_probe.yaml
EV=tools/tier1_walls/evidence

for A in 51 101 202; do
  python3 tools/tier1_walls/make_photometric_probe.py --albedo $A 2>/dev/null
  $GODOT --headless --path . --import >/dev/null 2>&1
  for S in a b; do
    python3 tools/tier0_harness/capture_corridor.py \
      --out $EV/range_${S}_a$(printf %03d $A).png \
      --theme-config $THEME \
      --scene-spec src/Presentation/assets/tier1_walls_probe/scenes/wall_range_${S}.json \
      --log-out $EV/range_${S}_a$(printf %03d $A).log 2>&1 | grep -aE "Captured|sha256"
  done
done
