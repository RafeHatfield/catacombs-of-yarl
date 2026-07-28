#!/usr/bin/env python3
"""Contact sheets for burn-down 3 (parked-six round).

Fresh palette-locked concepts (anvil, armor_stand, club, mushroom_cluster):
same single-concept layout as burn-down 2b -- live sprite + staged
candidate (if any) + generated candidates.

Bank-sourced concepts (rock <- rocks_rubble, water_barrel <- barrels): no
fresh generation. Live sprite(s) + every Part-A-passing (WARN/PASS) bank
candidate, organized by bank sub-concept, so Rafe can pick 2 (these are
2-live-ID variant groups) from real breadth rather than a forced pairing
that doesn't reflect how this material was actually produced.
"""
import csv
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
os.chdir(REPO)

from build_review_sheets import load_scaled, cell, row_image, stack_rows, staged_info_for_concept, find_live_path
from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
OUT_DIR = "tools/art_lint/candidates/burndown3/review"
os.makedirs(OUT_DIR, exist_ok=True)

log_rows = list(csv.DictReader(open("tools/art_lint/reports/burndown3_generation_log.csv")))


def passers_for(concept):
    return [r for r in log_rows if r["concept"] == concept and r["overall"] in ("PASS", "WARN")]


GAME_KEY_ALIASES = {
    "anvil": ["Anvil"], "armor_stand": ["Armor Stand"], "club": ["club"],
    "mushroom_cluster": ["mushroom_cluster"],
}


def build_single(concept, file_id, final_size=24):
    live_path = find_live_path(file_id)
    row_cells = [cell(f"LIVE {os.path.basename(live_path)}", load_scaled(live_path, final_size), border=(180, 60, 60))]

    staged_path, staged_label = staged_info_for_concept(GAME_KEY_ALIASES.get(concept, [concept]))
    if staged_path:
        row_cells.append(cell(staged_label, load_scaled(staged_path, final_size), border=(200, 160, 40)))

    passers = passers_for(concept)
    if not passers:
        row_cells.append(cell("NO PASSING CANDIDATES\n(see generation log for failure pattern)",
                               Image.new("RGBA", (final_size * 6, final_size * 6), (60, 20, 20, 255)),
                               border=(200, 40, 40)))
    for r in passers:
        label = f"seed{r['seed']} {r['overall']} {r['colors']}c"
        row_cells.append(cell(label, load_scaled(r["final_path"], final_size), border=(60, 160, 60)))

    stack_rows([row_image(row_cells)], f"{OUT_DIR}/{concept}_sheet.png")
    print(f"{concept}: {len(passers)} candidates in sheet")


def build_bank_sheet(concept, live_file_ids, bank_subcategory, final_size=24):
    bank_dir = f"tools/art_lint/candidates/bank_palette_locked/prop_variety/{bank_subcategory}"
    bank_rows = list(csv.DictReader(open("tools/art_lint/candidates/bank_palette_locked/prop_variety/index.csv")))
    bank_rows = [r for r in bank_rows if r["subcategory"] == bank_subcategory]

    live_paths = [find_live_path(fid) for fid in live_file_ids]
    ref_cells = [cell(f"LIVE {os.path.basename(p)}", load_scaled(p, final_size), border=(180, 60, 60)) for p in live_paths]
    rows = [row_image(ref_cells)]

    by_bank_concept = {}
    for r in bank_rows:
        by_bank_concept.setdefault(r["concept"], []).append(r)

    for bank_concept, items in sorted(by_bank_concept.items()):
        landable = [r for r in items if r["lint_overall"] in ("PASS", "WARN")]
        row_cells = []
        for r in landable:
            path = os.path.join(bank_dir, r["filename"])
            label = f"{bank_concept} s{r['seed']} {r['lint_overall']} {r['color_count']}c"
            border = (40, 160, 220) if r["lint_overall"] == "PASS" else (60, 160, 60)
            row_cells.append(cell(label, load_scaled(path, final_size), border=border))
        if row_cells:
            rows.append(row_image(row_cells))

    stack_rows(rows, f"{OUT_DIR}/{concept}_sheet.png")
    total_landable = sum(1 for r in bank_rows if r["lint_overall"] in ("PASS", "WARN"))
    print(f"{concept}: {total_landable} bank candidates ({bank_subcategory}) in sheet, "
          f"organized into {len(by_bank_concept)} sub-concepts")


def build_single_multi_live(concept, live_file_ids, final_size=24):
    """Like build_single, but for a concept with more than one live variant ID
    (water_barrel: 5084 has visible water, 5085 doesn't) -- reference row shows
    both, candidate row shows the fresh palette-locked generation."""
    live_paths = [find_live_path(fid) for fid in live_file_ids]
    row_cells = [cell(f"LIVE {os.path.basename(p)}", load_scaled(p, final_size), border=(180, 60, 60))
                 for p in live_paths]

    passers = passers_for(concept)
    for r in passers:
        label = f"seed{r['seed']} {r['overall']} {r['colors']}c"
        row_cells.append(cell(label, load_scaled(r["final_path"], final_size), border=(60, 160, 60)))

    stack_rows([row_image(row_cells)], f"{OUT_DIR}/{concept}_freshlocked_sheet.png")
    print(f"{concept}: {len(passers)} fresh-locked candidates in sheet")


if __name__ == "__main__":
    build_single("anvil", 5001)
    build_single("armor_stand", 5002)
    build_single("club", 4001, final_size=16)
    build_single("mushroom_cluster", 5109)
    build_bank_sheet("rock", [5104, 5105], "rocks_rubble")
    build_bank_sheet("water_barrel", [5084, 5085], "barrels")
    build_single_multi_live("water_barrel", [5084, 5085])
