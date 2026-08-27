#!/usr/bin/env python3
"""THE C-GAB EXHIBIT — the one question §13.2 routed to the human gate.

WHY THIS EXISTS
---------------
Three blind seats judged the same C-GAB capture and split 2-1 on whether it carries a keyline.
Bible §5.5 records the split as FLAGGED, UNRESOLVED BY INSTRUMENT, and §13.2 sends the deadlock
to the eye. This module builds what the eye needs and nothing more.

THE QUESTION, and it is one:

    CRACK THROUGH THE STONE, OR FRAME AROUND THE TILE?

WHAT DECIDES IT, AND WHY THE 3x3 IS THE EXHIBIT'S CENTREPIECE
-------------------------------------------------------------
The seat prompt already states the test, in its own words, and it is a test neither seat could
actually run — because every capture shows the tile *laid*, and the 32x32 PNG shows it *alone*:

    "A joint marks where one stone stops and the next begins; it runs on across the floor from
     tile to tile and the shapes it makes are the stones themselves. A keyline stops at one
     shape and rings it. If you cannot decide which you are looking at, ask: DOES THIS LINE
     CONTINUE INTO THE NEXT TILE ALONG, OR DOES IT TURN THE CORNER AND COME BACK TO WHERE IT
     STARTED?"

A 3x3 tiling answers exactly that and is the one view that does. It is built here at 1x and
magnified, with NO overlay and NO annotation, because it is the surface the answer comes from.

WHAT IS DELIBERATELY NOT DONE HERE
----------------------------------
* **No verdict, no score, no recommendation.** §13.4: the register clauses are carried eye-side
  and a proxy for them is forbidden. This module measures nothing.
* **The overlay is on its own image, never on the ones used to decide.** A magenta contour drawn
  over the tile tells the eye where to look, which is precisely the influence that must not
  touch the plain views. It is included because the disagreement is about a specific geometry
  and the gate should be able to see which geometry - but it comes AFTER, labelled.
* **Nearest-neighbour only.** Every magnification is integer and unsmoothed (§4.3).

THIS IS NOT AN APPROVAL SURFACE. §13.1 is untouched: no candidate is ever approved from a sheet,
and nothing here lands anything. The question asked is about what a construction IS, not about
whether a tile ships.
"""
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ring_instrument as RI      # noqa: E402
import near_ring as NR            # noqa: E402

TILE = os.path.join(REPO, "tools/pixellab/probe_6_4/survivors/C-GAB.png")
LIT = os.path.join(HERE, "evidence", "children_P", "CONTROL_parent_CGAB.png")
OUT = os.path.join(HERE, "exhibit_cgab")

# The four sides the dissenting seat named, verbatim from its transcript:
# "a dark rectangle runs down col 9 and col 23 from row 12 to row 20, closes along row 20 and
#  dashes across row 9".
CLAIMED = {
    "col 9, rows 12-20": [(y, 9) for y in range(12, 21)],
    "col 23, rows 12-20": [(y, 23) for y in range(12, 21)],
    "row 20, cols 9-23": [(20, x) for x in range(9, 24)],
    "row 9, cols 9-23": [(9, x) for x in range(9, 24)],
}
# TWO colours, and the distinction is the point. A first draft painted every CLAIMED cell one
# colour, which drew a closed magenta rectangle over a side that is dark in 4 pixels of 9 — the
# overlay would have asserted the very thing in dispute and led the gate straight to "frame".
# So: PRESENT means the pixel really is below the tile's median; ABSENT means the seat claimed
# contour there and the tile has none. The overlay now shows the claim AND its evidence.
PRESENT = (255, 0, 200)      # magenta - claimed, and the pixel is dark
ABSENT = (0, 230, 255)       # cyan    - claimed, and the pixel is NOT dark


def up(im, factor):
    return im.resize((im.width * factor, im.height * factor), Image.NEAREST)


def main():
    os.makedirs(OUT, exist_ok=True)
    tile = Image.open(TILE).convert("RGB")
    a = np.array(tile).astype(int)
    med = float(np.median(RI.lum(a.astype(float))))

    # 1x and magnified, plain.
    tile.save(os.path.join(OUT, "tile_1x.png"))
    up(tile, 12).save(os.path.join(OUT, "tile_12x.png"))

    # The 3x3, plain. THE view that answers the question.
    t3 = Image.new("RGB", (96, 96))
    for gy in range(3):
        for gx in range(3):
            t3.paste(tile, (gx * 32, gy * 32))
    t3.save(os.path.join(OUT, "tiled_3x3_1x.png"))
    up(t3, 6).save(os.path.join(OUT, "tiled_3x3_6x.png"))

    # The overlay, on its own image, AFTER the plain ones.
    lumv = RI.lum(a.astype(float))
    ov = np.array(tile).copy()
    for cells in CLAIMED.values():
        for y, x in cells:
            ov[y, x] = PRESENT if lumv[y, x] < med else ABSENT
    up(Image.fromarray(ov.astype("uint8")), 12).save(os.path.join(OUT, "overlay_12x.png"))

    # A 3x3 of the overlay too - so the gate can see whether the CLAIMED contour continues.
    o3 = Image.new("RGB", (96, 96))
    oi = Image.fromarray(ov.astype("uint8"))
    for gy in range(3):
        for gx in range(3):
            o3.paste(oi, (gx * 32, gy * 32))
    up(o3, 6).save(os.path.join(OUT, "overlay_3x3_6x.png"))

    # The lit in-scene capture, carried across unmodified.
    Image.open(LIT).convert("RGB").save(os.path.join(OUT, "lit_capture.png"))

    # The measured facts, stated without interpretation.
    sides = {}
    for name, cells in CLAIMED.items():
        vals = [RI.lum(a.astype(float))[y, x] for y, x in cells]
        sides[name] = dict(dark=int(sum(1 for v in vals if v < med)), of=len(cells))
    v, rings = RI.verdict(a)
    score, detail = NR.near_ring_score(a)
    facts = dict(
        tile=os.path.relpath(TILE, REPO),
        tile_sha256=hashlib.sha256(open(TILE, "rb").read()).hexdigest(),
        lit_capture=os.path.relpath(LIT, REPO),
        lit_sha256=hashlib.sha256(open(LIT, "rb").read()).hexdigest(),
        size=list(tile.size), colours=len(set(map(tuple, a.reshape(-1, 3).tolist()))),
        luminance_median=round(med, 1),
        instrument_verdict=v, instrument_findings=RI.public(rings),
        side_coverage=score, min_side_coverage_required=RI.MIN_SIDE_COVERAGE,
        best_near_ring_contour=detail,
        claimed_sides=sides,
        seats={"floor-remediation round A": "cull: none",
               "parent-rate round CP": "cull: none",
               "parent-rate round CS": "cull: keyline"},
        question="crack through the stone, or frame around the tile?",
        note=("This exhibit measures nothing and recommends nothing. Per bible §13.2 the "
              "instrument deadlock routes to the eye; per §13.1 nothing here approves anything."))
    with open(os.path.join(OUT, "facts.json"), "w") as f:
        json.dump(facts, f, indent=1)

    print("C-GAB EXHIBIT -> %s" % os.path.relpath(OUT, REPO))
    print("  tile        %s  sha %s" % (tile.size, facts["tile_sha256"][:16]))
    print("  instrument  %s   side coverage %.3f of %.2f required"
          % (v, score, RI.MIN_SIDE_COVERAGE))
    for name, s in sides.items():
        print("    %-20s dark %2d of %2d" % (name, s["dark"], s["of"]))
    print("  seats       A: none   CP: none   CS: keyline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
