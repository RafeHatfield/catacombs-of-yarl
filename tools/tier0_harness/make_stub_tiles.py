#!/usr/bin/env python3
"""Generate obviously-fake programmer-art stub tiles for the Tier 0 review harness.

THESE ARE NOT ART AND THEY ARE NOT A PALETTE PROPOSAL.

They are test fixtures whose entire job is to prove the harness renders, lights, and captures
whatever tiles it is pointed at. They are drawn in deliberately synthetic debug colours
(magenta walls, teal floor) precisely so that nobody can mistake them for a candidate, and so
that a swapped tile is unmistakable in a capture diff. ART-BIBLE-v0 §5 marks all palette values
PLACEHOLDER; nothing here proposes one.

TILE SIZE IS A PARAMETER (--size), never a constant. ART-BIBLE-v0 §4.3 marks canvas and tile
sizes PLACEHOLDER, so this script refuses to bake one in. The default comes from
harness_config.yaml's tile.size, which records the renderer's current hard-coded 24 as an
UNDERIVED parameter rather than a derived value.
"""
import argparse
import os
import struct
import zlib

# Tile ID allocation. A distinct 9xxx block so a stub can never be confused with, or collide
# with, any tile ID in the shipped config.
FLOOR_PRIMARY  = 9001
FLOOR_ACCENT   = 9002
FLOOR_DARK     = 9003
FLOOR_WORN     = 9004
WALL_MASK_BASE = 9010          # 9010..9025 for autotile masks 0..15
WALL_DIAG_BASE = 9030          # 9030..9034
STAIR_DOWN     = 9040
STAIR_UP       = 9041


def write_png(path, size, pixels):
    """Minimal RGBA PNG writer — no PIL dependency, deterministic output."""
    raw = b"".join(b"\x00" + bytes(row) for row in pixels)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    # Fixed compression level so the bytes are reproducible run to run.
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def solid(size, rgb, border_rgb=None, mark=None):
    """A flat tile, optional 1px border, optional corner mark — deliberately crude."""
    r, g, b = rgb
    rows = []
    for y in range(size):
        row = []
        for x in range(size):
            c = (r, g, b, 255)
            edge = x == 0 or y == 0 or x == size - 1 or y == size - 1
            if border_rgb and edge:
                c = (border_rgb[0], border_rgb[1], border_rgb[2], 255)
            # Corner mark: a small filled square so orientation and identity are visible
            # at true display size without needing to read a number.
            if mark and x < size // 4 and y < size // 4:
                c = (mark[0], mark[1], mark[2], 255)
            row.extend(c)
        rows.append(row)
    return rows


