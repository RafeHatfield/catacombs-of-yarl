#!/usr/bin/env python3
"""SURVIVOR-FLOOR RING REMEDIATION — real corpus work, replacing the instrument-only MOCK.

WHAT THIS IS AND WHAT IT REPLACES
---------------------------------
`tools/composition_spike/dering_floors.py` derived a MOCK floor for instrument use, explicitly
refused to correct the corpus, and sent the finding to the gate intact. That was the right call
for a session whose subject was walls. This module does the corpus work the finding asked for.

REFUSALS, STATED BEFORE ANYTHING IS WRITTEN
-------------------------------------------
  * It does NOT touch the originals. `tools/pixellab/probe_6_4/survivors/` is read-only to this
    module and every output is a NEW file carrying its parent's sha256.
  * It does NOT promote. §13.1 governs landing and nothing here satisfies it. The remediated set
    is a candidate set; the blind seat gates it and Rafe's eye rules on it.
  * It invents no colour. Every output pixel is a colour its own parent already contained, and
    an assertion enforces it rather than a comment claiming it.

THE ROUTE IS CHOSEN PER TILE, BY MEASUREMENT
--------------------------------------------
Bible §12 requires "value separation from the surface beneath". A ring drawn around a plate is
one way to get separation and it is the banned way; a plate that is genuinely a different value
from its ground is the sanctioned way. So the question that decides surgery vs regeneration is
measurable and narrow:

    STRIP THE RING. Does the plate still separate from its ground by value?

  * YES -> SURGERY. The ring was redundant with a separation the tile already had. Removing it
    removes a keyline and nothing else.
  * NO  -> REGENERATION. The ring was the ONLY thing making the plate read, so stripping it
    does not de-ring the tile, it deletes the tile. Regenerate by conditioning on the survivor
    itself (`regenerate.py`) and verify the child is ring-free.

This is not a character score and must not be read as one. It measures one specific mechanism -
the one the ring was performing - because that is the mechanism surgery removes. **Whether the
remediated tile still looks like the tile Rafe picked is his eye's call, not this file's**, and
the report routes it to him under the session's ruling trigger. Bible §13.4: do not build a
proxy for a register clause. There is no character detector here and there must not be one.

THE FILL
--------
Each ring pixel becomes the MODAL colour of its non-ring 8-neighbours, resolved outward over
several passes so a multi-pixel band has its outer course settled before its inner one needs
neighbours to borrow from. Modal rather than per-channel median: a channel-wise median mixes
channels and can produce a colour present in neither neighbour, which would be inventing one.
That reasoning is `dering_floors.py`'s and it was right; it is kept, not rewritten.

THE LOOP
--------
Strip the tightest loop the instrument can isolate, re-measure, repeat. The instrument is the
stopping condition, so the output is de-ringed by the same test the seat is armed with rather
than by this file's opinion of when it is done.
"""
import argparse
import collections
import hashlib
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ring_instrument as RI  # noqa: E402

SURVIVORS = os.path.join(REPO, "tools/pixellab/probe_6_4/survivors")
OUT = os.path.join(HERE, "remediated")
EVID = os.path.join(HERE, "evidence")
CODES = ("A-VAB", "A-HEB", "B-KAB", "C-GAB")
MAX_STRIPS = 8

# Below this, stripping the ring leaves the plate with no value separation from its ground and
# surgery has deleted the tile rather than de-ringed it. Bible §12's clause is the reason the
# question is asked at all; the clause's own threshold is PLACEHOLDER, so this is NOT presented
# as deriving it. It is a routing switch between two remediation methods, and it is set at the
# value the corpus makes unambiguous: the two tiles measure +11.2 and -1.4, which is not a
# borderline call in need of a fine threshold.
SEPARATION_FLOOR = 4.0


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    return sha256_bytes(open(p, "rb").read())


def git_commit():
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "UNKNOWN"


