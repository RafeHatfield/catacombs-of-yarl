#!/usr/bin/env python3
"""LIT IN-SCENE CAPTURES of arbitrary candidate floor tiles, through the same rig as the
survivors — for the parent ring-rate run's blind spot-check.

WHY A SIBLING MODULE AND NOT A FLAG ON capture_floors.py
--------------------------------------------------------
`capture_floors.py` captures a FIXED set: four survivor codes across three named sets, with
id blocks and filenames derived from that structure. This run captures an arbitrary, run-time
list of generated children. Bending the former into the latter would make a module that carries
a landed ruling into a general-purpose tool; instead this file CALLS `capture_floors.lay_walls`
and `capture_floors.write_theme_for`, so the walls, the theme construction, the asset root, the
scene and the light rig are literally the same code, not the same intention.

WHAT VARIES AND WHAT DOES NOT — unchanged from `capture_floors.py`
  varies:   the floor tile, and only the floor tile
  constant: corridor geometry, light rig, tile size, resolution, WALLS

THE TWO CONTROLS IN EVERY ROUND THIS MODULE FEEDS — bible §13.5, LOOP-PROCESS §4
--------------------------------------------------------------------------------
A seat's pass counts for nothing until the seat has been shown able to fail, and a seat that
culls everything has discriminated nothing either. Both directions are controlled, and both
controls have a PUBLISHED PRIOR VERDICT from this project's earlier rounds, which is what makes
them controls rather than two more candidates:

  PLANT (red)   the raw, un-remediated B-KAB - the hardest-ringed tile in the corpus. Culled
                `keyline` by the blind seat in BOTH round A and round B of the remediation
                session. If it is not culled here, THE ROUND IS VOID.
  PARENT (green) the raw C-GAB - the tile every child in the round was conditioned on, and the
                RULED primary style parent. The seat returned `cull: none` on it in round A. If
                it is culled `keyline` here, that is not a void round - it is a finding about
                the parent, and it must be reported as one rather than explained away.

The plant is RE-CAPTURED here rather than reused from `evidence/captures/`, so that every image
in the round comes off the same rig at the same commit. The re-capture is compared byte-for-byte
against the stored one and the comparison is reported: identical means the rig is unchanged and
the published prior verdict transfers directly; different means it does not, and the round says
so instead of assuming.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools/tier0_harness"))
sys.path.insert(0, HERE)
from capture_corridor import read_config, capture, sha256, git_commit  # noqa: E402
import capture_floors as CF       # noqa: E402
import ring_instrument as RI      # noqa: E402
import near_ring as NR            # noqa: E402

# A dedicated id block clear of BOTH capture_floors' floor ids (9120-9131) AND the composition
# spike's wall ids, which are sparse and run to 9343 (9200, 9209, 9218, 9227, ... 9343).
#
# THIS CONSTANT WAS 9200 AND THAT WAS A DEFECT — recorded rather than quietly corrected, because
# it is LOOP-PROCESS §4.2's family: a step that looks successful while not doing what it claims.
# 9200 is `wall_autotile: 0` in the spike's theme, so staging a child there silently made the
# floor tile double as a wall tile, in a rig whose entire claim is that the WALLS ARE HELD
# CONSTANT and the floor is the only variable.
#
# It did no damage, and that is measured rather than assumed: three separate runs staged three
# DIFFERENT tiles into fr_9200 (B-KAB, then P_seed9709, then S_seed9807) and the plant and parent
# captures came out BYTE-IDENTICAL every time, and identical to the stored survivor captures made
# before this module existed. Autotile mask 0 does not fire in this one-wide corridor. The
# captures the seats judged are therefore unaffected, and re-capturing under this corrected block
# reproduces them byte-for-byte - which is the check, not the claim.
ID_BASE = 9400
OUT_DIR = os.path.join(HERE, "evidence", "children")


def stage(tiles):
    """tiles: list of (label, absolute png path). Returns [(label, path, tid, theme)]."""
    CF.lay_walls()
    out = []
    for i, (label, path) in enumerate(tiles):
        tid = ID_BASE + i
        Image.open(path).convert("RGB").save(os.path.join(CF.ASSETS, "fr_%d.png" % tid))
        theme = CF.write_theme_for(tid, "tile_themes_child_%d.yaml" % tid, label,
                                   generator="capture_children.py")
        out.append((label, path, tid, theme))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiles", required=True,
                    help="JSON file: [[label, path_relative_to_repo], ...]")
    ap.add_argument("--build-only", action="store_true",
                    help="lay assets and themes and stop (run Godot --headless --import between)")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    tiles = [(lab, os.path.join(REPO, p)) for lab, p in json.load(open(args.tiles))]
    missing = [p for _, p in tiles if not os.path.exists(p)]
    if missing:
        raise SystemExit("HARD STOP: missing tiles %s" % missing)

    cfg = read_config()
    light = cfg["light"]
    rig = ("ambient=%s color=%s energy=%s radius_tiles=%s (ALL UNDERIVED - §6.2 PLACEHOLDER)"
           % (light["ambient"], light["color"], light["energy"], light["radius_tiles"]))
    staged = stage(tiles)

    print("CHILD FLOOR CAPTURES - the floor is the only variable")
    print("commit: %s" % git_commit())
    print("tile:   %sx%s at x%s" % (cfg["tile"]["size"], cfg["tile"]["size"],
                                    cfg["tile"]["scale"]))
    print("rig:    %s   IDENTICAL for every capture" % rig)
    print("walls:  composition spike `before` arm, unchanged, held constant")
    print("tiles:  %d\n" % len(staged))

    if args.build_only:
        print("--build-only: %d themes written. Run Godot --headless --import, then re-run."
              % len(staged))
        return 0

    out_dir = args.out_dir or OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    records = []
    for label, src, tid, theme in staged:
        out = os.path.join(out_dir, "%s.png" % label)
        rc, log, _ = capture(out, theme, cfg, CF.GODOT, scene_spec=CF.SCENE,
                             log_out=out.replace(".png", ".log"))
        if not os.path.exists(out):
            print("ABORT: %s produced no capture (exit %d)" % (label, rc), file=sys.stderr)
            print(log[-3000:], file=sys.stderr)
            return 1
        engine_rig = next((l.split("light rig:")[1].strip()
                           for l in log.splitlines() if "light rig:" in l), "(not reported)")
        a = np.array(Image.open(src).convert("RGB")).astype(int)
        v, _ = RI.verdict(a)
        score, _ = NR.near_ring_score(a)
        print("  %-24s instrument=%-5s near-ring=%.3f  sha256=%s"
              % (label, v, score, sha256(out)[:16]))
        records.append(dict(label=label, floor_tile=os.path.relpath(src, REPO), tile_id=tid,
                            floor_verdict=v, near_ring=score, file="%s.png" % label,
                            sha256=sha256(out), engine_rig=engine_rig,
                            tile_sha256=hashlib.sha256(open(src, "rb").read()).hexdigest()))

    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(dict(commit=git_commit(), rig_requested=rig, scene=CF.SCENE,
                       walls="composition_spike/before, held constant",
                       tile_size=cfg["tile"]["size"], tile_scale=cfg["tile"]["scale"],
                       captures=records), f, indent=1)
    print("\n%d captures -> %s" % (len(records), os.path.relpath(out_dir, REPO)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
