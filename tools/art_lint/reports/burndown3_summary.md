Burn-down 3 (parked-six round) — candidates only. Nothing lands in this
push; picks land in a follow-up commit, same two-phase flow as burn-downs
1 and 2b.

## Amendment executed: bank-first, generate-only-what-is-missing

Per the amendment to this round: pulled existing Part-A-passing candidates
from `bank_palette_locked/prop_variety/` for rock and water_barrel instead
of generating fresh. Generated fresh (palette-locked) only for anvil,
armor_stand, club, mushroom_cluster.

## Results

| concept | source | attempts | landable candidates | notes |
|---|---|---|---|---|
| anvil | fresh, palette-locked | 6 | 6 | 100% hit rate |
| armor_stand | fresh, palette-locked | 6 | 6 | 100% hit rate |
| club | fresh, palette-locked | 20 | **0** | see below |
| mushroom_cluster | fresh, palette-locked | 6 | 6 | 100% hit rate |
| rock | bank (rocks_rubble) | 0 (pulled from bank) | 56 (8 PASS + 48 WARN) | 7 sub-concepts |
| water_barrel | bank (barrels) | 0 (pulled from bank) | 56 (0 PASS + 56 WARN) | 7 sub-concepts, **no water content** — see below |

## Palette-lock correction: confirmed, dramatic

anvil/armor_stand/mushroom_cluster all hit 6/6 on the first 6 seeds tried —
100% hit rate, versus 13–30 attempts per concept needed in burn-down 2b
(no palette lock). Each concept's swatch was built from that concept's own
current live sprite (dominant opaque colors, snapped to the nearest
master-palette entry, capped at the class's color-budget ceiling) — not a
generic swatch — so the correction is doing real per-concept conforming
work, not just capping color count arbitrarily.

## club: confirmed structural, not a prompt/palette problem

20/20 attempts still fail A6 (outline coverage) even with palette lock —
and now for a cleanly isolated reason: **every single attempt passes A4**
(colors ranged 5–10, comfortably under budget) while A6 fails 20/20. This
confirms the burn-down-2b diagnosis precisely: the outline-coverage gap is
about spatial edge-tracing (a continuous dark border the length of a thin
shape), which color-budget conformance cannot touch. Palette lock was worth
ruling out before committing to the outline-repair-script path (issue
tracking the parked-six) — it's now ruled out. The outline-repair script is
the only remaining unblock path for club.

## water_barrel: bank candidates read as barrels, not *water* barrels

Flagging honestly rather than presenting this as a clean win: none of the
56 `barrels` bank candidates show visible water or liquid content — they
are generic sealed/open/broken/leaking/banded/keg/stacked barrel shapes.
The current live design's whole point is a barrel *of water* (quench-tank
flavor). If Rafe picks from this set, the result conforms on palette and
silhouette but changes what the object communicates — worth weighing
against Option 3's "don't replace the design" ruling before picking, not
after.

## First live test of the bank-to-landing path (issue #47)

Issue #47 flagged that nothing in the candidate bank had gone through an
actual accept/reject ruling yet. This round is the first real test of that
path end to end: bank files (already final-pipeline PNGs per the bank's own
`index.csv`, no re-processing needed) were referenced directly into the
contact-sheet builder alongside the fresh burn-down-3 candidates, with zero
friction — same `cell`/`load_scaled` helpers, same live-sprite-plus-
candidates layout, same PASS/WARN border convention. The only adaptation
needed was organizing by the bank's own sub-concept grouping (7 named
variants per category) instead of burn-down-2b's seed-based grouping, since
the bank was generated as independent per-concept sessions, not one shared-
construction session with paired variants. If rock or water_barrel picks
land from this bank, that will be the actual first bank-to-landing
instance — worth a follow-up note on issue #47 either way.

## Evidence

- `tools/art_lint/reports/burndown3_generation_log.csv` — every fresh
  generation attempt: seed, prompt, lint result, colors, A5/A6.
- `tools/art_lint/candidates/burndown3/{anvil,armor_stand,club,mushroom_cluster}/`
  — every candidate's raw/downscaled/snapped PNG + the per-concept color
  swatch used (`_color_swatch.png`, `_swatch_colors.txt`).
- `tools/art_lint/candidates/burndown3/review/*_sheet.png` — one contact
  sheet per concept (6 total).
- Bank candidates for rock/water_barrel are referenced in place from
  `tools/art_lint/candidates/bank_palette_locked/prop_variety/` (already
  committed via PR #25) — not duplicated into this PR's diff.
