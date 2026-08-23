#!/usr/bin/env python3
"""Round E2 — structural derivations + fixes (candidates only, not landed).

Per the Round E verdicts:
  bench  <- STRUCTURAL from canon chair 321 (widen seat by interior column insertion).
  bed    <- STRUCTURAL from canon table 319 (re-dress: bedding inset on the top surface,
            table's apron/footboard + 5px legs kept = front face present).
  nightstand -> golden desk-320 recolor + legs thickened 3px->5px (canon stroke).
  pillars -> keep contour, clean stone recolor (de-speckle + clean outline; edges not redrawn).

All colours are master-palette members. Deterministic. -> tools/art_lint/candidates/round_e2/
"""
import json, os
from PIL import Image
from collections import Counter

D = "src/Presentation/assets/sprites_16bf/world_24x24"
OUT = "tools/art_lint/candidates/round_e2"
os.makedirs(OUT, exist_ok=True)
MASTER = {tuple(c) for c in json.load(open("config/art/oryx_master_palette.json"))["colors"]}

OUTLINE=(38,38,38)
# canon furniture wood ramp (chair 321 / table 319 / desk 320)
W_DARK=(56,46,0); W_MED=(87,71,0); W_MID=(136,112,0); W_LT=(184,150,0)
CL_MED=(201,201,201); CL_LT=(243,243,243)
BL_DK=(59,92,148); BL_MD=(75,117,189); BL_LT=(145,186,255)
STONE=[(81,81,81),(105,105,105),(201,201,201),(243,243,243)]

def lum(c): return 0.299*c[0]+0.587*c[1]+0.114*c[2]

def load(cid):
    im=Image.open(f"{D}/oryx_16bit_fantasy_world_{cid}.png").convert("RGBA")
    px=im.load(); w,h=im.size
    return [[px[x,y] if px[x,y][3]==255 else None for x in range(w)] for y in range(h)]

def grid_new(): return [[None]*24 for _ in range(24)]

def save(g,name):
    im=Image.new("RGBA",(24,24),(0,0,0,0)); px=im.load()
    for y in range(24):
        for x in range(24):
            if g[y][x] is not None:
                c=g[y][x]; px[x,y]=(c[0],c[1],c[2],255)
    im.save(f"{OUT}/{name}.png")
    cnt=Counter((g[y][x][0],g[y][x][1],g[y][x][2]) for y in range(24) for x in range(24) if g[y][x])
    off=[c for c in cnt if c not in MASTER]
    print(f"{name}: {len(cnt)} colours off={off if off else 'NONE'} opaque={sum(cnt.values())}")

def add_outline(g):
    out=[row[:] for row in g]
    for y in range(24):
        for x in range(24):
            if g[y][x] is None: continue
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=x+dx,y+dy
                if not(0<=nx<24 and 0<=ny<24) or g[ny][nx] is None:
                    out[y][x]=(*OUTLINE,255); break
    return out

# ---------------- BENCH: widen chair 321 (structural) --------------------------
def bench_from_chair(insert, trim):
    src=load(321)  # 24x24 rows of RGBA-or-None; chair content cols 3..20
    g=grid_new()
    # split chair interior at col 11; keep 3..11 on the left, 12..20 on the right,
    # insert `insert` duplicates of col 11 between them, centred in 24.
    left=list(range(3,12))            # 9 cols
    right=list(range(12,21))          # 9 cols
    total=len(left)+insert+len(right) # width of content
    x0=(24-total)//2
    for y in range(24):
        ox=x0
        for cx in left:
            g[y][ox]=src[y][cx][:3] if src[y][cx] else None; ox+=1
        for _ in range(insert):
            g[y][ox]=src[y][11][:3] if src[y][11] else None; ox+=1
        for cx in right:
            g[y][ox]=src[y][cx][:3] if src[y][cx] else None; ox+=1
    # lower the tall chair back so it reads as a bench/settle, not a cabinet:
    # drop the top `trim` opaque rows, then re-outline the new top edge.
    if trim:
        for y in range(trim):
            g[y]=[None]*24
    g=add_outline_keep_interior(g)
    return g

