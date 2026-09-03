#!/usr/bin/env python3
"""DOES THE CAP'S TEXTURE SURVIVE BEING DELIVERED? — §13.9's representable floor, aimed upward.

`wall_laws.py`'s three cap tests read the ASSET: the field is seamless, it carries more levels
than the bar's cap, its variation lives at field scale. Every one of those is a statement about
albedo, and Godot's 2D pipeline is exactly multiplicative in albedo — so a surface at a delivered
value of seven receives its own texture multiplied by roughly 0.06, and a grain authored as a
fraction of a ladder rung quantises to **nothing at all**. The tile is not flat. The pixels are.

This is the same trap the void was pulled out of an hour earlier, and it was pulled out of it by
authoring its grain in LEVELS rather than in rungs. The cap was not, so this asks the question of
the cap, on the capture, where the answer lives:

    per cap cell, binned by range from the lamp —
      delivered mean          how bright the top actually is
      delivered sd            how much variation is left after the multiply and the 8-bit round
      distinct levels         how many values the cell actually contains

A cell that delivers **sd < 0.5 levels and two distinct values or fewer is a flat fill**, whatever
its albedo says, and §8.3.1's mirror — *incident-free is not empty* — is broken at that range no
matter how the asset measures.

NO PASS COUNTS UNTIL THE INSTRUMENT HAS FAILED (§13.5). `--controls` flattens every cap cell in
the capture to its own mean — the exact defect the test claims, introduced on the capture rather
than in the composer so the plant and the family differ in one thing.
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
from mask_census import build       # noqa: E402

SD_FLOOR = 0.5          # levels. Below this a cell is one value with rounding noise on it.
LEVELS_FLOOR = 3        # distinct 8-bit values. Two is a value and its neighbour.


def cap_cells(spec, wall, w, h):
    """Cells that show CAP AND ONLY CAP.

    A wall cell is capped when it is solid and adjacent to something walkable — `RingOf` == 1 in
    the renderer; past that it is void. But a capped cell whose SOUTH neighbour is open also
    carries the reveal, drawn over the cap as a child sprite, and a cell holding two planes has a
    standard deviation that says nothing about either. Those are excluded: the question here is
    what the TOP delivers, so the sample is tops with no face in them.
    """
    out = []
    for y in range(h):
        for x in range(w):
            if not wall[y][x]:
                continue
            near = any(0 <= x + dx < w and 0 <= y + dy < h and not wall[y + dy][x + dx]
                       for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy)
            south_open = y + 1 < h and not wall[y + 1][x]
            if near and not south_open:
                out.append((x, y))
    return out


def cell_stats(lum, g, x, y, inset=4):
    x0, y0, cw, ch = LF.cell_box(g, x, y)
    # ⚠ FULLY INSIDE THE DUNGEON VIEW OR NOT AT ALL — `LF.in_view`, not the image bounds.
    #
    # The first version checked only that the box fitted the PNG, and cell (7,7) sat at y=34,
    # above the view's top edge at y=90, holding interface pixels that peak at 255. It reported a
    # texture sd of 4.34 on a mean of 10.30 and called the cap textured. The plant seat, reading
    # the same capture with its eyes, reported the wall band's channel sds as 0.66/0.68/1.01 —
    # and the seat was right.
    if not LF.in_view(g, x, y):
        return None
    p = lum[int(y0) + inset:int(y0 + ch) - inset, int(x0) + inset:int(x0 + cw) - inset]
    if p.size < 16:
        return None
    # ⚠ THE LIGHT GRADIENT IS NOT TEXTURE, and the first version of this counted it as texture: a
    # cell five tiles out delivered sd 4.7 on a mean of 10.3 and was reported as *texture
    # survives*, when almost all of that spread is the lamp falling off across 32 pixels. §6.3 is
    # the reason it matters — assets receive light, never depict it — so the light is fitted as a
    # plane and removed, and what is left is what the ASSET put there.
    yy, xx = np.mgrid[0:p.shape[0], 0:p.shape[1]]
    A = np.stack([np.ones(p.size), xx.ravel(), yy.ravel()], axis=1)
    coef, *_ = np.linalg.lstsq(A, p.ravel(), rcond=None)
    resid = p.ravel() - A @ coef
    return dict(mean=float(p.mean()), sd=float(p.std()), texture_sd=float(resid.std()),
                levels=int(len(np.unique(np.round(p)))))


def measure(spec, png, log, flatten=False):
    wall, w, h = build(spec)
    img = np.array(Image.open(png).convert("RGB")).astype(float)
    lum = (img * LF.W709).sum(2)
    g = LF.read_grid(log)
    px, py = spec["player"]["x"], spec["player"]["y"]

    if flatten:
        # THE PLANT. Every cap cell replaced by its own mean — a genuinely flat top, introduced on
        # the capture so it differs from the family in this and in nothing else.
        for (x, y) in cap_cells(spec, wall, w, h):
            if not LF.in_view(g, x, y):
                continue
            x0, y0, cw, ch = LF.cell_box(g, x, y)
            sl = (slice(int(y0), int(y0 + ch)), slice(int(x0), int(x0 + cw)))
            lum[sl] = np.round(lum[sl].mean())

    rows = []
    for (x, y) in cap_cells(spec, wall, w, h):
        s = cell_stats(lum, g, x, y)
        if s is None:
            continue
        s.update(x=x, y=y, range=float(max(abs(x - px), abs(y - py))))
        rows.append(s)

    bands = (("standing <=2", 0, 2.5), ("3-4 tiles", 2.5, 4.5), ("beyond 4", 4.5, 1e9))
    out = []
    for name, lo, hi in bands:
        sel = [r for r in rows if lo <= r["range"] < hi]
        if not sel:
            continue
        # MEDIAN, not mean: one cell holding a HUD widget or the player sprite would otherwise
        # carry a whole band, which is how the first version came back saying the opposite.
        tx = float(np.median([r["texture_sd"] for r in sel]))
        lv = float(np.median([r["levels"] for r in sel]))
        out.append(dict(band=name, n=len(sel),
                        mean=round(float(np.median([r["mean"] for r in sel])), 2),
                        sd=round(float(np.median([r["sd"] for r in sel])), 3),
                        texture_sd=round(tx, 3), levels=round(lv, 2),
                        flat=bool(tx < SD_FLOOR or lv < LEVELS_FLOOR)))
    return rows, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--png", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    png, log = os.path.join(REPO, a.png), os.path.join(REPO, a.log)
    rows, bands = measure(spec, png, log)

    print("THE CAP AS DELIVERED — %d capped cells, %s" % (len(rows), os.path.basename(png)))
    print("  band            n    mean   sd(raw)  sd(texture)  levels   verdict")
    for b in bands:
        print("  %-14s %3d %7.2f %9.3f %12.3f %7.2f   %s"
              % (b["band"], b["n"], b["mean"], b["sd"], b["texture_sd"], b["levels"],
                 "FLAT FILL — the texture did not survive" if b["flat"] else "texture survives"))
    print("  floor: texture sd < %.1f levels OR fewer than %d distinct values is a flat fill"
          % (SD_FLOOR, LEVELS_FLOOR))

    res = dict(png=os.path.relpath(png, REPO), cells=len(rows), bands=bands,
               sd_floor=SD_FLOOR, levels_floor=LEVELS_FLOOR)

    if a.controls:
        _, pb = measure(spec, png, log, flatten=True)
        fired = all(b["flat"] for b in pb)
        res["plant"] = dict(bands=pb, fires=fired)
        print("\n  PLANT — every cap cell flattened to its own mean (§13.5)")
        for b in pb:
            print("  %-14s %3d %7.2f %9.3f %12.3f %7.2f   %s"
                  % (b["band"], b["n"], b["mean"], b["sd"], b["texture_sd"], b["levels"],
                     "FLAT FILL" if b["flat"] else "SILENT"))
        print("  plant: %s" % ("FIRES on every band — the instrument can fail" if fired
                               else "SILENT on some band — THE INSTRUMENT IS NOT PROVEN"))

    json.dump(res, open(os.path.join(EV, "CAP-DELIVERED-%s.json" % a.tag), "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(os.path.join(EV, "CAP-DELIVERED-%s.json" % a.tag), REPO))


if __name__ == "__main__":
    main()
