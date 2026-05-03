# Retro Diffusion walkthrough: generating Oryx-style sprites for YARL

A step-by-step guide for creating 24×24 pixel art sprites that match the Oryx 16-Bit Fantasy tileset, using the Retro Diffusion API. Written for someone who has never done this before.

## What you'll need before starting

1. **A Retro Diffusion account** — sign up at retrodiffusion.ai (you get 50 free credits)
2. **An API key** — once logged in, go to your account/devtools page and generate one
3. **Python 3** on your machine (you already have this via Godot development)
4. **The `requests` and `Pillow` libraries** — `pip install requests Pillow`
5. **A few Oryx tiles** extracted as individual PNGs to use as style references

## Can Claude Code drive this directly?

Yes. The Retro Diffusion API is a simple REST endpoint — Claude Code can call it with Python's `requests` library from your terminal. You'll need to give Claude Code your API key (set it as an environment variable: `export RD_API_KEY="your_key_here"`) and it can generate, download, and process sprites for you in a single session.

The workflow in Claude Code looks like: you describe what sprite you want → Claude Code writes a Python script → calls the RD API → saves the result → downscales to 24×24 → shows you the result. You can iterate by saying "make it more detailed" or "try a different style" without leaving the terminal.

## Step 1: Extract your Oryx palette

The Oryx 16-Bit Fantasy tileset uses a specific set of colors. We need to extract these into a small PNG that Retro Diffusion can use to constrain its output.

```python
# extract_palette.py
# Run this once on your Oryx sprite sheet to extract the palette

from PIL import Image
import collections

# Point this at your Oryx 16-Bit Fantasy sprite sheet
img = Image.open("path/to/oryx_16bit_fantasy_world_24x24.png").convert("RGBA")

# Collect all unique colors (ignoring fully transparent pixels)
colors = set()
for pixel in img.getdata():
    r, g, b, a = pixel
    if a > 128:  # skip transparent
        colors.add((r, g, b, 255))

colors = sorted(colors)
print(f"Found {len(colors)} unique colors in Oryx tileset")

# Create a palette image — one pixel per color, in a single row
palette_img = Image.new("RGBA", (len(colors), 1))
for i, c in enumerate(colors):
    palette_img.putpixel((i, 0), c)

palette_img.save("oryx_palette.png")
print("Saved oryx_palette.png")
```

This gives you a tiny PNG containing every color in the Oryx set. You'll feed this to Retro Diffusion as the `input_palette` parameter and it will constrain every generated pixel to only use these colors.

### About floor-specific palettes

You asked about different palettes for different floor themes. You have two options:

**Option A (recommended): Use the full Oryx palette for everything.** The palette constrains what colors *can* appear — it doesn't force all colors to appear. A stone dungeon sprite will naturally use grays and browns; a mossy cave sprite will naturally use greens. The full palette covers all themes.

**Option B: Create per-theme sub-palettes.** Extract colors from just the stone tiles, just the dirt tiles, etc. This gives tighter color matching per theme but means you need to manage multiple palette files. Only worth doing if you find the full palette produces color choices that look wrong for a specific theme.

Start with Option A. You can always create sub-palettes later if needed.

## Step 2: Prepare style reference images

To get Retro Diffusion's RD Pro model to match the Oryx style, you'll provide reference images. Extract 5–9 individual Oryx tiles that represent the breadth of what you need:

- 1–2 character/creature tiles
- 1–2 weapon/item tiles  
- 1–2 dungeon prop tiles (barrel, chest, table)
- 1–2 environment tiles (floor, wall)

Save each as a separate 24×24 PNG. These don't need to be related to what you're generating — they teach the model the *style* (outline weight, shading approach, color use, level of detail).

## Step 3: Create a persistent Oryx style (RD Pro)

This is a one-time setup. You're creating a reusable "style" that tells Retro Diffusion "make things that look like these reference images."

