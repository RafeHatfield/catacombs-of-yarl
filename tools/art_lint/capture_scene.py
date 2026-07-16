#!/usr/bin/env python3
"""Launch the art acceptance scene and capture a full-viewport PNG.

Reuses Main.LaunchArtAcceptanceScene (the exact --art-scene boot path) via the
--art-scene-capture Godot CLI flag — this script does no scene composition of its own,
it only invokes the engine and reads its own resolution config back out for logging.

Resolution comes from scene_capture_config.yaml (single source of truth), passed to
Godot's own --resolution engine flag — Main.cs does not read this file itself, so there
is exactly one place resolution is configured.
"""
import argparse
import os
import re
import subprocess
import sys

DEFAULT_GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(REPO_ROOT, "tools/art_lint/scene_capture_config.yaml")


def read_resolution(config_path):
    width = height = None
    in_resolution_block = False
    with open(config_path) as f:
        for line in f:
            if re.match(r"^resolution:\s*$", line):
                in_resolution_block = True
                continue
            if in_resolution_block:
                if re.match(r"^\S", line):  # dedented — block ended
                    break
                m = re.match(r"\s*width:\s*(\d+)", line)
                if m:
                    width = int(m.group(1))
                m = re.match(r"\s*height:\s*(\d+)", line)
                if m:
                    height = int(m.group(1))
    if width is None or height is None:
        raise ValueError(f"Could not read resolution.width/height from {config_path}")
    return width, height


def capture(godot_path, output_path, log_path=None, timeout=60):
    width, height = read_resolution(CONFIG_PATH)
    cmd = [
        godot_path,
        "--path", REPO_ROOT,
        "--resolution", f"{width}x{height}",
        "--art-scene-capture",
        "--capture-out", output_path,
        # project.godot pins the render canvas to its base viewport size (720x1280) via
        # stretch mode (canvas_items/keep_width/integer) regardless of --resolution, which
        # only resizes the OS window around that fixed canvas. --capture-width/-height tell
        # Main.cs to override the canvas size itself (ContentScaleSize) for this run only —
        # without these, the capture would silently come out at 720x1280, not the configured
        # resolution. See Main.ReadArtSceneCaptureResolution.
        "--capture-width", str(width),
        "--capture-height", str(height),
    ]
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    log = proc.stdout + proc.stderr
    if log_path:
        os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
        with open(log_path, "w") as f:
            f.write(log)
    return proc.returncode, log, (width, height)


def main():
    parser = argparse.ArgumentParser(description="Capture the art acceptance scene")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--log-out", help="Optional path to save the Godot stdout/stderr log")
    parser.add_argument("--godot", default=DEFAULT_GODOT)
    args = parser.parse_args()

    returncode, log, (w, h) = capture(args.godot, args.out, args.log_out)

    if not os.path.exists(args.out):
        print(f"ABORT: capture did not produce {args.out}", file=sys.stderr)
        print(log, file=sys.stderr)
        sys.exit(1)

    print(f"Captured {args.out} at {w}x{h} (exit code {returncode})")
    for line in log.splitlines():
        if "[Main]" in line and ("Capture written" in line or "floor_worn" in line
                                  or "Visible tile rect" in line or "Map renderer" in line):
            print(f"  {line.strip()}")

    sys.exit(0 if returncode == 0 else 1)


if __name__ == "__main__":
    main()
