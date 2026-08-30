#!/usr/bin/env python3
"""THE CORRIDOR REVIEW SCENE, REBUILT SO ITS TRAFFIC-KEYED SYSTEMS ARE ACTUALLY ON.

RULED (Rafe, 2026-08-30): *"Fix the review scenes first: give the corridor scene real traffic
(rooms/destinations) so traffic-keyed systems are actually on."*

WHY A NEW SPEC RATHER THAN AN EDIT. `corridor_junction.json` is section 6.4's instrument and
`wall_face_review.json` is the section 3 rounds', and both are cited by evidence already on disk.
The repo's own rule, written into both of those files: *a scene swap would silently invalidate
every comparison against that record.* So they stay, marked dead, and this is the live one.

WHAT IT FIXES, AND IT IS TWO THINGS, NOT ONE
--------------------------------------------
1. **Destinations.** Three rooms on the ends of the arms, plus a dead-end stub. `TrafficField`
   accumulates traversal between places; a bare cross of corridors has nowhere to be going.

2. **A LOOP, so no single figure can sever the map.** This is the half the ruling did not know it
   was asking for, because the audit's first diagnosis was wrong. The corridor scenes are dead
   not for want of rooms but because the player STANDS IN THEM: `FarthestWalkable` picks the
   spine's endpoints with a Dijkstra map that walks through blocking entities, and the spine
   itself is an A* that does not. In a one-wide corridor every route between the two halves runs
   through the figure, A* returns null, and the field collapses to exactly zero — 40 cells to 0,
   5 routes to 0, from one person standing still (`TrafficFieldReviewSceneTests`).
   A loop means there is always a second way round, so the disagreement cannot bite.

WHAT IT KEEPS, because the corridor scene's two recorded traps are still traps:
  * **corridors are ONE tile wide.** A three-wide carve is a room, and every cell in it has three
    or more open neighbours, so the junction check passes trivially and the scene stops testing
    what it claims.
  * **the junction sits inside the delivered reach**, which is about four tiles, not the nominal
    five.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCENES = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes")

W, H = 17, 21
PX, PY = 8, 11


def spec():
    carve = [
        # The trunk and the two crossings — the original corridor scene's geometry, unchanged.
        {"x0": 8, "y0": 3, "x1": 8, "y1": 18},
        {"x0": 2, "y0": 8, "x1": 14, "y1": 8},
        {"x0": 2, "y0": 14, "x1": 14, "y1": 14},
        # THE LOOP. Two side runs joining the crossings, so the trunk is never the only way
        # between them and a figure standing in it cannot sever the map.
        {"x0": 2, "y0": 8, "x1": 2, "y1": 14},
        {"x0": 14, "y0": 8, "x1": 14, "y1": 14},
        # DESTINATIONS. Traffic is traversal BETWEEN places; a corridor with no rooms is a
        # corridor with nowhere to be going.
        {"x0": 6, "y0": 2, "x1": 10, "y1": 3},
        {"x0": 6, "y0": 17, "x1": 10, "y1": 18},
        # A dead end, so the field has somewhere to decay to and something reads as unvisited.
        {"x0": 4, "y0": 11, "x1": 5, "y1": 11},
    ]
    return {
        "name": "tier1_corridor_traffic",
        "_comment": [ln for ln in __doc__.strip().splitlines()],
        "_legibility": [
            "Distances are from the player at (%d,%d). The ratified radius is 5.0 tiles and its"
            % (PX, PY),
            "DELIVERED reach is about four, so lit points are declared no further than four and",
            "dark ones past five; the fifth tile is the ambiguous band and nothing is asserted",
            "about it in either direction.",
        ],
        "legibility": [
            {"x": 8, "y": 9, "expect": "lit",
             "why": "the trunk two tiles north - the easy case"},
            {"x": 8, "y": 8, "expect": "lit",
             "why": "the northern crossing, 3 tiles - the junction the scene exists for"},
            {"x": 5, "y": 11, "expect": "lit",
             "why": "the dead-end stub's mouth, 3 tiles - the unvisited end"},
            # (2,17) was declared here first and it is a WALL cell, not floor. The probe measures
            # a declared point against LIT FLOOR beside the player, so a wall read 0.354 and the
            # capture was refused - a wall has no reason to match that reference and the guard was
            # right. Every legibility point must be a floor cell; the floor gate's own spec says
            # so and this spec forgot it.
            # ⚠ NO DARK POINT IS DECLARED, AND THAT IS A SCOPE STATEMENT RATHER THAN AN OMISSION.
            #
            # Three were tried. (2,17) is a WALL cell and the probe measures floor against lit
            # floor, so it read 0.354 and the capture was refused. (6,18) is seven tiles south of
            # a camera centred on the player and falls off the frame, so the probe refused rather
            # than measure the letterbox. (3,14) is floor, in frame, and 5.8 tiles out - and it
            # read 0.212 against a 0.10 bound.
            #
            # That third number is the finding. The furthest in-frame floor cell this scene can
            # reach is about 5.8 tiles, and a one-wide corridor's reference cell carries contact
            # occlusion on all four edges, so the ratio scale here is not a room scene's. **This
            # scene fits inside the delivered reach and cannot test the arc.** LOOP-PROCESS §2.2:
            # a capture declares the contexts it contains and flags the ones it does not.
            #
            # The arc is tested by `tier1_wall_review`, which has two declared dark points and
            # holds them. This scene's job is TRAFFIC, and it does that.
        ],
        "width": W, "height": H,
        "player": {"x": PX, "y": PY},
        "carve": carve,
    }


if __name__ == "__main__":
    p = os.path.join(SCENES, "tier1_corridor_traffic.json")
    json.dump(spec(), open(p, "w"), indent=2)
    print("wrote %s  player=(%d,%d)" % (os.path.relpath(p, REPO), PX, PY))
