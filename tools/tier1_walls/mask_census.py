#!/usr/bin/env python3
"""Which wall segments does a scene actually contain?

Replicates DungeonRenderer.ComputeWallMasks plus the 7/11->3, 13/14->12 collapse against an
authored scene spec, so the composed segment set is sized against the cells that exist rather
than against the sixteen the table can address.

Mask bits (a bit is SET when that neighbour IS a wall):  8=N  4=S  2=E  1=W
Under bible section 3 a tile shows a FRONT FACE exactly when the SOUTH bit is CLEAR.
"""
import json
import os
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def build(spec):
    w, h = spec["width"], spec["height"]
    wall = [[True] * w for _ in range(h)]
    for r in spec["carve"]:
        for y in range(r["y0"], r["y1"] + 1):
            for x in range(r["x0"], r["x1"] + 1):
                wall[y][x] = False
    return wall, w, h


def is_wall(wall, w, h, x, y):
    # IsWallTile returns false out of bounds - map borders do NOT count as walls.
    if x < 0 or y < 0 or x >= w or y >= h:
        return False
    return wall[y][x]


def masks(wall, w, h, x, y):
    c = 0
    if is_wall(wall, w, h, x, y - 1):
        c |= 8
    if is_wall(wall, w, h, x, y + 1):
        c |= 4
    if is_wall(wall, w, h, x + 1, y):
        c |= 2
    if is_wall(wall, w, h, x - 1, y):
        c |= 1
    d = 0
    if c == 15:
        if not is_wall(wall, w, h, x + 1, y - 1):
            d |= 8
        if not is_wall(wall, w, h, x - 1, y - 1):
            d |= 4
        if not is_wall(wall, w, h, x + 1, y + 1):
            d |= 2
        if not is_wall(wall, w, h, x - 1, y + 1):
            d |= 1
    return c, d


def collapse(c):
    return 3 if c in (7, 11) else 12 if c in (13, 14) else c


def census(path):
    spec = json.load(open(path))
    wall, w, h = build(spec)
    raw, eff, viol, cells = Counter(), Counter(), [], Counter()
    for y in range(h):
        for x in range(w):
            if not wall[y][x]:
                continue
            c, d = masks(wall, w, h, x, y)
            raw[c] += 1
            e = collapse(c)
            key = e if e != 15 else f"15/d{d}"
            eff[key] += 1
            # Section 3: a face is legal only where the SOUTH neighbour is not a wall.
            south_is_wall = bool(c & 4)
            face_drawn = not (e & 4)
            if south_is_wall and face_drawn:
                viol.append((x, y, c, e))
            cells["face" if face_drawn else "top-only"] += 1
    return spec, w, h, raw, eff, viol, cells


if __name__ == "__main__":
    for path in sys.argv[1:]:
        spec, w, h, raw, eff, viol, cells = census(path)
        print("=== %s  (%dx%d) ===" % (spec["name"], w, h))
        print("  raw cardinal masks :", dict(sorted(raw.items())))
        print("  after the collapse :", dict(sorted(eff.items(), key=lambda kv: str(kv[0]))))
        print("  planes drawn       :", dict(cells))
        print("  SECTION 3 VIOLATIONS (face drawn with wall to the south): %d" % len(viol))
        if viol:
            xs = ", ".join("(%d,%d) raw=%d->%d" % v for v in viol[:12])
            print("    " + xs + (" ..." if len(viol) > 12 else ""))
        print()
