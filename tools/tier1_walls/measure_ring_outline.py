#!/usr/bin/env python3
"""THE RING BOUNDARY IS A DRAWN LINE — §12.1, measured on the capture.

RULED (Rafe, 2026-08-31): *"VOID_RING=1 is a §12.1 violation — a baked outline from ring
placement, exactly the ban the floor family holds; fix by placement so the ring boundary is not a
hard step in a flat field, or drop VOID_RING."*

Round 8's blind seat found it without being told to look:

    *"Two perfectly straight vertical seams in the darkness at x=311 and x=502, running the full
    height y=0-197. On one side, pure black (1,1,1). On the other, (7,7,9). Nothing standing
    explains those edges — they are 200px-tall ruled lines in the dark itself, and the eye keeps
    finding them because they're the crispest verticals in the upper half of the frame."*

Those columns are cell boundaries. `RingOf` is a Chebyshev distance to the nearest walkable cell,
and everything past `void_ring` is filled with the void instead of the cap — so a classification
that changes at a grid position produces a luminance step at that grid position, and the step is
the only readable thing in a field the lamp has already flattened.

WHAT AN OUTLINE IS, STATED SO IT CAN BE MEASURED. Not "a step" — form makes steps, and §12.1 is
explicit that plane-boundary occlusion is form rather than outline. It is a step **at a boundary
nothing in the world put there**, and this family already has a bound for exactly that:
`cap_seamless` and `edge_agreement` both require a boundary to be no more than **1.35x an ordinary
interior step**. The ring boundary is held to the same bar, because it is the same claim — a cell
edge should not be louder than the material crossing it.

    ring_step        delivered levels across a cap|void boundary — reported WORST, not median
    peer_step        a cap|cap cell boundary — the same kind of edge with no classification
                     change behind it. THE DENOMINATOR: if the ring adds nothing to an ordinary
                     cell boundary, placement drew no line.
    interior_step    an ordinary step inside one capped cell, carried as context only

⚠ THE WORST EDGE, NOT THE MEDIAN, AND THE FIRST VERSION USED THE MEDIAN. Six of thirteen ring
boundaries in the gate scene carry a 6-7 level step and seven carry none, because past the lamp
the capped side is as black as the void; the median was 1.0 and the instrument said *form* about
a defect a blind seat had already found unaided. **You do not average an outline away** — one
readable ruled line is a ruled line, which is why `no_ring` is a worst-case bound too.

NO PASS COUNTS UNTIL THE INSTRUMENT HAS FAILED (§13.5). `--controls` runs it TWO-SIDED, because
this one starts life failing and an instrument that only ever reds proves as little as one that
only ever greens:
    the shipped build      must come back DIRTY  (the defect is real)
    the void set to cap    must come back CLEAN  (the instrument can say yes)
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

LEVELS_BAR = 8.0        # §13.8, as ruled: the perceptual floor reads in delivered levels.
BOUND = 1.35            # the family's own boundary bound — cap_seamless and edge_agreement both.


def ring_of(wall, w, h, x, y, cap):
    """Chebyshev distance to the nearest walkable cell, capped — the renderer's own RingOf."""
    for r in range(1, cap + 1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and not wall[ny][nx]:
                    return r
    return cap + 1


def edge_pair(lum, g, a, b, inset=6):
    """Mean luminance of the two pixel columns/rows either side of a shared cell boundary."""
    (ax, ay), (bx, by) = a, b
    ax0, ay0, cw, ch = LF.cell_box(g, ax, ay)
    bx0, by0, _, _ = LF.cell_box(g, bx, by)
    i, j = int(round(cw)), int(round(ch))
    if bx > ax:      # b is east of a
        p = lum[int(ay0) + inset:int(ay0) + j - inset, int(ax0) + i - 2:int(ax0) + i]
        q = lum[int(by0) + inset:int(by0) + j - inset, int(bx0):int(bx0) + 2]
    else:            # b is south of a
        p = lum[int(ay0) + j - 2:int(ay0) + j, int(ax0) + inset:int(ax0) + i - inset]
        q = lum[int(by0):int(by0) + 2, int(bx0) + inset:int(bx0) + i - inset]
    if p.size < 8 or q.size < 8:
        return None
    return float(p.mean()), float(q.mean())


def measure(spec, png, log, void_ring=1, void_as_cap=False):
    wall, w, h = build(spec)
    img = np.array(Image.open(png).convert("RGB")).astype(float)
    lum = (img * LF.W709).sum(2)
    g = LF.read_grid(log)
    px, py = spec["player"]["x"], spec["player"]["y"]

    # ⚠ A CELL THAT CARRIES A FACE IS EXCLUDED, AND THIS IS NOT CONVENIENCE. Where the south
    # neighbour is open the cell holds the reveal as well as the top, so its edges carry §3's
    # two-plane separation — which §12.1 names as FORM, in the same clause that bans the outline.
    # Counting it here reported a 5.7-level "outline" at (10,10)|(10,11) on the remedied build and
    # sent me hunting a second defect that was the wall doing its job.
    cls = {}
    for y in range(h):
        for x in range(w):
            if not wall[y][x]:
                continue
            if y + 1 < h and not wall[y + 1][x]:
                continue
            cls[(x, y)] = "void" if ring_of(wall, w, h, x, y, void_ring) > void_ring else "cap"

    if void_as_cap:
        # THE SECOND CONTROL: every void cell repainted with its own capped neighbour's value, so
        # the classification is still there and the STEP is not. An instrument that cannot come
        # back clean on this has not measured the boundary, it has measured the geometry.
        for (x, y), k in cls.items():
            if k != "void":
                continue
            near = [(nx, ny) for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
                    if cls.get((nx, ny)) == "cap"]
            if not near:
                continue
            nx0, ny0, cw, ch = LF.cell_box(g, *near[0])
            x0, y0, _, _ = LF.cell_box(g, x, y)
            src = lum[int(ny0):int(ny0 + ch), int(nx0):int(nx0 + cw)]
            dst = (slice(int(y0), int(y0 + ch)), slice(int(x0), int(x0 + cw)))
            if src.size and lum[dst].shape == src.shape:
                lum[dst] = src

    ring, peer, sds = [], [], []
    worst = None
    for (x, y), k in cls.items():
        if not LF.in_view(g, x, y):
            continue
        for nx, ny in ((x + 1, y), (x, y + 1)):
            if (nx, ny) not in cls or not LF.in_view(g, nx, ny):
                continue
            e = edge_pair(lum, g, (x, y), (nx, ny))
            if e is None:
                continue
            step = abs(e[0] - e[1])
            r = float(max(abs(x - px), abs(y - py)))
            if k != cls[(nx, ny)]:
                ring.append((r, step))
                if worst is None or step > worst[0]:
                    worst = (step, (x, y), (nx, ny), r)
            else:
                peer.append((r, step))
        if k == "cap":
            x0, y0, cw, ch = LF.cell_box(g, x, y)
            p = lum[int(y0) + 6:int(y0 + ch) - 6, int(x0) + 6:int(x0 + cw) - 6]
            if p.size > 16:
                sds.append((float(max(abs(x - px), abs(y - py))), float(p.std())))

    bands = (("standing <=2", 0, 2.5), ("3-4 tiles", 2.5, 4.5), ("beyond 4", 4.5, 1e9))
    out = []
    for name, lo, hi in bands:
        rs = [s for r, s in ring if lo <= r < hi]
        ps = [s for r, s in peer if lo <= r < hi]
        ss = [s for r, s in sds if lo <= r < hi]
        if not rs:
            continue
        rstep = float(np.max(rs))
        inner = float(np.median(ss)) if ss else 0.0
        # ⚠ AGAINST THE PEER BOUNDARY, NOT AGAINST INTERIOR NOISE. Past the lamp an interior step
        # is 0.55 levels — 8-bit rounding — so dividing by it makes any step at all look enormous
        # and the REMEDIED build came back at 1.59x, still "dirty", on a boundary of 0.88 levels
        # that nothing could see. The honest denominator is the same kind of edge with no
        # classification change behind it: if the ring adds nothing to an ordinary cell boundary,
        # it draws no line. Same scene, same rig, same range band, same face exclusion.
        pmax = float(np.max(ps)) if ps else 0.0
        ratio = rstep / max(pmax, 0.5)
        out.append(dict(band=name, n_ring=len(rs), n_peer=len(ps),
                        ring_step=round(rstep, 3), over_bar=int(sum(1 for v in rs if v >= 3.0)),
                        peer_step=round(pmax, 3) if ps else None,
                        interior_step=round(inner, 3), ring_over_peer=round(ratio, 3),
                        outline=bool(ratio > BOUND)))
    if out and worst is not None:
        out[-1]["worst_pair"] = dict(step=round(worst[0], 3), a=list(worst[1]),
                                     b=list(worst[2]), range=worst[3])
    return out


def report(bands, title):
    print(title)
    print("  band            ring  worst_step  over>=3   peer  interior    x peer   verdict")
    dirty = False
    for b in bands:
        if b["outline"]:
            dirty = True
        print("  %-14s %5d %11.3f %8d %5s %9.3f %11.2f   %s"
              % (b["band"], b["n_ring"], b["ring_step"], b["over_bar"],
                 "-" if b["peer_step"] is None else "%.2f" % b["peer_step"],
                 b["interior_step"], b["ring_over_peer"],
                 "OUTLINE — a ruled line placement drew" if b["outline"] else "form"))
        if b.get("worst_pair"):
            wp = b["worst_pair"]
            print("                 worst edge %s|%s  step %.2f levels at range %.0f"
                  % (tuple(wp["a"]), tuple(wp["b"]), wp["step"], wp["range"]))
    return dirty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--png", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--void-ring", type=int, default=1)
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    png, log = os.path.join(REPO, a.png), os.path.join(REPO, a.log)

    bands = measure(spec, png, log, a.void_ring)
    dirty = report(bands, "THE RING BOUNDARY — %s (bound: %.2fx an ordinary cell boundary)"
                   % (os.path.basename(png), BOUND))
    res = dict(png=os.path.relpath(png, REPO), void_ring=a.void_ring,
               bound=BOUND, bands=bands, outline=dirty)

    if a.controls:
        cb = measure(spec, png, log, a.void_ring, void_as_cap=True)
        print("")
        clean = not report(cb, "  CONTROL — the void repainted as its capped neighbour")
        res["control"] = dict(bands=cb, clean=clean)
        ok = dirty and clean
        print("\n  TWO-SIDED: shipped=%s  void-as-cap=%s  ->  %s"
              % ("DIRTY" if dirty else "clean", "CLEAN" if clean else "dirty",
                 "the instrument can say both" if ok
                 else "NOT PROVEN — it does not discriminate"))
        res["proven"] = bool(ok)

    json.dump(res, open(os.path.join(EV, "RING-OUTLINE-%s.json" % a.tag), "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(os.path.join(EV, "RING-OUTLINE-%s.json" % a.tag), REPO))


if __name__ == "__main__":
    main()
