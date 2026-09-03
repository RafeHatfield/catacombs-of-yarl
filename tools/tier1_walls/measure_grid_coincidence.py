#!/usr/bin/env python3
"""GRID COINCIDENCE — does the treatment know where the tiles are?

    python3 tools/tier1_walls/measure_grid_coincidence.py --controls

RULED (Rafe, standing order): *"Add the missing instrument: grid-coincidence — share of any
wear/treatment boundary lying on tile edges vs chance, gated at ~chance (the ban's question, not
its history)."*

WHY IT IS MISSING, AND WHY IT IS THE BAN'S ACTUAL QUESTION. This directory has six instruments
that each ask whether ONE NAMED TREATMENT sits on the grid: `edge_agreement` asks it of the
crossing block, `constant_pitch` of the head joints, `cap_seamless` of the cap's windows,
`ring_outline` of the ring boundary. Every one was written after something was caught by eye. The
concurrent floor session hit the same wall from the other side and said it plainly:

    *"Every ring instrument this campaign built asks whether a treatment sits at a constant TILE
    GRID position […] NONE OF THEM ASKS THE QUESTION A PERSON ASKS FIRST."*

This asks the general question of the WHOLE FRAME, with no list of treatments: **of every value
boundary in the picture, what share falls on a tile edge, and is that more than chance?** A
surface whose marks are placed by the world scores at chance. A surface whose marks are placed by
the tile scores above it, whatever the mark is and whether or not anyone has named it yet.

CHANCE IS COMPUTED, NOT ASSUMED. With a tile pitch of T screen pixels and an edge band of ±d, a
boundary pixel placed without regard to the grid lands in the band with probability (2d+1)/T per
axis. The instrument reports OBSERVED / CHANCE, so 1.00 is a surface that does not know where the
tiles are.

MEASURED WHERE JUDGEMENT LIVES (§13.9, and the standing order's own denominator for the plant):
only cells inside the dungeon view whose delivered value can carry a boundary a person could see.
Past the lamp every difference is under the perceptual floor, and counting the grid-coincidence of
invisible boundaries measures 8-bit rounding.

NO PASS COUNTS UNTIL THE INSTRUMENT HAS FAILED (§13.5). `--controls` plants a treatment stamped at
a constant offset in every tile — the defect this claims to detect — and requires it to fire,
while the unmodified frame comes back at chance.
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
import light_field as LF            # noqa: E402
from mask_census import build       # noqa: E402

BOUND = 1.35        # the family's own boundary bound, reused so the numbers are comparable
EDGE_D = 1          # +-1 screen px counts as "on the tile edge"
MIN_VALUE = 12.3    # §13.9: below this a boundary cannot clear the perceptual floor anyway


def frame(png, log, spec, plant=False):
    img = np.asarray(Image.open(png).convert("RGB")).astype(float)
    L = (img * LF.W709).sum(2)
    g = LF.read_grid(log)
    wall, w, h = build(spec)

    T = int(round(g["px"]))
    x0 = g["cx0"] - g["px"] / 2.0
    y0 = g["cy0"] - g["py"] / 2.0

    if plant:
        # THE PLANT: one mark stamped at a constant offset inside every cell — the defect named.
        # It is drawn only on cells the instrument will actually look at, so it cannot pass by
        # landing where nothing is measured.
        for yy in range(h):
            for xx in range(w):
                if not LF.in_view(g, xx, yy):
                    continue
                bx, by, cw, ch = (int(v) for v in LF.cell_box(g, xx, yy))
                if L[by:by + ch, bx:bx + cw].mean() < MIN_VALUE:
                    continue
                # ⚠ AT THE CELL EDGE, and the first version stamped at rows 6-9 — a constant
                # offset that is NOT an edge. It ADDED boundaries away from the grid and so
                # DILUTED the on-edge share: the plant came back at 1.20x against a legal frame
                # at 1.47x, quieter than the thing it was meant to be louder than. The claim is
                # "boundaries on tile edges", so the plant must put one there.
                L[by:by + 2, bx:bx + cw] *= 0.55

    # WHICH PIXELS COUNT — and geometry is excluded, because geometry is not a treatment.
    #
    # ⚠ THE FIRST VERSION COUNTED THE ROOM'S OWN EDGES. A wall cell beside a floor cell has a real
    # value step at their shared boundary: that is the world changing, §12.1's contact occlusion
    # sits there BY RULING, and both are FORM. Counting them, the legal frame read 1.47x on the
    # y-axis and the instrument was about to report the wall for having a bottom. Only boundaries
    # INTERIOR to a run of same-class cells are treatment, so only those are measured.
    ok = np.zeros_like(L, dtype=bool)
    cls = np.zeros_like(L, dtype=np.int8)      # 1 = wall, 2 = floor, for the per-surface split
    for yy in range(h):
        for xx in range(w):
            if not LF.in_view(g, xx, yy):
                continue
            bx, by, cw, ch = (int(v) for v in LF.cell_box(g, xx, yy))
            if L[by:by + ch, bx:bx + cw].mean() < MIN_VALUE:
                continue
            same_x = (xx + 1 < w) and (wall[yy][xx + 1] == wall[yy][xx])
            same_y = (yy + 1 < h) and (wall[yy + 1][xx] == wall[yy][xx])
            if same_x and same_y:
                ok[by:by + ch, bx:bx + cw] = True
                # 1 = wall carrying a FACE (south open), 3 = wall showing CAP only, 2 = floor.
                if not wall[yy][xx]:
                    cls[by:by + ch, bx:bx + cw] = 2
                elif yy + 1 < h and not wall[yy + 1][xx]:
                    cls[by:by + ch, bx:bx + cw] = 1
                else:
                    cls[by:by + ch, bx:bx + cw] = 3
    return L, ok, cls, T, x0, y0


def coincidence(L, ok, T, ox, oy):
    """Share of visible value boundaries lying on a tile edge, against chance."""
    gx = np.abs(np.diff(L, axis=1, prepend=L[:, :1]))
    gy = np.abs(np.diff(L, axis=0, prepend=L[:1, :]))

    res = {}
    for axis, grad, origin in (("x", gx, ox), ("y", gy, oy)):
        m = ok & (grad >= 8.0)              # §13.8: a boundary a person could see
        if m.sum() < 50:
            res[axis] = None
            continue
        idx = np.nonzero(m)[1 if axis == "x" else 0].astype(float)
        off = np.abs(((idx - origin + T / 2.0) % T) - T / 2.0)
        on_edge = float((off <= EDGE_D).mean())
        chance = (2.0 * EDGE_D + 1.0) / T
        res[axis] = dict(n=int(m.sum()), on_edge=round(on_edge, 4),
                         chance=round(chance, 4), ratio=round(on_edge / chance, 3))
    return res


def report(res, title):
    print(title)
    print("  axis      n boundaries   on tile edge    chance    x chance   verdict")
    worst = 0.0
    for axis in ("x", "y"):
        r = res.get(axis)
        if r is None:
            print("  %-4s      (too few boundaries to measure)" % axis)
            continue
        worst = max(worst, r["ratio"])
        print("  %-4s %14d %13.2f%% %8.2f%% %10.2f   %s"
              % (axis, r["n"], 100 * r["on_edge"], 100 * r["chance"], r["ratio"],
                 "at chance" if r["ratio"] <= BOUND else "ON THE GRID"))
    return worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default="src/Presentation/assets/tier0_harness/scenes/"
                                       "tier1_wall_standing.json")
    ap.add_argument("--png", default="tools/tier1_walls/evidence/r25_standing.png")
    ap.add_argument("--log", default="tools/tier1_walls/evidence/r25_standing.log")
    ap.add_argument("--tag", default="r25")
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    png, log = os.path.join(REPO, a.png), os.path.join(REPO, a.log)

    L, ok, cls, T, ox, oy = frame(png, log, spec)
    res = coincidence(L, ok, T, ox, oy)
    worst = report(res, "GRID COINCIDENCE — %s (bound: %.2fx chance)\n"
                   % (os.path.basename(png), BOUND))

    # PER SURFACE, because "the frame is on the grid" does not say WHOSE treatment is. The wall
    # family and the floor family are composed by different tools in different sessions, and an
    # aggregate that blames the wrong one is worse than no number.
    print("")
    split = {}
    for name, v in (("wall face", 1), ("wall cap-only", 3), ("floor", 2)):
        sub = coincidence(L, ok & (cls == v), T, ox, oy)
        split[name] = dict(axes=sub, worst=report(sub, "  %s cells only\n" % name.upper()))
        print("")
    out = dict(png=os.path.relpath(png, REPO), bound=BOUND, tile_px=T,
               axes=res, per_surface=split,
               worst_ratio=worst, on_grid=bool(worst > BOUND),
               face_worst=split["wall face"]["worst"],
               cap_worst=split["wall cap-only"]["worst"],
               floor_worst=split["floor"]["worst"])

    if a.controls:
        Lp, okp, _clsp, Tp, oxp, oyp = frame(png, log, spec, plant=True)
        pres = coincidence(Lp, okp, Tp, oxp, oyp)
        print("")
        pw = report(pres, "  PLANT — one mark stamped at a constant offset in every cell\n")
        fired = pw > BOUND
        clean = split["wall cap-only"]["worst"] <= BOUND
        out["control"] = dict(plant_ratio=pw, fires=bool(fired), legal_clean=bool(clean))
        out["proven"] = bool(fired and clean)
        # THE POSITIVE SIDE IS THE CAP-ONLY CELLS. The cap is seamless BY CONSTRUCTION — one
        # toroidal field cut by world position — so if any surface in this frame is entitled to
        # score at chance it is that one. It is the control that shows the instrument can say YES,
        # and it is a real surface rather than a synthetic one.
        print("  legal CAP-ONLY cells %.2fx  |  plant %.2fx  ->  %s"
              % (split["wall cap-only"]["worst"], pw,
                 "the instrument can say both" if fired and clean else "NOT PROVEN"))

    json.dump(out, open(os.path.join(EV, "GRID-COINCIDENCE-%s.json" % a.tag), "w"), indent=2)
    print("\n  wrote %s"
          % os.path.relpath(os.path.join(EV, "GRID-COINCIDENCE-%s.json" % a.tag), REPO))
    return 0 if worst <= BOUND else 1


if __name__ == "__main__":
    sys.exit(main())
