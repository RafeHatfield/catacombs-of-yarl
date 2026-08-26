#!/usr/bin/env python3
"""Guide v3 — geometry only, still. NOT an asset, NOT a palette, never shown to the critic.

WHAT ROUND 6 MEASURED, AND WHY IT MATTERS MORE THAN ROUND 6'S VERDICTS
----------------------------------------------------------------------
At init_image_strength 500 and 800 the generator returned **the guide, essentially unchanged**:
flat grey rectangles with no stone material on them at all. Set beside round 5's 300 and 150,
the shape of the parameter is now clear and it is not the shape that was hoped for:

    150  generator dominates — geometry is overridden, landmarks return
    300  the most balanced point observed
    500  guide dominates
    800  the output is the guide

**`init_image` is a BLEND control, not a composition control.** It does not let you pin the
geometry and generate the material; it interpolates between your image and a generated one. At
the strength where geometry holds, there is no generation left to supply material.

That has a consequence worth stating before it is designed around: **a candidate produced at
500 or 800 is not a generated asset, it is programmer-art laundered through an API.** Had any
of them passed the critic, the pass would have been worthless. They did not, which is a point
in the critic's favour.

So v3 does two things at once. It encodes round 6's structural flip items — which are pixel
surgery, and the guide is the one place in this pipeline where pixel surgery is executable —
and it carries intra-block value variation so that at a MODERATE strength the guide reads as
stone rather than as rectangles, leaving the generator something to work with rather than
something to overwrite.

If this still fails, the honest reading is not that the guide was wrong. It is that the useful
operating point does not exist on this endpoint.
"""
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "guides")
SIZE = 32
TOP_BAND = 4
BAULK_TOP, BAULK_H = 18, 6

V_TOP, V_TOP_TICK = 152, 130
V_LIP = 126                    # r6: a 1px lip, darker than top and LIGHTER than face — not black
V_FACE, V_FACE_HI, V_FACE_LO = 106, 118, 94
V_ALT = 128
V_JOINT = 40
V_SPALL = 138                  # pale unweathered core where a face has spalled
V_BAULK, V_GRAIN, V_GRAIN2 = 84, 96, 72   # timber: lighter than the joints, so it is not a gap
V_UNDER = 52
V_PIN, V_SHANK, V_MUSH = 176, 150, 190


def build(seed):
    rng = random.Random(seed)
    im = Image.new("RGB", (SIZE, SIZE))
    px = im.load()

    def fill(x0, y0, x1, y1, v):
        for y in range(max(0, y0), min(SIZE, y1)):
            for x in range(max(0, x0), min(SIZE, x1)):
                px[x, y] = (v, v, v + 4)

    fill(0, 0, SIZE, SIZE, V_FACE)

    # ---- courses first, so the top band can be aligned TO them (r6 item 1) ----------------
    courses, joint_cols = [], []
    y = TOP_BAND + 2
    course = 0
    while y < SIZE:
        h = rng.choice((5, 6, 7))
        cols, x = [], -rng.randint(2, 6) - (0 if course % 2 else 5)
        while x < SIZE:
            w = rng.choice((7, 9, 11, 13))
            # r6: wrapped stones at the seam must be at least 5px, not 2px stubs
            if 0 < SIZE - x < 5:
                w = max(w, 6)
            cols.append(x)
            x += w
        courses.append((y, h, cols))
        if course == 0:
            joint_cols = [c for c in cols if 0 < c < SIZE]
        y += h
        course += 1

    for ci, (cy, h, cols) in enumerate(courses):
        fill(0, cy - 1, SIZE, cy, V_JOINT)
        no_joint_run = rng.randint(0, SIZE - 7) if rng.random() < 0.5 else None
        for k, cx in enumerate(cols):
            nxt = cols[k + 1] if k + 1 < len(cols) else SIZE
            drop = 1 if (rng.random() < 0.12) else 0          # r6: a stone out of course
            base = rng.choice((V_FACE, V_FACE_HI, V_FACE_LO, V_ALT))
            fill(cx, cy + drop, nxt, cy + h + drop, base)
            # intra-block variation, darker along the lower edge where dust collects
            fill(cx, cy + h + drop - 2, nxt, cy + h + drop, max(0, base - 12))
            if rng.random() < 0.30:                            # r6: spalled patch
                sx, sy = cx + rng.randint(1, 3), cy + drop + 1
                fill(sx, sy, sx + 4, sy + 3, V_SPALL)
            if rng.random() < 0.25:                            # r6: 2x2 corner knocked off
                fill(cx, cy + drop, cx + 2, cy + drop + 2, V_JOINT)
            if cx > 0:
                # r6: vary joint width — 2px settled, 0px butted, and one run with none at all
                if no_joint_run is not None and no_joint_run <= cx <= no_joint_run + 6:
                    pass
                else:
                    fill(cx, cy + drop, cx + rng.choice((1, 1, 2)), cy + h + drop, V_JOINT)

    # ---- top band, divisions aligned to the first course's joints (r6 item 1) -------------
    fill(0, 0, SIZE, TOP_BAND, V_TOP)
    for cx in joint_cols:
        fill(cx, 0, cx + 1, TOP_BAND, V_TOP_TICK)
    fill(0, TOP_BAND, SIZE, TOP_BAND + 1, V_LIP)               # r6 item 2: a lip, not a black line

    # ---- the repair: timber, lighter than the joints so it cannot read as a gap (r6 item 5)
    fill(0, BAULK_TOP, SIZE, BAULK_TOP + BAULK_H, V_BAULK)
    for gy in range(BAULK_TOP + 1, BAULK_TOP + BAULK_H - 1, 2):
        fill(0, gy, SIZE, gy + 1, V_GRAIN if (gy % 4) else V_GRAIN2)
    fill(0, BAULK_TOP + BAULK_H, SIZE, BAULK_TOP + BAULK_H + 1, V_UNDER)

    # r6 items 4 + 8: named fixings — struck head, shank into the joint, mushroomed pixel —
    # at different sizes and off a shared row, so ten tiles do not lay down a lattice of dots.
    for cx, hw in ((rng.randint(3, 8), 3), (rng.randint(19, 25), rng.choice((2, 4)))):
        oy = BAULK_TOP + rng.choice((1, 2))
        fill(cx, oy, cx + hw, oy + 2, V_PIN)
        fill(cx + 1, oy + 2, cx + 2, BAULK_TOP + BAULK_H + 1, V_SHANK)
        px[min(SIZE - 1, cx + hw - 1), oy] = (V_MUSH, V_MUSH, V_MUSH + 4)
    return im


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    os.makedirs(OUT, exist_ok=True)
    for i in range(n):
        build(70700 + i).save(os.path.join(OUT, "guide_%02d.png" % i))
    sheet = Image.new("RGB", (n * (SIZE * 8 + 8) + 8, SIZE * 8 + 16), (30, 30, 34))
    for i in range(n):
        sheet.paste(Image.open(os.path.join(OUT, "guide_%02d.png" % i)).resize(
            (SIZE * 8, SIZE * 8), Image.NEAREST), (8 + i * (SIZE * 8 + 8), 8))
    sheet.save(os.path.join(OUT, "guides_sheet.png"))
    print("wrote %d v3 guides -> %s" % (n, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
