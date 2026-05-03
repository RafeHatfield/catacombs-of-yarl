#!/usr/bin/env python3
"""
Batch PixelLab generation for all NEW_SPRITES placeholder replacements.
22 objects × 8 seeds = 176 images.

Run: python3 batch_new_sprites.py
Results: batch_new_sprites_results/<object>/<object>_s<seed>_32px.png
         batch_new_sprites_results/<object>/<object>_s<seed>_preview.png
"""

import os, time
from pathlib import Path
from PIL import Image
import pixellab

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])
OUT = Path(__file__).parent / "batch_new_sprites_results"
OUT.mkdir(exist_ok=True)

SEEDS = [0, 1, 2, 3, 42, 137, 999, 1337]
BASE = dict(image_size={"width": 32, "height": 32}, no_background=True)

OBJECTS = [
    ("mushroom_cluster", "cluster of glowing mushrooms, small sprite, pixel art"),
    ("nightstand",       "wooden nightstand with drawer, small sprite, pixel art"),
    ("pipe_horiz",       "horizontal metal pipe section, small sprite, pixel art"),
    ("pipe_vert",        "vertical metal pipe section, small sprite, pixel art"),
    ("puddle",           "small muddy puddle on stone floor, small sprite, pixel art"),
    ("rock",             "stone rock or small boulder, small sprite, pixel art"),
    ("sack",             "tied burlap sack, small sprite, pixel art"),
    ("bottle_shelf",     "wooden shelf holding bottles and flasks, small sprite, pixel art"),
    ("shelf",            "wooden wall shelf, small sprite, pixel art"),
    ("pillar",           "stone pillar column, small sprite, pixel art"),
    ("straw",            "scattered pile of straw, small sprite, pixel art"),
    ("tool_rack",        "wooden rack holding tools and weapons, small sprite, pixel art"),
    ("training_dummy",   "stuffed training dummy on wooden post, small sprite, pixel art"),
    ("vine",             "hanging green vine plant, small sprite, pixel art"),
    ("water_barrel",     "wooden barrel with water, small sprite, pixel art"),
    ("workbench",        "wooden workbench with tools, small sprite, pixel art"),
    ("candelabra",       "tall iron candelabra with lit candles, small sprite, pixel art"),
    ("rubble",           "pile of broken stone rubble, small sprite, pixel art"),
    ("signpost",         "wooden signpost with directional sign, small sprite, pixel art"),
    ("mural_gold_land",  "ornate framed golden landscape painting, small sprite, pixel art"),
    ("mural_gold_warm",  "ornate framed warm golden painting, small sprite, pixel art"),
    ("mural_wood_cool",  "ornate framed cool-toned wooden panel painting, small sprite, pixel art"),
    # glowing_mushroom replaces deleted RD sprites 5013/5042-5044
    ("glowing_mushroom", "single glowing bioluminescent mushroom, small sprite, pixel art"),
]

total = len(OBJECTS) * len(SEEDS)
print(f"Generating {len(OBJECTS)} objects × {len(SEEDS)} seeds = {total} images\n")

for i, (obj_name, prompt) in enumerate(OBJECTS, 1):
    obj_dir = OUT / obj_name
    obj_dir.mkdir(exist_ok=True)
    print(f"[{i:2}/{len(OBJECTS)}] {obj_name}: {prompt}")
    for seed in SEEDS:
        out_32 = obj_dir / f"{obj_name}_s{seed}_32px.png"
        if out_32.exists():
            print(f"  seed {seed} (cached)")
            continue
        resp = client.generate_image_bitforge(description=prompt, seed=seed, **BASE)
        img = resp.image.pil_image()
        img.save(out_32)
        print(f"  seed {seed} ✓")
        time.sleep(0.15)
    print()

print(f"Done. Results in: {OUT}/")
print("\nNext: open preview images, pick seeds, update props.yaml and sprite browser.")