def separation(a, finding):
    """Value delta between the region this ring encloses and the ground outside the ring.

    The mechanism the ring performs, measured. Positive means the plate is lighter than its
    ground; the magnitude is what matters, not the sign.
    """
    L = RI.lum(a.astype(float))
    y0, x0, y1, x1 = finding["interior_bbox"]
    inside = np.zeros(L.shape, dtype=bool)
    inside[y0:y1 + 1, x0:x1 + 1] = True
    # The bbox includes the wall's inner face; take the ground as everything well outside it.
    outside = np.ones(L.shape, dtype=bool)
    outside[max(0, y0 - 1):y1 + 2, max(0, x0 - 1):x1 + 2] = False
    if not outside.any() or not inside.any():
        return 0.0
    return float(L[inside].mean() - L[outside].mean())


def strip_once(a, finding):
    """Remove one contour's pixels and fill from the tile's own material."""
    H, W = a.shape[:2]
    wall = finding["_wall"]
    ring = np.zeros((H, W), dtype=bool)
    for y, x in wall:
        ring[y, x] = True
    out = a.copy()
    n = int(ring.sum())
    for _ in range(6):
        todo = np.argwhere(ring)
        if not len(todo):
            break
        progressed = False
        for y, x in todo:
            vals = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < H and 0 <= nx < W and not ring[ny, nx]:
                        vals.append(tuple(out[ny, nx]))
            if vals:
                out[y, x] = collections.Counter(vals).most_common(1)[0][0]
                ring[y, x] = False
                progressed = True
        if not progressed:
            break
    return out, n


def tightest(a):
    """The ring finding with the smallest contour - the purest isolation of a loop in this tile.

    Stripping the tightest isolation removes the keyline and as little else as possible: a wider
    mask at a looser level would carry the tile's own material away with it.
    """
    rings = RI.find_rings(a)
    if not rings:
        return None
    return min(rings, key=lambda r: r["contour_px"])


