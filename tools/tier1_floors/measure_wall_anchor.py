import os, sys, json
os.chdir("/Users/rafehatfield/development/c-yarl/.claude/worktrees/tier1-floors")
sys.path.insert(0, os.path.abspath("tools/tier1_floors"))
import numpy as np, compose_ashlar as CA, field_ashlar as FA
man = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json"))); mat = man["material"]
T = CA.T; N = 16
ladder = np.array(mat["ladder"])
img, joints, _, cracks, dress = FA.assemble(N, N, 1337, mat, None)
L = np.asarray(img).astype(float)[..., 0] / mat["tint"][0]

print("THE LANDED FLOOR'S ANCHOR — measured on the family as it now stands, unlit.\n")
face_only = ~(joints | cracks)
print("  whole floor median          : %.2f" % np.median(L))
print("  stone faces only, median    : %.2f" % np.median(L[face_only]))
print("  session two recorded anchor : 114.50")
anchor = float(np.median(L))
print()
print("  ladder: %s" % [round(v,1) for v in ladder])
print()
print("§6.5's stack, derived from THIS floor rather than from the old anchor:\n")
for name, ratio in (("wall top", 1.11), ("floor", 1.00), ("wall face (0.60)", 0.60),
                    ("wall face (0.50)", 0.50)):
    v = anchor * ratio
    on = ladder[np.abs(ladder - v).argmin()]
    inside = ladder[0] - 1e-6 <= v <= ladder[-1] + 1e-6
    print("  %-18s %6.2f   nearest rung %6.2f   %s"
          % (name, v, on, "on the ladder" if inside else "*** BELOW THE LADDER'S FLOOR ***"))
print()
print("  The floor's ladder spans %.1f..%.1f. It was derived for FLOOR material only."
      % (ladder[0], ladder[-1]))
