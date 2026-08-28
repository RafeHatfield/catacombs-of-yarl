#!/usr/bin/env python3
"""One question: is the bar's terrain sheet grid what `measure_bar.Tiles` assumes it is?

The calibration run excluded EVERY floor gid for being 14-89% opaque, which cannot be true of a
floor tile — a floor is the opaque thing everything else sits on. Either the bar's floors really
are drawn on transparency, or the gid -> pixel resolution is landing somewhere other than on a
tile. Those two have opposite consequences and guessing between them is not available.

MEASUREMENTS LEAVE; PIXELS NEVER DO (§13.3). Prints numbers. Writes nothing.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools/sighted_round"))
import measure_bar as MB      # noqa: E402

SHEET = os.path.join(MB.BAR_ROOT, "uf_terrain.png")
T = 48

img = np.array(Image.open(SHEET).convert("RGBA")).astype(float)
H, W = img.shape[:2]
print("sheet %s  %dx%d   grid %dx%d at T=%d   tiles=%d"
      % (os.path.basename(SHEET), W, H, W // T, H // T, T, (W // T) * (H // T)))
A = img[..., 3]
print("sheet alpha: opaque fraction overall = %.3f" % float((A > 128).mean()))

cols = W // T
print("\nper-tile opacity for the gids the maps' floor layer cites (gid-1 = index):")
for gid in (62, 63, 64, 66, 67, 102, 112):
    i = gid - 1
    r, c = i // cols, i % cols
    cell = img[r * T:(r + 1) * T, c * T:(c + 1) * T]
    a = cell[..., 3]
    print("  gid %-4d idx %-4d row %-2d col %-2d  opaque=%.3f  "
          "alpha values present: %s"
          % (gid, i, r, c, float((a > 128).mean()),
             sorted(set(np.round(a).flatten().tolist()))[:6]))

print("\nopacity histogram over the whole sheet, per tile:")
op = []
for r in range(H // T):
    for c in range(cols):
        a = img[r * T:(r + 1) * T, c * T:(c + 1) * T, 3]
        op.append(float((a > 128).mean()))
op = np.array(op)
for lo, hi in ((0.0, 0.01), (0.01, 0.5), (0.5, 0.99), (0.99, 1.01)):
    print("  opaque in [%.2f,%.2f): %d tiles" % (lo, hi, int(((op >= lo) & (op < hi)).sum())))
print("  fully opaque tiles: %d of %d" % (int((op >= 0.99).sum()), len(op)))
