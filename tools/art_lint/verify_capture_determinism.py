#!/usr/bin/env python3
"""Pixel-identity self-test (docs/art_test_scene_spec_v2.md §4): two independent
cold-start captures of the art scene must be identical.

Comparison basis: SHA-256 of the raw PNG bytes, not just decoded pixels. Godot's PNG
encoder embeds no timestamp/random metadata for this asset type in testing so far — the
byte-level hash is also the pixel-level comparison here; if a future Godot/encoder change
introduces incidental metadata drift (chunk ordering, embedded text chunks) while pixels
stay identical, this script's decoded-pixel fallback comparison (via PIL) will still pass
and the discrepancy will be visible in the printed report, not hidden.

If the two captures differ, this contradicts FloorComposer's documented determinism
(seed=0, pure function of the map) and the scene's own "no seeds, no rolls, no variant
selection" design (spec §4) — stop and report, do not add a tolerance threshold.
"""
import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_scene import capture, DEFAULT_GODOT


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Pixel-identity self-test for the art scene capture")
    parser.add_argument("--out-dir", default="tools/art_lint/scene_evidence")
    parser.add_argument("--godot", default=DEFAULT_GODOT)
    args = parser.parse_args()

    run1_png = os.path.join(args.out_dir, "pixel_identity_run1.png")
    run2_png = os.path.join(args.out_dir, "pixel_identity_run2.png")

    rc1, log1, res1 = capture(args.godot, run1_png)
    rc2, log2, res2 = capture(args.godot, run2_png)

    if rc1 != 0 or rc2 != 0 or not os.path.exists(run1_png) or not os.path.exists(run2_png):
        print("ABORT: one or both captures failed.", file=sys.stderr)
        print(log1, file=sys.stderr)
        print(log2, file=sys.stderr)
        sys.exit(1)

    hash1, hash2 = sha256(run1_png), sha256(run2_png)
    byte_identical = hash1 == hash2

    pixel_identical = byte_identical
    if not byte_identical:
        from PIL import Image
        im1, im2 = Image.open(run1_png).convert("RGBA"), Image.open(run2_png).convert("RGBA")
        pixel_identical = (im1.size == im2.size) and (list(im1.getdata()) == list(im2.getdata()))

    report_path = os.path.join(args.out_dir, "pixel_identity_comparison.txt")
    with open(report_path, "w") as f:
        f.write(f"run1: {run1_png}\n  sha256: {hash1}\n  resolution: {res1}\n")
        f.write(f"run2: {run2_png}\n  sha256: {hash2}\n  resolution: {res2}\n")
        f.write(f"byte_identical: {byte_identical}\n")
        f.write(f"pixel_identical: {pixel_identical}\n")
        f.write("basis: SHA-256 of raw PNG bytes (see module docstring for why this is "
                 "also the pixel-level comparison here)\n")

    print(open(report_path).read())
    if not pixel_identical:
        print("FAIL: captures are not pixel-identical. This contradicts FloorComposer's "
              "documented determinism — investigate before proceeding, do not add tolerance.",
              file=sys.stderr)
        sys.exit(1)

    print("PASS: two cold-start captures are " +
          ("byte-identical" if byte_identical else "pixel-identical (byte-level metadata differs)"))


if __name__ == "__main__":
    main()
