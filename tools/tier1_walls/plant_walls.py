#!/usr/bin/env python3
"""LOOP-PROCESS §4's PLANT — a picturesquely RUINED wall. It never lands and Rafe never sees it.

    *"For the blind critic, tier one has no shipping corpus to mix in, so 'name them cold' cannot
    run as designed. The substitute is a PLANT: one deliberately wrong candidate seeded into the
    set — for tier one, a picturesquely RUINED floor, cobwebbed and collapsed, among the USED-UP
    ones (bible §8.1). If the critic does not catch the plant, the round is VOID and its findings
    are not read. Not discounted — void."*

The wall's version of the same defect. Bible §8.1 holds that **nothing in the Paths is ruined;
everything is used up** — decay is traffic and indifference, not drama. So the plant is the
drama: collapsed courses with rubble spilling out of them, cobweb in every corner, a bloom of
pale moss, and cracks that fork like lightning rather than settling like stone.

It is built by THE SAME COMPOSER, from THE SAME material, on THE SAME ladder, and captured in
THE SAME scene through THE SAME rig. Every variable except the one under test is held: a seat
that culls it must be culling the RUIN and not the resolution, the palette or the lighting.

A seat that calls this atmospheric has not read the register, and the round it sits in is void.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_walls as CW      # noqa: E402

T = CW.T


def ruin(a, ladder, k):
    """Collapse, cobweb, moss and a forked crack. Drawn LOUD on purpose."""
    rng = np.random.default_rng(4242 + k)
    dark = ladder[0] * 0.45
    pale = ladder[-1] * 1.02

    # A COLLAPSED COURSE, with rubble spilling from it. Stone does not do this from use; it does
    # it from a roof coming down, which is a thing that has happened rather than a thing that is
    # wearing out.
    if k % 2 == 0:
        y0 = 4 + (k % 3) * 7
        w = 9 + (k % 4) * 3
        x0 = 2 + (k * 5) % (T - w - 2)
        a[y0:y0 + 6, x0:x0 + w] = dark
        for i in range(14):
            rx = int(rng.integers(x0 - 2, x0 + w + 2)) % T
            ry = int(rng.integers(y0 + 5, y0 + 11)) % T
            a[ry, rx] = ladder[2] * (0.7 + 0.5 * rng.random())

    # COBWEB in the corners: three strands and a sag. Nothing in continuous heavy use is
    # cobwebbed, which is the whole of §8.1 in one image.
    for cx, cy, sx, sy in ((0, 0, 1, 1), (T - 1, 0, -1, 1)):
        for i in range(1, 9):
            a[cy + sy * i, cx] = pale
            a[cy, cx + sx * i] = pale
            a[cy + sy * i, cx + sx * (9 - i)] = pale

    # MOSS: a pale bloom, because a picturesque ruin is always damp.
    my = 12 + (k % 5) * 3
    mx = 6 + (k * 7) % 18
    for dy in range(-3, 4):
        for dx in range(-4, 5):
            if dx * dx + dy * dy * 2 < 12 and 0 <= my + dy < T and 0 <= mx + dx < T:
                a[my + dy, mx + dx] = pale * 0.86

    # A FORKED CRACK. Settlement cracks in laid stone follow the joints; this one does not.
    x, y = int(rng.integers(4, T - 4)), 0
    while y < T - 1:
        a[y, x] = dark
        if 0 <= x + 1 < T:
            a[y, x + 1] = dark * 1.15
        y += 1
        x = int(np.clip(x + rng.integers(-1, 2), 1, T - 2))
        if y == T // 2:
            fx = int(np.clip(x + 4, 1, T - 2))
            for fy in range(y, T - 1):
                a[fy, fx] = dark
                fx = int(np.clip(fx + rng.integers(0, 2), 1, T - 2))
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(REPO, CW.ASSETS_REL))
    ap.add_argument("--out", default=os.path.join(REPO, "src/Presentation/assets/tier1_walls_plant"))
    a = ap.parse_args()

    man = json.load(open(os.path.join(a.src, "MANIFEST.json")))
    ladder = np.array(man["ladder"])
    tint = np.array(json.load(open(os.path.join(
        REPO, "src/Presentation/assets/tier1_ashlar/MANIFEST.json")))["material"]["tint"])

    if os.path.isdir(a.out):
        for f in os.listdir(a.out):
            if f.endswith(".png") or f.endswith(".png.import"):
                os.remove(os.path.join(a.out, f))
    os.makedirs(a.out, exist_ok=True)

    tiles = []
    for i, t in enumerate(man["tiles"]):
        # ⚠ RGBA, NOT RGB. The face tiles became face-only — the top band cut away with alpha,
        # because the cap is a field drawn underneath them. Flattening to RGB here would give the
        # plant an opaque top band the family does not have, and a seat culling THAT would be
        # culling the conversion, not the ruin. §4.1: the plant carries one defect, on one axis.
        src = np.asarray(Image.open(os.path.join(a.src, t["file"])).convert("RGBA")).astype(float)
        lum = src[..., :3] @ np.array([0.299, 0.587, 0.114])
        if t["cls"] != "void":
            lum = ruin(lum, ladder, i)
        rgba = np.stack([lum * tint[0], lum * tint[1], lum * tint[2], src[..., 3]], axis=2)
        p = os.path.join(a.out, t["file"])
        Image.fromarray(np.clip(np.rint(rgba), 0, 255).astype(np.uint8)).save(p)
        d = dict(t)
        d["sha256"] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        tiles.append(d)

    out = dict(man)
    out["family"] = man["family"].replace("_v1", "_PLANT_v1")
    out["tiles"] = tiles
    out["plant"] = ("LOOP-PROCESS §4. A picturesquely RUINED wall against bible §8.1's "
                    "'nothing is ruined, things are used up'. NEVER LANDS. NEVER SHOWN TO RAFE. "
                    "If the plant seat does not cull it, the round is VOID.")
    json.dump(out, open(os.path.join(a.out, "MANIFEST.json"), "w"), indent=2)
    print("plant: %d tiles -> %s" % (len(tiles), os.path.relpath(a.out, REPO)))


if __name__ == "__main__":
    main()
