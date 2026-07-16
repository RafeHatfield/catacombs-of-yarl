# Art Lint Spec

Status: adopted 2026-07-16 (PR #4). Thresholds accepted as drafted: color ceilings at observed canon maxima, outline FAIL at 0.90, live generated tiles not grandfathered.
Sibling discipline: `voice-anti-tell-lint.md` — same model, machine checks plus judgment rubric, both required.

Baselines below were measured 2026-07-16 against the canonical Oryx library (150-tile world sample, 80 creatures, 312 items). Thresholds are observed Oryx values, not aspirations. Re-measurement requires a ruling.

## Part A — Machine checks

Implemented in `tools/art_lint/`. Run per-sprite; output CSV, one row per asset. FAIL blocks merge; WARN requires an explicit rubric override noted in the PR.

### A1. Palette membership — FAIL
Every pixel with alpha == 255 has an RGB value that is an exact member of `config/art/oryx_master_palette.json`. Off-palette count must be 0.

### A2. Binary alpha — FAIL
Zero pixels with 0 < alpha < 255. (Canonical baseline: zero partial-alpha pixels across all measured classes.)

### A3. Native resolution — FAIL
Exact cell size for the asset's class (see bible §3). Any other dimensions fail. No mixed resolutions within a class directory.

### A4. Color budget — FAIL at ceiling, WARN above median band
| class | WARN above | FAIL above |
|---|---|---|
| world tiles / props (24×24) | 8 | 10 |
| items (16×16) | 12 | 21 |
| creatures (24×24) | 16 | 18 |

Count = unique RGB values among fully opaque pixels.

### A5. Gradient detection (near-color pairs) — WARN > 2, FAIL > 7
Pairs of distinct in-sprite colors closer than 20 RGB units (Euclidean). Canonical baselines: world median 0 / max 7; creatures median 0 / max 2; items median 0 / max 7. Post-snap assets inherit only ramp steps present in the master palette, so sustained high values indicate a design that fights the format.

### A6. Outline coverage — class-dependent
Fraction of silhouette-boundary pixels (opaque, 4-adjacent to transparent) that are dark (max channel < 70):
- creatures, items: FAIL below 0.90 (canonical creature baseline min 0.97; flat decal-like items exempt via manifest tag)
- props / furniture: WARN below 0.75
- ground decals, full-cell tiles: exempt (tagged in `generated_assets_manifest.json`)

### A7. Speckle — WARN (advisory, unbaselined)
Count of opaque pixels whose color differs from all 4-neighbors. Not yet baselined against canon; collect distributions during the first audit pass, then promote to thresholded check by ruling. Do not gate on this yet.

## Part B — Rubric (judgment, per-asset, human)

Scored by Rafe or delegated reviewer at PR time. Any FAIL blocks merge regardless of Part A results.

1. **Sticker test.** In the acceptance test scene (bible §9), at arm's length on device: can this asset be picked out as non-canon? Pass/fail.
2. **Squint test.** Silhouette reads at 1× on device; threat-relevant entities distinguishable from decor. Pass/fail.
3. **Same-hand test.** Placed in a row with 4 canon neighbors of the same class at 6×: does it read as drawn by the same artist? Pass/fail.
4. **Light direction.** Consistent with adjacent canon sprites of the same class. Pass/fail (convention to be documented at first session, bible §7).
5. **Proportion and perspective.** Matches class conventions (top-down oblique, front-facing props). Pass/fail.
6. **Ramp-collapse review.** For palette-snapped assets: compare before/after; did snapping destroy a detail the design needs? If yes, redesign the sprite within the palette rather than reverting the snap.

## Part C — Process

- The lint runs over the staged output directory before any asset moves into `src/Presentation/assets/`.
- Audit passes over live assets target files listed in `config/art/generated_assets_manifest.json` (never naming heuristics).
- Every art PR attaches: lint CSV, rubric scores, before/after test-scene captures.
- Lint code self-report is not evidence; the CSV attached to the PR and the captures are.

## Known exempt/legacy state (at spec adoption)

- 75 live generated world tiles (IDs 5001–5114) predate this spec and fail A1/A4/A5/A6. They are the Phase 4 burn-down backlog, tracked in the manifest, and are not grandfathered — they are scheduled debt.
