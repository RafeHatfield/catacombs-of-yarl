#!/usr/bin/env python3
"""DOES THE WEAR KNOW WHERE THE TILES ARE? — it must not.

RULED at the gate: *"one tile worn, the one next to it not — that's not how it works."*

    WEAR IGNORES THE TILE GRID. ANY WEAR BOUNDARY COINCIDING WITH A TILE EDGE IS STAGED.

The test is a chance test, which is the only honest shape for it. A wear boundary has to fall
somewhere, and some of it will land on tile edges by luck — a 64px tile puts 6.2% of its pixels
within one of an edge, so a boundary that ignores the grid should put about 6.2% of itself there
too. Anything well above that is the grid showing through, and the number says how much.

Measured on the FIELD THE PAINTERS ACTUALLY READ, evaluated per pixel: the wear age at every
pixel, the boundary being where that age changes. The lane's edge is the largest of those
boundaries and the one the gate saw.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_ashlar as CA      # noqa: E402
import field_laws as FL          # noqa: E402
import route_polyline as RP      # noqa: E402


def edge_on_grid(w, h, seed, band=1, channel=None):
    """Share of wear-age boundary pixels that sit within `band` px of a tile edge.

    `channel` reproduces the defect: a PER-TILE predicate that raises the whole tile's wear to a
    floor, which is what the channel flag did to the joints, the chroma and the flatten alike
    until it was gated. It is the control arm — the instrument has to show it can see the thing it
    was built to forbid.
    """
    T = CA.T
    age = np.zeros((h * T, w * T), dtype=int)
    for ty in range(h):
        for tx in range(w):
            blk = CA.wear01_block(CA.wear_scalar_block(tx * T, ty * T, T, seed, None),
                                  bool(channel and channel(tx, ty)))
            ages = np.array(CA.WEAR_AGES)
            age[ty * T:(ty + 1) * T, tx * T:(tx + 1) * T] = \
                np.abs(blk[..., None] - ages).argmin(-1)

    # a boundary pixel is one whose age differs from a 4-neighbour's
    b = np.zeros(age.shape, bool)
    b[:-1, :] |= age[:-1, :] != age[1:, :]
    b[1:, :] |= age[:-1, :] != age[1:, :]
    b[:, :-1] |= age[:, :-1] != age[:, 1:]
    b[:, 1:] |= age[:, :-1] != age[:, 1:]

    yy, xx = np.mgrid[0:h * T, 0:w * T]
    on = (np.minimum(yy % T, T - 1 - (yy % T)) < band) | \
         (np.minimum(xx % T, T - 1 - (xx % T)) < band)
    chance = float(on.mean())
    if b.sum() == 0:
        return None
    return dict(boundary_px=int(b.sum()), on_grid=round(float(on[b].mean()), 4),
                chance=round(chance, 4),
                ratio=round(float(on[b].mean()) / max(chance, 1e-9), 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=12)
    ap.add_argument("--h", type=int, default=12)
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()

    route = [(a.w // 2, y) for y in range(1, a.h - 1)]
    line = [(RP.jitter(RP.smooth(route),
                       lambda x, y: 0 <= x < a.w and 0 <= y < a.h, a.seed), 1.0)]

    print("DOES THE WEAR KNOW WHERE THE TILES ARE?\n")
    print("  A wear boundary must land on tile edges no more often than chance. At %dpx tiles"
          % CA.T)
    print("  chance is about 6%%; a boundary drawn on the grid runs far above it.\n")
    print("  %-34s %12s %10s %10s %8s"
          % ("configuration", "boundary px", "on grid", "chance", "ratio"))
    out = {}
    keep = CA.LINES
    try:
        band = a.w // 2
        for label, lines, ch in (
                ("no route model (noise only)", [], None),
                ("with the route polyline", line, None),
                ("THE CONTROL: a per-tile channel flag", line,
                 lambda tx, ty: band - 1 <= tx <= band)):
            CA.LINES = lines
            r = edge_on_grid(a.w, a.h, a.seed, channel=ch)
            out[label] = r
            if r is None:
                print("  %-34s (no boundary)" % label)
                continue
            print("  %-34s %12d %9.1f%% %9.1f%% %7.2fx"
                  % (label, r["boundary_px"], 100 * r["on_grid"], 100 * r["chance"], r["ratio"]))
    finally:
        CA.LINES = keep
    print("\n  A ratio near 1.00 is a wear field that does not know the grid exists. The control")
    print("  is the defect the gate saw, restored on purpose: a per-tile flag whose boundary can")
    print("  only ever be a tile edge. If it does not run high, this instrument proves nothing.")
    p = os.path.join(HERE, "evidence", "WEAR-GRID-LOCK.json")
    json.dump(dict(commit=FL.git_commit(), results=out), open(p, "w"), indent=1)
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
