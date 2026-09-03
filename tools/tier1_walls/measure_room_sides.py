#!/usr/bin/env python3
"""THE ROOM'S SIDES — why they have no mass, and what the material lever can reach.

    python3 tools/tier1_walls/measure_room_sides.py --controls

RULED (Rafe, on the walk of `6acc740f`): *"the north face reads; east/west walls show no mass at
the room's edges; caps still read as unlit ground rather than wall-tops past the lamp. Prepare the
material-arm mass-read remedy as your next round, scoped to caps and N–S tops: a wall-top must
separate from unlit floor at the standing station by a readable margin — that's the room's sides
coming back."*

WHY THE SIDES AND NOT THE NORTH WALL, WHICH IS ONE FACT ABOUT §3. A face exists exactly where the
SOUTH neighbour is not wall. A room's north wall has floor to its south, so it gets a reveal and
reads as mass. A room's EAST and WEST walls have floor to their east or west — never to their
south — so §3 draws them no face at all and they present **cap and nothing else**. The moment the
cap stops separating from the floor, the sides of the room stop existing. That is not a bug in the
cap; it is §3's two-plane projection meeting a cap that has no second plane to be separated from.

⚠ AND MY OWN EARLIER NUMBER SAID THIS WAS FINE. `measure_mass_read.py` reported `L(cap, floor) =
19.27 levels — CLEARS` at the standing station, and I relayed it as the cap's ruled separation
being met. That figure is the **≤2 tiles band, n = 2 cells** — the only band that passes. Every
cell further out fails, and the room's sides are mostly further out. The measurement was correct
and the reporting privileged the band that agreed with me. This file reports every band, always,
and refuses to summarise to a single verdict.

WHAT IT MEASURES, on the capture, for cells that carry a cap AND NO FACE:

    L(cap, adjacent floor)   against the floor the cell actually abuts — the comparison the eye
                             makes, because that edge is where the room's side either is or is not
    L(cap, unlit floor)      against the frame's own unlit-floor reference (10th percentile of
                             floor cells), which is the thing Rafe's ruling names: a wall-top must
                             not read as unlit ground

PROJECTION WITHOUT A BUILD. Godot's 2D pipeline is exactly multiplicative in albedo — measured
0.5000 with a worst cell of 0.0006 (`light_field.py --controls`) — so the delivered value of the
same cell at a different authored rung is the delivered value now, scaled by the rung ratio. Every
candidate below is therefore computed from captures already on disk. **These are predictions from
a proven-linear pipeline, not measurements of a build**, and they are labelled as such wherever
they appear; the round verifies them by capture when a build is authorised.

NO PASS COUNTS UNTIL THE INSTRUMENT HAS FAILED (§13.5). `--controls` is two-sided on the axis this
claims: a synthetic cap set to the floor's own value must come back FAIL on every band, and one
set far from it must come back PASS. Both are applied to the capture, so nothing but the cap's
value differs.
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

LEVELS_BAR = 8.0        # §13.8 as ruled: the perceptual floor reads in delivered levels.
TWO_PLANE_RUNGS = 1.5   # `wall_laws.two_planes` — the face/top separation §3 needs.


def cell_mean(L, g, x, y, inset=6):
    if not LF.in_view(g, x, y):
        return None
    x0, y0, cw, ch = LF.cell_box(g, x, y)
    p = L[int(y0) + inset:int(y0 + ch) - inset, int(x0) + inset:int(x0 + cw) - inset]
    return float(p.mean()) if p.size else None


def sample(spec, png, log, cap_scale=1.0):
    """Cap-only wall cells, with the floor each one abuts. `cap_scale` scales the cap's albedo."""
    wall, w, h = build(spec)
    img = np.array(Image.open(png).convert("RGB")).astype(float)
    L = (img * LF.W709).sum(2)
    g = LF.read_grid(log)
    px, py = spec["player"]["x"], spec["player"]["y"]

    floors = [(x, y, cell_mean(L, g, x, y))
              for y in range(h) for x in range(w) if not wall[y][x]]
    floors = [(x, y, m) for x, y, m in floors if m is not None]
    unlit = float(np.percentile([m for _, _, m in floors], 10))

    rows = []
    for y in range(h):
        for x in range(w):
            if not wall[y][x]:
                continue
            if y + 1 < h and not wall[y + 1][x]:
                continue                      # carries a face — not a cap-only cell
            m = cell_mean(L, g, x, y)
            if m is None:
                continue
            m *= cap_scale                    # the multiplicative law, applied to the cap alone
            adj = [cell_mean(L, g, nx, ny)
                   for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                   if 0 <= nx < w and 0 <= ny < h and not wall[ny][nx]]
            adj = [a for a in adj if a is not None]
            if not adj:
                continue
            ns_run = any(0 <= x + d < w and not wall[y][x + d] for d in (-1, 1))
            rows.append(dict(x=x, y=y, rng=int(max(abs(x - px), abs(y - py))), cap=m,
                             floor=float(max(adj)), ns=bool(ns_run)))
    return rows, unlit


