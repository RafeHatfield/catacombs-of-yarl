#!/usr/bin/env python3
"""THE STANDING STATION — the gate scene's geometry, with the player where a player stands.

The gate ruled §6.5 down to a STANDING-DISTANCE law — two tiles and in — and the gate scene has
exactly ONE reveal inside 3.2 tiles, so every standing-case number was n=1.

The obvious alternative was the corridor review scene, which has close reveals in quantity. It
turned out to be unusable, for a reason worth recording rather than working around: **its traffic
field is entirely zero.** A symmetric cross of one-wide corridors with no rooms and no dead ends
gives `TrafficField` nothing to accumulate, so NO traffic-keyed system can be exercised there —
not the wall's aging, and not the floor's wear either. That reaches backwards into every round
that used that scene.

So the station keeps the geometry that HAS traffic and moves the eye instead. It is an INSTRUMENT
STATION, not a second gate scene: nothing is judged here that is not judged in the walk. It exists
so that a number about the standing case is taken standing.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCENES = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes")

if __name__ == "__main__":
    d = json.load(open(os.path.join(SCENES, "tier1_wall_review.json")))
    d["name"] = "tier1_wall_standing"
    d["_comment"] = [ln for ln in __doc__.strip().splitlines()]
    d["player"] = {"x": 8, "y": 12}
    d.pop("_legibility", None)
    d["legibility"] = [
        {"x": 8, "y": 13, "expect": "lit",
         "why": "the cell behind the player, 1 tile - the standing case's own ground"},
        {"x": 5, "y": 14, "expect": "lit", "why": "room A's west side, 3.6 tiles"},
        # (3,19) was the obvious dark point and it is 8.6 tiles from a player who has walked
        # four tiles NORTH, which puts it off the bottom of the frame. The probe refused the
        # capture rather than measuring the letterbox, which is the guard working. Moved to a
        # corner that is both dark and on screen.
        {"x": 3, "y": 17, "expect": "dark",
         "why": "room A's south-west corner, 7.1 tiles - the arc's outside, and in frame"},
    ]
    p = os.path.join(SCENES, "tier1_wall_standing.json")
    json.dump(d, open(p, "w"), indent=2)
    print("wrote %s  player=(%d,%d)" % (os.path.relpath(p, REPO),
                                        d["player"]["x"], d["player"]["y"]))
