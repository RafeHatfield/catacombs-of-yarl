#!/usr/bin/env python3
"""THE CAP COMPOSER REBUILDS THE FAMILY IT BUILT — #209's guard, and it can fail.

    python3 tools/tier1_walls/prove_cap_reproduces.py

WHY THIS EXISTS, AND WHY IT IS THE SECOND ONE. #206 spent a session finding three faults in
`compose_walls.py`, all of the same shape — an assertion that outlived the thing it asserts — and
the only reason any of them was ever caught is that something eventually rebuilt the family and
compared. A review put the lesson plainly: **three families carried that defect and the only one
that was caught is the only one with a reproduction guard.** This is the guard the cap did not
have.

Both of #209's faults were latent. Nothing on disk was wrong, no instrument reported anything,
and no frame looked different — because nobody had recomposed the cap since the floor's ladder
grew from nine rungs to eleven.

  FAULT 1 — THE PLANE, AS AN INDEX, AND THE TRAP IS IN THE MANIFEST RATHER THAN IN THE CODE.
  The cap shipped at 88.243, which on the nine-rung ladder is index 3 — and the manifest records
  `top_rung: 3`. On the eleven-rung ladder index 3 is 61.789. Rebuilding this family THE WAY ITS
  OWN MANIFEST SAYS IT WAS BUILT drops it 26 levels. (The default code path reads
  `ARMS["material"]["top"]` = 5, which on today's ladder lands on 88.243 by accident — the ladder
  grew by exactly the two rungs that turn index 5 into what index 3 used to mean. Case B below
  mutates to the RECORDED invocation, not to the default, because the default no longer fires
  it.) Fixed by stating the plane as a RATIO of the floor's anchor (§5.7).

  FAULT 2 — THE SNAP LADDER'S BOTTOM, which survived fixing fault 1. The cap quantises softly
  onto the floor's ladder, and the ladder's lowest rung was 48.5627 when this family was laid.
  The two new rungs beneath it (35.34, 22.11) are reachable by the cracks and fractures, which
  subtract. A recompose with the plane already fixed still came back with **652 of 1024 tiles
  darker, to a maximum of 27 levels, and every delta negative** — the signature of a clip that
  stopped clipping. Fixed by flooring the snap ladder at the same 0.48 x anchor the wall family
  floors at. That the two families share a floor is not a coincidence: both were composed against
  the nine-rung ladder, and 48.5627 was its bottom.

TOLERANCE IS ONE LEVEL, for the same named reason as the wall guard: the quarry tint is derived
at consumption from the floor's own pixels, so a floor recompose legitimately moves it. A
tolerance of zero would fail every time the floor is touched. Anything larger than one level is a
fault. A deliberate change re-baselines by recomposing and re-gating — it never widens TOL.
"""
import glob
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SHIPPED = os.path.join(REPO, "src/Presentation/assets/tier1_cap")
TOL = 1


def compose(extra_env=None):
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    p = subprocess.run(["python3", os.path.join(HERE, "compose_cap.py")],
                       cwd=REPO, capture_output=True, text=True, env=env)
    return p.returncode


def worst_delta(baseline):
    worst, where, n = 0, None, 0
    for p in sorted(glob.glob(os.path.join(baseline, "*.png"))):
        q = os.path.join(SHIPPED, os.path.basename(p))
        if not os.path.exists(q):
            continue
        n += 1
        a = np.asarray(Image.open(p).convert("RGBA"), dtype=int)
        b = np.asarray(Image.open(q).convert("RGBA"), dtype=int)
        d = int(np.abs(a - b).max())
        if d > worst:
            worst, where = d, os.path.basename(p)
    return worst, where, n


def main():
    print("PROVE — the cap composer reproduces its family (#209). tolerance %d level(s)\n" % TOL)
    with tempfile.TemporaryDirectory() as tmp:
        baseline = os.path.join(tmp, "cap")
        os.makedirs(baseline)
        for p in glob.glob(os.path.join(SHIPPED, "*.png")):
            Image.open(p).save(os.path.join(baseline, os.path.basename(p)))
        print("  baseline: %d shipped tiles copied aside\n" % len(os.listdir(baseline)))

        cases = [("A  the composer as it stands", True, None),
                 ("B  rebuilt from the manifest", False, {"YARL_CAP_PROVE": "record"}),
                 ("C  the snap ladder unfloored", False, {"YARL_CAP_PROVE": "unfloored"})]
        fails = 0
        for name, expect_pass, env in cases:
            if compose(env) != 0:
                print("  %-30s COMPOSE FAILED" % name)
                fails += 1
                continue
            d, where, n = worst_delta(baseline)
            passed = d <= TOL
            ok = (passed == expect_pass)
            fails += 0 if ok else 1
            print("  %-30s worst delta %3d (%s, %d tiles)  ->  %-4s  %s"
                  % (name, d, where or "-", n, "PASS" if passed else "FAIL",
                     "ok" if ok else "*** UNEXPECTED ***"))

        # leave the tree as we found it
        compose(None)
        for p in glob.glob(os.path.join(baseline, "*.png")):
            Image.open(p).save(os.path.join(SHIPPED, os.path.basename(p)))

    print("\n%s  (%d cases)" % ("ALL AS EXPECTED" if not fails else "%d UNEXPECTED" % fails,
                                len(cases)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
