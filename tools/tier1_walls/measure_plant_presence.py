#!/usr/bin/env python3
"""IS THE PLANT IN THE PICTURE? — LOOP-PROCESS §4's control, checked before it is trusted.

    python3 tools/tier1_walls/measure_plant_presence.py --controls

RULED (Rafe, 2026-09-02): *"Plant presence is measured within the lit band at the standing station
— a control lives where judgment lives (§13.9 defines the judgeable region for seat and plant
alike); validity bar: ruin deliverable above the perceptual floor where the seat looks."*

WHY THIS EXISTS. Rounds 9 and 10 both came back VOID on a missed plant, and the reason was neither
the seat nor the detector: **the plant had stopped being in the picture.** `plant_walls.ruin()`
marks the wall family's tiles, and since the cap pass the cell's base is a CAP WINDOW while the
family's `top_h`/`top_v` tiles are never drawn at all. Measured on the round-10 pair, the plant
differed from the family in 0.54% of the frame across 21 cells. A control absent from the picture
cannot be caught, and its misses say nothing about the seat that missed it.

THE DENOMINATOR IS THE RULING'S, AND IT IS NOT THE FRAME. Counting a ruin against the whole
capture, or against every wall cell, charges the plant for cells where NOTHING is deliverable —
past the lamp the floor itself holds seven levels and §13.9's representable floor swallows any
mark you put there. A control is only obliged to exist where a judgement is possible.

    JUDGEABLE      a wall cell whose delivered value is high enough that this plant's own
                   construction could clear the perceptual floor there. `ruin()` darkens to 0.35x
                   and brightens to 1.45x, so the largest excursion it can produce is 0.65x the
                   cell's value; clearing §13.8's 8 levels therefore needs a cell at
                   8 / 0.65 = 12.3 delivered. Derived from the plant's own numbers and the ruled
                   bar — not chosen to make a figure look better.

    PRESENT        a judgeable cell where the family and the plant actually differ by 8 levels or
                   more over at least 2% of the cell's pixels.

NO PASS COUNTS UNTIL THE INSTRUMENT HAS FAILED (§13.5). `--controls` runs it against the family
compared with ITSELF, which must report 0% present — an instrument that finds a ruin between a
capture and itself is measuring noise.
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

LEVELS_BAR = 8.0        # §13.8, as ruled.
RUIN_EXCURSION = 0.65   # `plant_walls.ruin()` darkens to 0.35x; the largest swing it can make.
JUDGEABLE = LEVELS_BAR / RUIN_EXCURSION      # 12.3 delivered levels
SHARE = 0.02            # of a cell's pixels, before that cell counts as carrying the ruin


def cells(spec, png_a, png_b, log):
    wall, w, h = build(spec)
    A = np.asarray(Image.open(png_a).convert("RGB")).astype(float)
    B = np.asarray(Image.open(png_b).convert("RGB")).astype(float)
    g = LF.read_grid(log)
    px, py = spec["player"]["x"], spec["player"]["y"]
    La = (A * LF.W709).sum(2)

    rows = []
    for y in range(h):
        for x in range(w):
            if not wall[y][x] or not LF.in_view(g, x, y):
                continue
            x0, y0, cw, ch = (int(v) for v in LF.cell_box(g, x, y))
            a, b = A[y0:y0 + ch, x0:x0 + cw], B[y0:y0 + ch, x0:x0 + cw]
            if a.size == 0 or a.shape != b.shape:
                continue
            val = float(La[y0:y0 + ch, x0:x0 + cw].mean())
            d = np.abs((a - b) * LF.W709).sum(2)
            rows.append(dict(x=x, y=y, rng=int(max(abs(x - px), abs(y - py))), value=val,
                             judgeable=bool(val >= JUDGEABLE),
                             share=float((d >= LEVELS_BAR).mean()),
                             present=bool((d >= LEVELS_BAR).mean() >= SHARE)))
    return rows


def report(rows, title):
    j = [r for r in rows if r["judgeable"]]
    p = [r for r in j if r["present"]]
    all_p = [r for r in rows if r["present"]]
    print(title)
    print("  wall cells in view            %3d" % len(rows))
    print("  JUDGEABLE (>= %.1f delivered)  %3d   — where a ruin could clear the %.0f-level bar"
          % (JUDGEABLE, len(j), LEVELS_BAR))
    print("  carrying the ruin             %3d" % len(p))
    pct = 100.0 * len(p) / max(len(j), 1)
    print("  PRESENCE, in the ruled denominator   %.1f%%" % pct)
    print("  (against every wall cell in view:    %.1f%%  — the figure the ruling replaces)"
          % (100.0 * len(all_p) / max(len(rows), 1)))
    for name, lo, hi in (("standing <=2", 0, 2.5), ("3-4 tiles", 2.5, 4.5), ("beyond 4", 4.5, 1e9)):
        band = [r for r in rows if lo <= r["rng"] < hi]
        bj = [r for r in band if r["judgeable"]]
        bp = [r for r in bj if r["present"]]
        if band:
            print("    %-14s cells %2d  judgeable %2d  present %2d"
                  % (name, len(band), len(bj), len(bp)))
    return pct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default="src/Presentation/assets/tier0_harness/scenes/"
                                       "tier1_wall_standing.json")
    ap.add_argument("--family", default="tools/tier1_walls/evidence/r24_standing.png")
    ap.add_argument("--plant", default="tools/tier1_walls/evidence/r24_standing_plant.png")
    ap.add_argument("--log", default="tools/tier1_walls/evidence/r24_standing.log")
    ap.add_argument("--tag", default="r24")
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    fam, pl = os.path.join(REPO, a.family), os.path.join(REPO, a.plant)
    log = os.path.join(REPO, a.log)

    rows = cells(spec, fam, pl, log)
    pct = report(rows, "PLANT PRESENCE — %s vs %s, at the standing station\n"
                 % (os.path.basename(fam), os.path.basename(pl)))
    out = dict(family=os.path.relpath(fam, REPO), plant=os.path.relpath(pl, REPO),
               judgeable_threshold=round(JUDGEABLE, 2), levels_bar=LEVELS_BAR,
               presence_pct=round(pct, 2), cells=rows)

    if a.controls:
        print("")
        self_pct = report(cells(spec, fam, fam, log),
                          "  CONTROL — the family against ITSELF (§13.5)\n")
        out["control_self_pct"] = round(self_pct, 2)
        ok = self_pct == 0.0
        out["proven"] = ok
        print("\n  self-comparison presence %.1f%%  ->  %s"
              % (self_pct, "the instrument can report absence"
                 if ok else "NOT PROVEN — it finds a ruin that is not there"))

    json.dump(out, open(os.path.join(EV, "PLANT-PRESENCE-%s.json" % a.tag), "w"), indent=2)
    print("\n  wrote %s"
          % os.path.relpath(os.path.join(EV, "PLANT-PRESENCE-%s.json" % a.tag), REPO))


if __name__ == "__main__":
    main()
