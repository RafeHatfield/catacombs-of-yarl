#!/usr/bin/env python3
"""Snap sprite RGB colors to the nearest exact color in the Oryx master palette.

Never modifies sprites in place — reads from --source-dir, writes to --output-dir.
"""
import argparse
import json
import math
import os
import sys

from PIL import Image


def load_palette(path):
    with open(path) as f:
        data = json.load(f)
    return [tuple(c) for c in data["colors"]]


def nearest_palette_color(color, palette):
    """Euclidean RGB distance; ties broken by lowest palette index (first found)."""
    best_index, best_dist_sq = 0, None
    cr, cg, cb = color
    for i, (pr, pg, pb) in enumerate(palette):
        dist_sq = (cr - pr) ** 2 + (cg - pg) ** 2 + (cb - pb) ** 2
        if best_dist_sq is None or dist_sq < best_dist_sq:
            best_dist_sq, best_index = dist_sq, i
    return palette[best_index], math.sqrt(best_dist_sq)


def snap_file(src_path, palette, dst_path):
    im = Image.open(src_path).convert("RGBA")
    pixels = list(im.getdata())

    partial_alpha_pixels = sum(1 for (_, _, _, a) in pixels if 0 < a < 255)
    if partial_alpha_pixels > 0:
        return {"status": "aborted", "reason": "partial_alpha",
                "partial_alpha_pixels": partial_alpha_pixels}

    colors_before = len({(r, g, b) for r, g, b, a in pixels if a == 255})

    cache = {}
    distances = []
    new_pixels = []
    for (r, g, b, a) in pixels:
        if a == 0:
            new_pixels.append((r, g, b, a))
            continue
        key = (r, g, b)
        if key not in cache:
            cache[key] = nearest_palette_color(key, palette)
        nc, dist = cache[key]
        distances.append(dist)
        new_pixels.append((nc[0], nc[1], nc[2], a))

    out_im = Image.new("RGBA", im.size)
    out_im.putdata(new_pixels)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    out_im.save(dst_path)

    colors_after = len({(r, g, b) for r, g, b, a in new_pixels if a == 255})
    mean_dist = sum(distances) / len(distances) if distances else 0.0

    return {
        "status": "ok",
        "colors_before": colors_before,
        "colors_after": colors_after,
        "mean_snap_distance": mean_dist,
        "dimensions": im.size,
    }


def main():
    parser = argparse.ArgumentParser(description="Snap sprite colors to the Oryx master palette")
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--palette", default="config/art/oryx_master_palette.json")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    palette = load_palette(args.palette)
    os.makedirs(args.output_dir, exist_ok=True)

    ok_count, aborted = 0, []
    for fname in sorted(os.listdir(args.source_dir)):
        if not fname.endswith(".png"):
            continue
        src = os.path.join(args.source_dir, fname)
        dst = os.path.join(args.output_dir, fname)
        result = snap_file(src, palette, dst)

        if result["status"] == "aborted":
            aborted.append(fname)
            print(f"ABORTED {fname}: {result['partial_alpha_pixels']} partial-alpha pixels "
                  f"(needs structural cleanup before snapping)", file=sys.stderr)
        else:
            ok_count += 1
            print(f"{fname}: colors {result['colors_before']} -> {result['colors_after']}, "
                  f"mean_snap_distance={result['mean_snap_distance']:.2f}")

    print(f"\nProcessed {ok_count + len(aborted)} files: {ok_count} snapped, "
          f"{len(aborted)} aborted")
    if aborted:
        print("Aborted (partial alpha):", ", ".join(aborted))


if __name__ == "__main__":
    main()
