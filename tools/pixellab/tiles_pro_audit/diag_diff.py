#!/usr/bin/env python3
"""Why does every identical-call pair return the SAME pixdiff to six decimals?

Six different pairs of kits returned 0.307935, and so did the two-different-seeds pair. An
instrument that returns one number to everything is the `NO INSTRUMENT` signature from the
§6.4 audit — there, MCP `pro` measured a lever at 1.0000 against a noise floor of 1.0000 — and
a number like that must be explained before it is allowed to be a noise floor.

The hypothesis this file tests: the diff is counting pixels that are INVISIBLE. PNG stores an
RGB triple for fully transparent pixels too, and nothing requires two encodings of the same
image to agree about what that triple is. If the kits differ only under alpha=0, then the
fraction differing is the fraction transparent — a fixed property of each tile's silhouette,
identical for every pair, exactly as observed.

Zero cost, no network. Runs on kits already on disk.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sheet as SH  # noqa: E402
import tiles_pro as tp  # noqa: E402


def visible_pixdiff(a, b):
    """Differing pixels among those visible in EITHER image, over the same denominator as
    pixdiff. A pixel where both alphas are 0 cannot differ visibly, whatever its RGB says."""
    a, b = a.convert("RGBA"), b.convert("RGBA")
    if a.size != b.size:
        return 1.0
    n = 0
    for p, q in zip(a.getdata(), b.getdata()):
        if p[3] == 0 and q[3] == 0:
            continue
        if p != q:
            n += 1
    return n / float(a.width * a.height)


def transparent_fraction(im):
    im = im.convert("RGBA")
    n = sum(1 for p in im.getdata() if p[3] == 0)
    return n / float(im.width * im.height)


def main():
    Y = os.path.join(HERE, "yield")
    a = SH.load_kit(os.path.join(Y, "kit_A0"))
    b = SH.load_kit(os.path.join(Y, "kit_A1"))
    c = SH.load_kit(os.path.join(Y, "kit_B"))

    print("%-6s %-10s %-10s %-10s %-10s" %
          ("tile", "raw A0/A1", "visible", "transp A0", "raw A0/B"))
    tot_raw = tot_vis = tot_tr = tot_rawb = 0.0
    ks = sorted(set(a) & set(b) & set(c))
    for i in ks:
        raw = tp.pixdiff(a[i], b[i])
        vis = visible_pixdiff(a[i], b[i])
        tr = transparent_fraction(a[i])
        rawb = tp.pixdiff(a[i], c[i])
        tot_raw += raw
        tot_vis += vis
        tot_tr += tr
        tot_rawb += rawb
        if i in (0, 1, 5, 13, 31, 49, 60, 79):
            print("%-6d %-10.6f %-10.6f %-10.6f %-10.6f" % (i, raw, vis, tr, rawb))
    n = len(ks)
    print("\nmean over %d tiles:" % n)
    print("  raw pixdiff      A0/A1 = %.6f   A0/B = %.6f" % (tot_raw / n, tot_rawb / n))
    print("  VISIBLE pixdiff  A0/A1 = %.6f" % (tot_vis / n))
    print("  transparent frac A0    = %.6f" % (tot_tr / n))

    print("\nreading:")
    if abs(tot_raw / n - tot_tr / n) < 1e-6:
        print("  ⚠ raw pixdiff == transparent fraction. The diff was counting INVISIBLE "
              "pixels\n    and 0.307935 was never a noise floor — it was the mean silhouette "
              "hole size.\n    Every verdict read against it would have been meaningless.")
    if tot_vis / n == 0.0:
        print("  ✅ VISIBLE difference is exactly zero: the kits are pixel-identical where "
              "anyone\n    can see them. /create-tiles-pro IS deterministic under seed.")
    else:
        print("  VISIBLE difference is %.6f — the kits genuinely differ." % (tot_vis / n))


if __name__ == "__main__":
    main()
