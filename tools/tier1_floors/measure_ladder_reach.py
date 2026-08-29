#!/usr/bin/env python3
"""DOES THE PALETTE REACH? — one instrument for two sessions, because it is one shortfall.

The floor's ladder was derived from the floor's donors, and it stops at 75.02. Three separate
things want to sit below that line and cannot, and each was diagnosed on its own before anyone
noticed they were the same fact:

    THE SHELTERED JOINT   the bond authors a joint at 0.42 x its stone — about 48 — and the
                          quantiser clamps every one of them to 75.02. Gate two's verdict, *"all
                          the gaps look standardized,"* is that clamp stated in words: they are
                          not the wrong darkness, they are all EXACTLY the same darkness, because
                          they are all pinned against the bottom of the ladder.
    THE JOINT LEVER       whose whole travel is therefore measured from a floor it did not choose,
                          which is what caps it below §13.8's perceptual floor.
    THE WALL FACE         §6.5 puts it at 0.50-0.60 x the floor. Both ends land under 75.02, so a
                          wall face cannot be authored on this palette at all.

None of the three is a tuning problem and none is fixable in its own session. They are one
missing pair of rungs, and this file measures whether adding them serves all three at once.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_ashlar as CA      # noqa: E402
import compose_family as CF      # noqa: E402
import field_ashlar as FA        # noqa: E402
import field_laws as FL          # noqa: E402

FLOOR = 0.144      # §13.8, in Weber contrast
N = 16             # see the anchor note in main(): 12 and 16 must agree, and only one statistic does


def snap(v, ladder):
    return min(ladder, key=lambda r: abs(r - v))


def reaches(v, ladder, tol=0.5):
    """A value REACHES the ladder when a rung sits within half a step of it — i.e. it is not
    being clamped by the ladder's own end. Landing on the terminal rung from outside is a clamp,
    not a fit, and that distinction is the entire finding."""
    step = ladder[1] - ladder[0]
    r = snap(v, ladder)
    return abs(r - v) <= step * tol and not (v < ladder[0] - step * tol)


def audit(ladder, mat, jf, jtravel_face, anchor, label):
    step = ladder[1] - ladder[0]
    joint_want = 0.42 * mat["lum_median"]
    rows = [
        ("floor's sheltered joint", joint_want),
        ("§6.5 wall top   1.11x", 1.11 * anchor),
        ("§6.5 floor      1.00x", 1.00 * anchor),
        ("§6.5 wall face  0.60x", 0.60 * anchor),
        ("§6.5 wall face  0.50x", 0.50 * anchor),
    ]
    print("\n%s" % label)
    print("  ladder: %s" % " ".join("%.1f" % r for r in ladder))
    print("  %-26s %9s %9s   %s" % ("what wants a rung", "value", "nearest", ""))
    ok = True
    for nm, v in rows:
        r = snap(v, ladder)
        good = reaches(v, ladder)
        ok = ok and good
        print("  %-26s %9.2f %9.2f   %s" % (nm, v, r, "" if good else "CLAMPED — no rung reaches it"))

    # The joint lever's ceiling: every trodden joint filled level with its stones, every sheltered
    # one left at the deepest rung the ladder actually offers.
    bottom = snap(joint_want, ladder)
    travel = jtravel_face - bottom
    shift = jf * travel
    w = shift / mat["lum_median"]
    print()
    print("  THE JOINT LEVER'S CEILING ON THIS LADDER")
    print("    sheltered joint sits at   %6.2f" % bottom)
    print("    filled level with stone   %6.2f" % jtravel_face)
    print("    travel x %.2f%% coverage   %6.2f units of tile mean" % (jf * 100, shift))
    print("    Weber contrast            %6.4f   floor %.4f   %s"
          % (w, FLOOR, "ABOVE" if w >= FLOOR else "BELOW (%.2fx short)" % (FLOOR / w)))
    return dict(label=label, ladder=[round(r, 3) for r in ladder], step=round(step, 3),
                all_reached=ok, joint_ceiling_weber=round(w, 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strip", type=int, default=2,
                    help="rungs to take OFF the bottom, for the control")
    a = ap.parse_args()

    man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))
    mat = man["material"]
    ladder = list(mat["ladder"])
    step = ladder[1] - ladder[0]

    # Measured, not assumed: joint coverage and the value of the stone a joint is filled up to.
    img, joints, _, _, _ = FA.assemble(N, N, 1337, mat, None, traffic=None)
    # De-tinted, so the numbers are in the ladder's own units and can be compared to its rungs.
    L = np.asarray(img).astype(float)[..., 0] / mat["tint"][0]
    jf = float(joints.mean())
    face = float(np.median(L[~joints]))

    # THE ANCHOR the wall session must use, and it is a MEAN, for two independent reasons.
    #
    # BECAUSE §6.5 SEPARATES PLANES. The floor's value is the floor AS SEEN, and its median is
    # identical to the median stone face — the joints are 21.86% of the area and a median simply
    # steps over them. Ratios taken against that would be ratios against a floor with no joints
    # in it, which is not the floor anyone looks at.
    #
    # BECAUSE THE MEDIAN OF A QUANTISED SURFACE IS NOT STABLE. On a seven-rung ladder the median
    # IS a rung, and it jumps a whole rung when the 50th percentile crosses over. Measured on the
    # same floor at two field sizes:
    #
    #     field   median      mean
    #     12x12   113.85     107.30
    #     16x16   100.86     105.91      <- the median moved 13.0 units, a full rung, 12%
    #
    # The 100.86 that opened the wall session was that artefact, not a moved floor. The mean is
    # stable to 1.3% across the same pair, and it is what a plane's apparent lightness is.
    anchor = float(L.mean())
    m12 = np.asarray(FA.assemble(12, 12, 1337, mat, None)[0]).astype(float)[..., 0] / mat["tint"][0]

    print("MEASURED ON THE LANDED FLOOR")
    print("  joint coverage            %6.2f%%" % (jf * 100))
    print("  median stone face         %6.2f" % face)
    print("  median of the whole floor %6.2f   <- steps over the joints AND moves with field"
          % float(np.median(L)))
    print("                                      size (%.2f at 12x12). NOT the anchor."
          % float(np.median(m12)))
    print("  MEAN of the whole floor   %6.2f   <- the anchor §6.5's ratios take" % anchor)
    print("                                      (%.2f at 12x12 — stable to %.1f%%)"
          % (float(m12.mean()), 100 * abs(m12.mean() - anchor) / anchor))
    print("  the anchor §6.5 was written against  114.50")
    print("  one rung                  %6.2f" % step)

    now = audit(ladder, mat, jf, face, anchor, "AS SHIPPED — %d rungs" % len(ladder))

    # THE CONTROL RUNS DOWNWARD, deliberately. While the ladder was short, the honest control was
    # to add the missing rungs and watch the clamps clear. Now that it reaches, that control would
    # pass twice and prove nothing — so the control is the ladder the ruling replaced: take the
    # two rungs back off and the instrument must go red. A check that cannot fail is not a check
    # (LOOP-PROCESS §4, bible §13.5), and a check whose control stops failing has quietly become
    # one.
    ctrl = audit(ladder[a.strip:], mat, jf, face, anchor,
                 "THE CONTROL — the %d bottom rungs taken back off" % a.strip)

    print()
    if not now["all_reached"]:
        print("  THE SHIPPED LADDER CLAMPS. Rows marked above have no rung within half a step;")
        print("  whatever wants them is being pinned against the end of the palette.")
        ok = False
    elif ctrl["all_reached"]:
        print("  CONTROL PASSED TOO: stripping %d rungs changed nothing, so this instrument has"
              % a.strip)
        print("  not shown it can fail and its pass does not count. (LOOP-PROCESS §4)")
        ok = False
    else:
        print("  REACHES, AND THE CONTROL FAILS: every row lands on the shipped ladder, and")
        print("  taking the bottom %d rungs back off puts them back against the clamp." % a.strip)
        print("  The joint lever's ceiling: %.4f shipped vs %.4f stripped, floor %.4f."
              % (now["joint_ceiling_weber"], ctrl["joint_ceiling_weber"], FLOOR))
        ok = True

    out = dict(commit=FL.git_commit(), anchor=round(anchor, 3), joint_coverage=round(jf, 4),
               floor=FLOOR, shipped=now, stripped_control=ctrl, decisive=ok)
    p = os.path.join(HERE, "evidence", "LADDER-REACH.json")
    json.dump(out, open(p, "w"), indent=1)
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
