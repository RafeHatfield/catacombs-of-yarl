#!/usr/bin/env python3
"""CAN THE CORNER CLASS LIVE AT RUNTIME? Three measurements, before K is sized.

The proposal: keep the authored tile set at 81 (edge families only), carry a per-pixel STONE
INDEX alongside the material, and have the renderer remap each stone's value from the coordinates
of the grid corner it surrounds — coordinates all four adjoining tiles already share. K then
becomes a runtime parameter instead of a K^4 multiplier on the asset count.

It rests on three claims, and none of them is safe to assume:

  A. THE KEYING IS WELL-DEFINED. Every enclosed stone in an assembled field must contain exactly
     ONE grid corner. Zero corners and the stone has no key; two and the key is ambiguous and the
     four adjoining tiles cannot agree. This is a property of the joint topology, not of the idea.

  B. THE REMAP SURVIVES §6.3. Authored occlusion is LAW — "a wall-top meeting floor without its
     occluded edge is not purity, it is a missing plane", and the joints are dark BECAUSE
     ENCLOSED (§6.5's derivation). A remap that REPLACES a stone's pixels with a flat value
     destroys that. An ADDITIVE offset preserves every internal difference exactly. The question
     is which one the proposal actually needs, and what an additive one costs.

  C. IT STAYS ON THE PALETTE. §5.1 is a zero-mercy gate and §4.3 forbids anti-aliasing, so the
     tiles are quantised to a 7-level ladder. An arbitrary offset pushes values off it. An offset
     of a whole number of ladder steps does not — except where it CLIPS at the ends, and the
     joints already sit near the bottom.

Measurements only. The ruling on K follows the numbers.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_wang as CW      # noqa: E402
import field_wang as FW        # noqa: E402
import field_laws as FL        # noqa: E402

T = CW.T


def stones_and_corners(joints, w, h):
    """Flood the non-joint pixels across the WHOLE field, then count grid corners per stone."""
    H, W = joints.shape
    lab = np.full((H, W), -1, dtype=int)
    nxt = 0
    sizes = []
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

    # Interior grid corners. A corner (cx,cy) sits at pixel (cy*T, cx*T); the stone that "owns" it
    # is whichever stone covers the four pixels around it that are not joint.
    owners = {}
    for cy in range(1, h):
        for cx in range(1, w):
            py, px = cy * T, cx * T
            near = []
            for dy in (-1, 0):
                for dx in (-1, 0):
                    yy, xx = py + dy, px + dx
                    if 0 <= yy < H and 0 <= xx < W and lab[yy, xx] >= 0:
                        near.append(int(lab[yy, xx]))
            owners[(cx, cy)] = set(near)

    per_stone = {}
    for corner, labs in owners.items():
        for l in labs:
            per_stone.setdefault(l, set()).add(corner)

    big = [i for i, s in enumerate(sizes) if s >= 64]
    counts = [len(per_stone.get(i, ())) for i in big]
    return dict(stones=nxt, stones_over_64px=len(big),
                corners_checked=len(owners),
                stones_with_exactly_one_corner=sum(1 for c in counts if c == 1),
                stones_with_no_corner=sum(1 for c in counts if c == 0),
                stones_with_multiple_corners=sum(1 for c in counts if c > 1),
                max_corners_in_a_stone=max(counts) if counts else 0,
                corners_claimed_by_multiple_stones=sum(1 for s in owners.values() if len(s) > 1))


def ladder_cost(mat):
    """What an additive offset in LADDER STEPS costs: how much clips, and what happens to form."""
    A = CW.ASSETS
    man = json.load(open(os.path.join(A, "MANIFEST.json")))
    lo, hi = mat["lum_lo"], mat["lum_hi"]
    step = (hi - lo) / (CW.CF.PALETTE_LEVELS - 1)

    rows = []
    for k in (1, 2, 3):
        off = k * step
        clipped_lo = clipped_hi = total = 0
        for e in man["base"][:24]:                 # a sample; every tile shares the ladder
            a = np.asarray(Image.open(os.path.join(A, e["file"])).convert("RGB")).astype(float)
            L = FL.RI.lum(a)
            total += L.size
            clipped_lo += int((L - off < lo - 1e-6).sum())
            clipped_hi += int((L + off > hi + 1e-6).sum())
        rows.append(dict(steps=k, offset=round(off, 2),
                         clip_low_pct=round(100.0 * clipped_lo / total, 2),
                         clip_high_pct=round(100.0 * clipped_hi / total, 2)))
    return dict(ladder_step=round(step, 2), lo=round(lo, 1), hi=round(hi, 1), rows=rows)


def occlusion_preserved(mat):
    """Does an ADDITIVE offset preserve the authored joint-to-stone contrast, and does a
    REPLACEMENT destroy it? The contrast IS the occlusion (§6.5: joints are dark because
    enclosed), so this is the §6.3 question stated as a number."""
    A = CW.ASSETS
    man = json.load(open(os.path.join(A, "MANIFEST.json")))
    step = (mat["lum_hi"] - mat["lum_lo"]) / (CW.CF.PALETTE_LEVELS - 1)
    keep_add, keep_replace = [], []
    for e in man["base"][:24]:
        a = np.asarray(Image.open(os.path.join(A, e["file"])).convert("RGB")).astype(float)
        L = FL.RI.lum(a)
        dark = L < np.percentile(L, 20)            # the joints
        light = L > np.percentile(L, 60)           # the stone faces
        if not dark.any() or not light.any():
            continue
        base_contrast = float(L[light].mean() - L[dark].mean())
        add = float((L[light] + step).mean() - (L[dark] + step).mean())
        flat = float(L.mean() + step) - float(L.mean() + step)     # replacement: one value
        keep_add.append(add / base_contrast if base_contrast else 0)
        keep_replace.append(flat / base_contrast if base_contrast else 0)
    return dict(n=len(keep_add),
                additive_contrast_retained=round(float(np.mean(keep_add)), 4),
                replacement_contrast_retained=round(float(np.mean(keep_replace)), 4))


def main():
    man = json.load(open(os.path.join(CW.ASSETS, "MANIFEST.json")))
    mat = man["material"]
    print("CAN THE CORNER CLASS LIVE AT RUNTIME? — three measurements\n")

    print("A. IS THE KEYING WELL-DEFINED? (every stone must contain exactly one grid corner)")
    _img, joints, _f = FW.assemble(8, 8, 1337, mat, None)
    k = stones_and_corners(joints, 8, 8)
    print("   stones: %d total, %d over 64px    interior corners checked: %d"
          % (k["stones"], k["stones_over_64px"], k["corners_checked"]))
    print("   stones (>=64px) with exactly ONE corner : %d" % k["stones_with_exactly_one_corner"])
    print("   stones with NO corner                   : %d" % k["stones_with_no_corner"])
    print("   stones with MULTIPLE corners            : %d  (max %d)"
          % (k["stones_with_multiple_corners"], k["max_corners_in_a_stone"]))
    print("   corners claimed by more than one stone  : %d" % k["corners_claimed_by_multiple_stones"])

    print("\nB. DOES THE REMAP SURVIVE §6.3? (authored occlusion = joint-to-stone contrast)")
    o = occlusion_preserved(mat)
    print("   additive offset    retains %.1f%% of the authored contrast (n=%d tiles)"
          % (100 * o["additive_contrast_retained"], o["n"]))
    print("   flat replacement   retains %.1f%%" % (100 * o["replacement_contrast_retained"]))

    print("\nC. DOES IT STAY ON THE PALETTE? (offsets in whole ladder steps; clipping at the ends)")
    lc = ladder_cost(mat)
    print("   ladder: %d levels from %.1f to %.1f, step %.2f"
          % (CW.CF.PALETTE_LEVELS, lc["lo"], lc["hi"], lc["ladder_step"]))
    for r in lc["rows"]:
        print("     +/-%d step (%.1f): clips %.2f%% low, %.2f%% high"
              % (r["steps"], r["offset"], r["clip_low_pct"], r["clip_high_pct"]))

    out = dict(commit=FL.git_commit(), keying=k, occlusion=o, ladder=lc)
    p = os.path.join(HERE, "evidence", "CORNER-KEYING-PROBE.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