def generate(out_dir, size, pattern, variant):
    """variant shifts the debug hue so different arms/rounds are visually separable."""
    os.makedirs(out_dir, exist_ok=True)
    v = variant * 40 % 200

    written = []

    def emit(tile_id, rgb, border, mark=None):
        path = os.path.join(out_dir, pattern.replace("{id}", str(tile_id)))
        write_png(path, size, solid(size, rgb, border, mark))
        written.append((tile_id, path))

    # Floors — teal family. Distinct enough from walls that a floor/wall swap is obvious.
    emit(FLOOR_PRIMARY, (30, 90 + v // 4, 95), (20, 60, 65))
    emit(FLOOR_ACCENT,  (35, 110 + v // 4, 115), (20, 60, 65))
    emit(FLOOR_DARK,    (18, 55, 60), (12, 40, 44))
    emit(FLOOR_WORN,    (60, 120 + v // 4, 120), (20, 60, 65), mark=(255, 255, 0))

    # Walls — magenta family, with a bright corner mark so autotile masks are distinguishable.
    for mask in range(16):
        shade = 120 + mask * 6
        emit(WALL_MASK_BASE + mask, (shade, 30 + v // 6, shade), (60, 15, 60),
             mark=(255, 255, 255))

    # Wall diagonals + interior fill.
    for i in range(5):
        emit(WALL_DIAG_BASE + i, (150, 40 + v // 6, 150), (60, 15, 60), mark=(200, 200, 255))

    emit(STAIR_DOWN, (200, 200, 60), (80, 80, 20))
    emit(STAIR_UP,   (200, 160, 60), (80, 60, 20))

    return written


def theme_yaml(tile_root, pattern, floor_primary_id=FLOOR_PRIMARY, floor_all_id=None):
    """Emit a tile_themes.yaml pointed at the stub tiles.

    floor_primary_id / floor_all_id are parameters so the 'scene is real' positive control can
    point a floor role at a WALL tile id and prove the capture reflects it.

    floor_all_id overrides EVERY floor role. That exists because of a finding the control itself
    surfaced: FloorComposer's Pass 2 marks any wall-adjacent tile Dark and never overrides it, so
    in a ONE-TILE-WIDE CORRIDOR every floor cell is Dark and floor_primary is never rendered at
    all. A control that swapped only floor_primary planted its defect in a dead role and passed
    a swap through unnoticed — it reported a difference of 0.0000% of pixels. Overriding every
    role makes the control independent of which pass wins.
    """
    masks = "\n".join(f"      {m}: {WALL_MASK_BASE + m}" for m in range(16))
    fp = floor_all_id if floor_all_id is not None else floor_primary_id
    fa = floor_all_id if floor_all_id is not None else FLOOR_ACCENT
    fd = floor_all_id if floor_all_id is not None else FLOOR_DARK
    fi = floor_all_id if floor_all_id is not None else FLOOR_PRIMARY
    fw = floor_all_id if floor_all_id is not None else FLOOR_WORN
    return f"""# GENERATED by tools/tier0_harness/make_stub_tiles.py — do not hand-edit.
# Stub programmer-art tiles for the Tier 0 review harness. Not art, not a palette.
tile_root: "{tile_root}"
tile_pattern: "{pattern}"

themes:
  sandstone:
    floor_primary: [{fp}]
    floor_accent: [{fa}]
    floor_dark: [{fd}]
    floor_interior: [{fi}]
    floor_worn: [{fw}]
    wall_autotile:
{masks}
    wall_diagonal:
      corner_outer_nw: {WALL_DIAG_BASE + 0}
      corner_outer_ne: {WALL_DIAG_BASE + 1}
      corner_outer_sw: {WALL_DIAG_BASE + 2}
      corner_outer_se: {WALL_DIAG_BASE + 3}
      interior_fill: {WALL_DIAG_BASE + 4}
    stair_down: [{STAIR_DOWN}]
    stair_up: [{STAIR_UP}]

default_theme: sandstone
"""


def main():
    ap = argparse.ArgumentParser(description="Generate Tier 0 stub tiles")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--size", type=int, required=True,
                    help="Tile edge in px. A PARAMETER (bible §4.3 PLACEHOLDER) — no default.")
    ap.add_argument("--pattern", default="tier0_stub_{id}.png")
    ap.add_argument("--variant", type=int, default=0)
    ap.add_argument("--theme-out", help="Also write a tile_themes.yaml pointed at these tiles")
    ap.add_argument("--tile-root", help="res:// root recorded in the theme yaml")
    ap.add_argument("--floor-primary-id", type=int, default=FLOOR_PRIMARY,
                    help="Override the floor_primary tile id (used by the scene-is-real control)")
    ap.add_argument("--floor-all-id", type=int, default=None,
                    help="Override EVERY floor role — see theme_yaml docstring")
    args = ap.parse_args()

    written = generate(args.out_dir, args.size, args.pattern, args.variant)
    print(f"wrote {len(written)} stub tiles at {args.size}x{args.size} -> {args.out_dir}")

    if args.theme_out:
        if not args.tile_root:
            raise SystemExit("--theme-out requires --tile-root")
        with open(args.theme_out, "w") as f:
            f.write(theme_yaml(args.tile_root, args.pattern, args.floor_primary_id, args.floor_all_id))
        print(f"wrote theme config -> {args.theme_out} (floor_primary={args.floor_primary_id})")


if __name__ == "__main__":
    main()
