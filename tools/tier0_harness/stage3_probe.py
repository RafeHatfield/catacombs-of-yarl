#!/usr/bin/env python3
"""§6.4 probe — STAGE 3: the lit comparison, on the reference device's grid.

RULED (Rafe, STOP 1): "lit corridor on device — survivor floors, best micro-probe walls (or
flagged neutral placeholders if the bar fails), identical rig, unlit companions."

WHY THIS IS NOT capture_probe_arms.py
-------------------------------------
That script captures exactly three arms, one tile directory each, because §6.4 declared a
three-arm probe. STOP 1 changed the shape: Rafe curated the floor sheets **as one pool**, on
the ground that arm labels carry no lighting information after Stage 1's positive-control
failure. The survivors are four floors that happen to come from arms A, A, B and C. Capturing
"three arms" would now be capturing a distinction the evidence says is not there.

So this captures **one tile set per survivor**, every one through the same rig, plus an unlit
companion for each. `capture_probe_arms.py` is left untouched and unused rather than bent —
it is still the correct script for a three-arm probe, and this probe stopped being one.

WHAT VARIES AND WHAT DOES NOT
-----------------------------
Varies: the floor tile, and only the floor tile.
Constant: the wall tile, the corridor geometry, the light rig, the tile size, the resolution.

The walls are held constant deliberately. They are the one micro-probe wall used for every
survivor, so they cannot explain a difference between survivors.

⚠ AND THE WALLS ARE A KNOWN WEAKNESS, STATED SO IT IS NOT DISCOVERED LATER. The micro-probe
cleared its declared bar 20/20 on framing, and every one of those 20 is undifferentiated noise
— no coursing, no mortar, no timber, no binding. These walls test how a surface RECEIVES light.
They do not test architecture, and no judgement about §7.1 or §12 can be drawn from them.

THE LIT/UNLIT PAIR IS THE POINT
-------------------------------
§6.3: receive-light assets "look flat and slightly disappointing on a contact sheet. They come
alive only in the lit scene." The unlit companion is that claim made checkable — it is the
contact-sheet view of the same asset, captured through the same renderer, so the difference
between the pair IS the thing §6.3 asserts. Ambient-only, with the carried light's energy at
zero; every other rig value unchanged.
"""
import argparse
import json
import os
import shutil
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_corridor import REPO, read_config, capture, sha256, git_commit  # noqa: E402
from make_stub_tiles import (theme_yaml, FLOOR_PRIMARY, FLOOR_ACCENT, FLOOR_DARK,  # noqa: E402
                             FLOOR_WORN, WALL_MASK_BASE, WALL_DIAG_BASE,
                             STAIR_DOWN, STAIR_UP)

GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"
ASSETS = "src/Presentation/assets/tier0_harness"
SURVIVORS = os.path.join(REPO, "tools/pixellab/probe_6_4/survivors")
WALLS = os.path.join(REPO, "tools/pixellab/probe_6_4/wall_microprobe/images")

FLOOR_IDS = (FLOOR_PRIMARY, FLOOR_ACCENT, FLOOR_DARK, FLOOR_WORN)
WALL_IDS = tuple(WALL_MASK_BASE + m for m in range(16)) \
    + tuple(WALL_DIAG_BASE + i for i in range(5)) + (STAIR_DOWN, STAIR_UP)


