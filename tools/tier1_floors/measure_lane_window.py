#!/usr/bin/env python3
"""THE LANE'S TARGET WINDOW — both halves, on the delivered frame, at once.

RULED (Rafe, 2026-09-02) at the gate that accepted the keyline fix and culled the lane:

    "it looks like all the tiles on the walked path have been replaced."

    WEAR MODULATES THE SAME STONES; IT NEVER REPLACES THEIR IDENTITY. A path you cannot
    recognise as the same masonry is a decal.

That is a law about a PAIR, and it is why one number was never going to hold the lane. Push the
specular up and the lane separates beautifully from its flanks while the stones inside it wash out
into one bright slab — a decal that measures well. Push it down and the masonry survives while the
lane says nothing. Only both together describe a floor that is worn rather than re-laid, so both
are measured here, simultaneously, and the target is a WINDOW rather than a threshold:

    ON-LANE LEGIBILITY   inside the lane, the joints and the texture must still read.
    LANE-VS-FLANK        the lane must still differ from the ground beside it.

Both in Weber contrast, both against §13.8's ruled floor of 0.144, both on the delivered frame at
the standing station — §13.9's converse: source-clean is necessary and not sufficient.
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

T = 64
FLOOR = 0.144
LIT = 60          # a tile below this is not being judged; dark illegibility is design


def tiles(png, log):
    L = MPF.lum(np.asarray(Image.open(png).convert("RGB")).astype(float))
    f = MTR.read_field(log)
    if f is None:
        return None
    H, W = L.shape
    fh, fw = f.shape
    # THE ORIGIN COMES FROM THE ENGINE, NEVER FROM AN ASSUMPTION OF CENTRING. The camera
    # follows the player; a centred formula was 160px out in x on the standing station and
    # every delivered reading taken through it sampled the wrong tiles.
    ox, oy = MTR.tile_origin(log) or ((W - fw * T) // 2, (H - fh * T) // 2)
    out = []
    for ty in range(fh):
        for tx in range(fw):
            lv = int(f[ty, tx])
            if lv < 0:
                continue
            y0, x0 = oy + ty * T, ox + tx * T
            if y0 < 0 or x0 < 0 or y0 + T > H or x0 + T > W:
                continue
            blk = L[y0:y0 + T, x0:x0 + T]
            if np.median(blk) < LIT:
                continue
            out.append((lv, blk))
    return out


def measure(png, log):
    ts = tiles(png, log)
    if not ts:
        return None
    lane = [b for lv, b in ts if lv >= 7]
    flank = [b for lv, b in ts if lv <= 4]
    if not lane or not flank:
        return None

    # ON-LANE LEGIBILITY, ON THE HIGH-FREQUENCY RESIDUAL ONLY.
    #
    # ⚠ NOT THE RAW SPREAD. The first version took p80 against p20 of the tile's luminance and
    # scored 0.383 on the very frame the gate culled as washed slabs — because a specular lane
    # lays a bright RAMP across each tile, and a ramp has a large spread. It was counting the
    # wash as legibility. The masonry is the HIGH-FREQUENCY part: joints two pixels wide, dressing
    # marks, the crack. So the tile's own smooth level is subtracted first and what remains is
    # measured against it.
    def spread(b):
        blur = MPF.box_blur(b, 4)
        res = b - blur
        hi, lo = np.percentile(res, 80), np.percentile(res, 20)
        return float((hi - lo) / max(float(np.median(b)), 1e-6))

    on_lane = float(np.mean([spread(b) for b in lane]))
    on_flank = float(np.mean([spread(b) for b in flank]))

    # LANE VS FLANK. The lane's own level against the ground beside it.
    lm = float(np.mean([b.mean() for b in lane]))
    fm = float(np.mean([b.mean() for b in flank]))
    delta = abs(lm - fm) / max((lm + fm) / 2, 1e-6)

    # THE LAW'S OWN NUMBER: does the lane read as the SAME masonry? Both halves can clear the
    # floor while the lane is quietly losing its stones to the wash, which is what a decal is.
    identity = on_lane / max(on_flank, 1e-6)

    return dict(identity_ratio=round(identity, 3),
                lane_tiles=len(lane), flank_tiles=len(flank),
                on_lane_legibility=round(on_lane, 4),
                on_flank_legibility=round(on_flank, 4),
                lane_vs_flank=round(delta, 4),
                lane_mean=round(lm, 1), flank_mean=round(fm, 1),
                in_window=bool(on_lane >= FLOOR and delta >= FLOOR))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stems", nargs="+")
    a = ap.parse_args()
    print("THE LANE'S TARGET WINDOW — both halves must clear §13.8's %.3f, together\n" % FLOOR)
    print("  %-24s %10s %8s %12s %10s %8s"
          % ("capture", "on-lane", "x floor", "lane-vs-flank", "identity", "window"))
    out = {}
    for stem in a.stems:
        png = os.path.join(HERE, "evidence", stem + ".png")
        log = os.path.join(HERE, "evidence", stem + ".log")
        if not (os.path.exists(png) and os.path.exists(log)):
            continue
        r = measure(png, log)
        if r is None:
            print("  %-24s (no lit lane and flank to compare)" % stem)
            continue
        out[stem] = r
        print("  %-24s %9.4f%s %7.2f %11.4f%s %10.3f %8s"
              % (stem,
                 r["on_lane_legibility"], " " if r["on_lane_legibility"] >= FLOOR else "!",
                 r["on_lane_legibility"] / FLOOR,
                 r["lane_vs_flank"], " " if r["lane_vs_flank"] >= FLOOR else "!",
                 r["identity_ratio"],
                 "IN" if r["in_window"] else "out"))
    print("\n  ! marks the half that is below the floor. The flank reference is what the same")
    print("  masonry reads at OFF the lane — the lane should not be far below it.")
    p = os.path.join(HERE, "evidence", "LANE-WINDOW.json")
    json.dump(dict(commit=FL.git_commit(), floor=FLOOR, captures=out), open(p, "w"), indent=1)
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
