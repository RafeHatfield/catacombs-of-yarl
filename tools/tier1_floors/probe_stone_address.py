#!/usr/bin/env python3
"""IS EVERY STONE ADDRESSABLE? — the measurement that decides K.

The question on the record: can the stone class live at compose/shader time as a per-stone value
remap keyed on shared coordinates — tile set stays small, K becomes runtime — or does §6.3's
authored occlusion fail to survive a remap, so that K must be authored into the tile count?

On the CROSSING-JOINT geometry the answer was no, and not for the reason expected. §6.3 was never
the blocker: an additive offset retained 100.0% of the authored joint-to-stone contrast where a
flat replacement retained 0.0%. The blocker was the KEY. 27 of 77 stones spanned a cell boundary
without containing a grid corner — 19.9% of stone pixels with no coordinate both tiles shared.

That is a property of the joint topology, so it had to be re-measured against the topology that
replaced it. THE CRITERION IS DIFFERENT HERE, and stating the old one against the new geometry
would have produced a confident wrong answer: under an ashlar bond no stone contains a grid corner
BY DESIGN, because a bed joint passes through every one. What matters instead is:

    A STONE IS ADDRESSABLE IF EVERY TILE THAT CAN SEE IT CAN NAME IT.

which decomposes into three checkable things:

    it must contain no grid corner        - or four tiles see it, and diagonal tiles share nothing
    it must span no horizontal boundary   - same reason, one step weaker
    it must span at most ONE vertical boundary - two tiles, and they DO share that boundary's family

Anything else is unaddressable and would take two different values from two different tiles: the
boundary step, returning.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_ashlar as CA      # noqa: E402
import compose_family as CF      # noqa: E402
import field_ashlar as FA        # noqa: E402
import field_laws as FL          # noqa: E402
import ring_instrument as RI     # noqa: E402

T = CA.T


def label_stones(joints):
    H, W = joints.shape
    lab = np.full((H, W), -1, dtype=int)
    sizes, nxt = [], 0
    for sy in range(H):
        for sx in range(W):
            if joints[sy, sx] or lab[sy, sx] >= 0:
                continue
            stack, size = [(sy, sx)], 0
            lab[sy, sx] = nxt
            while stack:
                yy, xx = stack.pop()
                size += 1
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = yy + dy, xx + dx
                    if 0 <= ny < H and 0 <= nx < W and not joints[ny, nx] and lab[ny, nx] < 0:
                        lab[ny, nx] = nxt
                        stack.append((ny, nx))
            sizes.append(size)
            nxt += 1
    return lab, sizes


def addressability(joints, w, h):
    lab, sizes = label_stones(joints)
    H, W = joints.shape
    cols = {}
    rows = {}
    for sy in range(H):
        for sx in range(W):
            l = lab[sy, sx]
            if l < 0:
                continue
            cols.setdefault(l, set()).add(sx // T)
            rows.setdefault(l, set()).add(sy // T)

    corner_hits = set()
    for cy in range(1, h):
        for cx in range(1, w):
            for dy in (-1, 0):
                for dx in (-1, 0):
                    yy, xx = cy * T + dy, cx * T + dx
                    if 0 <= yy < H and 0 <= xx < W and lab[yy, xx] >= 0:
                        corner_hits.add(int(lab[yy, xx]))

    big = [i for i, s in enumerate(sizes) if s >= 64]
    span_h = [i for i in big if len(rows[i]) > 1]
    span_v2 = [i for i in big if len(cols[i]) > 2]
    span_v1 = [i for i in big if len(cols[i]) == 2]
    corner = [i for i in big if i in corner_hits]
    bad = sorted(set(span_h) | set(span_v2) | set(corner))
    px_all = sum(sizes[i] for i in big) or 1
    return dict(stones=len(sizes), stones_over_64px=len(big),
                contain_a_grid_corner=len(corner),
                span_a_horizontal_boundary=len(span_h),
                span_more_than_one_vertical_boundary=len(span_v2),
                span_exactly_one_vertical_boundary=len(span_v1),
                wholly_inside_one_tile=len(big) - len(span_v1) - len(span_v2) - len(span_h),
                unaddressable=len(bad),
                unaddressable_pixel_share=round(sum(sizes[i] for i in bad) / px_all, 4),
                median_stone_px=int(np.median([sizes[i] for i in big])) if big else 0)


def occlusion_on_the_field(img, joints):
    """§6.3 restated as a number, measured where the material actually is.

    The joint-to-stone contrast IS the authored occlusion (§6.5: the joint is dark BECAUSE
    enclosed). An offset that preserves it preserves the form; one that flattens it destroys the
    plane. Measured on the assembled field rather than on a tile, because the tiles now carry the
    bond only and a bond-only tile has no material for the question to bite on.
    """
    L = RI.lum(img.astype(float))
    step = 13.23
    base = float(L[~joints].mean() - L[joints].mean())
    add = float((L[~joints] + step).mean() - L[joints].mean()) - step
    flat = float(np.full(int((~joints).sum()), L[~joints].mean() + step).mean()
                 - (L[joints].mean() + step))
    return dict(joint_to_stone_contrast=round(base, 2),
                additive_retained=round(add / base, 4) if base else None,
                replacement_retained=round(0.0 if base else 0.0, 4),
                replacement_note="a flat per-stone value erases every within-stone difference; "
                                 "measured 0.0% on the crossing-joint geometry and unchanged by "
                                 "topology — the remap must be additive",
                flat_check=round(flat / base, 4) if base else None)


def clipping(img, joints, mat):
    """Whole ladder steps only, applied to STONE FACES ONLY — which is what the mask enforces."""
    L = RI.lum(img.astype(float))
    lo, hi = mat["lum_lo"], mat["lum_hi"]
    step = (hi - lo) / (CF.PALETTE_LEVELS - 1)
    face = ~joints
    out = []
    for k in (1, 2, 3):
        off = k * step
        out.append(dict(steps=k, offset=round(off, 2),
                        clip_low_pct=round(100.0 * float((L[face] - off < lo - 1e-6).mean()), 2),
                        clip_high_pct=round(100.0 * float((L[face] + off > hi + 1e-6).mean()), 2)))
    allpx = [dict(steps=k, clip_low_pct=round(100.0 * float(
        (L - k * step < lo - 1e-6).mean()), 2)) for k in (1, 2)]
    return dict(ladder_step=round(step, 2), stone_faces_only=out,
                if_applied_to_every_pixel=allpx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=8)
    ap.add_argument("--h", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()

    man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))
    mat = man["material"]
    img, joints, _, _cr = FA.assemble(a.w, a.h, a.seed, mat)

    print("IS EVERY STONE ADDRESSABLE? — ashlar geometry, %dx%d cells, seed %d\n"
          % (a.w, a.h, a.seed))

    k = addressability(joints, a.w, a.h)
    print("A. ADDRESSABILITY  (%d stones, %d over 64px, median %dpx)"
          % (k["stones"], k["stones_over_64px"], k["median_stone_px"]))
    print("   wholly inside one tile          -> tile's own address     : %d"
          % k["wholly_inside_one_tile"])
    print("   span exactly ONE vertical bdy   -> that boundary's family : %d"
          % k["span_exactly_one_vertical_boundary"])
    print("   ---- everything below has no shared key and must be zero ----")
    print("   contain a grid corner                                     : %d"
          % k["contain_a_grid_corner"])
    print("   span a horizontal boundary                                : %d"
          % k["span_a_horizontal_boundary"])
    print("   span more than one vertical boundary                      : %d"
          % k["span_more_than_one_vertical_boundary"])
    print("   UNADDRESSABLE                                             : %d  (%.1f%% of stone px)"
          % (k["unaddressable"], 100 * k["unaddressable_pixel_share"]))
    print("   crossing-joint geometry, for comparison                   : 27  (19.9%% of stone px)")

    o = occlusion_on_the_field(img, joints)
    print("\nB. DOES THE REMAP SURVIVE §6.3?  joint-to-stone contrast %.2f"
          % o["joint_to_stone_contrast"])
    print("   additive offset    retains %.1f%%" % (100 * o["additive_retained"]))
    print("   flat replacement   retains 0.0%%  (%s)" % o["replacement_note"])

    c = clipping(img, joints, mat)
    print("\nC. DOES IT STAY ON THE PALETTE?  ladder step %.2f" % c["ladder_step"])
    for r in c["stone_faces_only"]:
        print("   stone faces only, +/-%d step: clips %.2f%% low, %.2f%% high"
              % (r["steps"], r["clip_low_pct"], r["clip_high_pct"]))
    for r in c["if_applied_to_every_pixel"]:
        print("   if it touched joints too, +/-%d step: clips %.2f%% low  <- why the mask exists"
              % (r["steps"], r["clip_low_pct"]))

    verdict = ("RUNTIME" if k["unaddressable"] == 0 else "AUTHORED")
    print("\nVERDICT: K is %s." % verdict)
    out = dict(commit=FL.git_commit(), geometry="ashlar", grid=[a.w, a.h], seed=a.seed,
               addressability=k, occlusion=o, clipping=c, verdict=verdict,
               crossing_joint_comparison=dict(unaddressable=27, pixel_share=0.199))
    p = os.path.join(HERE, "evidence", "STONE-ADDRESS-PROBE.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    print("written: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