```python
# create_oryx_style.py

import requests
import base64
import os

API_KEY = os.environ.get("RD_API_KEY", "YOUR_API_KEY_HERE")

# Load your reference images as base64
def load_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Point these at your extracted Oryx reference tiles
reference_images = [
    load_b64("ref_hero.png"),
    load_b64("ref_skeleton.png"),
    load_b64("ref_sword.png"),
    load_b64("ref_barrel.png"),
    load_b64("ref_chest.png"),
    load_b64("ref_floor_stone.png"),
    load_b64("ref_wall.png"),
]

url = "https://api.retrodiffusion.ai/v1/styles"
headers = {"X-RD-Token": API_KEY}

payload = {
    "name": "Oryx 16-Bit Fantasy Style",
    "description": "SNES-era 16-bit pixel art, dark outlines, limited palette, "
                   "top-down RPG perspective, clean readable silhouettes at small sizes",
    "reference_images": reference_images,
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

print("Style created!")
print(f"Style ID: {data['prompt_style']}")
print("Save this ID — you'll use it for every generation")
# Example output: user__oryx_16bit_abc123
```

Save the returned `prompt_style` value (something like `user__oryx_16bit_abc123`). You'll use this in every generation call.

## Step 4: Generate a sprite — the club weapon example

Now let's generate an actual sprite. A club is a great first test — simple shape, recognizable silhouette, just a wooden stick with a thick end.

```python
# generate_club.py

import requests
import base64
import os
from PIL import Image
from io import BytesIO

API_KEY = os.environ.get("RD_API_KEY", "YOUR_API_KEY_HERE")
ORYX_STYLE = "user__oryx_16bit_abc123"  # Your saved style ID from Step 3

# Load palette as base64
with open("oryx_palette.png", "rb") as f:
    palette_b64 = base64.b64encode(f.read()).decode("utf-8")

url = "https://api.retrodiffusion.ai/v1/inferences"
headers = {"X-RD-Token": API_KEY}

payload = {
    "prompt": "a simple wooden club weapon, thick end on top tapering to thin handle, "
              "dark wood with grain detail, small sprite on transparent background, "
              "top-down RPG item icon",
    "prompt_style": ORYX_STYLE,  # or try "rd_pro__fantasy" if no custom style yet
    "width": 48,          # Generate at 2x target size for better detail
    "height": 48,
    "num_images": 4,      # Generate 4 variants, pick the best one
    "input_palette": palette_b64,  # Lock to Oryx colors
    "remove_bg": True,    # Transparent background
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

print(f"Credits used: {data['credit_cost']}")
print(f"Credits remaining: {data.get('remaining_credits', 'unknown')}")

# Save all variants at native 48x48 and downscaled to 24x24
for i, img_b64 in enumerate(data["base64_images"]):
    img_bytes = base64.b64decode(img_b64)
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")

    # Save the 48x48 version
    img.save(f"club_48x48_{i}.png")

    # Downscale to 24x24 using nearest-neighbor (preserves pixel crispness)
    img_24 = img.resize((24, 24), Image.NEAREST)
    img_24.save(f"club_24x24_{i}.png")

    print(f"Saved club variant {i}")
```

This will give you 4 different club sprites. Look at them and pick the one that reads best at 24×24.

## Step 5: Evaluate and iterate

Look at your 4 results. Common issues and how to fix them:

**Too detailed / muddy at 24×24?** Generate at 48×48 instead of 96×96, or add "simple, minimal detail" to your prompt.

**Wrong perspective?** Add "top-down view" or "3/4 top-down RPG item" to your prompt. For weapons that should look like inventory icons (angled, floating), try "RPG inventory icon, angled 45 degrees."

**Colors don't match Oryx?** Make sure you're passing `input_palette`. If colors are technically in-palette but look wrong, try a sub-palette extracted from just the Oryx weapon tiles.

**Shape is unrecognizable at 24×24?** The silhouette is everything at this size. Add "clear silhouette, simple shape" to your prompt. Or generate at 48×48 and manually pick which variant downscales best.

**Style doesn't match?** Try different built-in styles before your custom style:
- `rd_pro__fantasy` — bright colors, outlines, closest to SNES RPG
- `rd_pro__simple` — minimal shading, strong outlines
- `rd_pro__default` — clean modern pixel art
- `rd_pro__topdown` — specifically 3/4 top-down perspective

## Step 6: Batch generation

Once you've dialed in prompts that work, you can batch-generate entire categories:

