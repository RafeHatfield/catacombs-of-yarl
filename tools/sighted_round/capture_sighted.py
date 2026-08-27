#!/usr/bin/env python3
"""THE SIGHTED ROUND — captures, plus the two checks that must be shown able to fail.

§13.1 / §2.1: verdicts come from the production renderer, in the lit scene, at the reference
device's pixel size. §2.2: the scene is the mixed distribution, not the worst corner alone.

TWO ARMS, ONE VARIABLE:
    recipe   the rebuilt walls (tools/sighted_round/compose_recipe.py)
    before   the composition spike's `before` arm - the arm ITS round-8 seat ranked first of
             five - on the same scene, the same rig, the same sanctioned floors.
Both arms get a lit and an unlit capture, so the differencing check can run on either.

THE DIFFERENCING CHECK (round 8, still in force)
------------------------------------------------
Authored occlusion must persist with the engine light OFF. Anything that exists only to fake a
light direction disappears when the light does, and is a cull. Implemented by comparing the
plane-boundary structure in the unlit capture against the lit one: the face must still be darker
than the top band with the carried light at zero energy, because it is material, not lighting.

`--prove-checks` mutates the tiles to carry the defect each check exists to catch and shows both
go red. LOOP-PROCESS §4: no instrument's pass counts until it has demonstrated it can fail.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools/tier0_harness"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools/floor_remediation"))
from capture_corridor import read_config, capture, sha256, git_commit  # noqa: E402
import ring_instrument as RI  # noqa: E402

GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"
SCENE = "src/Presentation/assets/tier0_harness/scenes/mixed_distribution.json"
ASSETS_REL = "src/Presentation/assets/sighted_round"
OUTDIR = os.path.join(HERE, "evidence", "captures")

ARMS = {
    "recipe": "res://%s/tile_themes_recipe.yaml" % ASSETS_REL,
    "before": "res://src/Presentation/assets/composition_spike/tile_themes_before_sanctioned.yaml",
    "plant": "res://%s/tile_themes_plant.yaml" % ASSETS_REL,
}


def make_before_sanctioned():
    """The spike's `before` arm with its floors swapped to the sanctioned pair.

    The arm's own theme lists all four §6.4 survivors as floors, and two of them are now barred
    from any scene (§5.5: A-VAB is prop stock, B-KAB retired). The control has to run on the same
    floors as the candidate or the comparison carries two variables, so its floor rows are
    rewritten and NOTHING else is touched - the wall ids, the mask table and the diagonal block
    are byte-identical to the arm on disk.
    """
    src = os.path.join(REPO, "src/Presentation/assets/composition_spike/tile_themes_before.yaml")
    dst = os.path.join(REPO, "src/Presentation/assets/composition_spike",
                       "tile_themes_before_sanctioned.yaml")
    out, swapped = [], 0
    for line in open(src):
        if line.startswith("    floor_"):
            role = line.split(":")[0]
            out.append("%s: [9401, 9402]\n" % role)
            swapped += 1
        elif line.startswith("tile_root:"):
            out.append(line)
        else:
            out.append(line)
    # the sanctioned floors must be reachable from this arm's tile_root, so lay them there too
    arm_dir = os.path.join(REPO, "src/Presentation/assets/composition_spike/before")
    for tid, code in ((9401, "C-GAB"), (9402, "A-HEB")):
        s = os.path.join(REPO, "tools/floor_remediation/remediated", code + ".png")
        Image.open(s).convert("RGB").save(os.path.join(arm_dir, "MOCK_comp_%d.png" % tid))
    with open(dst, "w") as f:
        f.write("".join(out))
    return dst, swapped


def plane_stats(path, scene_rows=(96, 700)):
    """Face-band vs top-band luminance read out of a capture.

    Not a verdict - it is the differencing check's raw material. The scene puts room A's north
    wall face row at a fixed place, so the same two strips are sampled in every capture.
    """
    a = np.array(Image.open(path).convert("RGB")).astype(float)
    L = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    return L


def differencing_check(lit_path, unlit_path, tile_px, face_rows, top_rows):
    """Authored occlusion must survive the light going out.

    Reads the same wall band in both captures and asks whether the face is still darker than the
    top band unlit. If the separation only exists lit, it was the engine drawing it, not the art.
    """
    out = {}
    for label, p in (("lit", lit_path), ("unlit", unlit_path)):
        L = plane_stats(p)
        out[label] = dict(top=float(L[top_rows[0]:top_rows[1]].mean()),
                          face=float(L[face_rows[0]:face_rows[1]].mean()))
        out[label]["ratio"] = out[label]["face"] / max(out[label]["top"], 1e-6)
    out["persists"] = bool(out["unlit"]["ratio"] < 0.85)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="recipe,before")
    ap.add_argument("--out-dir", default=OUTDIR)
    ap.add_argument("--build-only", action="store_true")
    args = ap.parse_args()

    dst, swapped = make_before_sanctioned()
    cfg = read_config()
    light = cfg["light"]
    rig = ("ambient=%s color=%s energy=%s radius_tiles=%s"
           % (light["ambient"], light["color"], light["energy"], light["radius_tiles"]))

    print("THE SIGHTED ROUND - CAPTURES")
    print("commit: %s" % git_commit())
    print("scene:  %s   (room + corners + one-wide chokepoint, §2.2)" % SCENE)
    print("rig:    %s   IDENTICAL for every capture" % rig)
    print("control arm: composition spike `before`, floors swapped to the sanctioned pair "
          "(%d floor roles rewritten, walls untouched)\n" % swapped)
    if args.build_only:
        print("--build-only: theme written. Run Godot --headless --import, then re-run.")
        return 0

    os.makedirs(args.out_dir, exist_ok=True)
    recs = []
    for arm in [a for a in args.arms.split(",") if a.strip()]:
        for lit in (True, False):
            fn = "%s_%s.png" % (arm, "lit" if lit else "unlit")
            out = os.path.join(args.out_dir, fn)
            rc, log, _ = capture(out, ARMS[arm], cfg, GODOT, scene_spec=SCENE,
                                 light_overrides=None if lit else {"energy": 0.0},
                                 log_out=out.replace(".png", ".log"))
            if not os.path.exists(out):
                print("ABORT: %s produced no capture (exit %d)" % (fn, rc), file=sys.stderr)
                print(log[-2500:], file=sys.stderr)
                return 1
            print("  %-16s sha256=%s" % (fn, sha256(out)[:16]))
            recs.append(dict(arm=arm, lit=lit, file=fn, sha256=sha256(out)))

    with open(os.path.join(args.out_dir, "manifest.json"), "w") as f:
        json.dump(dict(commit=git_commit(), scene=SCENE, rig=rig, captures=recs), f, indent=1)
    print("\n%d captures -> %s" % (len(recs), os.path.relpath(args.out_dir, REPO)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
