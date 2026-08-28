#!/usr/bin/env python3
"""DERIVE the floor-legibility bounds by sweeping the rig. Floor session two, precondition 2.

`JunctionLitMinRatio` was set by measurement rather than taste — its docstring carries the radius
sweep that put the boundary between 4.0 and 3.5 tiles, where the junction stops being legible.
This does the same job for the floor scene's declared points, and it has to sweep TWO axes because
the floor guard checks two directions:

    RADIUS DOWN   the lit points fall off. Where do they stop reading?
    AMBIENT UP    the dark points brighten. Where does the arc drown?

The ratified rig (Ruling 56: radius 5.0, falloff 1.00, ambient 0.70) is the operating point, and
the bounds want to sit far enough from it that ordinary variation does not trip them, and close
enough that a real failure does.

The capture REFUSES to write a PNG when a declared point fails — but it prints every ratio first,
so the sweep reads the log and does not care whether the image was written. That is deliberate:
a sweep that needed the guard disabled would be measuring a different build.

Nothing here is a verdict. It produces the table the constant is then set from, and the constant
is written into Main.cs by hand so the number and its derivation live together.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools/tier0_harness"))
import capture_corridor as CC      # noqa: E402

THEME = "res://src/Presentation/assets/tier1_floors/tile_themes_tier1_floors.yaml"
SCENE = "src/Presentation/assets/tier0_harness/scenes/tier1_floor_review.json"
OUT = os.path.join(HERE, "controls")
GODOT = os.environ.get("GODOT", "/Applications/Godot_mono.app/Contents/MacOS/Godot")

POINT_RE = re.compile(r"legibility\((\d+),(\d+)\) expect=(lit|dark)\s+ratio=([\d.]+)")


def run(radius=None, ambient=None):
    cfg = CC.read_config()
    ov = {}
    if radius is not None:
        ov["radius_tiles"] = radius
    if ambient is not None:
        ov["ambient_level"] = ambient
    tag = "r%s_a%s" % (radius if radius is not None else "-", ambient if ambient is not None else "-")
    png = os.path.join(OUT, "sweep_%s.png" % tag)
    log = os.path.join(OUT, "sweep_%s.log" % tag)
    _rc, out, _ = CC.capture(png, THEME, cfg, GODOT, light_overrides=ov,
                             scene_spec=SCENE, log_out=log)
    pts = {}
    for m in POINT_RE.finditer(out):
        pts[(int(m.group(1)), int(m.group(2)), m.group(3))] = float(m.group(4))
    if os.path.exists(png):
        os.remove(png)
    return pts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", default="9,7,6,5,4.5,4,3.5,3,2.5,2")
    ap.add_argument("--ambients", default="0.3,0.5,0.7,1.0,1.5,2.0,3.0")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    rows = {"radius": [], "ambient": []}

    print("RADIUS SWEEP (ambient held at the ratified 0.70) — where do the LIT points stop reading?")
    keys = None
    for r in [float(x) for x in a.radii.split(",")]:
        pts = run(radius=r, ambient=0.70)
        if not pts:
            print("  radius %-4s  (no probe output — scene declares no points?)" % r)
            continue
        keys = keys or sorted(pts)
        lit = {k: v for k, v in pts.items() if k[2] == "lit"}
        if not lit:
            print("  radius %-5s  lit points: NONE SAMPLED — the probe refused them" % r)
            continue
        print("  radius %-5s  lit points: %s   min=%.4f"
              % (r, "  ".join("(%d,%d)=%.3f" % (k[0], k[1], v) for k, v in sorted(lit.items())),
                 min(lit.values())))
        rows["radius"].append(dict(radius=r, ambient=0.70,
                                   points={"%d,%d,%s" % k: v for k, v in pts.items()},
                                   min_lit=min(lit.values())))

    print("\nAMBIENT SWEEP (radius held at the ratified 5.0) — where do the DARK points drown?")
    for amb in [float(x) for x in a.ambients.split(",")]:
        pts = run(radius=5.0, ambient=amb)
        if not pts:
            continue
        dark = {k: v for k, v in pts.items() if k[2] == "dark"}
        if not dark:
            # Not a crash: a declared point the probe REFUSED (outside the dungeon view) produces
            # no ratio, and a sweep that died here would hide the refusal behind a traceback.
            print("  ambient %-5s dark points: NONE SAMPLED — the probe refused them; see the log"
                  % amb)
            continue
        print("  ambient %-5s dark points: %s   max=%.4f"
              % (amb, "  ".join("(%d,%d)=%.3f" % (k[0], k[1], v) for k, v in sorted(dark.items())),
                 max(dark.values())))
        rows["ambient"].append(dict(radius=5.0, ambient=amb,
                                    points={"%d,%d,%s" % k: v for k, v in pts.items()},
                                    max_dark=max(dark.values())))

    p = os.path.join(OUT, "LEGIBILITY-SWEEP.json")
    with open(p, "w") as f:
        json.dump(dict(commit=subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                                             capture_output=True, text=True).stdout.strip(),
                       scene=SCENE, sweeps=rows), f, indent=1)
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
