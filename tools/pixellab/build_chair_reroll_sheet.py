#!/usr/bin/env python3
"""ONE combined chair re-roll sheet for the gate (Route A + Route B), composed next to table 5053.

Route A (transform): the three incumbent chairs (5051/5056/5057) recoloured to table 5053's palette
via snap_to_palette — front-facing orientation preserved (the gate said the incumbents had this
right; only colour/weight failed).
Route B (regenerate): fresh BitForge v1 candidates generated with a front-facing / straight-on
prompt constraint, palette-locked to table 5053. Non-front-facing candidates are discarded before
the sheet (see DISCARD list).

Each candidate is shown NEXT TO table 5053 so the set read is judgeable, with full labels.
"""
import glob
import os
import re

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(REPO)
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
WORLD = "src/Presentation/assets/sprites_16bf/world_24x24"
OUT = "tools/art_lint/candidates/remediation_review"
os.makedirs(OUT, exist_ok=True)

# Route B seeds discarded for not being front-facing (three-quarter/side view).
ROUTE_B_DISCARD = {1}


def _text_w(s):
    try:
        return FONT.getlength(s)
    except AttributeError:
        return FONT.getsize(s)[0]


def wrap_text(text, max_px, font):
    """Wrap `text` so every line fits within max_px. Never truncates — a single over-long
    word is hard-split rather than clipped."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if _text_w(trial) <= max_px or not cur:
            # hard-split a lone word that itself exceeds the width
            if not cur and _text_w(word) > max_px:
                piece = ""
                for ch in word:
                    if _text_w(piece + ch) > max_px and piece:
                        lines.append(piece)
                        piece = ch
                    else:
                        piece += ch
                cur = piece
            else:
                cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def load(p):
    return Image.open(p).convert("RGBA")


def checker(size):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    px = im.load()
    for y in range(size[1]):
        for x in range(size[0]):
            px[x, y] = (70, 66, 60, 255) if (x // 8 + y // 8) % 2 else (48, 45, 41, 255)
    return im


def tile(im, scale):
    big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    base = checker(big.size)
    base.alpha_composite(big)
    return base


# The rejected incumbent chairs are preserved as static files: once picks land, the live
# world_505x.png files hold the NEW chairs, so the sheet must not read them for the "rejected"
# reference/Route-A comparison.
ORIG = "tools/art_lint/candidates/burndown3/_rejected_originals"


def rows_for():
    rows = [("REFERENCE — table 5053 + the gate-rejected incumbent 5051 (front-facing, wrong colour)",
             load(f"{WORLD}/oryx_16bit_fantasy_world_5053.png"),
             load(f"{ORIG}/chair_5051_rejected.png"))]
    # Route A — recoloured incumbents
    for fid in (5051, 5056, 5057):
        rows.append((f"ROUTE A (recolour incumbent {fid} -> table 5053 palette; orientation preserved)",
                     load(f"{WORLD}/oryx_16bit_fantasy_world_5053.png"),
                     load(f"tools/art_lint/candidates/burndown3/chair_route_a/chair_{fid}_route_a.png")))
    # Route B — fresh front-facing, discard non-front-facing
    b = sorted(glob.glob("tools/art_lint/candidates/burndown3/chair_route_b/chair_route_b_locked_s*_snapped.png"),
               key=lambda p: int(re.search(r"_s(\d+)_", p).group(1)))
    for p in b:
        s = int(re.search(r"_s(\d+)_", p).group(1))
        if s in ROUTE_B_DISCARD:
            continue
        rows.append((f"ROUTE B (regenerate, front-facing prompt, palette-locked; seed {s})",
                     load(f"{WORLD}/oryx_16bit_fantasy_world_5053.png"), load(p)))
    return rows


def build():
    rows = rows_for()
    scale, pad, gap, line_h = 6, 12, 18, 15
    img_pair_w = 24 * scale * 2 + gap
    # Widen the canvas beyond the image pair so labels have room; labels also WRAP to the usable
    # width so they can never truncate (fix, 2nd occurrence — cf. the seed-42 label confusion).
    w = max(img_pair_w, 620) + pad * 2
    usable = w - pad * 2

    # Pre-wrap every title and compute per-row label height so nothing clips vertically either.
    wrapped = [wrap_text(title, usable, FONT) for title, _, _ in rows]
    label_hs = [max(1, len(lines)) * line_h + 6 for lines in wrapped]
    img_h = 24 * scale
    h = sum(lh + img_h + pad for lh in label_hs) + pad

    sheet = Image.new("RGBA", (w, h), (56, 50, 44, 255))
    d = ImageDraw.Draw(sheet)
    y = pad
    for (title, left, right), lines, lh in zip(rows, wrapped, label_hs):
        for i, ln in enumerate(lines):
            d.text((pad, y + i * line_h), ln, font=FONT, fill=(255, 255, 255, 255))
        yy = y + lh
        sheet.alpha_composite(tile(left, scale), (pad, yy))
        sheet.alpha_composite(tile(right, scale), (pad + 24 * scale + gap, yy))
        y += lh + img_h + pad
    sheet.convert("RGB").save(f"{OUT}/chairs_reroll_next_to_table_5053.png")
    print(f"combined chair re-roll sheet: {len(rows)} rows "
          f"(1 reference + 3 Route A + {len(rows) - 4} Route B), discarded Route B seeds {sorted(ROUTE_B_DISCARD)}")


def build_confirmation():
    """Post-landing verification strip: the three LANDED cells, full route+seed labels + sheet
    positions, so the position→ID translation is checkable at a glance. Reads the live world_505x
    files (now the landed chairs) beside table 5053."""
    # (live_id, note, position phrase, route-b seed)
    landed = [
        (5051, "PRIMARY", "5th from top  (builder row 5)", 0),
        (5056, "", "4th from bottom  (builder row 8)", 4),
        (5057, "", "3rd from bottom  (builder row 9)", 5),
    ]
    header = ("COUNTING BASIS: cell 1 = the REFERENCE row (table 5053 + rejected 5051), per the "
              "sheet builder's own row ordering. Bottom-counted picks (5056/5057) are invariant to "
              "this; only the primary depends on it (if the reference row were excluded, 5th-from-top "
              "would be seed 2, not seed 0).")
    scale, pad, gap, line_h = 6, 12, 18, 15
    img_pair_w = 24 * scale * 2 + gap
    w = max(img_pair_w, 760) + pad * 2
    usable = w - pad * 2

    hdr_lines = wrap_text(header, usable, FONT)
    rows = []
    for fid, note, pos, seed in landed:
        title = (f"{fid}{(' ('+note+')') if note else ''}  ←  {pos}  =  "
                 f"ROUTE B seed {seed} (front-facing, palette-locked to table 5053)")
        rows.append((title, load(f"{WORLD}/oryx_16bit_fantasy_world_5053.png"),
                     load(f"{WORLD}/oryx_16bit_fantasy_world_{fid}.png")))
    wrapped = [wrap_text(t, usable, FONT) for t, _, _ in rows]
    label_hs = [max(1, len(ls)) * line_h + 6 for ls in wrapped]
    img_h = 24 * scale
    hdr_h = len(hdr_lines) * line_h + 10
    h = hdr_h + sum(lh + img_h + pad for lh in label_hs) + pad
    sheet = Image.new("RGBA", (w, h), (44, 52, 46, 255))
    d = ImageDraw.Draw(sheet)
    for i, ln in enumerate(hdr_lines):
        d.text((pad, pad + i * line_h), ln, font=FONT, fill=(200, 230, 200, 255))
    y = pad + hdr_h
    for (title, left, right), lines, lh in zip(rows, wrapped, label_hs):
        for i, ln in enumerate(lines):
            d.text((pad, y + i * line_h), ln, font=FONT, fill=(255, 255, 255, 255))
        yy = y + lh
        sheet.alpha_composite(tile(left, scale), (pad, yy))
        sheet.alpha_composite(tile(right, scale), (pad + 24 * scale + gap, yy))
        y += lh + img_h + pad
    sheet.convert("RGB").save(f"{OUT}/chairs_landed_confirmation.png")
    print("confirmation strip: 3 landed cells (5051←s0, 5056←s4, 5057←s5)")


if __name__ == "__main__":
    build()
    build_confirmation()
