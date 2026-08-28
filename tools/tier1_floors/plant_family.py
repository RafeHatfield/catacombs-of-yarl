#!/usr/bin/env python3
"""THE PLANT — a picturesquely RUINED floor, built to be caught.

LOOP-PROCESS §4, and it names this exact object:

    For the blind critic, TIER ONE HAS NO SHIPPING CORPUS TO MIX IN, so "name them cold" cannot
    run as designed. The substitute is a PLANT: one deliberately wrong candidate seeded into the
    set — for tier one, a picturesquely RUINED floor, cobwebbed and collapsed, among the USED-UP
    ones (bible §8.1).

    **If the critic does not catch the plant, the round is void and its findings are not read.**
    Not discounted — VOID. A soft critic's findings are worse than no findings, because they
    will be acted on.

WHAT MAKES THIS A FAIR PLANT RATHER THAN AN EASY ONE
----------------------------------------------------
It is built by the SAME composer, from the SAME measured material, through the SAME rig, and it
is captured in the SAME scene. Everything that could let a seat spot it by craft rather than by
register is held constant: same palette, same grain, same bond machinery, same resolution, same
light. It is not worse drawn. If anything it is more picturesque, which is the point — §13.3
warns that a bar's wow can be presentational, and §1 holds that nothing is staged.

What differs is exactly one thing, and it is the thing with NO INSTRUMENT (§13.4):

    §8.1, LOCKED:  Nothing in the Paths is ruined; everything is USED UP.
                   Surfaces record TRAFFIC, not TIME.
    §8.1's failure test: is the state of this thing explained by traffic and indifference?

The plant fails that test on purpose. It carries collapse holes with darkness under them,
cobwebbing across corners, moss in the joints, and dramatic full-tile cracks BAKED INTO THE BASE
TILE — which is also §8.3's motif trap, so a seat that misses the register failure still has a
second, purely geometric thing to catch. Two independent ways to fail one tile; a seat that
finds neither is not rigorous enough for its findings to be read.

⚠ IT IS NOT SHOWN TO RAFE AND IT DOES NOT LAND. It exists to qualify the seat.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import compose_family as CF      # noqa: E402
import field_laws as FL          # noqa: E402

T = CF.T
ASSETS_REL = "src/Presentation/assets/tier1_plant"
ASSETS = os.path.join(REPO, ASSETS_REL)
BASE_IDS = [9800, 9801, 9802]


def ruined_base(variant, mat, seed):
    """A base tile with the ruin BAKED IN — §8.1's register failure and §8.3's motif trap.

    ⚠ REBUILT AFTER ROUND 1, WHICH THIS PLANT VOIDED BY BEING TOO SUBTLE.

    The first version put a 4px collapse hole, a moss tint on 45% of joint pixels, and a
    9x9 dithered cobweb in one corner. All three RENDERED and none of them READ. The seat
    described the result as *"dried, crazed earth"* with *"~55 dark round pits ... the same 14px
    diameter everywhere"* and *"crack lines hue-shifted toward olive"* — which is the holes read
    as pits, the moss read as a hue shift, and the cobweb read as speckle. It culled the image,
    but for REPETITION, a defect the real family shares, so it never separated plant from
    candidate and the control failed.

    That is a defect in the plant, not in the seat, and the distinction matters: LOOP-PROCESS §4
    asks the plant to carry the defect ON THE AXIS THE CONTROL CLAIMS (§4.1's law), and this one
    carried it at an amplitude invisible at 32 pixels. §4 calls for *a picturesquely RUINED
    floor, COBWEBBED AND COLLAPSED*. Picturesque is the operative word and the first attempt was
    not picturesque at all — it was a texture with small dark circles in it.

    So every feature below is drawn at an amplitude that survives 32 native pixels: a hole you
    could fall into rather than a pit, strands rather than speckle, moss in blobs rather than in
    joints. If a seat still fails to name this as ruined, that is a finding about the seat.
    """
    img, joints = CF.build_base(variant, mat, seed)
    L = FL.RI.lum(img.astype(float))
    rgb = img.astype(float)
    rng = np.random.default_rng(seed + variant * 31 + 5)
    T_ = T

    # 1. A COLLAPSE. An irregular hole with real depth under it and a rim of spalled chips —
    #    a quarter of the tile, not a 4px dot. §8.1: "nothing in the Paths is RUINED".
    cy, cx = rng.integers(10, T_ - 10), rng.integers(10, T_ - 10)
    edge = 6.0 + rng.normal(0, 0.4, 32)
    for yy in range(T_):
        for xx in range(T_):
            dy, dx = yy - cy, xx - cx
            d = (dy * dy + dx * dx) ** 0.5
            ang = int(((np.arctan2(dy, dx) + np.pi) / (2 * np.pi)) * 31) % 32
            r = edge[ang]
            if d <= r - 1.5:
                L[yy, xx] = 6.0                                    # depth: near black
            elif d <= r:
                L[yy, xx] = mat["lum_lo"] * 0.35                   # the broken lip
            elif d <= r + 1.6 and rng.random() < 0.55:
                L[yy, xx] = min(255.0, mat["lum_hi"] * 1.12)       # spalled chips on the rim

    # 2. A SHATTERED SLAB. Cracks radiating from one point, wide enough to be cracks.
    sy, sx = rng.integers(6, T_ - 6), rng.integers(6, T_ - 6)
    for _ in range(5):
        th = rng.random() * 2 * np.pi
        y, x = float(sy), float(sx)
        for _step in range(rng.integers(8, 15)):
            L[int(y) % T_, int(x) % T_] = mat["lum_lo"] * 0.30
            L[int(y) % T_, (int(x) + 1) % T_] = mat["lum_lo"] * 0.42
            y += np.sin(th) + rng.normal(0, 0.3)
            x += np.cos(th) + rng.normal(0, 0.3)

    # 3. COBWEBBING. Actual strands, corner to corner, with a sag — not a dither.
    web = min(255.0, mat["lum_hi"] * 1.22)
    for k in range(4):
        span = 9 + k * 4
        for i in range(span):
            t = i / max(1.0, span - 1.0)
            yy = int(round(t * span))
            xx = int(round((1 - t) * span + 2.5 * np.sin(t * np.pi)))
            if 0 <= yy < T_ and 0 <= xx < T_:
                L[yy, xx] = web
    for i in range(0, 14):                                          # a radial guy-line
        L[i % T_, i % T_] = web

    out = CF.colourise(CF.quantise(L, mat["ladder"]), mat["tint"])

    # 4. MOSS, in blobs. Living green, in the one place the register says nothing lives.
    n = CF.wrap_noise(T_, 4, rng)
    thr = float(np.percentile(n, 78))
    moss = n > thr
    for yy in range(T_):
        for xx in range(T_):
            if moss[yy, xx] or (joints[yy, xx] and rng.random() < 0.5 and moss[yy, (xx + 2) % T_]):
                shade = 0.75 + 0.5 * rng.random()
                out[yy, xx] = np.array([46.0, 92.0, 40.0]) * shade
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()

    real = json.load(open(os.path.join(CF.ASSETS, "MANIFEST.json")))
    mat = real["material"]
    os.makedirs(ASSETS, exist_ok=True)

    man = dict(family="boundary_floor_PLANT", commit=FL.git_commit(), seed=a.seed,
               material=mat, base=[], channel=[], incident=[], oriented=[],
               what=("LOOP-PROCESS §4's tier-one plant: a picturesquely RUINED floor among the "
                     "used-up ones. Built by the same composer from the same measured material "
                     "and captured through the same rig, so only the REGISTER differs. It is "
                     "not shown to Rafe and it never lands. If the seat does not catch it, the "
                     "round is VOID."))

    print("THE PLANT — ruined, cobwebbed, collapsed. Built to be caught.")
    for v in range(3):
        img = ruined_base(v, mat, a.seed)
        tid = BASE_IDS[v]
        p = os.path.join(ASSETS, "tier1_plant_%d.png" % tid)
        Image.fromarray(img).save(p)
        vd = FL.verdict(p)
        # Reported, and it is a real check on the plant rather than a formality: the plant must
        # ALSO trip the mechanical screen, because a register plant that happens to be
        # geometrically clean would leave the seat only one way to fail and would not test the
        # instrument stack at all.
        print("  variant %d id %d  field_laws says %-28s (a plant SHOULD trip this)"
              % (v, tid, vd["verdict"]))
        man["base"].append(dict(id=tid, variant=v, file=os.path.basename(p),
                                sha256=FL.sha256_file(p), verdict=vd["verdict"],
                                codes=vd["codes"]))

    # The plant's own oriented set, so it is laid by the same 24-id mechanism the family uses
    # and cannot be told apart by having a visibly smaller variant pool.
    oid = 9830
    for b in man["base"]:
        src = np.asarray(Image.open(os.path.join(ASSETS, b["file"])).convert("RGB"))
        for o in range(8):
            im = np.rot90(src, o % 4)
            if o >= 4:
                im = im[:, ::-1]
            im = np.ascontiguousarray(im)
            dst = os.path.join(ASSETS, "tier1_plant_%d.png" % oid)
            Image.fromarray(im).save(dst)
            man["oriented"].append(dict(id=oid, of=b["id"], orientation=o,
                                        file=os.path.basename(dst), sha256=FL.sha256_file(dst)))
            oid += 1

    # Same channel and incident overlays as the real family, copied — so the plant differs ONLY
    # in its base material's register. Anything else would be a second uncontrolled variable.
    for key in ("channel", "incident"):
        for e in real[key]:
            src = os.path.join(CF.ASSETS, e["file"])
            dst = os.path.join(ASSETS, "tier1_plant_%d.png" % e["id"])
            Image.open(src).save(dst)
            man[key].append(dict(e, file=os.path.basename(dst)))
    man["placement"] = real["placement"]

    with open(os.path.join(ASSETS, "MANIFEST.json"), "w") as f:
        json.dump(man, f, indent=1)

    # Theme, mirroring the real one so the two capture through identical code paths.
    ids = [o["id"] for o in man["oriented"]]
    lines = ["# GENERATED by tools/tier1_floors/plant_family.py — do not hand-edit.",
             "# LOOP-PROCESS §4's PLANT. A deliberately RUINED floor. Never lands, never shown to Rafe.",
             'tile_root: "res://%s"' % ASSETS_REL,
             'tile_pattern: "tier1_plant_{id}.png"', "", "themes:", "  boundary:"]
    idstr = "[" + ", ".join(str(i) for i in ids) + "]"
    for role in ("floor_primary", "floor_accent", "floor_dark", "floor_interior", "floor_worn"):
        lines.append("    %s: %s" % (role, idstr))
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
    # The plant uses the SAME wall mocks, copied here so its theme resolves under one root.
    stub = os.path.join(REPO, "src/Presentation/assets/tier0_harness/stub")
    for tid in list(range(9010, 9035)) + [9040, 9041]:
        src = os.path.join(stub, "tier0_stub_%d.png" % tid)
        if os.path.exists(src):
            Image.open(src).save(os.path.join(ASSETS, "tier1_plant_%d.png" % tid))
    tp = os.path.join(ASSETS, "tile_themes_tier1_plant.yaml")
    with open(tp, "w") as f:
        f.write("\n".join(lines))
    print("\nwritten: %s" % os.path.relpath(tp, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
