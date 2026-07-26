"""Regenerates the palette-lock evidence in this directory: swatch_input.png (a 10-color flat
swatch built from oryx_master_palette.json), chair_color_locked_output.png (BitForge output with
that swatch as color_image), and measurement.txt (the color-membership check).

Run from repo root: source ~/.bashrc && python3 tools/pixellab/palette_lock_evidence/regenerate_evidence.py
"""
import base64
import json
import os
import sys
from io import BytesIO

import requests
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "pixellab"))
import client_compat  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PALETTE_PATH = os.path.join(REPO_ROOT, "config", "art", "oryx_master_palette.json")

palette = [tuple(c) for c in json.load(open(PALETTE_PATH))["colors"]]
swatch_colors = palette[:10]
block = 8
swatch = Image.new("RGBA", (block * len(swatch_colors), block), (0, 0, 0, 255))
for i, c in enumerate(swatch_colors):
    for x in range(block):
        for y in range(block):
            swatch.putpixel((i * block + x, y), (*c, 255))
swatch.save(os.path.join(HERE, "swatch_input.png"))

client = client_compat._client()
request_data = {
    "description": "wooden chair, small sprite, pixel art",
    "image_size": {"width": 32, "height": 32},
    "no_background": True,
    "seed": 42,
    "color_image": {"type": "base64", "base64": base64.b64encode(
        (lambda buf: (swatch.save(buf, format="PNG"), buf.getvalue())[1])(BytesIO())
    ).decode()},
}
r = requests.post(f"{client.base_url}/generate-image-bitforge", headers=client.headers(), json=request_data)
r.raise_for_status()
img = client_compat._decode(r.json())
img.save(os.path.join(HERE, "chair_color_locked_output.png"))

used = sorted(set(img.convert("RGBA").getdata()))
unique_opaque = sorted(set((r_, g_, b_) for (r_, g_, b_, a_) in used if a_ == 255))
in_swatch = sum(1 for c in unique_opaque if c in swatch_colors)

report = (
    f"Prompt: \"wooden chair, small sprite, pixel art\", seed=42, no other structured params.\n"
    f"color_image: 10-color flat swatch (block image, no spatial structure), colors drawn from "
    f"config/art/oryx_master_palette.json[:10].\n\n"
    f"Swatch colors: {swatch_colors}\n\n"
    f"Unique opaque colors in output: {len(unique_opaque)}\n"
    f"Exact matches to swatch: {in_swatch}/{len(unique_opaque)}\n"
    f"Output colors: {unique_opaque}\n"
)
with open(os.path.join(HERE, "measurement.txt"), "w") as f:
    f.write(report)
print(report)
