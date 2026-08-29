#!/usr/bin/env python3
"""POSITIVE CONTROL for the floor-legibility guard. Floor session two, precondition 2.

    §13.5 / LOOP-PROCESS §4: no instrument's pass counts until it has demonstrated it can fail.

The guard checks TWO directions, so it needs TWO plants — and that is the whole reason this file
is not one arm:

    RADIUS DOWN   the subject falls out of the carried light. The classic MISFED: the scene still
                  renders, still passes determinism, and the critic is asked about ground it
                  cannot see.
    AMBIENT UP    the arc drowns. §6.2.1 rules the readability pass "not a licence to flood the
                  Boundary with light" — *you begin as the only thing here that burns* is register
                  and outranks convenience. A guard that only asked "is it bright enough" is blind
                  to this failure BY CONSTRUCTION, and would green it.

LOOP-PROCESS §4.1, LAW — the plant carries the defect on the axis the lever claims. Each arm
therefore has to fail for the RIGHT reason: the dark arm must fail on lit points and pass its dark
ones; the flooded arm must fail on dark points and pass its lit ones. An arm that failed on both
would prove only that the scene had been broken, not that the guard discriminates.

AND THE REFUSAL IS PART OF THE CHECK. A guard that logs FAIL and writes the PNG anyway has done
nothing — the artefact still exists and will be looked at. Each failing arm must produce NO IMAGE.
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

POINT_RE = re.compile(
    r"legibility\((\d+),(\d+)\) expect=(lit|dark)\s+ratio=([\d.]+).*?(OK|FAIL)")
VERDICT_RE = re.compile(r"floor-legibility probe: (\d+) declared points, "
                        r"reference lum=([\d.]+), verdict=(PASS|FAIL)")

ARMS = [
    ("ratified", dict(),                     "the rig as ruled — must PASS and write a PNG"),
    ("dark",     dict(radius_tiles=4.0),     "radius 4.0: the subject falls out of the light"),
    ("flooded",  dict(ambient_level=2.0),    "ambient 2.0: the arc is drowned"),
]


def run(tag, overrides):
    cfg = CC.read_config()
    png = os.path.join(OUT, "legib_%s.png" % tag)
    log = os.path.join(OUT, "legib_%s.log" % tag)
    if os.path.exists(png):
        os.remove(png)
    rc, out, _ = CC.capture(png, THEME, cfg, GODOT, light_overrides=overrides,
                            scene_spec=SCENE, log_out=log)
    pts = [dict(x=int(m.group(1)), y=int(m.group(2)), expect=m.group(3),
                ratio=float(m.group(4)), verdict=m.group(5))
           for m in POINT_RE.finditer(out)]
    v = VERDICT_RE.search(out)
    return dict(tag=tag, overrides=overrides, rc=rc,
                png_written=os.path.exists(png),
                verdict=v.group(3) if v else "MISSING",
                points=pts, log=os.path.relpath(log, REPO))


def main():
    ap = argparse.ArgumentParser()
    ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    print("CONTROL — the floor-legibility guard, shown able to fail in both directions\n")
    res = {}
    for tag, ov, why in ARMS:
        r = run(tag, ov)
        res[tag] = r
        lit = [p for p in r["points"] if p["expect"] == "lit"]
        dark = [p for p in r["points"] if p["expect"] == "dark"]
        print("  arm %-9s %s" % (tag, why))
        print("     verdict=%-7s png_written=%-5s  lit=%s  dark=%s"
              % (r["verdict"], r["png_written"],
                 " ".join("%.3f%s" % (p["ratio"], "" if p["verdict"] == "OK" else "!") for p in lit),
                 " ".join("%.3f%s" % (p["ratio"], "" if p["verdict"] == "OK" else "!") for p in dark)))

    rat, dk, fl = res["ratified"], res["dark"], res["flooded"]

    def failed(points, kind):
        return [p for p in points if p["expect"] == kind and p["verdict"] == "FAIL"]

    checks = [
        ("ratified rig PASSES and writes an image",
         rat["verdict"] == "PASS" and rat["png_written"]),
        ("shrinking the radius FAILS the guard",
         dk["verdict"] == "FAIL"),
        ("...and it fails on LIT points (the axis the radius moves)",
         len(failed(dk["points"], "lit")) > 0),
        ("...while its DARK points still pass (so the scene is not merely broken)",
         len(failed(dk["points"], "dark")) == 0),
        ("...and NO image is written",
         not dk["png_written"]),
        ("flooding the ambient FAILS the guard",
         fl["verdict"] == "FAIL"),
        ("...and it fails on DARK points (the axis ambient moves)",
         len(failed(fl["points"], "dark")) > 0),
        ("...while its LIT points still pass",
         len(failed(fl["points"], "lit")) == 0),
        ("...and NO image is written",
         not fl["png_written"]),
    ]
    print("\n== verdict")
    ok = True
    for name, passed in checks:
        print("  %-62s %s" % (name, "PASS" if passed else "*** FAIL ***"))
        ok = ok and passed

    out = dict(commit=subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                                     capture_output=True, text=True).stdout.strip(),
               instrument="Main.ProbeFloorLegibility",
               bounds=dict(lit_min=0.12, dark_max=0.10),
               law=("LOOP-PROCESS §4.1 — each plant carries the defect on the axis the guard "
                    "claims, and each failing arm must also REFUSE the artefact: a guard that "
                    "logs FAIL and writes the PNG anyway has done nothing."),
               arms=res, checks=[dict(check=n, passed=p) for n, p in checks], all_passed=ok)
    p = os.path.join(OUT, "LEGIBILITY-CONTROL.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    print("\n%s" % ("CONTROL PASSED — the guard fails on both axes and refuses the artefact."
                    if ok else "CONTROL FAILED — the guard is decorative until this passes."))
    print("written: %s" % os.path.relpath(p, REPO))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
