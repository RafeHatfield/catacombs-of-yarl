#!/usr/bin/env python3
"""HOW MANY PLANES IS THIS OBJECT SHOWING? — the object-projection instrument.

    python3 tools/tier2_props/measure_projection.py

§3 is ratified and it is specific: *"Objects and walls present exactly two visible planes: a
front face and a top surface."* That is a geometric claim, so it is measurable, and this
measures it two ways that fail independently.

── 1. SILHOUETTE SYMMETRY ────────────────────────────────────────────────────────────────────
An object showing only a top and a south face is BILATERALLY SYMMETRIC about its vertical axis:
whatever the top does, it does the same at both ends, and the front face is square to the
viewer. Reveal one side and the silhouette leans — the side adds width on exactly one hand.

    symmetry = the fraction of opaque pixels that survive mirroring the sprite about its own
               vertical centre line. 1.00 is perfectly symmetric.

⚠ IT IS NECESSARY, NOT SUFFICIENT, and the file says so rather than letting a reader assume.
A symmetric silhouette can still be drawn with a skewed top INSIDE it. That is what the second
measure is for.

── 2. TOP-EDGE SHEAR ─────────────────────────────────────────────────────────────────────────
In a two-plane object the top surface is an axis-aligned rectangle, so the sprite's topmost
opaque row is FLAT: its left and right ends sit at the same height. Shear the top into a
parallelogram — every three-plane projection does — and the topmost row tilts.

    shear = the height difference, in native pixels, between where the top edge starts on the
            left and where it ends on the right, as a fraction of the sprite's width.

Zero is flat. A 45-degree cabinet oblique on a square object approaches 1.0.

── 3. THE INTERIOR SEAM, and it is here because the first two were not enough ────────────────
⚠ BOTH MEASURES ABOVE READ THE SILHOUETTE, AND A PROJECTION CAN BE DRAWN ENTIRELY INSIDE A
RECTANGULAR OUTLINE. The oblique standing stone scored symmetry 1.000 and shear 0.000 — a
perfect two-plane result — while plainly showing a top parallelogram and a left side, because
its OUTLINE is a rectangle and all the geometry is painted within it. The instrument was
measuring the box the object came in.

So the third measure looks inside: the seam where the top surface meets the front face is the
strongest horizontal luminance step in the upper half of the sprite, and in a two-plane object
that seam is LEVEL. Tilt the top into a parallelogram and the seam tilts with it.

    seam_tilt = the height difference, in native pixels, between the seam at the left of the
                object and at the right, over the object's width. Zero is level.

── WHY THREE ────────────────────────────────────────────────────────────────────────────────
Symmetry catches a side face that widens the outline. Shear catches a skewed outline. Seam tilt
catches a projection painted inside a square outline, which is the case that fooled the first
two. §3 wants none of the three.

⚠ AND NONE OF THEM RULES. §13.2: the eye rules, on device. The projection is Rafe's to name.

⚠⚠ THE SEAM MEASURE IS NOT TRUSTWORTHY AND IS NOT USED TO ORDER THE CANDIDATES. Run against
the matrix it put the two-plane standing stone at 0.789 — a worse tilt than anything in the
oblique row — and the oblique standing stone at 0.000, which is the opposite of what the
contact sheet plainly shows. It is finding the strongest luminance step in the upper part of
the sprite, and on a textured stone that step is a JOINT rather than the top/front seam.

That is this project's own recurring lesson arriving in a new place: an instrument can be
correct, controlled, and answering the wrong question. It is left in, reported with its
failure, and explicitly excluded from ordering, because a measure that disagrees with the
picture is evidence about the measure.

WHAT THE NUMBERS ARE GOOD FOR: symmetry and top-shear read the silhouette honestly and agree
with the sheet. They are reported. The ordering, and the ruling, come from the walk.
"""
import glob
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
D = os.path.join(REPO, "src/Presentation/assets/tier1_ashlar/tier1_ashlar_%d.png")

MATRIX = [
    ("W  two-plane", [("stone", [9850, 9851], 1, 2), ("crate", [9852], 1, 1),
                      ("barrel", [9853], 1, 1), ("altar", [9854, 9855], 2, 1),
                      ("rack", [9856], 1, 1)]),
    ("A  oblique", [("stone", [9857, 9858], 1, 2), ("crate", [9859], 1, 1),
                    ("barrel", [9860], 1, 1), ("altar", [9861, 9862], 2, 1),
                    ("rack", [9863], 1, 1)]),
    ("C  current", [("stone", [9864, 9865], 1, 2), ("crate", [9866], 1, 1),
                    ("barrel", [9867], 1, 1), ("altar", [9868, 9869], 2, 1),
                    ("rack", [9870], 1, 1)]),
]
CELL = 32


