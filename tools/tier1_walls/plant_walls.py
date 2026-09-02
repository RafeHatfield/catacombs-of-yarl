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


def ruin_cap(src_dir, out_dir):
    """Ruin the CAP FIELD, because since the cap pass the cap is what is actually drawn.

    ⚠ THIS EXISTS BECAUSE THE PLANT HAD STOPPED BEING A PLANT. `ruin()` above marks the wall
    family's tiles — and after the cap pass the cell's base is a CAP WINDOW and the family's
    top_h/top_v tiles are never rendered at all (`face_suppressed=192`, `face=24`). Measured on
    the round-10 captures, the plant differed from the family in **0.54% of the frame, 21 cells,
    and only 0.15% of pixels by more than eight levels.** A control that is absent from 99.5% of
    the picture cannot be caught, and rounds 9 and 10 both died on it — not on the seat.

    THE RUIN IS APPLIED TO THE ASSEMBLED FIELD, NOT PER WINDOW. Ruining each 32px window
    independently would break the seamlessness the cap is built on, and a seat culling BROKEN
    SEAMS has not culled the ruin — §4.1: the plant carries one defect, on one axis. So the 256
    windows are reassembled into the one 512px field, ruined at field scale, and re-cut on the
    same grid with the same ids.
    """
    man = json.load(open(os.path.join(src_dir, "MANIFEST.json")))
    n, T_ = man["field_tiles"], man["tile"]
    files = {t["id"]: t["file"] for t in man["tiles"]}
    field = np.zeros((n * T_, n * T_, 3), float)
    for key, tid in man["table"].items():
        gx, gy = (int(v) for v in key.split(","))
        field[gy * T_:(gy + 1) * T_, gx * T_:(gx + 1) * T_] = np.asarray(
            Image.open(os.path.join(src_dir, files[tid])).convert("RGB")).astype(float)

    lum = field @ np.array([0.299, 0.587, 0.114])
    rng = np.random.default_rng(90210)
    dark, pale = lum.mean() * 0.35, lum.mean() * 1.45
    S = n * T_

    # A COLLAPSED PATCH with rubble spilling out of it — several tiles across, so it is a hole in
    # the mass rather than a mark repeated in every cell (§8.3's motif trap runs both ways).
    for k in range(5):
        cy, cx = int(rng.integers(0, S)), int(rng.integers(0, S))
        rh, rw = int(rng.integers(20, 46)), int(rng.integers(26, 60))
        ys, xs = np.arange(cy, cy + rh) % S, np.arange(cx, cx + rw) % S
        lum[np.ix_(ys, xs)] = dark
        for _ in range(90):
            ry, rx = (cy + int(rng.integers(-8, rh + 14))) % S, (cx + int(rng.integers(-8, rw + 14))) % S
            lum[ry, rx] = pale * (0.45 + 0.4 * rng.random())

    # MOSS, a damp pale bloom. Nothing in continuous heavy use blooms.
    for k in range(7):
        cy, cx = int(rng.integers(0, S)), int(rng.integers(0, S))
        for dy in range(-11, 12):
            for dx in range(-15, 16):
                if dx * dx + dy * dy * 2 < 150:
                    lum[(cy + dy) % S, (cx + dx) % S] *= 1.55

    # A FORKED CRACK that does not follow any joint, running the height of the field.
    x, y = int(rng.integers(0, S)), 0
    forks = []
    while y < S - 1:
        lum[y, x % S] = dark
        lum[y, (x + 1) % S] = dark * 1.2
        y += 1
        x = int(x + rng.integers(-1, 2))
        if y % (S // 3) == 0:
            forks.append((y, x + 9))
    for fy, fx in forks:
        while fy < S - 1:
            lum[fy, fx % S] = dark
            fy += 1
            fx = int(fx + rng.integers(0, 2))

    # COBWEB: long sagging strands, drawn across the field rather than in every cell's corner.
    for k in range(9):
        y0, x0 = int(rng.integers(0, S)), int(rng.integers(0, S))
        for i in range(70):
            lum[(y0 + i // 3) % S, (x0 + i) % S] = pale
            lum[(y0 + i) % S, (x0 + i // 3) % S] = pale

    scale = np.divide(lum, field @ np.array([0.299, 0.587, 0.114]),
                      out=np.ones_like(lum), where=(field.sum(2) > 1e-6))
    out = np.clip(field * scale[..., None], 0, 255).astype(np.uint8)

    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".png") or f.endswith(".png.import"):
            os.remove(os.path.join(out_dir, f))
    for key, tid in man["table"].items():
        gx, gy = (int(v) for v in key.split(","))
        Image.fromarray(out[gy * T_:(gy + 1) * T_, gx * T_:(gx + 1) * T_]).save(
            os.path.join(out_dir, files[tid]))
    for t in man["tiles"]:                       # the void windows pass through untouched
        dst = os.path.join(out_dir, t["file"])
        if not os.path.exists(dst):
            shutil.copyfile(os.path.join(src_dir, t["file"]), dst)
    man["family"] = man["family"].replace("_v1", "_PLANT_v1")
    man["plant"] = ("the cap field, ruined at FIELD scale. LOOP-PROCESS §4. Never lands.")
    json.dump(man, open(os.path.join(out_dir, "MANIFEST.json"), "w"), indent=2)
    print("plant cap: %d windows -> %s" % (len(man["table"]), os.path.relpath(out_dir, REPO)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(REPO, CW.ASSETS_REL))
    ap.add_argument("--out", default=os.path.join(REPO, "src/Presentation/assets/tier1_walls_plant"))
    ap.add_argument("--cap-src", default=os.path.join(REPO, "src/Presentation/assets/tier1_cap"))
    ap.add_argument("--cap-out", default=os.path.join(REPO,
                    "src/Presentation/assets/tier1_cap_plant"))
    a = ap.parse_args()

    ruin_cap(a.cap_src, a.cap_out)

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
