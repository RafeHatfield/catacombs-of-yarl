#!/usr/bin/env python3
"""Round 10 — the last 10 of the declared 100-generation budget."""
import json
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
d = json.load(open(os.path.join(P, "wall_round09.json")))

d["round"] = 10
d["framing"] = "guide v6 — per-tile variation; the final round of the declared budget"
d["init_strengths"] = [350] * 10
d["hypothesis"] = (
    "Ninety generations spent, nine rounds, zero passes. Round 9's leading flip item is the "
    "guide's own fault and is fixed here: a constant course height put every tile's joints on "
    "the same rows, so a set of ten guides could not help banding a wall into stripes. v6 "
    "varies course count and heights per tile, floats the timber to a different height in each, "
    "and drives a pin through a course JOINT rather than into a block face — round 9's third "
    "item, and the ninth consecutive round in which the critic has reported nothing fastened in "
    "the set. This is the last round of the declared budget. It is run to spend the budget "
    "honestly rather than because the trajectory suggests it will clear the bar: the bar was "
    "declared at 5 passes before the first generation and stopping short of the budget would be "
    "cutting the measurement to fit the expectation (LOOP-PROCESS §8).")

with open(os.path.join(P, "wall_round10.json"), "w") as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print("round 10 written")
