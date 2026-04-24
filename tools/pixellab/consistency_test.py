#!/usr/bin/env python3
"""8 variants of minimal-params chair to check consistency."""

import os, sys, time
from pathlib import Path
from PIL import Image
import pixellab

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])
OUT = Path(__file__).parent / "consistency_results"
OUT.mkdir(exist_ok=True)

PROMPT = "wooden chair, small sprite, pixel art"
SEEDS = [0, 1, 2, 3, 42, 137, 999, 1337]

print(f"Generating {len(SEEDS)} variants...")
for seed in SEEDS:
    resp = client.generate_image_bitforge(
        description=PROMPT,
        image_size={"width": 32, "height": 32},
        no_background=True,
        seed=seed,
    )
    img = resp.image.pil_image()
    img.save(OUT / f"chair_s{seed}_32px.png")
    img.resize((128, 128), Image.NEAREST).save(OUT / f"chair_s{seed}_preview.png")
    print(f"  seed {seed} ✓")
    time.sleep(0.2)

print(f"\nDone. Results: {OUT}/")
