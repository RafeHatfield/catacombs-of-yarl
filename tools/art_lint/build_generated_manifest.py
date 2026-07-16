#!/usr/bin/env python3
"""Build config/art/generated_assets_manifest.json from git provenance.

Method (per the lint spec): git provenance, not ID heuristics. ID-range
guessing is exactly what missed world_3001 and the items_16x16 4001-series
during palette extraction (see extract_master_palette.py docstring) — this
manifest exists to prevent that class of miss from recurring.

A file's *earliest add-commit* (first "A" status for its current path, walked
chronologically) determines its ruling:
  - CANON_COMMITS  — the original Oryx (sprites_16bf) and UF (sprites/,
    tiles/iso) library imports. Verified by commit message and file-count
    cross-check (e.g. a67ac2a's 248 additions + ff630613's 80 == 328, the
    exact current sprites/items count; 84ce76d's 162 == exact current
    sprites/fx count).
  - GENERATED_COMMITS — placeholder/PixelLab/RetroDiffusion content living
    under Oryx naming in world_24x24 and items_16x16.

Every currently-existing PNG under the swept directories must resolve to
exactly one of these two sets. Zero unclassified files is a hard requirement
of this script, not just an aspiration — it exits nonzero otherwise.

Per-entry origin/asset_class metadata is cross-referenced from the project's
own generation-tracking sources, not guessed:
  - tools/sprite_browser_ai.html — RD_SPRITES / PIXELLAB_SPRITES arrays,
    the authoritative per-ID generator/seed log.
  - config/props.yaml — blocks_movement/placement, used to distinguish
    discrete props from floor-level decals.
  - config/art/art_bible.md's explicit decal list (moss, puddles, vines,
    straw) overrides placement-based inference where the two would disagree
    (e.g. vine is wall_adjacent but is bible-named as a decal).
  - world_3001 and world_5039 predate the tracking sheet and are hand-cited
    from their commit messages / tile_themes.yaml instead.
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone

REPO_ROOT = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
os.chdir(REPO_ROOT)

SWEPT_DIRS = [
    "src/Presentation/assets/sprites_16bf",
    "src/Presentation/assets/sprites",
    "src/Presentation/assets/tiles/iso",
]

CANON_COMMITS = {
    "d124b5ff6131dd5762a9155800a1ab95ed7c08bb": "feat: Phase 2 — Godot project setup, Oryx asset import, scene tree skeleton",
    "ff630613bf50be07bdfd9c27ae592f0a059bb66c": "feat: dungeon generation, visibility, HUD/inventory, and observability infrastructure",
    "c9c27f18d7e0fdcf3276dc8b5de56599b77b238d": "feat: spell/wand/portal system, status effects, monster knowledge, tech debt fixes — 734 tests",
    "ae5969f024eaa34111915ac906bc586f699c7e62": "chore: add 16-bit fantasy sprite assets (Oryx 24x24 creatures + 16x16 items)",
    "a67ac2ac0e0934cc27592123ad6db235e092b7c2": "feat: import full UF items sprite set (328 sprites) and fix shield mapping",
    "84ce76d17cb6e5594718808ded3e2750e8767343": "feat: import UF FX sprite set (162 sprites) and add FX sprite browser",
}

GENERATED_COMMITS = {
    "447f5237b440791c5bb2981078caa29ab0cc935e": "feat: room prop system, placeholder sprites, dungeon visual improvements",
    "fccf258d7e23171dd329442217b3f882feee6008": "fix: corridor wall tiles, door rotation, rubble sprite; clean up new-sprites imports",
    "c5af9dd9d0798e996ed1d9d66cf0424df8661cd5": "feat: chests, signs, murals — bump interaction, PoC content, rendering",
    "f953c23ae3a7c53a2f552a8b21ce1843fa1ee678": "feat: adopt PixelLab as primary sprite tool; replace RD furniture sprites",
    "676847ae0d756b10a314ca33917f342cf7cbf1fa": "feat: cross-run persistence Phases 1-3 + Under-Warden design docs + style bible",
}

# world_3001 predates tools/sprite_browser_ai.html (added 447f523, before the
# tracking sheet existed). Cited from config/tile_themes.yaml's floor_worn
# entry and the commit's own "placeholder sprites" message.
WORLD_3001_OVERRIDE = {
    "origin": "placeholder",
    "asset_class": "decal",
    "game_key": "floor_worn",
    "notes": "Full-cell worn-floor tile (config/tile_themes.yaml). Predates the PixelLab/RD tracking sheet.",
    "lint_exemptions": ["A6_outline"],
}

# Bible-named ground decals (docs/art_bible.md §6): "moss, puddles, vines,
# straw" are explicitly exempt from outline coverage regardless of
# props.yaml placement (vine is wall_adjacent, not floor_overlay, but is
# still bible-named as a decal).
BIBLE_NAMED_DECAL_GAME_KEYS = {"moss_patch", "puddle", "vine", "straw_pile"}


def git_log_add_events():
    """(path, commit_hash) for every A-status event across the swept dirs, oldest first."""
    out = subprocess.check_output(
        ["git", "log", "--diff-filter=A", "--name-only",
         "--format=COMMIT|%H", "--reverse", "--"] + SWEPT_DIRS
    ).decode()
    events = []
    current = None
    for line in out.splitlines():
        if not line:
            continue
        if line.startswith("COMMIT|"):
            current = line.split("|", 1)[1]
        elif line.endswith(".png"):
            events.append((line, current))
    return events


def earliest_add_commit_map():
    first = {}
    for path, commit in git_log_add_events():
        if path not in first:
            first[path] = commit
    return first


def current_png_files():
    files = []
    for d in SWEPT_DIRS:
        for root, _, names in os.walk(d):
            for n in names:
                if n.endswith(".png"):
                    files.append(os.path.join(root, n))
    return sorted(files)


def parse_props_yaml(path="config/props.yaml"):
    """tile_id -> (prop_key, blocks_movement, placement).

    Field order in the YAML is tile_ids, footprint, blocks_movement,
    placement, tags — blocks_movement/placement come AFTER tile_ids within
    each prop's block, so tile_ids must be buffered and only resolved once
    the whole block (up to the next prop key) has been read.
    """
    id_info = {}
    current_key = None
    current_tids = []
    current_bm = None
    current_placement = None

    def flush():
        for tid in current_tids:
            id_info[tid] = (current_key, current_bm, current_placement)

    with open(path) as f:
        for line in f:
            m = re.match(r"^  ([a-z_0-9]+):\s*$", line)
            if m:
                flush()
                current_key, current_tids, current_bm, current_placement = m.group(1), [], None, None
                continue
            m = re.match(r"^\s*blocks_movement:\s*(true|false)", line)
            if m:
                current_bm = m.group(1) == "true"
                continue
            m = re.match(r"^\s*placement:\s*(\S+)", line)
            if m:
                current_placement = m.group(1)
                continue
            m = re.match(r"^\s*tile_ids:\s*\[([^\]]*)\]", line)
            if m and current_key:
                current_tids = [int(x) for x in re.findall(r"\d+", m.group(1))]
        flush()
    return id_info


def parse_sprite_browser(path="tools/sprite_browser_ai.html"):
    """id -> dict(name, dir, status, game_key, notes, origin)."""
    text = open(path).read()
    entries = {}
    for m in re.finditer(
        r'\{\s*id:(\d+),\s*name:"([^"]*)",\s*dir:"([^"]*)",\s*status:"([^"]*)",\s*'
        r'gameKey:(null|"[^"]*"),\s*notes:"([^"]*)"\s*\}',
        text,
    ):
        tid, name, d, status, game_key, notes = m.groups()
        game_key = None if game_key == "null" else game_key.strip('"')
        if notes.startswith("RD "):
            origin = "retrodiffusion"
        elif notes.startswith("PixelLab"):
            origin = "pixellab"
        elif notes.startswith("Placeholder"):
            origin = "placeholder"
        else:
            origin = "unknown"
        entries[int(tid)] = {
            "name": name, "dir": d, "status": status,
            "game_key": game_key, "notes": notes, "origin": origin,
        }
    return entries


def classify_asset_class(tile_id, browser_entry, props_info):
    prop_key = props_info[0] if props_info else (browser_entry["game_key"] if browser_entry else None)
    if prop_key in BIBLE_NAMED_DECAL_GAME_KEYS:
        return "decal", ["A6_outline"]
    if props_info and props_info[2] == "floor_overlay":
        return "decal", ["A6_outline"]
    return "prop", []


def build_entry(path, commit, world_id=None, items_id=None,
                 browser_entries=None, props_info_map=None):
    if path.endswith("oryx_16bit_fantasy_world_3001.png"):
        e = dict(WORLD_3001_OVERRIDE)
        return {
            "path": path,
            "origin": e["origin"],
            "added_commit": commit,
            "asset_class": e["asset_class"],
            "conformance_status": "nonconformant",
            "lint_exemptions": e["lint_exemptions"],
            "game_key": e["game_key"],
            "notes": e["notes"],
        }
    if path.endswith("oryx_16bit_fantasy_world_5039.png"):
        return {
            "path": path,
            "origin": "placeholder",
            "added_commit": commit,
            "asset_class": "world_tile",
            "conformance_status": "nonconformant",
            "lint_exemptions": [],
            "game_key": "key_item",
            "notes": ("Key icon overlay rendered directly from world_24x24 by "
                      "ItemSpriteManager/DungeonRenderer, bypassing the items_16x16 "
                      "pipeline — see src/Presentation/Entities/ItemSpriteManager.cs. "
                      "24x24 is correct/intentional for this asset, not a resolution bug. "
                      "Classified world_tile (not item) so A3 checks the resolution it "
                      "actually ships at. Flagging for Part B rubric: confirm this "
                      "classification with Rafe rather than assuming it."),
        }

    tid = world_id if world_id is not None else items_id
    browser = browser_entries.get(tid) if browser_entries else None
    asset_class = "item" if items_id is not None else None
    exemptions = []
    if world_id is not None:
        props_info = props_info_map.get(tid)
        asset_class, exemptions = classify_asset_class(tid, browser, props_info)

    origin = browser["origin"] if browser else "unknown"
    game_key = browser["game_key"] if browser else None
    notes = browser["notes"] if browser else ""
    if browser and browser["status"] == "reserved":
        notes = f"{notes} (status: reserved — not currently used by any game_key)"

    return {
        "path": path,
        "origin": origin,
        "added_commit": commit,
        "asset_class": asset_class,
        "conformance_status": "nonconformant",
        "lint_exemptions": exemptions,
        "game_key": game_key,
        "notes": notes,
    }


def main():
    first_commit = earliest_add_commit_map()
    files = current_png_files()

    unclassified = [p for p in files if p not in first_commit]
    if unclassified:
        print(f"ABORT: {len(unclassified)} files have no add-commit in git history:",
              file=sys.stderr)
        for p in unclassified[:20]:
            print(f"  {p}", file=sys.stderr)
        sys.exit(1)

    unknown_commit = [p for p in files
                       if first_commit[p] not in CANON_COMMITS
                       and first_commit[p] not in GENERATED_COMMITS]
    if unknown_commit:
        print(f"ABORT: {len(unknown_commit)} files trace to a commit not in "
              f"CANON_COMMITS or GENERATED_COMMITS — this script's commit "
              f"lists are stale relative to history. Not writing output.",
              file=sys.stderr)
        for p in unknown_commit[:20]:
            c = first_commit[p]
            print(f"  {p}  <- {c}", file=sys.stderr)
        sys.exit(1)

    browser_entries = parse_sprite_browser()
    props_info_map = parse_props_yaml()

    entries = []
    for p in files:
        commit = first_commit[p]
        if commit not in GENERATED_COMMITS:
            continue
        fname = os.path.basename(p)
        m = re.search(r"_(\d+)\.png$", fname)
        tid = int(m.group(1)) if m else None
        world_id = tid if "world_24x24" in p else None
        items_id = tid if "items_16x16" in p else None
        entries.append(build_entry(p, commit, world_id, items_id,
                                    browser_entries, props_info_map))

    entries.sort(key=lambda e: e["path"])

    # Classification table: commit -> ruling -> live file count
    commit_live_counts = defaultdict(int)
    for p in files:
        commit_live_counts[first_commit[p]] += 1

    all_commits = sorted(
        set(CANON_COMMITS) | set(GENERATED_COMMITS),
        key=lambda c: subprocess.check_output(
            ["git", "show", "-s", "--format=%ad", "--date=short", c]).decode().strip()
    )

    print("=== Classification table (commit -> ruling -> live file count) ===")
    print(f"{'commit':10s}  {'date':10s}  {'ruling':10s}  {'count':>6s}  subject")
    total_canon, total_generated = 0, 0
    table_rows = []
    for c in all_commits:
        date = subprocess.check_output(
            ["git", "show", "-s", "--format=%ad", "--date=short", c]).decode().strip()
        ruling = "CANON" if c in CANON_COMMITS else "GENERATED"
        subject = CANON_COMMITS.get(c) or GENERATED_COMMITS.get(c)
        count = commit_live_counts.get(c, 0)
        if ruling == "CANON":
            total_canon += count
        else:
            total_generated += count
        print(f"{c[:10]}  {date}  {ruling:10s}  {count:6d}  {subject}")
        table_rows.append({"commit": c, "date": date, "ruling": ruling,
                            "live_file_count": count, "subject": subject})

    print(f"\nTotal files swept: {len(files)}")
    print(f"Canon: {total_canon}")
    print(f"Generated (manifest entries): {total_generated}")
    print(f"Unclassified: {len(unclassified)}")

    if total_generated != len(entries):
        print(f"ABORT: entry count {len(entries)} != generated count {total_generated}",
              file=sys.stderr)
        sys.exit(1)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": ("Git provenance sweep: earliest add-commit per currently-live file, "
                   "classified against a hand-verified canon/generated commit ruling. "
                   "See tools/art_lint/build_generated_manifest.py for the ruling and "
                   "per-entry metadata sources."),
        "swept_dirs": SWEPT_DIRS,
        "total_files_swept": len(files),
        "canon_file_count": total_canon,
        "generated_file_count": total_generated,
        "unclassified_count": len(unclassified),
        "classification_table": table_rows,
        "entries": entries,
    }

    out_path = "config/art/generated_assets_manifest.json"
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nWrote {out_path}: {len(entries)} entries")


if __name__ == "__main__":
    main()
