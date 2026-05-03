"""
img2img_test_bed2.py

Second img2img bed test:
- Reference sprite 264 upscaled 4× (24→96px, nearest-neighbor) for clearer perspective signal
- Strength 0.3 for more content freedom
- More explicit bed prompt to fight chest content bleed

Usage:
  cd tools/retrodiffusion
  source ../../.venv/bin/activate
  python3 img2img_test_bed2.py
"""

import requests
import base64
import os
import sys
import numpy as np
from PIL import Image
from io import BytesIO

API_KEY = os.environ.get("RD_API_KEY")
if not API_KEY:
    print("ERROR: Set RD_API_KEY environment variable")
    sys.exit(1)

PALETTE_FILE = "oryx_palette.png"
REFERENCE_SPRITE = "../../src/Presentation/assets/sprites_16bf/world_24x24/oryx_16bit_fantasy_world_264.png"
REFERENCE_UPSCALE = 4  # nearest-neighbor upscale before passing to API

STYLE = "rd_plus__low_res"
VARIANTS = 4
SIZE = 24
STRENGTH = 0.3

PROMPT = (
    "wooden bed with tall headboard, rectangular mattress, white pillow, "
    "dungeon bedroom furniture, small sprite on transparent background, pixel art, clear silhouette"
)


def remove_dark_background(img, threshold=30):
    arr = np.array(img.convert("RGBA"))
    h, w = arr.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    is_bg = np.zeros((h, w), dtype=bool)
    stack = [(x, y) for x in range(w) for y in [0, h - 1]] + \
            [(x, y) for y in range(h) for x in [0, w - 1]]
    while stack:
        x, y = stack.pop()
        if x < 0 or x >= w or y < 0 or y >= h or visited[y, x]:
            continue
        visited[y, x] = True
        r, g, b, a = arr[y, x]
        if int(r) + int(g) + int(b) < threshold:
            is_bg[y, x] = True
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    arr[is_bg] = [0, 0, 0, 0]
    return Image.fromarray(arr)


def main():
    if not os.path.exists(PALETTE_FILE):
        print(f"ERROR: {PALETTE_FILE} not found")
        sys.exit(1)
    if not os.path.exists(REFERENCE_SPRITE):
        print(f"ERROR: Reference sprite not found: {REFERENCE_SPRITE}")
        sys.exit(1)

    with open(PALETTE_FILE, "rb") as f:
        palette_b64 = base64.b64encode(f.read()).decode()

    # Upscale reference sprite (nearest-neighbor — preserves pixel art structure)
    ref_img = Image.open(REFERENCE_SPRITE).convert("RGBA")
    upscaled_size = ref_img.size[0] * REFERENCE_UPSCALE
    ref_img = ref_img.resize((upscaled_size, upscaled_size), Image.NEAREST)
    buf = BytesIO()
    ref_img.save(buf, format="PNG")
    ref_b64 = base64.b64encode(buf.getvalue()).decode()

    print(f"Reference: {REFERENCE_SPRITE} → {upscaled_size}×{upscaled_size} (nearest-neighbor {REFERENCE_UPSCALE}×)")
    print(f"Strength: {STRENGTH}  Variants: {VARIANTS}  Output: {SIZE}×{SIZE}")
    print(f"Estimated cost: ~${VARIANTS * 0.027:.2f}")
    if input("Proceed? [y/N]: ").strip().lower() != "y":
        print("Aborted.")
        return

    payload = {
        "prompt": PROMPT,
        "prompt_style": STYLE,
        "width": SIZE,
        "height": SIZE,
        "num_images": VARIANTS,
        "input_palette": palette_b64,
        "input_image": ref_b64,
        "input_image_strength": STRENGTH,
        "remove_bg": True,
    }

    resp = requests.post(
        "https://api.retrodiffusion.ai/v1/inferences",
        headers={"X-RD-Token": API_KEY},
        json=payload,
    )
    data = resp.json()

    if "detail" in data:
        print(f"ERROR: {data['detail']}")
        print(f"Full response: {data}")
        return

    print(f"Cost: ${data.get('balance_cost', '?')}  Remaining: ${data.get('remaining_balance', '?')}")

    out_dir = "img2img_test_bed2"
    os.makedirs(out_dir, exist_ok=True)

    for i, b64 in enumerate(data.get("base64_images", [])):
        img = Image.open(BytesIO(base64.b64decode(b64))).convert("RGBA")
        img = remove_dark_background(img)
        fname = f"bed_s03_96ref_{i}.png"
        img.save(os.path.join(out_dir, fname))
        print(f"  Saved {fname}")

    print("\nDone.")


if __name__ == "__main__":
    main()
