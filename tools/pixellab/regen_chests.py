#!/usr/bin/env python3
"""
Phase 1: Generate closed chest base designs for hero selection.
Phase 2 (regen_chests_variants.py): Use selected hero as init_image for open/empty/trapped.

Run from project root: source ~/.bashrc && .venv/bin/python3 tools/pixellab/regen_chests.py
"""

import os, time
from pathlib import Path
import pixellab

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])
OUT = Path("tools/pixellab/batch_new_sprites_results/chest/chest_closed")
OUT.mkdir(parents=True, exist_ok=True)

SEEDS = [0, 1, 2, 3, 42, 137, 999, 1337]
BASE = dict(
    image_size={"width": 32, "height": 32},
    no_background=True,
    coverage_percentage=85,
)

PROMPT = "large ornate treasure chest, iron bands and clasps, pixel art"

print(f"Prompt: {PROMPT}\n")
for seed in SEEDS:
    out = OUT / f"chest_closed_s{seed}_32px.png"
    if out.exists():
        print(f"  seed {seed} (cached)")
        continue
    resp = client.generate_image_bitforge(description=PROMPT, seed=seed, **BASE)
    img = resp.image.pil_image()
    img.save(out)
    print(f"  seed {seed} ✓")
    time.sleep(0.15)

print(f"\nDone — pick a hero seed, then run regen_chests_variants.py <seed>")
