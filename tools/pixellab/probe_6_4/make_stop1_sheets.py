#!/usr/bin/env python3
"""§6.4 probe — STOP 1 contact sheets.

One sheet per arm x subject. Every candidate the arm produced is on it — nothing is filtered,
nothing is ordered by any opinion of mine. **This seat does not curate.** Rafe picks 2-4
survivors per arm x subject and this script's only job is to make that possible without
leaking anything that would bias the pick.

WHAT IS DELIBERATELY NOT ON THE SHEET (session brief, STOP 1)
  * generation order — cells are shuffled by a fixed shuffle seed, so the order carries no
    information about which came first or which the server produced most readily
  * counts — no "20 candidates", no tallies, no yield
  * any quality mark, ranking, score, or ordering hint of any kind

WHAT IS ON IT, AND WHY
  * a neutral three-letter pick code per cell, so a pick can be communicated back. It encodes
    nothing: it is drawn from the shuffle, not from the index. The code -> file mapping is
    written to a sidecar JSON that the sheet does not reveal.
  * each candidate at x6 (judgeable) and the same row again at x2 (the declared display scale,
    32x32 native at x2 integer).

⚠ THE TRAP THIS SHEET SITS IN, stated on the sheet itself (bible §6.3):
"receive-light assets look flat and slightly disappointing on a contact sheet. They come alive
only in the lit scene. A critic — or a human at a gate — who rejects a receive-light asset for
looking underlit in isolation is applying the wrong instrument in the wrong context."
Arms B and C are the receive-light arms. Out-of-scene curation is legitimate HERE AND ONLY
HERE, because these are reference DNA and never land (§13.1 governs landing).
"""
import argparse
import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE1 = os.path.join(HERE, "stage1")
OUT = os.path.join(HERE, "stop1_sheets")
ARMS = ("A", "B", "C")
SUBJECTS = ("floor", "wall")

BG = (34, 34, 38)
CARD = (58, 58, 64)
INK = (222, 222, 228)
DIM = (150, 150, 158)

BIG, SMALL = 6, 2          # x6 to judge, x2 = the declared display scale
COLS = 5
PAD, GAP = 28, 18
SHUFFLE_SEED = 20260825    # fixed so the sheet is reproducible from the ledger


def font(sz):
    for p in ("/System/Library/Fonts/Menlo.ttc",
              "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


def code_for(i):
    """Pronounceable, order-free three-letter code."""
    cons, vow = "BDFGHKLMNPRSTVZ", "AEIOU"
    return cons[i % 15] + vow[(i // 15) % 5] + cons[(i // 75) % 15]


def build(arm, subject, rows):
    tiles = []
    for r in rows:
        p = os.path.join(STAGE1, r["image"])
        if os.path.exists(p):
            tiles.append((r, Image.open(p).convert("RGB")))

    rng = random.Random("%s|%s|%d" % (arm, subject, SHUFFLE_SEED))
    rng.shuffle(tiles)

    n = len(tiles)
    ncols = min(COLS, n) or 1
    nrows = (n + ncols - 1) // ncols
    cw = 32 * BIG
    ch = 32 * BIG + 6 + 32 * SMALL + 4 + 15
    W = PAD * 2 + ncols * cw + (ncols - 1) * GAP
    H = PAD + 106 + nrows * ch + (nrows - 1) * GAP + PAD + 34

    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    f_h, f_s, f_c = font(21), font(12), font(13)

    d.text((PAD, PAD), "§6.4 PROBE — STAGE 1 — ARM %s — %s" % (arm, subject.upper()),
           font=f_h, fill=INK)
    d.text((PAD, PAD + 30),
           "Pick 2-4. Survivors are REFERENCE DNA for Stage 2 conditioning — they are not "
           "game candidates and never land (§13.1).", font=f_s, fill=DIM)
    d.text((PAD, PAD + 48),
           "Each candidate: x6 to judge, then the same tile at x2 — the declared 32x32-at-x2 "
           "display scale.", font=f_s, fill=DIM)
    if arm in ("B", "C"):
        d.text((PAD, PAD + 66),
               "§6.3: receive-light assets look flat and disappointing on a contact sheet "
               "and come alive only in the lit scene —", font=f_s, fill=(226, 188, 120))
        d.text((PAD, PAD + 80),
               "judging this arm for looking underlit here is the wrong instrument in the "
               "wrong context.", font=f_s, fill=(226, 188, 120))
    else:
        d.text((PAD, PAD + 66),
               "Arm A bakes a directional key light. It is the positive control and the "
               "denominator of the effort ratio.", font=f_s, fill=DIM)

    mapping = {}
    y = PAD + 106
    for i, (row, im) in enumerate(tiles):
        cx = PAD + (i % ncols) * (cw + GAP)
        cy = y + (i // ncols) * (ch + GAP)
        d.rectangle([cx - 4, cy - 4, cx + cw + 3, cy + ch + 3], fill=CARD)
        sheet.paste(im.resize((32 * BIG, 32 * BIG), Image.NEAREST), (cx, cy))
        sy = cy + 32 * BIG + 6
        sheet.paste(im.resize((32 * SMALL, 32 * SMALL), Image.NEAREST), (cx, sy))
        code = code_for(i)
        d.text((cx + 32 * SMALL + 8, sy + 14), code, font=f_c, fill=INK)
        mapping[code] = {"image": row["image"], "sha256": row.get("image_sha256"),
                         "seed": row["request"].get("seed"), "arm": arm, "subject": subject}

    d.text((PAD, H - PAD - 8),
           "PROBE REFERENCE — NOT RATIFIED.  Nothing on this sheet is approved, promoted, or "
           "landed. Generated candidates, unfiltered and shuffled.", font=f_s, fill=DIM)

    os.makedirs(OUT, exist_ok=True)
    png = os.path.join(OUT, "arm_%s_%s.png" % (arm, subject))
    sheet.save(png)
    with open(os.path.join(OUT, "arm_%s_%s.codes.json" % (arm, subject)), "w") as f:
        json.dump(mapping, f, indent=1, sort_keys=True)
    return png, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=os.path.join(STAGE1, "ledger.jsonl"))
    args = ap.parse_args()

    rows = []
    with open(args.ledger) as f:
        for line in f:
            r = json.loads(line)
            if r.get("verdict") == "OK" and r.get("image") and r.get("claim", "").startswith("stage1:"):
                rows.append(r)

    for arm in ARMS:
        for subj in SUBJECTS:
            sel = [r for r in rows if "/%s/%s/" % (arm, subj) in "/" + r["image"].replace(os.sep, "/")]
            if not sel:
                print("arm %s / %s: no images" % (arm, subj))
                continue
            png, n = build(arm, subj, sel)
            print("arm %s / %-5s -> %s  (%d cells)" % (arm, subj, png, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