def surgery(a):
    """Strip loops until the instrument reports CLEAN. Returns (tile, log)."""
    out = a.copy()
    log = []
    for i in range(MAX_STRIPS):
        finding = tightest(out)
        if finding is None:
            break
        sep = separation(out, finding)
        out, n = strip_once(out, finding)
        log.append(dict(strip=i + 1, level=finding["level"], kind=finding["kind"],
                        wall_px=n, interior_px=finding["interior_px"],
                        interior_bbox=finding["interior_bbox"],
                        separation_before=round(sep, 1)))
    return out, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(EVID, "remediation.json"))
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(EVID, exist_ok=True)
    parents = json.load(open(os.path.join(SURVIVORS, "MANIFEST.json")))["survivors"]
    by_code = {s["code"]: s for s in parents}

    print("SURVIVOR-FLOOR RING REMEDIATION")
    print("commit:    %s" % git_commit())
    print("originals: %s  READ-ONLY to this module" % os.path.relpath(SURVIVORS, REPO))
    print("outputs:   %s  NEW files, provenance-linked, NOT promoted\n"
          % os.path.relpath(OUT, REPO))

    records = []
    for code in CODES:
        src = os.path.join(SURVIVORS, code + ".png")
        a = np.array(Image.open(src).convert("RGB")).astype(int)
        pal = set(map(tuple, a.reshape(-1, 3).tolist()))
        v0, rings0 = RI.verdict(a)

        print("== %s ==  %s" % (code, v0))
        if v0 == "CLEAN":
            print("   carries no ring. Verified, not assumed: %d enclosures were tested at every"
                  % _enclosure_count(a))
            print("   value level and every one was rejected on ragged wall or on reaching the")
            print("   tile border. Carried into the remediated set UNCHANGED.")
            out = a
            route, log = "clean-verified", []
        else:
            cut, log = surgery(a)
            v1, _ = RI.verdict(cut)
            sep_after = _plate_separation_after(a, cut, rings0)
            print("   %d loop(s) stripped: %s"
                  % (len(log), ", ".join("%dpx at %s" % (l["wall_px"], l["level"]) for l in log)))
            print("   instrument after surgery: %s" % v1)
            print("   plate/ground value separation with the ring gone: %+.1f  (floor %+.1f)"
                  % (sep_after, SEPARATION_FLOOR))
            if abs(sep_after) >= SEPARATION_FLOOR:
                print("   -> SURGERY HOLDS. The ring was redundant with separation the tile")
                print("      already had. Stripping it removed a keyline and nothing else.")
                out, route = cut, "surgery"
            else:
                print("   -> SURGERY DELETES THE TILE. The ring was the only thing separating")
                print("      the plate from its ground, so stripping it does not de-ring this")
                print("      tile, it empties it. Routed to conditioned regeneration.")
                out, route = cut, "surgery-rejected-regenerate"
            got = set(map(tuple, out.reshape(-1, 3).tolist()))
            assert got <= pal, "remediation invented a colour - it must not"

        dst = os.path.join(OUT, code + ".png")
        Image.fromarray(out.astype(np.uint8)).save(dst)
        v_out, rings_out = RI.verdict(np.array(Image.open(dst).convert("RGB")).astype(int))
        changed = int((a != out).any(-1).sum())
        records.append(dict(
            code=code, route=route, file=code + ".png",
            parent=dict(file=code + ".png",
                        path=os.path.relpath(src, REPO),
                        sha256=by_code[code]["sha256"],
                        sha256_verified=sha256_file(src) == by_code[code]["sha256"],
                        stage1_source=by_code[code]["stage1_source"]),
            sha256=sha256_file(dst), pixels_changed=changed,
            verdict_before=v0, verdict_after=v_out,
            rings_before=RI.public(rings0), rings_after=RI.public(rings_out), strips=log))
        print("   %d/1024 px changed   sha256 %s\n" % (changed, sha256_file(dst)[:16]))

    manifest = dict(
        status="REMEDIATION CANDIDATES - NOT PROMOTED, NOT LANDED",
        governs="bible §13.1 governs landing; the blind seat gates; Rafe's eye rules",
        commit=git_commit(),
        instrument="tools/floor_remediation/ring_instrument.py",
        originals_untouched=True,
        floors=records)
    with open(os.path.join(OUT, "MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    with open(args.json, "w") as f:
        json.dump(manifest, f, indent=1)

    n_ring = sum(1 for r in records if r["verdict_after"] == "RING")
    n_regen = sum(1 for r in records if r["route"] == "surgery-rejected-regenerate")
    print("SUMMARY")
    for r in records:
        print("  %-6s %-28s %s -> %s" % (r["code"], r["route"], r["verdict_before"],
                                         r["verdict_after"]))
    print("\n  %d still carry a ring after surgery." % n_ring)
    print("  %d need conditioned regeneration (run regenerate.py)." % n_regen)
    return 0


def _enclosure_count(a):
    n = 0
    for kind, label, mask in RI.masks_of(a):
        if not mask.any() or mask.all():
            continue
        enc = RI.enclosed(mask)
        if not enc.any():
            continue
        n += sum(1 for r in RI.components(enc) if len(r) >= RI.MIN_INTERIOR)
    return n


def _plate_separation_after(before, after, rings_before):
    """The plate/ground value delta in the CUT tile, over the region the ring used to enclose."""
    if not rings_before:
        return 0.0
    widest = max(rings_before, key=lambda r: r["interior_px"])
    L = RI.lum(after.astype(float))
    y0, x0, y1, x1 = widest["interior_bbox"]
    inside = np.zeros(L.shape, dtype=bool)
    inside[y0:y1 + 1, x0:x1 + 1] = True
    outside = np.ones(L.shape, dtype=bool)
    outside[max(0, y0 - 1):y1 + 2, max(0, x0 - 1):x1 + 2] = False
    if not outside.any():
        return 0.0
    return float(L[inside].mean() - L[outside].mean())


if __name__ == "__main__":
    sys.exit(main())
