#!/usr/bin/env python3
"""Derive round 5 from round 4 so the text is provably identical and only the lever moves."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "prompts")

d = json.load(open(os.path.join(P, "wall_round04.json")))
d["round"] = 5
d["framing"] = "GUIDED GENERATION — init_image structural under-drawing on the frozen surface"
d["conditioned"] = False
d.pop("style_reference", None)
d.pop("style_strength", None)
d["init_guide"] = True
d["init_strengths"] = [300] * 5 + [150] * 5

d["hypothesis"] = (
    "Four rounds, 40 generations, 0 passes, four different text framings — object (r1), noise "
    "(micro-probe), landmark (r3), conditioned (r4). Across ALL of them two critic demands never "
    "once appeared in output: a 3-4px TOP-SURFACE BAND along the top edge (every round put its "
    "band along the bottom instead), and a REPAIR at readable scale. Both are requests to put a "
    "specific element at a specific PLACE in a 32x32 frame. By round 4 the flip lists had become "
    "pixel surgery — 'shift the right-hand blocks down two rows', 'repaint pixel (5,23)' — which "
    "no text prompt can execute. Four differently-worded attempts is enough evidence to stop "
    "rewording. This round supplies the geometry directly as `init_image`, a documented parameter "
    "of the FROZEN surface, and lets the prompt keep supplying material, register and wear. Two "
    "strengths run in the same round so the lever's shape is measured rather than assumed. "
    "⚠ If this works, the finding is NOT 'text-to-image produces architectural surfaces'. It "
    "is 'text-to-image does not, and guided generation does' — a different pipeline, reported as "
    "one.")

d["text_unchanged_from_round"] = 4
d["parameter_provenance"]["init_image"] = {
    "value": "guides/guide_NN.png",
    "clause": ("A structural under-drawing: top band, irregular courses cut by the frame edges, "
               "a baulk running off both sides with two pin heads. GEOMETRY ONLY — neutral greys "
               "for value separation, never a palette proposal (§5 forbids this probe "
               "creating one), and `color_image` is never set. The guide is not an asset, is "
               "never shown to the critic, and cannot land.")}
d["parameter_provenance"]["init_image_strength"] = {
    "value": "300 x5, 150 x5",
    "clause": ("300 is the schema's documented default. Both run in one round because the "
               "direction and magnitude of this parameter are unmeasured on this endpoint, and "
               "AUDIT 9.3 measured a neighbouring parameter being silently ignored while still "
               "billing in full.")}
d["parameter_provenance"]["note"] = (
    "The DESCRIPTION and NEGATIVE_DESCRIPTION are byte-identical to round 4's, deliberately. One "
    "lever moves this round and it is init_image, so any difference is attributable to it.")

with open(os.path.join(P, "wall_round05.json"), "w") as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print("round 5 written; text identical to round 4:",
      d["description"] == json.load(open(os.path.join(P, "wall_round04.json")))["description"])
