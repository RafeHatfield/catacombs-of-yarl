#!/usr/bin/env python3
"""Land props authored at READABILITY SCALE — bible §12.2.

    python3 tools/tier2_props/land_scaled_props.py --plan <plan.json>

WHAT CHANGED, AND IT IS THE SIZE RATHER THAN THE METHOD. `land_props.py` is still right about
how a prop is generated: style-matched, conditioned on a crop of the LANDED FRAME, downsampled
2:1 because the context is the family at 2x and the generator draws 2px per art-pixel. That
finding stands and this script keeps it.

What Rafe's walk changed is how big the thing may be. The old family authored every prop into one
32px cell and the content came out as small as 10 x 15 px — a fifth of the cell, twenty device
pixels across — and the gate failed it on identifiability: *"small, unrecognizable except the
fire."* §12.2 now authors a prop at the size at which it can be named, and lets a large object
span 1x2 or 2x2 cells. So a sprite arrives as a FOOTPRINT, not a tile, and this cuts it into the
cells the renderer lays row-major.

⚠ THE CUT IS THE PART THAT CAN SILENTLY GO WRONG. `DungeonRenderer` indexes TileLayout row-major
over FootprintW x FootprintH. Cut the sheet column-major and a 1x2 still works — one column — so
the error hides until the first 2x2 and then draws a scrambled object with no error anywhere.
The cut here is row-major and `--selftest` asserts it against a numbered probe.
"""
import argparse
import hashlib
import io
import json
import os
import sys
import urllib.request

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DEST = os.path.join(REPO, "src/Presentation/assets/tier1_ashlar")
NATIVE = 32
DEVICE = 2                      # the frame, and therefore the generator's canvas, is 2x


def fetch(url, cache):
    if os.path.exists(cache):
        return Image.open(cache).convert("RGBA")
    with urllib.request.urlopen(url) as r:
        data = r.read()
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    open(cache, "wb").write(data)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def quantised_share(a):
    """How much of the art is already 2x2 blocks — the evidence the downsample is lossless."""
    bad = tot = 0
    for y in range(0, a.shape[0] - 1, 2):
        for x in range(0, a.shape[1] - 1, 2):
            blk = a[y:y + 2, x:x + 2].reshape(4, -1)
            tot += 1
            if not np.all(blk == blk[0]):
                bad += 1
    return 1.0 - bad / float(max(tot, 1))


def downsample(im):
    """2:1 by SAMPLING, never by averaging — §4.3 forbids an authored sub-pixel gradient."""
    a = np.asarray(im, dtype=np.uint8)
    return Image.fromarray(a[::DEVICE, ::DEVICE].copy(), "RGBA")


def cut(im, w, h):
    """Row-major cells, exactly what DungeonRenderer's TileLayout indexes."""
    assert im.size == (w * NATIVE, h * NATIVE), \
        "sprite is %s, expected %s" % (im.size, (w * NATIVE, h * NATIVE))
    cells = []
    for row in range(h):
        for col in range(w):
            box = (col * NATIVE, row * NATIVE, (col + 1) * NATIVE, (row + 1) * NATIVE)
            cells.append(im.crop(box))
    return cells


def selftest():
    """§13.5 for the cut: a numbered probe proves row-major, and column-major would fail it."""
    w, h = 2, 2
    probe = Image.new("RGBA", (w * NATIVE, h * NATIVE), (0, 0, 0, 255))
    px = probe.load()
    for row in range(h):
        for col in range(w):
            v = row * w + col + 1          # cell index, 1..4, row-major
            for y in range(row * NATIVE, (row + 1) * NATIVE):
                for x in range(col * NATIVE, (col + 1) * NATIVE):
                    px[x, y] = (v * 40, 0, 0, 255)
    cells = cut(probe, w, h)
    got = [int(np.asarray(c)[0, 0, 0] / 40) for c in cells]
    want = [1, 2, 3, 4]
    ok = got == want
    print("  cut selftest: got %s, want %s -> %s" % (got, want, "OK" if ok else "*** WRONG ***"))
    if not ok:
        return 1
    # and the mutation: column-major on the same probe must NOT match
    colmajor = []
    for col in range(w):
        for row in range(h):
            colmajor.append(int(np.asarray(
                probe.crop((col * NATIVE, row * NATIVE,
                            (col + 1) * NATIVE, (row + 1) * NATIVE)))[0, 0, 0] / 40))
    print("  the mutation (column-major) gives %s -> %s"
          % (colmajor, "correctly differs" if colmajor != want else "*** INDISTINGUISHABLE ***"))
    return 0 if colmajor != want else 1


def land(plan_path):
    plan = json.load(open(plan_path))
    out = []
    for item in plan["props"]:
        cache = os.path.join(HERE, "gen", plan["wave"], item["key"] + ".png")
        im = fetch(item["url"], cache)
        a = np.asarray(im.convert("RGB"), dtype=int)
        share = quantised_share(a)
        native = downsample(im)
        w, h = item["w"], item["h"]
        cells = cut(native, w, h)

        ids, opaque = [], []
        for i, c in enumerate(cells):
            tid = item["ids"][i]
            p = os.path.join(DEST, "tier1_ashlar_%d.png" % tid)
            c.save(p)
            arr = np.asarray(c)
            opaque.append(float((arr[:, :, 3] > 0).mean()))
            ids.append(tid)
            sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
            print("    cell %d -> id %d  %s  opaque %.3f  sha %s"
                  % (i, tid, os.path.basename(p), opaque[-1], sha[:12]))

        full = float((np.asarray(native)[:, :, 3] > 0).mean())
        print("  %-11s %dx%d cells, sprite %s, 2x2-uniform %.1f%%, OPAQUE FRACTION %.3f"
              % (item["key"], w, h, native.size, 100 * share, full))
        out.append(dict(key=item["key"], w=w, h=h, ids=ids,
                        opaque_fraction=round(full, 4),
                        per_cell_opaque=[round(v, 4) for v in opaque],
                        quantised_share=round(share, 4), source=item["url"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.plan:
        print("--plan is required (or --selftest)", file=sys.stderr)
        return 2
    print("LANDING props at readability scale (§12.2)\n")
    if selftest():
        print("  cut selftest FAILED — refusing to land", file=sys.stderr)
        return 1
    print()
    res = land(a.plan)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=2)
        print("\n  wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
