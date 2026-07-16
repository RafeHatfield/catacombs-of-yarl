#!/usr/bin/env python3
"""General art-conformance checker — Part A of config/rubric/art-lint-spec.md.

Two target modes:
  --target-dir DIR      every PNG in DIR, class inferred from directory name
                         (falls back to --default-class for staging dirs that
                         don't match a known sprites_16bf subdirectory name).
  --target-manifest FILE  every entry in a generated_assets_manifest.json —
                         path, asset_class, and lint_exemptions come from the
                         manifest, never from directory-name guessing (this is
                         the mechanism the spec calls for in Part C: "Audit
                         passes over live assets target files listed in
                         generated_assets_manifest.json, never naming
                         heuristics").

Thresholds are transcribed verbatim from config/rubric/art-lint-spec.md.
Do not adjust them here — if a threshold looks wrong in practice, that's a
finding to report, not a reason to edit this file.

A7 (speckle) is report-only per the spec: it is never PASS/WARN/FAIL and
never affects the exit code. "Speckle" is operationalized here as: an opaque
pixel where every one of its 4-adjacent (up/down/left/right) pixels either
falls outside the canvas, is transparent, or has a different RGB. This is
the algorithmic reading of "differs from all 4-neighbors" — not specified
further by the spec, which explicitly defers thresholding to a later ruling.
"""
import argparse
import csv
import json
import os
import sys
from itertools import combinations

from PIL import Image

DIR_CLASS_RESOLUTION = {
    "world_24x24": ("world_tile", (24, 24)),
    "items_16x16": ("item", (16, 16)),
    "creatures_24x24": ("creature", (24, 24)),
    "classes_26x28": ("class", (26, 28)),
    "fx_24x24": ("fx", (24, 24)),
    "fx_32x32": ("fx", (32, 32)),
}

# A3 — native resolution by class (bible §3). Classes absent here (e.g. the
# non-bible "class" bucket) are checked against DIR_CLASS_RESOLUTION instead.
RESOLUTION_BY_CLASS = {
    "world_tile": (24, 24),
    "prop": (24, 24),
    "decal": (24, 24),
    "creature": (24, 24),
    "item": (16, 16),
    "fx": (24, 24),
    "class": (26, 28),
}

# A4 — color budget (unique opaque RGB count). (warn_above, fail_above).
COLOR_BUDGET_BY_CLASS = {
    "world_tile": (8, 10),
    "prop": (8, 10),
    "decal": (8, 10),
    "fx": (8, 10),
    "item": (12, 21),
    "creature": (16, 18),
    "class": (16, 18),
}

# A5 — near-color pairs under 20 RGB units. (warn_above, fail_above), fixed.
A5_NEAR_THRESHOLD = 20
A5_WARN_ABOVE = 2
A5_FAIL_ABOVE = 7

# A6 — outline coverage. class -> (severity, min_fraction) or None (exempt).
A6_BY_CLASS = {
    "creature": ("FAIL", 0.90),
    "item": ("FAIL", 0.90),
    "prop": ("WARN", 0.75),
    "decal": None,
    "world_tile": None,
    "fx": None,
    "class": None,
}

DARK_MAX_CHANNEL = 70


def load_palette(path):
    with open(path) as f:
        data = json.load(f)
    return set(tuple(c) for c in data["colors"])


def opaque_pixels(im):
    return [(x, y, im.getpixel((x, y))) for y in range(im.height) for x in range(im.width)
            if im.getpixel((x, y))[3] == 255]


def check_a1_palette(pixels, palette_set):
    off = sum(1 for (_, _, (r, g, b, a)) in pixels if (r, g, b) not in palette_set)
    return off, ("FAIL" if off > 0 else "PASS")


def check_a2_alpha(im):
    partial = sum(1 for y in range(im.height) for x in range(im.width)
                  if 0 < im.getpixel((x, y))[3] < 255)
    return partial, ("FAIL" if partial > 0 else "PASS")


def check_a3_resolution(im, expected):
    ok = (im.width, im.height) == expected
    return (im.width, im.height), expected, ("PASS" if ok else "FAIL")


def check_a4_color_budget(pixels, asset_class):
    count = len({(r, g, b) for (_, _, (r, g, b, a)) in pixels})
    warn_above, fail_above = COLOR_BUDGET_BY_CLASS.get(asset_class, (8, 10))
    if count > fail_above:
        status = "FAIL"
    elif count > warn_above:
        status = "WARN"
    else:
        status = "PASS"
    return count, status


