#!/usr/bin/env python3
"""WHICH REVIEW SCENES CAN EXERCISE A TRAFFIC-KEYED SYSTEM, AND WHICH CANNOT.

    python3 tools/tier1_walls/audit_scene_traffic.py

RULED (Rafe, 2026-08-30): *"Fix the review scenes first: give the corridor scene real traffic
(rooms/destinations) so traffic-keyed systems are actually on — and note which prior verdicts need
re-checking under it."*

The corridor review scene's traffic field is exactly zero: a symmetric cross of one-wide corridors
with no rooms and no dead ends gives `TrafficField` nothing to accumulate. Every traffic-keyed
system is therefore OFF in it — the wall's aging, and **the floor's wear**, which is older and has
had verdicts taken through it.

⚠ THIS AUDITS RATHER THAN ASSUMES. The scene that was found broken was found by accident, while
measuring something else. Guessing which of the others share the defect would be the same mistake
one level up, so every spec in the review set is captured and its ENGINE-REPORTED field is read.
`spine` and `routes` come from the floor painter's own line; the occupancy comes from the traffic
ASCII the engine prints, counted rather than eyeballed.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(HERE, "evidence")
SCENES = os.path.join(REPO, "src/Presentation/assets/tier0_harness/scenes")

TRAFFIC_RE = re.compile(r"traffic=spine:([0-9.]+)/routes:([0-9]+)")


def capture(spec_rel, tag):
    out = os.path.join(EV, "audit_%s.png" % tag)
    log = os.path.join(EV, "audit_%s.log" % tag)
    cmd = [
        "python3", os.path.join(REPO, "tools/tier0_harness/capture_corridor.py"),
        "--out", os.path.relpath(out, REPO),
        "--theme-config", "res://src/Presentation/assets/tier1_ashlar/tile_themes_tier1_ashlar.yaml",
        "--scene-spec", spec_rel,
        "--floor-overlays", "res://src/Presentation/assets/tier1_floors/MANIFEST.json",
        "--ashlar-floor", "res://src/Presentation/assets/tier1_ashlar/MANIFEST.json",
        "--log-out", os.path.relpath(log, REPO),
    ]
    subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=300)
    return log


def read_field(log_path):
    """Occupancy of the engine's own traffic ASCII: how many walkable cells carry any wear."""
    txt = open(log_path, "rb").read().decode("utf8", "replace").splitlines()
    rows, on = [], False
    for line in txt:
        if "traffic field" in line and "DIAG" not in line:
            on = True
            rows = []
            continue
        if on:
            if "[Tier1]   " not in line or "DIAG" in line:
                if rows:
                    break
                continue
            rows.append(line.split("[Tier1]   ", 1)[1])
    walkable = sum(1 for r in rows for c in r if c != "#")
    worn = sum(1 for r in rows for c in r if c not in ("#", " "))
    return walkable, worn


def main():
    specs = sorted(f for f in os.listdir(SCENES) if f.endswith(".json"))
    print("REVIEW-SCENE TRAFFIC AUDIT — the engine's own field, not a re-derivation")
    print("  %-30s %8s %8s %10s %8s   %s"
          % ("spec", "spine", "routes", "walkable", "worn", "verdict"))
    out = {"produced_by": "tools/tier1_walls/audit_scene_traffic.py", "scenes": {}}
    for f in specs:
        rel = "src/Presentation/assets/tier0_harness/scenes/" + f
        tag = f[:-5]
        log = capture(rel, tag)
        txt = open(log, "rb").read().decode("utf8", "replace")
        m = TRAFFIC_RE.search(txt)
        spine, routes = (float(m.group(1)), int(m.group(2))) if m else (None, None)
        walkable, worn = read_field(log)
        dead = (routes == 0) or (worn == 0)
        out["scenes"][tag] = dict(spine=spine, routes=routes, walkable=walkable, worn=worn,
                                  traffic_dead=bool(dead))
        print("  %-30s %8s %8s %10d %8d   %s"
              % (tag, "%.0f" % spine if spine is not None else "-",
                 routes if routes is not None else "-", walkable, worn,
                 "*** NO TRAFFIC - every keyed system is OFF ***" if dead else "live"))
    p = os.path.join(EV, "SCENE-TRAFFIC-AUDIT.json")
    json.dump(out, open(p, "w"), indent=2)
    print("\n  wrote %s" % os.path.relpath(p, REPO))
    dead = [k for k, v in out["scenes"].items() if v["traffic_dead"]]
    if dead:
        print("\n  DEAD: %s" % ", ".join(dead))
        print("  Any verdict about wear, aging, or route legibility taken through one of those")
        print("  scenes was taken with the system switched off, and is re-checkable rather than")
        print("  wrong: the art was there, the field that drives it was not.")


if __name__ == "__main__":
    main()