# ---------------- BED: re-dress table 319 (structural) -------------------------
def bed_from_table(blanket):
    src=load(319)
    g=[[ (src[y][x][:3] if src[y][x] else None) for x in range(24)] for y in range(24)]
    # bedding inset on the TOP surface, leaving a wood frame border; table rows 17..23
    # (front apron + legs) kept as-is = front face present.
    # pillow band (head) rows 3..6, blanket rows 7..16, cols 4..19
    for y in range(3,17):
        for x in range(4,20):
            if g[y][x] is None: continue
            if y<=6:
                g[y][x]=CL_LT if not (y==6) else CL_MED           # pillow + a shade seam
            else:
                g[y][x]=blanket[1]                                # blanket mid
    # blanket fold highlight + shadow lines
    for x in range(4,20):
        if g[8][x] is not None and 8>6: g[8][x]=blanket[2]        # highlight fold
        if g[12][x] is not None: g[12][x]=blanket[0]              # shadow fold
        if g[16][x] is not None: g[16][x]=blanket[0]              # blanket foot edge
    # dark seam framing the bedding (definition, not silhouette)
    for x in range(3,21):
        if g[2][x] is not None: g[2][x]=OUTLINE                   # headboard top seam
        if g[17][x] is not None: g[17][x]=OUTLINE                 # footboard top seam
    for y in range(3,17):
        if g[y][3] is not None: g[y][3]=OUTLINE
        if g[y][20] is not None: g[y][20]=OUTLINE
    return g

# ---------------- NIGHTSTAND: golden recolor + 5px legs -----------------------
def nightstand():
    src=load(5106)
    cols=[rgb[:3] for rgb in [src[y][x] for y in range(24) for x in range(24) if src[y][x]]]
    distinct=[c for c,_ in Counter(cols).most_common()]
    darkest=min(distinct,key=lum)
    wood=sorted([c for c in distinct if c!=darkest],key=lum)
    ramp=[W_DARK,W_MED,W_MID,W_LT]; k=len(wood)
    m={darkest:OUTLINE}
    for i,c in enumerate(wood):
        m[c]=ramp[round(i*(len(ramp)-1)/(k-1))] if k>1 else ramp[-1]
    g=[[ (m[src[y][x][:3]] if src[y][x] else None) for x in range(24)] for y in range(24)]
    # thicken legs 3px->5px: body is cols 5..18; legs currently 5..7 and 16..18 (rows 20..22).
    # extend to 5..9 and 14..18 by copying the leg colour column.
    for y in range(20,23):
        legcol=g[y][6] or W_MED
        for x in range(5,10): g[y][x]=g[y][x] or legcol
        for x in range(14,19): g[y][x]=g[y][x] or legcol
        # fill the leg interior solid wood (front face)
        for x in list(range(5,10))+list(range(14,19)):
            if g[y][x] is None: g[y][x]=W_MED
    g=add_outline_keep_interior(g)
    return g

def add_outline_keep_interior(g):
    out=[row[:] for row in g]
    for y in range(24):
        for x in range(24):
            if g[y][x] is None: continue
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=x+dx,y+dy
                if not(0<=nx<24 and 0<=ny<24) or g[ny][nx] is None:
                    out[y][x]=OUTLINE; break
    return out

# ---------------- PILLAR: keep contour, clean stone recolor -------------------
def pillar_clean(cid):
    src=load(cid)
    # 1. per-pixel luminance -> interior stone band (81/105/201), keep silhouette
    g=grid_new()
    for y in range(24):
        for x in range(24):
            if src[y][x] is None: continue
            L=lum(src[y][x][:3])
            g[y][x]= (81,81,81) if L<100 else (105,105,105) if L<150 else (201,201,201)
    # 2. de-speckle: pixel differing from >=3 of 4 opaque neighbours -> neighbour majority
    for _ in range(2):
        nxt=[row[:] for row in g]
        for y in range(24):
            for x in range(24):
                if g[y][x] is None: continue
                nb=[g[ny][nx] for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)) if 0<=nx<24 and 0<=ny<24 and g[ny][nx]]
                if nb:
                    mc,mn=Counter(nb).most_common(1)[0]
                    if mc!=g[y][x] and mn>=3: nxt[y][x]=mc
        g=nxt
    # 3. clean outline on the (unchanged) silhouette
    g=add_outline_keep_interior(g)
    return g

save(bench_from_chair(4,4),"5060_bench")
save(bench_from_chair(6,8),"5061_bench")
save(bed_from_table((BL_DK,BL_MD,BL_LT)),"5058_bed")
save(bed_from_table((W_MED,CL_MED,CL_LT)),"5059_bed")
save(nightstand(),"5106_wood")
save(nightstand(),"5107_wood")
save(pillar_clean(5093),"5093_stone")
save(pillar_clean(5094),"5094_stone")
save(pillar_clean(5094),"5095_altform")
