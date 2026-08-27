#!/usr/bin/env python3
"""Guide v4 — geometry only. NOT an asset, NOT a palette, never shown to the critic.

Round 7's flip list encoded literally. Its items are almost entirely tone-discipline and
placement, both of which are executable here and nowhere else in this pipeline:

  * one light tone, reserved to rows 0-4 and appearing nowhere below row 5
  * top band >= 25 luminance above the face, seated on a 1px dark line
  * at most three courses per 32px, blocks at least 9px wide (this is also the register's
    chunk requirement arriving from the other direction)
  * alternate courses offset by a NON-half-block amount so joints stop stacking into columns
  * flat block faces with a 1px chamfer top AND bottom, so a value change describes geometry
    rather than a light source — which is §6.3 as well as the critic's note
  * the timber 4px tall, full width, INTERRUPTING the mortar course it crosses
  * pins as a 2px head with a 1px dark seat where it bites the wood
  * bright motifs at a different coordinate in every variant, and one discontinuous course

⚠ The repair has now been absent from critic verdicts for seven consecutive rounds, including
three in which it was drawn directly into the guide. This build makes it structurally
unavoidable — it interrupts a course rather than sitting on top of one — which is the last
untried way to state it. If it goes missing again the finding is about the endpoint.
"""
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "guides")
SIZE, TOP_BAND = 32, 5

V_TOP = 168            # reserved: rows 0-4 ONLY, and nothing this light appears below
V_TOP_TICK = 146
V_HARD = 34            # the 1px dark line the band is seated on
V_FACE = 104
V_FACE_HI, V_FACE_LO = 114, 92
V_CHAMFER_HI, V_CHAMFER_LO = 122, 84   # 1px top and bottom: geometry, not a light source
V_JOINT = 40
V_RUBBLE = 70
V_BAULK, V_GRAIN = 88, 100
V_UNDER = 50
V_PIN, V_SEAT = 152, 44


def build(seed):
    rng = random.Random(seed)
    im = Image.new("RGB", (SIZE, SIZE))
    px = im.load()

    def fill(x0, y0, x1, y1, v):
        for y in range(max(0, y0), min(SIZE, y1)):
            for x in range(max(0, x0), min(SIZE, x1)):
                px[x, y] = (v, v, v + 4)

    fill(0, 0, SIZE, SIZE, V_FACE)

    # Three courses at most, blocks >= 9px, alternate courses offset by a NON-half-block amount.
    body_top = TOP_BAND + 1
    n_courses = 3
    ch = (SIZE - body_top) // n_courses
    baulk_course = rng.randint(0, n_courses - 1)
    gap_course = rng.choice([c for c in range(n_courses) if c != baulk_course])
    first_cols = []

    for ci in range(n_courses):
        cy = body_top + ci * ch
        fill(0, cy, SIZE, cy + 1, V_JOINT)
        offset = -rng.choice((3, 4, 7, 8))        # never half a block
        x = offset if ci % 2 else offset - 5
        cols = []
        while x < SIZE:
            w = rng.choice((9, 11, 13))
            cols.append(x)
            base = rng.choice((V_FACE, V_FACE_HI, V_FACE_LO))
            fill(x, cy + 1, x + w, cy + ch, base)
            fill(x, cy + 1, x + w, cy + 2, V_CHAMFER_HI)          # 1px chamfer, top
            fill(x, cy + ch - 1, x + w, cy + ch, V_CHAMFER_LO)    # and bottom
            if ci == gap_course and rng.random() < 0.4:           # a discontinuous course
                fill(x, cy + 1, x + w, cy + ch, V_RUBBLE)
                for k in range(x, min(SIZE, x + w), 3):
                    fill(k, cy + 2, k + 1, cy + ch - 1, V_JOINT)
            if x > 0:
                fill(x, cy + 1, x + rng.choice((1, 2)), cy + ch, V_JOINT)
            x += w
        if ci == 0:
            first_cols = [c for c in cols if 0 < c < SIZE]

    # Top band: one reserved tone, its divisions on the first course's joints, seated on a line.
    fill(0, 0, SIZE, TOP_BAND, V_TOP)
    for cx in first_cols:
        fill(cx, 0, cx + 1, TOP_BAND, V_TOP_TICK)
    fill(0, TOP_BAND, SIZE, TOP_BAND + 1, V_HARD)

    # The repair, INTERRUPTING its course rather than lying on it.
    by = body_top + baulk_course * ch + (ch - 4) // 2
    fill(0, by - 1, SIZE, by, V_UNDER)
    fill(0, by, SIZE, by + 4, V_BAULK)
    for gy in range(by + 1, by + 3):
        fill(0, gy, SIZE, gy + 1, V_GRAIN)
    fill(0, by + 4, SIZE, by + 5, V_UNDER)
    # Pins at a different coordinate in every variant, so ten tiles lay down no lattice.
    for cx in (rng.randint(2, 9), rng.randint(18, 27)):
        fill(cx, by + 1, cx + 2, by + 3, V_PIN)
        fill(cx, by + 3, cx + 2, by + 4, V_SEAT)
    return im


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    os.makedirs(OUT, exist_ok=True)
    for i in range(n):
        build(90900 + i).save(os.path.join(OUT, "guide_%02d.png" % i))
    sheet = Image.new("RGB", (n * (SIZE * 8 + 8) + 8, SIZE * 8 + 16), (30, 30, 34))
    for i in range(n):
        sheet.paste(Image.open(os.path.join(OUT, "guide_%02d.png" % i)).resize(
            (SIZE * 8, SIZE * 8), Image.NEAREST), (8 + i * (SIZE * 8 + 8), 8))
    sheet.save(os.path.join(OUT, "guides_sheet.png"))
    print("wrote %d v4 guides -> %s" % (n, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
