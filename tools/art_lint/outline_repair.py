#!/usr/bin/env python3
"""Outline-repair pass: trace the darkest in-sprite ramp color onto every
silhouette-boundary pixel.

A6 (art-lint-spec) defines a boundary pixel as an opaque pixel with at least one
4-neighbor that is transparent or out of bounds, and counts it as "dark" when
max(r,g,b) < 70. Creatures/items must have >= 0.90 dark-boundary coverage.

This pass takes a sprite that reads correctly but has a broken/partial outline,
finds its own darkest fully-opaque color (min by max channel -- the natural
outline color already in the ramp), and paints that color onto the full
silhouette boundary. Because the color is already in the sprite (hence already a
palette member after snapping), A1 stays green; because no new color is
introduced, A4/A5 cannot get worse; A6 goes to ~1.0.

Does not touch interior pixels, alpha, or resolution. This is a repair, not a
redesign -- it only rewrites the one-pixel edge.
"""
import argparse
import os
import sys

from PIL import Image


def darkest_opaque_color(im):
    colors = set()
    w, h = im.size
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 255:
                colors.add((r, g, b))
    if not colors:
        return None
    return min(colors, key=lambda c: max(c))


def boundary_pixels(im):
    w, h = im.size
    px = im.load()
    out = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] != 255:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or px[nx, ny][3] == 0:
                    out.append((x, y))
                    break
    return out


def repair(src, dst):
    im = Image.open(src).convert("RGBA")
    dark = darkest_opaque_color(im)
    if dark is None:
        raise SystemExit(f"{src}: no opaque pixels")
    if max(dark) >= 70:
        raise SystemExit(
            f"{src}: darkest in-sprite color {dark} has max channel {max(dark)} >= 70; "
            "tracing it would not satisfy A6's dark-boundary test. Aborting rather than "
            "introducing an off-ramp color.")
    px = im.load()
    changed = 0
    for (x, y) in boundary_pixels(im):
        if px[x, y][:3] != dark:
            px[x, y] = (*dark, 255)
            changed += 1
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    im.save(dst)
    print(f"{os.path.basename(src)} -> {os.path.basename(dst)}: "
          f"outline color {dark}, {changed} boundary pixels rewritten")
    return dark, changed


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Trace darkest in-sprite color onto silhouette boundary")
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    args = ap.parse_args()
    repair(args.src, args.dst)
