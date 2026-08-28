#!/usr/bin/env python3
"""THE PLANT for the course-aligned ashlar family. LOOP-PROCESS §4.

    For the blind critic, tier one has no shipping corpus to mix in, so "name them cold" cannot
    run as designed. The substitute is a PLANT: one deliberately wrong candidate — for tier one, a
    picturesquely RUINED floor among the USED-UP ones (bible §8.1: *nothing in the Paths is ruined;
    everything is used up*).

    If the critic does not catch the plant, the round is VOID and its findings are not read. Not
    discounted — void. A soft critic's findings are worse than no findings, because they will be
    acted on.

§4.1 REQUIRES THE LEVER BE PROVEN ON ITS OWN AXIS, and that is what shapes this file. Everything a
seat could use to spot the plant by CRAFT rather than by REGISTER is held constant: the same
composer, the same bond, the same courses, the same head-joint merges, the same palette, the same
grain bank, the same stone addressing, the same rig, the same scene. **It goes through the very
same engine painter** — the plant is an atlas set, not a pile of pre-coloured PNGs, so its stones
are addressed and painted by exactly the code that paints the candidate's.

That last point is why the ruin is drawn into the BOND rather than over the top of it. The engine
paints class 1..6 and leaves class 0 alone, so damage is marked class 0 and survives untouched —
and the plant's ladder carries two extra entries, a void and a cobweb value, which only class-0
pixels can reach. A ruin painted after the fact would sit on the image rather than in the floor,
and a seat could then catch it for being pasted on, which is not the axis this control is testing.

The session-one plant voided its own round by being too subtle: a 4px hole read as a pit, moss in
the joints read as a hue shift, a dithered cobweb read as speckle. The amplitudes here are the
corrected ones. Picturesque is the operative word — a hole you could fall into, strands rather
than speckle, cracks that go somewhere.

NEVER LANDS. NEVER SHOWN TO RAFE.
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
import compose_ashlar as CA      # noqa: E402
import compose_family as CF      # noqa: E402
import field_laws as FL          # noqa: E402

T = CA.T
ASSETS_REL = "src/Presentation/assets/tier1_ashlar_plant"
ASSETS = os.path.join(REPO, ASSETS_REL)

VOID_IDX = 7          # extra ladder entries, reachable only by class 0
WEB_IDX = 8


def ruin(li, cls, seed, mat):
    """Bake picturesque ruin into one tile's ladder-index map and class mask.

    Damage is marked class 0 so the engine leaves it exactly as drawn — the same treatment the
    joints get, and for the same reason: it is authored form, not material.
    """
    rng = np.random.default_rng(seed)
    li = li.copy()
    cls = cls.copy()

    if rng.random() < 0.55:
        # A collapse with real depth, a quarter of the tile across. Lipped on one side, because a
        # hole with an even rim reads as a design element rather than as a floor giving way.
        cy, cx = rng.integers(9, T - 9), rng.integers(9, T - 9)
        edge = 6.0 + rng.normal(0, 0.5, 32)
        for yy in range(T):
            for xx in range(T):
                dy, dx = yy - cy, xx - cx
                d = float((dy * dy + dx * dx) ** 0.5)
                ang = int(((np.arctan2(dy, dx) + np.pi) / (2 * np.pi)) * 31) % 32
                r = edge[ang]
                if d <= r - 1.5:
                    li[yy, xx], cls[yy, xx] = VOID_IDX, 0
                elif d <= r:
                    li[yy, xx], cls[yy, xx] = 0, 0
                elif d <= r + 1.6 and rng.random() < 0.5:
                    li[yy, xx], cls[yy, xx] = len(mat["ladder"]) - 1, 0

    if rng.random() < 0.45:
        # Cobweb strands with a sag. Strands, not a dither — the session-one plant's speckle read
        # as grain and the seat never saw it.
        for k in range(3):
            span = 9 + k * 5
            x0, y0 = rng.integers(0, T - 4), rng.integers(0, T - 4)
            for i in range(span):
                t = i / max(1.0, span - 1.0)
                yy = int(round(y0 + t * span))
                xx = int(round(x0 + (1 - t) * span * 0.6 + 2.5 * np.sin(t * np.pi)))
                if 0 <= yy < T and 0 <= xx < T:
                    li[yy, xx], cls[yy, xx] = WEB_IDX, 0

    if rng.random() < 0.7:
        # A dramatic crack that GOES somewhere — branching, crossing courses. The candidate's
        # joints are structural; this is damage, and it is meant to look like it.
        x, y = float(rng.integers(2, T - 2)), 0.0
        while y < T - 1:
            x += rng.normal(0, 0.9)
            y += 1.0
            for dx in (0, 1):
                xx = int(round(x)) + dx
                if 0 <= xx < T:
                    li[int(y), xx], cls[int(y), xx] = 0, 0
    return li, cls


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()

    src = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))
    mat = dict(src["material"])
    # The two extra rungs. They sit ABOVE the family's seven so no stone value can reach them —
    # the engine only re-quantises class 1..6, and it re-quantises against the whole array, so
    # putting them anywhere but the end would let a stone snap onto the void.
    mat["ladder"] = list(mat["ladder"]) + [6.0, 196.0]
    os.makedirs(ASSETS, exist_ok=True)

    man = dict(src)
    man["family"] = "boundary_floor_ashlar_PLANT"
    man["material"] = mat
    man["what"] = ("LOOP-PROCESS §4's plant: the SAME bond, courses, merges, palette, grain bank "
                   "and stone addressing as the candidate, with picturesque ruin baked into the "
                   "bond so it goes through the identical engine painter. Never lands, never "
                   "shown to Rafe. If the seat does not catch it, the round is VOID.")
    man["base"] = []
    # The candidate's finished-pixel check describes the CANDIDATE's pixels. Inherited here it
    # would make the plant refuse to lay — the control arm silenced by the candidate's evidence.
    # `emit_paint_check.py --assets ...` writes the plant its own afterwards.
    man.pop("paint_check", None)

    print("THE PLANT — the course-aligned ashlar family, ruined")
    for e in src["base"]:
        atlas = np.asarray(Image.open(os.path.join(CA.ASSETS, e["file"])).convert("RGB")).copy()
        # EVERY CELL OF THE ATLAS, and the count is read from the image rather than assumed. The
        # first version hard-coded a 3x3 and kept it after the atlas grew to 6x6 for the course
        # splits — which would have left three quarters of the plant UNRUINED and handed the
        # control seat a floor that was mostly the candidate.
        cells = atlas.shape[0] // T
        for cr in range(cells):
            for cc in range(cells):
                sl = (slice(cr * T, (cr + 1) * T), slice(cc * T, (cc + 1) * T))
                li, cls = ruin(atlas[sl][..., 0], atlas[sl][..., 1],
                               a.seed + e["id"] * 64 + cr * cells + cc, mat)
                atlas[sl][..., 0] = li
                atlas[sl][..., 1] = cls
        p = os.path.join(ASSETS, e["file"].replace("tier1_ashlar_", "tier1_ashlarp_"))
        Image.fromarray(atlas).save(p)
        man["base"].append(dict(e, file=os.path.basename(p), sha256=FL.sha256_file(p)))
    print("  %d atlases ruined, every cell of each" % len(man["base"]))

    # Same grain bank, byte for byte. A different one would be a second variable.
    shutil.copyfile(os.path.join(CA.ASSETS, src["grain_file"]),
                    os.path.join(ASSETS, src["grain_file"]))

    # Same wall mocks, same names the theme asks for — the seat prompt declares the walls
    # placeholder and out of scope, and they must be identically placeholder in both arms.
    stub = os.path.join(REPO, "src/Presentation/assets/tier0_harness/stub")
    for tid in list(range(9010, 9035)) + [9040, 9041]:
        s = os.path.join(stub, "tier0_stub_%d.png" % tid)
        if os.path.exists(s):
            shutil.copyfile(s, os.path.join(ASSETS, "tier1_ashlarp_%d.png" % tid))

    json.dump(man, open(os.path.join(ASSETS, "MANIFEST.json"), "w"), indent=1)
    print("written: %s/MANIFEST.json" % ASSETS_REL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
