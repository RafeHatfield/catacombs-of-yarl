#!/usr/bin/env python3
"""Round E canon derivations (candidates only — not landed).

No canon bench or bed sprite exists (recon confirmed), so per the ruling both are
DERIVED from canon furniture construction using only canon-furniture colours:

  wood ramp (canon chair 321 / table 319 / desk 320, identical):
     (56,46,0) (87,71,0) (136,112,0) (184,150,0), outline (38,38,38)
  bedding neutrals (master palette): (201,201,201) (243,243,243)
  blanket blue (canon fountain 486): (59,92,148) (75,117,189) (145,186,255)

Register discipline: chunky members (>=2px), two-plane (front face + top surface only,
no side planes), bold (38,38,38) silhouette outline auto-added. All colours are
master-palette members. Deterministic. Outputs to tools/art_lint/candidates/round_e/.
"""
import json, os
from PIL import Image

OUT = "tools/art_lint/candidates/round_e"
os.makedirs(OUT, exist_ok=True)
MASTER = {tuple(c) for c in json.load(open("config/art/oryx_master_palette.json"))["colors"]}

OUTLINE=(38,38,38)
W_DARK=(56,46,0); W_MED=(87,71,0); W_MID=(136,112,0); W_LT=(184,150,0)
CL_MED=(201,201,201); CL_LT=(243,243,243)
BL_DK=(59,92,148); BL_MD=(75,117,189); BL_LT=(145,186,255)

def canvas(): return [[None]*24 for _ in range(24)]  # grid[y][x]

def rect(g,x0,y0,x1,y1,c):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            if 0<=x<24 and 0<=y<24: g[y][x]=c

def add_silhouette_outline(g):
    # any opaque pixel 4-adjacent to transparent (or border) becomes outline
    out=[row[:] for row in g]
    for y in range(24):
        for x in range(24):
            if g[y][x] is None: continue
            edge=False
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=x+dx,y+dy
                if not(0<=nx<24 and 0<=ny<24) or g[ny][nx] is None: edge=True;break
            if edge: out[y][x]=OUTLINE
    return out

def save(g,name):
    im=Image.new("RGBA",(24,24),(0,0,0,0)); px=im.load()
    for y in range(24):
        for x in range(24):
            if g[y][x] is not None: px[x,y]=(*g[y][x],255)
    im.save(f"{OUT}/{name}.png")
    pal=set();
    from collections import Counter
    c=Counter(g[y][x] for y in range(24) for x in range(24) if g[y][x])
    off=[k for k in c if k not in MASTER]
    print(f"{name}: {len(c)} colours off-palette={off if off else 'NONE'}  opaque={sum(c.values())}")

# ---------------- BENCH 5060 : seat + chunky back rail + posts + legs -------------
def bench_backed():
    g=canvas()
    # legs (behind seat) - front two
    rect(g,3,15,5,21,W_MED); rect(g,18,15,20,21,W_MED)
    # seat slab: top surface (light) + front face (mid)
    rect(g,2,11,21,12,W_LT)      # top surface
    rect(g,2,13,21,14,W_MID)     # front face
    # back posts (chunky)
    rect(g,4,5,6,11,W_MED); rect(g,17,5,19,11,W_MED)
    # back top rail (chunky horizontal)
    rect(g,4,4,19,6,W_LT); rect(g,4,7,19,8,W_MID)   # rail top + face
    # a lower back rail for a solid chunky read
    rect(g,6,9,17,10,W_MID)
    g=add_silhouette_outline(g)
    # interior definition: dark seam under seat top, along rail
    for x in range(4,20):
        if g[12][x]==W_LT: g[12][x]=W_MID
    return g

# ---------------- BENCH 5061 : open low-back bench (differentiate from a table) ----
def bench_lowback():
    g=canvas()
    # open low back: two posts + a single rail, gap between (reads through -> seating)
    rect(g,4,4,5,12,W_MED); rect(g,18,4,19,12,W_MED)        # back posts
    rect(g,4,5,19,7,W_LT); rect(g,4,8,19,8,W_MID)           # single chunky back rail
    # legs
    rect(g,3,15,5,21,W_MED); rect(g,18,15,20,21,W_MED)
    # seat slab: top surface (light) + front face (mid)
    rect(g,2,12,21,13,W_LT)
    rect(g,2,14,21,15,W_MID)
    g=add_silhouette_outline(g)
    return g

# ---------------- BED 5058 : wood frame + white pillow + blue blanket -------------
def bed_blue():
    g=canvas()
    # headboard (top), tall wood panel
    rect(g,3,2,20,6,W_MID); rect(g,3,2,20,3,W_LT)
    # side rails (frame) running down
    rect(g,3,6,4,21,W_MED); rect(g,19,6,20,21,W_MED)
    # footboard (front)
    rect(g,3,18,20,21,W_MID); rect(g,3,18,20,18,W_LT)
    # pillow
    rect(g,5,6,11,9,CL_LT); rect(g,5,9,11,9,CL_MED)
    # blanket (mattress top surface) blue with fold highlight + shadow
    rect(g,5,9,18,17,BL_MD)
    rect(g,5,10,18,10,BL_LT)          # top highlight fold
    rect(g,5,14,18,14,BL_DK)          # a fold shadow line
    rect(g,5,17,18,17,BL_DK)          # blanket edge shadow
    g=add_silhouette_outline(g)
    return g

# ---------------- BED 5059 : wood frame + white coverlet (neutral variant) --------
def bed_white():
    g=canvas()
    rect(g,3,2,20,6,W_MID); rect(g,3,2,20,3,W_LT)
    rect(g,3,6,4,21,W_MED); rect(g,19,6,20,21,W_MED)
    rect(g,3,18,20,21,W_MID); rect(g,3,18,20,18,W_LT)
    rect(g,5,6,11,9,CL_LT)                     # pillow
    rect(g,5,9,18,17,CL_MED)                   # white coverlet
    rect(g,5,10,18,10,CL_LT)
    rect(g,5,14,18,14,W_MED)                   # a wood-toned fold/seam
    g=add_silhouette_outline(g)
    return g

save(bench_backed(),"5060_bench")
save(bench_lowback(),"5061_bench")
save(bed_blue(),"5058_bed")
save(bed_white(),"5059_bed")
