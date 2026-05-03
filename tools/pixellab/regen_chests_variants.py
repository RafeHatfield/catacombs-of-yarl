#!/usr/bin/env python3
"""
Chest variant generation — two strategies:

STRATEGY 1: Inpaint with surgical mask (lid area only)
  - Upscale hero to 64x64, mask the lid, inpaint open/empty/trapped states
  - Pixels outside mask are preserved exactly → structurally identical chest body

STRATEGY 2: animate_with_text with reference_image
  - Uses the proper identity-anchor mechanism designed for consistent frames
  - reference_image tells the model "this is what the object looks like"

Run from project root: source ~/.bashrc && .venv/bin/python3 tools/pixellab/regen_chests_variants.py
"""

import os, time
from pathlib import Path
from PIL import Image, ImageDraw
import pixellab

client = pixellab.Client(secret=os.environ["PIXELLAB_API_KEY"])

HERO_32 = Path("tools/pixellab/batch_new_sprites_results/chest/chest_closed/chest_closed_s42_32px.png")
OUT = Path("tools/pixellab/batch_new_sprites_results/chest")

hero_32 = Image.open(HERO_32).convert("RGBA")
# Upscale to 64x64 for inpaint (clean ratio, avoids min-area issues)
hero_64 = hero_32.resize((64, 64), Image.NEAREST)


def save_done(path, img):
    img.save(path)
    print(f"  ✓ {path.name}")
    time.sleep(0.15)


# ─── Strategy 1: Inpaint with surgical mask ──────────────────────────────────

print("=== STRATEGY 1: Inpaint (surgical mask at 64x64) ===\n")
out_s1 = OUT / "strategy1_inpaint"
out_s1.mkdir(parents=True, exist_ok=True)

def make_mask_64(lid_rows=28):
    """White (255) = regenerate, Black (0) = preserve. Lid = top N rows."""
    mask = Image.new("RGB", (64, 64), (0, 0, 0))
    draw = ImageDraw.Draw(mask)
    draw.rectangle([0, 0, 63, lid_rows], fill=(255, 255, 255))
    return mask

lid_mask = make_mask_64(lid_rows=28)  # top ~44% = lid area

INPAINT_VARIANTS = [
    ("open",    "large ornate treasure chest, open lid showing gold coins inside, pixel art"),
    ("empty",   "large ornate treasure chest, open lid, empty dark interior, pixel art"),
    ("trapped", "large ornate treasure chest, open lid, spiked trap mechanism inside, pixel art"),
]

for state, desc in INPAINT_VARIANTS:
    out_64 = out_s1 / f"{state}_64px.png"
    out_32 = out_s1 / f"{state}_32px.png"
    if out_32.exists():
        print(f"  {state} (cached)")
        continue
    print(f"  [{state}] {desc}")
    resp = client.inpaint(
        description=desc,
        image_size={"width": 64, "height": 64},
        inpainting_image=hero_64,
        mask_image=lid_mask,
        text_guidance_scale=7.0,
        extra_guidance_scale=4.0,
        no_background=True,
        seed=42,
    )
    img_64 = resp.image.pil_image()
    img_64.save(out_64)
    img_32 = img_64.resize((32, 32), Image.NEAREST)
    save_done(out_32, img_32)

# Also try a taller mask (covers more of the chest front) for trapped
print("  [trapped_tall_mask] skull on front face")
out_32 = out_s1 / "trapped_tall_mask_32px.png"
if not out_32.exists():
    tall_mask = make_mask_64(lid_rows=48)  # top 75% — exposes front face too
    resp = client.inpaint(
        description="large ornate treasure chest, skull and crossbones warning on front, closed lid, pixel art",
        image_size={"width": 64, "height": 64},
        inpainting_image=hero_64,
        mask_image=tall_mask,
        text_guidance_scale=7.0,
        extra_guidance_scale=4.0,
        no_background=True,
        seed=42,
    )
    img_64 = resp.image.pil_image()
    img_64.save(out_s1 / "trapped_tall_mask_64px.png")
    save_done(out_32, img_64.resize((32, 32), Image.NEAREST))
else:
    print("  trapped_tall_mask (cached)")


# ─── Strategy 2: animate_with_text with reference_image ──────────────────────

print("\n=== STRATEGY 2: animate_with_text (reference_image identity lock) ===\n")
out_s2 = OUT / "strategy2_animate"
out_s2.mkdir(parents=True, exist_ok=True)

ANIM_OUT = out_s2 / "frames_raw"
ANIM_OUT.mkdir(exist_ok=True)

# Must be 64x64 for animate endpoint
if not any(ANIM_OUT.iterdir()) if ANIM_OUT.exists() else True:
    print("  Generating 4 frames (closed, open, empty, trapped)...")
    resp = client.animate_with_text(
        description="large ornate treasure chest in four states: closed, open with gold, empty, trapped with skull, pixel art",
        action="chest state variants: closed shut, lid open showing treasure, lid open empty, lid closed with warning",
        reference_image=hero_64,
        image_size={"width": 64, "height": 64},
        n_frames=4,
        image_guidance_scale=8.0,
        text_guidance_scale=5.0,
        negative_description="",
        seed=42,
    )
    frames = resp.images if hasattr(resp, 'images') else [resp.image]
    for i, frame in enumerate(frames):
        labels = ["closed", "open", "empty", "trapped"]
        label = labels[i] if i < len(labels) else f"frame{i}"
        img_64 = frame.pil_image()
        img_64.save(ANIM_OUT / f"{label}_64px.png")
        img_32 = img_64.resize((32, 32), Image.NEAREST)
        img_32.save(ANIM_OUT / f"{label}_32px.png")
        print(f"  frame {i} ({label}) ✓")
        time.sleep(0.1)
else:
    print("  (cached)")

print("\nDone — review strategy1_inpaint/ and strategy2_animate/frames_raw/")
