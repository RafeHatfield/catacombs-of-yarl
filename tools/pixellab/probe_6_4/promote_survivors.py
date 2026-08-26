#!/usr/bin/env python3
"""§6.4 probe — promote the STOP 1 survivors Rafe picked. Copies files; decides nothing.

RULED (Rafe, STOP 1, 2026-08-25). Four survivors, taken from the floor sheets **as one pool**:
arm labels were treated as carrying no lighting information, which follows directly from the
Stage 1 finding that the three arms are indistinguishable on the lighting axis. The pick codes
and their arm-of-origin are recorded anyway — the arms may yet turn out to differ somewhere
this probe has not looked, and discarding the provenance would make that unrecoverable.

**Wall sheets: zero picks.** The 1-usable-in-60 finding stands. Walls route to the micro-probe.

Every promoted file is stamped `PROBE REFERENCE — NOT RATIFIED` in its manifest. These are
reference DNA for conditioning. They are not game candidates, they are not approved, and they
do not land — §13.1 governs landing and is not satisfied by anything that happened at STOP 1.
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE1 = os.path.join(HERE, "stage1")
OUT = os.path.join(HERE, "survivors")

# code -> (arm of origin, source path). RULED at STOP 1; this seat picked none of them.
PICKS = [
    ("A-VAB", "A", "A/floor/A_floor_17.png"),
    ("A-HEB", "A", "A/floor/A_floor_16.png"),
    ("B-KAB", "B", "B/floor/B_floor_18.png"),
    ("C-GAB", "C", "C/floor/C_floor_16.png"),
]
# Named by Rafe as the two strongest; the conditioning smoke test uses exactly these.
STRONGEST = ("A-VAB", "C-GAB")


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {
        "status": "PROBE REFERENCE — NOT RATIFIED",
        "ruled_by": "Rafe, STOP 1, 2026-08-25",
        "pooled": ("floor sheets curated as ONE pool; arm labels treated as carrying no "
                   "lighting information, per the Stage 1 positive-control failure"),
        "wall_picks": ("NONE — the 1-usable-in-60 finding stands; walls route to the "
                       "micro-probe"),
        "landing": ("These never land. §13.1 governs landing and STOP 1 does not satisfy it. "
                    "They exist to condition Stage 2 generations and for nothing else."),
        "survivors": [],
    }
    for code, arm, rel in PICKS:
        src = os.path.join(STAGE1, rel)
        raw = open(src, "rb").read()
        dst_rel = "%s.png" % code
        shutil.copy2(src, os.path.join(OUT, dst_rel))
        manifest["survivors"].append({
            "code": code, "arm_of_origin": arm, "file": dst_rel,
            "stage1_source": rel, "sha256": hashlib.sha256(raw).hexdigest(),
            "size": [32, 32],
            "strongest": code in STRONGEST,
        })
        print("promoted %-6s <- %-28s %s" % (code, rel, "(strongest)" if code in STRONGEST else ""))

    with open(os.path.join(OUT, "MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print("\n%d survivors -> %s" % (len(PICKS), OUT))
    print("status: PROBE REFERENCE — NOT RATIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
