import os, sys
os.chdir("/Users/rafehatfield/development/c-yarl/.claude/worktrees/tier1-floors")
sys.path.insert(0, os.path.abspath("tools/tier1_floors"))
import numpy as np
from PIL import Image

def lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

a = np.asarray(Image.open("tools/tier1_floors/evidence/scene_ashlar_r7.png").convert("RGB")).astype(float)
b = np.asarray(Image.open("/Users/rafehatfield/.claude/jobs/b976c466/tmp/no_overlays.png").convert("RGB")).astype(float)
sl = (slice(400, 1000), slice(0, 750))
A, B = lum(a)[sl], lum(b)[sl]
d = np.abs(A - B)
lit = B > 40
print("WHAT THE INCIDENT OVERLAYS ACTUALLY ADD, in the lit ground:")
print("  pixels changed at all        : %.2f%%" % (100.0 * (d[lit] > 0.5).mean()))
print("  changed by >= 1 ladder step  : %.2f%%   (step 13.23)" % (100.0 * (d[lit] >= 13.23).mean()))
print("  changed by >= 2 ladder steps : %.2f%%" % (100.0 * (d[lit] >= 26.5).mean()))
ch = d[lit][d[lit] > 0.5]
print("  mean delta where changed     : %.2f luminance" % (ch.mean() if ch.size else 0))
print("  max delta                    : %.1f" % d[lit].max())

m = ((d > 13.23) & lit).astype(np.uint8)
H, W = m.shape
lab = np.zeros((H, W), int); nxt = 0; sizes = []
for y in range(H):
    for x in range(W):
        if not m[y, x] or lab[y, x]:
            continue
        nxt += 1; st = [(y, x)]; lab[y, x] = nxt; n = 0
        while st:
            yy, xx = st.pop(); n += 1
            for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
                ny, nx = yy+dy, xx+dx
                if 0 <= ny < H and 0 <= nx < W and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = nxt; st.append((ny, nx))
        sizes.append(n)
sizes.sort(reverse=True)
print("  marks of >=1 step: %d, largest %dpx, median %dpx, over 20px: %d"
      % (len(sizes), sizes[0] if sizes else 0,
         int(np.median(sizes)) if sizes else 0, sum(1 for s in sizes if s >= 20)))
