#!/usr/bin/env python3
"""THE COMPOSITION SPIKE — lit captures of the composed wall segments, through the tier-0 rig.

ART-BIBLE-v0 §13.1 / LOOP-PROCESS §2.1: verdicts come from the production renderer, in the lit
scene, at true display size. §6.3: a receive-light asset captured unlit is judged by the wrong
instrument, which is why every arm gets an unlit companion rather than a contact sheet.

WHAT VARIES AND WHAT DOES NOT
-----------------------------
Varies: the WALL tiles, and only the wall tiles.
Constant: the corridor geometry, the light rig, the tile size, the resolution, the floor tiles.

THE RULED ROUNDS (Rafe, 2026-08-26): "spend them on edge-occlusion + wall-top value
separation, with south-facing front faces present in scene. Depth arriving ratifies §3; depth
failing reopens it with evidence."

    before         round 6 as shipped: 3px plane-boundary occlusion, top plane at 0.76 of floor
    after          5px occlusion, top plane albedo at 0.62 of floor — THE RULED TEST
    after_unbound  `after` with the MOCK overlays omitted — the held control
    after_noocc    `after`'s albedo with occlusion OFF — isolates §12.1's ruled construction
    plant          `after` plus a baked key light — the within-arm A/B against depicted light

Every arm is the same stones, the same rig, the same geometry and the same floors. `after` vs
`before` is the ruled test; `after` vs `after_noocc` isolates plane-boundary occlusion as the
sole cause of any difference; `after` vs `plant` is authored occlusion against depicted light on
identical stone, which is the comparison §6.4 recorded as never having been run.

THE SOLO-FLOOR PAIR
-------------------
The briefed floor is the four §6.4 survivors, and that is what the ten arm captures use. The
survivors are four visibly different flagstones and mixing them makes the corridor floor a
patchwork, which competes with the wall for the eye. Two extra captures repeat `after` and `after_unbound`
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
ARMS = ["before", "after", "after_unbound", "after_nocap", "plant"]
SOLO_FLOOR_ARMS = ["after", "after_unbound"]

# RULED (Rafe, 2026-08-26): the ruled rounds run "with south-facing front faces present in
# scene". corridor_junction.json puts 7.3% of its wall cells in the class that can carry a face;
# wall_face_review.json puts 14.5% there and both crossings inside the lit radius. The original
# spec is NOT replaced - it is §6.4's instrument and every capture already on disk was taken
# through it - so the scene is selected per capture and named in the manifest.
SCENE = "src/Presentation/assets/tier0_harness/scenes/wall_face_review.json"
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
                             scene_spec=SCENE, log_out=out.replace(".png", ".log"))
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
                       scene=SCENE, captures=records), f, indent=1)
    print("\n%d captures -> %s" % (len(records), out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
