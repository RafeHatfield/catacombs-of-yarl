import os, sys, json
os.chdir("/Users/rafehatfield/development/c-yarl/.claude/worktrees/tier1-floors")
sys.path.insert(0, os.path.abspath("tools/tier1_floors"))
import numpy as np, compose_ashlar as CA, field_ashlar as FA
man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json"))); mat = man["material"]
T = CA.T; N = 12
traffic = np.zeros((N, N), dtype=np.uint8); traffic[N//2-1:N//2+1, :] = 255
from numpy.lib.stride_tricks import sliding_window_view
def ratio(dk):
    keep = CA.DRESSING_KEEP
    CA.DRESSING_KEEP = dk
    try:
        img, j, _, c, d = FA.assemble(N, N, 1337, mat, None, traffic=traffic)
    finally:
        CA.DRESSING_KEEP = keep
    L = np.asarray(img).astype(float)[..., 0]
    sd = sliding_window_view(L, (3, 3)).std(axis=(2, 3))
    hot = np.zeros(L.shape, bool); cold = np.zeros(L.shape, bool)
    hot[:, (N//2-1)*T:(N//2+1)*T] = True
    cold[:, 0:2*T] = True
    return sd[hot[1:-1,1:-1]].mean(), sd[cold[1:-1,1:-1]].mean()
print("HOW DEEP MUST THE MODULATION BE BEFORE A TRODDEN STONE LOOKS TRODDEN?\n")
print("  %-22s %9s %9s %8s" % ("dressing lost at wear=1", "trodden", "off-route", "ratio"))
for dk in (0.45, 0.65, 0.80, 0.90, 1.00):
    h, c = ratio(dk)
    print("  %-22.2f %9.3f %9.3f %8.3f" % (dk, h, c, h/c))
print("\n  0.45 is the shipped value: a fully trodden stone still keeps 55% of its dressing.")
print("  1.00 means a fully trodden stone is bare — polished smooth, as the ruling describes.")
