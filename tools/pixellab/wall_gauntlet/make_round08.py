#!/usr/bin/env python3
"""Round 8 — guide v4, strength held flat so the guide is the only variable."""
import json
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
d = json.load(open(os.path.join(P, "wall_round07.json")))

d["round"] = 8
d["framing"] = "guide v4 — round 7's items encoded; strength held at the balance point"
d["init_strengths"] = [350] * 10
d["hypothesis"] = (
    "Round 7's flip list is almost entirely tone discipline and placement, and both are "
    "executable in the guide and nowhere else in this pipeline. v4 encodes them literally, and "
    "makes the repair INTERRUPT its mortar course rather than lie on top of one — the last "
    "untried way to state it, after seven rounds in which the repair never once appeared in a "
    "critic verdict, three of them with a baulk drawn straight into the guide. Strength is held "
    "flat at 350 so guide v4 is the single variable against round 7's 300/400 bracket.")
d["parameter_provenance"]["init_image_strength"] = {
    "value": "350 x10",
    "clause": ("Held FLAT this round, deliberately. Rounds 5, 6 and 7 all moved strength, so "
               "holding it now is what makes guide v4 the only thing that changed.")}
d["parameter_provenance"]["init_image"] = {
    "value": "guides/guide_NN.png (v4)",
    "clause": ("Geometry only; no palette, `color_image` never set, never shown to the critic, "
               "cannot land. Round 7's items: one light tone reserved to rows 0-4 and absent "
               "below row 5; band seated on a 1px dark line; at most three courses with blocks "
               ">=9px wide; alternate courses offset by a non-half-block amount so joints stop "
               "stacking; flat faces with 1px chamfers top AND bottom so a value change "
               "describes geometry rather than a light source; timber 4px tall at full width "
               "interrupting its course; pins as a 2px head with a 1px dark seat; bright motifs "
               "at a different coordinate in every variant; one discontinuous course packed "
               "with rubble.")}

with open(os.path.join(P, "wall_round08.json"), "w") as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print("round 8 written")
