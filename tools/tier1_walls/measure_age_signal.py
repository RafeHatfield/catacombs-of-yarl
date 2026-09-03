#!/usr/bin/env python3
"""DOES THE WALL'S AGE READ? — §13.8, on the capture, at the standing case.

    python3 tools/tier1_walls/measure_age_signal.py --controls   # the plant. Run this first.
    python3 tools/tier1_walls/measure_age_signal.py --scene ... --png ... --log ...

RULED at the gate: *"walls have opted out of history … wall aging at the base courses, keyed to
the existing traffic/age fields."* Built. This asks the only question that decides whether it was
built or merely intended: **is the age there loudly enough to exist, in the lit capture, at 1×.**

⚠ THE FIRST VERSION OF THIS INSTRUMENT WAS WRONG AND ITS OWN NUMBERS SAID SO.
It compared the base band of a face tile against the course above it, claiming the two were
"illumination-matched by construction, because they are the same cell". They are not. The base of
a wall is the SOUTHERN half of its cell and the lamp is to the south, so the two bands sit half a
tile apart along the steepest part of the gradient — and at four tiles that difference is the same
size as the signal. It reported Weber values scattered from −0.57 to +0.31 with the sign flipping
between neighbouring cells, which is the shape of noise, and it would have been read as *the aging
does not work* when what did not work was the measurement.

SO THE COMPARISON IS AN A/B AGAINST AN AGELESS BUILD OF THE SAME FAMILY.
The control is composed with AGES=1 and nothing else changed, laid on the SAME cells, in the SAME
scene, under the SAME lamp. Every lighting term cancels exactly rather than being modelled, which
is the only kind of cancellation worth trusting; what is left is the aging and nothing else. It is
also the positive control, for free: if the two builds measure the same, the aging is not running.
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

FLOOR_REFERENCE = 0.1440            # the FLOOR family's perceptual floor. A reference, not a bound.


def bands(scale, y0, hcell):
    """(base band, reference band) row slices in captured pixels, for a face cell."""
    base_from = CW.FACE_COURSES[-1][0]
    ref_from, ref_to = CW.FACE_TOP_ROW + CW.OCCLUSION_ROWS, CW.FACE_COURSES[-1][0]
    b = (int(round(y0 + base_from * scale)), int(round(y0 + hcell)))
    r = (int(round(y0 + ref_from * scale)), int(round(y0 + ref_to * scale)))
    return b, r


def measure(scene, png, log, assets):
    spec = json.load(open(os.path.join(REPO, scene)))
    man = json.load(open(os.path.join(assets, "MANIFEST.json")))
    pred = MA.predict(spec, man, MA.read_age_map(os.path.join(REPO, log)))
    eng = MA.engine_counts(os.path.join(REPO, log))
    got = dict(face=sum(1 for v in pred.values() if v[0] == "face"))
    if int(eng.get("face", -1)) != got["face"]:
        raise SystemExit("REFUSED: prediction disagrees with the engine on face count "
                         "(engine %s, this file %d)." % (eng.get("face"), got["face"]))

    ages = {t["id"]: t.get("age", 0) for t in man["tiles"]}
    img = np.array(Image.open(os.path.join(REPO, png)).convert("RGB")).astype(float)
    lum = (img * LF.W709).sum(2)
    g = LF.read_grid(os.path.join(REPO, log))
    scale = g["px"] / CW.T
    px, py = spec["player"]["x"], spec["player"]["y"]

    rows = []
    for (x, y), (cls, tid) in sorted(pred.items()):
        if cls != "face" or not LF.in_view(g, x, y):
            continue
        x0, y0, w, hcell = LF.cell_box(g, x, y)
        (b0, b1), (r0, r1) = bands(scale, y0, hcell)
        xa, xb = int(round(x0 + 3 * scale)), int(round(x0 + w - 3 * scale))
        base = lum[b0:b1, xa:xb]
        ref = lum[r0:r1, xa:xb]
        if base.size < 8 or ref.size < 8 or ref.mean() < 0.6:
            continue
        rows.append(dict(x=x, y=y, age=ages.get(tid, 0),
                         dist=round(float(np.hypot(x - px, y - py)), 2),
                         base=round(float(base.mean()), 3), ref=round(float(ref.mean()), 3),
                         weber=round(float((ref.mean() - base.mean()) / ref.mean()), 4),
                         levels=round(float(ref.mean() - base.mean()), 2)))
    return spec, man, rows


def report(rows, title):
    print(title)
    print("  %-8s %5s %6s %9s %9s %9s %8s"
          % ("cell", "age", "range", "course", "base", "Weber", "levels"))
    for r in sorted(rows, key=lambda r: (r["age"], r["dist"])):
        print("  (%2d,%2d) %5d %6.2f %9.2f %9.2f %9.4f %8.2f"
              % (r["x"], r["y"], r["age"], r["dist"], r["ref"], r["base"],
                 r["weber"], r["levels"]))
    print()
    print("  %-6s %4s %10s %10s %10s" % ("age", "n", "Weber", "levels", "vs 0.1440"))
    by = {}
    for r in rows:
        by.setdefault(r["age"], []).append(r)
    summary = {}
    for a in sorted(by):
        w = float(np.mean([r["weber"] for r in by[a]]))
        lv = float(np.mean([r["levels"] for r in by[a]]))
        summary[a] = dict(n=len(by[a]), weber=round(w, 4), levels=round(lv, 2))
        print("  %-6d %4d %10.4f %10.2f %10s"
              % (a, len(by[a]), w, lv, "above" if w >= FLOOR_REFERENCE else "BELOW"))
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default="src/Presentation/assets/tier0_harness/scenes/tier1_wall_review.json")
    ap.add_argument("--png", default="tools/tier1_walls/evidence/r13_family.png")
    ap.add_argument("--log", default="tools/tier1_walls/evidence/r13_family.log")
    ap.add_argument("--assets", default=os.path.join(REPO, CW.ASSETS_REL + "_compensated"))
    ap.add_argument("--ageless-png", default="tools/tier1_walls/evidence/r14_ageless.png")
    ap.add_argument("--ageless-log", default="tools/tier1_walls/evidence/r14_ageless.log")
    ap.add_argument("--ageless-assets",
                    default=os.path.join(REPO, CW.ASSETS_REL + "_compensated_ageless"))
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--tag", default="age")
    a = ap.parse_args()

    spec, man, rows = measure(a.scene, a.png, a.log, a.assets)
    _, man0, rows0 = measure(a.scene, a.ageless_png, a.ageless_log, a.ageless_assets)
    if not rows:
        raise SystemExit("no measurable face cells in view")
    ref = {(r["x"], r["y"]): r for r in rows0}

    paired = []
    for r in rows:
        c = ref.get((r["x"], r["y"]))
        if c is None or c["ref"] < 0.6:
            continue
        # THE A/B. Both terms are the same cell's base-over-course ratio; dividing them cancels
        # the lamp, the range, the tint and the tile's own bond, and leaves the aging.
        aged = r["base"] / max(r["ref"], 1e-6)
        sharp = c["base"] / max(c["ref"], 1e-6)
        paired.append(dict(x=r["x"], y=r["y"], age=r["age"], dist=r["dist"],
                           aged_ratio=round(aged, 4), sharp_ratio=round(sharp, 4),
                           weber=round(float((sharp - aged) / max(sharp, 1e-6)), 4),
                           levels=round(float(c["base"] - r["base"]), 2),
                           lit=round(float(r["ref"]), 2)))

    print("AGE AT THE BASE COURSE — the aged build against an AGELESS build of the same family,")
    print("cell for cell, under the same lamp. Every lighting term cancels.")
    print("  %-8s %5s %6s %8s %10s %10s %9s %8s"
          % ("cell", "age", "range", "lit", "aged b/c", "sharp b/c", "Weber", "levels"))
    for r in sorted(paired, key=lambda r: (r["age"], r["dist"])):
        print("  (%2d,%2d) %5d %6.2f %8.2f %10.4f %10.4f %9.4f %8.2f"
              % (r["x"], r["y"], r["age"], r["dist"], r["lit"], r["aged_ratio"],
                 r["sharp_ratio"], r["weber"], r["levels"]))

    by = {}
    for r in paired:
        by.setdefault(r["age"], []).append(r)
    summary = {}
    print()
    print("  %-6s %4s %10s %10s %9s   %s" % ("age", "n", "Weber", "levels", "lit", "vs 0.1440"))
    for ag in sorted(by):
        w = float(np.mean([r["weber"] for r in by[ag]]))
        lv = float(np.mean([r["levels"] for r in by[ag]]))
        li = float(np.mean([r["lit"] for r in by[ag]]))
        summary[ag] = dict(n=len(by[ag]), weber=round(w, 4), levels=round(lv, 2),
                           lit=round(li, 2))
        print("  %-6d %4d %10.4f %10.2f %9.2f   %s"
              % (ag, len(by[ag]), w, lv, li, "above" if w >= FLOOR_REFERENCE else "BELOW"))

    out = dict(produced_by="tools/tier1_walls/measure_age_signal.py", scene=spec["name"],
               capture=a.png, control=a.ageless_png, family=man["family"],
               reference_floor=FLOOR_REFERENCE, cells=paired, by_age=summary)

    # §13.9: NAME THE ILLUMINATION. A row's verdict is only about the light it was measured at.
    standing = [r for r in paired if r["dist"] <= 3.2 and r["age"] > 0]
    if standing:
        w = float(np.mean([r["weber"] for r in standing]))
        out["standing_case"] = dict(n=len(standing), weber=round(w, 4),
                                    lit=round(float(np.mean([r["lit"] for r in standing])), 2))
        print()
        print("  THE STANDING CASE (<=3.2 tiles), which is the one the gate ruled §6.5 down to:")
        print("    n=%d  Weber %.4f  at a delivered course value of %.2f/255"
              % (len(standing), w, out["standing_case"]["lit"]))

    if a.controls:
        # The control is structural rather than added: the ageless build IS the plant. If it
        # measured the same as the aged one, every number above would be zero by construction.
        zero = [r for r in paired if r["age"] == 0]
        nz = [r for r in paired if r["age"] > 0]
        moved = bool(nz) and abs(float(np.mean([r["weber"] for r in nz]))) > 0.02
        flat = (not zero) or abs(float(np.mean([r["weber"] for r in zero]))) < 0.02
        print()
        print("POSITIVE CONTROL")
        print("  aged cells move against the ageless build : %s" % ("YES" if moved else "NO — SILENT"))
        print("  age-0 cells do NOT move (sealed stays sharp): %s" % ("YES" if flat else "NO"))
        out["control"] = dict(aged_cells_move=moved, sealed_cells_flat=flat)

    p = os.path.join(EV, "AGE-SIGNAL-%s.json" % a.tag)
    json.dump(out, open(p, "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(p, REPO))


if __name__ == "__main__":
    main()
