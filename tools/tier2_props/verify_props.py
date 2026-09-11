#!/usr/bin/env python3
"""EVERY DECLARED PROP MUST DRAW, AND EVERY ONE MUST BE LIT.

The tier-two acceptance criterion routed here from the wall lane has two halves, and only one of
them is about the art:

    "the props session PASSES only if orc work is visible AS STANDING OBJECTS IN THE LIT RADIUS
     of the walked scene."

⚠ THIS EXISTS BECAUSE I MADE THE SAME MISTAKE TWICE IN ONE RUN. The first props scene put a second
marker at 5.4 tiles to test §8.3.1's repetition; it measured 17.97 against §13.8's floor of 36.7
and could not answer the question it was placed for. The next scene put the whole barricade family
at 4.0–4.5 tiles; they measured 22–32 and could not either. Both times the placement looked
obviously fine and both times it was dark.

A prop in the dark answers nothing, and remembering that is not a mechanism. So this refuses the
scene, and it refuses BEFORE a panel is seated rather than after five seats have ranked a frame
whose subject is invisible.

⚠ IT DOES NOT CHECK THE OTHER HALF, AND THIS PARAGRAPH USED TO SAY IT DID. It claimed drawing
was "checked against a propless control"; `main` measures luminance and nothing else, and a review
found the claim sitting directly on top of a real gap. The gap is worth keeping written down: an
earlier probe measured "pixels changed at the prop's cell" and read it as the sprite drawing, when
it was `MarkPropCell` repainting the floor underneath. So a drawing check is OWED and unbuilt, and
the headline above is an aspiration for the second half rather than a description of it.

WHAT IT DOES MEASURE: delivered luminance at every cell of every prop's footprint, reporting the
WORST cell. Anchor-only sampling was right while every prop was 1x1 and became wrong the moment
§12.2 allowed a 1x2 — the far cell of a tall prop is always the darker one.

Usage: python3 tools/tier2_props/verify_props.py [frame.png]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SPEC = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes/tier1_props_review.json")
FRAME = os.path.join(REPO, "tools/tier1_floors/evidence/combined.png")

PERCEPTUAL_FLOOR = 36.7          # §13.8's 0.1440 on a 0..255 scale
GRID_X0, GRID_Y0, PITCH = 23, -190.5, 64


def lum(p):
    a = np.asarray(Image.open(p).convert("RGB"), dtype=float)
    return 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]


def cell(tx, ty):
    return int(round(GRID_X0 + PITCH * tx)), int(round(GRID_Y0 + PITCH * ty))


def main(frame=FRAME):
    L = lum(frame)
    spec = json.load(open(SPEC))
    px, py = spec["player"]["x"], spec["player"]["y"]
    props = spec.get("props", [])
    if not props:
        print("no props declared — nothing to verify")
        return 0

    print("THE ROUTED CRITERION: orc work visible as standing objects IN THE LIT RADIUS")
    print("  station (%d,%d), §13.8's perceptual floor is %.1f\n" % (px, py, PERCEPTUAL_FLOOR))
    # ⚠ EVERY CELL OF THE FOOTPRINT, AND THE WORST ONE IS THE ANSWER — §12.2.
    #
    # This sampled the ANCHOR cell alone, which was right while every prop was 1x1 and became
    # wrong the moment §12.2 let a standing stone be two cells tall. The light falls off radially
    # from the station, so the far cell of a tall prop is always the darker one — and on the
    # exemplar the clause was written for, the marker's dressed face is IN that far cell. A 2x2
    # went three-quarters unchecked.
    #
    # Reporting the mean of the whole footprint would be worse than the anchor: it lets a bright
    # near cell carry a dark far one over the floor. The rule is the floor family's own — report
    # the WORST cell, every band — so the footprint passes only if its darkest cell passes.
    print("  tile    cell      footprint   worst cell   worst mean   lit?    tiles from station")
    dark = []
    for p in props:
        pw, ph = int(p.get("w", 1)), int(p.get("h", 1))
        worst, worst_cell = None, None
        for dy in range(ph):
            for dx in range(pw):
                sx, sy = cell(p["x"] + dx, p["y"] + dy)
                reg = L[max(0, sy):sy + PITCH, max(0, sx):sx + PITCH]
                if reg.size == 0:
                    continue
                m = float(reg.mean())
                if worst is None or m < worst:
                    worst, worst_cell = m, (p["x"] + dx, p["y"] + dy)
        if worst is None:
            worst, worst_cell = 0.0, (p["x"], p["y"])
        d = ((worst_cell[0] - px) ** 2 + (worst_cell[1] - py) ** 2) ** 0.5
        ok = worst > PERCEPTUAL_FLOOR
        if not ok:
            dark.append((p["tileId"], worst_cell[0], worst_cell[1], worst, d))
        print("  %-6d  (%2d,%2d)   %dx%-7d  (%2d,%2d)     %7.2f      %-5s   %.1f"
              % (p["tileId"], p["x"], p["y"], pw, ph,
                 worst_cell[0], worst_cell[1], worst, "LIT" if ok else "DARK", d))

    if dark:
        print("\n*** REFUSED — %d prop(s) are below the perceptual floor:" % len(dark))
        for tid, x, y, m, d in dark:
            print("      tile %d at (%d,%d): %.2f at %.1f tiles, floor is %.1f"
                  % (tid, x, y, m, d, PERCEPTUAL_FLOOR))
        print("    A prop in the dark cannot answer the criterion it was placed for. Move it")
        print("    inside the lit radius, or remove it — do NOT lower the floor.")
        return 1

    print("\nEVERY DECLARED PROP IS LIT. %d props, nearest %.1f tiles, furthest %.1f."
          % (len(props),
             min(((p["x"] - px) ** 2 + (p["y"] - py) ** 2) ** 0.5 for p in props),
             max(((p["x"] - px) ** 2 + (p["y"] - py) ** 2) ** 0.5 for p in props)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else FRAME))
