# batch_generate.py
#
# Batch-generate pixel art sprites via Retro Diffusion API.
# Reads a list of sprites to generate, calls the API for each, cleans up the
# output (flood-fill background removal), and saves both the native size and
# a downscaled version to their target game size.
#
# Usage:
#   1. Set your API key:  export RD_API_KEY="your_key_here"
#   2. Edit SPRITES list below to define what you want to generate
#   3. python batch_generate.py
#
# Cost: ~$0.18 per 64x64 image. Budget accordingly.

import requests
import base64
import os
import sys
import time
import numpy as np
from PIL import Image
from io import BytesIO

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------

API_KEY = os.environ.get("RD_API_KEY")
if not API_KEY:
    print("ERROR: Set RD_API_KEY environment variable")
    sys.exit(1)

ORYX_STYLE = "user__oryx_16_bit_fantasy_style_d970121a"  # Your style ID
PALETTE_FILE = "oryx_palette.png"
OUTPUT_DIR = "generated"
VARIANTS_PER_SPRITE = 4  # Generate N variants, pick the best one by eye

# -----------------------------------------------------------------------------
# SPRITES TO GENERATE
# -----------------------------------------------------------------------------
# Each sprite defines:
#   name:        filename (no extension)
#   prompt:      what to generate — describe the object, not the art style
#   gen_size:    size to generate at (must be 64+ for RD Pro Fantasy)
#   final_size:  size to downscale to (16 for items, 24 for props)

SPRITES = [
    # ---- Weapons (16x16 items) ----
    {"name": "club_01",    "prompt": "simple wooden club weapon, thick end tapering to thin handle, dark wood with grain, RPG item",
     "gen_size": 64, "final_size": 16},
    {"name": "club_02",    "prompt": "heavy wooden cudgel, knotted thick end, short grip, medieval weapon",
     "gen_size": 64, "final_size": 16},
    {"name": "mace",       "prompt": "iron mace weapon, spiked metal ball on wooden handle, medieval",
     "gen_size": 64, "final_size": 16},
    {"name": "dagger",     "prompt": "short dagger, silver blade, brown leather-wrapped handle, sharp point",
     "gen_size": 64, "final_size": 16},
    {"name": "shortsword", "prompt": "short sword, steel blade, crossguard, leather grip, RPG weapon",
     "gen_size": 64, "final_size": 16},
    {"name": "staff",      "prompt": "wooden wizard staff, tall thin wood, small crystal or orb on top",
     "gen_size": 64, "final_size": 16},
    {"name": "bow",        "prompt": "wooden shortbow, curved wood limbs, taut bowstring",
     "gen_size": 64, "final_size": 16},
    {"name": "battleaxe",  "prompt": "battle axe, iron head with curved blade, wooden handle",
     "gen_size": 64, "final_size": 16},

    # ---- Props (24x24) — generate at 48+ for good detail ----
    # {"name": "anvil",      "prompt": "iron anvil on wooden stump, blacksmith workshop tool",
    #  "gen_size": 64, "final_size": 24},
    # {"name": "cauldron",   "prompt": "black iron cauldron, round with handles, on three legs",
    #  "gen_size": 64, "final_size": 24},
]

# -----------------------------------------------------------------------------
# BACKGROUND CLEANUP
# -----------------------------------------------------------------------------

def remove_dark_background(img, darkness_threshold=30):
    """Flood-fill from edges to remove dark background pixels.
    Keeps dark pixels inside the sprite (outlines, shadows) intact."""
    arr = np.array(img.convert("RGBA"))
    h, w = arr.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    is_bg = np.zeros((h, w), dtype=bool)

    stack = []
    for x in range(w):
        stack.append((x, 0))
        stack.append((x, h - 1))
    for y in range(h):
        stack.append((0, y))
        stack.append((w - 1, y))

    while stack:
        x, y = stack.pop()
        if x < 0 or x >= w or y < 0 or y >= h or visited[y, x]:
            continue
        visited[y, x] = True
        r, g, b, a = arr[y, x]
        if int(r) + int(g) + int(b) < darkness_threshold:
            is_bg[y, x] = True
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    arr[is_bg] = [0, 0, 0, 0]
    return Image.fromarray(arr)

# -----------------------------------------------------------------------------
# GENERATION
# -----------------------------------------------------------------------------

def generate_sprite(sprite_def, palette_b64):
    """Generate N variants of a single sprite, clean each one, save."""
    name = sprite_def["name"]
    prompt = sprite_def["prompt"]
    gen_size = sprite_def["gen_size"]
    final_size = sprite_def["final_size"]

    # Full prompt with transparency cues
    full_prompt = (
        f"{prompt}, small sprite on transparent background, "
        f"top-down RPG, pixel art, clear silhouette"
    )

    payload = {
        "prompt": full_prompt,
        "prompt_style": ORYX_STYLE,
        "width": gen_size,
        "height": gen_size,
        "num_images": VARIANTS_PER_SPRITE,
        "input_palette": palette_b64,
        "remove_bg": True,
    }

    print(f"\n[{name}] Generating {VARIANTS_PER_SPRITE} variants...")
    print(f"  Prompt: {prompt[:70]}{'...' if len(prompt) > 70 else ''}")

    response = requests.post(
        "https://api.retrodiffusion.ai/v1/inferences",
        headers={"X-RD-Token": API_KEY},
        json=payload,
    )
    data = response.json()

    if "detail" in data:
        print(f"  ERROR: {data['detail']}")
        return False

    cost = data.get("balance_cost", "?")
    remaining = data.get("remaining_balance", "?")
    print(f"  Cost: ${cost}  Remaining: ${remaining}")

    # Process each variant
    native_dir = os.path.join(OUTPUT_DIR, f"{gen_size}x{gen_size}")
    final_dir = os.path.join(OUTPUT_DIR, f"{final_size}x{final_size}")
    os.makedirs(native_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    for i, img_b64 in enumerate(data.get("base64_images", [])):
        img = Image.open(BytesIO(base64.b64decode(img_b64))).convert("RGBA")
        img_clean = remove_dark_background(img)

        native_path = os.path.join(native_dir, f"{name}_{i}.png")
        final_path = os.path.join(final_dir, f"{name}_{i}.png")

        img_clean.save(native_path)
        img_clean.resize((final_size, final_size), Image.NEAREST).save(final_path)

    print(f"  Saved {VARIANTS_PER_SPRITE} variants to {native_dir}/ and {final_dir}/")
    return True

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main():
    # Load palette once
    if not os.path.exists(PALETTE_FILE):
        print(f"ERROR: {PALETTE_FILE} not found. Run extract_palette.py first.")
        sys.exit(1)

    with open(PALETTE_FILE, "rb") as f:
        palette_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Cost preview
    total_images = len(SPRITES) * VARIANTS_PER_SPRITE
    est_cost = total_images * 0.18
    print(f"About to generate {len(SPRITES)} sprites x {VARIANTS_PER_SPRITE} variants = {total_images} images")
    print(f"Estimated cost: ${est_cost:.2f}")
    response = input("Proceed? [y/N]: ").strip().lower()
    if response != "y":
        print("Aborted.")
        return

    # Generate
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start = time.time()
    successes = 0
    for sprite_def in SPRITES:
        if generate_sprite(sprite_def, palette_b64):
            successes += 1
        time.sleep(1)  # Be nice to the API

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"Done! {successes}/{len(SPRITES)} sprites generated in {elapsed:.1f}s")
    print(f"Review variants in {OUTPUT_DIR}/ and pick your favorites.")

if __name__ == "__main__":
    main()