#!/usr/bin/env python3
"""Round E canon-ramp recolors (candidates only — not landed).

Two recolors, both shape-preserving (opaque pixel positions/alpha untouched; only RGB
values remapped onto an exact canon ramp so zero foreign hues remain):

  columns 5093/5094/5095 -> fountain (canon 486/487) stone ramp
  nightstand 5106/5107   -> desk (canon 320) golden furniture-wood ramp

Method: force the sprite's darkest distinct colour to the canon outline (38,38,38);
map every other distinct colour onto the canon ramp. Columns use nearest-luminance
(preserve each tier's lightness, snap hue to stone). Nightstand uses rank-across-ramp
(spread its washed-out tones over the full wood ramp, darkening/enriching them).

Outputs to tools/art_lint/candidates/round_e/. Validates every output colour against
the master palette and prints the resulting palette. Deterministic.
"""
import json, os
from PIL import Image
from collections import Counter

D = "src/Presentation/assets/sprites_16bf/world_24x24"
OUT = "tools/art_lint/candidates/round_e"
os.makedirs(OUT, exist_ok=True)

MASTER = {tuple(c) for c in json.load(open("config/art/oryx_master_palette.json"))["colors"]}

def lum(c): return 0.299*c[0] + 0.587*c[1] + 0.114*c[2]

# --- canon ramps (from recon; all master-palette members) ---
FOUNTAIN_STONE = [(81,81,81),(105,105,105),(201,201,201),(243,243,243)]  # non-outline stone steps
OUTLINE = (38,38,38)
DESK_WOOD = [(56,46,0),(87,71,0),(136,112,0),(184,150,0)]  # dark->light golden wood

def distinct(im):
    return [rgb for rgb,_ in Counter(px[:3] for px in im.getdata() if px[3]==255).most_common()]

def nearest_lum(c, ramp):
    return min(ramp, key=lambda r: abs(lum(c)-lum(r)))

def recolor(idsrc, mapping, outname):
    im = Image.open(f"{D}/oryx_16bit_fantasy_world_{idsrc}.png").convert("RGBA")
    px = im.load()
    w,h = im.size
    for y in range(h):
        for x in range(w):
            r,g,b,a = px[x,y]
            if a==255:
                px[x,y] = (*mapping[(r,g,b)], 255)
    outpath = f"{OUT}/{outname}.png"
    im.save(outpath)
    pal = Counter(px2[:3] for px2 in im.getdata() if px2[3]==255)
    off = [c for c in pal if c not in MASTER]
    print(f"{outname}: {len(pal)} colours  off-palette={off if off else 'NONE'}")
    for c,n in pal.most_common(): print(f"    {c} n={n}")
    return outpath

def build_column_mapping(idsrc):
    im = Image.open(f"{D}/oryx_16bit_fantasy_world_{idsrc}.png").convert("RGBA")
    cols = distinct(im)
    darkest = min(cols, key=lum)
    m = {}
    for c in cols:
        m[c] = OUTLINE if c==darkest else nearest_lum(c, FOUNTAIN_STONE)
    return im, m

def build_nightstand_mapping(idsrc):
    im = Image.open(f"{D}/oryx_16bit_fantasy_world_{idsrc}.png").convert("RGBA")
    cols = distinct(im)
    darkest = min(cols, key=lum)
    wood = sorted([c for c in cols if c!=darkest], key=lum)  # dark->light
    m = {darkest: OUTLINE}
    k = len(wood)
    for i,c in enumerate(wood):
        idx = round(i*(len(DESK_WOOD)-1)/(k-1)) if k>1 else 0
        m[c] = DESK_WOOD[idx]
    return im, m

print("=== columns -> fountain stone ramp ===")
for cid in ["5093","5094","5095"]:
    _, m = build_column_mapping(cid)
    recolor(cid, m, f"{cid}_stone")

print("\n=== nightstand -> desk golden wood ramp ===")
_, m = build_nightstand_mapping("5106")
recolor("5106", m, "5106_wood")
# 5107 is byte-identical to 5106; same recolor
recolor("5107", m, "5107_wood")
