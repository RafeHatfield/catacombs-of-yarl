#!/usr/bin/env python3
"""Build the burn-down 2b review contact sheets: one sheet per concept.

Singles: one row = live sprite | staged/reference candidate (if any) | N generated
candidates (each labeled with seed + lint result).

Variant groups: a reference row (both live sprites + staged single if any), then one
row per candidate GROUP (pair of generated images sharing one prompt session).
"""
import csv
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

REPO = "/Users/rafehatfield/development/c-yarl/.claude/worktrees/art-burndown-2b"
CAND_DIR = os.path.join(REPO, "tools/art_lint/candidates/burndown2b")
OUT_DIR = os.path.join(CAND_DIR, "review")
os.chdir(REPO)
os.makedirs(OUT_DIR, exist_ok=True)

FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
SCALE = 6
PAD = 10
LABEL_H = 26

STAGED_LABELS = {
    "rejected_rubric_review": "STAGED (previously rejected, PR #12 — high redesign distance)",
    "unused_triage_candidate": "STAGED (unused triage candidate, PR #12)",
}

FILE_ID_BY_PATH_SUFFIX = None  # filled lazily


def find_live_path(file_id):
    for cls, prefix in [("world_24x24", "world"), ("items_16x16", "items")]:
        p = f"src/Presentation/assets/sprites_16bf/{cls}/oryx_16bit_fantasy_{prefix}_{file_id}.png"
        if os.path.exists(p):
            return p
    return None


def load_scaled(path, final_size=24):
    if path is None or not os.path.exists(path):
        im = Image.new("RGBA", (final_size, final_size), (40, 40, 40, 255))
    else:
        im = Image.open(path).convert("RGBA")
    big = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
    cb = Image.new("RGBA", big.size, (0, 0, 0, 0))
    px = cb.load()
    for yy in range(big.height):
        for xx in range(big.width):
            px[xx, yy] = (200, 200, 200, 255) if (xx // 6 + yy // 6) % 2 == 0 else (150, 150, 150, 255)
    cb.alpha_composite(big)
    return cb


def cell(label, img, border=(60, 60, 60)):
    w, h = img.size
    c = Image.new("RGBA", (w + PAD * 2, h + LABEL_H + PAD * 2), (25, 25, 25, 255))
    draw = ImageDraw.Draw(c)
    c.paste(img, (PAD, LABEL_H + PAD))
    for line_i, line in enumerate(_wrap(label, 24)):
        draw.text((PAD, 2 + line_i * 11), line, font=FONT, fill=(255, 255, 255, 255))
    draw.rectangle([0, 0, c.width - 1, c.height - 1], outline=border, width=2)
    return c


def _wrap(text, width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines[:2]


def row_image(cells):
    h = max(c.height for c in cells)
    w = sum(c.width for c in cells)
    row = Image.new("RGBA", (w, h), (10, 10, 10, 255))
    x = 0
    for c in cells:
        row.paste(c, (x, 0))
        x += c.width
    return row


def stack_rows(rows, out_path):
    w = max(r.width for r in rows)
    h = sum(r.height for r in rows)
    sheet = Image.new("RGBA", (w, h), (10, 10, 10, 255))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.convert("RGB").save(out_path)


def staged_info_for_concept(concept_game_key_variants):
    """Look up staging_to_live_map.csv for a matching staged file."""
    rows = list(csv.DictReader(open("tools/art_lint/reports/staging_to_live_map.csv")))
    for r in rows:
        if r["game_key"] in concept_game_key_variants and r["mapping_type"] in STAGED_LABELS:
            return r["staging_file"], STAGED_LABELS[r["mapping_type"]]
    return None, None


if __name__ == "__main__":
    print("Import build_single_sheet / build_group_sheet from a driver script.")