```python
# batch_generate.py

import requests
import base64
import os
import time
from PIL import Image
from io import BytesIO

API_KEY = os.environ.get("RD_API_KEY", "YOUR_API_KEY_HERE")
ORYX_STYLE = "user__oryx_16bit_abc123"

with open("oryx_palette.png", "rb") as f:
    palette_b64 = base64.b64encode(f.read()).decode("utf-8")

# Define all the sprites you need
sprites = [
    # Weapons
    {"name": "club",         "prompt": "wooden club weapon, thick end tapering to handle, dark wood"},
    {"name": "mace",         "prompt": "iron mace weapon, spiked ball on wooden handle"},
    {"name": "staff",        "prompt": "wooden wizard staff, crystal on top, tall thin"},
    {"name": "bow",          "prompt": "wooden shortbow, curved, with bowstring"},
    {"name": "dagger",       "prompt": "short dagger, silver blade, brown leather handle"},
    {"name": "battleaxe",    "prompt": "battle axe, iron head, wooden handle"},

    # Props
    {"name": "anvil",        "prompt": "iron anvil on wooden stump, blacksmith tool"},
    {"name": "cauldron",     "prompt": "black iron cauldron, round with handles, bubbling green liquid"},
    {"name": "bookshelf",    "prompt": "wooden bookshelf full of colorful books, wall furniture"},
    {"name": "throne",       "prompt": "ornate stone throne with red cushion, royal furniture"},

    # Characters (if needed)
    {"name": "goblin",       "prompt": "small green goblin, holding a dagger, menacing pose"},
    {"name": "skeleton",     "prompt": "undead skeleton warrior, holding a sword, front facing"},
]

url = "https://api.retrodiffusion.ai/v1/inferences"
headers = {"X-RD-Token": API_KEY}

os.makedirs("generated_48", exist_ok=True)
os.makedirs("generated_24", exist_ok=True)

for sprite in sprites:
    print(f"Generating: {sprite['name']}...")

    payload = {
        "prompt": f"{sprite['prompt']}, small sprite on transparent background, "
                  f"top-down RPG, pixel art, clear silhouette",
        "prompt_style": ORYX_STYLE,
        "width": 48,
        "height": 48,
        "num_images": 4,
        "input_palette": palette_b64,
        "remove_bg": True,
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    for i, img_b64 in enumerate(data["base64_images"]):
        img = Image.open(BytesIO(base64.b64decode(img_b64))).convert("RGBA")
        img.save(f"generated_48/{sprite['name']}_{i}.png")
        img_24 = img.resize((24, 24), Image.NEAREST)
        img_24.save(f"generated_24/{sprite['name']}_{i}.png")

    print(f"  → Saved 4 variants, cost: {data['credit_cost']} credits")
    time.sleep(1)  # Be nice to the API

print("Done! Review generated_24/ folder and pick your favorites.")
```

## Quick reference: what things cost

Based on the API documentation:

| Action | Credits |
|---|---|
| RD Fast generation (up to 256×256) | ~1 credit per image |
| RD Plus generation (up to 256×256) | ~1–2 credits per image |
| RD Pro generation (up to 256×256) | ~0.25 balance per image |
| Creating a custom style | Free |
| Free signup bonus | 50 credits |

At 48×48 generation with 4 variants per sprite, you're spending roughly 1–4 credits per sprite attempt. Your 50 free credits should get you 12–50 sprites to experiment with before you need to buy more.

## The complete workflow, summarized

1. **Once:** Extract Oryx palette → `oryx_palette.png`
2. **Once:** Extract 5–9 reference tiles → create RD Pro custom style
3. **Per sprite:** Write a prompt → generate 4 variants at 48×48 with palette lock → downscale to 24×24 → pick the best one
4. **If needed:** Touch up in Aseprite (fix a stray pixel, adjust an outline)
5. **Batch:** Once your prompts are dialed in, batch-generate entire categories

## Tips from experience

- **Prompts should describe the object, not the art style.** The style comes from your custom style + the model. Your prompt should focus on "what is this thing" — shape, material, pose, distinguishing features.
- **"transparent background" and "small sprite" are magic words.** Always include them for individual game assets.
- **Generate more variants than you think you need.** 4 per sprite is minimum. The pick-the-best-one step is where quality happens.
- **48×48 is the sweet spot for 24×24 targets.** Generating at 96×96 gives more detail but downscales poorly. 48×48 forces the model to keep things simple, which is what you want.
- **Save your good prompts.** When you find a prompt structure that works for weapons, save it as a template and swap out the specific weapon description.
- **The built-in `rd_pro__fantasy` style is a great starting point** before you invest in a custom style. Try it first — you might not even need the custom style for many assets.
