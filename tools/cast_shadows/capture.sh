#!/bin/bash
# CAST-SHADOWS CAPTURE — the props review room at the ratified rig, with the shadow flags.
#
#   tools/cast_shadows/capture.sh <tag> <occluders none|cw|ccw|all> [softness] [flicker 0|1] [scene]
#
# Everything else is the ratified rig and the same families as every combined capture; the
# void ring stays 1 so before/after frames differ in ONE thing. Writes
# tools/cast_shadows/evidence/<tag>.png + .log and prints the instrument's line.
set -e
cd "$(dirname "$0")/../.."
TAG="$1"; OCC="${2:-none}"; SOFT="${3:-2.0}"; FLICK="${4:-0}"
SCENE="${5:-src/Presentation/assets/tier0_harness/scenes/tier1_props_review.json}"
RING="${6:-1}"
DARK="${7:-1.0}"
EV=tools/cast_shadows/evidence
mkdir -p "$EV"
/Applications/Godot_mono.app/Contents/MacOS/Godot --path "$PWD" --resolution 750x1334 --art-scene-capture \
  --capture-out "$EV/$TAG.png" --capture-width 750 --capture-height 1334 \
  --corridor-scene "res://$SCENE" \
  --tile-theme-config res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml \
  --tile-size 32 --tile-scale 2.0 --light-ambient 1a1a22 --light-color ffb066 --light-energy 1.6 \
  --light-radius-tiles 6.0 --light-falloff 1.0 --light-ambient-level 1.5 \
  --floor-overlays res://src/Presentation/assets/tier1_floors/MANIFEST.json \
  --ashlar-floor res://src/Presentation/assets/tier1_ashlar/MANIFEST.json \
  --boundary-wall res://src/Presentation/assets/tier1_walls/MANIFEST.json --void-ring "$RING" \
  --wall-bindings res://src/Presentation/assets/tier1_bindings/MANIFEST.json \
  --wall-cap res://src/Presentation/assets/tier1_cap/MANIFEST.json \
  --occluders "$OCC" --shadow-softness "$SOFT" --fire-flicker "$FLICK" --shadow-darkness "$DARK" \
  > "$EV/$TAG.log" 2>&1 || true
grep -m1 "\[Tier1\] shadows:" "$EV/$TAG.log" || echo "  (no shadows line — did the build run?)"
python3 tools/cast_shadows/measure_occlusion.py "$EV/$TAG.png" "$EV/$TAG.log" "$SCENE" --tag "$TAG" --json "$EV/$TAG.json"
