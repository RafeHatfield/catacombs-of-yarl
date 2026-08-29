#!/usr/bin/env python3
"""What the three void candidates actually DELIVER, and what the unlit wall beside them delivers.

The void has no clause in the bible and this session proposes none — §13.1 gives the choice to
Rafe, in the scene, on the device. What a builder can do is put the numbers beside the pictures,
and one number in particular:

**how far apart are the three candidates, compared with how far the void is from the unlit stone
next to it.** A blind seat on the gate build separated them by measurement and then said the
thing that matters:

    *"Above y≈195 the pixels are exactly (1,1,2) with zero variance. Not dark — EMPTY. Authored
    void. Everywhere else is more of the same place, simply unlit. **The image gives you no way
    to tell them apart at 1:1.**"*

If the unlit wall already sits where the void does, the candidates are choosing between three
values that the rig has already collapsed — and that is worth knowing before a walk rather than
after it.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(HERE, "evidence")
sys.path.insert(0, HERE)
import light_field as LF                    # noqa: E402
import measure_wall_amplitude as MA         # noqa: E402

SCENE = "src/Presentation/assets/tier0_harness/scenes/tier1_wall_review.json"
ARMS = [("choice 0", "r12_family", 0), ("choice 1", "r12_void1", 1), ("choice 2", "r12_void2", 2)]


def patch(lum, g, x, y, inset=6):
    x0, y0, w, h = LF.cell_box(g, x, y)
    return lum[int(y0) + inset:int(y0 + h) - inset, int(x0) + inset:int(x0 + w) - inset]


def main():
    spec = json.load(open(os.path.join(REPO, SCENE)))
    man = json.load(open(os.path.join(REPO,
                    "src/Presentation/assets/tier1_walls_compensated/MANIFEST.json")))
    pred = MA.predict(spec, man)
    voids = [k for k, v in pred.items() if v[0] == "void"]
    tops = [k for k, v in pred.items() if v[0].startswith("top")]
    px, py = spec["player"]["x"], spec["player"]["y"]

    out = {"produced_by": "tools/tier1_walls/measure_void.py", "candidates": {}}
    print("THE VOID, DELIVERED — and the unlit wall beside it")
    print("  %-10s %8s %9s %9s   %s" % ("candidate", "authored", "delivered", "spread", "cells"))
    for label, tag, choice in ARMS:
        g = LF.read_grid(os.path.join(EV, tag + ".log"))
        img = np.array(Image.open(os.path.join(EV, tag + ".png")).convert("RGB")).astype(float)
        lum = (img * LF.W709).sum(2)
        vs = [patch(lum, g, x, y) for (x, y) in voids if LF.in_view(g, x, y)]
        if not vs:
            print("  %-10s no void cells in view" % label)
            continue
        allv = np.concatenate([v.ravel() for v in vs])
        authored = [t for t in man["tiles"] if t["cls"] == "void"][choice]["value"]
        out["candidates"][label] = dict(authored=authored, delivered=round(float(allv.mean()), 3),
                                        spread=round(float(allv.max() - allv.min()), 3),
                                        cells=len(vs))
        print("  %-10s %8d %9.3f %9.3f   %d" % (label, authored, allv.mean(),
                                                allv.max() - allv.min(), len(vs)))

    # The comparator: unlit wall top, past the delivered reach.
    g = LF.read_grid(os.path.join(EV, "r12_family.log"))
    img = np.array(Image.open(os.path.join(EV, "r12_family.png")).convert("RGB")).astype(float)
    lum = (img * LF.W709).sum(2)
    far = [patch(lum, g, x, y).mean() for (x, y) in tops
           if LF.in_view(g, x, y) and np.hypot(x - px, y - py) >= 6]
    if far:
        out["unlit_wall_beyond_six_tiles"] = round(float(np.mean(far)), 3)
        print()
        print("  unlit wall top past six tiles: %.3f   (n=%d)" % (np.mean(far), len(far)))

    d = [v["delivered"] for v in out["candidates"].values()]
    if len(d) > 1:
        print()
        print("  THE THREE CANDIDATES SPAN %.2f LUMINANCE." % (max(d) - min(d)))
        if far:
            print("  The unlit wall sits %.2f above the darkest of them."
                  % (float(np.mean(far)) - min(d)))
        print("  Both numbers are for the gate, not for this file. Section 13.1 rules the void.")
    json.dump(out, open(os.path.join(EV, "VOID-CANDIDATES.json"), "w"), indent=2)
    print("\n  wrote tools/tier1_walls/evidence/VOID-CANDIDATES.json")


if __name__ == "__main__":
    main()
