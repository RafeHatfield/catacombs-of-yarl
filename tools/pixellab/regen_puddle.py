#!/usr/bin/env python3
"""Regenerate puddle with a better prompt — all 8 original seeds hallucinated creatures."""

import os, time
from pathlib import Path
from PIL import Image
import pixellab

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])
OUT = Path(__file__).parent / "batch_new_sprites_results" / "puddle"
OUT.mkdir(parents=True, exist_ok=True)

SEEDS = [0, 1, 2, 3, 42, 137, 999, 1337]
BASE = dict(image_size={"width": 32, "height": 32}, no_background=True)

PROMPTS = [
    "small dirty pond, overhead view, pixel art",
]

for pi, prompt in enumerate(PROMPTS):
    print(f"\nPrompt {pi}: {prompt}")
    for seed in SEEDS:
        out = OUT / f"puddle_p{pi+4}_s{seed}_32px.png"
        resp = client.generate_image_bitforge(description=prompt, seed=seed, **BASE)
        img = resp.image.pil_image()
        img.save(out)
        print(f"  p{pi} seed {seed} ✓")
        time.sleep(0.15)

print("\nDone — check batch_new_sprites_results/puddle/")
