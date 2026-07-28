#!/usr/bin/env python3
"""Burn-down 3 candidate generation harness — palette-locked variant.

Same pipeline as generate_candidates.py (burn-down 2b) but passes a themed
color_image swatch built from the CONCEPT'S OWN CURRENT LIVE SPRITE colors,
snapped to the nearest master-palette entries — i.e. "make something whose
colors resemble the existing design, but exactly on-palette," directly in
the spirit of the Option 3 conformance ruling (conform to canon, don't
replace the design). This is not the same swatch for every concept; each
concept gets its own, derived from its own live art.

See tools/pixellab/PIXELLAB_CONVENTIONS.md's color_image section and
tools/pixellab/palette_lock_evidence/ for why this parameter (fed a flat
swatch, not a detailed composite) is a genuine forced-palette lock and not
the spatial-color-transfer footgun the April sweep.py test found.
"""
import os
import sys
import time
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
sys.path.insert(0, os.path.join(REPO, "tools/art_lint"))
os.chdir(REPO)

import warnings
warnings.filterwarnings("ignore")

from PIL import Image
from client_compat import generate_image_bitforge
from generate_candidates import pipeline_one, snap_mod, lint_mod, palette, GEN_SIZE

FLOOR_BY_CLASS = {"world_tile": 8, "prop": 8, "decal": 8, "fx": 8, "item": 12, "creature": 16, "class": 16}


def build_swatch_from_live(live_path, asset_class, block=8):
    """Take the live sprite's own opaque colors, snap each to the nearest
    master-palette color, and build a flat swatch of the most common
    resulting colors (capped at the class's WARN-band size, for headroom)."""
    im = Image.open(live_path).convert("RGBA")
    pixels = [(r, g, b) for (r, g, b, a) in im.getdata() if a == 255]
    counts = Counter(pixels)

    snapped_counts = Counter()
    cache = {}
    for color, n in counts.items():
        if color not in cache:
            cache[color] = snap_mod.nearest_palette_color(color, palette)[0]
        snapped_counts[cache[color]] += n

    budget = FLOOR_BY_CLASS.get(asset_class, 8)
    top_colors = [c for c, _ in snapped_counts.most_common(budget)]

    swatch = Image.new("RGBA", (block * len(top_colors), block), (0, 0, 0, 255))
    for i, c in enumerate(top_colors):
        for x in range(block):
            for y in range(block):
                swatch.putpixel((i * block + x, y), (*c, 255))
    return swatch, top_colors


def generate_concept_locked(concept_name, prompt, file_ids, asset_class, final_size,
                             exempt, live_path, target=6, max_attempts=20, seed_start=0):
    out_dir = f"tools/art_lint/candidates/burndown3/{concept_name}"
    os.makedirs(out_dir, exist_ok=True)

    swatch, swatch_colors = build_swatch_from_live(live_path, asset_class)
    swatch.save(os.path.join(out_dir, "_color_swatch.png"))
    with open(os.path.join(out_dir, "_swatch_colors.txt"), "w") as f:
        f.write(f"Swatch colors (from live sprite, snapped to master palette): {swatch_colors}\n")

    results = []
    passers = []
    attempt = 0
    seed = seed_start
    while attempt < max_attempts and len(passers) < target:
        attempt += 1
        tag = f"{concept_name}_locked_s{seed}"
        try:
            raw = generate_image_bitforge(prompt + ", small sprite, pixel art", GEN_SIZE,
                                           seed=seed, color_image=swatch)
        except Exception as e:
            results.append({"tag": tag, "status": "error", "reason": str(e), "seed": seed, "prompt": prompt})
            seed += 1
            time.sleep(0.3)
            continue
        r = pipeline_one(raw, final_size, asset_class, exempt, out_dir, tag)
        r["seed"] = seed
        r["prompt"] = prompt
        results.append(r)
        if r["status"] == "ok" and r["overall"] in ("PASS", "WARN"):
            passers.append(r)
        seed += 1
        time.sleep(0.2)

    return {
        "concept": concept_name, "file_ids": file_ids, "attempts": attempt,
        "passers": len(passers), "results": results,
    }


if __name__ == "__main__":
    print("Import this module from a driver script; not meant to run standalone.")
