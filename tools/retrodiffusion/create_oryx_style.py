# create_oryx_style.py

import requests
import base64
import os
from PIL import Image

API_KEY = os.environ.get("RD_API_KEY", "YOUR_API_KEY_HERE")

SPRITES = "src/Presentation/assets/sprites_16bf"
CELL = 24  # grid cell size — all sprites normalised to 24×24

sprite_paths = [
    (f"{SPRITES}/creatures_24x24/oryx_16bit_fantasy_creatures_01.png", "humanoid"),
    (f"{SPRITES}/creatures_24x24/oryx_16bit_fantasy_creatures_02.png", "orc"),
    (f"{SPRITES}/items_16x16/oryx_16bit_fantasy_items_199.png",        "shortsword"),
    (f"{SPRITES}/items_16x16/oryx_16bit_fantasy_items_202.png",        "dagger"),
    (f"{SPRITES}/world_24x24/oryx_16bit_fantasy_world_268.png",        "barrel"),
    (f"{SPRITES}/world_24x24/oryx_16bit_fantasy_world_261.png",        "chest"),
    (f"{SPRITES}/world_24x24/oryx_16bit_fantasy_world_327.png",        "table"),
    (f"{SPRITES}/world_24x24/oryx_16bit_fantasy_world_774.png",        "floor"),
    (f"{SPRITES}/world_24x24/oryx_16bit_fantasy_world_182.png",        "wall"),
]

# Build a 3×3 grid (72×72px). Sprites smaller than CELL are centred; larger are not expected.
cols, rows = 3, 3
grid = Image.new("RGBA", (cols * CELL, rows * CELL), (0, 0, 0, 0))

for i, (path, label) in enumerate(sprite_paths):
    sprite = Image.open(path).convert("RGBA")
    x_off = ((CELL - sprite.width)  // 2)
    y_off = ((CELL - sprite.height) // 2)
    col, row = i % cols, i // cols
    grid.paste(sprite, (col * CELL + x_off, row * CELL + y_off), sprite)
    print(f"  [{row},{col}] {label} ({sprite.width}×{sprite.height})")

grid.save("oryx_style_reference.png")
print("Saved oryx_style_reference.png")

# Encode the composite grid as base64
with open("oryx_style_reference.png", "rb") as f:
    ref_b64 = base64.b64encode(f.read()).decode("utf-8")

url = "https://api.retrodiffusion.ai/v1/styles"
headers = {"X-RD-Token": API_KEY}

payload = {
    "name": "Oryx 16-Bit Fantasy Style",
    "description": "SNES-era 16-bit pixel art, dark outlines, limited palette, "
                   "top-down RPG perspective, clean readable silhouettes at small sizes",
    "reference_images": [ref_b64],
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

print(f"Full response: {data}")
style_id = data.get("prompt_style") or data.get("style_id") or data.get("id")
if style_id:
    print(f"\nStyle ID: {style_id}")
    print("Save this — use it in every generation call")
else:
    print("No style ID in response — check full response above")
