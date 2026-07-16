#!/usr/bin/env python3
"""Independent verification of palette-snapped sprites.

Re-derives every check from the output pixels and the master palette rather
than trusting snap_to_palette.py's own bookkeeping, so a bug in the snapper
can't silently pass its own report.
"""
import argparse
import csv
import json
import math
import os
import sys

from PIL import Image


def load_palette(path):
    with open(path) as f:
        data = json.load(f)
    return set(tuple(c) for c in data["colors"]), data["count"]


def verify_file(fname, source_dir, snapped_dir, palette_set):
    snapped_im = Image.open(os.path.join(snapped_dir, fname)).convert("RGBA")
    snapped_pixels = list(snapped_im.getdata())

    off_palette = 0
    partial_alpha = 0
    opaque_colors_after = set()
    for (r, g, b, a) in snapped_pixels:
        if 0 < a < 255:
            partial_alpha += 1
        elif a == 255:
            opaque_colors_after.add((r, g, b))
            if (r, g, b) not in palette_set:
                off_palette += 1

    source_path = os.path.join(source_dir, fname)
    dims_changed = False
    colors_before = ""
    mean_dist = 0.0
    if os.path.exists(source_path):
        source_im = Image.open(source_path).convert("RGBA")
        dims_changed = source_im.size != snapped_im.size
        source_pixels = list(source_im.getdata())
        colors_before = len({(r, g, b) for r, g, b, a in source_pixels if a == 255})

        dists = []
        for sp, np_ in zip(source_pixels, snapped_pixels):
            if sp[3] == 255 and np_[3] == 255:
                dists.append(math.sqrt(
                    (sp[0] - np_[0]) ** 2 + (sp[1] - np_[1]) ** 2 + (sp[2] - np_[2]) ** 2
                ))
        mean_dist = sum(dists) / len(dists) if dists else 0.0
    else:
        print(f"WARNING: no source file for {fname}, skipping before/after comparison",
              file=sys.stderr)

    return {
        "file": fname,
        "off_palette_colors": off_palette,
        "colors_before": colors_before,
        "colors_after": len(opaque_colors_after),
        "partial_alpha_pixels": partial_alpha,
        "dimensions_changed": dims_changed,
        "mean_snap_distance": round(mean_dist, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Verify palette-snapped sprites")
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--snapped-dir", required=True)
    parser.add_argument("--palette", default="config/art/oryx_master_palette.json")
    parser.add_argument("--output", default="snap_report.csv")
    args = parser.parse_args()

    palette_set, palette_size = load_palette(args.palette)

    rows = [
        verify_file(fname, args.source_dir, args.snapped_dir, palette_set)
        for fname in sorted(os.listdir(args.snapped_dir))
        if fname.endswith(".png")
    ]

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "file", "off_palette_colors", "colors_before", "colors_after",
            "partial_alpha_pixels", "dimensions_changed", "mean_snap_distance",
        ])
        writer.writeheader()
        writer.writerows(rows)

    files_processed = len(rows)
    all_off_palette_zero = all(r["off_palette_colors"] == 0 for r in rows)
    all_partial_alpha_zero = all(r["partial_alpha_pixels"] == 0 for r in rows)
    all_dims_unchanged = all(not r["dimensions_changed"] for r in rows)
    max_snap_distance = max((r["mean_snap_distance"] for r in rows), default=0.0)
    mean_of_means = (sum(r["mean_snap_distance"] for r in rows) / files_processed
                      if files_processed else 0.0)
    palette_size_ok = palette_size < 600

    print("=== Verification Summary ===")
    print(f"Master palette size: {palette_size} (< 600: {palette_size_ok})")
    print(f"Files processed: {files_processed}")
    print(f"Max per-file mean snap distance: {max_snap_distance:.3f}")
    print(f"Mean snap distance across set: {mean_of_means:.3f}")
    print(f"All off_palette_colors == 0: {all_off_palette_zero}")
    print(f"All partial_alpha_pixels == 0: {all_partial_alpha_zero}")
    print(f"All dimensions unchanged: {all_dims_unchanged}")

    gate_pass = (
        all_off_palette_zero
        and all_partial_alpha_zero
        and all_dims_unchanged
        and palette_size_ok
        and mean_of_means > 0
    )
    print(f"\nMERGE GATE: {'PASS' if gate_pass else 'FAIL'}")

    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
