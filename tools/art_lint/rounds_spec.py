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


GN = "tools/art_lint/candidates/gauntlet/nightstand2"
BD = "tools/art_lint/candidates/burndown3"
ROUND_D = [
    c(5106, "5106 nightstand -> regen2 s101 [candidate]", f"{GN}/nightstand2_s101_snapped.png"),
    n(319, "canon 319 table"),
    c(5107, "5107 nightstand -> regen2 s107 [candidate]", f"{GN}/nightstand2_s107_snapped.png"),
    n(320, "canon 320 desk"),
    c(5082, "5082 workbench -> DERIVED (319 + tools) [candidate]", f"{BD}/workbench_derived/workbench_5082_derived.png"),
    n(319, "canon 319 table"),
    c(5084, "5084 water_barrel -> DERIVED (268 + water, bright) [candidate]", f"{BD}/water_barrel_derived/water_barrel_5084_derived.png"),
    n(268, "canon 268 barrel"),
    c(5085, "5085 water_barrel -> DERIVED (268 + water, calm) [candidate]", f"{BD}/water_barrel_derived/water_barrel_5085_derived.png"),
    n(268, "canon 268 barrel"),
]


def main_d(run_round):
    run_round("review_round_D_rework_resubmit", "Review round D — Round-C rejects reworked. Nightstands: regen2 s101/s107 (strict form-coherence). Workbench: DERIVED (canon 319 + tool clutter, regen route closed). Water barrels 5084/5085: DERIVED (canon 268 + water surface, variant pair). Orange = candidate, grey = canon.", ROUND_D, cols=5, map_w=12, map_h=12, player=(6, 5))


# ---------------------------------------------------------------------------
# Round E — post-play-session. Two captures (before/after) because a tile ID
# can only render one sprite per scene. Capture 1 = live incumbents (the
# fallback-stripped set + colour-failed nightstand + columns). Capture 2 =
# canon-only candidates temp-written in. Rafe verdicts each pair across the two.
RE = "tools/art_lint/candidates/round_e"

ROUND_E_BEFORE = [
    c(5058, "5058 bed — INCUMBENT (fallback-stripped)"),   n(319, "canon 319 table (wood ref)"),
    c(5059, "5059 bed — INCUMBENT (fallback-stripped)"),
    c(5060, "5060 bench — INCUMBENT (fallback-stripped)"), n(321, "canon 321 chair (wood ref)"),
    c(5061, "5061 bench — INCUMBENT (fallback-stripped)"),
    c(5106, "5106 nightstand — INCUMBENT (colour FAILED play review)"), n(320, "canon 320 desk (wood ref)"),
    c(5107, "5107 nightstand — INCUMBENT (colour FAILED)"),
    c(5093, "5093 pillar — INCUMBENT"),                    n(486, "canon 486 fountain (stone ref)"),
    c(5094, "5094 pillar — INCUMBENT"),                    n(258, "canon 258 wall (stone ref)"),
    c(5095, "5095 pillar — INCUMBENT (deep-collapse blob)"),
    c(5102, "5102 sack — INCUMBENT (fallback-stripped; review-as-is)"), n(268, "canon 268 barrel"),
]

ROUND_E_AFTER = [
    c(5058, "5058 bed -> DERIVED (canon wood frame + blue blanket)", f"{RE}/5058_bed.png"),
    n(319, "canon 319 table (wood ref)"),
    c(5059, "5059 bed -> DERIVED (canon wood + white coverlet)", f"{RE}/5059_bed.png"),
    c(5060, "5060 bench -> DERIVED (canon 321/319 wood, backed)", f"{RE}/5060_bench.png"),
    n(321, "canon 321 chair (wood ref)"),
    c(5061, "5061 bench -> DERIVED (canon wood, open low back)", f"{RE}/5061_bench.png"),
    c(5106, "5106 nightstand -> RECOLOR (canon desk-320 wood, shape kept)", f"{RE}/5106_wood.png"),
    n(320, "canon 320 desk (wood ref)"),
    c(5107, "5107 nightstand -> RECOLOR (canon desk-320 wood)", f"{RE}/5107_wood.png"),
    c(5093, "5093 pillar -> RECOLOR (fountain stone ramp)", f"{RE}/5093_stone.png"),
    n(486, "canon 486 fountain (stone ref)"),
    c(5094, "5094 pillar -> RECOLOR (fountain stone ramp)", f"{RE}/5094_stone.png"),
    n(258, "canon 258 wall (stone ref)"),
    c(5095, "5095 pillar -> ADOPT 5094 form (blob unrecolorable)", f"{RE}/5095_altform.png"),
]


RE2 = "tools/art_lint/candidates/round_e2"

ROUND_E2_AFTER = [
    c(5058, "5058 bed -> STRUCTURAL (table 319 re-dressed, blue blanket)", f"{RE2}/5058_bed.png"),
    n(319, "canon 319 table (donor)"),
    c(5059, "5059 bed -> STRUCTURAL (table 319 re-dressed, white coverlet)", f"{RE2}/5059_bed.png"),
    c(5060, "5060 bench -> STRUCTURAL (chair 321 widened, settle)", f"{RE2}/5060_bench.png"),
    n(321, "canon 321 chair (donor)"),
    c(5061, "5061 bench -> STRUCTURAL (chair 321 widened, low back)", f"{RE2}/5061_bench.png"),
    c(5106, "5106 nightstand -> golden + 5px legs (canon stroke)", f"{RE2}/5106_wood.png"),
    n(320, "canon 320 desk (5px legs ref)"),
    c(5107, "5107 nightstand -> golden + 5px legs", f"{RE2}/5107_wood.png"),
    c(5093, "5093 pillar -> clean stone (contour kept, de-speckled)", f"{RE2}/5093_stone.png"),
    n(486, "canon 486 fountain (stone ref)"),
    c(5094, "5094 pillar -> clean stone (jaggedness fixed)", f"{RE2}/5094_stone.png"),
    n(258, "canon 258 wall (stone ref)"),
    c(5095, "5095 pillar -> adopt 5094 clean form", f"{RE2}/5095_altform.png"),
    c(5102, "5102 sack -> review-as-is (carried from E)"),
]


