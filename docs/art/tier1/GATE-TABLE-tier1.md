# Yarl Tier 1 — GATE TABLE (floors and walls) v0.1

Shape adopted from Gemfall `bulk/PLAN.md §5`. **BLOCK** halts the asset. **WARN** records and
proceeds. **NO INSTRUMENT** means the step exists and is carried by the human gate.

**This table is mostly empty on purpose.** Bible §15 finds nine of ten clauses uninstrumented,
four of them permanently by design (§13.4). A gate table padded with proxies would be worse
than a thin one, because proxies re-enter the optimisation and win trades they have not earned.

**No gate in this table may be marked green until it has been shown to go red** (LOOP-PROCESS
§4). A gate whose positive control has not been recorded is `UNPROVEN` and its pass does not
count.

| # | Step | Gate | Instrument | Status |
|---|---|---|---|---|
| 1 | Identity card exists and is complete | BLOCK | Schema validation | Buildable |
| 2 | Generation prompt is a committed file with clause provenance | BLOCK | File exists; self-check asserts load-bearing clauses survived | Buildable |
| 3 | Style references: ≥2, ≤8, authored at target canvas | BLOCK | Count + dimension check | Buildable |
| 4 | Output canvas matches declared native size | BLOCK | Dimension check | **PLACEHOLDER** — canvas not derived |
| 5 | Zero off-palette pixels after snap | BLOCK | `palette_check` | **Portable, not yet built** — new palette |
| 6 | Region slot legality (Boundary reserved slots only) | BLOCK | `palette_check --region` | **Portable, not yet built** |
| 7 | Mean snap distance below regeneration threshold | BLOCK | `verify_snap` | **Portable; threshold PLACEHOLDER** |
| 8 | Snap distance recorded to manifest | BLOCK | `build_generated_manifest` | Survives, re-point |
| 9 | Warm-share allocation within region band | WARN | — | ⚠ **NO INSTRUMENT.** Threshold may not exist; Ruling 70 applies — prefer refusal to a number with a story. |
| 10 | No baked directional highlight (§6.3) | WARN | — | ⚠ **NO INSTRUMENT.** A directional-highlight census is owed. Gemfall's analogue measured as a blunt proxy and was refused a verdict. |
| 11 | No baked outline (§12.1) | WARN | Edge-darkness census — **candidate only, unproven** | ⚠ Do not promote until it has demonstrated a fail |
| 12 | Tiles tile — no seam, no visible grid, no recurring blemish | BLOCK | Tiling census on an assembled field | Buildable, **owed** |
| 13 | Value separation from surface beneath | WARN | — | ⚠ **NO INSTRUMENT.** Gemfall found no defensible threshold for their analogue; expect the same. |
| 14 | Capture is in-scene, lit, on device, at true size | BLOCK | `verify_capture_determinism` + hash match | Survives |
| 15 | Evidence carries producing commit hash | BLOCK | Hash comparison at ruling | Survives |
| 16 | Plant seeded into critic set | BLOCK | Set composition check | Buildable |
| 17 | Critic identified the plant | BLOCK — **round VOID on failure** | Blind critic output | Process gate |
| 18 | Critic verdict = PASS, unhedged | BLOCK | Blind critic output | Process gate |
| 19 | Everything is held (§7.1) | — | — | ⚠ **NO INSTRUMENT — BY DESIGN.** Human gate. |
| 20 | Wear explained by traffic and indifference (§8.1) | — | — | ⚠ **NO INSTRUMENT — BY DESIGN.** Human gate. |
| 21 | Wear is legible — route readable (§8.2) | — | — | ⚠ **NO INSTRUMENT — BY DESIGN.** Critic Q3; human gate. |
| 22 | Register conformance, all clauses (§1) | — | — | ⚠ **NO INSTRUMENT — BY DESIGN (§13.4).** Human gate. **Final.** |

---

## Count

- **BLOCK with a working or buildable instrument:** 10
- **Blocked on the palette not existing yet:** 3
- **WARN with no instrument:** 4
- **No instrument, permanently, by design:** 4

**Fourteen of twenty-two steps are either uninstrumented or blocked on a value that Phase 5
derives.** This is the honest state of a tier-one gate before the pilot has run. It is recorded
rather than papered over, and the four permanent gaps are a decision rather than a deficiency.

---

## The landing gate is not in this table

Nothing above lands an asset. A clean run of every gate here ends a **round**. The asset lands
only at the human gate: in-scene, lit, on device, judged by eye (LOOP-PROCESS §1).

**Gate screens for tier one:**

- **The cast on its worst ground** — each candidate tile field against its measured worst
  contexts. The measure is uncalibrated, renders no verdict, and decides ordering only. **No
  pass or fail is drawn on the screen.**
- **Name them cold** — cannot run at tier one; there is no shipping corpus to shuffle against.
  The plant (step 16) is the substitute. **This screen activates at tier two**, once tier-one
  assets ship and can act as positive controls on the eye.

---

*v0.1 — 2026-08-24.*
