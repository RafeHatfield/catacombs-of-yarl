#!/usr/bin/env python3
"""WHAT SHARE OF THE DELIVERED FLOOR VALUE IS THE SPECULAR — by range band.

Issue #184 asks for this figure to be RE-TAKEN before the gain is touched, and says why: the last
one (10.8% / 12.6% / 0.0%) was measured on the pre-#174 lamp and on the pre-re-ratification rig,
and §6.2's re-derivation rule has fired twice since. A share carried across a rig change is a
number that describes a room nobody is standing in any more.

It is a DIFFERENCE against the null-polish arm, not an estimate from the mask: `polish_gain 0`
removes the specular term and nothing else, so `(arm - null) / arm` is exactly what the term
contributes to the pixel that was delivered. That is the same control #184 asks to ship with the
fix, used as the measurement rather than only as a demonstration.

    measure_specular_share.py <arm-stem> --null <null-stem>

Bands are distance from the PLAYER in tiles, and the player and the tile origin both come from
the engine's own log (§13.10) rather than from an assumption about where the camera is.
"""
import argparse
import json
import os
import re
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
LIT = 40                     # below this nothing is being judged (§8.2.1, dark is by design)
BANDS = ((0.0, 2.0), (2.0, 4.0), (4.0, 99.0))
PLAYER_RE = re.compile(r"player=\((\d+),(\d+)\)")


def player_of(log):
    """The station, from the log if the engine printed it, else from the scene spec it names."""
    txt = open(log).read()
    m = PLAYER_RE.search(txt)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"--corridor-scene res://(\S+\.json)", txt)
    if not m:
        return None
    d = json.load(open(os.path.join(REPO, m.group(1))))
    return d["player"]["x"], d["player"]["y"]


def tiles(png, log):
    L = MPF.lum(np.asarray(Image.open(png).convert("RGB")).astype(float))
    f = MTR.read_field(log)
    o = MTR.tile_origin(log)
    p = player_of(log)
    if f is None or o is None or p is None:
        return None
    ox, oy = o
    H, W = L.shape
    out = {}
    for ty in range(f.shape[0]):
        for tx in range(f.shape[1]):
            if int(f[ty, tx]) < 0:
                continue
            y0, x0 = oy + ty * T, ox + tx * T
            if y0 < 0 or x0 < 0 or y0 + T > H or x0 + T > W:
                continue
            out[(tx, ty)] = float(np.mean(L[y0:y0 + T, x0:x0 + T]))
    return out, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arms", nargs="+")
    ap.add_argument("--null", required=True, help="the polish_gain 0 arm")
    a = ap.parse_args()

    def load(stem):
        png = os.path.join(HERE, "evidence", stem + ".png")
        log = os.path.join(HERE, "evidence", stem + ".log")
        if not (os.path.exists(png) and os.path.exists(log)):
            return None
        return tiles(png, log)

    nul = load(a.null)
    if nul is None:
        raise SystemExit("null arm %s has no capture" % a.null)
    nmap, p = nul

    print("THE SPECULAR'S SHARE OF DELIVERED FLOOR VALUE — (arm - null)/arm, null = %s\n" % a.null)
    print("  %-16s %-10s %5s %10s %10s %9s %10s"
          % ("arm", "band", "n", "arm mean", "null mean", "share", "worst cell"))
    out = {}
    for stem in a.arms:
        r = load(stem)
        if r is None:
            print("  %-16s (missing capture)" % stem)
            continue
        amap, _ = r
        rows = {}
        for lo, hi in BANDS:
            got = []
            for k, av in amap.items():
                d = max(abs(k[0] - p[0]), abs(k[1] - p[1]))
                if not (lo <= d < hi) or k not in nmap:
                    continue
                if av < LIT:
                    continue
                got.append((av, nmap[k], k))
            if not got:
                print("  %-16s %-10s (no lit cell)" % (stem, "%.0f-%.0f" % (lo, hi)))
                continue
            am = float(np.mean([g[0] for g in got]))
            nm = float(np.mean([g[1] for g in got]))
            # THE WORST CELL, every band. A mean share hides the tile carrying the most shine,
            # and that tile is the one a seat calls a flat pale block.
            worst = max(got, key=lambda g: (g[0] - g[1]) / max(g[0], 1e-6))
            ws = (worst[0] - worst[1]) / max(worst[0], 1e-6)
            share = (am - nm) / max(am, 1e-6)
            rows["%.0f-%.0f" % (lo, hi)] = dict(
                n=len(got), arm_mean=round(am, 2), null_mean=round(nm, 2),
                share=round(share, 4), worst_share=round(ws, 4), worst_cell=list(worst[2]))
            print("  %-16s %-10s %5d %10.2f %10.2f %8.1f%% %5.1f%% @%s"
                  % (stem, "%.0f-%.0f" % (lo, hi), len(got), am, nm,
                     100 * share, 100 * ws, worst[2]))
        out[stem] = rows
    p_out = os.path.join(HERE, "evidence", "SPECULAR-SHARE.json")
    json.dump(dict(commit=FL.git_commit(), null=a.null, station=list(p), arms=out),
              open(p_out, "w"), indent=1)
    print("\n  written: %s" % os.path.relpath(p_out, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
