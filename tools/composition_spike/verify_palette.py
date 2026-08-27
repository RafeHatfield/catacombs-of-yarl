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
    surv = json.load(open(os.path.join(C.SURVIVORS, "MANIFEST.json")))["survivors"]
    floors = [np.array(Image.open(os.path.join(C.SURVIVORS, s["file"])).convert("RGB"))
              .astype(np.int16) for s in surv]

    ok = True
    for arm, cfg in C.ARMS.items():
        # The reference palette must be built from EXACTLY the stock the composer used. When
        # round 5 gave the face plane three parts and this checker was still building its
        # reference from one, it reported 175 colours "outside the parts bin" - the checker was
        # wrong, not the tiles. Recorded because that is this check demonstrating it can fail
        # (§13.5), which is the only thing that makes its passes worth anything.
        stock = C.build_top_stock(cfg["tops"], face, cfg["match"])
        pal = set(map(tuple, C.palette_of(*[f[0] for f in faces],
                                          *[t[0] for t in stock], *floors)))
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
