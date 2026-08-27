#!/usr/bin/env python3
"""Lit in-scene captures of the survivor floors, un-remediated and remediated, through the
tier-0 rig.

ART-BIBLE-v0 §13.1 / LOOP-PROCESS §2.1: verdicts come from the production renderer, in the lit
scene, at true display size, never from a contact sheet. §6.3: a receive-light asset judged
unlit is judged by the wrong instrument. So the blind seat that gates this session's remediation
sees THIS, not the 32x32 PNGs.

WHAT VARIES AND WHAT DOES NOT
-----------------------------
Varies: the FLOOR tile, and only the floor tile.
Constant: the corridor geometry, the light rig, the tile size, the resolution, the WALLS.

The walls are the composition spike's `before` arm - the arm its round-8 seat ranked FIRST of
five, carrying the two ruled variables at their best measured settings. Holding them fixed means
any difference a seat reports between two captures here is the floor, because nothing else moved.

ONE FLOOR PER CAPTURE
---------------------
Each capture holds every floor slot to a SINGLE tile. The briefed §6.4 configuration mixes all
four survivors, and three separate seats have already reported that they do not read as one
floor - "salmon, grey-brown and olive tiles abut with no transition ... three tilesets pushed
together" (spike §5.5.2). That is a real finding about the set and it is NOT this session's to
fix, but it would confound a per-floor verdict: a seat culling a mixed capture cannot tell you
WHICH floor it culled. The session's bar is per-floor - "the seat passes all four" - so the
capture is per-floor. capture_spike.py established the solo-floor mechanism for the same reason.

THE THREE SETS
--------------
  orig   the four survivors exactly as they sit in the ledger, un-remediated
  remed  this session's remediated set
  mock   `dering_floors.py`'s output - the instrument-only MOCK this session replaces

`mock` is captured because the claim that it needed replacing should be shown rather than
asserted. Its value threshold at 0.30x the median cannot see a ring at 0.48x, so it left A-VAB
ringed - both loops, findings byte-identical to the raw original - while A-VAB is the tile the
survivor manifest marks `strongest` and the tile the spike's own solo-floor captures used.
"""
import argparse
import json
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools/tier0_harness"))
sys.path.insert(0, HERE)
from capture_corridor import read_config, capture, sha256, git_commit  # noqa: E402
import ring_instrument as RI  # noqa: E402

GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"
ASSETS_REL = "src/Presentation/assets/floor_remediation"
ASSETS = os.path.join(REPO, ASSETS_REL)
SPIKE_ARM = os.path.join(REPO, "src/Presentation/assets/composition_spike/before")
SPIKE_THEME = os.path.join(REPO,
                           "src/Presentation/assets/composition_spike/tile_themes_before.yaml")
SCENE = "src/Presentation/assets/tier0_harness/scenes/wall_face_review.json"
CODES = ("A-VAB", "A-HEB", "B-KAB", "C-GAB")

# Floor id blocks. The spike's floor ids are 9120-9123; this rig re-lays every tile under its
# own pattern so nothing here can be confused with, or silently inherit from, that arm's assets.
SETS = {
    "orig":  (9120, os.path.join(REPO, "tools/pixellab/probe_6_4/survivors"), "%s.png"),
    "remed": (9124, os.path.join(HERE, "remediated"), "%s.png"),
    "mock":  (9128, os.path.join(REPO, "src/Presentation/assets/composition_spike/floors_deringed"),
              None),   # MOCK files are id-named, not code-named; resolved positionally
}
PATTERN = "fr_{id}.png"


def lay_walls():
    """The spike's `before` walls, laid under this rig's ids. Floors are laid by the caller.

    Extracted from `lay_assets` unchanged so a sibling capture module can hold the walls
    constant by CALLING this rather than by copying the loop. The walls being byte-identical
    across every capture is what makes the floor the only variable, and a mirrored copy of that
    loop is a second place for it to stop being true.
    """
    os.makedirs(ASSETS, exist_ok=True)
    laid = {}
    for f in sorted(os.listdir(SPIKE_ARM)):
        m = re.match(r"MOCK_comp_(\d+)\.png$", f)
        if not m:
            continue
        tid = int(m.group(1))
        if 9120 <= tid <= 9123:
            continue                      # the arm's own floors - replaced per set below
        shutil.copy2(os.path.join(SPIKE_ARM, f), os.path.join(ASSETS, "fr_%d.png" % tid))
        laid[tid] = "wall"
    return laid


def lay_assets():
    """One asset directory holding the spike's walls plus every floor variant under its own id."""
    laid = lay_walls()
    for setname, (base, src, pat) in SETS.items():
        for i, code in enumerate(CODES):
            tid = base + i
            fn = (pat % code) if pat else ("MOCK_dering_%d.png" % (9120 + i))
            path = os.path.join(src, fn)
            if not os.path.exists(path):
                # Expected, not an error: B-KAB has no remediation (RULED 2026-08-27), so there
                # is no remediated tile to lay. Skipped and NAMED below, never silently
                # substituted with the original - that substitution is exactly the silent
                # success LOOP-PROCESS §4.2 exists to stop.
                continue
            im = Image.open(path).convert("RGB")
            im.save(os.path.join(ASSETS, "fr_%d.png" % tid))
            laid[tid] = "%s/%s" % (setname, code)
    return laid


