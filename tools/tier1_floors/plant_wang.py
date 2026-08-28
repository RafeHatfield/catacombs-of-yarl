#!/usr/bin/env python3
"""THE PLANT for the edge-matched family. LOOP-PROCESS §4, floor session two.

    For the blind critic, tier one has no shipping corpus to mix in, so "name them cold" cannot
    run as designed. The substitute is a PLANT: one deliberately wrong candidate seeded into the
    set — for tier one, a picturesquely RUINED floor, cobwebbed and collapsed, among the USED-UP
    ones (bible §8.1).

    If the critic does not catch the plant, the round is VOID and its findings are not read.

Built from THE SAME edge-matched tiles as the candidate, with the ruin applied on top. Everything
that could let a seat spot it by craft is held constant — same bond, same enclosure, same palette,
same crossings, same rig, same scene. What differs is the register, which is the axis the control
claims (LOOP-PROCESS §4.1).

Session one's first plant was too subtle and voided its own round: a 4px hole read as a pit, moss
in the joints read as a hue shift, a dithered cobweb read as speckle. The amplitudes here are the
ones that survived that correction — a hole you could fall into, strands rather than speckle, moss
in blobs. Picturesque is the operative word.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_wang as CW      # noqa: E402
import compose_family as CF    # noqa: E402
import field_laws as FL        # noqa: E402

T = CW.T
ASSETS_REL = "src/Presentation/assets/tier1_wang_plant"
ASSETS = os.path.join(REPO, ASSETS_REL)
SRC = CW.ASSETS


def ruin(img, mat, seed):
    """Bake the ruin over an edge-matched tile. The bond and its crossings are untouched, so the
    plant still tiles and still encloses — only the register is wrong."""
    rng = np.random.default_rng(seed)
    L = FL.RI.lum(img.astype(float))

    # A collapse with real depth, a quarter of the tile.
    cy, cx = rng.integers(10, T - 10), rng.integers(10, T - 10)
    edge = 6.0 + rng.normal(0, 0.4, 32)
    for yy in range(T):
        for xx in range(T):
            dy, dx = yy - cy, xx - cx
            d = (dy * dy + dx * dx) ** 0.5
            ang = int(((np.arctan2(dy, dx) + np.pi) / (2 * np.pi)) * 31) % 32
            r = edge[ang]
            if d <= r - 1.5:
                L[yy, xx] = 6.0
            elif d <= r:
                L[yy, xx] = mat["lum_lo"] * 0.35
            elif d <= r + 1.6 and rng.random() < 0.55:
                L[yy, xx] = min(255.0, mat["lum_hi"] * 1.12)

    # Cobweb strands with a sag — not a dither.
    web = min(255.0, mat["lum_hi"] * 1.22)
    for k in range(4):
        span = 9 + k * 4
        for i in range(span):
            t = i / max(1.0, span - 1.0)
            yy = int(round(t * span))
            xx = int(round((1 - t) * span + 2.5 * np.sin(t * np.pi)))
            if 0 <= yy < T and 0 <= xx < T:
                L[yy, xx] = web

    out = CF.colourise(CF.quantise(L, mat["ladder"]), mat["tint"])

    # Moss in blobs. Living green, where the register says nothing lives.
    n = CF.wrap_noise(T, 4, rng)
    moss = n > float(np.percentile(n, 78))
    for yy in range(T):
        for xx in range(T):
            if moss[yy, xx]:
                out[yy, xx] = np.array([46.0, 92.0, 40.0]) * (0.75 + 0.5 * rng.random())
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()

    src = json.load(open(os.path.join(SRC, "MANIFEST.json")))
    mat = src["material"]
    os.makedirs(ASSETS, exist_ok=True)

    man = dict(src)          # same families, salts, seed, crossings, cross-check vector
    man["family"] = "boundary_floor_wang_PLANT"
    man["what"] = ("LOOP-PROCESS §4's plant, built from the SAME edge-matched tiles as the "
                   "candidate with the ruin baked on top. Never lands, never shown to Rafe. If "
                   "the seat does not catch it, the round is VOID.")

    print("THE PLANT — the edge-matched family, ruined")
    for key in ("base", "channel"):
        out = []
        for e in src[key]:
            im = np.asarray(Image.open(os.path.join(SRC, e["file"])).convert("RGB"))
            r = ruin(im, mat, a.seed + e["id"])
            p = os.path.join(ASSETS, e["file"].replace("tier1_wang_", "tier1_wangp_"))
            Image.fromarray(r).save(p)
            out.append(dict(e, file=os.path.basename(p), sha256=FL.sha256_file(p)))
        man[key] = out
        print("  %-8s %d tiles ruined" % (key, len(out)))

    # Same wall mocks, same names the theme will ask for.
    stub = os.path.join(REPO, "src/Presentation/assets/tier0_harness/stub")
    for tid in list(range(9010, 9035)) + [9040, 9041]:
        s = os.path.join(stub, "tier0_stub_%d.png" % tid)
        if os.path.exists(s):
            shutil.copyfile(s, os.path.join(ASSETS, "tier1_wangp_%d.png" % tid))

    floor_ids = [e["id"] for e in man["base"]]
    lines = ["# GENERATED by tools/tier1_floors/plant_wang.py — do not hand-edit.",
             "# LOOP-PROCESS §4's PLANT. Never lands, never shown to Rafe.",
             'tile_root: "res://%s"' % ASSETS_REL,
             'tile_pattern: "tier1_wangp_{id}.png"', "", "themes:", "  boundary:"]
    ids = "[" + ", ".join(str(i) for i in floor_ids) + "]"
    for role in ("floor_primary", "floor_accent", "floor_dark", "floor_interior", "floor_worn"):
        lines.append("    %s: %s" % (role, ids))
    lines.append("    wall_autotile:")
    for k in range(16):
        lines.append("      %d: %d" % (k, 9010 + k))
    lines.append("    wall_diagonal:")
    for k, v in (("corner_outer_nw", 9030), ("corner_outer_ne", 9031),
                 ("corner_outer_sw", 9032), ("corner_outer_se", 9033), ("interior_fill", 9034)):
        lines.append("      %s: %d" % (k, v))
    lines.append("    stair_down: [9040]")
    lines.append("    stair_up: [9041]")
    lines += ["", "default_theme: boundary", ""]
    tp = os.path.join(ASSETS, "tile_themes_tier1_wang_plant.yaml")
    open(tp, "w").write("\n".join(lines))
    json.dump(man, open(os.path.join(ASSETS, "MANIFEST.json"), "w"), indent=1)
    print("written: %s" % os.path.relpath(tp, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
