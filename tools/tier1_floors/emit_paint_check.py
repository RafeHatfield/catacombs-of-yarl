#!/usr/bin/env python3
"""FINISHED PIXELS FOR THE ENGINE TO REPRODUCE — the last unchecked seam.

The manifest already carries two cross-check vectors, and between them they prove a great deal:
`edge_family_check` says the engine agrees with the composer about which family a boundary has,
and `stone_check` says it agrees about how many ladder steps a stone moves.

**They prove nothing about the two largest pieces of arithmetic in the painter.** Where in the
grain bank a stone samples — which depends on its key, its origin measured from its boundary, and
a modulo — and which joints the arris pass rounds, which depends on a class-mask neighbourhood.
Either could be wrong in a way that still produced a plausible floor, on the device, with every
existing check green. That is the exact shape of the failures this session has spent its time
finding, and it was the one place left where nothing would have said so.

So this walks the shipped path — atlas in, grain sampled, stones painted, arris rounded — and
writes FINISHED RGB for a scatter of pixels chosen to cover every case the painter has:

    a joint, and a joint beside trodden stone
    plain stone, and trodden stone
    a stone spanning a vertical boundary, seen from BOTH sides of it

`Tier1AshlarFloor.SelfCheck` runs the very code that lays the floor against these and refuses to
lay anything if a single one disagrees. A check against a reimplementation would only prove the
reimplementation.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_ashlar as CA        # noqa: E402
import verify_atlas_path as VP     # noqa: E402

WORN_COLUMNS = [3, 4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=8)
    ap.add_argument("--h", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--samples", type=int, default=96)
    ap.add_argument("--assets", help="asset directory; defaults to the candidate family. The "
                                     "PLANT needs its own check: it inherits the candidate's "
                                     "manifest wholesale, and a check written for the candidate's "
                                     "pixels would make the plant REFUSE TO LAY — the control arm "
                                     "silenced by the candidate's evidence.")
    a = ap.parse_args()

    assets = os.path.join(REPO, a.assets) if a.assets else CA.ASSETS
    mp = os.path.join(assets, "MANIFEST.json")
    man = json.load(open(mp))
    if man["seed"] != a.seed:
        raise SystemExit("REFUSING: the manifest was built at seed %d, not %d."
                         % (man["seed"], a.seed))

    worn = lambda x, y: x in WORN_COLUMNS
    img = VP.paint_from_atlas(a.w, a.h, a.seed, man, worn=worn, assets=assets)

    # Deliberate spread: the trodden columns and their neighbours (so the arris pass and the
    # channel's edge are both covered), and cells away from them for the plain case.
    rng = np.random.default_rng(a.seed)
    picks, seen = [], set()
    cols = [2, 3, 4, 5, 0, 6, 1, 7]
    while len(picks) < a.samples:
        x = int(cols[len(picks) % len(cols)])
        y = int(rng.integers(0, a.h))
        px, py = int(rng.integers(0, CA.T)), int(rng.integers(0, CA.T))
        k = (x, y, px, py)
        if k in seen:
            continue
        seen.add(k)
        r, g, b = img[y * CA.T + py, x * CA.T + px]
        picks.append(dict(x=x, y=y, px=px, py=py, r=int(r), g=int(g), b=int(b)))

    man["paint_check"] = dict(
        worn_columns=WORN_COLUMNS, grid=[a.w, a.h], samples=picks,
        what=("finished RGB from the shipped path. The engine reproduces every one of these or "
              "refuses to lay the floor. Covers joints, plain stone, trodden stone, joints beside "
              "trodden stone, and spanning stones seen from both sides."))
    with open(mp, "w") as f:
        json.dump(man, f, indent=1)

    print("PAINT CHECK — %d finished pixels the engine must reproduce" % len(picks))
    print("  assets: %s" % os.path.relpath(assets, REPO))
    print("  trodden columns: %s" % WORN_COLUMNS)
    print("  written: %s" % os.path.relpath(mp, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