def build_tile_set(code, floor_png, wall_png):
    """One directory per survivor: every floor role gets the survivor, every wall role the
    single constant wall.

    Every floor role is written, not just floor_primary. FloorComposer's Pass 2 marks any
    wall-adjacent tile Dark and never overrides it, so in a one-wide corridor EVERY floor cell
    is Dark and floor_primary is never drawn at all — a trap this harness already fell into
    once, where a control planted its defect in a dead role and passed a swap through with
    0.0000% of pixels changed. Writing the same image to every role makes the capture
    independent of which pass wins.
    """
    out_dir = os.path.join(REPO, ASSETS, "stage3_%s" % code)
    os.makedirs(out_dir, exist_ok=True)
    for tid in FLOOR_IDS:
        shutil.copy2(floor_png, os.path.join(out_dir, "tier0_stub_%d.png" % tid))
    for tid in WALL_IDS:
        shutil.copy2(wall_png, os.path.join(out_dir, "tier0_stub_%d.png" % tid))

    theme_path = os.path.join(REPO, ASSETS, "tile_themes_stage3_%s.yaml" % code)
    with open(theme_path, "w") as f:
        f.write(theme_yaml("res://%s/stage3_%s" % (ASSETS, code), "tier0_stub_{id}.png"))
    return out_dir, "res://%s/tile_themes_stage3_%s.yaml" % (ASSETS, code)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", default="wallsurf_14.png",
                    help="the constant wall tile, from the micro-probe")
    ap.add_argument("--out-dir", default="tools/tier0_harness/evidence/stage3")
    ap.add_argument("--build-only", action="store_true",
                    help="write tile sets and themes, capture nothing (run --import between)")
    args = ap.parse_args()

    cfg = read_config()
    manifest = json.load(open(os.path.join(SURVIVORS, "MANIFEST.json")))
    codes = [s["code"] for s in manifest["survivors"]]
    wall_png = os.path.join(WALLS, args.wall)
    if not os.path.exists(wall_png):
        print("no such wall tile: %s" % wall_png, file=sys.stderr)
        return 1

    print("STAGE 3 — the lit comparison")
    print("commit:    %s" % git_commit())
    print("tile:      %sx%s at x%s" % (cfg["tile"]["size"], cfg["tile"]["size"],
                                       cfg["tile"]["scale"]))
    print("survivors: %s" % ", ".join(codes))
    print("wall:      %s  — CONSTANT across every survivor, so it cannot explain a difference"
          % args.wall)
    print("           ⚠ structureless: it tests light response, never architecture\n")

    themes = {}
    for s in manifest["survivors"]:
        d, theme = build_tile_set(s["code"], os.path.join(SURVIVORS, s["file"]), wall_png)
        themes[s["code"]] = theme
        print("  built %-6s -> %s" % (s["code"], os.path.relpath(d, REPO)))

    if args.build_only:
        print("\n--build-only: run Godot --headless --import, then re-run without the flag.")
        return 0

    light = cfg["light"]
    rig = ("ambient=%s color=%s energy=%s radius_tiles=%s (ALL UNDERIVED — §6.2 PLACEHOLDER)"
           % (light["ambient"], light["color"], light["energy"], light["radius_tiles"]))
    print("\nIDENTICAL RIG, EVERY CAPTURE: %s\n" % rig)

    out_dir = os.path.join(REPO, args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    records = []
    for code in codes:
        for lit in (True, False):
            name = "%s_%s.png" % (code, "lit" if lit else "unlit")
            out = os.path.join(out_dir, name)
            # Unlit = ambient only. Energy to zero and NOTHING else touched, so the pair
            # differs by the carried light and by nothing else.
            overrides = None if lit else {"energy": 0.0}
            rc, log, _ = capture(out, themes[code], cfg, GODOT,
                                 light_overrides=overrides, log_out=out.replace(".png", ".log"))
            if not os.path.exists(out):
                print("ABORT: %s produced no capture (exit %d)" % (name, rc), file=sys.stderr)
                print(log[-2000:], file=sys.stderr)
                return 1
            engine_rig = next((l.split("light rig:")[1].strip()
                               for l in log.splitlines() if "light rig:" in l), "(not reported)")
            engine_tile = next((l.split("Map renderer:")[1].strip()
                                for l in log.splitlines() if "Map renderer:" in l), "?")
            print("  %-16s sha256=%s" % (name, sha256(out)[:16]))
            print("      engine rig:  %s" % engine_rig)
            print("      engine tile: %s" % engine_tile)
            records.append({"code": code, "lit": lit, "file": name,
                            "sha256": sha256(out), "engine_rig": engine_rig,
                            "engine_tile": engine_tile})

    with open(os.path.join(out_dir, "stage3_manifest.json"), "w") as f:
        json.dump({"commit": git_commit(), "rig_requested": rig, "wall": args.wall,
                   "tile_size": cfg["tile"]["size"], "tile_scale": cfg["tile"]["scale"],
                   "captures": records}, f, indent=1)
    print("\n%d captures -> %s" % (len(records), out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
