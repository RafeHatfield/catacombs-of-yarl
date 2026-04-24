# PixelLab API walkthrough (API-only, no MCP)

A guide to setting up PixelLab for YARL using the official Python SDK, driven via scripts that Claude Code writes and runs. Same execution model as your current Retro Diffusion workflow — no MCP server required.

Specifically targeted at Oryx 16-Bit Fantasy style matching, with 24×24 props and 16×16 items.

## Why the Python SDK (and not raw REST)

PixelLab maintains an official Python package (`pixellab` on PyPI) that wraps their API with proper types, automatic base64 encoding, and clean error handling. Using it instead of hitting REST directly gives you:

- Image objects that serialize cleanly between API and PIL
- Proper typed parameters so you get IDE autocomplete
- Automatic handling of reference image encoding for BitForge
- Built-in balance checking

You'll still be writing and running Python scripts — exactly like your Retro Diffusion workflow — just with a nicer client library instead of manual `requests.post()` calls.

## PixelLab's two generation models

Understanding these matters because you'll pick between them for each sprite:

### BitForge (use this for Oryx-style work)

- **Purpose**: Style-matched generation using a reference image
- **Best for**: Small-to-medium sprites (16×16 to 128×128)
- **How it works**: You pass a reference PNG (e.g., an Oryx composite) + a description; BitForge generates a new sprite that matches that reference's style
- **Key parameter**: `style_strength` (0–100) — how closely to match the reference. Higher = stickier to reference style.

### PixFlux

- **Purpose**: Text-to-pixel-art from description alone
- **Best for**: Medium-to-large sprites (64×64 to 256×256)
- **When to use**: Larger scenery/environment generation, or when you don't have a reference

For YARL, **BitForge is your primary tool** because style-matching Oryx is the whole point.

## Size constraints and your strategy

PixelLab generates natively at common sizes: 32×32, 64×64, 128×128, with some flexibility for arbitrary dimensions. **There is no native 24×24.** This matters because your props are 24×24.

Three approaches:

**Approach A: Generate at 32×32, downscale to 24×24.** Clean but not ideal — 32→24 isn't an integer ratio, so nearest-neighbor produces uneven pixel blocks. Results in slightly noisy sprites.

**Approach B: Generate at 48×48, downscale 48→24 (2:1 clean).** PixelLab accepts arbitrary widths/heights, but quality drops outside the recommended sizes. Worth testing for your specific use case.

**Approach C (recommended): Generate at 64×64, center-crop to 24×24.** Higher detail per pixel, and you keep control over what portion of the sprite ends up in the final tile. For most props, the main subject only occupies the center anyway, so the crop is easy.

For items (16×16), you're fine — generate natively at 32×32 and do a clean 2:1 downscale.

## Setup walkthrough

### Step 1: Get a PixelLab API key

- Sign up at pixellab.ai
- Go to account settings → API keys → generate a new key
- Copy it somewhere safe

### Step 2: Install the Python SDK

In your project directory (with your venv activated):

```bash
pip install pixellab
```

### Step 3: Store the API key

Add it to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export PIXELLAB_API_KEY="your_key_here"
```

Then `source ~/.zshrc` or restart your terminal. This keeps the key out of any scripts you commit to git, and Claude Code inherits your shell environment automatically.

### Step 4: Verify the connection

Create a test script `test_pixellab.py`:

```python
import os
import pixellab

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])
balance = client.get_balance()
print(f"Balance: {balance.balance} {balance.currency}")
```

Run it. If you see a balance, the SDK is working.

### Step 5: Prepare your Oryx reference image

You already have `oryx_style_reference.png` from your Retro Diffusion setup — the 3×3 composite of representative Oryx tiles. Copy it to your project root or reference it from the existing path. PixelLab's SDK will handle base64 encoding automatically.

### Step 6: Single-sprite generation script

Create `generate_sprite_pixellab.py`:

```python
# generate_sprite_pixellab.py
# Generate a single sprite using PixelLab BitForge with Oryx reference style

import os
import pixellab
from pixellab import Base64Image
from PIL import Image

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])

