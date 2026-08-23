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

### A7. Speckle — WARN (advisory, unbaselined) → PROMOTED, see AF (Structural fineness)
Count of opaque pixels whose color differs from all 4-neighbors. **Promoted 2026-08** (play-review register ruling): now thresholded against canon as metric F1 of the Structural-fineness family below.

### AF. Structural fineness — WARN at canon p90, FAIL at canon max (ruled: play review 2026-08)
The register is Shattered-Pixel / Oryx school — chunky, low-detail, bold-read. The dominant generated-art failure is **refinement** (too fine, too many small structures) which passes A1–A6 while still reading as non-canon. This family measures fineness directly and thresholds it against the canonical Oryx population per sheet-class, WARN at canon **p90**, FAIL at canon **max** (same upper-bound philosophy as A4). Metrics (all: higher = finer = worse), computed by `tools/art_lint/fineness_metrics.py`:

- **F1 speckle** — opaque pixels with no same-colour 4-neighbour (isolated singles). (= A7, now thresholded.)
- **F2 small_clusters** — count of same-colour 4-connected components with area ≤ 4 px ("below meaningful structure size" in the chunky register).
- **F3 color_regions** — total count of same-colour 4-connected components (region fragmentation).
- **F4 edge_density** — interior colour-boundary pixels / opaque pixels (an opaque pixel with an opaque, different-coloured 4-neighbour; silhouette edges to transparency excluded). **ADVISORY / report-only (Rafe ruling 2026-08):** compact props legitimately run high on this (even canon-derived sprites and some literal canon tiles exceed its p90), so it over-flags and does not gate. Reported for signal; F1–F3 are the gating fineness metrics.

Canon-derived thresholds (`tools/art_lint/fineness_thresholds.json`, from the full canonical population — world_24x24 n=1784, creatures_24x24 n=396, items_16x16 n=308):

| class | F1 speckle p90/max | F2 small_clusters p90/max | F3 color_regions p90/max | F4 edge_density p90/max |
|---|---|---|---|---|
| world_24x24 | 42 / 207 | 62 / 216 | 75 / 239 | 0.885 / 1.0 |
| creatures_24x24 | 65 / 100 | 105 / 140 | 121 / 153 | 0.958 / 0.990 |
| items_16x16 | 49 / 112 | 62 / 117 | 65 / 128 | 0.987 / 1.0 |

Re-derive with `python3 tools/art_lint/fineness_metrics.py`. Sweep generated assets with `tools/art_lint/fineness_sweep.py`. This family **feeds** the Part B rubric and the acceptance scene — it ranks, the human eye rules; nothing is gated on a fineness score alone.

## Part B — Rubric (judgment, per-asset, human)

Scored by Rafe or delegated reviewer at PR time. Any FAIL blocks merge regardless of Part A results.

1. **Sticker test.** In the acceptance test scene (bible §9), at arm's length on device: can this asset be picked out as non-canon? Pass/fail.
2. **Squint test.** Silhouette reads at 1× on device; threat-relevant entities distinguishable from decor. Pass/fail.
3. **Same-hand test.** Placed in a row with 4 canon neighbors of the same class at 6×: does it read as drawn by the same artist? Pass/fail.
4. **Light direction.** Consistent with adjacent canon sprites of the same class. Pass/fail (convention to be documented at first session, bible §7).
5. **Proportion and perspective.** Matches class conventions (top-down oblique, front-facing props). **Two-plane rule (2026-08, strengthened Round E):** the projection is exactly two planes — front face **and** top surface. Both questions must pass: (a) no side face is visible (a single pixel column fails), **and** (b) both the front face and the top surface are present. A top-down-only sprite (top, no front) or an elevation-only sprite (front, no top) fails by omission. Applies to every candidate route, derivations included, and is run as a discard filter before review. Pass/fail.
6. **Ramp-collapse review.** For palette-snapped assets: compare before/after; did snapping destroy a detail the design needs? If yes, redesign the sprite within the palette rather than reverting the snap.
7. **Names itself at 1× in scene** — a sprite whose object is not identifiable without being told fails, regardless of style conformance.

