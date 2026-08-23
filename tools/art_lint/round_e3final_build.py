#!/usr/bin/env python3
"""Round E3-final — two new depths props (candidates only, not landed).

bone_pile (5115): canon bone GRAMMAR (grey-white ramp from tile 96 / prop 612 / creature 291
  + skull/long-bone components), TARGET silhouette = a low mounded ossuary heap, two-plane
  (lit top surface + shaded front face), names itself at 1x via skulls.
flood_marker (5116): canon fountain water ramp deepened to a true-blue (non-teal) region;
  fills the cell as a deep pool (distinct from the small teal puddle 5110). Water = decal class
  (flat top plane, outline-exempt, per bible s6 — same as puddle/moss).

All colours master-palette members. Deterministic. -> tools/art_lint/candidates/round_e3final/
"""
import json, os, math
from PIL import Image
from collections import Counter

OUT="tools/art_lint/candidates/round_e3final"; os.makedirs(OUT,exist_ok=True)
MASTER={tuple(c) for c in json.load(open("config/art/oryx_master_palette.json"))["colors"]}
OUTLINE=(38,38,38)
# bone grey-white ramp (canon)
B_DK=(105,105,105); B_MED=(145,145,145); B_MID=(196,196,196); B_LT=(201,201,201); B_HI=(243,243,243)
# deep true-blue water (master palette; deeper/cooler than fountain, no teal)
W_DEEP=(0,47,118); W_BODY=(12,89,145); W_MID=(56,96,168); W_HI=(112,176,240)

def new(): return [[None]*24 for _ in range(24)]
def save(g,name):
    im=Image.new("RGBA",(24,24),(0,0,0,0)); px=im.load()
    for y in range(24):
        for x in range(24):
            if g[y][x]: px[x,y]=(*g[y][x],255)
    im.save(f"{OUT}/{name}.png")
    c=Counter(g[y][x] for y in range(24) for x in range(24) if g[y][x])
    off=[k for k in c if k not in MASTER]
    print(f"{name}: {len(c)}c off={off if off else 'NONE'} opaque={sum(c.values())}")
def outline(g):
    o=[r[:] for r in g]
    for y in range(24):
        for x in range(24):
            if g[y][x] is None: continue
            for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                nx,ny=x+dx,y+dy
                if not(0<=nx<24 and 0<=ny<24) or g[ny][nx] is None: o[y][x]=OUTLINE;break
    return o
def px(g,x,y,c):
    if 0<=x<24 and 0<=y<24: g[y][x]=c

# ---------------- BONE PILE (built from visible, outlined bone components) --------
def filled_circle(g,cx,cy,r,c):
    for y in range(cy-r,cy+r+1):
        for x in range(cx-r,cx+r+1):
            if (x-cx)**2+(y-cy)**2<=r*r+1: px(g,x,y,c)
def skull(g,cx,cy,r):
    # cranium dome (top-lit), big dark eye sockets, jaw notch, dark outline ring
    filled_circle(g,cx,cy,r,B_HI)
    for y in range(cy-r,cy+r+1):
        for x in range(cx-r,cx+r+1):
            if g[y][x]==B_HI and (y-cy)>r-2: g[y][x]=B_MID   # shade lower cranium
    # eye sockets (2x2 each)
    for ex in (cx-1,cx+1):
        for dy in (0,1):
            px(g,ex,cy+ (0 if ex<cx else 0),OUTLINE)
    for dx,dy in [(-2,0),(-2,1),(-1,0),(-1,1),(1,0),(1,1),(2,0),(2,1)]:
        px(g,cx+dx,cy+dy,OUTLINE)                              # two 2x2 sockets
    px(g,cx,cy+2,OUTLINE)                                      # nasal
    # jaw (a couple teeth rows below)
    for dx in range(-2,3):
        px(g,cx+dx,cy+r,B_LT)
    px(g,cx-1,cy+r+1,B_LT); px(g,cx+1,cy+r+1,B_LT)
def long_bone(g,x0,y0,x1,y1):
    steps=max(abs(x1-x0),abs(y1-y0),1)
    for i in range(steps+1):
        xx=round(x0+(x1-x0)*i/steps); yy=round(y0+(y1-y0)*i/steps)
        for dx,dy in [(0,0),(1,0),(0,1)]: px(g,xx+dx,yy+dy,B_HI)   # thick shaft
    for (kx,ky) in [(x0,y0),(x1,y1)]:                              # knobbed ends
        filled_circle(g,kx,ky,1,B_HI)
def bone_pile():
    g=new()
    # ground-contact shadow ellipse (reads the heap sitting on the floor)
    for x in range(3,21):
        for y in range(18,21):
            if (x-11.5)**2/72 + (y-19)**2/3.5 <= 1: px(g,x,y,B_DK)
    # long bones jumbled through the heap (asymmetric -> reads as a pile, not an emblem)
    long_bone(g,4,18,17,10)
    long_bone(g,6,10,20,15)
    long_bone(g,3,14,11,12)
    # base fragments (widen the mound at the floor)
    long_bone(g,5,19,10,19); long_bone(g,13,19,18,18)
    # two skulls nestled at different heights (name it at 1x)
    skull(g,9,16,4)
    skull(g,16,13,3)
    g=outline(g)
    return g

# ---------------- FLOOD MARKER (full-cell deep-water region) ----------------------
def flood_marker():
    g=new()
    # fill the whole cell with water (a REGION, not a centred blob) with a slightly
    # irregular shoreline at the very corners so it doesn't read as a hard rectangle.
    cx,cy=11.5,11.5
    for y in range(24):
        for x in range(24):
            r=math.hypot((x-cx)/13.0,(y-cy)/13.0)
            wob=0.10*math.sin(x*1.7)+0.10*math.cos(y*1.5)
            if r+wob<1.06:
                depth=0.35 + (11.5-abs(y-14))/24 + (1-r)*0.5   # deeper centre/lower
                g[y][x]= W_DEEP if depth>0.85 else W_BODY if depth>0.55 else W_MID
    # surface ripples (broken horizontal highlight dashes)
    for (y,xs) in [(4,range(5,11)),(7,range(13,20)),(11,range(4,10)),(14,range(13,21)),(18,range(6,14))]:
        for x in xs:
            if g[y][x] is not None and (x//2)%2==0: g[y][x]=W_HI
    # deep-water shoreline band (darkest at the edge → reads as depth, a pool not a spill)
    o=[r[:] for r in g]
    for y in range(24):
        for x in range(24):
            if g[y][x] is None: continue
            if any(not(0<=x+dx<24 and 0<=y+dy<24) or g[y+dy][x+dx] is None
                   for dx,dy in((1,0),(-1,0),(0,1),(0,-1))):
                if g[y][x]!=W_HI: o[y][x]=W_DEEP
    return o   # water is decal-class: no black outline (bible s6)

save(bone_pile(),"5115_bone_pile")
save(flood_marker(),"5116_flood_marker")
