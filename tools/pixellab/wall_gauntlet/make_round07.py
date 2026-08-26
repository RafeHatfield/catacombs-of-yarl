#!/usr/bin/env python3
"""Round 7 — guide v3 at the measured balance point. Prompt text unchanged since round 4."""
import json
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
d = json.load(open(os.path.join(P, "wall_round06.json")))

d["round"] = 7
d["framing"] = "guide v3 at the measured balance point — the gauntlet's best shot"
d["init_strengths"] = [300] * 5 + [400] * 5
d["hypothesis"] = (
    "Round 6 measured the lever's real shape, and it is not the useful one: at 500 and 800 the "
    "generator returned the GUIDE — flat grey rectangles with no stone material on them at all. "
    "Set against round 5's 300 and 150, `init_image` is a BLEND control, not a composition "
    "control. It interpolates between your image and a generated one, so at the strength where "
    "geometry holds there is no generation left to supply material. A candidate produced at 800 "
    "is programmer-art laundered through an API, and had one passed the critic the pass would "
    "have been worthless — none did, which is a point in the critic's favour. Round 7 returns to "
    "the balanced point (300, with 400 to bracket it) using a guide rebuilt to do two jobs: "
    "carry round 6's structural flip items — which are pixel surgery, and the guide is the one "
    "place in this pipeline where pixel surgery is executable — and carry intra-block value "
    "variation, so whatever share of the output the guide wins reads as stone rather than as "
    "rectangles. If this fails, the honest reading is not that the guide was wrong. It is that "
    "the useful operating point does not exist on this endpoint.")
d["parameter_provenance"]["init_image_strength"] = {
    "value": "300 x5, 400 x5",
    "clause": ("300 was the most balanced of the four strengths measured across rounds 5 and 6 "
               "(150 / 300 / 500 / 800). 400 brackets it upward without re-entering the range "
               "where the guide simply wins and the generator contributes nothing.")}
d["parameter_provenance"]["init_image"] = {
    "value": "guides/guide_NN.png (v3)",
    "clause": ("Geometry only; no palette, `color_image` never set, never shown to the critic, "
               "cannot land. v3 encodes round 6's items literally: top-band divisions aligned to "
               "the first course's joints; a 1px lip darker than the top and lighter than the "
               "face rather than a black line; named fixings — struck head, shank down into the "
               "joint, one mushroomed pixel — at differing sizes and off a shared row; timber "
               "lighter than the joint value so it cannot read as a gap in the wall; knocked "
               "corners, spalled patches, a stone dropped out of course, joint width varying "
               "including one run with no joint at all; seam stones widened to at least 5px.")}

with open(os.path.join(P, "wall_round07.json"), "w") as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
r4 = json.load(open(os.path.join(P, "wall_round04.json")))
print("round 7 written; prompt text unchanged since round 4:",
      d["description"] == r4["description"])
