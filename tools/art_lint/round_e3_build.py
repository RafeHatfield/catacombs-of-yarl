#!/usr/bin/env python3
"""Round E3 — target-silhouette-led structural rebuilds + sack recolor (candidates only).

Per Round E2 verdicts + the grammar/silhouette refinement:
  bench  <- chair 321 GRAMMAR (wood ramp, 5px legs, seat top+front planes), TARGET silhouette:
            backless wide seat + legs (back removed entirely).
  bed    <- table 319 GRAMMAR (wood ramp, outline), TARGET signature features lead: blanket
            dominating the top plane (~70%+) + pillow band at the head + frame reduced to
            headboard/footboard edges (no apron).
  sack   -> recolor only (one lever): canon burlap/tan ramp (crate/barrel family 267/268),
            shape untouched.
All colours master-palette members. Deterministic. -> tools/art_lint/candidates/round_e3/
"""
import json, os
from PIL import Image
from collections import Counter

D="src/Presentation/assets/sprites_16bf/world_24x24"
OUT="tools/art_lint/candidates/round_e3"; os.makedirs(OUT,exist_ok=True)
MASTER={tuple(c) for c in json.load(open("config/art/oryx_master_palette.json"))["colors"]}

OUTLINE=(38,38,38)
W_DARK=(56,46,0); W_MED=(87,71,0); W_MID=(136,112,0); W_LT=(184,150,0)     # canon 319/321 wood
CL_MED=(201,201,201); CL_LT=(243,243,243)
BL_DK=(59,92,148); BL_MD=(75,117,189); BL_LT=(145,186,255)
BURLAP=[(71,52,23),(105,63,0),(150,90,0),(191,115,0)]                       # canon crate/barrel

def lum(c): return 0.299*c[0]+0.587*c[1]+0.114*c[2]
def load(cid):
    im=Image.open(f"{D}/oryx_16bit_fantasy_world_{cid}.png").convert("RGBA"); px=im.load()
    return [[px[x,y] if px[x,y][3]==255 else None for x in range(24)] for y in range(24)]
def new(): return [[None]*24 for _ in range(24)]
def outline(g):
    o=[r[:] for r in g]
    for y in range(24):
        for x in range(24):
            if g[y][x] is None: continue
            for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=x+dx,y+dy
                if not(0<=nx<24 and 0<=ny<24) or g[ny][nx] is None: o[y][x]=OUTLINE;break
    return o
def save(g,name):
    im=Image.new("RGBA",(24,24),(0,0,0,0)); px=im.load()
    for y in range(24):
        for x in range(24):
            if g[y][x]: px[x,y]=(*g[y][x],255)
    im.save(f"{OUT}/{name}.png")
    c=Counter(g[y][x] for y in range(24) for x in range(24) if g[y][x])
    off=[k for k in c if k not in MASTER]
    print(f"{name}: {len(c)}c off={off if off else 'NONE'} opaque={sum(c.values())}")

def rect(g,x0,y0,x1,y1,c):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            if 0<=x<24 and 0<=y<24: g[y][x]=c

# ---- BENCH: chair 321 seat+legs (rows 13..23), back removed, widened, shifted up ----
def bench_backless(insert=4, shift=3):
    src=load(321)
    g=new()
    left=list(range(3,12)); right=list(range(12,21)); total=len(left)+insert+len(right)
    x0=(24-total)//2
    for y in range(13,24):                 # seat (13-18) + legs (19-22) + outline (23)
        ny=y-13+ (13-shift-0)              # place block starting near row (13-shift)... compute below
    # simpler: build widened block for rows 13..23, then blit shifted up by `shift`
    block={}
    for y in range(13,24):
        row=[];
        for cx in left: row.append(src[y][cx][:3] if src[y][cx] else None)
        for _ in range(insert): row.append(src[y][11][:3] if src[y][11] else None)
        for cx in right: row.append(src[y][cx][:3] if src[y][cx] else None)
        block[y]=row
    for y in range(13,24):
        ty=y-shift
        if 0<=ty<24:
            for i,c in enumerate(block[y]):
                if c is not None: g[ty][x0+i]=c
    g=outline(g)
    return g

# ---- BED: target signature features lead (blanket-dominant), 319 grammar ----
def bed(blanket):
    g=new()
    # headboard edge (thin wood) at the head
    rect(g,3,1,20,2,W_MID)
    # pillow band at the head
    rect(g,4,3,19,6,CL_LT); rect(g,4,6,19,6,CL_MED)
    # blanket dominates the top plane (rows 7..18)
    rect(g,3,7,20,18,blanket[1])
    rect(g,3,8,20,8,blanket[2])            # highlight fold
    rect(g,3,12,20,12,blanket[0])          # shadow fold
    rect(g,3,15,20,15,blanket[0])          # shadow fold
    rect(g,3,18,20,18,blanket[0])          # blanket foot edge
    # footboard FRONT FACE (thin, darker wood -> reads as front plane, not apron)
    rect(g,3,19,20,20,W_MED)
    rect(g,3,19,20,19,W_MID)               # a lit top lip on the footboard
    # short legs
    rect(g,4,21,6,22,W_MED); rect(g,17,21,19,22,W_MED)
    g=outline(g)
    return g

# ---- SACK: recolor only to canon burlap ramp, shape untouched ----
def sack_recolor():
    src=load(5102)
    cols=[src[y][x][:3] for y in range(24) for x in range(24) if src[y][x]]
    distinct=[c for c,_ in Counter(cols).most_common()]
    darkest=min(distinct,key=lum)
    body=sorted([c for c in distinct if c!=darkest],key=lum)
    k=len(body); m={darkest:OUTLINE}
    for i,c in enumerate(body):
        m[c]=BURLAP[round(i*(len(BURLAP)-1)/(k-1))] if k>1 else BURLAP[-1]
    g=[[ (m[src[y][x][:3]] if src[y][x] else None) for x in range(24)] for y in range(24)]
    return g

save(bench_backless(4,3),"5060_bench")
save(bench_backless(4,3),"5061_bench")
save(bed((BL_DK,BL_MD,BL_LT)),"5058_bed")
save(bed((W_MED,CL_MED,CL_LT)),"5059_bed")
save(sack_recolor(),"5102_sack")
