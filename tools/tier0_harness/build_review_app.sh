#!/bin/bash
# Tier 0 REVIEW BUILD — put the lit review corridor on the reference device.
#
# ART-BIBLE-v0 §13.1: the verdict comes from the production renderer, in the lit scene, at true
# display size, ON DEVICE. An iOS app gets no command line, so --corridor-scene cannot reach it.
# This script bakes REVIEW_BUILD.json into the export, which makes the app boot straight into the
# corridor (see ReviewBuildMarker), and installs it under its OWN bundle id so it sits beside the
# real game instead of replacing it.
#
# The marker is written before the export and removed afterwards, always — a leftover marker
# would turn the next ordinary build into a review build without anyone noticing.
#
#   tools/tier0_harness/build_review_app.sh                 # build + install the review build
#   tools/tier0_harness/build_review_app.sh --no-install    # build only
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MARKER="$ROOT/src/Presentation/assets/tier0_harness/REVIEW_BUILD.json"
TEMPLATE="$MARKER.template"
BUNDLE_ID="${TIER0_BUNDLE_ID:-com.rafehatfield.catacombsofyarl.tier0}"
NAME="${TIER0_APP_NAME:-YARL Tier0}"

[ -f "$TEMPLATE" ] || { echo "missing $TEMPLATE" >&2; exit 1; }

cleanup() { rm -f "$MARKER"; echo "== marker removed (a leftover would silently make the next build a review build)"; }
trap cleanup EXIT

cp "$TEMPLATE" "$MARKER"
# TIER0_THEME points the review build at an alternate tile theme — a §6.4 survivor set, say —
# without editing the committed template. The template stays the default so an ordinary review
# build is unchanged, and the substitution is echoed because a device build that quietly showed
# different tiles than the operator expected would be the worst possible review artefact.
if [ -n "${TIER0_THEME:-}" ]; then
  python3 - "$MARKER" "$TIER0_THEME" <<'PY'
import json, sys
path, theme = sys.argv[1], sys.argv[2]
with open(path) as f:
    d = json.load(f)
d["themeConfig"] = theme
with open(path, "w") as f:
    json.dump(d, f, indent=2)
PY
  echo "== theme override: $TIER0_THEME"
fi
echo "== marker written: $(basename "$MARKER")"
echo "== grid: $(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print("tile %s at x%s" % (d.get("tileSize","default"), d.get("tileScale","default")))' "$MARKER")"
echo "== bundle id: $BUNDLE_ID   name: $NAME"

# The marker is a new res:// file, so it must be imported before it can be packed.
"${GODOT:-/Applications/Godot_mono.app/Contents/MacOS/Godot}" --headless --path "$ROOT" --import >/dev/null 2>&1 || true

"$ROOT/tools/ios_build.sh" --bundle-id "$BUNDLE_ID" --name "$NAME" "$@"
