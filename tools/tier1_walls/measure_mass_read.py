#!/usr/bin/env python3
"""MASS-READ AT DISTANCE — the number the three remedies have to move, measured before any of them.

RULED at the gate: *"wall mass beats void by a readable margin (perceptual-floor law applies to
mass-vs-nothing)."* And separately, for the design thread: *"present your three named remedies
with delivered numbers at the standing case and at 3–4 tiles."*

Both need one quantity first, and it is not the one the session has been measuring. Every earlier
instrument here asked whether the wall's MATERIAL reads — its joints, its grain, its age. This
asks whether the wall READS AS MASS: can a person tell solid from not-solid, at a glance, without
walking into it. A blind seat put the failure exactly:

    *"at y=225, the 'solid wall' column at x=300 reads luminance 18. The open passage floor at
    x=405, same row, also reads 18. Identical. The renderer draws mass and void at the same
    brightness."*

THREE SEPARATIONS, all Weber, all on the capture, all reported by range:

    wall / void      is the mass distinguishable from the dark beyond it
    wall / floor     is the mass distinguishable from the ground you may walk on
    wall / passage   the seat's own comparison: a wall column against an open corridor column
                     at the same row, which is the question a player actually asks

The floor family's perceptual floor (0.1440) is carried as a REFERENCE, not a bound — §13.8
derives a floor from a human's ruled-present and ruled-absent pair, and no such pair exists for
mass-versus-nothing yet. The gate's new requirement is what will produce one.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(HERE, "evidence")
sys.path.insert(0, HERE)
import compose_walls as CW          # noqa: E402
import light_field as LF            # noqa: E402
import measure_wall_amplitude as MA  # noqa: E402
from mask_census import build        # noqa: E402

FLOOR_REFERENCE = 0.1440
# ── THE BAR, AND IT IS READ IN LEVELS ─────────────────────────────────────────────────────────
#
# RULED (Rafe, 2026-08-30): *"The perceptual-floor law reads in DELIVERED LEVELS, not ratios —
# 8 levels is 'barely met', and wall-vs-floor must clear the same bar after the material change;
# measure both."*
#
# So the bar is not picked here, and it is not invented: it is a human verdict on a measured
# quantity, which is the only way §13.8 permits a floor to come into existence. Eight levels is
# the AMBIGUOUS point — §13.8's own words about a signal that clears by a hair: *"that is the
# geometric midpoint between present and absent, which is precisely the ambiguous point."* The
# obligation the clause then imposes is to say where a signal sits relative to it and why it sits
# there rather than higher.
LEVELS_BAR = 8.0


def cell_mean(lum, g, x, y, inset=6):
    x0, y0, w, h = LF.cell_box(g, x, y)
    p = lum[int(y0) + inset:int(y0 + h) - inset, int(x0) + inset:int(x0 + w) - inset]
    return float(p.mean()) if p.size else None


def weber(a, b):
    """Signed Weber contrast of a against b, against whichever is brighter."""
    hi = max(a, b)
    return (a - b) / hi if hi > 1e-6 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--png", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--assets", default=os.path.join(REPO, CW.ASSETS_REL + "_compensated"))
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    man = json.load(open(os.path.join(a.assets, "MANIFEST.json")))
    pred = MA.predict(spec, man, MA.read_age_map(os.path.join(REPO, a.log)))
    wall, w, h = build(spec)
    img = np.array(Image.open(os.path.join(REPO, a.png)).convert("RGB")).astype(float)
    lum = (img * LF.W709).sum(2)
    g = LF.read_grid(os.path.join(REPO, a.log))
    px, py = spec["player"]["x"], spec["player"]["y"]

    def dist(x, y):
        return float(np.hypot(x - px, y - py))

    rows = []
    for (x, y), (cls, _) in sorted(pred.items()):
        if cls == "void" or not LF.in_view(g, x, y):
            continue
        m = cell_mean(lum, g, x, y)
        if m is None:
            continue
        # The nearest VOID cell at a comparable range, and the nearest FLOOR cell at the same
        # range. Same range on purpose: a contrast measured between two different distances from
        # the lamp is a measurement of the lamp.
        d = dist(x, y)
        best_v = best_f = None
        for (vx, vy), (vc, _) in pred.items():
            if vc != "void" or not LF.in_view(g, vx, vy):
                continue
            if abs(dist(vx, vy) - d) < 1.2:
                vm = cell_mean(lum, g, vx, vy)
                if vm is not None and (best_v is None or abs(dist(vx, vy) - d) < best_v[0]):
                    best_v = (abs(dist(vx, vy) - d), vm)
        for fy in range(h):
            for fx in range(w):
                if wall[fy][fx] or not LF.in_view(g, fx, fy):
                    continue
                if abs(dist(fx, fy) - d) < 0.6:
                    fm = cell_mean(lum, g, fx, fy)
                    if fm is not None and (best_f is None or abs(dist(fx, fy) - d) < best_f[0]):
                        best_f = (abs(dist(fx, fy) - d), fm)
        rows.append(dict(x=x, y=y, cls=cls, dist=round(d, 2), wall=round(m, 2),
                         void=round(best_v[1], 2) if best_v else None,
                         floor=round(best_f[1], 2) if best_f else None,
                         w_void=round(weber(m, best_v[1]), 4) if best_v else None,
                         w_floor=round(weber(m, best_f[1]), 4) if best_f else None,
                         # DELIVERED LEVELS, which is what the bar is now read in. Absolute and
                         # signed: a ratio survives the lamp's multiplication and eight bits do
                         # not, which is the whole reason the ruling moved the bar here.
                         l_void=round(m - best_v[1], 2) if best_v else None,
                         l_floor=round(m - best_f[1], 2) if best_f else None))

    print("MASS-READ — can the wall be told from the dark beyond it, and from the ground?")
    print("  %-8s %6s %8s %8s %8s %10s %10s"
          % ("cell", "range", "wall", "void", "floor", "W(wall,void)", "W(wall,floor)"))
    for r in sorted(rows, key=lambda r: r["dist"])[:26]:
        print("  (%2d,%2d) %6.2f %8.2f %8s %8s %10s %10s"
              % (r["x"], r["y"], r["dist"], r["wall"],
                 "%.2f" % r["void"] if r["void"] is not None else "-",
                 "%.2f" % r["floor"] if r["floor"] is not None else "-",
                 "%.4f" % r["w_void"] if r["w_void"] is not None else "-",
                 "%.4f" % r["w_floor"] if r["w_floor"] is not None else "-"))

    def band(lo, hi):
        return [r for r in rows if lo <= r["dist"] < hi]
    print()
    print("  %-14s %5s %10s %10s %10s %10s   %s"
          % ("range band", "n", "W(w,void)", "W(w,floor)", "L(w,void)", "L(w,floor)",
             "vs the %.0f-level bar" % LEVELS_BAR))
    summary = {}
    for label, lo, hi in (("standing <=2", 0, 2.5), ("3-4 tiles", 2.5, 4.5),
                          ("beyond 4", 4.5, 99)):
        b = band(lo, hi)
        wv = [r["w_void"] for r in b if r["w_void"] is not None]
        wf = [r["w_floor"] for r in b if r["w_floor"] is not None]
        if not b:
            continue
        lv = [r["l_void"] for r in b if r["l_void"] is not None]
        lf = [r["l_floor"] for r in b if r["l_floor"] is not None]
        mv = float(np.mean(wv)) if wv else float("nan")
        mf = float(np.mean(wf)) if wf else float("nan")
        alv = float(np.mean(np.abs(lv))) if lv else float("nan")
        alf = float(np.mean(np.abs(lf))) if lf else float("nan")
        summary[label] = dict(n=len(b), w_void=round(mv, 4), w_floor=round(mf, 4),
                              levels_void=round(alv, 2), levels_floor=round(alf, 2),
                              void_clears=bool(alv >= LEVELS_BAR),
                              floor_clears=bool(alf >= LEVELS_BAR))
        print("  %-14s %5d %10.4f %10.4f %10.2f %10.2f   void %s / floor %s"
              % (label, len(b), mv, mf, alv, alf,
                 "CLEARS" if alv >= LEVELS_BAR else "under",
                 "CLEARS" if alf >= LEVELS_BAR else "under"))

    out = dict(produced_by="tools/tier1_walls/measure_mass_read.py", scene=spec["name"],
               capture=a.png, family=man["family"], reference=FLOOR_REFERENCE,
               levels_bar=LEVELS_BAR,
               levels_bar_provenance=("RULED (Rafe, 2026-08-30): the perceptual-floor law reads "
                                      "in delivered levels, and 8 levels is 'barely met'. A human "
                                      "verdict on a measured quantity, which is the only way "
                                      "§13.8 permits a floor to exist."),
               cells=rows, by_band=summary)
    p = os.path.join(EV, "MASS-READ-%s.json" % a.tag)
    json.dump(out, open(p, "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(p, REPO))


if __name__ == "__main__":
    main()
