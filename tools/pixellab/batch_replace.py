#!/usr/bin/env python3
"""
Batch replacement generation for RD-era sprites.
Generates 8 seeds per object, saves previews for selection.
"""

import os, time
from pathlib import Path
from PIL import Image
import pixellab

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])
OUT = Path(__file__).parent / "batch_replace_results"
OUT.mkdir(exist_ok=True)

SEEDS = [0, 1, 2, 3, 42, 137, 999, 1337]
BASE = dict(image_size={"width": 32, "height": 32}, no_background=True)

OBJECTS = [
    ("bed",   "wooden bed with headboard, small sprite, pixel art"),
    ("bench", "wooden bench, small sprite, pixel art"),
    ("desk",  "wooden writing desk, small sprite, pixel art"),
    ("cage",  "iron cage with bars, small sprite, pixel art"),
]

total = len(OBJECTS) * len(SEEDS)
print(f"Generating {len(OBJECTS)} objects × {len(SEEDS)} seeds = {total} images\n")

for obj_name, prompt in OBJECTS:
    obj_dir = OUT / obj_name
    obj_dir.mkdir(exist_ok=True)
    print(f"[{obj_name}] {prompt}")
    for seed in SEEDS:
        resp = client.generate_image_bitforge(description=prompt, seed=seed, **BASE)
        img = resp.image.pil_image()
        img.save(obj_dir / f"{obj_name}_s{seed}_32px.png")
        img.resize((24, 24), Image.NEAREST).resize((144, 144), Image.NEAREST).save(
            obj_dir / f"{obj_name}_s{seed}_preview.png"
        )
        print(f"  seed {seed} ✓")
        time.sleep(0.2)
    print()

print(f"Done. Results: {OUT}/")
