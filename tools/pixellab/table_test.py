#!/usr/bin/env python3
"""8-variant consistency test + perspective/style sweep for table. No style_image."""

import os, sys, time
from pathlib import Path
from PIL import Image
import pixellab

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])
OUT = Path(__file__).parent / "table_results"
OUT.mkdir(exist_ok=True)

PROMPT = "wooden table, small sprite, pixel art"
SEEDS = [0, 1, 2, 3, 42, 137, 999, 1337]

BASE = dict(image_size={"width": 32, "height": 32}, no_background=True)

# Consistency: minimal params across 8 seeds
print("=== Consistency (minimal params) ===")
cons_dir = OUT / "consistency"
cons_dir.mkdir(exist_ok=True)
for seed in SEEDS:
    resp = client.generate_image_bitforge(description=PROMPT, seed=seed, **BASE)
    img = resp.image.pil_image()
    img.save(cons_dir / f"table_s{seed}_32px.png")
    img.resize((128, 128), Image.NEAREST).save(cons_dir / f"table_s{seed}_preview.png")
    print(f"  seed {seed} ✓")
    time.sleep(0.2)

# Perspective sweep (A group only — no style_image, no shading/detail/outline)
PERSP = [
    ("default",         {}),
    ("oblique_side",    dict(oblique_projection=True, view="side")),
    ("oblique_lowtop",  dict(oblique_projection=True, view="low top-down")),
    ("oblique_noview",  dict(oblique_projection=True)),
    ("iso",             dict(isometric=True)),
    ("side_only",       dict(view="side")),
]

print("\n=== Perspective sweep ===")
for name, kwargs in PERSP:
    d = OUT / "persp" / name
    d.mkdir(parents=True, exist_ok=True)
    for i, seed in enumerate([42, 137]):
        resp = client.generate_image_bitforge(description=PROMPT, seed=seed, **BASE, **kwargs)
        img = resp.image.pil_image()
        img.save(d / f"table_{i}_32px.png")
        img.resize((128, 128), Image.NEAREST).save(d / f"table_{i}_preview.png")
        print(f"  {name} [{i}] ✓")
        time.sleep(0.2)

print(f"\nDone. Results: {OUT}/")
