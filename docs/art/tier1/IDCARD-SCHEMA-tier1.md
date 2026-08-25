# Yarl Identity Card — SCHEMA v0.1 — Tier 1 (floors and walls)

The identity card is **the builder's contract and the screens' checklist**: one per asset,
written before generation, checked after.

**Every clause names its own instrument. A clause with no instrument says `NONE` out loud.**
A card that silently omits the instrument field is malformed.

**This schema is incomplete by design.** Clauses marked `PLACEHOLDER` reference values Phase 5
derives — canvas sizes, palette hexes, thresholds. Per the bible's governing principle, no law
is ratified ahead of its derivation.

---

## Fields

```yaml
# ---- IDENTITY ----
id:                 # e.g. B-FLOOR-001. B = Boundary.
layer:              # floor | wall
region:             # boundary   (only region derived at v0)
title:              # human-readable, e.g. "worn stone, main flow"

# ---- I1  ROLE ----
# What this asset IS, in one line. The builder generates against this.
role:
role_accept:        # list — readings that count as correct
role_reject:        # list — readings that are failures, INCLUDING near-misses
                    #   e.g. floor: reject "wall top", "ceiling", "water"
role_instrument: HUMAN GATE + blind critic Q1

# ---- I2  WEAR STATE ----  (bible §8)
traffic:            # heavy | light | none
care:               # none    (always "none" — the institution neither repairs nor removes)
wear_reads_as:      # polished | dished | grimed | undisturbed | collapsed
on_path:            # true | false
                    #   true  -> polish. This is the route.
                    #   false -> decay. Stepping off it is information (§8.2).
wear_instrument: NONE
                    # BY DESIGN. Carried by blind critic Q3 ("which way would you walk")
                    # and the human gate. No script scores this (§13.4).

# ---- I3  BINDING ----  (bible §7)
is_made:            # true | false   (false = raw geology; §7.1 applies to MADE things)
binding_authority:  # orc | institution | none
                    #   orc         -> redundant, visible, over-built, repairs over repairs.
                    #                  Competent but tough. Nothing present for appearance.
                    #   institution -> minimal and correct. One seal, one tag, never touched.
held_by:            # list of visible fasteners: pin | band | rope | cramp | mortar | clamp | seal
tagged:             # true | false   (institution has inventoried its world)
binding_instrument: NONE
                    # BY DESIGN. Blind critic Q5 ("show me what holds this together")
                    # and the human gate.

# ---- I4  PALETTE ----  (bible §5)
spine_colours:      # PLACEHOLDER — shared spine not yet derived
region_slots:       # PLACEHOLDER — Boundary reserved slots not yet derived
warm_share_target:  # PLACEHOLDER — allocation band not yet derived
palette_instrument: palette_check  (BLOCK)  — portable, not yet built
warm_share_instrument: NONE
                    # Threshold may not exist. Ruling 70: "no defensible threshold" is a
                    # COMPLETE calibration result. Prefer the refusal.

# ---- I5  LIGHT ----  (bible §6)
authored_for:       # receive        (LOCKED unless §6.4's probe retires §6.3)
baked_highlight:    # false — no directional key light
baked_outline:      # false — no dark ring anywhere (§12.1)
light_instrument: NONE (highlight census owed)
outline_instrument: edge-darkness census — CANDIDATE, UNPROVEN
                    # Do not promote until it has demonstrated a fail (LOOP-PROCESS §4).

# ---- I6  CANVAS & DENSITY ----  (bible §4)
native_canvas:      # PLACEHOLDER
scale_factor:       # PLACEHOLDER — integer only, nearest-neighbour, no AA
density_target:     # PLACEHOLDER — a RATIO to the figure layer, never an absolute
canvas_instrument: dimension check (BLOCK)
density_instrument: NONE — pending derivation

# ---- I7  TILING ----   (Yarl-specific; Gemfall has no analogue)
tiles:              # true | false
tile_edges:         # which edges must match
seam_tolerance:     # PLACEHOLDER
tiling_instrument: tiling census on an assembled field (BLOCK) — buildable, OWED

# ---- I8  FIGURE SEPARATION ----  (bible §12)
declared_dominant_value:   # PLACEHOLDER
separation_from_figure:    # PLACEHOLDER — no outline, no rim, no plate. Unaided.
separation_instrument: NONE
                    # Gemfall found no defensible threshold for their analogue.
                    # Blind critic Q8 and the human gate.

# ---- I9  UNIQUENESS ----
distinct_from:      # sibling asset ids this must not be confusable with
uniqueness_instrument: HUMAN GATE
                    # "Name them cold" — activates at tier 2, once tier 1 assets
                    # can serve as positive controls on the eye.

# ---- PROVENANCE ----
prompt_file:        # committed path — never a chat string
style_references:   # ≥2, ≤8, authored at target canvas (size/style_images mutually exclusive)
mean_snap_distance: # recorded per asset — the audit trail of how far the art was reinterpreted
producing_commit:   # hash. Mismatch at a ruling invalidates the evidence.
park_state:         # finalised-not-iterated | prepared-not-generated | in-flight
refusals:           # written BEFORE the run: what this seat refuses to do
```

---

## Instrument audit for this schema

| Clause | Instrument | Status |
|---|---|---|
| I1 role | Human + critic Q1 | Eye-side |
| I2 wear | — | ⚠ NO INSTRUMENT — by design |
| I3 binding | — | ⚠ NO INSTRUMENT — by design |
| I4 palette | `palette_check` | Portable, not built |
| I4 warm share | — | ⚠ NO INSTRUMENT |
| I5 highlight | — | ⚠ NO INSTRUMENT — census owed |
| I5 outline | Edge-darkness census | ⚠ Candidate, unproven |
| I6 canvas | Dimension check | Buildable |
| I6 density | — | ⚠ Pending derivation |
| I7 tiling | Tiling census | Buildable, owed |
| I8 separation | — | ⚠ NO INSTRUMENT |
| I9 uniqueness | Human gate | Eye-side; screen activates tier 2 |

**Three of twelve clauses have a working or immediately buildable instrument.** That is the
honest number before the pilot, and it is recorded rather than closed with proxies.

---

*v0.1 — 2026-08-24. I7 (tiling) is new for Yarl; Gemfall's discrete block portraits never
needed it. I2, I3, and I9 are deliberately uninstrumented per bible §13.4.*
