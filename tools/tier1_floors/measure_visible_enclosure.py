import os, sys, json
os.chdir("/Users/rafehatfield/development/c-yarl/.claude/worktrees/tier1-floors")
sys.path.insert(0, os.path.abspath("tools/tier1_floors"))
import numpy as np, compose_ashlar as CA, field_ashlar as FA
man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json"))); mat = man["material"]
T = CA.T; N = 12
traffic = np.zeros((N, N), dtype=np.uint8); traffic[N//2-1:N//2+1, :] = 255

def visible_enclosure(traffic):
    """Session one's own metric, applied to the RENDERED image rather than to the bond.

    The bond is untouched by the joint lever — the class mask still divides every stone, so every
    stone keeps its address. What changes is how much of the bond you can SEE. Filling a joint
    level with the floor is the point of the lever, and it necessarily merges the stones either
    side of it visually. The question this answers is how far that goes before the floor stops
    showing stones at all, which is session one's terminal finding:
    'joints enclose nothing - 99.1% of the floor is one connected region'.
    """
    img, joints, _, cracks, dress = FA.assemble(N, N, 1337, mat, None, traffic=traffic)
    L = np.asarray(img).astype(int)[..., 0]
    # a pixel is "joint-like" if it is markedly darker than the local stone
    dark = L < (np.median(L) - 6)
    H, W = L.shape
    lab = np.zeros((H, W), int); n = 0; sizes = []
    for sy in range(H):
        for sx in range(W):
            if dark[sy, sx] or lab[sy, sx]: continue
            n += 1; st = [(sy, sx)]; lab[sy, sx] = n; c = 0
            while st:
                yy, xx = st.pop(); c += 1
                for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
                    ny, nx = yy+dy, xx+dx
                    if 0 <= ny < H and 0 <= nx < W and not dark[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n; st.append((ny, nx))
            sizes.append(c)
    tot = (~dark).sum()
    return len(sizes), max(sizes)/tot

print("VISIBLE enclosure — the bond is untouched; this is what the eye can still separate.\n")
for label, tf in (("no traffic (all off-route)", np.zeros((N, N), dtype=np.uint8)),
                  ("with the spine", traffic)):
    n, share = visible_enclosure(tf)
    print("  %-28s %5d visible regions, largest holds %.1f%%" % (label, n, 100*share))
print("\n  session one's terminal finding was a largest region of 99.1%.")
