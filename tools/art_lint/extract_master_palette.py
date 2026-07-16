#!/usr/bin/env python3
"""Extract the canonical Oryx master palette from source sprite sheets.

Contamination guard: world_24x24 and items_16x16 both contain generated tiles
living under Oryx naming, mixed in with the canonical Oryx import. Only the
canonical tiles belong in the master palette. If generated tiles leak into
this extraction, the palette silently absorbs off-palette colors and every
downstream snap/verify check becomes a no-op (sprites "snap" to their own
already-wrong colors).

The exclusion sets below were derived from git provenance, not guessed: a
file is canonical iff it was added in ae5969f ("chore: add 16-bit fantasy
sprite assets"), the original bulk import. Everything added in later commits
(447f523 "room prop system, placeholder sprites", c5af9dd, f953c23 "adopt
PixelLab as primary sprite tool", fccf258, 676847a) is generated content that
happens to sit in the same directories under Oryx-style filenames:
  - world_24x24: ID >= 5000 (72 files) is the known documented block, PLUS
    ID 3001 — a single orphan placeholder tile added in 447f523, isolated in
    the ID gap between 2250 and 5001 with no other files nearby. Confirmed by
    `git log --follow` (added 2026-04-16, not in the 2026-04-01 bulk import)
    and by visual inspection (soft gradient shading, not flat-color/hard-
    outline Oryx style).
  - items_16x16: ID >= 4001 (4 files: 4001, 4002, 4003, 4004) — added in the
    same commit (f953c23) as the known-generated world_24x24 5000+ block.
    Confirmed by visual inspection (anti-aliased shading on tool heads, not
    Oryx house style).
  - creatures_24x24: no contamination found — the ID range is fully dense
    (1-396, no gaps) and 100% of files trace to ae5969f.
This was verified three ways for both directories: git-commit provenance,
visual style inspection, and ID-gap isolation — all three agree exactly
(counts match to the file).
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

from PIL import Image

ID_RE = re.compile(r"_(\d+)\.png$")

# Orphan generated tile in world_24x24, isolated in the ID gap between the
# canonical range (ends 2250) and the documented 5000+ generated block. See
# module docstring for provenance.
WORLD_EXTRA_EXCLUDED_IDS = {3001}


def iter_id_filtered_pngs(directory, max_id, extra_excluded_ids=frozenset()):
    included, excluded = [], 0
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".png"):
            continue
        m = ID_RE.search(fname)
        if not m:
            continue
        tile_id = int(m.group(1))
        if tile_id < max_id and tile_id not in extra_excluded_ids:
            included.append(os.path.join(directory, fname))
        else:
            excluded += 1
    return included, excluded


def iter_all_pngs(directory):
    return [
        os.path.join(directory, fname)
        for fname in sorted(os.listdir(directory))
        if fname.endswith(".png")
    ]


def collect_opaque_colors(paths):
    colors = set()
    for path in paths:
        im = Image.open(path).convert("RGBA")
        for r, g, b, a in im.getdata():
            if a == 255:
                colors.add((r, g, b))
    return colors


def main():
    parser = argparse.ArgumentParser(description="Extract canonical Oryx master palette")
    parser.add_argument("--world-dir", default="src/Presentation/assets/sprites_16bf/world_24x24")
    parser.add_argument("--creatures-dir", default="src/Presentation/assets/sprites_16bf/creatures_24x24")
    parser.add_argument("--items-dir", default="src/Presentation/assets/sprites_16bf/items_16x16")
    parser.add_argument("--world-max-id", type=int, default=5000,
                         help="World tiles with numeric ID >= this are generated, not canonical Oryx")
    parser.add_argument("--items-max-id", type=int, default=4001,
                         help="Item tiles with numeric ID >= this are generated, not canonical Oryx")
    parser.add_argument("--abort-threshold", type=int, default=600,
                         help="Abort if palette exceeds this size (signals contamination)")
    parser.add_argument("--output", default="config/art/oryx_master_palette.json")
    args = parser.parse_args()

    world_paths, world_excluded = iter_id_filtered_pngs(
        args.world_dir, args.world_max_id, WORLD_EXTRA_EXCLUDED_IDS)
    creatures_paths = iter_all_pngs(args.creatures_dir)
    items_paths, items_excluded = iter_id_filtered_pngs(args.items_dir, args.items_max_id)

    sources = {}
    all_colors = set()
    for label, paths in [
        ("world_24x24", world_paths),
        ("creatures_24x24", creatures_paths),
        ("items_16x16", items_paths),
    ]:
        colors = collect_opaque_colors(paths)
        all_colors |= colors
        sources[label] = {"file_count": len(paths), "unique_colors": len(colors)}
        print(f"{label}: {len(paths)} files, {len(colors)} unique opaque colors "
              f"(running total {len(all_colors)})")

    print(f"world_24x24: excluded {world_excluded} files (id >= {args.world_max_id} or in "
          f"{sorted(WORLD_EXTRA_EXCLUDED_IDS)}, generated/non-canonical)")
    print(f"items_16x16: excluded {items_excluded} files with id >= {args.items_max_id} "
          f"(generated, non-canonical)")

    palette = sorted(all_colors)

    if len(palette) > args.abort_threshold:
        print(
            f"ABORT: master palette has {len(palette)} colors, exceeds threshold "
            f"{args.abort_threshold}. This indicates contamination (e.g. the world_24x24 "
            f"ID filter did not exclude generated tiles). Not writing output.",
            file=sys.stderr,
        )
        sys.exit(1)

    out = {
        "count": len(palette),
        "colors": [list(c) for c in palette],
        "sources": {
            "world_24x24": {
                "dir": args.world_dir,
                "file_count": sources["world_24x24"]["file_count"],
                "id_filter": f"< {args.world_max_id}, excluding {sorted(WORLD_EXTRA_EXCLUDED_IDS)}",
                "excluded_generated_files": world_excluded,
            },
            "creatures_24x24": {
                "dir": args.creatures_dir,
                "file_count": sources["creatures_24x24"]["file_count"],
            },
            "items_16x16": {
                "dir": args.items_dir,
                "file_count": sources["items_16x16"]["file_count"],
                "id_filter": f"< {args.items_max_id}",
                "excluded_generated_files": items_excluded,
            },
        },
        "extraction_date": datetime.now(timezone.utc).isoformat(),
    }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(out, f, indent=2)

    print(f"\nWrote {args.output}: {len(palette)} colors")


if __name__ == "__main__":
    main()
