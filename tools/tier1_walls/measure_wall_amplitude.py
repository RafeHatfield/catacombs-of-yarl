#!/usr/bin/env python3
"""SECTION 13.8 ON THE WALL — is the material there LOUDLY ENOUGH TO EXIST, in the lit capture?

    *"A signal authored below the perceptual floor is ABSENT. Everything authored proves readable
    amplitude under the ratified rig at 1x."*  — bible section 13.8, LOCKED at the device gate

and its sibling, from the floor session that ran alongside this one:

    *"A signal is absent if the rig does not deliver enough of it to be represented ... an
    instrument that measures the SOURCE has not measured the ASSET."*  — section 13.9

So this instrument uses the source for ONE thing only — to know which pixels are joints and which
are blocks, which the composer knows exactly — and takes every number off the CAPTURE. The
statistic is Weber contrast against the feature's own local brightness, per section 13.8's own
warning: do not flatten the lamp to measure amplitude, because dividing by a local blur cancels
any signal that covers a large fraction of its own neighbourhood, which is what a surface texture
is. A ratio divides the lamp out for free.

⚠ WHAT THIS INSTRUMENT CANNOT DO, STATED BECAUSE THE ALTERNATIVE IS TO INVENT A NUMBER.
Section 13.8 sets the floor from **verdicts already given** — one signal a human ruled present and
one the same human ruled absent, measured the same way, in the same capture, under the same rig —
and forbids a threshold from being picked. **No human has yet ruled on a wall signal.** There is
therefore NO WALL PERCEPTUAL FLOOR and this session does not propose one. What is reported is the
delivered amplitude and its comparison with the FLOOR family's floor of 0.1440, which is the
nearest derived quantity in the project and is a REFERENCE rather than a bound. The first pair of
wall verdicts the gate produces is what turns this into a threshold.
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
from mask_census import build, is_wall   # noqa: E402

FLOOR_FAMILY_PERCEPTUAL_FLOOR = 0.1440      # section 13.8, derived for the FLOOR. A reference.


def ring_of(wall, w, h, x, y, cap=2):
    for r in range(1, cap + 1):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and not wall[ny][nx]:
                    return r
    return cap + 1


def predict(spec, man):
    """Which tile the engine laid on each wall cell — the same rules, restated.

    A third copy of this arithmetic would be indefensible if it were not CHECKED: the engine
    prints its own face/top/void counts into every capture log, and `main` compares them. A
    prediction that disagrees with the engine is reported and the measurement is refused, rather
    than measuring the wrong pixels and reporting a confident number about them.
    """
    wall, w, h = build(spec)
    sv, sh = man["salts"]["v"], man["salts"]["h"]
    ef, nv = man["edge_families"], man["variants"]
    out = {}
    for y in range(h):
        for x in range(w):
            if not wall[y][x]:
                continue
            ring = ring_of(wall, w, h, x, y)
            if ring > 2:
                out[(x, y)] = ("void", man["table"]["void"]["0"])
                continue
            south_open = (0 <= y + 1 < h) and not wall[y + 1][x]
            ns = ((0 <= y - 1 < h) and not wall[y - 1][x]) or south_open
            ew = ((0 <= x - 1 < w) and not wall[y][x - 1]) \
                or ((0 <= x + 1 < w) and not wall[y][x + 1])
            if ring == 2:
                ns = _facing(wall, w, h, x, y, vertical=False)
                ew = _facing(wall, w, h, x, y, vertical=True)
            horiz = ns or not ew
            if horiz:
                ka = CW.h(sv, "v", x, y) % ef
                kb = CW.h(sv, "v", x + 1, y) % ef
            else:
                ka = CW.h(sh, "h", x, y) % ef
                kb = CW.h(sh, "h", x, y + 1) % ef
            var = CW.h(90777, "h" if horiz else "v", x, y) % nv
            cls = "face" if south_open else ("top_h" if horiz else "top_v")
            out[(x, y)] = (cls, man["table"][cls]["%d,%d,%d" % (ka, kb, var)])
    return out


def _facing(wall, w, h, x, y, vertical):
    for dx, dy in ((-1, 0), (1, 0)) if vertical else ((0, -1), (0, 1)):
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or not wall[ny][nx]:
            continue
        if vertical:
            if (nx - 1 >= 0 and not wall[ny][nx - 1]) or (nx + 1 < w and not wall[ny][nx + 1]):
                return True
        else:
            if (ny - 1 >= 0 and not wall[ny - 1][nx]) or (ny + 1 < h and not wall[ny + 1][nx]):
                return True
    return False


def engine_counts(log_path):
    txt = open(log_path, "rb").read().decode("utf8", "replace")
    for line in txt.splitlines():
        if "[Tier1] boundary wall:" in line and "DIAG" not in line:
            # Parse only the leading key=value tokens, stopping at the first bracketed group:
            # `planes(top=... face=...)` reuses the words "top" and "face" for the PLANE VALUES,
            # and a naive split would compare a tile count against a luminance.
            d, depth = {}, 0
            for tok in line.split():
                depth += tok.count("(") - tok.count(")")
                if depth > 0 or tok.count(")") > tok.count("("):
                    continue
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    if k not in d:
                        d[k] = v
            return d
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--png", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--assets", default=os.path.join(REPO, CW.ASSETS_REL))
    ap.add_argument("--tag", default="wall")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    man = json.load(open(os.path.join(a.assets, "MANIFEST.json")))
    pred = predict(spec, man)

    # THE CROSS-CHECK, BEFORE A SINGLE PIXEL IS MEASURED.
    eng = engine_counts(os.path.join(REPO, a.log))
    got = dict(face=sum(1 for v in pred.values() if v[0] == "face"),
               top=sum(1 for v in pred.values() if v[0].startswith("top")),
               void=sum(1 for v in pred.values() if v[0] == "void"))
    said = dict(face=int(eng.get("face", -1)), top=int(eng.get("top", -1)),
                void=int(eng.get("void", "-1(").split("(")[0]))
    if got != said:
        raise SystemExit("REFUSED: the prediction disagrees with the engine.\n"
                         "  engine says %s\n  this file says %s\n"
                         "Measuring under a disagreement would report a confident number about "
                         "the wrong pixels." % (said, got))

    img = np.array(Image.open(os.path.join(REPO, a.png)).convert("RGB")).astype(float)
    lum = (img * LF.W709).sum(2)
    g = LF.read_grid(os.path.join(REPO, a.log))
    px, py = spec["player"]["x"], spec["player"]["y"]
    scale = int(round(g["px"] / CW.T))

    src = {}
    for t in man["tiles"]:
        src[t["id"]] = (np.asarray(Image.open(os.path.join(a.assets, t["file"]))
                                   .convert("RGB")).astype(float) @ np.array([.299, .587, .114]))

    step = man["ladder_step"]
    rows = []
    for (x, y), (cls, tid) in sorted(pred.items()):
        if cls == "void" or not LF.in_view(g, x, y):
            continue
        s = src[tid]
        # THE MASK COMES FROM THE SOURCE, THE VALUES FROM THE CAPTURE (section 13.9). A joint is
        # a pixel the composer drew a rung and a half or more below its own plane's median.
        plane = s[CW.FACE_TOP_ROW:] if cls == "face" else s
        band0 = CW.FACE_TOP_ROW if cls == "face" else 0
        med = np.median(plane)
        jm = plane <= med - 1.5 * step
        bm = plane >= med - 0.5 * step
        if jm.sum() < 8 or bm.sum() < 8:
            continue
        x0, y0, w, hh = LF.cell_box(g, x, y)
        sub = lum[int(round(y0)) + band0 * scale: int(round(y0 + hh)),
                  int(round(x0)): int(round(x0 + w))]
        if sub.shape[0] < plane.shape[0] * scale or sub.shape[1] < CW.T * scale:
            continue
        big_j = np.kron(jm, np.ones((scale, scale), bool))[:sub.shape[0], :sub.shape[1]]
        big_b = np.kron(bm, np.ones((scale, scale), bool))[:sub.shape[0], :sub.shape[1]]
        jv, bv = sub[big_j].mean(), sub[big_b].mean()
        if bv < 1.0:
            continue
        rows.append(dict(x=x, y=y, cls=cls,
                         dist=round(float(np.hypot(x - px, y - py)), 2),
                         joint=round(float(jv), 3), block=round(float(bv), 3),
                         weber=round(float((bv - jv) / bv), 4),
                         levels=round(float(bv - jv), 2)))

    if not rows:
        raise SystemExit("no measurable wall cells in view")

    print("SECTION 13.8 ON THE WALL — delivered joint amplitude, by range from the lamp")
    print("  %-8s %6s %8s %8s %9s %8s" % ("cell", "range", "block", "joint", "Weber", "levels"))
    for r in sorted(rows, key=lambda r: r["dist"]):
        print("  (%2d,%2d) %6.2f %8.2f %8.2f %9.4f %8.2f"
              % (r["x"], r["y"], r["dist"], r["block"], r["joint"], r["weber"], r["levels"]))

    by_band = {}
    for r in rows:
        b = int(r["dist"])
        by_band.setdefault(b, []).append(r)
    print()
    print("  %-8s %5s %9s %9s   %s" % ("range", "n", "Weber", "levels", "vs the FLOOR family's"))
    print("  %-8s %5s %9s %9s   %s" % ("", "", "", "", "0.1440 (a reference, not a bound)"))
    summary = {}
    for b in sorted(by_band):
        w = np.mean([r["weber"] for r in by_band[b]])
        lv = np.mean([r["levels"] for r in by_band[b]])
        summary[b] = dict(n=len(by_band[b]), weber=round(float(w), 4), levels=round(float(lv), 2))
        print("  %-8d %5d %9.4f %9.2f   %s"
              % (b, len(by_band[b]), w, lv,
                 "above" if w >= FLOOR_FAMILY_PERCEPTUAL_FLOOR else "BELOW"))

    print()
    print("  WEBER CONTRAST IS PRESERVED BY THE RIG - the pipeline is multiplicative, measured at")
    print("  0.5000 with a worst-cell error of 0.0006 - so the ratio column is nearly flat with")
    print("  range by construction. THE LEVELS COLUMN IS THE ONE THAT MOVES, and it is the one")
    print("  eight bits can run out of: a joint two levels below its block is a joint nobody can")
    print("  see, whatever its ratio says. That is section 13.9 in one table.")

    out = dict(produced_by="tools/tier1_walls/measure_wall_amplitude.py",
               scene=spec["name"], capture=a.png, family=man["family"],
               reference_floor=FLOOR_FAMILY_PERCEPTUAL_FLOOR,
               reference_note="The FLOOR family's perceptual floor. There is no wall floor: "
                              "section 13.8 derives one from a human's ruled-present and "
                              "ruled-absent pair and no such pair exists for walls yet.",
               cells=rows, by_range=summary)
    p = os.path.join(EV, "WALL-AMPLITUDE-%s.json" % a.tag)
    json.dump(out, open(p, "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(p, REPO))


if __name__ == "__main__":
    main()
