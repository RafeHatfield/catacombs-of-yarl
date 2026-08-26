#!/usr/bin/env python3
"""Round 9 — guide v5: the chamfers deleted, the materials separated by hue."""
import json
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
d = json.load(open(os.path.join(P, "wall_round08.json")))

d["round"] = 9
d["framing"] = "guide v5 — the guide stops baking light, and the materials stop being one grey"
d["init_strengths"] = [350] * 10
d["hypothesis"] = (
    "Round 8 went backwards on the one axis §6.3 governs: key-light culls rose from 0 to 3. The "
    "cause is identifiable and it is mine. v4's 1px chamfers — light on a block's top edge, "
    "dark on its bottom — were taken literally from ROUND 7'S OWN FLIP LIST, and at 32px a "
    "per-course light-top/dark-bottom pattern is indistinguishable from a baked directional "
    "light. A critic instruction, executed faithfully, manufactured the violation the same "
    "critic then culled. That is worth more than the round's verdicts: at this canvas size the "
    "vocabulary for 'describe geometry with value' and the vocabulary for 'bake a key light' "
    "are the same vocabulary. v5 deletes the chamfers and separates courses by mortar recess "
    "and block variation alone. It also answers round 8's other structural note — 'every tile "
    "is 4-13 values of the same grey-blue' — by giving timber and iron their own hue, since a "
    "monochrome guide was arguably causing the monochrome output.")
d["parameter_provenance"]["init_image"] = {
    "value": "guides/guide_NN.png (v5)",
    "clause": ("Geometry and material separation. Chamfers deleted (they caused round 8's "
               "key-light culls). Timber and iron carry their own hue offsets so a beam is not "
               "the same colour as the wall it is pinned to. ⚠ Material differentiation, NOT a "
               "palette: §5.1 reserves colour authorship to the bible, nothing here proposes a "
               "game colour, `color_image` is never set, the guide never reaches the critic and "
               "cannot land, and the output's colours still come from the generator.")}

with open(os.path.join(P, "wall_round09.json"), "w") as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print("round 9 written")
