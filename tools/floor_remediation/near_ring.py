#!/usr/bin/env python3
"""NEAR-RING SCORE — the highest side coverage a tile reaches WITHOUT being called a ring.

Why this file exists, and why it is not part of `ring_instrument.py`.

REPORT.md §6 tabulates "highest side coverage in the tile" for six floors and uses it to show
that the instrument's classes OVERLAP with the blind seat's: a tile the seat called a keyline
scored 0.654, BELOW two tiles it called clean (0.688, 0.791). That table was computed ad hoc and
the number it reports is not exposed by the instrument. It is needed again here, to decide which
CLEAN children go to the seat, so it is written down once instead of re-derived by hand.

WHAT IT IS. The maximum `side_coverage` over every candidate contour that satisfies EVERY ring
criterion EXCEPT criterion 1 (presence on every side). A tile the instrument calls RING scores at
or above MIN_SIDE_COVERAGE by definition; a CLEAN tile's score says how close its closest
contour came.

WHAT IT IS NOT — and this is the whole point of the separate file. **It is not a second
threshold and it renders no verdict.** REPORT §6 measured that no threshold on this number
separates the seat's classes, and ruling 3 closed the question: the instrument stands as
labelled, with its limit written down, and is not tuned. This number's only job is TRIAGE — to
pick which of the instrument's CLEAN calls are worth a human-equivalent second look. Reading a
pass or a fail off it would be exactly the proxy §13.4 forbids.

`ring_instrument.py` is imported and NOT modified. Nothing here changes a constant.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ring_instrument as RI      # noqa: E402


def near_ring_score(a):
    """(score, detail) — the highest side coverage reached by an otherwise-ring-shaped contour.

    Mirrors `RI.find_rings` candidate-for-candidate, in the same order, with criterion 1's
    rejection replaced by a record. Every other criterion is applied unchanged and by calling
    RI's own functions, so this cannot drift from the instrument it reports on.
    """
    H, W = a.shape[:2]
    best = 0.0
    detail = None
    for kind, label, mask in RI.masks_of(a):
        if not mask.any() or mask.all():
            continue
        comps = RI.components(mask)
        candidates = list(comps)
        if len(comps) > 1:
            candidates.append([p for c in comps for p in c])
        for comp in candidates:
            ys = [p[0] for p in comp]
            xs = [p[1] for p in comp]
            bbox = [min(ys), min(xs), max(ys), max(xs)]
            occ = np.zeros((H, W), dtype=bool)
            for y, x in comp:
                occ[y, x] = True
            cov, interior = RI.side_coverage(occ, bbox)
            if len(interior) < RI.MIN_INTERIOR:                              # criterion 3
                continue
            th, spread = RI.wall_thickness(occ)
            if th > RI.MAX_THICKNESS or spread > RI.MAX_THICKNESS_SPREAD:    # criterion 2
                continue
            if RI.hollowness(comp, bbox) < RI.MIN_HOLLOWNESS:                # criterion 2b
                continue
            if RI.regions_separated(occ) > RI.MAX_REGIONS_SEPARATED:         # criterion 4
                continue
            if cov > best:                                    # criterion 1 recorded, not applied
                best = cov
                detail = dict(kind=kind, level=label, side_coverage=round(cov, 3),
                              contour_px=len(comp), interior_px=len(interior),
                              wall_thickness=round(th, 2), wall_thickness_spread=round(spread, 2),
                              interior_bbox=[int(v) for v in bbox])
    return round(best, 3), detail


def main():
    """Self-check: reproduce REPORT.md §6's published table. Run with no arguments.

    The four survivor originals have published numbers. If this file does not reproduce them it
    is wrong and must not be used to triage anything.
    """
    from PIL import Image
    repo = os.path.dirname(os.path.dirname(HERE))
    surv = os.path.join(repo, "tools/pixellab/probe_6_4/survivors")
    published = {"A-VAB": 1.000, "B-KAB": 0.992, "C-GAB": 0.791, "A-HEB": 0.688}
    print("SELF-CHECK against REPORT.md §6's published table\n")
    print("  %-8s %-9s %-9s %s" % ("floor", "published", "measured", ""))
    ok = True
    for code, want in published.items():
        a = np.array(Image.open(os.path.join(surv, code + ".png")).convert("RGB")).astype(int)
        got, _ = near_ring_score(a)
        agree = abs(got - want) < 0.0015
        ok = ok and agree
        print("  %-8s %-9.3f %-9.3f %s" % (code, want, got, "OK" if agree else "MISMATCH"))
    print("\n  %s" % ("SELF-CHECK: PASS" if ok else "SELF-CHECK: FAIL - do not use this file"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
