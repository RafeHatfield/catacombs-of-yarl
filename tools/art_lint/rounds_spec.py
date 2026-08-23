#!/usr/bin/env python3
"""First in-scene review round layouts (art-lint-spec Part B review protocol).

Cell = (tileId, label, is_candidate, candidate_png_or_None). Candidate cells with a png are
temp-written to their tile IDs for the render, then reverted. All other cells are live tiles
(canon neighbours or already-landed sprites) rendered as-is.
"""
GA = "tools/art_lint/candidates/gauntlet"
RC = "tools/art_lint/candidates/burndown3/recolor"


def n(tid, label):        # neighbour / approved / landed — rendered live
    return (tid, label, False, None)


def c(tid, label, png=None):  # candidate — temp-written if png given
    return (tid, label, True, png)


ROUND_A = [
    c(5062, "5062 desk [rework: re-verdict]"),      n(319, "canon 319 table"),
    c(5064, "5064 desk [rework]"),                  n(321, "canon 321 chair"),
    c(5063, "5063 desk [rework]"),
    n(320, "canon 320 desk"),                       c(5106, "5106 nightstand [rework]"),
    n(319, "canon 319 table"),                      c(5107, "5107 nightstand [rework]"),
    n(323, "canon 323 weapon stand"),
    c(5082, "5082 workbench [rework]"),             n(322, "canon 322 throne"),
    c(5094, "5094 pillar [rework]"),                n(318, "canon 318 bookshelf"),
    c(5098, "5098 shelf [rework]"),
    n(268, "canon 268 barrel"),                     c(5097, "5097 shelf [rework]"),
    n(319, "canon 319 table"),                      c(5084, "5084 water_barrel [rework]"),
    n(5054, "5054 table [now canon 319]"),
]

ROUND_B = [
    c(5077, "5077 sign RECOLORED [candidate]", f"{RC}/5077_recolored.png"),
    n(319, "canon 319 table"),
    c(5093, "5093 pillar RECOLORED [candidate]", f"{RC}/5093_recolored.png"),
    n(258, "canon 258 (grey stone ref)"),
    c(5088, "5088 training_dummy s5 [candidate]", f"{GA}/training_dummy/training_dummy_s5_snapped.png"),
    n(5002, "5002 armor stand [approved]"),         n(323, "canon 323 weapon stand"),
    n(5090, "5090 tool_rack [approved]"),
    c(5108, "5108 mushroom_cluster [rank 3 verdict]"),
    c(5069, "5069 glowing_mushroom [rank 51 verdict]"),
    n(317, "canon 317 bookshelf"),
    n(5100, "5100 [canon 317 books, landed]"),
    n(5099, "5099 bottle-shelf [derived, landed]"),
    n(5101, "5101 bottle-shelf [derived, landed]"),
    n(318, "canon 318 bookshelf"),
]


def main(run_round):
    run_round("review_round_A_reworks", "Review round A — 11 former edge-only reworks (machine-clean; eye re-verdict). Orange = candidate, grey = canon/approved neighbour.", ROUND_A, cols=5)
    run_round("review_round_B_recolor_dummy_mushroom_shelf", "Review round B — recolors (sign 37 / pillar 52), training_dummy s5 (67) beside stands, mushrooms (3 / 51), landed shelf trio (317 books + derived bottles). Orange = candidate.", ROUND_B, cols=5)


W = "src/Presentation/assets/sprites_16bf/world_24x24"
GAU = "tools/art_lint/candidates/gauntlet"
ROUND_C = [
    c(5062, "5062 desk -> canon 320 [substitute]", f"{W}/oryx_16bit_fantasy_world_320.png"),
    n(319, "canon 319 table"),
    c(5064, "5064 desk -> canon 320 [substitute]", f"{W}/oryx_16bit_fantasy_world_320.png"),
    n(321, "canon 321 chair"),
    c(5063, "5063 desk -> canon 320 [substitute]", f"{W}/oryx_16bit_fantasy_world_320.png"),
    n(320, "canon 320 desk"),
    c(5106, "5106 nightstand -> regen s3 [candidate]", f"{GAU}/nightstand/nightstand_s3_snapped.png"),
    n(319, "canon 319 table"),
    c(5107, "5107 nightstand -> regen s5 [candidate]", f"{GAU}/nightstand/nightstand_s5_snapped.png"),
    n(323, "canon 323 weapon stand"),
    c(5082, "5082 workbench -> regen s2 [candidate; marginal]", f"{GAU}/workbench/workbench_s2_snapped.png"),
    n(322, "canon 322 throne"),
    c(5097, "5097 shelf -> canon 318 [substitute]", f"{W}/oryx_16bit_fantasy_world_318.png"),
    n(318, "canon 318 bookshelf"),
    c(5098, "5098 shelf -> canon 318 [substitute]", f"{W}/oryx_16bit_fantasy_world_318.png"),
    n(268, "canon 268 barrel"),
    c(5084, "5084 water_barrel -> regen s0 [candidate]", f"{GAU}/water_barrel/water_barrel_s0_snapped.png"),
    n(319, "canon 319 table"),
]


def main_c(run_round):
    run_round("review_round_C_rework9", "Review round C — the 9 Round-A rejects reworked. Substitutes: desks->canon 320, shelves->canon 318. Regen (F1-F3 critic + pre-filter): nightstands s3/s5, workbench s2 (marginal), water_barrel s0. Orange = candidate, grey = canon neighbour.", ROUND_C, cols=5)
