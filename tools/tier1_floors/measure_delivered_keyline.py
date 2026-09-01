#!/usr/bin/env python3
"""IS EVERY STONE OUTLINED — ON THE FRAME THAT WAS ACTUALLY SHOWN?

§13.9's CONVERSE, ruled 2026-08-31 after a device walk contradicted a green table and the walk won
(§13.2). §13.9 says a signal the rig does not deliver is absent however well it was authored. Its
converse is the one that cost this round:

    AN ARTEFACT THE RIG CREATES IS PRESENT HOWEVER CLEAN THE SOURCE IS.
    SOURCE-CLEAN IS NECESSARY AND NOT SUFFICIENT.

`joint_contrast` and `constant_pitch` both went green on the laid field — share above the floor
20.3%, grid line under §13.8 — and the phone still showed a keyline, strongest in the lamp's pool
and fading into the dark. A metric that only ever reads the composer's output cannot see anything
the renderer adds, and everything this campaign bans is a thing a viewer sees.

MASK-FREE, DELIBERATELY. There is no joint mask on a delivered frame and reconstructing one would
be measuring the reconstruction. Instead each floor pixel is compared to the brightest pixel in its
own small neighbourhood: an outlined floor is one where a large share of pixels sit far below their
local maximum, in thin runs. That is what "outlined chips" means as a measurement.

BINNED BY DELIVERED ILLUMINATION, because the complaint has a shape — strongest where the lamp
reaches. A ring that grows with light is the rig's doing; one that is flat is the source's.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import field_laws as FL                  # noqa: E402
import measure_perceptual_floor as MPF   # noqa: E402
import measure_traffic_read as MTR       # noqa: E402

T = 64          # screen px per tile (32 art at x2)
DARK = 0.22     # a pixel is "outline" when it sits this far below its local maximum


def local_max(L, r=2):
    """Max over a (2r+1) square, by successive shifts — no scipy."""
    m = L.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx == 0 and dy == 0:
                continue
            m = np.maximum(m, np.roll(np.roll(L, dy, 0), dx, 1))
    return m


def measure(png, log):
    L = MPF.lum(np.asarray(Image.open(png).convert("RGB")).astype(float))
    f = MTR.read_field(log)
    if f is None:
        return None
    H, W = L.shape
    fh, fw = f.shape
    oy, ox = (H - fh * T) // 2, (W - fw * T) // 2

    floor = np.zeros(L.shape, bool)
    for ty in range(fh):
        for tx in range(fw):
            if f[ty, tx] < 0:
                continue
            y0, x0 = oy + ty * T, ox + tx * T
            if y0 < 0 or x0 < 0 or y0 + T > H or x0 + T > W:
                continue
            floor[y0:y0 + T, x0:x0 + T] = True

    lm = local_max(L)
    below = (lm - L) / np.maximum(lm, 1e-6)
    outline = floor & (below > DARK)

    bands = []
    for lo, hi, name in ((0, 40, "dark      <40"), (40, 80, "dim     40-80"),
                         (80, 140, "lit    80-140"), (140, 256, "bright  >140")):
        m = floor & (L >= lo) & (L < hi)
        if m.sum() < 500:
            continue
        bands.append(dict(band=name, px=int(m.sum()),
                          outline_share=round(float(outline[m].mean()), 4),
                          mean_below=round(float(below[m].mean()), 4)))
    return dict(floor_px=int(floor.sum()),
                outline_share=round(float(outline[floor].mean()), 4), bands=bands)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("captures", nargs="*", help="evidence stems, e.g. r24_onroute")
    a = ap.parse_args()
    stems = a.captures or sorted(
        os.path.basename(p)[:-4]
        for p in glob.glob(os.path.join(HERE, "evidence", "r2*_*.png")))

    print("IS EVERY STONE OUTLINED, ON THE FRAME THAT WAS SHOWN?\n")
    print("  A pixel counts as outline when it sits >%.0f%% below the brightest pixel within two"
          % (DARK * 100))
    print("  of it. Binned by DELIVERED illumination: a ring that GROWS with the light is the")
    print("  rig's doing; a flat one is the source's.\n")
    out = {}
    for stem in stems:
        png = os.path.join(HERE, "evidence", stem + ".png")
        log = os.path.join(HERE, "evidence", stem + ".log")
        if not (os.path.exists(png) and os.path.exists(log)):
            continue
        r = measure(png, log)
        if r is None:
            continue
        out[stem] = r
        print("  %-26s overall %5.1f%%   %s"
              % (stem, 100 * r["outline_share"],
                 "  ".join("%s %4.1f%%" % (b["band"].split()[0], 100 * b["outline_share"])
                           for b in r["bands"])))
    p = os.path.join(HERE, "evidence", "DELIVERED-KEYLINE.json")
    json.dump(dict(commit=FL.git_commit(), dark=DARK, captures=out), open(p, "w"), indent=1)
    print("\n  written: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
