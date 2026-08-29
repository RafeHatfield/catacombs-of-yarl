import os, sys, json
os.chdir("/Users/rafehatfield/development/c-yarl/.claude/worktrees/tier1-floors")
sys.path.insert(0, os.path.abspath("tools/tier1_floors"))
import numpy as np, compose_ashlar as CA, field_ashlar as FA
man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json"))); mat = man["material"]
img, joints, _, cracks = FA.assemble(8, 8, 1337, mat, None)

# How many times does a crack meet a BED joint? The seat counted 138 identical wedges, every one
# "hugging the joint line", in ten horizontal ribbons — which is what a 1px crack crossing a 2px
# bed line looks like, over and over, because neither ever deflects.
bed = np.zeros_like(joints)
rows = np.where(joints.mean(axis=1) > 0.8)[0]
bed[rows, :] = True
touch = np.zeros_like(cracks)
for dy in (-1, 0, 1):
    for dx in (-1, 0, 1):
        touch |= np.roll(np.roll(bed, dy, 0), dx, 1)
junc = cracks & touch
# connected components of the junctions
H, W = junc.shape
lab = np.zeros((H, W), int); n = 0; sizes = []
for sy in range(H):
    for sx in range(W):
        if not junc[sy, sx] or lab[sy, sx]:
            continue
        n += 1; st = [(sy, sx)]; lab[sy, sx] = n; c = 0
        while st:
            yy, xx = st.pop(); c += 1
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = yy+dy, xx+dx
                    if 0 <= ny < H and 0 <= nx < W and junc[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n; st.append((ny, nx))
        sizes.append(c)
print("crack-meets-bed-joint junctions in an 8x8 field: %d" % n)
print("  their sizes: %s" % sorted(sizes)[:14])
print("  the seat counted 138 identical wedges in a 14x13-cell room")
print("  scaled to that room: ~%d" % int(round(n * (14*13) / 64.0)))