# Load the Oryx style reference
style_image = Base64Image.from_file("oryx_style_reference.png")

# Generate 4 variants of a club
for i in range(4):
    response = client.generate_image_bitforge(
        description=(
            "simple wooden club weapon, thick end tapering to thin handle, "
            "dark wood with grain detail, small sprite, top-down RPG item icon"
        ),
        image_size={"width": 32, "height": 32},  # Native 32, downscale to 16
        style_image=style_image,
        style_strength=70.0,   # High — we want strong Oryx matching
        no_background=True,    # Transparent background
    )
    
    # Save the native 32x32
    img_32 = response.image.pil_image()
    img_32.save(f"club_32x32_{i}.png")
    
    # Downscale to 16x16 with nearest-neighbor
    img_16 = img_32.resize((16, 16), Image.NEAREST)
    img_16.save(f"club_16x16_{i}.png")
    
    print(f"Saved club variant {i}")

# Check remaining balance
balance = client.get_balance()
print(f"\nRemaining balance: {balance.balance} {balance.currency}")
```

Run this as your first real test. If you get 4 clubs with transparent backgrounds, you're set.

## Background cleanup

PixelLab's `no_background=True` flag should produce proper alpha transparency, which is a nice improvement over Retro Diffusion's `remove_bg` (which gave you near-black pixels). But edge cases happen — if you see unwanted dark pixels at edges, reuse the same flood-fill cleanup from your RD pipeline:

```python
import numpy as np

def remove_dark_background(img, threshold=30):
    """Flood-fill from edges to remove dark background pixels."""
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
        if a > 0 and int(r) + int(g) + int(b) < threshold:
            is_bg[y, x] = True
            stack.extend([(x+1,y), (x-1,y), (x,y+1), (x,y-1)])

    arr[is_bg] = [0, 0, 0, 0]
    return Image.fromarray(arr)
```

## Cropping 64×64 → 24×24 for props

For props (24×24 target), generate at 64×64 and crop. The trick is finding the "center of mass" of the sprite so the crop captures the important part, not just the geometric center.

```python
import numpy as np
from PIL import Image

def smart_crop_to_24(img_64):
    """Crop a 64x64 sprite to a 24x24 centered on the sprite's content."""
    arr = np.array(img_64.convert("RGBA"))
    
    # Find bounding box of non-transparent pixels
    alpha = arr[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)
    
    if not rows.any() or not cols.any():
        # Empty image, just center crop
        return img_64.crop((20, 20, 44, 44))
    
    # Bounding box
    r_min, r_max = np.where(rows)[0][[0, -1]]
    c_min, c_max = np.where(cols)[0][[0, -1]]
    
    # Center of the content
    cx = (c_min + c_max) // 2
    cy = (r_min + r_max) // 2
    
    # 24x24 crop centered on content
    left = max(0, min(40, cx - 12))
    top = max(0, min(40, cy - 12))
    
    return img_64.crop((left, top, left + 24, top + 24))
```

Use this in your generation loop for any 24×24 target sprites.

## Batch generation script

A production-ready batch script, same pattern as your Retro Diffusion `batch_generate.py`:

```python
# batch_generate_pixellab.py

import os
import sys
import time
import pixellab
from pixellab import Base64Image
from PIL import Image
import numpy as np

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("PIXELLAB_API_KEY")
if not API_KEY:
    print("ERROR: Set PIXELLAB_API_KEY environment variable")
    sys.exit(1)

STYLE_REF_FILE = "oryx_style_reference.png"
STYLE_STRENGTH = 70.0
OUTPUT_DIR = "generated_pixellab"
VARIANTS_PER_SPRITE = 4

client = pixellab.Client(secret=API_KEY)
style_image = Base64Image.from_file(STYLE_REF_FILE)

# ---------------------------------------------------------------------------
# SPRITES TO GENERATE
# ---------------------------------------------------------------------------

