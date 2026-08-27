#!/usr/bin/env python3
"""Contact sheets — evidence, never a shortlist (bible §13.1).

Two products, and the difference matters:

  * `--zoom N` writes a nearest-neighbour magnified sheet for a human to read a 32px tile at
    all. Magnification is a reading aid; nothing is judged at 4x that would not be judged at 1x.
  * the critic set is written at NATIVE size, one file per tile, because a sheet lets a critic
    compare candidates against each other instead of against the questions.

Usage:
  sheet.py <kit_dir> <out.png> [--zoom 4] [--set wall|all] [--label]
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

# The wall set: everything that is a piece of standing wall. Deliberately excludes floor (0),
# floor_roof (44), the whole gable roof (60-79), stairs/slopes (40-43, 56-59) and doors
# (32-39, 45-48) — a doorway is an opening, and judging one against a wall bar is the
# scope error LOOP-PROCESS §2.2 exists to stop.
WALL_SET = list(range(1, 32)) + list(range(49, 56))


def load_kit(d):
    kit = {}
    for fn in sorted(os.listdir(d)):
        if fn.startswith("tile_") and fn.endswith(".png"):
            kit[int(fn[5:-4])] = Image.open(os.path.join(d, fn)).convert("RGBA")
    return kit


def part_names(d):
    """index -> human part name, straight from the returned grammar."""
    p = os.path.join(d, "tile_rules.json")
    if not os.path.exists(p):
        return {}
    rules = json.load(open(p)) or {}
    names = {}

    def walk(node, prefix):
        if isinstance(node, int):
            names[node] = prefix
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, prefix + "." + k if prefix else k)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (prefix, i))
    for k, v in (rules.get("parts") or {}).items():
        if k in ("materials", "painted"):
            continue
        walk(v, k)
    return names


def build(kit_dir, out, zoom=4, which="wall", label=True, cols=8, bg=(24, 24, 28, 255)):
    kit = load_kit(kit_dir)
    names = part_names(kit_dir)
    painted = set()
    p = os.path.join(kit_dir, "tile_rules.json")
    if os.path.exists(p):
        rules = json.load(open(p)) or {}
        painted = set((rules.get("parts") or {}).get("painted") or [])

    idx = [i for i in (WALL_SET if which == "wall" else sorted(kit)) if i in kit]
    if not idx:
        raise SystemExit("no tiles for set " + which)
    tw = max(kit[i].width for i in idx) * zoom
    th = max(kit[i].height for i in idx) * zoom
    pad, cap = 8, (16 if label else 0)
    rows = (len(idx) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * (tw + pad) + pad,
                               rows * (th + cap + pad) + pad), bg)
    dr = ImageDraw.Draw(sheet)
    for n, i in enumerate(idx):
        r, c = divmod(n, cols)
        x = pad + c * (tw + pad)
        y = pad + r * (th + cap + pad)
        im = kit[i].resize((kit[i].width * zoom, kit[i].height * zoom), Image.NEAREST)
        sheet.alpha_composite(im, (x, y))
        if label:
            mark = "*" if i in painted else " "
            dr.text((x, y + th + 2), "%02d%s %s" % (i, mark, names.get(i, "")[:18]),
                    fill=(200, 200, 205, 255))
    sheet.save(out)
    print("%s  %d tiles, zoom=%d, %s  (* = individually painted)" %
          (out, len(idx), zoom, sheet.size))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kit_dir")
    ap.add_argument("out")
    ap.add_argument("--zoom", type=int, default=4)
    ap.add_argument("--set", dest="which", default="wall", choices=["wall", "all"])
    ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--no-label", dest="label", action="store_false")
    a = ap.parse_args()
    build(a.kit_dir, a.out, a.zoom, a.which, a.label, a.cols)


if __name__ == "__main__":
    main()
