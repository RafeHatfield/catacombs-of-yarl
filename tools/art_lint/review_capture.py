#!/usr/bin/env python3
"""Drive an in-scene candidate-review round (review protocol, art-lint-spec Part B 2026-08).

Authors a ReviewSceneBuilder round: candidates seated among approved/canon neighbours of their class
on themed floor, rendered through the production renderer and captured. Candidates enter via
temporary in-place pixel writes to their tile IDs (with a Godot reimport), then are reverted after
capture — nothing lands. A caption bar with full labels is added under the capture. Output →
tools/art_lint/review_scenes/.

A round is a list of cells; each cell is (tileId, label, is_candidate, candidate_png_or_None).
Candidate cells get an orange caption; neighbour (canon/approved) cells get a grey caption.
"""
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
GODOT = "/Applications/Godot_mono.app/Contents/MacOS/Godot"
WDIR = "src/Presentation/assets/sprites_16bf/world_24x24"
OUT = "tools/art_lint/review_scenes"
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 15)
RES = (750, 1334)


def tile_path(tid):
    return f"{WDIR}/oryx_16bit_fantasy_world_{tid}.png"


def reimport():
    subprocess.run([GODOT, "--headless", "--path", REPO, "--import"],
                   capture_output=True, text=True, timeout=300)


def capture(round_json, out_png):
    cmd = [GODOT, "--path", REPO, "--resolution", f"{RES[0]}x{RES[1]}",
           "--art-scene-capture", "--capture-out", out_png,
           "--capture-width", str(RES[0]), "--capture-height", str(RES[1]),
           "--review-scene", round_json]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def run_round(name, title, cells, cols=5, x0=1, y0=2, dx=2, dy=2, map_w=12, map_h=14, player=(6, 7)):
    os.makedirs(OUT, exist_ok=True)
    # layout: grid, row-major
    placed = []
    for i, c in enumerate(cells):
        gx = x0 + (i % cols) * dx
        gy = y0 + (i // cols) * dy
        placed.append((gx, gy, c))

    # temp pixel writes for candidate cells that carry a source PNG
    backups = []
    any_write = False
    for _, _, c in placed:
        tid, label, is_cand, src = c
        if src:
            live = tile_path(tid)
            bak = f"/tmp/review_bak_{tid}.png"
            shutil.copyfile(live, bak)
            shutil.copyfile(src, live)
            backups.append((live, bak))
            any_write = True
    if any_write:
        reimport()

    round_json = f"/tmp/review_round_{name}.json"
    json.dump({"width": map_w, "height": map_h, "playerX": player[0], "playerY": player[1],
               "props": [{"tileId": c[0], "x": gx, "y": gy, "blocks": True} for gx, gy, c in placed]},
              open(round_json, "w"))
    raw_png = f"/tmp/review_{name}.png"
    capture(round_json, raw_png)

    # revert
    for live, bak in backups:
        shutil.copyfile(bak, live)
    if any_write:
        reimport()

    if not os.path.exists(raw_png):
        print(f"ABORT {name}: no capture produced")
        return
    # caption bar under the capture
    cap = Image.open(raw_png).convert("RGBA")
    legend_lines = [f"cell ({gx},{gy}): {c[1]}" for gx, gy, c in placed]
    line_h = 20
    bar_h = 30 + len(legend_lines) * line_h + 10
    out = Image.new("RGBA", (cap.width, cap.height + bar_h), (20, 19, 18, 255))
    out.alpha_composite(cap, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((12, cap.height + 6), title, font=FONT, fill=(255, 220, 150, 255))
    for i, (gx, gy, c) in enumerate(placed):
        col = (240, 170, 60, 255) if c[2] else (150, 150, 150, 255)
        d.text((12, cap.height + 30 + i * line_h), f"cell ({gx},{gy}): {c[1]}", font=FONT, fill=col)
    dst = f"{OUT}/{name}.png"
    out.convert("RGB").save(dst)
    print(f"wrote {dst}  ({len(placed)} cells, {len(backups)} temp-written)")


if __name__ == "__main__":
    import rounds_spec  # noqa
    rounds_spec.main(run_round)