SPRITES = [
    # Items (16x16 final): generate at 32, downscale to 16
    {"name": "club_01", "prompt": "simple wooden club weapon, thick end tapering to handle, dark wood",
     "gen_size": 32, "final_size": 16, "crop": False},
    {"name": "dagger", "prompt": "short dagger, silver blade, brown leather handle",
     "gen_size": 32, "final_size": 16, "crop": False},

    # Props (24x24 final): generate at 64, crop to 24
    # {"name": "anvil", "prompt": "iron anvil on wooden stump, blacksmith tool, top-down view",
    #  "gen_size": 64, "final_size": 24, "crop": True},
]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def remove_dark_background(img, threshold=30):
    """Flood-fill from edges to remove dark background pixels."""
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
        if a > 0 and int(r) + int(g) + int(b) < threshold:
            is_bg[y, x] = True
            stack.extend([(x+1,y), (x-1,y), (x,y+1), (x,y-1)])

    arr[is_bg] = [0, 0, 0, 0]
    return Image.fromarray(arr)


def smart_crop_to_24(img_64):
    """Crop a 64x64 sprite to a 24x24 centered on the sprite's content."""
    arr = np.array(img_64.convert("RGBA"))
    alpha = arr[:, :, 3]
    rows = np.any(alpha > 0, axis=1)
    cols = np.any(alpha > 0, axis=0)

    if not rows.any() or not cols.any():
        return img_64.crop((20, 20, 44, 44))

    r_min, r_max = np.where(rows)[0][[0, -1]]
    c_min, c_max = np.where(cols)[0][[0, -1]]

    cx = (c_min + c_max) // 2
    cy = (r_min + r_max) // 2

    left = max(0, min(40, cx - 12))
    top = max(0, min(40, cy - 12))

    return img_64.crop((left, top, left + 24, top + 24))

# ---------------------------------------------------------------------------
# GENERATION
# ---------------------------------------------------------------------------

