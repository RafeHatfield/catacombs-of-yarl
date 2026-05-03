"""
style_test_prop.py

Compare rd_plus style variants for a single prop at 48x48 → 24x24.
Usage:
  python style_test_prop.py

Output: style_test_{name}/ with {name}_{style}_48x48_{i}.png and 24x24 versions.
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

STYLES = [
    "rd_plus__low_res",
    "rd_plus__classic",
    "rd_plus__topdown_item",
]
VARIANTS = 4
GEN_SIZE = 48
FINAL_SIZE = 24
PALETTE_FILE = "oryx_palette.png"

# ---- Edit these per test ----
SPRITE_NAME = "anvil"
PROMPT = (
    "iron anvil on a small wooden base, blacksmith tool, "
    "heavy dark metal body with wide flat top and pointed horn, "
    "dungeon prop, RPG pixel art"
)
# -----------------------------


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


def run_style(style, palette_b64, out_dir):
    full_prompt = (
        f"{PROMPT}, small sprite on transparent background, pixel art, clear silhouette"
    )
    payload = {
        "prompt": full_prompt,
        "prompt_style": style,
        "width": GEN_SIZE,
        "height": GEN_SIZE,
        "num_images": VARIANTS,
        "input_palette": palette_b64,
        "remove_bg": True,
    }

    print(f"\n--- {style} ---")
    resp = requests.post(
        "https://api.retrodiffusion.ai/v1/inferences",
        headers={"X-RD-Token": API_KEY},
        json=payload,
    )
    data = resp.json()
    if "detail" in data:
        print(f"  ERROR: {data['detail']}")
        return

    cost = data.get("balance_cost", "?")
    remaining = data.get("remaining_balance", "?")
    print(f"  Cost: ${cost}  Remaining: ${remaining}")

    style_short = style.replace("rd_plus__", "")
    for i, b64 in enumerate(data.get("base64_images", [])):
        img = Image.open(BytesIO(base64.b64decode(b64))).convert("RGBA")
        img = remove_dark_background(img)

        native_name = f"{SPRITE_NAME}_{style_short}_{GEN_SIZE}x{GEN_SIZE}_{i}.png"
        small_name  = f"{SPRITE_NAME}_{style_short}_{FINAL_SIZE}x{FINAL_SIZE}_{i}.png"

        img.save(os.path.join(out_dir, native_name))
        img.resize((FINAL_SIZE, FINAL_SIZE), Image.NEAREST).save(os.path.join(out_dir, small_name))
        print(f"  Saved {native_name} + {FINAL_SIZE}x{FINAL_SIZE}")


def main():
    if not os.path.exists(PALETTE_FILE):
        print(f"ERROR: {PALETTE_FILE} not found — run extract_palette.py first")
        sys.exit(1)

    with open(PALETTE_FILE, "rb") as f:
        palette_b64 = base64.b64encode(f.read()).decode()

    total = len(STYLES) * VARIANTS
    est = total * 0.027
    print(f"Sprite: {SPRITE_NAME}")
    print(f"Styles: {len(STYLES)}  Variants: {VARIANTS}  Images: {total}")
    print(f"Estimated cost: ~${est:.2f}")
    if input("Proceed? [y/N]: ").strip().lower() != "y":
        print("Aborted.")
        return

    out_dir = f"style_test_{SPRITE_NAME}"
    os.makedirs(out_dir, exist_ok=True)

    for style in STYLES:
        run_style(style, palette_b64, out_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