def check_a5_near_colors(pixels):
    colors = sorted({(r, g, b) for (_, _, (r, g, b, a)) in pixels})
    near_pairs = 0
    for (r1, g1, b1), (r2, g2, b2) in combinations(colors, 2):
        dist_sq = (r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2
        if dist_sq < A5_NEAR_THRESHOLD ** 2:
            near_pairs += 1
    if near_pairs > A5_FAIL_ABOVE:
        status = "FAIL"
    elif near_pairs > A5_WARN_ABOVE:
        status = "WARN"
    else:
        status = "PASS"
    return near_pairs, status


def check_a6_outline(im, asset_class, exempt):
    rule = A6_BY_CLASS.get(asset_class)
    if exempt or rule is None:
        return None, "EXEMPT"
    severity, min_fraction = rule

    boundary = 0
    dark = 0
    w, h = im.width, im.height
    for y in range(h):
        for x in range(w):
            r, g, b, a = im.getpixel((x, y))
            if a != 255:
                continue
            is_boundary = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or im.getpixel((nx, ny))[3] == 0:
                    is_boundary = True
                    break
            if is_boundary:
                boundary += 1
                if max(r, g, b) < DARK_MAX_CHANNEL:
                    dark += 1

    if boundary == 0:
        return None, "EXEMPT"
    fraction = dark / boundary
    if fraction < min_fraction:
        status = severity
    else:
        status = "PASS"
    return round(fraction, 4), status


def count_speckle(im):
    w, h = im.width, im.height
    speckle = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = im.getpixel((x, y))
            if a != 255:
                continue
            matched = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    nr, ng, nb, na = im.getpixel((nx, ny))
                    if na == 255 and (nr, ng, nb) == (r, g, b):
                        matched = True
                        break
            if not matched:
                speckle += 1
    return speckle


def lint_file(path, asset_class, palette_set, a6_exempt=False):
    im = Image.open(path).convert("RGBA")
    pixels = opaque_pixels(im)

    off_palette, a1 = check_a1_palette(pixels, palette_set)
    partial_alpha, a2 = check_a2_alpha(im)
    expected_res = RESOLUTION_BY_CLASS.get(asset_class, (im.width, im.height))
    actual_res, expected_res, a3 = check_a3_resolution(im, expected_res)
    color_count, a4 = check_a4_color_budget(pixels, asset_class)
    near_pairs, a5 = check_a5_near_colors(pixels)
    outline_fraction, a6 = check_a6_outline(im, asset_class, a6_exempt)
    speckle = count_speckle(im)

    row = {
        "file": path,
        "asset_class": asset_class,
        "A1_off_palette_colors": off_palette, "A1": a1,
        "A2_partial_alpha_pixels": partial_alpha, "A2": a2,
        "A3_actual_resolution": f"{actual_res[0]}x{actual_res[1]}",
        "A3_expected_resolution": f"{expected_res[0]}x{expected_res[1]}", "A3": a3,
        "A4_color_count": color_count, "A4": a4,
        "A5_near_color_pairs": near_pairs, "A5": a5,
        "A6_outline_fraction": outline_fraction if outline_fraction is not None else "",
        "A6": a6,
        "A7_speckle_count": speckle,
    }
    any_fail = any(row[k] == "FAIL" for k in ("A1", "A2", "A3", "A4", "A5", "A6"))
    row["overall"] = "FAIL" if any_fail else (
        "WARN" if any(row[k] == "WARN" for k in ("A4", "A5", "A6")) else "PASS")
    return row


def targets_from_dir(target_dir, default_class):
    targets = []
    dirname = os.path.basename(os.path.normpath(target_dir))
    asset_class, _ = DIR_CLASS_RESOLUTION.get(dirname, (default_class, None))
    for fname in sorted(os.listdir(target_dir)):
        if fname.endswith(".png"):
            targets.append((os.path.join(target_dir, fname), asset_class, False))
    return targets


def targets_from_manifest(manifest_path):
    with open(manifest_path) as f:
        manifest = json.load(f)
    targets = []
    for e in manifest["entries"]:
        exempt = "A6_outline" in e.get("lint_exemptions", [])
        targets.append((e["path"], e["asset_class"], exempt))
    return targets


def main():
    parser = argparse.ArgumentParser(description="Art conformance checker (spec Part A)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--target-dir")
    group.add_argument("--target-manifest")
    parser.add_argument("--default-class", default="prop",
                        help="asset_class for --target-dir files not in a known sprites_16bf subdir")
    parser.add_argument("--palette", default="config/art/oryx_master_palette.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    palette_set = load_palette(args.palette)

    if args.target_dir:
        targets = targets_from_dir(args.target_dir, args.default_class)
    else:
        targets = targets_from_manifest(args.target_manifest)

    rows = []
    for path, asset_class, exempt in targets:
        if not os.path.exists(path):
            print(f"MISSING: {path}", file=sys.stderr)
            continue
        rows.append(lint_file(path, asset_class, palette_set, exempt))

    fieldnames = ["file", "asset_class",
                  "A1_off_palette_colors", "A1", "A2_partial_alpha_pixels", "A2",
                  "A3_actual_resolution", "A3_expected_resolution", "A3",
                  "A4_color_count", "A4", "A5_near_color_pairs", "A5",
                  "A6_outline_fraction", "A6", "A7_speckle_count", "overall"]
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    fails = sum(1 for r in rows if r["overall"] == "FAIL")
    warns = sum(1 for r in rows if r["overall"] == "WARN")
    passes = total - fails - warns

    print(f"=== Lint Summary: {args.output} ===")
    print(f"Files checked: {total}")
    print(f"PASS: {passes}  WARN: {warns}  FAIL: {fails}")
    for check in ("A1", "A2", "A3", "A4", "A5", "A6"):
        c = {}
        for r in rows:
            c[r[check]] = c.get(r[check], 0) + 1
        print(f"  {check}: {c}")
    speckle_vals = [r["A7_speckle_count"] for r in rows]
    if speckle_vals:
        print(f"  A7 speckle (report-only): min={min(speckle_vals)} "
              f"max={max(speckle_vals)} mean={sum(speckle_vals)/len(speckle_vals):.2f}")

    sys.exit(1 if fails > 0 else 0)


if __name__ == "__main__":
    main()