def generate_sprite(sprite_def):
    name = sprite_def["name"]
    prompt = sprite_def["prompt"]
    gen_size = sprite_def["gen_size"]
    final_size = sprite_def["final_size"]
    needs_crop = sprite_def["crop"]

    full_prompt = f"{prompt}, small sprite, top-down RPG, pixel art, clear silhouette"

    print(f"\n[{name}] Generating {VARIANTS_PER_SPRITE} variants...")

    native_dir = os.path.join(OUTPUT_DIR, f"{gen_size}x{gen_size}")
    final_dir = os.path.join(OUTPUT_DIR, f"{final_size}x{final_size}")
    os.makedirs(native_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    for i in range(VARIANTS_PER_SPRITE):
        try:
            response = client.generate_image_bitforge(
                description=full_prompt,
                image_size={"width": gen_size, "height": gen_size},
                style_image=style_image,
                style_strength=STYLE_STRENGTH,
                no_background=True,
            )

            img = response.image.pil_image()
            img = remove_dark_background(img)  # Safety net
            img.save(os.path.join(native_dir, f"{name}_{i}.png"))

            # Generate final-size version
            if needs_crop and gen_size == 64 and final_size == 24:
                final = smart_crop_to_24(img)
            else:
                final = img.resize((final_size, final_size), Image.NEAREST)

            final.save(os.path.join(final_dir, f"{name}_{i}.png"))
            print(f"  Variant {i} saved")

        except Exception as e:
            print(f"  ERROR on variant {i}: {e}")
            return False

    return True

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    balance = client.get_balance()
    print(f"Starting balance: {balance.balance} {balance.currency}")

    total = len(SPRITES) * VARIANTS_PER_SPRITE
    print(f"About to generate {len(SPRITES)} sprites x {VARIANTS_PER_SPRITE} variants = {total} images")
    response = input("Proceed? [y/N]: ").strip().lower()
    if response != "y":
        print("Aborted.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start = time.time()
    successes = 0
    for sprite_def in SPRITES:
        if generate_sprite(sprite_def):
            successes += 1
        time.sleep(1)

    balance_end = client.get_balance()
    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"Done! {successes}/{len(SPRITES)} sprites generated in {elapsed:.1f}s")
    print(f"Final balance: {balance_end.balance} {balance_end.currency}")
    print(f"Review variants in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
```

## Claude Code conventions file

Create `PIXELLAB_CONVENTIONS.md` in your project root so Claude Code follows consistent patterns:

```markdown
# PixelLab Conventions for YARL

## API setup
- API key in $PIXELLAB_API_KEY environment variable
- Python SDK: `pixellab` package (pip install pixellab)
- Style reference: oryx_style_reference.png (3x3 grid of Oryx tiles)
- Default style_strength: 70.0 (high Oryx matching)

## Default model
Use generate_image_bitforge for all Oryx-style asset generation.
Use generate_image_pixflux only when explicitly told, or for large non-sprite content.

## Sprite sizes
- Items (16x16): Generate at 32x32, nearest-neighbor downscale
- Props (24x24): Generate at 64x64, smart-crop to 24x24
- Characters (24x24): Generate at 64x64, smart-crop to 24x24

## Pipeline per sprite
1. Call generate_image_bitforge with description, style_image, style_strength=70, no_background=true
2. Save native-size to generated_pixellab/{NxN}/
3. For items: nearest-neighbor downscale to final size
4. For props: smart_crop_to_24 (crop centered on content bounding box)
5. Apply flood-fill background cleanup as safety net

## Budget rules
- Default to 4 variants per sprite for selection
- Always check balance before batches > 10 images
- Warn before any batch that would cost > $3
```

## Improving existing Oryx assets with inpainting

PixelLab has a dedicated inpainting method. You can take an existing Oryx tile, mask a region, and regenerate just that masked area.

```python
# inpaint_oryx.py

from pixellab import Base64Image

original = Base64Image.from_file("oryx_tile_table.png")
mask = Base64Image.from_file("mask.png")  # White = regenerate, Black = keep

response = client.inpaint(
    description="add wine stains and candlewax to the table surface",
    image_size={"width": 24, "height": 24},
    init_image=original,
    mask_image=mask,
    inpainting_image=original,
)

response.image.pil_image().save("table_with_stains.png")
```

This is powerful for:

- Adding variants to existing Oryx props (10 different barrels from one base)
- Adding wear/damage to pristine items
- Mixing in details from other tilesets
- Recoloring specific regions

## Environmental tiles (floors, walls, seamless textures)

PixelLab has specific tools for this that Retro Diffusion doesn't:

- **`create_texture`** — generates tileable textures
- **`create_tileset`** — generates full tilesets with matching variants
- **`create_map`** — generates pixflux-based map content

These are worth exploring specifically for your dungeon floor/wall variants. The docs are at pixellab.ai/docs.

## Cost tracking

PixelLab uses subscription-based tiers. When you call `client.get_balance()` you get your remaining credits. Check balance regularly, especially before and after batches. Put a `get_balance()` call in a helper script so Claude Code can check it whenever you ask.

## Recommended first session

1. Install the SDK: `pip install pixellab`
2. Set `PIXELLAB_API_KEY` in your shell
3. Run `test_pixellab.py` to verify the balance call works
4. Run `generate_sprite_pixellab.py` for your first 4 clubs
5. Compare side-by-side with your Retro Diffusion clubs
6. Try one inpainting test on an existing Oryx tile

That first session will tell you within an hour whether PixelLab's output quality justifies the switch, or whether it's a "use for specific tasks" tool alongside RD.

## Workflow comparison

| Task | Retro Diffusion | PixelLab |
|---|---|---|
| Style-matched generation | Custom user style | BitForge with reference |
| Palette locking | `input_palette` param (strong) | No built-in palette lock |
| Transparency | `remove_bg` (needs cleanup) | `no_background=True` (cleaner) |
| Inpainting existing tiles | Not available | Yes |
| Tileable textures | `rd_tile__*` styles | `create_texture`, `create_tileset` |
| Native 16×16 | Yes | Via 32→16 downscale |
| Native 24×24 | No (downscale) | No (crop from 64×64) |
| Cost model | Pay-per-image | Subscription tiers |

In your script-driven workflow (no MCP), both feel similar — write Python, run, iterate. The real differentiators are inpainting (PixelLab wins) and palette locking (RD wins). Those two features suggest using both tools side-by-side for different jobs rather than picking one and sticking with it.
