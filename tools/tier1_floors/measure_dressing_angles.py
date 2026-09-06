#!/usr/bin/env python3
"""THE ANGLE CENSUS — how many directions the dressing actually draws, over a laid field.

A BUILDER'S TOOL. It gates nothing (LOOP-PROCESS §1.2, bible §13.4): the verdict on the hatch is
the frame critic's, and this exists so the aim between rounds is not a guess.

WHAT IT ANSWERS. The floor's last round was culled on the dressing with one sentence:

    "vary the 45 degree hatch; same angle and spacing on a dozen slabs"

That is section 8.3's motif trap arriving through the ANGLE rather than through the position.
Section 8.3.1 is written about a treatment at a constant POSITION inside a tile; the same
arithmetic runs one axis over. So the quantity is: over the stones a field actually lays, how
many distinct directions does the dressing draw, and what share of them sit on the modal one.

MEASURED ON THE STONES THE FIELD LAYS, not on the table. A table of twelve directions is not
evidence -- section 8.3.3's own words about family counts, applied here. `compose_ashlar` records
each dressed stone's chosen direction through `DIR_CENSUS`, so the census counts draws.

SECTION 13.5 -- THE POSITIVE CONTROL IS BUILT IN AND RUNS EVERY TIME. `--control` re-runs the same
field with the direction table the cull was made against, and the census must report the defect it
was written to find. A run whose control comes back clean prints REFUSING and exits non-zero: an
instrument that cannot fail has not passed.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_ashlar as CA        # noqa: E402
import field_ashlar as FA          # noqa: E402

# The table the cull was made against, kept here as the control and nowhere else.
CULLED_DIRS = ((1, 0), (0, 1), (1, 1), (1, -1))


def angle(d):
    """The UNDIRECTED angle of a run, in degrees over [0, 180). A groove has no arrowhead: a
    stone dressed at 45 and one dressed at 225 draw the same hatch, and counting them as two
    directions would flatter the table by a factor of two."""
    a = math.degrees(math.atan2(d[1], d[0])) % 180.0
    return round(a, 1)


def census(w, h, seed, mat, dirs):
    """Lay the field once with `dirs` in the table and count what the stones drew."""
    was = CA.MARK_DIRS
    CA.MARK_DIRS = dirs
    CA.DIR_CENSUS = []
    try:
        FA.assemble(w, h, seed, mat, None)
        drawn = list(CA.DIR_CENSUS)
    finally:
        CA.MARK_DIRS = was
        CA.DIR_CENSUS = None

    hist = {}
    for d in drawn:
        hist[angle(d)] = hist.get(angle(d), 0) + 1
    total = sum(hist.values())
    modal = max(hist.values()) / total if total else 1.0
    return dict(runs=total, distinct=len(hist), modal_share=modal,
                at_45=(hist.get(45.0, 0) + hist.get(135.0, 0)) / total if total else 0.0,
                hist={k: v for k, v in sorted(hist.items())})


def line(tag, c):
    print("  %-9s runs=%-6d distinct angles=%-3d modal share=%.3f  at 45 deg=%.3f"
          % (tag, c["runs"], c["distinct"], c["modal_share"], c["at_45"]))
    print("            %s" % json.dumps(c["hist"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=16)
    ap.add_argument("--h", type=int, default=16)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--json-out")
    a = ap.parse_args()

    mat = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))["material"]
    print("DRESSING ANGLE CENSUS -- %dx%d cells, seed %d\n" % (a.w, a.h, a.seed))

    ctrl = census(a.w, a.h, a.seed, mat, CULLED_DIRS)
    live = census(a.w, a.h, a.seed, mat, CA.MARK_DIRS)
    line("control", ctrl)
    line("live", live)

    # THE CONTROL MUST SHOW THE DEFECT. Half the culled table's entries are the same 45 degrees,
    # so a table that is working reports a heavy 45 and few angles. If it does not, the census is
    # not counting what it says it counts and its reading of the live family means nothing.
    print()
    if not (ctrl["distinct"] <= 4 and ctrl["at_45"] > 0.35):
        print("REFUSING: the control did not show the defect it was built from "
              "(distinct=%d, at 45 deg=%.3f). Fix the instrument before reading the family."
              % (ctrl["distinct"], ctrl["at_45"]))
        sys.exit(2)
    print("CONTROL FIRES: the culled table reports %d angles with %.1f%% of runs at 45 deg."
          % (ctrl["distinct"], 100 * ctrl["at_45"]))
    print("LIVE:          %d angles, %.1f%% at 45 deg, modal angle holds %.1f%%."
          % (live["distinct"], 100 * live["at_45"], 100 * live["modal_share"]))

    if a.json_out:
        json.dump(dict(control=ctrl, live=live), open(a.json_out, "w"), indent=1)
        print("wrote %s" % a.json_out)
