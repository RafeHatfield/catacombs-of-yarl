#!/usr/bin/env python3
"""Derive guide v5 from v4: delete the chamfers, separate the materials by hue."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "make_guide_v4.py")).read()

src = src.replace('"""Guide v4 — geometry only.',
                  '"""Guide v5 — geometry AND material separation. Still not an asset, not a palette.')

# Round 8 produced THREE key-light culls. The cause was v4's 1px chamfers, taken literally from
# round 7's own flip list: light on top, dark underneath, on every course. At 32px that is
# indistinguishable from a baked directional light — a §6.3 violation the guide introduced.
src = src.replace(
    """            fill(x, cy + 1, x + w, cy + 2, V_CHAMFER_HI)          # 1px chamfer, top
            fill(x, cy + ch - 1, x + w, cy + ch, V_CHAMFER_LO)    # and bottom
""",
    """            # ⚠ v4's 1px chamfers (light top / dark bottom) are DELETED. They came straight
            # from round 7's flip list and, executed literally at 32px, produced THREE
            # key-light culls in round 8 — a §6.3 violation introduced by the guide itself.
            # Courses now separate by mortar recess and block variation alone, which is what
            # round 8's flip list asked for in their place.
""")

src = src.replace(
    """    def fill(x0, y0, x1, y1, v):
        for y in range(max(0, y0), min(SIZE, y1)):
            for x in range(max(0, x0), min(SIZE, x1)):
                px[x, y] = (v, v, v + 4)
""",
    """    # Round 8: "every tile is 4-13 values of the same grey-blue; give timber, iron and rope
    # distinct hues and value ranges from stone." The guide was monochrome, so it was arguably
    # CAUSING that. Materials now separate by hue as well as by value.
    # ⚠ Material differentiation, NOT a palette. §5.1 reserves colour authorship to the bible.
    # Nothing here proposes a game colour, the guide is never an asset and never reaches the
    # critic, `color_image` is never set, and the output's colours still come from the generator.
    TINT = {"stone": (0, 0, 6), "timber": (16, 4, -12), "iron": (-6, -2, 10)}

    def fill(x0, y0, x1, y1, v, mat="stone"):
        dr, dg, db = TINT[mat]
        c = (max(0, min(255, v + dr)), max(0, min(255, v + dg)), max(0, min(255, v + db)))
        for y in range(max(0, y0), min(SIZE, y1)):
            for x in range(max(0, x0), min(SIZE, x1)):
                px[x, y] = c
""")

for a, b in (
        ("fill(0, by - 1, SIZE, by, V_UNDER)", 'fill(0, by - 1, SIZE, by, V_UNDER, "timber")'),
        ("fill(0, by, SIZE, by + 4, V_BAULK)", 'fill(0, by, SIZE, by + 4, V_BAULK, "timber")'),
        ("fill(0, gy, SIZE, gy + 1, V_GRAIN)", 'fill(0, gy, SIZE, gy + 1, V_GRAIN, "timber")'),
        ("fill(0, by + 4, SIZE, by + 5, V_UNDER)", 'fill(0, by + 4, SIZE, by + 5, V_UNDER, "timber")'),
        ("fill(cx, by + 1, cx + 2, by + 3, V_PIN)", 'fill(cx, by + 1, cx + 2, by + 3, V_PIN, "iron")'),
        ("fill(cx, by + 3, cx + 2, by + 4, V_SEAT)", 'fill(cx, by + 3, cx + 2, by + 4, V_SEAT, "iron")')):
    assert a in src, a
    src = src.replace(a, b)

src = src.replace("build(90900 + i)", "build(110110 + i)")
open(os.path.join(HERE, "make_guide_v5.py"), "w").write(src)
print("make_guide_v5.py written")
