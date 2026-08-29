#!/usr/bin/env python3
"""IS THE PATH SIGNAL ABOVE THE PERCEPTUAL FLOOR? — the traffic delta, in delivered units.

`measure_traffic_read.py` answers a DIRECTION question: is a trodden stone smoother than a
sheltered one, yes or no. It answered yes — 0.901, the lever pushing the right way. The blind
seat then read the same capture and said *"the ground told me nothing, I routed entirely off the
walls,"* and the two are not in conflict. A ratio has no size.

This file asks the size question, and it asks it in the only units that matter: **what a viewer
receives at 1:1 after the rig has multiplied everything down.** §13.8 is the law it applies —
*a signal authored below the perceptual floor is absent* — and the ruled floor is a Weber
contrast of 0.144, derived from the gate's own two verdicts.

Two channels are measured, because a path can announce itself two ways and neither is assumed:

    VALUE      a lane that is darker or lighter than the ground beside it. Measured on the
               LAMP-FLATTENED capture, so a bright patch of torchlight is not mistaken for a
               worn one — this is the mistake the seat itself flagged when it noted its own
               detail-density gap was "lighting, not surface."
    TEXTURE    a lane that is smoother or rougher than the ground beside it. Measured as local
               standard deviation, and then — the step the direction instrument skips —
               converted to a Weber contrast so it can be compared against the SAME floor.

Both are reported against 0.144. A number below it is not a weak signal; under §13.8 it is an
absent one, and no amount of pushing the same lever reaches it.
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
import field_laws as FL                  # noqa: E402
import measure_perceptual_floor as MPF   # noqa: E402
import measure_traffic_read as MTR       # noqa: E402

# The floor is re-derived in Weber space in the same way §13.8 derives it: the geometric mean of
# a signal the gate called excellent and one it called absent.
FLOOR = 0.144


# THE LAMP AND THE LANE ARE ON DIFFERENT SCALES, and that is the only reason this can be
# measured at all. Ruling 56 put the rig's falloff radius at 5.0 tiles, so illumination varies
# over ~320 screen px; a worn lane is one to two tiles, ~64-128 px. Dividing by a blur wider than
# the lamp but narrower than nothing removes the first and keeps the second.
#
# `measure_perceptual_floor` flattens at radius 30 because it judges MATERIAL, where killing
# every structure bigger than a tile is exactly right. Reusing that radius here would divide the
# lane out of the image and then report, with perfect confidence, that there is no lane.
LAMP_RADIUS = 200


def bands(capture, log, tile, plant=None):
    """Per traffic level: lamp-corrected mean value, and local roughness, over lit floor pixels."""
    f = MTR.read_field(log)
    if f is None:
        raise SystemExit("no traffic field in the log")
    img = np.asarray(Image.open(capture).convert("RGB")).astype(float)
    L = MPF.lum(img)
    H, W = L.shape
    fh, fw = f.shape
    oy, ox = (H - fh * tile) // 2, (W - fw * tile) // 2

    # The lit mask comes from the UNPLANTED image, always. Deriving it after the plant lets the
    # plant delete its own darkest tiles from the sample and then take credit for the difference.
    lit = L > 60

    if plant is not None:
        # THE PLANT. A lane of known amplitude, painted straight onto the delivered capture at
        # the tiles the field itself calls trodden. If the instrument cannot see a delta it was
        # handed, it cannot be trusted to report one it was not. (LOOP-PROCESS §4.)
        for ty in range(fh):
            for tx in range(fw):
                if f[ty, tx] >= 7:
                    y0, x0 = oy + ty * tile, ox + tx * tile
                    L[y0:y0 + tile, x0:x0 + tile] *= (1.0 - plant)

    flat = L / np.maximum(MPF.box_blur(L, LAMP_RADIUS), 1e-6) * float(np.median(L[lit]))
    from numpy.lib.stride_tricks import sliding_window_view
    sd = sliding_window_view(flat, (3, 3)).std(axis=(2, 3))

    out = {}
    for ty in range(fh):
        for tx in range(fw):
            lvl = int(f[ty, tx])
            if lvl < 0:
                continue
            y0, x0 = oy + ty * tile, ox + tx * tile
            if y0 < 1 or x0 < 1 or y0 + tile > H - 1 or x0 + tile > W - 1:
                continue
            m = lit[y0:y0 + tile, x0:x0 + tile][1:-1, 1:-1]
            if m.sum() < 200:
                continue
            v = flat[y0:y0 + tile, x0:x0 + tile][1:-1, 1:-1]
            r = sd[y0 - 1:y0 + tile - 1, x0 - 1:x0 + tile - 1][:m.shape[0], :m.shape[1]]
            out.setdefault(lvl, []).append((float(v[m].mean()), float(r[m].mean())))
    return out


def weber(a, b):
    """Symmetric Weber contrast between two region means — |a-b| over the common ground."""
    base = (a + b) / 2.0
    return abs(a - b) / base if base else 0.0


def report(bk, label):
    rows = []
    for lvl in sorted(bk):
        vs = bk[lvl]
        rows.append((lvl, len(vs),
                     float(np.mean([x[0] for x in vs])),
                     float(np.mean([x[1] for x in vs]))))
    quiet = [r for r in rows if r[0] <= 2]
    busy = [r for r in rows if r[0] >= 7]
    if not (quiet and busy):
        raise SystemExit("the scene has no trodden and sheltered ground to compare")

    def wmean(sel, i):
        return sum(r[i] * r[1] for r in sel) / sum(r[1] for r in sel)

    qv, bv = wmean(quiet, 2), wmean(busy, 2)
    qr, br = wmean(quiet, 3), wmean(busy, 3)
    wv, wr = weber(qv, bv), weber(qr, br)

    print("\n%s" % label)
    print("  %-8s %6s %12s %12s" % ("traffic", "tiles", "value(flat)", "roughness"))
    for lvl, n, v, r in rows:
        print("  %-8s %6d %12.2f %12.3f" % (MTR.RAMP[lvl] * 3, n, v, r))
    print()
    print("  off-route (0-2)   value %7.2f   roughness %6.3f   over %d tiles"
          % (qv, qr, sum(r[1] for r in quiet)))
    print("  trodden   (7-9)   value %7.2f   roughness %6.3f   over %d tiles"
          % (bv, br, sum(r[1] for r in busy)))
    print()
    print("  WEBER CONTRAST OF THE PATH, AS DELIVERED")
    print("    value channel     %.4f   %s" % (wv, "ABOVE" if wv >= FLOOR else "below"))
    print("    texture channel   %.4f   %s" % (wr, "ABOVE" if wr >= FLOOR else "below"))
    print("    the ruled floor   %.4f   (§13.8)" % FLOOR)
    return dict(value_weber=round(wv, 4), texture_weber=round(wr, 4),
                off_value=round(qv, 3), trodden_value=round(bv, 3),
                off_rough=round(qr, 4), trodden_rough=round(br, 4),
                levels=[dict(level=l, tiles=n, value=round(v, 3), roughness=round(r, 4))
                        for l, n, v, r in rows])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--tile", type=int, default=64)
    ap.add_argument("--plant", type=float, default=0.20,
                    help="control: darken every trodden tile by this fraction and re-measure")
    a = ap.parse_args()

    real = report(bands(a.capture, a.log, a.tile), "AS SHIPPED")
    ctrl = report(bands(a.capture, a.log, a.tile, plant=a.plant),
                  "THE PLANT — every trodden tile darkened %.0f%%" % (a.plant * 100))

    print()
    if ctrl["value_weber"] > real["value_weber"] + 0.05:
        print("  PLANT CAUGHT: %.4f -> %.4f. The instrument can see a path when there is one."
              % (real["value_weber"], ctrl["value_weber"]))
        ok = True
    else:
        print("  PLANT MISSED: %.4f -> %.4f. This instrument proves nothing today."
              % (real["value_weber"], ctrl["value_weber"]))
        ok = False

    out = dict(commit=FL.git_commit(), capture=os.path.relpath(a.capture, REPO),
               floor=FLOOR, shipped=real, plant=ctrl, plant_caught=ok)
    p = os.path.join(HERE, "evidence", "PATH-SIGNAL.json")
    json.dump(out, open(p, "w"), indent=1)
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
