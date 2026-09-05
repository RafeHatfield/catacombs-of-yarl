#!/bin/zsh
# ONE ROOM — the combined capture. Real floor, real walls, real void, no magenta anywhere.
#
#   capture_combined.sh [out-tag] [void-ring] [extra flags...]
#
# EVERY FLAG IS LOAD-BEARING and the failure modes differ, which is why this is a script and not
# a line in a README. All of these have cost a round in this project:
#   --ashlar-floor      omit and the floor is the MAGENTA placeholder
#   --floor-overlays    omit and §12.1's plane-boundary occlusion silently disappears
#   --theme-config      omit and the tier-1 family lays under the tier-0 STUB THEME, which looks
#                       entirely plausible in a screenshot and was caught only on the device
#   --boundary-wall     omit and the walls are the tier-0 MAGENTA MOCKS
#   --wall-bindings     omit and the walls are bare — §7.1's "show me what holds this", answered
#                       with nothing, silently
#   --wall-cap          omit and the walls have no top surface
#
# ── WHY --void-ring 1 IS THE DEFAULT HERE, AND WHY IT IS ON A COMMAND LINE ────────────────────
#
# §12.1a (Rafe, 2026-09-03) RULED the void dark by OCCLUSION rather than by a ring, and the wall
# manifest carries `void_ring: 0` for it. **That ruling's implementation is recorded-outstanding
# in the clause's own text**: "the renderer currently lights wall cells regardless of what stands
# between them and the lamp". So at zero, nothing is void and the lamp lights every cell of
# unexcavated mass out to the map edge. Measured on this scene's own first combined capture:
#
#     void=0(choice=0,ring>0)  face_suppressed=192  cap=216+0void
#
# — 192 cells of solid rock, lit, and a room with no dark beyond it. That is exactly the
# consequence a frame critic measured when the ring was first dropped: "Light is passing through
# solid rock ... the unexcavated mass is 77% as bright as the walked surface."
#
# So this round runs the FLAT-DARK FALLBACK — the ring — and says so, in the log of every frame
# it produces, because the alternative is judging one room in a frame that has no outside.
# The cost is named rather than hidden: a ring is a classification that changes at a cell
# boundary, so it puts a luminance step on the grid, and round 8's seat read that step unaided as
# "two perfectly straight vertical seams in the darkness". THAT COST IS THIS ROUND'S, AND IT IS
# FLAGGED IN THE ROUND REPORT. It is not a re-ruling of §12.1a, which stands: the occluder pass
# is the real fix and it is a later round with a walk behind it.
#
# ON THE COMMAND LINE RATHER THAN IN THE MANIFEST because the manifest's 0 is a RULED value and a
# round does not get to quietly move one. `--void-ring` is echoed into every capture log with the
# manifest value beside it, so no frame can circulate without carrying its own departure.
set -e
cd "$(dirname "$0")/../.."

TAG=${1:-combined}
RING=${2:-1}
shift 2 2>/dev/null || true

python3 tools/tier0_harness/capture_corridor.py \
  --out "tools/tier1_floors/evidence/${TAG}.png" \
  --theme-config res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml \
  --scene-spec src/Presentation/assets/tier0_harness/scenes/tier1_combined_review.json \
  --floor-overlays res://src/Presentation/assets/tier1_floors/MANIFEST.json \
  --ashlar-floor res://src/Presentation/assets/tier1_ashlar/MANIFEST.json \
  --boundary-wall res://src/Presentation/assets/tier1_walls/MANIFEST.json \
  --wall-bindings res://src/Presentation/assets/tier1_bindings/MANIFEST.json \
  --wall-cap res://src/Presentation/assets/tier1_cap/MANIFEST.json \
  --void-ring "$RING" \
  --log-out "tools/tier1_floors/evidence/${TAG}.log" "$@"
