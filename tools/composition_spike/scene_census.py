#!/usr/bin/env python3
"""How much WALL FACE a review scene can actually show.

Under bible §3 a wall presents a front face only where floor lies to its SOUTH. That makes the
share of a scene's wall cells that can carry a face a property of the CARVE, not of the art —
and it bounds every verdict the scene can produce about a face. corridor_junction.json puts
about 6% of its wall cells in that class, which is why six critic rounds answered the thickness
question on a two-row strip.

This reimplements DungeonRenderer's mask computation and its 7/11->3, 13/14->12 collapse. If it
disagrees with the engine, the engine is the truth and this is the bug.
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCENES = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes")
SOUTH_BIT = 4


def census(path):
    spec = json.load(open(path))
    W, H = spec["width"], spec["height"]
    wall = [[True] * W for _ in range(H)]
    for c in spec["carve"]:
        for y in range(c["y0"], c["y1"] + 1):
            for x in range(c["x0"], c["x1"] + 1):
                wall[y][x] = False

    def isw(x, y):
        return True if x < 0 or y < 0 or x >= W or y >= H else wall[y][x]

    masks, faces, south_facing = Counter(), 0, 0
    for y in range(H):
        for x in range(W):
            if not wall[y][x]:
                continue
            c = (8 if isw(x, y - 1) else 0) | (4 if isw(x, y + 1) else 0) \
                | (2 if isw(x + 1, y) else 0) | (1 if isw(x - 1, y) else 0)
            raw = c
            c = {7: 3, 11: 3, 13: 12, 14: 12}.get(c, c)
            masks[c] += 1
            if not (c & SOUTH_BIT):
                faces += 1
                # A TRUE south-facing wall: floor below it, wall above it. These are the cells
                # §3's front face was written for.
                if raw == 11:
                    south_facing += 1
    total = sum(masks.values())
    return spec, masks, faces, south_facing, total


def main():
    names = sys.argv[1:] or ["corridor_junction.json", "wall_face_review.json"]
    for n in names:
        spec, masks, faces, south, total = census(os.path.join(SCENES, n))
        print("%s  (%s)" % (n, spec["name"]))
        print("  player %s   %dx%d   %d wall cells"
              % (spec["player"], spec["width"], spec["height"], total))
        for m in sorted(masks):
            kind = "top surface only" if (m & SOUTH_BIT) else "TOP BAND + FRONT FACE"
            print("    mask %-2d  %4d   %s" % (m, masks[m], kind))
        print("  cells that can show a face: %d of %d = %.1f%%   (true south-facing: %d)\n"
              % (faces, total, 100.0 * faces / total, south))
    return 0


if __name__ == "__main__":
    sys.exit(main())
