"""
oblique_test_bed.py

Test cavalier/cabinet oblique projection for Oryx-style props.
Target: front face perfectly flat and square-on, top + right side
recede at 45 degrees to the right — technical drawing oblique style.

4 prompt strategies × 4 variants = 16 images ~$0.43

Usage:
  cd tools/retrodiffusion
  source ../../.venv/bin/activate
  python3 oblique_test_bed.py
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
STYLE = "rd_plus__low_res"
VARIANTS = 4
SIZE = 24
OUT_DIR = "oblique_test_bed"

PROMPTS = [
    {
        "label": "cavalier",
        "prompt": (
            "wooden bed with headboard and white pillow, dungeon furniture, "
            "cavalier oblique drawing, front face flat and square, "
            "top and right side angled at 45 degrees, "
            "small sprite on transparent background, pixel art, clear silhouette"
        ),
    },
    {
        "label": "tech_drawing",
        "prompt": (
            "wooden bed with headboard and white pillow, dungeon furniture, "
            "technical drawing oblique style, front face perfectly straight on, "
            "depth recedes diagonally to upper right at 45 degrees, "
            "small sprite on transparent background, pixel art, clear silhouette"
        ),
    },
    {
        "label": "geometric",
        "prompt": (
            "wooden bed with headboard and white pillow, dungeon furniture, "
            "front face is a flat rectangle viewed dead-on, "
            "top surface is a parallelogram going upper-right at 45 degrees, "
            "right side is a parallelogram going lower-right at 45 degrees, "
            "small sprite on transparent background, pixel art, clear silhouette"
        ),
    },
    {
        "label": "axonometric",
        "prompt": (
            "wooden bed with headboard and white pillow, dungeon furniture, "
            "axonometric oblique, front face faces viewer directly with no distortion, "
            "side and top shown receding diagonally, "
            "small sprite on transparent background, pixel art, clear silhouette"
        ),
    },
]


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


def run_prompt(entry, palette_b64):
    label = entry["label"]
    prompt = entry["prompt"]

    payload = {
        "prompt": prompt,
        "prompt_style": STYLE,
        "width": SIZE,
        "height": SIZE,
        "num_images": VARIANTS,
        "input_palette": palette_b64,
        "remove_bg": True,
    }

    print(f"\n--- [{label}] ---")
    print(f"  {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

    resp = requests.post(
        "https://api.retrodiffusion.ai/v1/inferences",
        headers={"X-RD-Token": API_KEY},
        json=payload,
    )
    data = resp.json()

    if "detail" in data:
        print(f"  ERROR: {data['detail']}")
        return

    print(f"  Cost: ${data.get('balance_cost','?')}  Remaining: ${data.get('remaining_balance','?')}")

    for i, b64 in enumerate(data.get("base64_images", [])):
        img = Image.open(BytesIO(base64.b64decode(b64))).convert("RGBA")
        img = remove_dark_background(img)
        fname = f"bed_{label}_{i}.png"
        img.save(os.path.join(OUT_DIR, fname))
        print(f"  Saved {fname}")


def main():
    if not os.path.exists(PALETTE_FILE):
        print(f"ERROR: {PALETTE_FILE} not found")
        sys.exit(1)

    with open(PALETTE_FILE, "rb") as f:
        palette_b64 = base64.b64encode(f.read()).decode()

    total = len(PROMPTS) * VARIANTS
    print(f"Oblique projection test: {len(PROMPTS)} prompts × {VARIANTS} variants = {total} images")
    print(f"Estimated cost: ~${total * 0.027:.2f}")
    print()
    for p in PROMPTS:
        print(f"  [{p['label']}] {p['prompt'][:80]}...")
    print()

    if input("Proceed? [y/N]: ").strip().lower() != "y":
        print("Aborted.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    for entry in PROMPTS:
        run_prompt(entry, palette_b64)

    print("\nDone.")


if __name__ == "__main__":
    main()