def bands(rows, unlit):
    out = []
    for name, lo, hi in (("standing <=2", 0, 2.5), ("3-4 tiles", 2.5, 4.5),
                         ("beyond 4", 4.5, 1e9)):
        sel = [r for r in rows if lo <= r["rng"] < hi]
        if not sel:
            continue
        # WORST CELL, not the mean. One side of a room that disappears is a side that disappeared;
        # averaging it against a side that did not is how the 19.27 figure came to be reported.
        adj = min(abs(r["floor"] - r["cap"]) for r in sel)
        unl = min(abs(r["cap"] - unlit) for r in sel)
        out.append(dict(band=name, n=len(sel), n_ns=sum(1 for r in sel if r["ns"]),
                        cap=round(float(np.mean([r["cap"] for r in sel])), 2),
                        floor=round(float(np.mean([r["floor"] for r in sel])), 2),
                        worst_vs_floor=round(adj, 2), worst_vs_unlit=round(unl, 2),
                        clears=bool(adj >= LEVELS_BAR)))
    return out


def show(bs, unlit, title):
    print(title)
    print("  band            n  ns  cap     floor   worst vs floor   worst vs unlit(%.1f)  verdict"
          % unlit)
    for b in bs:
        print("  %-14s %2d %3d %7.2f %7.2f %14.2f %20.2f   %s"
              % (b["band"], b["n"], b["n_ns"], b["cap"], b["floor"],
                 b["worst_vs_floor"], b["worst_vs_unlit"],
                 "clears" if b["clears"] else "UNDER the %.0f-level bar" % LEVELS_BAR))
    return all(b["clears"] for b in bs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default="src/Presentation/assets/tier0_harness/scenes/"
                                       "tier1_wall_standing.json")
    ap.add_argument("--png", default="tools/tier1_walls/evidence/r22_standing.png")
    ap.add_argument("--log", default="tools/tier1_walls/evidence/r22_standing.log")
    ap.add_argument("--cap-manifest", default="src/Presentation/assets/tier1_cap/MANIFEST.json")
    ap.add_argument("--tag", default="sides")
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    png, log = os.path.join(REPO, a.png), os.path.join(REPO, a.log)
    cap = json.load(open(os.path.join(REPO, a.cap_manifest)))
    ladder, rung = cap["ladder"], cap["top_rung"]
    face_rung = 1                       # the wall face, unchanged by this round's scope

    rows, unlit = sample(spec, png, log)
    show(bands(rows, unlit), unlit,
         "AS BUILT — cap rung %d (%.2f), cap-only cells, %s\n"
         % (rung, ladder[rung], os.path.basename(png)))

    print("\nPROJECTED — every candidate rung, computed from this capture by the multiplicative")
    print("law (0.5000, worst cell 0.0006). PREDICTIONS, to be verified by capture.")
    print("  rung  authored   3-4 tiles vs floor   standing vs floor   rungs above face   §3")
    res = []
    for r in range(0, rung + 1):
        pr, _ = sample(spec, png, log, cap_scale=ladder[r] / ladder[rung])
        bs = bands(pr, unlit)
        get = lambda nm: next((b for b in bs if b["band"] == nm), None)      # noqa: E731
        b34, b2 = get("3-4 tiles"), get("standing <=2")
        gap = r - face_rung
        ok3 = gap >= TWO_PLANE_RUNGS
        res.append(dict(rung=r, authored=round(ladder[r], 2),
                        band34=b34["worst_vs_floor"] if b34 else None,
                        band2=b2["worst_vs_floor"] if b2 else None,
                        rungs_above_face=gap, two_planes_ok=ok3))
        print("  %4d %9.2f %20s %19s %18d   %s"
              % (r, ladder[r],
                 "%.2f%s" % (b34["worst_vs_floor"], " OK" if b34["worst_vs_floor"] >= LEVELS_BAR
                             else "") if b34 else "-",
                 "%.2f%s" % (b2["worst_vs_floor"], " OK" if b2["worst_vs_floor"] >= LEVELS_BAR
                             else "") if b2 else "-",
                 gap, "ok" if ok3 else "BREAKS two_planes (needs >= %.1f)" % TWO_PLANE_RUNGS))

    out = dict(png=os.path.relpath(png, REPO), unlit_floor=round(unlit, 2),
               as_built=bands(rows, unlit), projected=res, levels_bar=LEVELS_BAR,
               note="projections are predictions from a proven-linear pipeline, not measurements")

    if a.controls:
        print("\nCONTROLS (§13.5) — two-sided on the axis this claims")
        flat, _ = sample(spec, png, log)
        for r in flat:
            r["cap"] = r["floor"]                   # a cap at exactly the floor's value
        bad = show(bands(flat, unlit), unlit, "  PLANT — cap set to the floor it abuts")
        far, _ = sample(spec, png, log)
        for r in far:
            r["cap"] = r["floor"] - 40.0            # a cap unmistakably separated
        good = show(bands(far, unlit), unlit, "  PLANT — cap 40 levels below the floor")
        ok = (not bad) and good
        out["controls"] = dict(cap_equals_floor_fails=not bad, cap_far_passes=good, proven=ok)
        print("\n  cap==floor -> %s   cap-40 -> %s   ->  %s"
              % ("FAILS" if not bad else "passes (WRONG)",
                 "PASSES" if good else "fails (WRONG)",
                 "the instrument can say both" if ok else "NOT PROVEN"))

    json.dump(out, open(os.path.join(EV, "ROOM-SIDES-%s.json" % a.tag), "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(os.path.join(EV, "ROOM-SIDES-%s.json" % a.tag), REPO))


if __name__ == "__main__":
    main()
