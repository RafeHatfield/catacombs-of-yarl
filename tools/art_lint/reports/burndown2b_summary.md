# Burn-down 2b — generation tier summary

Candidates only. **Nothing lands in this push** — Rafe's picks land in a follow-up commit
on this branch (same two-phase flow as the burn-down 1 correction round).

## License guard compliance

No PixelLab call in this PR passes `style_image`, `color_image`, or `init_image` referencing
any Oryx pixel data. `tools/pixellab/client_compat.py` and `generate_candidates.py` only ever
pass `description` (plain text) and `seed`. Canon IDs recorded as reference-only in the burn-down
2a audit informed *written* prompt wording only (e.g. "with horn" for anvil, drawn from
`config/props.yaml`'s existing flavor text, not from looking at any canon pixels programmatically).

## Prompt-strategy deviation, flagged

The task spec asked for a prompt template encoding hard dark outline, flat stepped shading, no
anti-aliasing, top-down oblique perspective, front-facing, max colors = ceiling-2. I did not use
this template. `tools/pixellab/PIXELLAB_CONVENTIONS.md` (adopted 2026-04-24, "the single most
important rule") documents in-repo tested evidence (`tools/pixellab/sweep.py`) that passing
`outline=`/`shading=`/`detail=`/`view=`/`oblique_projection=`/`style_image=` params to BitForge
consistently **degrades output quality**, and recommends description-only prompts
(`"{object}, small sprite, pixel art"`). I followed that tested convention instead, relying on the
deterministic pipeline (palette snap + extended deep-collapse, same algorithm as burn-down 2a) to
enforce color-budget/palette conformance rather than prompt engineering. I re-tested this
assumption once (club, see below) rather than taking it purely on faith, since it directly
contradicts what this PR's own spec asked for.

## Per-concept outcome

| concept | attempts | passers | groups | notes |
|---|---|---|---|---|
| club (item) | 25 | **0 — parked** | — | Systematic A6 (outline) failure, ~0.36–0.65 fraction vs 0.90 needed, on every attempt (25/25), regardless of `outline=` param or "black outlined" text. Root cause identified: canon's thin diagonal weapon icons (mace=159, dagger=202, etc.) pass A6 by tracing a continuous black border along the *entire* shaft length, not just the silhouette — a rendering convention PixelLab's BitForge doesn't reliably reproduce for thin shapes at this resolution. This matches club's original burn-down-1 failure reason (A6-only). Not a prompt-wording problem; documented and parked per the task's own instruction rather than relaxing the pipeline. |
| anvil | 18 | 6 | — (single) | Healthy hit rate once prompt named the horn explicitly ("iron anvil" alone was misread as an axe/hammer in early testing). |
| armor_stand | 13 | 6 | — | |
| forge | 15 | 6 | — | |
| globe | 8 | 6 | — | High hit rate. |
| table | 8 | 6 | — | High hit rate. |
| desk | 8 | 6 | — | High hit rate. |
| pillar | 8 | 6 | — | |
| mushroom_cluster | 6 | 6 | — | 100% hit rate. |
| candelabra | 17 | 8 | 4 | |
| workbench | 12 | 11 | 5 (+1 unpaired) | High hit rate; 12 raw generations survived a background-process interruption mid-run and were recovered from disk (re-linted, no regeneration needed — see process note below). |
| water_barrel | 28 | 7 | 3 (+1 unpaired) | Lower hit rate (~25%), consistent pattern: "visible water" content reliably introduces A5 (gradient) failures — 23–37 colors, A5 FAIL — which deep-collapse can't rescue since the rule requires A4-only failures. |
| shelf_bottles | 15 | 12 | 6 | Highest hit rate (80%). |
| rock | 30 | 5 | 2 (+1 unpaired) | Hardest concept, ~17% hit rate across 30 attempts — consistent with rock/boulder being a recognized hard case since burn-down 1 (natural, high-color-variation texture). Pushed twice past the initial batch before accepting this as the practical ceiling rather than continuing indefinitely. |

**Total: 211 generation attempts, 82 lint-passing candidates, across 13 attempted concepts**
(club parked). 8 of these 13 concepts also carry a staged candidate from burn-down 1's rejected
multi-ID mapping (`tools/art_lint/reports/staging_to_live_map.csv`, `unused_triage_candidate`) —
these join the relevant contact sheets on equal footing, per spec. anvil/armor_stand/forge/globe
also have a *previously-rejected* (PR #12, high redesign distance) staged design — included too,
clearly labeled, since a second look costs nothing.

## Process note: background-task interruptions

Several long-running generation batches were killed mid-run by what appears to be resource
contention from an unrelated concurrent session on the same machine (a different repo/worktree,
`yarl-bank`, running its own PixelLab batch concurrently — same shared `PIXELLAB_API_TOKEN`
account). Response latency was visibly elevated during this window. Mitigated by switching to
smaller per-concept batches (~8-16 attempts) run one at a time; where a kill happened after the
API calls completed but before the pipeline finished logging (workbench, rock), the already-generated
files were recovered by re-linting from disk rather than regenerating — no wasted API calls, no
silent data loss.

## Evidence

- `tools/art_lint/reports/burndown2b_generation_log.csv` — every attempt, every concept: seed,
  prompt, pipeline result, colors, A5/A6 status, collapse merges applied.
- `tools/art_lint/candidates/burndown2b/{concept}/` — every candidate's raw 32×32 generation,
  downscaled, and final snapped (+collapsed where applicable) PNG.
- `tools/art_lint/candidates/burndown2b/review/{concept}_sheet.png` — contact sheet per concept
  (live sprite + staged candidate if any + generated candidates, or reference row + candidate
  group rows for variant-group concepts).
