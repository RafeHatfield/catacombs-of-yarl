#!/usr/bin/env python3
"""Driver: build one review contact sheet per burn-down 2b concept, using the
generation log + staging_to_live_map.csv for staged/reference candidates."""
import csv
import os
import sys

REPO = "/Users/rafehatfield/development/c-yarl/.claude/worktrees/art-burndown-2b"
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
os.chdir(REPO)

from build_review_sheets import (load_scaled, cell, row_image, stack_rows,
                                  staged_info_for_concept, find_live_path)
from run_batch import CONCEPTS

SINGLES = ["club", "anvil", "armor_stand", "forge", "globe", "table", "desk", "pillar", "mushroom_cluster"]
GROUPS = ["candelabra", "workbench", "water_barrel", "shelf_bottles", "rock"]

GAME_KEY_ALIASES = {
    "anvil": ["Anvil"], "armor_stand": ["Armor Stand"], "forge": ["Forge"], "globe": ["Globe"],
    "table": ["table"], "desk": ["desk"], "candelabra": ["candelabra"], "workbench": ["workbench"],
    "water_barrel": ["water_barrel"], "shelf_bottles": ["shelf_bottles"], "rock": ["rock"],
    "pillar": ["pillar"], "mushroom_cluster": ["mushroom_cluster"], "club": ["club"],
}

log_rows = list(csv.DictReader(open("tools/art_lint/reports/burndown2b_generation_log.csv")))


def passers_for(concept):
    rows = [r for r in log_rows if r["concept"] == concept and r["overall"] in ("PASS", "WARN")]
    return rows


def build_single(concept):
    cfg = CONCEPTS[concept]
    final_size = cfg["final_size"]
    live_path = find_live_path(cfg["file_ids"][0])
    row_cells = [cell(f"LIVE {os.path.basename(live_path)}", load_scaled(live_path, final_size), border=(180, 60, 60))]

    staged_path, staged_label = staged_info_for_concept(GAME_KEY_ALIASES[concept])
    if staged_path:
        row_cells.append(cell(staged_label, load_scaled(staged_path, final_size), border=(200, 160, 40)))

    for r in passers_for(concept):
        label = f"seed{r['seed']} {r['overall']} {r['colors']}c" + (f" collapse={r['collapse_merges']}" if r['collapse_merges'] not in ("", "0") else "")
        row_cells.append(cell(label, load_scaled(r["final_path"], final_size), border=(60, 160, 60)))

    stack_rows([row_image(row_cells)], f"tools/art_lint/candidates/burndown2b/review/{concept}_sheet.png")
    print(f"{concept}: {len(row_cells)-1-(1 if staged_path else 0)} candidates in sheet")


def build_group(concept):
    cfg = CONCEPTS[concept]
    final_size = cfg["final_size"]
    live_paths = [find_live_path(fid) for fid in cfg["file_ids"]]
    ref_cells = [cell(f"LIVE {os.path.basename(p)}", load_scaled(p, final_size), border=(180, 60, 60)) for p in live_paths]
    staged_path, staged_label = staged_info_for_concept(GAME_KEY_ALIASES[concept])
    if staged_path:
        ref_cells.append(cell(staged_label, load_scaled(staged_path, final_size), border=(200, 160, 40)))
    rows = [row_image(ref_cells)]

    passers = passers_for(concept)
    # group consecutive passers into pairs (shared prompt session -> adjacent seeds)
    for i in range(0, len(passers) - 1, 2):
        a, b = passers[i], passers[i + 1]
        group_cells = []
        for r in (a, b):
            label = f"seed{r['seed']} {r['overall']} {r['colors']}c" + (f" collapse={r['collapse_merges']}" if r['collapse_merges'] not in ("", "0") else "")
            group_cells.append(cell(label, load_scaled(r["final_path"], final_size), border=(60, 160, 60)))
        rows.append(row_image(group_cells))
    if len(passers) % 2 == 1:
        r = passers[-1]
        label = f"seed{r['seed']} {r['overall']} {r['colors']}c (unpaired)"
        rows.append(row_image([cell(label, load_scaled(r["final_path"], final_size), border=(160, 60, 160))]))

    stack_rows(rows, f"tools/art_lint/candidates/burndown2b/review/{concept}_sheet.png")
    print(f"{concept}: {len(passers)} passers -> {(len(passers))//2} groups")


if __name__ == "__main__":
    os.makedirs("tools/art_lint/candidates/burndown2b/review", exist_ok=True)
    for c in SINGLES:
        build_single(c)
    for c in GROUPS:
        build_group(c)
