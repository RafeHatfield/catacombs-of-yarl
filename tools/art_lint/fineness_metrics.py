#!/usr/bin/env python3
"""Structural-fineness metrics + canon baseline (play-review register ruling, 2026-08).

The register is Shattered-Pixel / Oryx school: chunky, low-detail, bold-read. The generated-art
failure mode is REFINEMENT — too fine, too many small structures — which passes A1-A6 (palette and
color budget) while still reading wrong. This module measures fineness directly, four ways, and
baselines each on the canonical Oryx population per sheet-class. Thresholds: WARN at canon p90,
FAIL at canon max — the same upper-bound philosophy as A4's color budget.

Metrics (all: higher = finer = worse):
  F1 speckle          — opaque pixels with no 4-neighbour of the same colour (isolated singles).
                        Same as art_lint.count_speckle (A7), now thresholded.
  F2 small_clusters   — count of same-colour 4-connected components with area <= SMALL_CLUSTER_MAX.
                        "minimum meaningful cluster size": in the chunky register a real structure is
                        bigger than a few pixels; this counts the sub-meaningful specks/slivers.
  F3 color_regions    — total count of same-colour 4-connected components (region fragmentation).
  F4 edge_density     — interior colour-boundary pixels / opaque pixels. A boundary pixel is an
                        opaque pixel with a 4-neighbour that is opaque and a DIFFERENT colour
                        (silhouette edges to transparency are excluded — this is interior detail).

Run as a script to (re)derive tools/art_lint/fineness_canon_baseline.csv (raw per-file) and
tools/art_lint/fineness_thresholds.json (per-class p90/max).
"""
import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image

SMALL_CLUSTER_MAX = 4  # area <= this is "below meaningful structure size" in the chunky register

METRICS = ["speckle", "small_clusters", "color_regions", "edge_density"]


def _opaque_color_grid(im):
    w, h = im.width, im.height
    px = im.load()
    grid = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 255:
                grid[y][x] = (r, g, b)
    return grid, w, h


def _components(grid, w, h):
    """Same-colour 4-connected components over opaque pixels. Returns list of areas."""
    seen = [[False] * w for _ in range(h)]
    areas = []
    for y0 in range(h):
        for x0 in range(w):
            if grid[y0][x0] is None or seen[y0][x0]:
                continue
            col = grid[y0][x0]
            stack = [(x0, y0)]
            seen[y0][x0] = True
            area = 0
            while stack:
                x, y = stack.pop()
                area += 1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and grid[ny][nx] == col:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            areas.append(area)
    return areas


def compute(im):
    grid, w, h = _opaque_color_grid(im)
    opaque = sum(1 for y in range(h) for x in range(w) if grid[y][x] is not None)
    if opaque == 0:
        return dict(speckle=0, small_clusters=0, color_regions=0, edge_density=0.0)

    # F1 speckle + F4 edge boundary, single pass
    speckle = 0
    boundary = 0
    for y in range(h):
        for x in range(w):
            col = grid[y][x]
            if col is None:
                continue
            same_neighbor = False
            diff_neighbor = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] is not None:
                    if grid[ny][nx] == col:
                        same_neighbor = True
                    else:
                        diff_neighbor = True
            if not same_neighbor:
                speckle += 1
            if diff_neighbor:
                boundary += 1

    areas = _components(grid, w, h)
    small = sum(1 for a in areas if a <= SMALL_CLUSTER_MAX)
    return dict(
        speckle=speckle,
        small_clusters=small,
        color_regions=len(areas),
        edge_density=round(boundary / opaque, 4),
    )


def _pctl(sorted_vals, q):
    if not sorted_vals:
        return 0
    idx = min(len(sorted_vals) - 1, int(math.ceil(q * len(sorted_vals)) - 1))
    return sorted_vals[max(0, idx)]


def derive_baseline():
    from extract_master_palette import (
        WORLD_EXTRA_EXCLUDED_IDS, iter_id_filtered_pngs, iter_all_pngs)
    world, _ = iter_id_filtered_pngs(
        "src/Presentation/assets/sprites_16bf/world_24x24", 5000, WORLD_EXTRA_EXCLUDED_IDS)
    creatures = iter_all_pngs("src/Presentation/assets/sprites_16bf/creatures_24x24")
    items, _ = iter_id_filtered_pngs("src/Presentation/assets/sprites_16bf/items_16x16", 4001)

    rows = []
    for label, paths in [("world_24x24", world), ("creatures_24x24", creatures),
                         ("items_16x16", items)]:
        for p in paths:
            m = compute(Image.open(p).convert("RGBA"))
            rows.append(dict(file=p, **{"class": label}, **m))

    with open("tools/art_lint/fineness_canon_baseline.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file", "class"] + METRICS)
        w.writeheader()
        w.writerows(rows)

    thresholds = {}
    for label in ("world_24x24", "creatures_24x24", "items_16x16"):
        vals = {m: sorted(r[m] for r in rows if r["class"] == label) for m in METRICS}
        thresholds[label] = {m: {"warn_p90": _pctl(vals[m], 0.90), "fail_max": (vals[m][-1] if vals[m] else 0)}
                             for m in METRICS}
        thresholds[label]["_n"] = len(vals[METRICS[0]])
    thresholds["_meta"] = {"small_cluster_max_area": SMALL_CLUSTER_MAX,
                           "warn": "canon p90", "fail": "canon max",
                           "ruling": "play review 2026-08"}
    with open("tools/art_lint/fineness_thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=2)

    print(f"canon files scored: {len(rows)}")
    for label in ("world_24x24", "creatures_24x24", "items_16x16"):
        t = thresholds[label]
        print(f"  {label} (n={t['_n']}): " +
              ", ".join(f"{m} p90={t[m]['warn_p90']} max={t[m]['fail_max']}" for m in METRICS))


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    derive_baseline()
