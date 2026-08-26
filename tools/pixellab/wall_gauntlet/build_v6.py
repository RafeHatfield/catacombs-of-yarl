#!/usr/bin/env python3
"""Guide v6 — vary per tile, so ten guides stop laying down a lattice.

Round 9's first flip item is the guide's own fault and it is worth naming as such: "every tile
puts its dark division lines at exactly y=5, y=14 and y=22, so a tiled wall bands into fixed
horizontal stripes." v4/v5 computed course height as a constant division of the canvas, so
every guide in the set shared its joint rows. Ten tiles built from that guide cannot help
producing a lattice.

v6 varies course COUNT and HEIGHTS per tile, floats the baulk to a different height per tile,
and adds a fixing that visibly crosses a joint — round 9's third item, and the ninth
consecutive round in which the critic has reported no fastening in the set.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "make_guide_v5.py")).read()

src = src.replace('"""Guide v5 — geometry AND material separation. Still not an asset, not a palette.',
                  '"""Guide v6 — per-tile variation. Still geometry only, still not an asset or a palette.')

old = """    body_top = TOP_BAND + 1
    n_courses = 3
    ch = (SIZE - body_top) // n_courses
    baulk_course = rng.randint(0, n_courses - 1)
    gap_course = rng.choice([c for c in range(n_courses) if c != baulk_course])
    first_cols = []

    for ci in range(n_courses):
        cy = body_top + ci * ch
"""
new = """    body_top = TOP_BAND + 1
    # Round 9: a fixed course height put every tile's joints on the same rows and banded the
    # wall into stripes. Course count and heights now vary per tile, so a set of guides shares
    # no joint row and the 32px rhythm has nothing to lock onto.
    n_courses = rng.choice((2, 3, 3, 4))
    span = SIZE - body_top
    heights = []
    left = span
    for k in range(n_courses):
        h = left // (n_courses - k) + rng.choice((-2, -1, 0, 1, 2))
        h = max(6, min(left - (n_courses - k - 1) * 6, h)) if k < n_courses - 1 else left
        heights.append(h)
        left -= h
    tops = []
    acc = body_top
    for h in heights:
        tops.append(acc)
        acc += h
    baulk_course = rng.randint(0, n_courses - 1)
    gap_course = rng.choice([c for c in range(n_courses) if c != baulk_course])
    first_cols = []

    for ci in range(n_courses):
        cy = tops[ci]
        ch = heights[ci]
"""
assert old in src
src = src.replace(old, new)

# the baulk floats within its course rather than sitting at a computed constant
old_b = "    by = body_top + baulk_course * ch + (ch - 4) // 2"
new_b = ("    bh = heights[baulk_course]\n"
         "    by = tops[baulk_course] + rng.randint(1, max(1, bh - 5))")
assert old_b in src
src = src.replace(old_b, new_b)

# round 9 item 3: a fixing that visibly CROSSES a joint, proud rim and darker seat
old_p = """    for cx in (rng.randint(2, 9), rng.randint(18, 27)):
        fill(cx, by + 1, cx + 2, by + 3, V_PIN, "iron")
        fill(cx, by + 3, cx + 2, by + 4, V_SEAT, "iron")
    return im"""
new_p = """    for cx in (rng.randint(2, 9), rng.randint(18, 27)):
        fill(cx, by + 1, cx + 2, by + 3, V_PIN, "iron")
        fill(cx, by + 3, cx + 2, by + 4, V_SEAT, "iron")

    # Round 9 item 3, and the ninth round running in which the critic reports nothing fastened:
    # a pin driven through a COURSE JOINT rather than into a block face, so the fixing visibly
    # crosses the thing it is holding together.
    jx = rng.randint(6, SIZE - 8)
    jy = tops[gap_course]
    fill(jx - 1, jy - 2, jx + 3, jy + 3, V_SEAT, "iron")
    fill(jx, jy - 1, jx + 2, jy + 2, V_PIN, "iron")
    return im"""
assert old_p in src
src = src.replace(old_p, new_p)
src = src.replace("build(110110 + i)", "build(130130 + i)")

open(os.path.join(HERE, "make_guide_v6.py"), "w").write(src)
print("make_guide_v6.py written")
