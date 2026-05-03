# Aseprite + Retro Diffusion Lite setup walkthrough

A guide to setting up a production-quality pixel art workflow for YARL, going beyond pure AI generation to include hand-editing in Aseprite. Written for someone who's never used Aseprite.

## The conceptual model

Think of the pipeline as three layers:

**Layer 1 — Generation (Retro Diffusion API):** Produces a 64×64 sprite via the Python script you've built. Gets you ~80% of the way there — good silhouette, palette-matched colors, transparent background. But it has rough edges: stray pixels, slightly wrong outlines, colors that are close to but not exactly Oryx, details that look noisy at 16×16.

**Layer 2 — Editor (Aseprite):** The industry-standard pixel art editor. Where you fix the last 20% — hand-edit individual pixels, refine silhouettes, clean up outlines, make the sprite "sing." Professional pixel artists spend 90% of their time in Aseprite.

**Layer 3 — AI-powered cleanup inside the editor (RD Lite extension):** Aseprite plugin that adds AI tools directly inside Aseprite — palettize (force exact Oryx colors), color style transfer (recolor one sprite to match another's palette), pixfix (fix mixels), and text-guided palette generation.

You don't strictly need all three to ship a game. But all three together is what lets a non-artist produce sprites that a pixel artist would accept.

## What each piece actually does

### Aseprite ($20 on Steam or aseprite.org)

A dedicated pixel art editor. The core things you need to learn:

- **Pixel-perfect drawing tools** — single-pixel pencil, color picker, bucket fill
- **Indexed color mode** — lock your canvas to a specific palette (the Oryx palette) so you physically can't draw with wrong colors
- **Layers** — keep the AI-generated base on one layer, your edits on another, compare by toggling
- **Timeline** — for animations (you won't need this yet)
- **Onion skinning** — see adjacent frames while editing (again, animations)

For your workflow: you'll open a generated 64×64 sprite, set the palette to your Oryx palette file, and manually fix anything that's off. Most sprites need 5–15 minutes of cleanup.

### RD Lite Extension for Aseprite ($20 on itch.io)

**Important clarification:** this is different from the retrodiffusion.ai API you've been using. The RD website/API uses large server-side models. The RD Aseprite extension runs a smaller model locally (or connects to their API for some features). Same brand, different tools.

The extension adds four menu items inside Aseprite:

- **Palettize** — Takes your current image and snaps every pixel to the nearest color in your active palette. If you load the Oryx palette and run this on your AI-generated club, it forces all pixels to exactly match Oryx colors. This is the single most useful feature for your workflow.
- **PixFix** — Detects mixels (those wrong-sized "pixels" AI generators sometimes produce) and snaps everything to a clean grid. Less critical for RD API output which is already grid-aligned, but useful if you ever use Midjourney/DALL-E for reference.
- **Color Style Transfer** — Take an Oryx tile, take your AI sprite, and transfer Oryx's color style (not just palette) to your sprite. Very useful for matching the specific Oryx shading feel.
- **Text-guided palette creation** — Generate a new palette from a text prompt ("mossy cave dungeon"). Useful if you want per-theme sub-palettes later.

### RD Full Extension ($45 on itch.io)

Same as Lite but adds local generation — you can generate pixel art inside Aseprite without calling the API. Requires a decent GPU. **You don't need this.** You're already generating via the API cheaply. Stick with Lite.

## Setup walkthrough

### Step 1: Install Aseprite

- Buy Aseprite on Steam ($20) or from aseprite.org ($20)
- Install and launch it
- Open any generated sprite (`generated/64x64/club_01_0.png`) to verify it opens correctly

### Step 2: Create an Oryx palette file for Aseprite

Aseprite uses `.gpl` (GIMP palette) or `.pal` formats, not PNG. Convert your `oryx_palette.png` to a palette file:

```python
# export_palette_for_aseprite.py
from PIL import Image

img = Image.open("oryx_palette.png").convert("RGBA")
colors = []
for pixel in img.getdata():
    r, g, b, a = pixel
    if a > 0:
        colors.append((r, g, b))
colors = sorted(set(colors))

with open("oryx_palette.gpl", "w") as f:
    f.write("GIMP Palette\n")
    f.write("Name: Oryx 16-Bit Fantasy\n")
    f.write("Columns: 16\n")
    f.write("#\n")
    for r, g, b in colors:
        f.write(f"{r:3d} {g:3d} {b:3d}\tOryx\n")

print(f"Wrote {len(colors)} colors to oryx_palette.gpl")
```

In Aseprite: **Window → Palette → Preset folder → Open** to drop the `.gpl` file in, or just **File → Import Palette** to load it directly.

### Step 3: Install RD Lite Extension

- Buy RD Lite on itch.io ($20) — astropulse.itch.io/retrodiffusionlite
- Download the `.aseprite-extension` file
- In Aseprite: **Edit → Preferences → Extensions → Add Extension**
- Select the downloaded file, click Install, restart Aseprite
- You'll see a new "Retro Diffusion" menu in the top menu bar

### Step 4: Your new per-sprite workflow

Here's what a production pass on a single sprite looks like:

1. **Open** the 64×64 generated sprite in Aseprite
2. **Palette → Open Palette → oryx_palette.gpl** (loads Oryx colors)
3. **Sprite → Color Mode → Indexed** (locks canvas to palette)
4. **Retro Diffusion menu → Palettize** (snaps all pixels to exact Oryx colors)
5. **Hand-edit** anything that looks off — zoom to 800%+, fix outlines, remove stray pixels, sharpen silhouette
6. **Sprite → Sprite Size → 25% (nearest neighbor)** to preview at 16×16
7. Toggle between 64×64 and 16×16 to make sure silhouette reads correctly at game size
8. **Export** as PNG at both sizes

### Step 5: Learn the essential Aseprite skills

Three YouTube resources that cover 95% of what you need:

- **MortMort** — "Pixel Art Class" series, the gold standard
- **AdamCYounis** — long-form Aseprite tutorials for game devs
- **Pixel Pete** — quick practical tips

Focus specifically on: pixel-level outline cleanup, anti-aliasing rules (mostly: don't), dithering basics, and silhouette checks. Skip animation for now.

## Realistic quality expectations

Even with the full toolchain, you're not going to match Oryx's own work immediately — Christopher Barrett has decades of experience. But with the AI base + palettize + ~10 minutes of cleanup per sprite, you'll produce sprites that blend with Oryx at game scale without looking obviously out of place. That's the realistic target.

For a batch of 100 sprites, the math looks like:

- AI generation (8 variants/sprite, pick best): ~$140
- Your time: ~20 hours of Aseprite cleanup
- Aseprite + RD Lite: $40 one-time

That's a full indie game's sprite library for ~$180 + your time, vs thousands to commission.

## Recommended starting point

Start with just **Aseprite alone** ($20). Open one of your generated clubs, fumble through the interface for 30 minutes, try to clean up one sprite by hand. See if you enjoy it and if the output is meaningfully better than the raw AI version.

If the answer is yes, then buy RD Lite ($20) to accelerate the palettize step. If the answer is "I don't want to pixel-edit," then the AI-only workflow you have is good enough for prototyping, and you can commission a pixel artist later for production sprites.

The skill you're really investing in is **pixel editing judgment** — which doesn't come from the tools, it comes from staring at sprites and developing taste. Aseprite is just where that skill lives.
