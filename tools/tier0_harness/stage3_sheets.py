#!/usr/bin/env python3
"""§6.4 probe — STOP 2 presentation. Captures shown UNLABELLED as to origin.

The brief and the STOP 1 ruling agree on this: "captures presented unlabelled as to arm".
Cells are shuffled by a fixed seed and carry a neutral pick code; the code->survivor mapping is
written to a sidecar the sheet does not reveal.

Blinding matters more here than anywhere else in the probe. §13.2's "name them cold" exists so
the human is not grading on novelty or softening toward the one they expect to win — and by
STOP 2 there are expectations to protect against, including mine.

Two sheets, because §6.4 asks two different questions:

  LIT   — the comparison. "Do they look good lit?" Every capture through one identical rig.
  PAIRS — lit beside its own unlit companion, per survivor. This is §6.3's central claim made
          checkable: receive-light assets "look flat and slightly disappointing on a contact
          sheet ... they come alive only in the lit scene". If a pair shows no such difference,
          that is evidence against the clause, and it should be as visible as evidence for it.

Nothing here scores, ranks, or orders by any opinion. §13.1 gives the verdict to Rafe, in the
scene, on the device — and these sheets are an aid to that, never a substitute for it.
"""
import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(REPO, "tools/tier0_harness/evidence/stage3")
SHUFFLE_SEED = 20260826
INK, DIM, BG, CARD = (226, 226, 232), (150, 150, 158), (24, 24, 28), (48, 48, 54)


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
    return ("ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT")[i]


def crop_play(im):
    """The play area only. The HUD is identical in every capture and eats a third of the frame;
    leaving it in shrinks the thing actually under review. Nothing inside the crop is altered."""
    return im.crop((0, 60, im.width, 700))


def main():
    man = json.load(open(os.path.join(EV, "stage3_manifest.json")))
    lit = [c for c in man["captures"] if c["lit"]]
    rng = random.Random(SHUFFLE_SEED)
    rng.shuffle(lit)

    scale = 0.62
    tiles = []
    for i, c in enumerate(lit):
        im = crop_play(Image.open(os.path.join(EV, c["file"])).convert("RGB"))
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        tiles.append((code_for(i), c, im))

    pad, gap = 26, 16
    tw, th = tiles[0][2].size
    W = pad * 2 + len(tiles) * tw + (len(tiles) - 1) * gap
    H = pad + 96 + th + 30 + pad
    sh = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sh)
    d.text((pad, pad), "§6.4 STAGE 3 — LIT, ONE IDENTICAL RIG", font=font(22), fill=INK)
    d.text((pad, pad + 32), man["rig_requested"], font=font(12), fill=DIM)
    d.text((pad, pad + 50),
           "Unlabelled as to origin and shuffled. Walls are CONSTANT across all four, so they "
           "cannot explain a difference — and they are structureless,", font=font(12), fill=DIM)
    d.text((pad, pad + 66),
           "so they test light response and never architecture. Tile %s at x%s. "
           "§13.1: the verdict is the device's, not this sheet's."
           % (man["tile_size"], man["tile_scale"]), font=font(12), fill=(226, 188, 120))

    mapping = {}
    for i, (code, c, im) in enumerate(tiles):
        x = pad + i * (tw + gap)
        y = pad + 96
        d.rectangle([x - 3, y - 3, x + tw + 2, y + th + 2], fill=CARD)
        sh.paste(im, (x, y))
        d.text((x + 4, y + th + 8), code, font=font(16), fill=INK)
        mapping[code] = {"survivor": c["code"], "file": c["file"], "sha256": c["sha256"]}
    sh.save(os.path.join(EV, "stop2_lit_unlabelled.png"))

    # -- pairs: lit beside unlit, same survivor, same shuffle order --
    pw = tw
    W2 = pad * 2 + len(tiles) * (pw * 2 + 8) + (len(tiles) - 1) * gap
    H2 = pad + 92 + th + 30 + pad
    sh2 = Image.new("RGB", (W2, H2), BG)
    d2 = ImageDraw.Draw(sh2)
    d2.text((pad, pad), "§6.4 STAGE 3 — LIT vs UNLIT, same asset, same renderer",
            font=font(22), fill=INK)
    d2.text((pad, pad + 32),
            "§6.3: receive-light assets \"look flat and slightly disappointing on a contact "
            "sheet ... they come alive only in the lit scene.\"", font=font(12), fill=DIM)
    d2.text((pad, pad + 50),
            "Left of each pair is lit; right is the SAME asset with the carried light at zero "
            "energy and every other rig value untouched.", font=font(12), fill=DIM)
    d2.text((pad, pad + 66),
            "A pair that shows no difference is evidence AGAINST the clause and counts as much "
            "as a pair that shows one.", font=font(12), fill=(226, 188, 120))
    by_code = {c["code"]: c for c in man["captures"] if not c["lit"]}
    for i, (code, c, im) in enumerate(tiles):
        x = pad + i * (pw * 2 + 8 + gap)
        y = pad + 92
        un = crop_play(Image.open(os.path.join(EV, by_code[c["code"]]["file"])).convert("RGB"))
        un = un.resize((pw, th), Image.LANCZOS)
        d2.rectangle([x - 3, y - 3, x + pw * 2 + 8 + 2, y + th + 2], fill=CARD)
        sh2.paste(im, (x, y))
        sh2.paste(un, (x + pw + 8, y))
        d2.text((x + 4, y + th + 8), code, font=font(16), fill=INK)
    sh2.save(os.path.join(EV, "stop2_lit_vs_unlit.png"))

    with open(os.path.join(EV, "stop2_codes.json"), "w") as f:
        json.dump(mapping, f, indent=1, sort_keys=True)
    print("lit sheet   -> %s" % os.path.join(EV, "stop2_lit_unlabelled.png"))
    print("pairs sheet -> %s" % os.path.join(EV, "stop2_lit_vs_unlit.png"))
    print("codes       -> %s   [the mapping the sheets do not show]"
          % os.path.join(EV, "stop2_codes.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
