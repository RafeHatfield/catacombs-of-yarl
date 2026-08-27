#!/usr/bin/env python3
"""Verify the one honesty claim this composition makes about colour.

ART-BIBLE-v0 §5 marks every palette value PLACEHOLDER. This spike therefore proposes nothing:
every pixel it writes - stone, occlusion, iron, rope, tag - is snapped to the union of the
colours already present in the parts it was built from. That is a checkable claim rather than
an assurance, so it is checked here and the number goes in the report.

This is NOT a lint and NOT a gate. It measures a property of this session's own script against
this session's own inputs. It instruments no register clause (§13.4).
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_walls as C  # noqa: E402


def main():
    faces = C.build_face_stock()
    face = faces[0][0]
    # Mirror the composer EXACTLY, including which floor files it actually loads. Round 8 uses
    # the de-ringed derivation; a checker still reading the raw survivors reported 391 colours
    # "outside the parts bin" on tiles that were fine. Second time this check has failed on its
    # own reference rather than on the tiles, and both are kept on the record: a check that has
    # never failed is not evidence of anything (§13.5).
    surv = json.load(open(os.path.join(C.SURVIVORS, "MANIFEST.json")))["survivors"]
    dering = os.path.join(REPO, C.ASSETS, "floors_deringed")
    floors = []
    for i, s in enumerate(surv):
        d = os.path.join(dering, "MOCK_dering_%d.png" % (C.FLOOR_BASE + i))
        used = d if os.path.exists(d) else os.path.join(C.SURVIVORS, s["file"])
        floors.append(np.array(Image.open(used).convert("RGB")).astype(np.int16))

    ok = True
    for arm, cfg in C.ARMS.items():
        # The reference palette must be built from EXACTLY the stock the composer used. When
        # round 5 gave the face plane three parts and this checker was still building its
        # reference from one, it reported 175 colours "outside the parts bin" - the checker was
        # wrong, not the tiles. Recorded because that is this check demonstrating it can fail
        # (§13.5), which is the only thing that makes its passes worth anything.
        floors_lum = float(sum(C.mean_lum(f) for f in floors) / len(floors))
        stock = C.build_top_stock(cfg["tops"], face, cfg.get("albedo"), floors_lum)
        extra = [C.load_part(C.COPING_PART, C.TOP_PARTS)[0]] if cfg.get("cap") else []
        pal = set(map(tuple, C.palette_of(*[f[0] for f in faces],
                                          *[t[0] for t in stock], *extra, *floors)))
        seen, outside, n = set(), 0, 0
        for p in sorted(glob.glob(os.path.join(REPO, C.ASSETS, arm, "*.png"))):
            n += 1
            cols = set(map(tuple, np.array(Image.open(p).convert("RGB"))
                           .astype(int).reshape(-1, 3)))
            seen |= cols
            outside += len(cols - pal)
        ok &= outside == 0
        print("  %-8s %3d tiles  %4d distinct colours  %d outside the parts bin"
              % (arm, n, len(seen), outside))
    print("\n%s" % ("every composed pixel is a colour that exists in the parts bin"
                    if ok else "A COMPOSED PIXEL IS NOT IN THE PARTS BIN"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
