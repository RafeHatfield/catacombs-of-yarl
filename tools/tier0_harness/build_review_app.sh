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
# TIER0_SCENE points the review build at an alternate scene spec. Added for the sighted round's
# §13.1 gate build: that round was judged on the MIXED DISTRIBUTION scene (§2.2 — room, corners
# and a one-wide chokepoint), not on the corridor junction the template names, and a device build
# showing a different scene than the round it is meant to ratify is the wrong picture. Same
# reasoning and same echo as TIER0_THEME: the substitution is announced, because the operator
# must be able to see which scene they are walking.
if [ -n "${TIER0_SCENE:-}" ]; then
  python3 - "$MARKER" "$TIER0_SCENE" <<'PY'
import json, sys
path, scene = sys.argv[1], sys.argv[2]
with open(path) as f:
    d = json.load(f)
d["scene"] = scene
with open(path, "w") as f:
    json.dump(d, f, indent=2)
PY
  echo "== scene override: $TIER0_SCENE"
fi
# TIER1_OVERLAYS points the review build at a floor family's MANIFEST.json — ART-BIBLE-v0 §8.3's
# incident overlays and §8.2.1's trodden channel. Same reasoning and same echo as the two
# overrides above: an overlay is NOT a tile role (a cell may carry none, one or two of them,
# chosen per instance), so it cannot ride in on TIER0_THEME. And a device build that quietly
# showed a floor with no incident on it would be the wrong picture at the one gate that decides
# anything (§13.1), which is why the substitution is announced rather than assumed.
if [ -n "${TIER1_OVERLAYS:-}" ]; then
  python3 - "$MARKER" "$TIER1_OVERLAYS" <<'PY'
import json, sys
path, manifest = sys.argv[1], sys.argv[2]
with open(path) as f:
    d = json.load(f)
d["floorOverlays"] = manifest
with open(path, "w") as f:
    json.dump(d, f, indent=2)
PY
  echo "== floor overlays: $TIER1_OVERLAYS"
fi
# STAMP THE BUILD'S OWN IDENTITY INTO THE MARKER.
#
# LOOP-PROCESS §2.3: every evidence file records the commit hash of the code that produced it,
# and a hash mismatch at a ruling invalidates the evidence. A DEVICE BUILD carried none — the
# headless captures stamp their commit, the app did not — so "is the thing on the phone the thing
# in the branch?" could only be answered by trusting whoever built it.
#
# That is exactly the question a device verification exists to answer, and it is why exit 0 from
# an export is not a deployment. The app now reports its commit and build time into Diag at boot,
# where they can be pulled back off the handset.
COMMIT="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
if [ -n "$(git -C "$ROOT" status --porcelain 2>/dev/null | head -1)" ]; then
  COMMIT="$COMMIT+dirty"
fi
BUILT_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
python3 - "$MARKER" "$COMMIT" "$BUILT_AT" <<'PY'
import json, sys
path, commit, built = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path) as f:
    d = json.load(f)
d["commit"] = commit
d["builtAt"] = built
with open(path, "w") as f:
    json.dump(d, f, indent=2)
PY
echo "== build identity: commit=$COMMIT built=$BUILT_AT"
echo "== marker written: $(basename "$MARKER")"
echo "== grid: $(python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));print("tile %s at x%s" % (d.get("tileSize","default"), d.get("tileScale","default")))' "$MARKER")"
echo "== bundle id: $BUNDLE_ID   name: $NAME"

# The marker is a new res:// file, so it must be imported before it can be packed.
"${GODOT:-/Applications/Godot_mono.app/Contents/MacOS/Godot}" --headless --path "$ROOT" --import >/dev/null 2>&1 || true

"$ROOT/tools/ios_build.sh" --bundle-id "$BUNDLE_ID" --name "$NAME" "$@"