RE3 = "tools/art_lint/candidates/round_e3"

ROUND_E3_AFTER = [
    c(5058, "5058 bed -> signature-led (blanket-dominant, blue)", f"{RE3}/5058_bed.png"),
    n(319, "canon 319 table (grammar donor)"),
    c(5059, "5059 bed -> signature-led (white coverlet)", f"{RE3}/5059_bed.png"),
    c(5060, "5060 bench -> BACKLESS wide seat + legs", f"{RE3}/5060_bench.png"),
    n(321, "canon 321 chair (grammar donor)"),
    c(5061, "5061 bench -> BACKLESS wide seat + legs", f"{RE3}/5061_bench.png"),
    c(5102, "5102 sack -> RECOLOR only (canon burlap ramp)", f"{RE3}/5102_sack.png"),
    n(268, "canon 268 barrel (burlap ramp ref)"),
    n(5106, "5106 nightstand [LANDED E2]"),
    n(5093, "5093 pillar [LANDED E2]"),
    n(486, "canon 486 fountain (stone ref)"),
]


ROUND_E3FINAL = [
    c(5058, "5058 bed [E3 signature-led]", f"{RE3}/5058_bed.png"),
    n(319, "canon 319 table (bed grammar)"),
    c(5059, "5059 bed [E3 signature-led]", f"{RE3}/5059_bed.png"),
    c(5060, "5060 bench [E3 backless]", f"{RE3}/5060_bench.png"),
    n(321, "canon 321 chair (bench grammar)"),
    c(5061, "5061 bench [E3 backless]", f"{RE3}/5061_bench.png"),
    c(5115, "5115 bone pile [NEW: canon bone grammar -> mounded heap]"),
    n(96, "canon 96 bones (grammar ref)"),
    n(612, "canon 612 skeleton (bone ramp ref)"),
    c(5116, "5116 flood marker [NEW: deep-water region]"),
    n(5110, "puddle 5110 (must read distinct)"),
    n(486, "canon 486 fountain (water ramp ref)"),
]


def main_e3final(run_round):
    run_round("review_round_E3final_cross_silhouette",
              "Review round E3-final (sprint-exit cross-silhouette test). Four target silhouettes, donor grammar only. Benches: chair 321 grammar, backless. Beds: table 319 grammar, signature-led (blanket-dominant). Bone pile 5115 [NEW]: canon bone grey-white ramp + skull/long-bone components (tiles 96/612), target silhouette = mounded ossuary heap, two-plane. Flood marker 5116 [NEW]: canon fountain water ramp deepened to a true-blue region filling the cell (distinct from the small teal puddle 5110); water is decal-class (flat top plane, outline-exempt per bible s6). NOTE: no darker/crypt room theme is wired (Crypt->sandstone fallback), so both depths props sit on the standard sandstone floor. Orange = candidate, grey = canon/ref.",
              ROUND_E3FINAL, cols=3)


def main_e3(run_round):
    run_round("review_round_E3_after_candidates",
              "Review round E3 — target-silhouette-led rebuilds. Beds: signature features lead (blanket dominates the top plane, pillow band at head, frame reduced to headboard/footboard edges — no apron); 319 grammar only. Benches: chair 321 grammar, back REMOVED (backless wide seat + legs). Sack: recolor only to canon burlap ramp, shape untouched. Landed E2 items (nightstand 5106, pillar 5093) shown as approved context. Orange = candidate, grey = canon/landed.",
              ROUND_E3_AFTER, cols=3)


def main_e2(run_round):
    run_round("review_round_E2_after_candidates",
              "Review round E2 — structural rebuilds. Beds re-dress canon table 319 (bedding on the top surface, table apron/legs = front face); benches widen canon chair 321 (settle / low-back). Nightstands: legs thickened to canon 5px. Pillars: clean stone recolor, contour kept, jaggedness fixed. Sack carried for verdict. Compare vs the E BEFORE capture. Orange = candidate, grey = canon donor/ref.",
              ROUND_E2_AFTER, cols=3)


def main_e(run_round):
    run_round("review_round_E_before_incumbents",
              "Review round E (BEFORE) — live incumbents. Fallback-stripped set (beds 5058/5059, benches 5060/5061, sack 5102), colour-failed nightstands 5106/5107, pillars 5093/5094/5095. Orange = under review, grey = canon ref. Compare against the AFTER capture.",
              ROUND_E_BEFORE, cols=3)
    run_round("review_round_E_after_candidates",
              "Review round E (AFTER) — canon-only candidates. Beds/benches DERIVED from canon furniture wood; nightstands RECOLORED to canon desk-320 wood; pillars RECOLORED to fountain stone ramp (5095 adopts 5094's form — its blob is unrecolorable). No generation used. Orange = candidate, grey = canon ref.",
              ROUND_E_AFTER, cols=3)