**Fallback preserves pixels, never confers acceptance (ruled 2026-08).** When a rework produces no candidate that beats the live incumbent, the incumbent's pixels are *kept* — but "kept by fallback" is **not** an accepted-by-eye verdict. Acceptance is conferred only by an actual in-scene Part B pass on the sprite in question. A kept-by-fallback incumbent stays `pending_review` in the manifest until it earns an in-scene verdict; it is never marked `accepted` on the strength of "no candidate beat it." (This corrects the sweep-closure hole where beds 5058/5059, benches 5060/5061, and sack 5102 were recorded as accepted-by-eye without a real in-scene look.)

### Review protocol (ruled by Rafe 2026-08)
**No candidate is approved from a standalone contact sheet.** A candidate is reviewed only as it is
**rendered in a game scene through the production renderer** — seated adjacent to approved/canon props
of its own class, on themed floor, under normal lighting, at gameplay zoom, and captured. Contact
sheets remain a **pre-filter tool only** (they trim; they never approve). The in-scene review capture
is produced by `ReviewSceneBuilder` (sibling of `ArtAcceptanceSceneBuilder`, same
authored-data→production-renderer path); candidates enter via temporary in-place pixel writes in the
worktree (render → capture → revert; nothing lands until the in-scene verdict returns). Review
captures are committed to `tools/art_lint/review_scenes/` and linked in **one** PR comment per round —
never scattered.

## Part C — Process

- The lint runs over the staged output directory before any asset moves into `src/Presentation/assets/`.
- Audit passes over live assets target files listed in `config/art/generated_assets_manifest.json` (never naming heuristics).
- Every art PR attaches: lint CSV, rubric scores, before/after test-scene captures.
- Lint code self-report is not evidence; the CSV attached to the PR and the captures are.

## Known exempt/legacy state (at spec adoption)

- 75 live generated world tiles (IDs 5001–5114) predate this spec and fail A1/A4/A5/A6. They are the Phase 4 burn-down backlog, tracked in the manifest, and are not grandfathered — they are scheduled debt.

## Changelog

- 2026-08 (Rafe ruling, Round E verdicts): **two-plane rule strengthened** — now requires both (a) no side face and (b) front face AND top surface both present (a top-down-only or front-only sprite fails by omission). Run as a discard filter on every candidate route before review. Companion (bible/conventions): **structural derivation only for props** — a derivation re-dresses a canon donor's construction; palette-only derivation (canon colours on an invented form) is retired.
- 2026-08 (Rafe ruling, post-play-session): added Part B rule **"fallback preserves pixels, never confers acceptance"** — a kept-by-fallback incumbent stays `pending_review` until it earns an actual in-scene verdict. Corrects the sweep-closure hole (beds 5058/5059, benches 5060/5061, sack 5102 were marked accepted-by-eye without a real in-scene look; stripped to pending_review and re-reviewed in Round E). Companion ruling (bible changelog): **prop generation retired** — prop rework ladder is canon-substitution → canon-derivation → stop-and-discuss, no regen route; bank is reference-only.
- 2026-08 (Rafe ruling, from the Round-D nightstand rejection): **two-plane perspective rule** — only the front face and top surface are visible; any side face (even one pixel column) fails Part B perspective. Folded into the rubric perspective line.

- 2026-08 (Rafe rulings): **F4 edge_density DEMOTED to advisory/report-only** (over-flags compact props; F1–F3 gate). Added the **in-scene review protocol** to Part B (candidates reviewed only in a production-rendered scene beside approved neighbours; contact sheets are a pre-filter; captures → tools/art_lint/review_scenes/, one PR comment per round).

- 2026-08 (play review): promoted A7 speckle to a thresholded check and added the **Structural-fineness family (AF: F1–F4)** — speckle, small_clusters, color_regions, edge_density — baselined on the full canonical population per sheet-class, WARN at canon p90, FAIL at canon max (same philosophy as A4). Named the register explicitly (Shattered-Pixel / Oryx: chunky, low-detail, bold-read) and the failure mode (refinement). Thresholds in `tools/art_lint/fineness_thresholds.json`; derivation `tools/art_lint/fineness_metrics.py`.
- 2026-08: added Part B item 7 ("Names itself at 1× in scene"), ruled at the Track A gate review after candelabra 5080/5081 were rejected for reading as an unidentifiable shape at gameplay scale despite passing every Part A check.
