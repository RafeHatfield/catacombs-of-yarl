#!/usr/bin/env python3
"""GRID COINCIDENCE — does ANY treatment boundary lie on the tile edges?

RULED as a standing instrument: *the ban's question, not its history.* Every ring instrument
before this one asked about the shape the ring had last time it was caught — a value step at the
boundary, a lattice, a constant-pitch line — and each went green while the next form of the same
ban walked past it. This asks the question itself:

    WEAR IGNORES THE TILE GRID. ANY WEAR OR TREATMENT BOUNDARY COINCIDING WITH A TILE EDGE IS
    STAGED.

CHANCE IS THE GATE, not zero. A boundary has to fall somewhere and some of it lands on tile edges
by luck: at 32px tiles a one-pixel band is about 12% of the surface, so an honest boundary puts
about 12% of itself there. The number reported is the RATIO to chance, and ~1.00 is the pass.

EVERY TREATMENT, not just the one that was caught. The wear age drives the joints, the flatten and
the chroma; the lane drives the polish and the dish; the grit has its own band. Each is evaluated
per pixel, its boundary extracted, and its coincidence measured separately — because a single
pooled number would let one grid-locked treatment hide inside four clean ones.
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

PASS_RATIO = 1.35   # above this, the grid is showing through


def boundary(field):
    """Pixels whose value differs from a 4-neighbour's."""
    b = np.zeros(field.shape, bool)
    d = field[:-1, :] != field[1:, :]
    b[:-1, :] |= d
    b[1:, :] |= d
    d = field[:, :-1] != field[:, 1:]
    b[:, :-1] |= d
    b[:, 1:] |= d
    return b


def coincidence(b, w, h, band=1):
    T = CA.T
    yy, xx = np.mgrid[0:h * T, 0:w * T]
    on = (np.minimum(yy % T, T - 1 - (yy % T)) < band) | \
         (np.minimum(xx % T, T - 1 - (xx % T)) < band)
    chance = float(on.mean())
    if b.sum() == 0:
        return None
    return dict(boundary_px=int(b.sum()), on_grid=round(float(on[b].mean()), 4),
                chance=round(chance, 4),
                ratio=round(float(on[b].mean()) / max(chance, 1e-9), 3))


def treatments(w, h, seed, channel=None):
    """Every treatment's own per-pixel field, keyed the way the painters key it."""
    T = CA.T
    ages = np.array(CA.WEAR_AGES)
    wear = np.zeros((h * T, w * T), dtype=int)
    axis = np.zeros((h * T, w * T), dtype=int)
    lane = np.zeros((h * T, w * T), dtype=int)
    dish = np.zeros((h * T, w * T), dtype=int)
    grit = np.zeros((h * T, w * T), dtype=int)
    for ty in range(h):
        for tx in range(w):
            sl = (slice(ty * T, (ty + 1) * T), slice(tx * T, (tx + 1) * T))
            blk = CA.wear01_block(CA.wear_scalar_block(tx * T, ty * T, T, seed, None),
                                  bool(channel and channel(tx, ty)))
            wear[sl] = np.abs(blk[..., None] - ages).argmin(-1)
            axis[sl] = CA.axis_block(tx * T, ty * T, T)
            d, _tx, _ty = CA.line_geometry_block(tx * T, ty * T, T)
            # quantised the way each treatment quantises, so the boundary is the one drawn
            lane[sl] = np.round(np.clip((CA.POLISH_SHOULDER - d) / CA.POLISH_SHOULDER, 0, 1) * 6)
            dish[sl] = np.round(np.clip(1.0 - d / CA.POLISH_SHOULDER, 0, 1) * 4)
            grit[sl] = ((d > CA.GRIT_INNER) & (d < CA.GRIT_OUTER)).astype(int)
    return dict(wear_age=wear, travel_axis=axis, specular_lane=lane,
                lane_dish=dish, margin_grit=grit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=12)
    ap.add_argument("--h", type=int, default=12)
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()

    route = [(a.w // 2, y) for y in range(1, a.h - 1)]
    line = [(RP.jitter(RP.smooth(route),
                       lambda x, y: 0 <= x < a.w and 0 <= y < a.h, a.seed), 1.0)]

    print("GRID COINCIDENCE — does any treatment boundary lie on the tile edges?\n")
    print("  Chance is the gate, not zero: a boundary has to fall somewhere. Pass is a ratio")
    print("  at or below %.2f. Every treatment is measured SEPARATELY, so a grid-locked one" % PASS_RATIO)
    print("  cannot hide inside four clean ones.\n")
    print("  %-18s %12s %10s %10s %8s %6s"
          % ("treatment", "boundary px", "on grid", "chance", "ratio", ""))

    keep = CA.LINES
    out, ok = {}, True
    try:
        CA.LINES = line
        for name, f in treatments(a.w, a.h, a.seed).items():
            r = coincidence(boundary(f), a.w, a.h)
            if r is None:
                continue
            good = r["ratio"] <= PASS_RATIO
            ok = ok and good
            out[name] = dict(r, pass_=good)
            print("  %-18s %12d %9.1f%% %9.1f%% %7.2fx %6s"
                  % (name, r["boundary_px"], 100 * r["on_grid"], 100 * r["chance"],
                     r["ratio"], "ok" if good else "GRID"))

        # THE CONTROL. A per-tile flag, which is the defect in its purest form: its boundary can
        # only ever be a tile edge. If this does not run high the instrument proves nothing.
        band = a.w // 2
        ctl = treatments(a.w, a.h, a.seed,
                         channel=lambda tx, ty: band - 1 <= tx <= band)["wear_age"]
        rc = coincidence(boundary(ctl), a.w, a.h)
        print("\n  %-18s %12d %9.1f%% %9.1f%% %7.2fx %6s"
              % ("CONTROL per-tile", rc["boundary_px"], 100 * rc["on_grid"],
                 100 * rc["chance"], rc["ratio"], "fires" if rc["ratio"] > PASS_RATIO else "SILENT"))
        if rc["ratio"] <= PASS_RATIO:
            print("  ^^ the control did not fire; this instrument's pass does not count today.")
            ok = False
    finally:
        CA.LINES = keep

    print("\n  VERDICT: %s" % ("every treatment is at chance" if ok else "A TREATMENT IS ON THE GRID"))
    p = os.path.join(HERE, "evidence", "GRID-COINCIDENCE.json")
    json.dump(dict(commit=FL.git_commit(), pass_ratio=PASS_RATIO, treatments=out,
                   control=rc, verdict=ok), open(p, "w"), indent=1)
    print("  written: %s" % os.path.relpath(p, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
