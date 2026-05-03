# extract_palette.py
# Scans all Oryx 16bf sprites and extracts the full unique palette for RetroDiffusion.

from PIL import Image
from pathlib import Path

SPRITES_DIR = Path("src/Presentation/assets/sprites_16bf")

colors = set()
files_scanned = 0

for png in SPRITES_DIR.rglob("*.png"):
    img = Image.open(png).convert("RGBA")
    for r, g, b, a in img.getdata():
        if a > 128:
            colors.add((r, g, b, 255))
    files_scanned += 1

colors = sorted(colors)
print(f"Scanned {files_scanned} sprites, found {len(colors)} unique colors")

palette_img = Image.new("RGBA", (len(colors), 1))
for i, c in enumerate(colors):
    palette_img.putpixel((i, 0), c)

palette_img.save("oryx_palette.png")
print("Saved oryx_palette.png")
