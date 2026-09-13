#!/usr/bin/env python3
"""SCREEN A GENERATION WAVE against the clauses the prompt files declare load-bearing.

⚠ THIS GATES NOTHING. CLAUDE.md: instruments are builder's tools and are forever ungated; a FAIL
here blocks nothing and a PASS approves nothing. What it does is stop me carrying an obvious
clause violation all the way to a blind seat, which wastes the seat's round on something the
prompt already refused in writing.

WHAT IT MEASURES, and each one is a clause with a number rather than a taste:

  outline_ratio   §12.1 — no baked dark ring. The alpha silhouette's boundary pixels against the
                  interior. A generator that draws an outline makes this ratio drop well below 1.
  glow_r          §6.3 — no baked halo. Correlation of luminance with distance from the brightest
                  region, over opaque pixels. A painted glow is bright at the middle and falls off
                  monotonically, so it correlates strongly negative. Authored form does not.
  margin_alpha    a glow that spills into the transparent margin shows up as partial alpha in the
                  outer ring — the halo's own footprint.
  mass            §7.3 / the direction ruling — mass in the silhouette. Opaque fraction.
  value band      the family's measured ladder is lum_lo 75.0 to lum_hi 154.4. Generated material
                  is snapped at composition, so this is reported and not judged; a wildly off band
                  means the snap will have to do violence.

Usage: python3 tools/tier2_props/screen_wave.py tools/tier2_props/gen/wave1
"""
import os
import sys
import numpy as np
from PIL import Image

LUM_LO, LUM_HI = 75.016, 154.376          # the ashlar family's measured ladder ends


def screen(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im, dtype=float)
    rgb, alpha = a[:, :, :3], a[:, :, 3]
    op = alpha > 128
    if op.sum() < 20:
        return None
    lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]

    # ── §12.1: the silhouette's boundary against its interior ────────────────────────────────
    from scipy import ndimage  # noqa
    er = ndimage.binary_erosion(op, np.ones((3, 3), bool))
    edge, inner = op & ~er, er
    outline_ratio = (lum[edge].mean() / lum[inner].mean()) if inner.sum() > 10 else float("nan")

    # ── §6.3: does luminance fall off radially from the bright core? ─────────────────────────
    ys, xs = np.where(op)
    bright = lum[op] >= np.percentile(lum[op], 90)
    cy, cx = ys[bright].mean(), xs[bright].mean()
    d = np.hypot(ys - cy, xs - cx)
    glow_r = float(np.corrcoef(d, lum[op])[0, 1])

    # a halo's own footprint: partial alpha in the outer ring of the canvas
    h, w = alpha.shape
    ring = np.zeros_like(op)
    ring[:3, :] = ring[-3:, :] = ring[:, :3] = ring[:, -3:] = True
    margin = float(((alpha > 8) & (alpha <= 128) & ring).sum())

    return dict(mass=op.mean(), outline=outline_ratio, glow=glow_r, margin=margin,
                lum_lo=float(lum[op].min()), lum_hi=float(lum[op].max()),
                lum_med=float(np.median(lum[op])), colours=len(np.unique(
                    (rgb[op] // 8).astype(int) @ np.array([1, 1000, 1000000]))))


def main(d):
    print("WAVE SCREEN — %s\n" % d)
    print("  name           mass   outline   glow   margin   lum lo/med/hi      cols  notes")
    rows = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".png"):
            continue
        r = screen(os.path.join(d, f))
        if r is None:
            print("  %-13s  EMPTY" % f[:-4])
            continue
        notes = []
        if r["outline"] < 0.80:
            notes.append("BAKED OUTLINE?")
        if r["glow"] < -0.45:
            notes.append("BAKED GLOW?")
        if r["margin"] > 12:
            notes.append("halo spill")
        if r["mass"] < 0.18:
            notes.append("thin")
        print("  %-13s  %.2f   %6.2f  %+5.2f   %5d    %5.1f/%5.1f/%5.1f   %4d  %s"
              % (f[:-4], r["mass"], r["outline"], r["glow"], r["margin"],
                 r["lum_lo"], r["lum_med"], r["lum_hi"], r["colours"], ", ".join(notes)))
        rows.append((f[:-4], r, notes))
    print("\nthe family's ladder runs %.1f to %.1f; material is snapped at composition, so the"
          % (LUM_LO, LUM_HI))
    print("value columns are reported rather than judged.")
    clean = [n for n, _, notes in rows if not notes]
    print("\n%d of %d carry no flagged clause violation: %s"
          % (len(clean), len(rows), ", ".join(clean) or "(none)"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tools/tier2_props/gen/wave1")