def assemble(ids, w, h):
    im = Image.new("RGBA", (w * CELL, h * CELL))
    for i, tid in enumerate(ids):
        im.paste(Image.open(D % tid).convert("RGBA"), ((i % w) * CELL, (i // w) * CELL))
    return np.asarray(im)[:, :, 3] > 0


def symmetry(op):
    cols = np.where(op.any(axis=0))[0]
    rows = np.where(op.any(axis=1))[0]
    if not len(cols):
        return 0.0
    box = op[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    mirrored = box[:, ::-1]
    both = (box & mirrored).sum()
    either = (box | mirrored).sum()
    return float(both) / float(either) if either else 0.0


def top_shear(op):
    """Height of the top edge at the left extreme vs the right extreme, over the width."""
    cols = np.where(op.any(axis=0))[0]
    if len(cols) < 4:
        return 0.0
    # the top edge: first opaque row per column, over the middle 80% to ignore stray corners
    lo, hi = cols.min(), cols.max()
    span = hi - lo + 1
    a, b = lo + int(span * 0.10), hi - int(span * 0.10)
    tops = []
    for x in range(a, b + 1):
        r = np.where(op[:, x])[0]
        tops.append(r.min() if len(r) else None)
    tops = [t for t in tops if t is not None]
    if len(tops) < 4:
        return 0.0
    k = max(2, len(tops) // 5)
    left = float(np.mean(tops[:k]))
    right = float(np.mean(tops[-k:]))
    return abs(left - right) / float(span)


def seam_tilt(ids, w, h):
    """Tilt of the top/front seam, measured on luminance INSIDE the silhouette."""
    im = Image.new("RGBA", (w * CELL, h * CELL))
    for i, tid in enumerate(ids):
        im.paste(Image.open(D % tid).convert("RGBA"), ((i % w) * CELL, (i // w) * CELL))
    a = np.asarray(im).astype(float)
    op = a[:, :, 3] > 0
    lum = a[:, :, :3] @ np.array([0.2126, 0.7152, 0.0722])
    cols = np.where(op.any(axis=0))[0]
    rows = np.where(op.any(axis=1))[0]
    if len(cols) < 4 or len(rows) < 4:
        return 0.0
    lo, hi = cols.min(), cols.max()
    span = hi - lo + 1
    top, bot = rows.min(), rows.max()
    # search the upper 60% of the object for the strongest downward step per column
    limit = top + max(2, int((bot - top) * 0.6))
    seams = []
    for x in range(lo + int(span * 0.12), hi - int(span * 0.12) + 1):
        col = np.where(op[:, x])[0]
        if len(col) < 4:
            seams.append(None)
            continue
        y0 = col.min()
        y1 = min(limit, col.max() - 1)
        if y1 - y0 < 3:
            seams.append(None)
            continue
        seg = lum[y0:y1 + 1, x]
        d = seg[:-1] - seg[1:]          # positive = it got darker going down
        seams.append(y0 + int(np.argmax(d)) if len(d) else None)
    vals = [v for v in seams if v is not None]
    if len(vals) < 4:
        return 0.0
    k = max(2, len(vals) // 5)
    return abs(float(np.mean(vals[:k])) - float(np.mean(vals[-k:]))) / float(span)


def main():
    print("OBJECT PROJECTION — planes, measured (§3: exactly two, a front face and a top)\n")
    print("  %-14s %-8s %10s %10s %10s   %s" % ("class", "archetype", "symmetry",
                                                 "top-shear", "seam-tilt", "reads as"))
    rows = []
    for name, items in MATRIX:
        for arch, ids, w, h in items:
            if not all(os.path.exists(D % t) for t in ids):
                continue
            op = assemble(ids, w, h)
            s, sh = symmetry(op), top_shear(op)
            st = seam_tilt(ids, w, h)
            # seam_tilt is REPORTED but does not classify — see the docstring.
            planes = ("2 planes" if (s >= 0.90 and sh <= 0.06) else "3 planes")
            rows.append((name, arch, s, sh, st, planes))
            print("  %-14s %-8s %10.3f %10.3f %10.3f   %s" % (name, arch, s, sh, st, planes))
    print()
    for name, _ in MATRIX:
        sub = [r for r in rows if r[0] == name]
        if not sub:
            continue
        two = sum(1 for r in sub if r[5] == "2 planes")
        print("  %-14s %d of %d read as TWO planes   (symmetry %.3f, shear %.3f, seam %.3f)"
              % (name, two, len(sub), np.mean([r[2] for r in sub]),
                 np.mean([r[3] for r in sub]), np.mean([r[4] for r in sub])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
