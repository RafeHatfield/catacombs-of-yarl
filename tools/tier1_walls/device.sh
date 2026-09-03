#!/bin/zsh
# THE WALL SESSION'S OWN SLOT ON THE HANDSET.
#
#   device.sh build     export, install, and stamp the wall review build
#   device.sh verify     ask the device what it is actually running
#
# WHY THIS FILE EXISTS AT ALL. Review builds install under a bundle id, and two live sessions
# sharing one id means the last install silently wins. That happened: a wall session overwrote the
# floor gate's build on this handset, and the only symptom was the floor's scene check going MISS
# — which reads as *your build is wrong* when the truth is *your build is gone*. The default slot
# `…catacombsofyarl.tier0` stays with the floor gate; the walls take their own, here, so it cannot
# be forgotten at three in the morning.
#
# EVERY MANIFEST BELOW IS LOAD-BEARING and the failure modes differ, which is the same reason
# `capture.sh` is a script and not a line in a README:
#   TIER1_ASHLAR      omit and the floor is a MAGENTA placeholder
#   TIER1_OVERLAYS    omit and plane-boundary occlusion disappears (bible §12.1's form)
#   TIER1_WALLS       omit and the walls are the tier-0 magenta mocks
#   TIER1_BINDINGS    omit and the walls are bare — §7.1's "show me what holds this" answered
#                     with nothing, silently
#   TIER1_WALLS_CAP   omit and the tops fall back to the per-tile top plane the gate rejected
set -e
cd "$(dirname "$0")/../.."

export TIER0_BUNDLE_ID="${TIER0_BUNDLE_ID:-com.rafehatfield.catacombsofyarl.tier1walls}"
export TIER0_APP_NAME="${TIER0_APP_NAME:-YARL Tier1 Walls}"
export TIER0_SCENE="${TIER0_SCENE:-res://src/Presentation/assets/tier0_harness/scenes/tier1_wall_review.json}"
export TIER0_THEME="${TIER0_THEME:-res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml}"
export TIER1_OVERLAYS="${TIER1_OVERLAYS:-res://src/Presentation/assets/tier1_floors/MANIFEST.json}"
export TIER1_ASHLAR="${TIER1_ASHLAR:-res://src/Presentation/assets/tier1_ashlar/MANIFEST.json}"
export TIER1_WALLS="${TIER1_WALLS:-res://src/Presentation/assets/tier1_walls/MANIFEST.json}"
export TIER1_BINDINGS="${TIER1_BINDINGS:-res://src/Presentation/assets/tier1_bindings/MANIFEST.json}"
export TIER1_WALLS_CAP="${TIER1_WALLS_CAP:-res://src/Presentation/assets/tier1_cap/MANIFEST.json}"

# The wall checks are opt-in in the verifier, because a floor gate build legitimately has no wall
# family and a check that fails on a build never meant to satisfy it teaches the operator to
# ignore checks. A wall build always wants them, so they are not optional here.
export TIER0_EXPECT_WALLS=1

# ── THE DEVICE GATE (standing order, Rafe) ────────────────────────────────────────────────────
# No build installs to the phone unless, on that exact build: its round is VALID, its diagnostic
# seat answered its axis, a whole-frame comparative seat ran without culling or calling it a
# regression, and every ruled fix is present. Checked by `install_gate.py` against the built
# artefacts and that round's seat records.
#
# Rafe's walk is the LAST gate, not the first working one. Every rule in this directory that
# depended on being remembered was eventually not remembered, so the gate is the thing that
# installs rather than a paragraph beside it.
#
# `--force-ungated` exists for ONE purpose: producing an artefact to MEASURE. It says so, loudly,
# every time, and `announce` still refuses — a build that cannot produce an announcement is a
# build nobody is being asked to walk.
gate() {
  if [ -z "${TIER1_GATE_ROUND:-}" ]; then
    echo "== GATE: refusing — set TIER1_GATE_ROUND to the round this build is for." >&2
    echo "   The gate checks THAT round's seats. A build with no round has not been judged." >&2
    return 1
  fi
  python3 tools/tier1_walls/install_gate.py --round "$TIER1_GATE_ROUND" \
          --axis "${TIER1_GATE_AXIS:-Q12}"
}

case "${1:-}" in
  build)
    shift
    if [ "${1:-}" = "--force-ungated" ]; then
      shift
      echo "== UNGATED BUILD — for measurement only. NOT for Rafe's walk, and no walk"
      echo "   announcement can be produced for it."
    elif ! gate; then
      echo "" >&2
      echo "== BLOCKED. This build does not go to the phone. Fix the failures above." >&2
      exit 3
    fi
    exec tools/tier0_harness/build_review_app.sh "$@" ;;
  announce)
    shift
    exec python3 tools/tier1_walls/install_gate.py \
         --round "${TIER1_GATE_ROUND:?set TIER1_GATE_ROUND}" \
         --axis "${TIER1_GATE_AXIS:-Q12}" --announce ;;
  verify) shift; exec tools/tier0_harness/verify_on_device.sh \
                      --out tools/tier1_walls/evidence "$@" ;;
  *) echo "usage: tools/tier1_walls/device.sh {build|verify|announce} [args...]" >&2; exit 2 ;;
esac
