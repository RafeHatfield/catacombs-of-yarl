import os
os.chdir("/Users/rafehatfield/development/c-yarl/.claude/worktrees/tier1-floors")
import numpy as np
from PIL import Image
a = np.asarray(Image.open("tools/tier1_floors/evidence/scene_ashlar_r8.png").convert("RGB")).astype(int)
sl = (slice(400, 1000), slice(0, 750))
A = a[sl]
H, W, _ = A.shape
# The art is authored at 32px tiles drawn at tile_scale 2.0, so every ART pixel should be a 2x2
# block of identical SCREEN pixels. Measure how often it isn't.
h2, w2 = (H // 2) * 2, (W // 2) * 2
B = A[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2, 3)
same = (B.max(axis=(1, 3)) == B.min(axis=(1, 3))).all(axis=-1)
print("2x2 blocks that are a single flat colour : %.2f%%" % (100.0 * same.mean()))
d = B.max(axis=(1, 3)).astype(int) - B.min(axis=(1, 3)).astype(int)
print("mean spread inside a 2x2 block           : %.2f  (max %d)" % (d.mean(), d.max()))
lit = A[..., 0][:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2).mean(axis=(1, 3)) > 40
print("  ... restricted to lit ground           : %.2f%% flat, mean spread %.2f"
      % (100.0 * same[lit].mean(), d[lit].mean()))
# How many distinct luminances does the LIT floor actually contain?
L = (0.299 * A[..., 0] + 0.587 * A[..., 1] + 0.114 * A[..., 2])
m = L > 40
print("distinct luminance values in the lit ground: %d  (the family's ladder has 7 rungs)"
      % len(np.unique(np.round(L[m], 1))))