def write_theme_for(tid, name, floor_note, generator="capture_floors.py"):
    """The spike's `before` theme, re-rooted here, with EVERY floor slot held to tile `tid`.

    Extracted from `write_theme` unchanged, for the same reason as `lay_walls`: a sibling
    capture module needs the identical theme construction, and the way to hold a rig constant
    across two modules is to share the code that builds it rather than to copy it.
    """
    text = open(SPIKE_THEME).read()
    text = re.sub(r'^tile_root: ".*"$', 'tile_root: "res://%s"' % ASSETS_REL, text,
                  flags=re.MULTILINE)
    text = re.sub(r'^tile_pattern: ".*"$', 'tile_pattern: "%s"' % PATTERN, text,
                  flags=re.MULTILINE)
    text = re.sub(r"^(    floor_\w+): \[.*\]$", r"\1: [%d]" % tid, text, flags=re.MULTILINE)
    text = text.replace(
        "# GENERATED by tools/composition_spike/compose_walls.py - do not hand-edit.",
        "# GENERATED by tools/floor_remediation/%s - do not hand-edit.\n"
        "# Walls: the composition spike's `before` arm, UNCHANGED and held constant.\n"
        "# Floor: %s (tile %d) in every floor slot. The floor is the only variable."
        % (generator, floor_note, tid))
    with open(os.path.join(ASSETS, name), "w") as f:
        f.write(text)
    return "res://%s/%s" % (ASSETS_REL, name)


def write_theme(setname, code_index):
    """The spike's `before` theme, re-rooted here, with every floor slot held to one tile."""
    tid = SETS[setname][0] + code_index
    return write_theme_for(tid, "tile_themes_%s_%s.yaml" % (setname, CODES[code_index]),
                           "%s/%s" % (setname, CODES[code_index]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="orig,remed,mock")
    ap.add_argument("--out-dir", default="tools/floor_remediation/evidence/captures")
    ap.add_argument("--build-only", action="store_true",
                    help="lay assets and themes and stop (run Godot --headless --import between)")
    args = ap.parse_args()

    sets = [s for s in args.sets.split(",") if s.strip()]
    cfg = read_config()
    light = cfg["light"]
    rig = ("ambient=%s color=%s energy=%s radius_tiles=%s (ALL UNDERIVED - §6.2 PLACEHOLDER)"
           % (light["ambient"], light["color"], light["energy"], light["radius_tiles"]))

    laid = lay_assets()
    jobs, skipped = [], []
    for s in sets:
        for i, code in enumerate(CODES):
            if not os.path.exists(os.path.join(ASSETS, "fr_%d.png" % (SETS[s][0] + i))):
                skipped.append("%s/%s" % (s, code))
                continue
            jobs.append((s, code, write_theme(s, i)))

    print("SURVIVOR-FLOOR CAPTURES - the floor is the only variable")
    print("commit: %s" % git_commit())
    print("tile:   %sx%s at x%s" % (cfg["tile"]["size"], cfg["tile"]["size"], cfg["tile"]["scale"]))
    print("rig:    %s   IDENTICAL for every capture" % rig)
    print("walls:  composition spike `before` arm, unchanged, held constant")
    print("assets: %d tiles laid in %s" % (len(laid), ASSETS_REL))
    if skipped:
        print("SKIPPED, no such tile (expected where a code has no remediation): %s"
              % ", ".join(skipped))
    print()

    if args.build_only:
        print("--build-only: %d themes written. Run Godot --headless --import, then re-run."
              % len(jobs))
        return 0

    out_dir = os.path.join(REPO, args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    records = []
    for setname, code, theme in jobs:
        fn = "%s_%s_lit.png" % (setname, code)
        out = os.path.join(out_dir, fn)
        rc, log, _ = capture(out, theme, cfg, GODOT, scene_spec=SCENE,
                             log_out=out.replace(".png", ".log"))
        if not os.path.exists(out):
            print("ABORT: %s produced no capture (exit %d)" % (fn, rc), file=sys.stderr)
            print(log[-3000:], file=sys.stderr)
            return 1
        engine_rig = next((l.split("light rig:")[1].strip()
                           for l in log.splitlines() if "light rig:" in l), "(not reported)")
        tile_src = os.path.join(ASSETS, "fr_%d.png" % (SETS[setname][0] + CODES.index(code)))
        v, _ = RI.verdict(np.array(Image.open(tile_src).convert("RGB")).astype(int))
        print("  %-22s floor=%s/%-6s instrument=%-5s sha256=%s"
              % (fn, setname, code, v, sha256(out)[:16]))
        records.append(dict(set=setname, code=code, file=fn, theme=theme,
                            floor_tile=os.path.relpath(tile_src, REPO),
                            floor_verdict=v, sha256=sha256(out), engine_rig=engine_rig))

    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(dict(commit=git_commit(), rig_requested=rig, scene=SCENE,
                       walls="composition_spike/before, held constant",
                       tile_size=cfg["tile"]["size"], tile_scale=cfg["tile"]["scale"],
                       captures=records), f, indent=1)
    print("\n%d captures -> %s" % (len(records), os.path.relpath(out_dir, REPO)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
