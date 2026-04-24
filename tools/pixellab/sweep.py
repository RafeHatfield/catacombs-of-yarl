#!/usr/bin/env python3
"""
PixelLab BitForge parameter sweep for YARL prop generation.

Groups:
  A - perspective modes (oblique/iso/view combos)
  B - style quality (shading, detail, outline)
  C - style strength (0 → 100)
  D - palette locking (color_image variants)

Subject: wooden chair at 48x48 → 24x24 downscale.
"""

import os
import sys
import time
from pathlib import Path
from PIL import Image
import pixellab

# ---- Setup ----
API_KEY = os.environ.get("PIXELLAB_API_KEY")
if not API_KEY:
    print("ERROR: PIXELLAB_API_KEY not set")
    sys.exit(1)

client = pixellab.Client(secret=API_KEY)
balance = client.get_balance()
print(f"Balance: {balance}")

TOOLS_DIR = Path(__file__).parent
RD_DIR = TOOLS_DIR.parent / "retrodiffusion"
# color_image does spatial color transfer (not palette quantization) — do not pass palette strip
# style_image must match generation size exactly — resized below after GEN_SIZE is defined
_ORYX_STYLE_REF_RAW = Image.open(RD_DIR / "oryx_style_reference.png").convert("RGBA")

OUT_DIR = TOOLS_DIR / "sweep_results"
OUT_DIR.mkdir(exist_ok=True)

PROMPT = "wooden chair, small sprite, pixel art, clear silhouette"
VARIANTS = 2
SEEDS = [42, 137]
GEN_SIZE = {"width": 32, "height": 32}
FINAL_SIZE = 24

# style_image must match GEN_SIZE exactly (API requirement)
ORYX_STYLE_REF = _ORYX_STYLE_REF_RAW.resize((GEN_SIZE["width"], GEN_SIZE["height"]), Image.NEAREST)

# Base: no color_image (palette strip causes spatial corruption), style_image optional per-test
BASE = {
    "style_strength": 50.0,
    "shading": "basic shading",
    "detail": "low detail",
    "outline": "single color black outline",
    "no_background": True,
}

def cfg(**overrides):
    return {**BASE, **overrides}


TESTS = [
    # ---- Group A: Perspective ----
    ("A_persp", "default",           cfg()),
    ("A_persp", "oblique_side",      cfg(oblique_projection=True,  view="side")),
    ("A_persp", "oblique_lowtop",    cfg(oblique_projection=True,  view="low top-down")),
    ("A_persp", "oblique_hightop",   cfg(oblique_projection=True,  view="high top-down")),
    ("A_persp", "oblique_noview",    cfg(oblique_projection=True)),
    ("A_persp", "iso",               cfg(isometric=True)),
    ("A_persp", "side_only",         cfg(view="side")),

    # ---- Group B: Style quality (base: oblique + side) ----
    ("B_style", "no_params",         cfg()),   # baseline — no shading/detail/outline overrides
    ("B_style", "flat_low_black",    cfg(oblique_projection=True, view="side", shading="flat shading",   detail="low detail")),
    ("B_style", "basic_low_black",   cfg(oblique_projection=True, view="side", shading="basic shading",  detail="low detail")),
    ("B_style", "medium_low_black",  cfg(oblique_projection=True, view="side", shading="medium shading", detail="low detail")),
    ("B_style", "basic_med_black",   cfg(oblique_projection=True, view="side", shading="basic shading",  detail="medium detail")),
    ("B_style", "basic_low_lineless",cfg(oblique_projection=True, view="side", outline="lineless")),
    ("B_style", "basic_low_nooutline",cfg(oblique_projection=True, view="side", outline=None)),

    # ---- Group C: Style image strength (base: oblique + side) ----
    ("C_strength", "no_style_img",   cfg(oblique_projection=True, view="side", style_strength=0.0)),
    ("C_strength", "s25",            cfg(oblique_projection=True, view="side", style_image=ORYX_STYLE_REF, style_strength=25.0)),
    ("C_strength", "s50",            cfg(oblique_projection=True, view="side", style_image=ORYX_STYLE_REF, style_strength=50.0)),
    ("C_strength", "s75",            cfg(oblique_projection=True, view="side", style_image=ORYX_STYLE_REF, style_strength=75.0)),
    ("C_strength", "s100",           cfg(oblique_projection=True, view="side", style_image=ORYX_STYLE_REF, style_strength=100.0)),
]

total = len(TESTS) * VARIANTS
print(f"\n{len(TESTS)} configs × {VARIANTS} variants = {total} images")
if "--yes" not in sys.argv:
    confirm = input("Proceed? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(0)

# ---- Generate ----
count = 0
total_usd = 0.0
errors = []

for group, name, kwargs in TESTS:
    test_dir = OUT_DIR / group / name
    test_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{group}/{name}]")
    for i, seed in enumerate(SEEDS):
        try:
            response = client.generate_image_bitforge(
                description=PROMPT,
                image_size=GEN_SIZE,
                seed=seed,
                **kwargs,
            )
            img = response.image.pil_image()

            img.save(test_dir / f"chair_{i}_32px.png")

            preview = img.resize((128, 128), Image.NEAREST)
            preview.save(test_dir / f"chair_{i}_preview.png")

            usd = response.usage.usd
            total_usd += usd
            count += 1
            print(f"  [{i}] ✓  ${usd:.4f}")
        except Exception as e:
            msg = f"[{group}/{name} v{i}] {e}"
            print(f"  [{i}] ERROR: {e}")
            errors.append(msg)
        time.sleep(0.3)

print(f"\n{'='*60}")
print(f"Done: {count}/{total} images")
print(f"Total cost: ${total_usd:.4f}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
print(f"\nResults: {OUT_DIR}/")
print("Subfolders: A_persp / B_style / C_strength / D_palette")
print("Each config has: *_48px.png (native), *_24px.png (final), *_preview.png (6x)")
