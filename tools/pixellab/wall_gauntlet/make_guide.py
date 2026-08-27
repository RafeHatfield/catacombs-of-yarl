#!/usr/bin/env python3
"""A structural under-drawing for `init_image`. Geometry only — NOT an asset, NOT a palette.

WHY THIS EXISTS
---------------
Four rounds and 40 generations produced 0 passes, and the critic's flip lists converged on two
demands that never once appeared in output:

  * a 3-4px TOP-SURFACE BAND along the top edge (every round put its band along the bottom)
  * a REPAIR at readable scale — a baulk across the width with driven pins

Both are requests to put a specific element at a specific PLACE in a 32x32 frame, and by round
4 the flip lists had become pixel surgery — "shift the right-hand blocks down two rows",
"repaint pixel (5,23)". A text prompt cannot aim that precisely, and four differently-worded
attempts is enough evidence to stop trying.

`init_image` is a documented parameter of the FROZEN surface, so reaching for it is a
parameter-side lever, not a surface switch. The prompt keeps supplying material, register and
wear; the guide supplies only where things sit.

WHAT THIS IS NOT
----------------
* **Not a palette.** Neutral greys chosen for value separation only. §5 forbids this probe
  creating a palette and nothing here proposes colours for the game — the output's colours come
  from the generator, and `color_image` is never set.
* **Not an asset, and not a candidate.** It is never submitted to the critic and can never land.
* **Not the same claim as before.** If guided generation works where text alone did not, the
  finding is NOT "text-to-image produces architectural surfaces". It is "text-to-image does not,
  and guided generation does" — a materially different pipeline, and it must be reported as one.
"""
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "guides")

SIZE = 32
TOP_BAND = 4          # rows 0-3: the wall's upper surface
BAULK_TOP, BAULK_H = 17, 6

V_TOP = 150           # top surface — lightest
V_TOP_TICK = 128      # perpendicular coursing ON the top band, so it reads as a SURFACE
V_FACE = 104          # block face
V_FACE_ALT = 116      # a block that sits a value off its neighbours
V_JOINT = 38          # mortar, ~a third of face value per the critic's note
V_HARD = 22           # the hard dark row where top surface meets front face
V_BAULK = 62          # timber — pushed well clear of every stone value so it cannot be
                      # mistaken for another course, which is how r5 lost it
V_BAULK_GRAIN = 74    # a second timber value: end grain / face break
V_BAULK_UNDER = 30    # the under-edge where it stands proud
V_PIN = 178           # driven pin head
V_PIN_BRUISE = 48     # spalled stone around the pin


def build(seed):
    rng = random.Random(seed)
    im = Image.new("RGB", (SIZE, SIZE))
    px = im.load()

    def fill(x0, y0, x1, y1, v):
        for y in range(max(0, y0), min(SIZE, y1)):
            for x in range(max(0, x0), min(SIZE, x1)):
                px[x, y] = (v, v, v + 4)

    fill(0, 0, SIZE, SIZE, V_FACE)

    # --- top surface: a SURFACE, not a value. The critic's r5 note is explicit that a flat
    # lighter band reads as "no thickness at all", so the band gets its own coursing running
    # perpendicular to the face, and a hard dark row where it meets the front.
    fill(0, 0, SIZE, TOP_BAND, V_TOP)
    tx = -rng.randint(0, 5)
    while tx < SIZE:
        fill(tx, 0, tx + 1, TOP_BAND, V_TOP_TICK)
        tx += rng.choice((6, 8, 10))
    fill(0, TOP_BAND, SIZE, TOP_BAND + 1, V_HARD)

    # --- running bond: courses offset by about half a block, so no vertical joint runs
    # through two courses (the critic's r5 item on r05_07's lattice).
    y = TOP_BAND + 1
    course = 0
    while y < SIZE:
        h = rng.choice((5, 6, 7))
        fill(0, y, SIZE, y + 1, V_JOINT)
        w0 = rng.choice((9, 11, 13))
        x = -(w0 // 2) - (0 if course % 2 else w0 // 2) - rng.randint(0, 3)
        while x < SIZE:
            w = rng.choice((7, 9, 11, 13))
            if rng.random() < 0.25:
                fill(x, y + 1, x + w, y + h, V_FACE_ALT)
            if x > 0:
                fill(x, y + 1, x + 1, y + h, V_JOINT)
            x += w
        y += h
        course += 1

    # --- the repair. r5 drew this into the guide and the generator painted over it, so the
    # timber is pushed to a value no stone in the guide uses, given a second grain value so it
    # is not one flat bar, and the pins are enlarged with bruised stone under them.
    fill(0, BAULK_TOP, SIZE, BAULK_TOP + BAULK_H, V_BAULK)
    gx = -rng.randint(0, 4)
    while gx < SIZE:
        fill(gx, BAULK_TOP + 1, gx + 1, BAULK_TOP + BAULK_H - 1, V_BAULK_GRAIN)
        gx += rng.choice((7, 9, 11))
    fill(0, BAULK_TOP - 1, SIZE, BAULK_TOP, V_BAULK_UNDER)
    fill(0, BAULK_TOP + BAULK_H, SIZE, BAULK_TOP + BAULK_H + 1, V_BAULK_UNDER)
    for cx in (rng.randint(3, 9), rng.randint(20, 26)):
        fill(cx - 1, BAULK_TOP + 1, cx + 3, BAULK_TOP + BAULK_H - 1, V_PIN_BRUISE)
        fill(cx, BAULK_TOP + 1, cx + 3, BAULK_TOP + 4, V_PIN)
    return im


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    os.makedirs(OUT, exist_ok=True)
    for i in range(n):
        p = os.path.join(OUT, "guide_%02d.png" % i)
        build(50500 + i).save(p)
    # A x8 sheet so the guides are inspectable as what they are: geometry, not art.
    sheet = Image.new("RGB", (n * (SIZE * 8 + 8) + 8, SIZE * 8 + 16), (30, 30, 34))
    for i in range(n):
        g = Image.open(os.path.join(OUT, "guide_%02d.png" % i)).resize(
            (SIZE * 8, SIZE * 8), Image.NEAREST)
        sheet.paste(g, (8 + i * (SIZE * 8 + 8), 8))
    sheet.save(os.path.join(OUT, "guides_sheet.png"))
    print("wrote %d guides -> %s" % (n, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
