#!/usr/bin/env python3
"""THE CONNECTION TEST — does the lamp's energy reach the floor at all?

Issue #174. `tier1_polish.gdshader`'s `light()` read `LIGHT_COLOR` and never `LIGHT_ENERGY`,
under a comment asserting that LIGHT_COLOR carries the energy. It does not: a custom `light()`
that never multiplies by LIGHT_ENERGY discards it. Every floor tile carries a ShaderMaterial
built from that shader, so the floor was lit at energy 1.0 while every wall, cap and prop beside
it was lit at Ruling 56's 1.6 — two planes, two arithmetics.

WHAT THIS INSTRUMENT ASKS, AND WHAT IT REFUSES TO ASK. It asks exactly one question: **does the
floor's delivered value move when the lamp's energy moves, and does it move as the arithmetic
predicts.** It does not ask whether the frame is prettier. It cannot: the fix RAISES `delivered`,
`pow(delivered, polish_exp)` amplifies the polish mask, and the mask's four discrete
reflectivities are a dither a blind seat already culled (round 28, flip 1). **A louder frame is
the fix working.** Anyone reading a worse picture here as a failed fix has read the wrong number.

THE PREDICTION, stated before the measurement, because a test that fits itself to its answer is
not a test:

    diffuse  = COLOR * LIGHT_COLOR * LIGHT_ENERGY          -> LINEAR in energy
    spec     = polish * gain * pow(delivered, exp)          -> delivered carries energy, so with
               where delivered = max(LIGHT_COLOR.rgb) * E      exp=2 the term is QUADRATIC in it
                                 clamped to [0,1]             until `delivered` clamps at 1.0

    So: floor lit / floor unlit rises with energy, superlinearly near the lamp, and the
    ambient-only pass (energy 0) is untouched by either term.

HOW IT DEMONSTRATES IT CAN FAIL (§13.5, LOOP-PROCESS §4). It does not need a synthetic plant:
**the pre-fix captures are the failing case, and they are kept.** Run it on `conn_before_*` and
it reports `identical_share = 1.000` on the floor — every floor pixel byte-identical across
energy 0, 1.6 and 8.0 — while the wall column moves. That is the instrument printing NO
CONNECTION on real data. A pass counts only because that failure is on record beside it.

Ground truth for cell positions comes from the ENGINE'S OWN LOGGED GRID (§13.10), never from an
assumed centring.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "tier1_walls"))
import light_field as LF          # noqa: E402
from mask_census import build     # noqa: E402

# The dungeon view has interface drawn inside it (zoom buttons, minimap, RIG panel, Msg button,
# the player sprite). A cell whose box overlaps one of those is measuring interface, not surface
# — the failure light_field.scene_mask was written for. Here the guard is cruder and sufficient:
# cells are sampled with an inset, and the player's own cell and its eight neighbours are dropped.
INSET = 6


def cell_pixels(img, g, x, y):
    x0, y0, w, h = LF.cell_box(g, x, y)
    p = img[int(y0) + INSET:int(y0 + h) - INSET, int(x0) + INSET:int(x0 + w) - INSET]
    return p if p.size else None


def classify(spec):
    """floor / wall, from the scene's own carve list. Nothing is inferred from pixels."""
    wall, w, h = build(spec)
    out = {}
    for y in range(h):
        for x in range(w):
            out[(x, y)] = "wall" if wall[y][x] else "floor"
    return out, w, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--arm", action="append", required=True, metavar="ENERGY:PNG:LOG",
                    help="one energy arm, e.g. 1.6:evidence/conn_after_e1.6.png:...log")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--json-out")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(REPO, a.scene)))
    cls, w, h = classify(spec)
    px, py = spec["player"]["x"], spec["player"]["y"]

    arms = []
    for s in a.arm:
        e, png, log = s.split(":")
        img = np.array(Image.open(os.path.join(REPO, png)).convert("RGB")).astype(np.int32)
        arms.append(dict(energy=float(e), png=png, log=log, img=img,
                         g=LF.read_grid(os.path.join(REPO, log))))
    base = arms[0]
    for arm in arms[1:]:
        if arm["img"].shape != base["img"].shape:
            raise SystemExit("arms differ in frame size — not a control")
        if arm["g"] != base["g"]:
            raise SystemExit("arms disagree about the engine's grid — the camera moved (§13.10)")

    # Which cells are sampled: fully in view, not the player's own cell or its neighbours.
    cells = [(x, y) for (x, y) in cls
             if LF.in_view(base["g"], x, y) and max(abs(x - px), abs(y - py)) > 1]

    def band(x, y):
        d = float(np.hypot(x - px, y - py))
        return "<=2" if d <= 2.0 else ("2-4" if d <= 4.0 else ">4")

    # ── 1. THE CONNECTION. Byte-identity of the two planes across the energy arms. ────────────
    ident = {}
    for plane in ("floor", "wall"):
        tot = same = 0
        for (x, y) in cells:
            if cls[(x, y)] != plane:
                continue
            p0 = cell_pixels(base["img"], base["g"], x, y)
            if p0 is None or p0.size == 0:
                continue
            for arm in arms[1:]:
                p1 = cell_pixels(arm["img"], arm["g"], x, y)
                tot += p0.size
                same += int((p0 == p1).sum())
        ident[plane] = dict(pixels=tot, identical=same,
                            identical_share=(same / tot if tot else float("nan")))

    # ── 2. THE RESPONSE. Mean delivered luminance per plane per band per energy. ──────────────
    resp = {}
    for arm in arms:
        lum = (arm["img"] * LF.W709).sum(2)
        for plane in ("floor", "wall"):
            for b in ("<=2", "2-4", ">4"):
                vals = []
                for (x, y) in cells:
                    if cls[(x, y)] != plane or band(x, y) != b:
                        continue
                    p = cell_pixels(lum, arm["g"], x, y)
                    if p is not None and p.size:
                        vals.append(float(p.mean()))
                if vals:
                    resp.setdefault(f"{plane}|{b}", {})[f"{arm['energy']:g}"] = dict(
                        n=len(vals), mean=float(np.mean(vals)))

    print(f"=== connection test — {a.tag} ===")
    print(f"scene   {a.scene}")
    print(f"arms    " + ", ".join(f"E={x['energy']:g} ({os.path.basename(x['png'])})" for x in arms))
    print(f"grid    {base['g']}   cells sampled: {len(cells)}")
    print()
    print("1. BYTE-IDENTITY ACROSS THE ENERGY ARMS  (1.000 = the knob does not reach this plane)")
    for plane in ("floor", "wall"):
        d = ident[plane]
        print(f"   {plane:<6} identical {d['identical']:>9}/{d['pixels']:<9} "
              f"= {d['identical_share']:.4f}")
    print()
    print("2. DELIVERED MEAN LUMINANCE BY BAND — and the ratio to the lowest energy arm")
    lo = f"{arms[0]['energy']:g}"
    hdr = "   ".join(f"E={x['energy']:g}" for x in arms)
    print(f"   {'plane|band':<14} {hdr}      ratios vs E={lo}")
    for key in sorted(resp, key=lambda k: (k.split("|")[0], ["<=2", "2-4", ">4"].index(k.split("|")[1]))):
        row = resp[key]
        means = [row[f"{x['energy']:g}"]["mean"] for x in arms]
        rats = [m / means[0] if means[0] > 1e-9 else float("nan") for m in means]
        n = row[lo]["n"]
        print(f"   {key:<14} " + "  ".join(f"{m:8.2f}" for m in means)
              + "     " + "  ".join(f"{r:6.3f}" for r in rats) + f"    n={n}")

    # ── 3. ONE ARITHMETIC. Lit contribution against the energy-0 arm. ─────────────────────────
    #
    # THE CLAIM THE FIX MAKES is not "the floor got brighter" — it is "the floor and the wall are
    # now lit by the SAME EXPRESSION". That is checkable and it is checked here rather than
    # asserted: with the specular nulled (`polish_gain: 0.0`) the floor's light() reduces to
    # `COLOR * LIGHT_COLOR * LIGHT_ENERGY`, which is the default pass every wall already runs, so
    # **the two planes must respond to a doubling of energy by the same factor.** With the
    # specular live the floor must exceed it, because `pow(delivered, 2)` is quadratic — and by
    # how much is the specular's share, which is the quantity §6.5 needs.
    #
    # Measured as LIT CONTRIBUTION, L(E) - L(0), because the ambient pass is not the lamp and
    # including it would dilute every ratio toward 1.0 by a different amount on each plane.
    lit = {}
    if abs(arms[0]["energy"]) < 1e-9:
        for key, row in resp.items():
            amb = row[lo]["mean"]
            ser = {}
            for arm in arms[1:]:
                k = f"{arm['energy']:g}"
                ser[k] = row[k]["mean"] - amb
            lit[key] = dict(ambient=amb, lit=ser)
        print()
        print("3. LIT CONTRIBUTION  L(E) - L(0), and its ratio between consecutive arms")
        print("   (nulled polish -> floor and wall must agree; live polish -> floor must exceed)")
        es = [f"{x['energy']:g}" for x in arms[1:]]
        print(f"   {'plane|band':<14} ambient   " + "   ".join(f"lit@{e}" for e in es) + "     ratio")
        for key in sorted(lit, key=lambda k: (k.split("|")[0],
                                              ["<=2", "2-4", ">4"].index(k.split("|")[1]))):
            d = lit[key]
            vals = [d["lit"][e] for e in es]
            rat = [vals[i + 1] / vals[i] if abs(vals[i]) > 1e-6 else float("nan")
                   for i in range(len(vals) - 1)]
            print(f"   {key:<14} {d['ambient']:7.2f}   "
                  + "   ".join(f"{v:7.2f}" for v in vals)
                  + "     " + "  ".join(f"{r:6.3f}" for r in rat))

    out = dict(tag=a.tag, scene=a.scene, grid=base["g"], lit_contribution=lit,
               arms=[dict(energy=x["energy"], png=x["png"], log=x["log"]) for x in arms],
               cells_sampled=len(cells), identity=ident, response=resp)
    if a.json_out:
        json.dump(out, open(os.path.join(REPO, a.json_out), "w"), indent=2)
        print(f"\nwrote {a.json_out}")


if __name__ == "__main__":
    main()
