#!/usr/bin/env python3
"""Chair gate re-roll — two routes onto one sheet, both aimed at the gate's finding:
the fresh burn-down chairs failed on ORIENTATION (isometric/three-quarter); the library
convention is front-facing / straight-on, which the gate-rejected incumbents had right — they
failed only on colour/weight.

Route A (transform): recolour the incumbent chairs 5051/5056/5057 to table 5053's palette via the
deterministic snap tooling. Orientation is preserved by construction (we never regenerate), so the
one thing the incumbents got right is kept while the colour is pulled onto the table's warm wood.

Route B (regenerate): fresh BitForge v1 candidates with a front-facing / straight-on prompt as the
dominant constraint, palette-locked to table 5053. v2 note below.

    python3 tools/pixellab/chair_reroll.py route_a
    python3 tools/pixellab/chair_reroll.py route_b

## v2 map-object / rotation tooling — investigated, not used
PixelLab v2 (`api.pixellab.ai/v2/openapi.json`) does expose direct view control, but not a
front-elevation one: `Create1DirectionObjectRequest.view` is {top-down, sidescroller} and
`CreateMapObjectRequest.view` is {low top-down, high top-down, side}. None is a straight-on front
view, so it would not target "front-facing" better than an explicit BitForge prompt — and the
endpoints are async (object -> review -> select-frames) and unwired in this repo. Route B therefore
uses the v1 BitForge path with a front-facing prompt; non-front-facing seeds are discarded before
the sheet. Noted here so the choice is on the record.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools/pixellab"))
sys.path.insert(0, os.path.join(REPO, "tools/art_lint"))
os.chdir(REPO)
import warnings
warnings.filterwarnings("ignore")

WORLD = "src/Presentation/assets/sprites_16bf/world_24x24"
TABLE = f"{WORLD}/oryx_16bit_fantasy_world_5053.png"
CHAIR_IDS = [5051, 5056, 5057]

FRONT_FACING_PROMPT = (
    "a plain wooden chair seen from the front, straight-on front elevation facing the viewer, "
    "symmetric, tall plank backrest, four legs, flat orthographic, no angle no perspective")


def route_a():
    """Recolour incumbents to table 5053's palette (deterministic; orientation preserved)."""
    import snap_to_palette as snap
    import art_lint
    from generate_candidates_locked import build_swatch_from_live
    out = "tools/art_lint/candidates/burndown3/chair_route_a"
    os.makedirs(out, exist_ok=True)
    _, table_colors = build_swatch_from_live(TABLE, "prop")
    palette = [tuple(c) for c in table_colors]
    ps = art_lint.load_palette("config/art/oryx_master_palette.json")
    for fid in CHAIR_IDS:
        dst = f"{out}/chair_{fid}_route_a.png"
        snap.snap_file(f"{WORLD}/oryx_16bit_fantasy_world_{fid}.png", palette, dst)
        l = art_lint.lint_file(dst, "prop", ps)
        print(f"[A] {fid} -> {l['overall']} A4={l['A4_color_count']} A5={l['A5']} A6={l['A6']}")


def route_b(target=8, max_attempts=12):
    """Fresh front-facing candidates, palette-locked to table 5053 (BitForge v1)."""
    from generate_candidates_locked import generate_concept_locked
    res = generate_concept_locked(
        concept_name="chair_route_b", prompt=FRONT_FACING_PROMPT, file_ids=CHAIR_IDS,
        asset_class="prop", final_size=24, exempt=False, live_path=TABLE,
        target=target, max_attempts=max_attempts, seed_start=0)
    print(f"[B] attempts={res['attempts']} passers={res['passers']} "
          f"(discard non-front-facing seeds by eye before the sheet)")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "route_a"
    (route_a if which == "route_a" else route_b)()
