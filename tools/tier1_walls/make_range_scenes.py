#!/usr/bin/env python3
"""SOUTH REVEALS AT EVERY RANGE THE LAMP REACHES — the geometry the stack question needs.

WHY. `tier1_floor_review.json` contains south-facing reveals at exactly one band of ranges,
3.0 to 3.6 tiles, because the player stands in the middle of a room whose north wall is three
cells away. Solving the authored stack against that alone answers *what does the rig do at three
tiles* and reports it as *what the rig does*. Bible section 6.2.1 asks the opposite question -
**the stack surviving the falloff ACROSS the lit radius, not only at its middle** - and a scene
that samples one range cannot pose it.

WHAT IT BUILDS. Two specs. Each carves one wide room and leaves a column of ISOLATED single-cell
wall blocks standing in it, directly north of the player, at alternating ranges: spec A holds
ranges 1, 3 and 5, spec B holds 2 and 4. Alternating because two blocks in adjacent cells are
neighbours - they would stop being isolated, their masks would change, and the north one would
lose the floor to its south that makes it a reveal at all.

An isolated block is cardinal mask 0: floor on all four sides, so it shows a top plane and a
front face, which is exactly the pair being measured. It is a MEASURING FIXTURE and not a
proposal about level design - nothing here is captured for a seat or shown to anyone.

The room is carved wide enough that no block is wall-adjacent to the room's own boundary, so
DarkFloorModulate lands on the same cells around every block and cannot bias one range.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "src/Presentation/assets/tier1_walls_probe/scenes")

W, H = 17, 25
PX, PY = 8, 18          # far enough south that six ranges north of it stay inside the room
BX = PX - 1             # THE BLOCKS STAND ONE COLUMN WEST OF THE PLAYER, and that is not
                        # cosmetic. A block directly north at range one has the PLAYER'S OWN
                        # CELL as the floor it faces, and the player sprite is drawn on it - so
                        # the one range where a wall is closest is the one range whose floor
                        # sample is a picture of Sasha. Offsetting by a column keeps every paired
                        # floor cell bare.


def spec(name, ranges):
    # One room, wide and tall enough to hold every block with floor on all four sides.
    # The spec format carves floor out of solid rock and has no "leave this cell standing"
    # primitive, so a block is expressed as the row it sits in being carved either side of it.
    y0, y1 = PY - 8, PY + 2
    blocked = {PY - r for r in ranges}
    carve = []
    run = None
    for y in range(y0, y1 + 1):
        if y in blocked:
            if run is not None:
                carve.append({"x0": 2, "y0": run, "x1": 14, "y1": y - 1})
                run = None
            carve.append({"x0": 2, "y0": y, "x1": BX - 1, "y1": y})
            carve.append({"x0": BX + 1, "y0": y, "x1": 14, "y1": y})
        else:
            run = y if run is None else run
    if run is not None:
        carve.append({"x0": 2, "y0": run, "x1": 14, "y1": y1})
    return {
        "name": name,
        "_comment": [
            "MEASURING FIXTURE - tools/tier1_walls/make_range_scenes.py. Not a review scene.",
            "Isolated wall blocks (cardinal mask 0) stand at ranges %s tiles due north of the"
            % ", ".join(str(r) for r in ranges),
            "player, each with floor on all four sides, so each shows the top/face pair whose",
            "delivered ratio against the floor it faces is the quantity bible section 6.5 states",
            "and section 6.2's coupling flag says must be solved backwards through this rig.",
        ],
        "width": W, "height": H,
        "player": {"x": PX, "y": PY},
        "carve": carve,
        "_blocks": [{"x": BX, "y": PY - r, "row": r} for r in ranges],
    }


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for tag, ranges in (("a", (1, 3, 5, 7)), ("b", (2, 4, 6))):
        s = spec("tier1_wall_range_%s" % tag, ranges)
        p = os.path.join(OUT, "wall_range_%s.json" % tag)
        json.dump(s, open(p, "w"), indent=2)
        print("wrote %s  ranges=%s" % (os.path.relpath(p, REPO), ranges))
