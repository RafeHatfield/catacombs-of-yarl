#!/usr/bin/env python3
"""F4 edge_density recalibration against Rafe's labeled Round-A verdicts (2026-08).

Ground truth: 9 in-scene REJECTS (should flag) vs 2 KEEPS (must not flag) + 2488 canon negatives
(must not flag). The p90-of-all-canon edge_density threshold failed (both keeps and rejects exceed
it). Test interpretable edge-density variants for a threshold that flags all 9 rejects, neither keep,
and ~zero canon (zero false positives). Candidates:

  F4  edge_density              — current: opaque-opaque different-colour boundary / opaque
  F4i edge_density_interior     — same, but only pixels whose 4-neighbours are all opaque (drop the
                                  silhouette rim, which inflates compact objects)
  F4n edge_density_nonoutline   — colour complexity WITHIN the fill: among non-dark (max ch >= 70)
                                  opaque pixels, fraction with a different-coloured non-dark opaque
                                  neighbour. Isolates internal refinement from the (expected) outline.
  F4p edge_perimeter_norm       — opaque-opaque colour-boundary pixels / silhouette-perimeter pixels

Interpretable metrics only; no classifiers. Validated on ALL labels.
"""
import csv
import glob
import os
import re
import sys

from PIL import Image

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, "tools/art_lint")
from extract_master_palette import WORLD_EXTRA_EXCLUDED_IDS, iter_id_filtered_pngs, iter_all_pngs

W = "src/Presentation/assets/sprites_16bf/world_24x24"
REJECTS = [5062, 5063, 5064, 5106, 5107, 5082, 5097, 5098, 5084]
KEEPS = [5094, 5054]


def metrics(im):
    px = im.load()
    w, h = im.size
    def op(x, y):
        return 0 <= x < w and 0 <= y < h and px[x, y][3] == 255
    opaque = interior = nonoutline = perim = 0
    edge = edge_int = edge_non = 0
    for y in range(h):
        for x in range(w):
            if px[x, y][3] != 255:
                continue
            opaque += 1
            col = px[x, y][:3]
            dark = max(col) < 70
            n4 = [(x+dx, y+dy) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))]
            all_op = all(op(nx, ny) for nx, ny in n4)
            if not all_op:
                perim += 1
            diff = any(op(nx, ny) and px[nx, ny][:3] != col for nx, ny in n4)
            if diff:
                edge += 1
            if all_op:
                interior += 1
                if diff:
                    edge_int += 1
            if not dark:
                nonoutline += 1
                if any(op(nx, ny) and px[nx, ny][3] == 255 and max(px[nx, ny][:3]) >= 70
                       and px[nx, ny][:3] != col for nx, ny in n4):
                    edge_non += 1
    return {
        "F4": round(edge / opaque, 4) if opaque else 0,
        "F4i": round(edge_int / interior, 4) if interior else 0,
        "F4n": round(edge_non / nonoutline, 4) if nonoutline else 0,
        "F4p": round(edge / perim, 4) if perim else 0,
    }


def canon_paths():
    world, _ = iter_id_filtered_pngs(f"{W}", 5000, WORLD_EXTRA_EXCLUDED_IDS)
    creatures = iter_all_pngs("src/Presentation/assets/sprites_16bf/creatures_24x24")
    items, _ = iter_id_filtered_pngs("src/Presentation/assets/sprites_16bf/items_16x16", 4001)
    return world + creatures + items


def main():
    rej = {fid: metrics(Image.open(f"{W}/oryx_16bit_fantasy_world_{fid}.png").convert("RGBA")) for fid in REJECTS}
    kep = {fid: metrics(Image.open(f"{W}/oryx_16bit_fantasy_world_{fid}.png").convert("RGBA")) for fid in KEEPS}
    canon = [metrics(Image.open(p).convert("RGBA")) for p in canon_paths()]
    print(f"canon negatives: {len(canon)}")

    for key in ("F4", "F4i", "F4n", "F4p"):
        rvals = sorted(rej[f][key] for f in REJECTS)
        kvals = sorted(kep[f][key] for f in KEEPS)
        cvals = sorted(c[key] for c in canon)
        min_rej = min(rvals); max_keep = max(kvals)
        # a clean separator must sit below every reject and above both keeps and all canon
        canon_max = cvals[-1]
        # candidate threshold: just under the smallest reject
        thr = min_rej
        canon_fp = sum(1 for v in cvals if v >= thr)
        keep_fp = sum(1 for v in kvals if v >= thr)
        # is there ANY threshold t with all rejects>=t, all keeps<t, all canon<t?
        upper = min_rej  # rejects floor
        lower = max(max_keep, canon_max)  # negatives ceiling
        clean = lower < upper
        print(f"\n{key}:")
        print(f"  rejects  min={rvals[0]:.3f} max={rvals[-1]:.3f}  {[f'{v:.3f}' for v in rvals]}")
        print(f"  keeps    {[f'{v:.3f}' for v in kvals]}")
        print(f"  canon    p90={cvals[int(0.9*len(cvals))]:.3f} p99={cvals[int(0.99*len(cvals))]:.3f} max={canon_max:.3f}")
        print(f"  separation: rejects-floor={min_rej:.3f}  negatives-ceiling(max keep,canon)={lower:.3f}  "
              f"CLEAN={clean}")
        if clean:
            t = (upper + lower) / 2
            print(f"  >>> CLEAN SEPARATOR at threshold {t:.4f}: flags all 9 rejects, 0 keeps, 0 canon FP")


if __name__ == "__main__":
    main()
