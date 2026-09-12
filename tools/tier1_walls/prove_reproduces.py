#!/usr/bin/env python3
"""THE COMPOSER REBUILDS THE FAMILY IT BUILT — #206's guard, and it demonstrates it can fail.

    python3 tools/tier1_walls/prove_reproduces.py

WHY THIS EXISTS. #206 was *"the wall composer does not reproduce its own family"*, and it went
unseen for two milestones for one reason: **nothing ever recomposed and compared.** Three separate
faults had accumulated in the composer, each invisible on its own, each shipped:

  1. THE LADDER DRIFT (§5.7). The arms were index constants on a nine-rung ladder. The floor's
     ladder grew to eleven at the bottom and the indices kept their numbers while their meaning
     moved two rungs down — a whole plane 26 levels dark. Fixed by stating the arms as RATIOS.

  2. THE INDEX-0 CLIP, which is fault 1 one layer down and survived its fix. A joint is written
     `rung(face, -3)` and a block's value break as offsets of -2..+2, and `rung()` clipped at
     index 0. On the nine-rung ladder the face sat at rung 1, so the joint AND the darkest blocks
     all piled onto 48.5627 — one value where three were authored. On the eleven-rung ladder they
     separate and the face went 3-8.6 levels light across all 108 face tiles. Fixed by clipping at
     FLOOR_RATIO's rung, which is a value and is stable under field size.

  3. A DELETED FEATURE WITH ITS DOCUMENTATION LEFT BEHIND. The occlusion lip — the turn between
     the planes, `min(lip*0.55, rung(face,-2))` — went out in bceb7446 when face tiles became
     face-only RGBA. The paragraph describing it stayed. The manifest's `occlusion_rows: 2` stayed.
     So the composer went on ADVERTISING a 22-level band it no longer painted, on every face tile.

The common shape: **an assertion that outlived the thing it asserts** (§13.12). The only instrument
that catches that class is one that rebuilds and compares, so this is it.

A DELIBERATE CHANGE RE-BASELINES; IT DOES NOT LOWER THE BAR. This guard's reference is the
family on disk, so case A fails the moment the composer is asked to draw something new - as it did
when #202's worn arris went in. That failure is the guard working: a look change has to be
recomposed, shipped and taken through the gate, and case A passes again against the bytes the gate
saw. What it must never mean is widening TOL to make a change quiet.

TOLERANCE IS ONE LEVEL, AND THE REASON IS NAMED. The quarry tint is derived AT CONSUMPTION from
the floor's own tile pixels (`derive_quarry_tint`), so a floor recompose legitimately moves it: it
has drifted 0.82575 -> 0.820778 in blue since the walls were laid, which is -1 level on the blue
channel of about a sixth of the pixels. That is the same-quarry law working, not a defect, and a
tolerance of 0 would fail on it every time the floor is touched. Anything larger than one level is
a fault. §13.5: the FAIL cases below prove this bar can be reached from the wrong side.
"""
import os
import sys
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import compose_walls as CW  # noqa: E402

SHIPPED = os.path.join(REPO, CW.ASSETS_REL)
TOL = 1                       # levels; see the tolerance note in the docstring
GRAIN_AMP = 1.0


def _family():
    import json
    import compose_ashlar as CA
    import compose_family as CF
    import derive_quarry_tint as QT
    floor = json.load(open(os.path.join(CA.ASSETS, "MANIFEST.json")))
    mat = dict(floor["material"])
    CF.rehydrate(mat)
    quarry, _, _, _ = QT.derive()
    return CW.Family("material", mat["ladder"], quarry, None)


def worst_delta():
    """Recompose every tile in memory and return (max level delta, tile id, n tiles)."""
    fam = _family()
    worst, where, n = 0, None, 0
    for cls, base in (("face", CW.IDS["face"]), ("top_h", CW.IDS["top_h"]),
                      ("top_v", CW.IDS["top_v"])):
        i = 0
        ages = range(CW.AGES) if cls == "face" else (0,)
        for ka in range(CW.EDGE_FAMILIES):
            for kb in range(CW.EDGE_FAMILIES):
                for var in range(CW.VARIANTS):
                    for age in ages:
                        img = fam.tile(cls, dict(w=ka, e=kb, n=0), GRAIN_AMP, var, age)
                        got = fam.rgb(img, face_only=(cls == "face"))
                        tid = base + i
                        i += 1
                        p = os.path.join(SHIPPED, "tier1_wall_%d.png" % tid)
                        if not os.path.exists(p):
                            continue
                        n += 1
                        mode = "RGBA" if cls == "face" else "RGB"
                        ref = np.asarray(Image.open(p).convert(mode), dtype=int)
                        d = int(np.abs(ref - np.asarray(got, dtype=int)[..., :ref.shape[2]]).max())
                        if d > worst:
                            worst, where = d, tid
    return worst, where, n


CASES = []


def case(name, expect_pass, mutate, why):
    CASES.append((name, expect_pass, mutate, why))


def _noop():
    return lambda: None


def _clip_at_zero():
    """Fault 2: the clip that shipped, restored."""
    orig = CW.Family.rung

    def rung(self, base_index, offset):
        i = int(np.clip(base_index + offset, 0, len(self.ladder) - 1))
        return self.ladder[i]
    CW.Family.rung = rung
    return lambda: setattr(CW.Family, "rung", orig)


def _delete_lip():
    """Fault 3: the occlusion lip removed again."""
    orig = CW.OCCLUSION_ROWS
    CW.OCCLUSION_ROWS = 0
    return lambda: setattr(CW, "OCCLUSION_ROWS", orig)


def _index_arms():
    """Fault 1: the arms back to indices on a ladder that has since grown."""
    orig = dict(CW.ARMS["material"])
    CW.ARMS["material"] = dict(top=5, face=1, why="index arms, the pre-#206 state")
    return lambda: CW.ARMS.__setitem__("material", orig)


def _floor_ratio_drift():
    """The floor stated as an index again, by moving its ratio off the family's darkest value."""
    orig = CW.FLOOR_RATIO
    CW.FLOOR_RATIO = 0.22
    return lambda: setattr(CW, "FLOOR_RATIO", orig)


case("A  the composer as it stands", True, _noop, "must rebuild the shipped family")
case("B  index-0 clip restored", False, _clip_at_zero,
     "fault 2 — joint and dark blocks separate where the family collapsed them")
case("C  occlusion lip deleted", False, _delete_lip,
     "fault 3 — rows 16-17 lose a 22-level band")
case("D  arms back to indices", False, _index_arms,
     "fault 1 — the planes move two rungs down")
case("E  family floor moved off its value", False, _floor_ratio_drift,
     "the floor is an anchor; moving it must be caught")


def main():
    print("PROVE — the wall composer reproduces its family (#206). tolerance %d level(s)\n" % TOL)
    fails = 0
    for name, expect_pass, mutate, why in CASES:
        undo = mutate()
        try:
            d, tid, n = worst_delta()
        finally:
            undo()
        passed = d <= TOL
        ok = (passed == expect_pass)
        fails += 0 if ok else 1
        print("  %-30s worst delta %3d (tile %s, %d tiles)  ->  %-4s  %s" % (
            name, d, tid, n, "PASS" if passed else "FAIL", "ok" if ok else "*** UNEXPECTED ***"))
        if not ok:
            print("       expected %s: %s" % ("PASS" if expect_pass else "FAIL", why))
    print("\n%s  (%d case%s)" % ("ALL AS EXPECTED" if not fails else "%d UNEXPECTED" % fails,
                                 len(CASES), "" if len(CASES) == 1 else "s"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
