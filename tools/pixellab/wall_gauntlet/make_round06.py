#!/usr/bin/env python3
"""Derive round 6 from round 5 so the prompt text is provably unchanged for a third round."""
import json
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
d = json.load(open(os.path.join(P, "wall_round05.json")))

d["round"] = 6
d["framing"] = "guided generation, guide v2 + higher strength — the lever's direction is now measured"
d["init_strengths"] = [500] * 5 + [800] * 5
d["hypothesis"] = (
    "Round 5 was the best round of the gauntlet on mechanical culls — 8 of 10 reached the wall "
    "questions, against 4, 6, 0, 6 before it — and still returned 0 passes. Two things were "
    "MEASURED there and both drive this round. FIRST: init_image_strength 300 beat 150 clearly. "
    "At 150 the guide's geometry was overridden and one candidate reverted to a doorway; at 300 "
    "the coursing held. The lever's direction is up, so this round runs 500 and 800. SECOND: the "
    "guide CONTAINED a baulk with pin heads and the generator painted over it at both strengths "
    "— the timber sat at a value close to the stone and was absorbed as just another course. "
    "Guide v2 pushes the timber well clear of every stone value, gives it a second grain value "
    "so it is not one flat bar, enlarges the pins and bruises the stone under them. The top band "
    "gains its own perpendicular coursing and a hard dark row at its front edge, because the "
    "critic's round-5 objection was exactly that a flat lighter band reads as 'no thickness at "
    "all'. Prompt text stays byte-identical to rounds 4 and 5.")
d["parameter_provenance"]["init_image_strength"] = {
    "value": "500 x5, 800 x5",
    "clause": ("MEASURED in round 5: 300 held the guide's coursing and 150 did not, so the "
               "parameter's direction is up and higher means more adherence. 500 and 800 "
               "bracket the range above the tested point; running both in one round keeps the "
               "shape of the lever visible rather than assumed.")}
d["parameter_provenance"]["init_image"] = {
    "value": "guides/guide_NN.png (v2)",
    "clause": ("Geometry only, still — no palette, `color_image` never set, never shown to the "
               "critic, cannot land. v2 changes three things and each traces to a round-5 critic "
               "item: timber value pushed clear of every stone value; top band given "
               "perpendicular coursing plus a hard dark row at the front edge; courses laid in "
               "running bond so no vertical joint crosses two courses.")}

with open(os.path.join(P, "wall_round06.json"), "w") as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
r4 = json.load(open(os.path.join(P, "wall_round04.json")))
print("round 6 written; text still identical to round 4:", d["description"] == r4["description"])
