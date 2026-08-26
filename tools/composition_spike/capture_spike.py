#!/usr/bin/env python3
"""THE COMPOSITION SPIKE — lit captures of the composed wall segments, through the tier-0 rig.

ART-BIBLE-v0 §13.1 / LOOP-PROCESS §2.1: verdicts come from the production renderer, in the lit
scene, at true display size. §6.3: a receive-light asset captured unlit is judged by the wrong
instrument, which is why every arm gets an unlit companion rather than a contact sheet.

WHAT VARIES AND WHAT DOES NOT
-----------------------------
Varies: the WALL tiles, and only the wall tiles.
Constant: the corridor geometry, the light rig, the tile size, the resolution, the floor tiles.

The four arms:
    boundA  composed wall, MOCK bindings, top plane at the R4 part's native value
    boundB  composed wall, MOCK bindings, top plane luminance-matched to the face (derived)
    ctrlA   the same stones as boundA with the overlays omitted
    ctrlB   the same stones as boundB with the overlays omitted

ctrlA/ctrlB are the held-vs-unheld control. They differ from their bound arm by exactly one
thing — whether the binding overlays were drawn — so the delta between the pair IS the answer
to "does it read as HELD", with nothing else able to explain it.

THE SOLO-FLOOR PAIR
-------------------
The briefed floor is the four §6.4 survivors, and that is what the eight arm captures use. The
survivors are four visibly different flagstones and mixing them makes the corridor floor a
patchwork, which competes with the wall for the eye. Two extra captures repeat boundB and ctrlB
with the floor held to the single strongest survivor (A-VAB), so the wall question can also be
read without that competition. Stated rather than substituted: the briefed configuration is
what the arms ran on.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "tier0_harness"))
from capture_corridor import REPO, read_config, capture, sha256, git_commit  # noqa: E402

GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"
ASSETS = "src/Presentation/assets/composition_spike"
ARMS = ["boundA", "boundB", "ctrlA", "ctrlB"]
SOLO_FLOOR_ARMS = ["boundB", "ctrlB"]
SOLO_FLOOR_ID = 9120           # FLOOR_BASE + 0 = A-VAB, the survivor manifest's `strongest`


def write_solo_floor_theme(arm):
    src = os.path.join(REPO, ASSETS, "tile_themes_%s.yaml" % arm)
    dst = os.path.join(REPO, ASSETS, "tile_themes_%s_solofloor.yaml" % arm)
    text = open(src).read()
    text = re.sub(r"^(    floor_\w+): \[.*\]$", r"\1: [%d]" % SOLO_FLOOR_ID, text,
                  flags=re.MULTILINE)
    with open(dst, "w") as f:
        f.write(text)
    return "res://%s/tile_themes_%s_solofloor.yaml" % (ASSETS, arm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="tools/composition_spike/evidence")
    ap.add_argument("--build-only", action="store_true",
                    help="write the derived themes and stop (run Godot --import between)")
    args = ap.parse_args()

    cfg = read_config()
    light = cfg["light"]
    rig = ("ambient=%s color=%s energy=%s radius_tiles=%s (ALL UNDERIVED — §6.2 PLACEHOLDER)"
           % (light["ambient"], light["color"], light["energy"], light["radius_tiles"]))

    jobs = []
    for arm in ARMS:
        theme = "res://%s/tile_themes_%s.yaml" % (ASSETS, arm)
        jobs.append((arm, theme, True))
        jobs.append((arm, theme, False))
    for arm in SOLO_FLOOR_ARMS:
        jobs.append((arm + "_solofloor", write_solo_floor_theme(arm), True))

    print("THE COMPOSITION SPIKE — lit captures")
    print("commit:   %s" % git_commit())
    print("tile:     %sx%s at x%s" % (cfg["tile"]["size"], cfg["tile"]["size"],
                                      cfg["tile"]["scale"]))
    print("rig:      %s   IDENTICAL for every capture below\n" % rig)

    if args.build_only:
        print("--build-only: derived themes written. Run Godot --headless --import, then re-run.")
        return 0

    out_dir = os.path.join(REPO, args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    records = []
    for name, theme, lit in jobs:
        fn = "%s_%s.png" % (name, "lit" if lit else "unlit")
        out = os.path.join(out_dir, fn)
        # Unlit = ambient only: the carried light's energy to zero and nothing else touched,
        # so the pair differs by the carried light and by nothing else.
        overrides = None if lit else {"energy": 0.0}
        rc, log, _ = capture(out, theme, cfg, GODOT, light_overrides=overrides,
                             log_out=out.replace(".png", ".log"))
        if not os.path.exists(out):
            print("ABORT: %s produced no capture (exit %d)" % (fn, rc), file=sys.stderr)
            print(log[-3000:], file=sys.stderr)
            return 1
        engine_rig = next((l.split("light rig:")[1].strip()
                           for l in log.splitlines() if "light rig:" in l), "(not reported)")
        engine_tile = next((l.split("Map renderer:")[1].strip()
                            for l in log.splitlines() if "Map renderer:" in l), "?")
        print("  %-24s sha256=%s" % (fn, sha256(out)[:16]))
        print("      engine rig:  %s" % engine_rig)
        print("      engine tile: %s" % engine_tile)
        records.append(dict(arm=name, lit=lit, file=fn, theme=theme, sha256=sha256(out),
                            engine_rig=engine_rig, engine_tile=engine_tile))

    with open(os.path.join(out_dir, "manifest.json"), "w") as f:
        json.dump(dict(commit=git_commit(), rig_requested=rig,
                       tile_size=cfg["tile"]["size"], tile_scale=cfg["tile"]["scale"],
                       scene=cfg["scene"]["spec"], captures=records), f, indent=1)
    print("\n%d captures -> %s" % (len(records), out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
