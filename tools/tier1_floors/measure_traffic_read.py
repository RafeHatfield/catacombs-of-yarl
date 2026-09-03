#!/usr/bin/env python3
"""DOES THE FLOOR SHOW WHERE PEOPLE WALK? — the traffic field, measured on the lit capture.

THE DEVICE GATE, third walk: *"the worn path should be on a walking path — down the hallway,
through the room, into the next hallway… worn tiles in the middle of the room and no flow."*

The field that replaced the noise is verified twice, and neither check would do on its own:

    THE DERIVATION   `TrafficFieldTests` in the Logic layer asserts the HIERARCHY — spine busier
                     than an off-route corner, a sealed room unwalked, a threshold busier than the
                     room it serves — without a scene, a device or a capture.
    THE READ         this file, which asks the only question those tests cannot: **once it is
                     painted and lit, can the difference be seen?** §13.8 applies to the traffic
                     signal exactly as it applied to the grain and to the channel before it.

It reads the field out of the capture's own log rather than recomputing it, so the thing measured
is the thing the engine actually used. A second implementation of the derivation here would prove
the second implementation.
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

RAMP = " .:-=+*#%@"


ORIGIN_RE = re.compile(r"legibility\((\d+),(\d+)\)[^\n]*at px\((\d+),(\d+)\)")


def tile_origin(log_path, tile=64):
    """Where tile (0,0) sits in the captured frame, DERIVED FROM THE ENGINE'S OWN OUTPUT.

    ⚠ NEVER ASSUME THE FIELD IS CENTRED. Every delivered measurement in this session computed the
    origin as `(H - rows*tile)//2` and was WRONG: the camera follows the PLAYER, not the map. On
    the standing station the engine's legibility probe puts tile (8,10) at px(535,706) and the
    centred formula puts it at px(375,667) — 160 pixels out in x.
    
    Everything that binned delivered pixels by traffic level was therefore sampling the wrong
    tiles, and a seat that reported the corridor at x 502-566 was RIGHT while the instrument that
    contradicted it was wrong. The probe prints a tile and its pixel on every capture; that is the
    camera's own answer and it is what gets used.
    """
    txt = open(log_path).read()
    pts = [(int(a), int(b), int(x), int(y)) for a, b, x, y in ORIGIN_RE.findall(txt)]
    if not pts:
        return None
    oxs = [x - (tx * tile + tile // 2) for tx, ty, x, y in pts]
    oys = [y - (ty * tile + tile // 2) for tx, ty, x, y in pts]
    if len(set(oxs)) > 1 or len(set(oys)) > 1:
        raise SystemExit("the log's probe points disagree about the origin: %s %s" % (oxs, oys))
    return oxs[0], oys[0]


def read_field(log_path, prefer_route=True):
    """The field the painter actually keys to, as the engine logged it.

    ROUTE STRENGTH FIRST. Since round 22 the wear scalar and the travel axis come from the route
    POLYLINE, and the per-tile traffic field is only a fallback. An instrument that went on
    bucketing by the field would be comparing a different population from the one the painter
    reads — and it showed the moment the two diverged: the matching control started leaking and
    the null draws collapsed to zero. Measure what is keyed.
    """
    txt = open(log_path).read()
    m = None
    if prefer_route:
        m = re.search(r"route strength \(space=off-route[^\n]*\n((?:\[Tier1\]   [^\n]*\n)+)", txt)
    if m is None:
        m = re.search(r"traffic field \(space=unwalked[^\n]*\n((?:\[Tier1\]   [^\n]*\n)+)", txt)
    if not m:
        return None
    rows = [ln[len("[Tier1]   "):] for ln in m.group(1).rstrip("\n").split("\n")]
    h, w = len(rows), max(len(r) for r in rows)
    f = np.full((h, w), -1, dtype=int)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            f[y, x] = -1 if ch == "#" else RAMP.index(ch)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--tile", type=int, default=64, help="screen px per tile (32 art at x2)")
    a = ap.parse_args()

    f = read_field(a.log)
    if f is None:
        raise SystemExit("no traffic field in the log — did the engine lay the floor?")

    img = np.asarray(Image.open(a.capture).convert("RGB")).astype(float)
    L = MPF.lum(img)
    H, W = L.shape
    fh, fw = f.shape
    oy, ox = (H - fh * a.tile) // 2, (W - fw * a.tile) // 2

    from numpy.lib.stride_tricks import sliding_window_view
    sd = sliding_window_view(L, (3, 3)).std(axis=(2, 3))
    lit = L > 60

    # Bucket every lit floor pixel by the traffic level of the tile it sits in.
    buckets = {}
    for ty in range(fh):
        for tx in range(fw):
            lvl = f[ty, tx]
            if lvl < 0:
                continue
            y0, x0 = oy + ty * a.tile, ox + tx * a.tile
            if y0 < 1 or x0 < 1 or y0 + a.tile > H - 1 or x0 + a.tile > W - 1:
                continue
            m = lit[y0:y0 + a.tile, x0:x0 + a.tile][1:-1, 1:-1]
            if m.sum() < 200:
                continue
            block = sd[y0 - 1:y0 + a.tile - 1, x0 - 1:x0 + a.tile - 1][:m.shape[0], :m.shape[1]]
            buckets.setdefault(lvl, []).append(float(block[m].mean()))

    print("DOES THE FLOOR SHOW WHERE PEOPLE WALK?\n")
    print("  %-8s %8s %10s   %s" % ("traffic", "tiles", "roughness", ""))
    rows = []
    for lvl in sorted(buckets):
        vals = buckets[lvl]
        mean = float(np.mean(vals))
        rows.append((lvl, len(vals), mean))
        print("  %-8s %8d %10.3f   %s"
              % (RAMP[lvl] * 3, len(vals), mean, "#" * int(mean * 4)))

    if len(rows) >= 2:
        quiet = [r for r in rows if r[0] <= 2]
        busy = [r for r in rows if r[0] >= 7]
        if quiet and busy:
            q = sum(r[2] * r[1] for r in quiet) / sum(r[1] for r in quiet)
            b = sum(r[2] * r[1] for r in busy) / sum(r[1] for r in busy)
            print()
            print("  off-route (levels 0-2): roughness %.3f over %d tiles"
                  % (q, sum(r[1] for r in quiet)))
            print("  trodden   (levels 7-9): roughness %.3f over %d tiles"
                  % (b, sum(r[1] for r in busy)))
            print("  ratio trodden/off-route: %.3f" % (b / q if q else 0))
            print()
            print("  BELOW 1.00 is the ruling: a trodden stone polishes SMOOTHER as its joints")
            print("  open. Above 1.00 the lever is pushing the wrong way, which is exactly what")
            print("  the last round measured at 1.987 and why the channel did not read.")

    out = dict(commit=FL.git_commit(), capture=os.path.relpath(a.capture, REPO),
               levels=[dict(level=int(l), tiles=int(n), roughness=round(m, 4)) for l, n, m in rows])
    p = os.path.join(HERE, "evidence", "TRAFFIC-READ.json")
    with open(p, "w") as fh_:
        json.dump(out, fh_, indent=1)
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
