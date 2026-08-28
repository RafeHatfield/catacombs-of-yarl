#!/usr/bin/env python3
"""Tier 0 review harness — capture the lit review corridor from the production renderer.

ART-BIBLE-v0 §13.1: no candidate is ever approved from a contact sheet. Verdicts come from the
production renderer, in the lit scene, at true display size. This script is the reproducible
half of that: it boots the real game binary with the real renderer, assembles the authored
corridor, attaches the engine light rig, and captures the settled viewport at the reference
device's pixel size.

It composes no scene of its own. Geometry comes from the corridor spec JSON, tiles come from
whatever tile-theme config it is pointed at, and light values come from harness_config.yaml —
so what this file contributes is only the invocation and the evidence trail.

Reuses the retired Oryx track's corpus-agnostic capture plumbing per tools/art_lint/NOTICE.md:
the --art-scene-capture engine path, ContentScaleSize override, and settle-then-capture
sequence are unchanged and were never Oryx-specific.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(REPO, "tools/tier0_harness/harness_config.yaml")
DEFAULT_GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"


def read_config(path=CONFIG):
    """Minimal reader for this file's flat two-level shape.

    Hand-rolled rather than PyYAML for the same reason TileThemeLoader is: the repo does not
    depend on PyYAML, and the shape here is fixed and simple. Unknown keys are preserved as
    strings; nothing is coerced beyond int/float where the value looks numeric.
    """
    cfg, section = {}, None
    with open(path) as f:
        for line in f:
            line = line.split("#", 1)[0].rstrip()
            if not line.strip():
                continue
            if re.match(r"^\S", line):
                section = line.split(":", 1)[0].strip()
                cfg[section] = {}
                continue
            m = re.match(r"^\s{2}([A-Za-z_]+):\s*(.*)$", line)
            if m and section:
                k, v = m.group(1), m.group(2).strip().strip('"')
                if v == "":
                    cfg[section][k] = {}
                    continue
                if re.fullmatch(r"-?\d+", v):
                    v = int(v)
                elif re.fullmatch(r"-?\d*\.\d+", v):
                    v = float(v)
                cfg[section][k] = v
                continue
            m = re.match(r"^\s{4}([A-Za-z_]+):\s*(.*)$", line)
            if m and section:
                last = list(cfg[section])[-1] if cfg[section] else None
                if last is not None and isinstance(cfg[section][last], dict):
                    cfg[section][last][m.group(1)] = m.group(2).strip().strip('"')
    return cfg


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


def capture(out_png, theme_config, cfg, godot=DEFAULT_GODOT,
            light_overrides=None, scene_spec=None, log_out=None, timeout=180,
            floor_overlays=None):
    """Invoke the engine. Returns (returncode, log, cmd)."""
    w = cfg["resolution"]["width"]
    h = cfg["resolution"]["height"]
    light = dict(cfg["light"])
    if light_overrides:
        light.update(light_overrides)
    tile = dict(cfg["tile"])

    spec = scene_spec or cfg["scene"]["spec"]
    # Main reads the spec through Godot's FileAccess (so the same path works inside the packed
    # .pck on device), which resolves res:// but not a repo-relative path.
    if not spec.startswith(("res://", "user://", "/")):
        spec = "res://" + spec

    cmd = [
        godot, "--path", REPO,
        "--resolution", f"{w}x{h}",
        "--art-scene-capture", "--capture-out", out_png,
        "--capture-width", str(w), "--capture-height", str(h),
        "--corridor-scene", spec,
        "--tile-theme-config", theme_config,
        # Tile size is a PARAMETER, and until this was passed it was a parameter in name only:
        # the config could declare 32 and TopDownRenderer would draw a 24px grid regardless, so
        # a capture could silently disagree with its own manifest. The engine echoes what it
        # actually used, so the capture log carries the grid it was drawn on.
        "--tile-size", str(tile["size"]),
        "--tile-scale", str(tile["scale"]),
        # Every light value is passed explicitly. The engine REFUSES to default any of them
        # (Main.ReadLightParams), so no capture can be produced by an undeclared rig.
        "--light-ambient", str(light["ambient"]),
        "--light-color", str(light["color"]),
        "--light-energy", str(light["energy"]),
        "--light-radius-tiles", str(light["radius_tiles"]),
        # RULED at the §6.2.1 gate (Ruling 56) and therefore PASSED EXPLICITLY, not defaulted.
        # These two were code defaults until the pass ratified them, and a ratified value that
        # can be silently defaulted is a ratified value that can silently drift. The engine
        # requires both, on the same discipline as the other four: no capture is produced by an
        # undeclared rig.
        "--light-falloff", str(light["falloff"]),
        "--light-ambient-level", str(light["ambient_level"]),
    ]
    # ART-BIBLE-v0 §8.3's incident overlays, added for the tier-one floor round. Optional: a
    # capture taken without it draws base tiles only, which is what every capture before tier
    # one did. The engine reports which branch it took either way, so a capture cannot silently
    # be missing the incident system and look like a floor that simply has no incident on it.
    if floor_overlays:
        cmd += ["--floor-overlays", floor_overlays]

    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    log = proc.stdout + proc.stderr
    if log_out:
        os.makedirs(os.path.dirname(log_out) or ".", exist_ok=True)
        with open(log_out, "w") as f:
            f.write(" ".join(cmd) + "\n\n" + log)
    return proc.returncode, log, cmd


def echo_evidence(out_png, log):
    """Print the lines that make a capture self-describing — rig, scene, junction, commit."""
    for line in log.splitlines():
        if "[Tier0]" in line or "Capture written" in line or "Map renderer" in line:
            print("  " + line.strip())
    if os.path.exists(out_png):
        print(f"  sha256: {sha256(out_png)}")
        print(f"  bytes:  {os.path.getsize(out_png)}")
        print(f"  commit: {git_commit()}")


def main():
    ap = argparse.ArgumentParser(description="Capture the Tier 0 lit review corridor")
    ap.add_argument("--out", required=True)
    ap.add_argument("--theme-config", default="res://src/Presentation/assets/tier0_harness/tile_themes_stub.yaml")
    ap.add_argument("--scene-spec", help="Override the corridor spec path")
    ap.add_argument("--light-energy", help="Override light energy (positive control)")
    ap.add_argument("--light-radius-tiles",
                    help="Override the carried light's reach (junction-lit positive control)")
    ap.add_argument("--floor-overlays",
                    help="res:// path to a floor family MANIFEST.json — ART-BIBLE-v0 §8.3's "
                         "incident overlays and §8.2.1's trodden channel. Omitted, the capture "
                         "draws base tiles only and the engine says so in the log.")
    ap.add_argument("--log-out")
    ap.add_argument("--godot", default=DEFAULT_GODOT)
    args = ap.parse_args()

    cfg = read_config()
    overrides = {}
    if args.light_energy is not None:
        overrides["energy"] = args.light_energy
    if args.light_radius_tiles is not None:
        overrides["radius_tiles"] = args.light_radius_tiles

    rc, log, cmd = capture(args.out, args.theme_config, cfg, args.godot,
                           light_overrides=overrides, scene_spec=args.scene_spec,
                           log_out=args.log_out, floor_overlays=args.floor_overlays)

    if not os.path.exists(args.out):
        # Exit 2 from the engine is a REFUSED capture (junction-lit check failed), not a crash.
        # Surfaced distinctly so the controls can assert the refusal rather than just "no file".
        refused = rc == 2 or "CAPTURE REFUSED" in log
        for line in log.splitlines():
            if "[Tier0]" in line and ("JUNCTION-LIT" in line or "REFUSED" in line
                                      or "junction-lit probe" in line or "MISFED" in line
                                      or "Fix:" in line):
                print("  " + line.strip(), file=sys.stderr)
        print(f"{'REFUSED' if refused else 'ABORT'}: no capture written to {args.out}",
              file=sys.stderr)
        sys.exit(2 if refused else 1)

    print(f"Captured {args.out} at {cfg['resolution']['width']}x{cfg['resolution']['height']} (exit {rc})")
    echo_evidence(args.out, log)
    sys.exit(0 if rc == 0 else 1)


if __name__ == "__main__":
    main()
