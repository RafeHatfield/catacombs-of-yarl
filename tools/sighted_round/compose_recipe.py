#!/usr/bin/env python3
"""THE SIGHTED ROUND — STEP 2. Rebuild the wall segments to WALL-RECIPE.md.

WHAT CHANGES AND WHAT DOES NOT
------------------------------
Changes: the VALUES and the PROPORTIONS of the wall tiles, per the measured recipe.
Unchanged: the mask table (recipe §4.2 - copying the bar's autotile convention would be
conformance, not a lesson crossing), the parts bin, the binding-overlay policy (§7.1), the
renderer, and the floors.

Material comes from the existing parts bin - the wall gauntlet's round-07 face parts, the same
source `compose_walls.py` used. **No bar pixel is used, read, or blended here.** The bar's
contribution to this file is six numbers, and they are in WALL-RECIPE.md with their derivations.

THE RECIPE, AS BUILT (WALL-RECIPE.md §5)
-----------------------------------------
    wall-top albedo     1.15 x floor
    wall-face albedo    0.60 x floor
    face / top          0.52
    top band            15 px, rows 0-14
    turn                row 15
    face                16 px, rows 16-31
    contact occlusion   the ladder, 5 px, at the face's BOTTOM edge
    bright cap at turn  OFF (recipe §4.1 - flagged, needs a wear system)

⚠ THE OCCLUSION IS NOT WHERE THE RECIPE SAYS IT BELONGS, AND THAT IS A KNOWN SHORTFALL.
Recipe §3.1 measured that the bar puts the seam on the FLOOR cell south of the wall, on its own
layer, 0.29 tile deep - and §12.1 already ruled that occlusion "is not on the object at all".
This renderer cannot place it there directionally: `FloorComposer.ApplyEdgeDarkening` marks a
floor cell Dark when ANY of its eight neighbours is a wall, so it cannot tell which side the
wall is on, and a north-edge ramp applied through that path would stripe every corridor cell.
Rather than fake it, the seam is built where §12.1's own sentence also permits - *"on the wall's
own edge, only where floor is adjacent"* - i.e. the bottom edge of the face tile, which exists
only on face tiles and therefore only where floor lies south. Depth 5 px, the deepest value the
composition spike has tested, NOT the recipe's 9 px: 9 px of a 16 px face would crush the plane
the round is trying to make readable. **The floor-side placement is carried as a finding.**
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools/floor_remediation"))
import preconditions as PRE       # noqa: E402
import ring_instrument as RI      # noqa: E402

PARTS = os.path.join(REPO, "tools/pixellab/wall_gauntlet/rounds/round07/images")
PART_FILES = ["r07_00.png", "r07_01.png", "r07_02.png", "r07_03.png"]
PART_ROWS = (5, 31)               # the band compose_walls.py established as usable
FLOORS = os.path.join(REPO, "tools/floor_remediation/remediated")
ASSETS_REL = "src/Presentation/assets/sighted_round"
ASSETS = os.path.join(REPO, ASSETS_REL)

T = 32
FLOOR_IDS = {9401: "C-GAB", 9402: "A-HEB"}
FACE_IDS = [9500, 9501, 9502, 9503]
TOP_IDS = [9510, 9511, 9512, 9513]

# --- the recipe, as numbers. Every one of these has a derivation in WALL-RECIPE.md. -----------
# ROUND 3 - AUTHOR TO DELIVER, NOT TO STATE. Round 2's seat: "A's face sits at 0.65-0.81 of its
# top and its wall top is DARKER than its floor" - both true on screen and neither true in the
# art, because the lamp is the player and the player stands south of a north wall. Measured
# delivery ratios through this rig (checks.py): top/floor 1.15 authored -> 0.718 delivered
# (x0.624), face/top 0.52 authored -> 0.77 delivered (x1.48). So the recipe's numbers are
# DELIVERY targets and the albedo is solved backwards from them.
DELIVER_TOP_OVER_FLOOR = 1.15
DELIVER_FACE_OVER_TOP = 0.52
TOP_DELIVERY = 0.624       # measured, this rig only
TOP_ALBEDO = 1.80          # = 1.15 / 0.624, clamped just under the clip at 1.85x floor
FACE_ALBEDO = 0.60         # §1.2  enclosure: a vertical plane is self-occluded under a top ambient
# ROUND 3. Recipe §4.4, measured not guessed: the carried light sits SOUTH of a north wall, so
# the face is one tile nearer the lamp than its own top and the engine brightens it relative to
# the top. Authored 0.52 arrived as 0.77 lit - a compression of 1.48. To DELIVER the bar's 0.52
# the art must author 0.52/1.48. This compensates for a measured falloff; it does not depict a
# light direction, so §6.3 holds. It is FLAGGED in §4.4 because it ties the art to a rig whose
# values are still PLACEHOLDER.
LIGHT_COMPRESSION = 1.48
COMPENSATE = True
TOP_ROWS = (0, 15)         # §2.1  15 px
TURN_ROW = 15              # §2.1
FACE_ROWS = (16, 32)       # §2.1  16 px = 0.50 tile
TOP_SPREAD = 16.0          # contrast within the top band (joints darker)
# ROUND 2. Both round-1 seats culled BOTH Yarl arms `wrong-projection` for the same reason, and
# neither was shown the other's verdict:
#   "A top surface does not show five courses of face-brick."            (S1, on the recipe arm)
#   "the brick coursing above it has the same pitch, proportion and
#    orientation as below, so it is not a top surface - it is more face." (S2, on the control)
# Measured on the bar by the same seats, independently: the top plane is FLAT - "held at exactly
# 90, 91.5% of those pixels are literally 90" - broken only by 2px joints on a half-tile grid.
# Register derivation, so this is not conformance: §12 grants the top plane no interior detail,
# §4.2 keeps centres open with events at edges, and §8.1's wear is traffic-driven - nothing walks
# on a wall top, so nothing has ever happened to it. A surface with no incident has no texture.
TOP_FLAT = True
TOP_JOINT_PITCH = 16       # px - half a tile, the bar's own block grid
TOP_JOINT_PX = 2
TOP_JOINT_RATIO = 0.78     # joint value against the plane, measured on the bar (70.4 / 89.5)
FACE_SPREAD = 20.0         # contrast within the face (courses)
OCCLUSION = [(31, 64), (30, 64), (29, 38), (28, 38), (27, 13)]   # §3.2 ladder, wall's own edge
# ROUND 4. THREE seats, across three rounds, none shown the others, all named the same missing
# element - and it is the number §4.1 flagged and switched off:
#   "rows 30-31 jump to L~125 (a 2px lip catch)"                            (r1 S1, on the bar)
#   "a 2px cap course at y30-31 at 124-147"                                 (r1 S2, on the bar)
#   "B has a top plane, a CHAMFERED NEAR EDGE and a front face at three
#    separated values; A has one flat band"                                 (r3 S1, on ours)
# The flag was raised because §12.1's worked example culled a pale coping ribbon. The distinction
# that makes this legal is the one §12.1 itself draws: that ribbon ran along EVERY wall edge for
# its entire length; this sits only at the top-to-face TURN, which exists only on a tile that has
# floor to its south. It answers to the geometry. The ring instrument adjudicates rather than
# this comment - and it is run on every tile below.
CAP_ON = True
CAP_RATIO = 1.42           # measured on the bar: 129.8 cap against an 89.5 top band
QUANT_LEVELS = 6           # keep each band's palette small (§5.1 discipline)


def lum(a):
    return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114


def retone(band, target_mean, spread):
    """Map a band's luminance onto a target mean and spread, preserving hue.

    A uniform per-pixel gain on RGB, so nothing shifts colour; the curve is linear between the
    band's own 10th and 90th percentiles so a single speck cannot set the range. Quantised
    afterwards to keep the palette small.
    """
    L = lum(band)
    lo, hi = np.percentile(L, 10), np.percentile(L, 90)
    if hi - lo < 1e-6:
        newL = np.full_like(L, target_mean)
    else:
        newL = target_mean + (L - (lo + hi) / 2.0) * (2.0 * spread / (hi - lo))
    newL = np.clip(newL, 4, 250)
    gain = newL / np.maximum(L, 1.0)
    out = np.clip(band * gain[..., None], 0, 255)
    # quantise by luminance into QUANT_LEVELS bands, each taking that band's mean colour
    q = np.clip(((lum(out) - newL.min()) / max(newL.max() - newL.min(), 1e-6)
                 * QUANT_LEVELS).astype(int), 0, QUANT_LEVELS - 1)
    res = out.copy()
    for k in range(QUANT_LEVELS):
        m = q == k
        if m.any():
            res[m] = out[m].mean(0)
    return res


def top_plane(value, phase, rows):
    """A wall top as seen from above: one flat value, broken only by the joints between blocks.

    NOT the face material re-toned. That was round 1's defect and both seats named it.
    """
    out = np.zeros((rows, T, 3), dtype=float)
    base = np.array([value, value, value], dtype=float)
    # a hair of hue from the face material would be invented here, so the plane is neutral and
    # the engine's warm light does the colouring - §6.3, the art receives light.
    out[:, :] = base
    j = base * TOP_JOINT_RATIO
    for x in range(phase % TOP_JOINT_PITCH, T, TOP_JOINT_PITCH):
        out[:, x:x + TOP_JOINT_PX] = j
    for y in range((phase * 7) % TOP_JOINT_PITCH, rows, TOP_JOINT_PITCH):
        out[y:y + TOP_JOINT_PX, :] = j
    return out


def apply_occlusion(tile):
    """The ladder, black, on the face's bottom edge. §12.1: on the wall's own edge, only where
    floor is adjacent - which is true of a face tile by construction."""
    out = tile.astype(float)
    for row, alpha in OCCLUSION:
        f = alpha / 255.0
        out[row] = out[row] * (1.0 - f)
    return out


def build(part, floor_mean, phase=0):
    """One face tile and one top tile from one part.

    The FACE keeps the parts-bin masonry - a face is coursed, and that is correct. The TOP is
    authored flat (see TOP_FLAT), because a top surface showing courses reads as elevation.
    """
    src = part[PART_ROWS[0]:PART_ROWS[1]].astype(float)
    top_t = TOP_ALBEDO * floor_mean
    face_t = FACE_ALBEDO * floor_mean
    if COMPENSATE:
        face_t = top_t * DELIVER_FACE_OVER_TOP / LIGHT_COMPRESSION

    # TOP tile: the whole 32 rows are top plane.
    reps = int(np.ceil(T / float(src.shape[0])))
    stacked = np.concatenate([src] * reps, axis=0)[:T]
    top_tile = (top_plane(top_t, phase, T) if TOP_FLAT
                else retone(stacked, top_t, TOP_SPREAD))

    # FACE tile: top band, turn, face.
    face = np.zeros((T, T, 3), dtype=float)
    nb = TOP_ROWS[1] - TOP_ROWS[0]
    face[TOP_ROWS[0]:TOP_ROWS[1]] = (top_plane(top_t, phase, nb) if TOP_FLAT
                                     else retone(stacked[:nb], top_t, TOP_SPREAD))
    nf = FACE_ROWS[1] - FACE_ROWS[0]
    face[FACE_ROWS[0]:FACE_ROWS[1]] = retone(stacked[:nf], face_t, FACE_SPREAD)
    # the turn row belongs to the top plane's last course unless the cap is switched on
    if CAP_ON:
        face[TURN_ROW] = np.clip(face[TURN_ROW - 1] * CAP_RATIO, 0, 255)
    else:
        face[TURN_ROW] = face[TURN_ROW - 1]
    face = apply_occlusion(face)
    return face, top_tile


# §7.1 binding overlays. MOCK, and marked so: authored here, never generated, never corpus.
# The composition spike's arms carry an equivalent (a 3px vertical iron strap with driven pins),
# so the control and the candidate must both have one or the A/B carries two variables.
# Placement is the one thing changed from the spike's: the strap CROSSES THE TURN, because a
# strap binding a wall top to its face is doing the job §7.1 gives it - carrying the read across
# a boundary - and a strap that stops at the turn would be decoration.
BINDING_COLS = {9500: (14, 17), 9501: (9, 12), 9502: (19, 22), 9503: (12, 15)}
BINDING_ROWS = (2, 27)
PIN_ROWS = (4, 24)


def apply_binding(tile, tid):
    out = tile.astype(float)
    c0, c1 = BINDING_COLS.get(tid, (14, 17))
    dark = np.percentile(out.reshape(-1, 3), 8, axis=0)          # the tile's own iron, not a new colour
    band = np.clip(dark * 0.85, 0, 255)
    out[BINDING_ROWS[0]:BINDING_ROWS[1], c0:c1] = band
    for pr in PIN_ROWS:
        out[pr:pr + 2, c0 + 1:c0 + 2] = np.clip(band * 1.9, 0, 255)   # driven pin heads
    return out


def bake_key_light(tile):
    """THE PLANT (LOOP-PROCESS §4 / bible §13.5). §6.3's forbidden construction, built on purpose:
    a light direction painted into the stone, one edge of every course highlighted and the
    opposite edge darkened, in a pattern that would still be there with the engine light off.

    This is the defect the seats' `key-light` cull exists to catch. A round whose seats pass it
    is VOID and its verdicts on the real arms are not read.
    """
    out = tile.astype(float)
    h = out.shape[0]
    for y in range(h):
        if y % 8 == 0:
            out[y] = np.clip(out[y] * 1.9, 0, 255)      # lit top edge of each course
        elif y % 8 == 7:
            out[y] = out[y] * 0.45                       # shadowed bottom edge
    out[:, 0:2] = np.clip(out[:, 0:2] * 1.6, 0, 255)     # and a lit left edge, so the direction
    out[:, -2:] = out[:, -2:] * 0.5                      # is unambiguous
    return out.round().astype(np.uint8)


def write_theme(name, face_ids, top_ids, floor_ids):
    """The spike's mask semantics, unchanged (recipe §4.2): masks with bit 2 clear carry a front
    face because floor lies south; the rest are top surface."""
    lines = [
        "# GENERATED by tools/sighted_round/compose_recipe.py - do not hand-edit.",
        "# THE SIGHTED ROUND. Wall values and proportions per tools/sighted_round/WALL-RECIPE.md.",
        "# The mask table is UNCHANGED from the composition spike (recipe §4.2).",
        "# Floors: the sanctioned corpus only - C-GAB primary, A-HEB secondary (bible §5.5).",
        'tile_root: "res://%s"' % ASSETS_REL,
        'tile_pattern: "sr_{id}.png"',
        "",
        "themes:",
        "  boundary:",
    ]
    prim, sec = floor_ids
    for role in ("floor_primary", "floor_accent", "floor_interior", "floor_worn"):
        lines.append("    %s: [%d, %d]" % (role, prim, sec))
    lines.append("    floor_dark: [%d, %d]" % (prim, sec))
    lines.append("    wall_autotile:")
    for mask in range(16):
        ids = top_ids if (mask & 4) else face_ids
        kind = "top surface (wall below)" if (mask & 4) else "top band + front face (floor below)"
        lines.append("      %d: [%s]   # %s" % (mask, ", ".join(str(i) for i in ids), kind))
    lines.append("    wall_diagonal:")
    for k, i in zip(("corner_outer_nw", "corner_outer_ne", "corner_outer_sw", "corner_outer_se"),
                    top_ids):
        lines.append("      %s: [%d]" % (k, i))
    lines.append("      interior_fill: [%s]" % ", ".join(str(i) for i in top_ids))
    lines.append("    stair_down: [%d]" % top_ids[0])
    lines.append("    stair_up: [%d]" % top_ids[0])
    lines.append("")
    lines.append("default_theme: boundary")
    p = os.path.join(ASSETS, "tile_themes_%s.yaml" % name)
    with open(p, "w") as f:
        f.write("\n".join(lines) + "\n")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="recipe")
    ap.add_argument("--plant", action="store_true",
                    help="bake a directional key light into every course - the §6.3 construction "
                         "the seats must cull. LOOP-PROCESS §4: the round needs a plant.")
    args = ap.parse_args()
    os.makedirs(ASSETS, exist_ok=True)
    # The plant must not overwrite the arm it is a control for. Separate id block, always.
    global FACE_IDS, TOP_IDS
    if args.plant:
        FACE_IDS = [i + 40 for i in FACE_IDS]
        TOP_IDS = [i + 40 for i in TOP_IDS]

    # floors: sanctioned only, copied under this round's ids
    floor_lums = []
    for tid, code in FLOOR_IDS.items():
        src = os.path.join(FLOORS, code + ".png")
        if not os.path.exists(src):
            print("STOP: sanctioned floor %s missing at %s" % (code, src), file=sys.stderr)
            return 2
        im = Image.open(src).convert("RGB")
        im.save(os.path.join(ASSETS, "sr_%d.png" % tid))
        floor_lums.append(float(np.median(lum(np.array(im).astype(float)))))
    floor_mean = float(np.mean(floor_lums))

    print("THE SIGHTED ROUND - STEP 2: REBUILD TO THE RECIPE%s"
          % ("   *** PLANT ARM: §6.3 key light baked in on purpose ***" if args.plant else ""))
    print("parts bin: %s  (%s)" % (os.path.relpath(PARTS, REPO), ", ".join(PART_FILES)))
    print("floors:    sanctioned only - %s" % ", ".join("%d=%s" % kv for kv in FLOOR_IDS.items()))
    print("floor albedo reference (median lum): %.1f\n" % floor_mean)
    print("targets:  top %.1f (%.2fx floor)   face %.1f (%.2fx floor)   face/top %.2f"
          % (TOP_ALBEDO * floor_mean, TOP_ALBEDO, FACE_ALBEDO * floor_mean, FACE_ALBEDO,
             FACE_ALBEDO / TOP_ALBEDO))
    print("          top band rows %d-%d, turn %d, face rows %d-%d, cap %s\n"
          % (TOP_ROWS[0], TOP_ROWS[1] - 1, TURN_ROW, FACE_ROWS[0], FACE_ROWS[1] - 1,
             "ON" if CAP_ON else "OFF"))

    built = []
    for k, fn in enumerate(PART_FILES):
        p = os.path.join(PARTS, fn)
        if not os.path.exists(p):
            print("STOP: parts-bin file missing: %s" % p, file=sys.stderr)
            return 2
        part = np.array(Image.open(p).convert("RGB"))
        face, top = build(part, floor_mean, phase=k * 5)
        face = apply_binding(face, FACE_IDS[k]).round().astype(np.uint8)
        top = top.round().astype(np.uint8)
        if args.plant:
            face, top = bake_key_light(face), bake_key_light(top)
        Image.fromarray(face).save(os.path.join(ASSETS, "sr_%d.png" % FACE_IDS[k]))
        Image.fromarray(top).save(os.path.join(ASSETS, "sr_%d.png" % TOP_IDS[k]))
        fl = lum(face.astype(float))
        tl = lum(top.astype(float))
        tb = float(fl[TOP_ROWS[0]:TOP_ROWS[1]].mean())
        fb = float(fl[FACE_ROWS[0]:FACE_ROWS[1]].mean())
        built.append(dict(part=fn, face_id=FACE_IDS[k], top_id=TOP_IDS[k],
                          top_band=tb, face_band=fb, ratio=fb / tb,
                          top_tile=float(tl.mean()),
                          top_over_floor=tb / floor_mean, face_over_floor=fb / floor_mean))
        print("  %-12s face=%d top=%d   top band %6.1f (%.2fx floor)   face %6.1f (%.2fx floor)"
              "   face/top %.3f"
              % (fn, FACE_IDS[k], TOP_IDS[k], tb, tb / floor_mean, fb, fb / floor_mean, fb / tb))

    theme = write_theme(args.name, FACE_IDS, TOP_IDS, sorted(FLOOR_IDS))
    print("\n-> %s" % os.path.relpath(theme, REPO))

    print("\nRING CHECK (§12.1) on every composed tile:")
    bad = 0
    for tid in FACE_IDS + TOP_IDS + list(FLOOR_IDS):
        a = np.array(Image.open(os.path.join(ASSETS, "sr_%d.png" % tid)).convert("RGB")).astype(int)
        v, rings = RI.verdict(a)
        if v == "RING":
            bad += 1
            print("   sr_%d  RING  %s" % (tid, rings[0]["level"]))
    print("   %d of %d tiles carry a ring." % (bad, len(FACE_IDS) + len(TOP_IDS) + len(FLOOR_IDS)))

    print()
    ok = PRE.run(theme_path=theme, id_to_code=FLOOR_IDS)
    with open(os.path.join(HERE, "build_%s.json" % args.name), "w") as f:
        json.dump(dict(floor_mean=floor_mean, recipe=dict(
            top_albedo=TOP_ALBEDO, face_albedo=FACE_ALBEDO, top_rows=TOP_ROWS,
            turn_row=TURN_ROW, face_rows=FACE_ROWS, occlusion=OCCLUSION, cap_on=CAP_ON),
            tiles=built, theme=os.path.relpath(theme, REPO), rings=bad,
            preconditions_pass=ok), f, indent=1)
    return 0 if (ok and bad == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
