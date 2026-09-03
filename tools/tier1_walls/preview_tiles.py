#!/usr/bin/env python3
"""A contact sheet of the composed tiles, and an ASSEMBLED RUN beside it.

⚠ THE SHEET IS A DEBUGGING AID AND NOTHING ELSE. Bible section 13.1: no candidate is ever
approved from a contact sheet, and section 8.3's scale rule says the property that matters -
whether a tiled field reads as a lattice - does not exist at tile scale at all. So the run is
here too, because a wall is judged AS LAID or it is not judged.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)


def key_v(x, y, salt):
    import compose_walls as CW
    return CW.h(salt, "v", x, y) % CW.EDGE_FAMILIES


def key_h(x, y, salt):
    import compose_walls as CW
    return CW.h(salt, "h", x, y) % CW.EDGE_FAMILIES


def run_strip(assets, man, cells=10, rows=2, scale=4):
    """A wall run as the engine would lay it: keys from world position, tiles by lookup."""
    import compose_walls as CW
    sv, sh = man["salts"]["v"], man["salts"]["h"]
    T = 32
    out = Image.new("RGB", (cells * T * scale, rows * T * scale), (18, 18, 24))
    for r in range(rows):
        for i in range(cells):
            x, y = i + 3, r + 3
            cls = "face" if r == rows - 1 else "top"
            kw = CW.h(sv, "v", x, y) % CW.EDGE_FAMILIES
            ke = CW.h(sv, "v", x + 1, y) % CW.EDGE_FAMILIES
            kn = CW.h(sh, "h", x, y) % CW.EDGE_FAMILIES
            tid = man["table"][cls]["%d,%d,%d" % (kw, ke, kn)]
            f = [t for t in man["tiles"] if t["id"] == tid][0]["file"]
            im = Image.open(os.path.join(assets, f)).convert("RGB")
            out.paste(im.resize((T * scale, T * scale), Image.NEAREST),
                      (i * T * scale, r * T * scale))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default=os.path.join(REPO, "src/Presentation/assets/tier1_walls"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    man = json.load(open(os.path.join(a.assets, "MANIFEST.json")))
    strip = run_strip(a.assets, man)
    strip.save(a.out)
    print("wrote %s  (%s)" % (a.out, strip.size))
