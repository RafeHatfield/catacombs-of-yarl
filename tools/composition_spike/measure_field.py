#!/usr/bin/env python3
"""Check the critic's repetition charge against the capture itself.

Round 3's seat said of the north-south wall mass: "the same 32px stamp repeated identically for
roughly twenty columns by twenty-eight rows without a single variation" and "the dark Y-mark
and dark bar land on the same pixel row in every tile".

That is a measurable claim and it disagrees with what this session measured on the TILES
(median tile-to-mean correlation 0.441 across nine interior_fill variants, zero identical
pairs) and with control 3 (pinning interior_fill to one id moves 18.079% of the capture's
pixels, which it could not do if the variants were not being drawn).

Both cannot be right about the same thing, so this measures the RENDERED FIELD - the thing the
seat actually looked at - rather than the tiles or the config. A seat's finding is not taken at
face value and neither is this session's own.

Method: the capture is the corridor at 32px tiles, x2 zoom, so a tile is 64 screen px. The grid
origin is recovered from the strongest vertical edge periodicity rather than assumed, a block
of solid-wall cells is sampled well away from the corridor, and each 64x64 block is correlated
against the block mean.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.join(HERE, "evidence")
TILE_PX = 64          # 32px tile at x2


def grid_origin(gray):
    """Recover the x/y phase of the tile grid from column/row difference energy."""
    def phase(diff):
        best, best_p = -1.0, 0
        for p in range(TILE_PX):
            s = diff[p::TILE_PX].sum()
            if s > best:
                best, best_p = s, p
        return best_p
    dx = np.abs(np.diff(gray, axis=1)).sum(0)
    dy = np.abs(np.diff(gray, axis=0)).sum(1)
    return phase(dx), phase(dy)


def field_blocks(img, x0, y0, cols, rows, ox, oy):
    out = []
    for r in range(rows):
        for c in range(cols):
            x = ox + (x0 + c) * TILE_PX
            y = oy + (y0 + r) * TILE_PX
            b = img[y:y + TILE_PX, x:x + TILE_PX]
            if b.shape[:2] == (TILE_PX, TILE_PX):
                out.append(b.astype(float))
    return out


def report(name, x0, y0, cols, rows):
    p = os.path.join(EVIDENCE, name)
    im = np.array(Image.open(p).convert("RGB"))
    gray = im[..., 0] * .299 + im[..., 1] * .587 + im[..., 2] * .114
    ox, oy = grid_origin(gray)
    blocks = field_blocks(im, x0, y0, cols, rows, ox, oy)
    if len(blocks) < 4:
        print("  %-28s too few blocks sampled" % name)
        return
    mean = np.mean(blocks, axis=0)
    cors = [np.corrcoef(b.ravel(), mean.ravel())[0, 1] for b in blocks]
    ident = sum(1 for i in range(len(blocks)) for j in range(i + 1, len(blocks))
                if np.array_equal(blocks[i], blocks[j]))
    print("  %-28s grid phase (%2d,%2d)  %2d blocks  median corr %.3f  "
          "identical pairs %d/%d"
          % (name, ox, oy, len(blocks), float(np.median(cors)), ident,
             len(blocks) * (len(blocks) - 1) // 2))


def main():
    print("RENDERED WALL FIELD - repetition, measured on the capture")
    print("sampling a block of solid-wall cells left of the corridor, below the branch\n")
    for name in ("boundB_lit.png", "ctrlB_lit.png", "boundB_solofloor_lit.png"):
        report(name, x0=0, y0=8, cols=5, rows=5)
    print("\nA median correlation near 1.0 with many identical pairs would confirm the seat's")
    print("charge. Anything well below it means the field varies and the charge is about")
    print("something else - most likely that nine offsets of ONE part still read as one part.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
