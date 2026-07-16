# Catacombs of Yarl — Art Bible

Status: draft for ruling. Companion document: `config/rubric/art-lint-spec.md`.

## 1. Canon

The Oryx 16-Bit Fantasy library is the visual specification for this game. This bible is descriptive, not aspirational: it documents the discipline already present in the Oryx sheets so that every generated or hand-made asset conforms to it. Where this document and the Oryx sheets disagree, the sheets win and this document gets corrected.

All new art, regardless of origin (Retro Diffusion, hand-pixeled, commissioned), passes the art lint and the acceptance test scene before it lands in `src/Presentation/assets/`.

## 2. Palette

The master palette is `config/art/oryx_master_palette.json`, extracted from canonical Oryx sheets only (world tiles ID < 5000, creatures, items). It is the single source of truth for color membership.

Rules:
- Every fully opaque pixel in every asset uses a color that is an exact member of the master palette. No near-matches. A color 10 RGB units from a palette color reads as subtly foreign at scale and is the single strongest sticker tell identified in diagnosis.
- The palette is never extended by adding colors found in generated output. Extending the palette is a design ruling, made here, recorded in the JSON metadata.

## 3. Resolution and cell sizes

Assets are authored at native cell size for their class and never mixed:

| class | cell size |
|---|---|
| world tiles, creatures, fx (standard) | 24×24 |
| items | 16×16 |
| player classes | 26×28 |
| fx (large) | 32×32 |

No asset is authored larger and downscaled into place. Rendering uses nearest-neighbor filtering (`default_texture_filter=0`, already set) and integer scaling only.

## 4. Shading discipline

Oryx shading is stepped, not blended:
- Color ramps use discrete steps. Adjacent ramp steps within a sprite sit at least ~20 RGB units apart; smooth gradients (many colors within 20 units of each other) are the machine signature of generated art and are prohibited.
- No anti-aliasing, internal or edge. Alpha is binary: 0 or 255. Zero partial-alpha pixels exist anywhere in the canonical library.
- No single-pixel color noise. Detail is built from clusters, not speckle.
- Dithering: not observed as a significant Oryx technique in the measured sample; do not introduce it.

## 5. Color budget

Measured Oryx baselines (medians, with observed maxima as hard ceilings):

| class | median colors | ceiling |
|---|---|---|
| world tiles / props | 4 | 10 |
| items (16×16) | 5 | 21 |
| creatures | 13 | 18 |

If a sprite needs more colors than the ceiling to read, the design is too refined for the format; simplify the design rather than raising the ceiling.

## 6. Outlines

- Creatures and items: hard dark outline (all channels < 70) on effectively the full silhouette boundary. Measured Oryx creature baseline: 97–100% dark-edge coverage.
- Props and furniture: hard dark outline is the norm (cleaned staging assets measure 76–100%).
- Ground decals (moss, puddles, vines, straw) and full-cell tiles legitimately lack outlines. The lint treats outline coverage as class-dependent; exceptions are per-asset rubric calls, not silent.

## 7. Perspective and proportion

Top-down oblique, front-facing props, consistent with the Oryx sheets. Judgment-level conformance (silhouette language, proportion, "same hand" reading) is assessed against the rubric in the lint spec, not automated. Light direction convention: to be documented from sheet observation at first rubric session; until then, match neighboring canon sprites for the same asset class.

## 8. Provenance

- Generated assets currently live in `world_24x24` under Oryx naming at IDs ≥ 5000. This convention is documented here and must not drift.
- `config/art/generated_assets_manifest.json` lists every non-Oryx asset in the live tree: filename, origin (generator/hand), conformance status, date landed. The lint targets its audit passes from this manifest, not from naming heuristics.
- License note: the master palette and this bible's rules are derived constraints and safe to use as generation conditioning. Feeding Oryx sprite images directly into a generator as img2img/style reference requires a check of the Oryx license terms before it becomes workflow. Unresolved; do not do it until ruled.

## 9. Acceptance test scene

A standing worst-case scene gates all art: busiest floor composition, portrait orientation, real device at target DPI, full UI including Hollowmark ribbon, deliberately mixing canon and generated assets.

Acceptance criteria:
- Sticker test: at arm's length, generated assets cannot be sorted from canon.
- Squint test: silhouettes and threat-relevant entities remain readable.

Every art PR includes before/after captures of this scene. The scene definition (floor, entity placement, device) is fixed and versioned so captures are comparable across PRs.

## 10. Pipeline

Generate → structural clean (background strip, color reduction, outline) → palette snap (`tools/art_lint/snap_to_palette.py`) → lint (`config/rubric/art-lint-spec.md` thresholds) → rubric pass → PR with lint report and test-scene captures → merge on green.

No asset lands in `src/Presentation/assets/` without completing the full pipeline.
