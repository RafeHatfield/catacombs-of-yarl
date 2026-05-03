"""
img2img_test_bed.py

Test bed generation using an Oryx sprite as input_image conditioning
to guide the oblique/cabinet perspective. Generates 4 variants at
24x24 native (correct prop size).

Usage:
  cd tools/retrodiffusion
  python img2img_test_bed.py
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
# Oryx sprite 264 — oblique chest/crate, clear front face + top angle
REFERENCE_SPRITE = "../../src/Presentation/assets/sprites_16bf/world_24x24/oryx_16bit_fantasy_world_264.png"

STYLE = "rd_plus__low_res"
VARIANTS = 4
SIZE = 24  # native prop size — no downscaling needed

PROMPT = (
    "wooden bed with headboard and pillow, dungeon furniture prop, "
    "small sprite on transparent background, pixel art, clear silhouette"
)

# Strength values to test: lower = more content change, less perspective lock
# 0.6 = strong perspective guidance, 0.4 = moderate
STRENGTHS = [0.4, 0.6]


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


def run(palette_b64, ref_b64, strength, out_dir):
    payload = {
        "prompt": PROMPT,
        "prompt_style": STYLE,
        "width": SIZE,
        "height": SIZE,
        "num_images": VARIANTS,
        "input_palette": palette_b64,
        "input_image": ref_b64,
        "input_image_strength": strength,
        "remove_bg": True,
    }

    label = f"strength={strength}"
    print(f"\n--- {label} ---")
    resp = requests.post(
        "https://api.retrodiffusion.ai/v1/inferences",
        headers={"X-RD-Token": API_KEY},
        json=payload,
    )
    data = resp.json()

    if "detail" in data:
        print(f"  ERROR: {data['detail']}")
        print(f"  Full response: {data}")
        return

    cost = data.get("balance_cost", "?")
    remaining = data.get("remaining_balance", "?")
    print(f"  Cost: ${cost}  Remaining: ${remaining}")

    for i, b64 in enumerate(data.get("base64_images", [])):
        img = Image.open(BytesIO(base64.b64decode(b64))).convert("RGBA")
        img = remove_dark_background(img)
        fname = f"bed_img2img_s{int(strength*10):02d}_{i}.png"
        img.save(os.path.join(out_dir, fname))
        print(f"  Saved {fname}")


def main():
    if not os.path.exists(PALETTE_FILE):
        print(f"ERROR: {PALETTE_FILE} not found")
        sys.exit(1)

    if not os.path.exists(REFERENCE_SPRITE):
        print(f"ERROR: Reference sprite not found: {REFERENCE_SPRITE}")
        sys.exit(1)

    with open(PALETTE_FILE, "rb") as f:
        palette_b64 = base64.b64encode(f.read()).decode()

    # Encode the Oryx reference sprite
    ref_img = Image.open(REFERENCE_SPRITE).convert("RGBA")
    buf = BytesIO()
    ref_img.save(buf, format="PNG")
    ref_b64 = base64.b64encode(buf.getvalue()).decode()

    print(f"Reference sprite: {REFERENCE_SPRITE} ({ref_img.size[0]}x{ref_img.size[1]})")
    print(f"Generating: {len(STRENGTHS)} strength values x {VARIANTS} variants = {len(STRENGTHS)*VARIANTS} images")
    est = len(STRENGTHS) * VARIANTS * 0.027
    print(f"Estimated cost: ~${est:.2f}")
    if input("Proceed? [y/N]: ").strip().lower() != "y":
        print("Aborted.")
        return

    out_dir = "img2img_test_bed"
    os.makedirs(out_dir, exist_ok=True)

    for strength in STRENGTHS:
        run(palette_b64, ref_b64, strength, out_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
