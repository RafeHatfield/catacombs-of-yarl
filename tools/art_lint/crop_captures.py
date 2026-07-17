#!/usr/bin/env python3
"""Produce the three 6x nearest-neighbor crops from a full-viewport art scene capture.

Tile-rect -> pixel-rect conversion reimplements the exact camera transform the renderer
used to produce the capture:
    src/Presentation/Map/TopDownRenderer.cs   GridToScreen(x,y) = (x*tile_size, y*tile_size)
    src/Presentation/Map/PlayerCamera.cs      Update(): gameView.Scale = zoom;
                                               gameView.Position = (viewport.x/2 - playerScreen.x*zoom,
                                                                     centerY - playerScreen.y*zoom)
All constants (tile_size, zoom, UI margins, player_tile) come from
scene_capture_config.yaml, not hardcoded here, so a config change and a source change
can't silently drift apart from each other without at least being visible in one diff.
"""
import argparse
import re
import sys

from PIL import Image

UPSCALE = 6


def read_config(config_path):
    text = open(config_path).read()

    def scalar(block_key, field_key, cast=float):
        m = re.search(rf"^{block_key}:\s*\n(?:.*\n)*?\s*{field_key}:\s*([\d.]+)",
                       text, re.MULTILINE)
        if not m:
            raise ValueError(f"Could not find {block_key}.{field_key} in {config_path}")
        return cast(m.group(1))

    width = scalar("resolution", "width", int)
    height = scalar("resolution", "height", int)
    tile_size = scalar("camera", "tile_size", int)
    zoom = scalar("camera", "zoom", float)
    ui_top = scalar("camera", "ui_top_margin", float)
    ui_bottom = scalar("camera", "ui_bottom_margin", float)

    m = re.search(r"player_tile:\s*\[(\d+),\s*(\d+)\]", text)
    if not m:
        raise ValueError(f"Could not find camera.player_tile in {config_path}")
    player_tile = (int(m.group(1)), int(m.group(2)))

    crops = _parse_crops(text)

    return {
        "resolution": (width, height),
        "tile_size": tile_size,
        "zoom": zoom,
        "ui_top_margin": ui_top,
        "ui_bottom_margin": ui_bottom,
        "player_tile": player_tile,
        "crops": crops,
    }


def _parse_crops(text):
    """Line-by-line parse of the crops: list — deliberately not one regex, so each
    crop's name/description/tile_rect can't cross-contaminate with its neighbors."""
    lines = text.splitlines()
    crops = []
    current = None
    in_crops = False
    for line in lines:
        if re.match(r"^crops:\s*$", line):
            in_crops = True
            continue
        if not in_crops:
            continue
        if re.match(r"^\S", line):  # dedented to column 0 — crops: block ended
            break

        m = re.match(r"\s*- name:\s*(\S+)\s*$", line)
        if m:
            if current:
                crops.append(current)
            current = {"name": m.group(1), "description": "", "tile_rect": None}
            continue

        if current is None:
            continue

        m = re.match(r"\s*tile_rect:\s*\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]", line)
        if m:
            current["tile_rect"] = tuple(int(g) for g in m.groups())
            continue

        if re.match(r"\s*description:\s*>?\s*$", line):
            continue  # description header line, content follows on subsequent lines

        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            current["description"] = (current["description"] + " " + stripped).strip()

    if current:
        crops.append(current)

    for c in crops:
        if c["tile_rect"] is None:
            raise ValueError(f"crop '{c['name']}' has no tile_rect")
    return crops


def game_view_position(cfg):
    vw, vh = cfg["resolution"]
    ts = cfg["tile_size"]
    zoom = cfg["zoom"]
    px, py = cfg["player_tile"]
    player_screen = (px * ts, py * ts)
    center_y = cfg["ui_top_margin"] + (vh - cfg["ui_top_margin"] - cfg["ui_bottom_margin"]) / 2
    return (vw / 2 - player_screen[0] * zoom, center_y - player_screen[1] * zoom)


def tile_to_pixel(cfg, gv_pos, tx, ty):
    ts, zoom = cfg["tile_size"], cfg["zoom"]
    local = (tx * ts, ty * ts)
    return (local[0] * zoom + gv_pos[0], local[1] * zoom + gv_pos[1])


def tile_rect_to_pixel_box(cfg, gv_pos, tile_rect):
    x0, y0, x1, y1 = tile_rect
    # Inclusive tile range -> include the full extent of tile (x1, y1), not just its corner.
    p0 = tile_to_pixel(cfg, gv_pos, x0, y0)
    p1 = tile_to_pixel(cfg, gv_pos, x1 + 1, y1 + 1)
    return (round(p0[0]), round(p0[1]), round(p1[0]), round(p1[1]))


def main():
    parser = argparse.ArgumentParser(description="Crop the art scene capture per scene_capture_config.yaml")
    parser.add_argument("--capture", required=True, help="Full-viewport capture PNG")
    parser.add_argument("--config", default="tools/art_lint/scene_capture_config.yaml")
    parser.add_argument("--out-prefix", required=True,
                         help="Output path prefix; crop name is appended, e.g. prefix_crop1_chest_key_items.png")
    args = parser.parse_args()

    cfg = read_config(args.config)
    im = Image.open(args.capture).convert("RGBA")
    if im.size != cfg["resolution"]:
        print(f"WARNING: capture is {im.size}, config resolution is {cfg['resolution']} — "
              f"crop rectangles were computed for the configured resolution.", file=sys.stderr)

    gv_pos = game_view_position(cfg)

    for crop in cfg["crops"]:
        box = tile_rect_to_pixel_box(cfg, gv_pos, crop["tile_rect"])
        clamped = (
            max(0, box[0]), max(0, box[1]),
            min(im.width, box[2]), min(im.height, box[3]),
        )
        if clamped[2] <= clamped[0] or clamped[3] <= clamped[1]:
            print(f"ABORT: crop '{crop['name']}' tile_rect {crop['tile_rect']} -> pixel box "
                  f"{box} is entirely outside the {im.size} capture — nothing to crop.",
                  file=sys.stderr)
            sys.exit(1)
        if clamped != box:
            print(f"NOTE: crop '{crop['name']}' pixel box {box} was clamped to {clamped} "
                  f"(partially outside the capture).", file=sys.stderr)

        region = im.crop(clamped)
        upscaled = region.resize(
            (region.width * UPSCALE, region.height * UPSCALE), Image.NEAREST)
        out_path = f"{args.out_prefix}_{crop['name']}.png"
        upscaled.save(out_path)
        print(f"{crop['name']}: tile_rect={crop['tile_rect']} pixel_box={clamped} "
              f"-> {upscaled.size} -> {out_path}")


if __name__ == "__main__":
    main()
