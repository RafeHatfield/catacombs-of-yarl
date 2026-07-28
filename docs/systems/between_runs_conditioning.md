# Mini-spec #42 — Between-runs (results screen) conditioning schema
## Hollowmark voice batch 1g — spec-before-lines artifact

Status: v1.1 — APPROVED with rulings applied (Q1 milestones confirmed;
Q2 a line always shows, fallback deepened to 6; Q3 resolved now via
PostRunContext.Ending using the existing EndingType enum — see PR-A task).
Survived splits into clean_audit / theft / swap per the real ending enum.

---

## 1. Verified data substrate

Available at results time today (no wiring needed):

| Field | Source | Values |
|---|---|---|
| Died | PostRunContext | true / false |
| CauseOfDeath | PostRunContext | "hazard", "monster", "weighing_loss_refused", "weighing_loss_guardians", "weighing_loss_debt" (granular codes arrive when Foundation's cause producer lands; null on survival) |
| KillerSpecies | PostRunContext | entities.yaml species id, monster deaths only |
| FloorReached | PostRunContext | 1–25 |
| RunNumber | PostRunContext | 1-based, post-increment |
| Fired-set | HollowmarkMetaData.BetweenRunsLinesFired | stable line ids, once-ever semantics, patch-safe (spec §6.11) |

Derivable with trivial mapping: cause class from KillerSpecies faction
(unshriven / undead / beast / cultist) — stable regardless of when the
granular cause taxonomy lands, which is the point.

Substrate notes: (a) PostRunContext's doc-comment claims granular cause
strings the engine never assigns — documentation drift from the known
cause-taxonomy gap; evidence forwarded to the Foundation item. (b) RESOLVED
by ruling: PostRunContext gains `EndingType Ending` (existing enum: None /
CleanAudit / Theft / Swap / losses), populated at all four construction
sites — commissioned as PR-A alongside 1g. (c) Depth bands below use numeric
ids, NOT region names — region naming is Foundation #34's ruling; bands
re-alias to regions after it lands, keys never change.

## 2. Design decisions

**D1 — Two tiers, two guarantee models.**
- MILESTONE tier: one-shot-forever lines, gated by the fired-set. Fire at
  RunNumber 1, 2, 3, 10, 25, 50. Highest precedence. These carry the arc
  v3 assigns to this surface: her particular between-runs weariness, which
  the player eventually learns to read as the span cost.
- CONDITIONED tier: repeatable pools, selected by run shape, exempt from
  the fired-set (they may recur across a long history; within-history
  variety comes from pool depth and the scheduler's eventual shuffle-bag).

**D2 — Modifier pools, not a matrix.** Cause-class and depth-band are
independent pools, not a cause x band matrix. A 4x5 matrix at pool depth 2
is 40 thin cells that mostly never fire; two independent pool families at
depth 3-4 are deep enough to stay fresh and every line gets exposure. The
selector alternates dimensions (see §4) so both flavors surface over time.

**D3 (amended by ruling) — A line always shows.** The fallback pool is
unconditioned and deepened to 6 lines, so every results screen carries
exactly one Hollowmark line. Repeatable pools recycle under the eventual
shuffle-bag; the fallback guarantees the floor.

## 3. Key schema and budget (50 lines)

| Key | Lines | Tier | Fires when |
|---|---|---|---|
| between_runs.milestone.run_1 | 1 | one-shot | first run ever ends (any outcome) |
| between_runs.milestone.run_2 | 1 | one-shot | second run ends |
| between_runs.milestone.run_3 | 1 | one-shot | third run ends |
| between_runs.milestone.run_10 | 1 | one-shot | tenth |
| between_runs.milestone.run_25 | 1 | one-shot | twenty-fifth |
| between_runs.milestone.run_50 | 1 | one-shot | fiftieth |
| between_runs.died.unshriven | 4 | conditioned | KillerSpecies faction = orc |
| between_runs.died.undead | 4 | conditioned | faction = undead |
| between_runs.died.beast | 4 | conditioned | faction = beast (spiders/slimes/beetles) |
| between_runs.died.cultist | 3 | conditioned | faction = cultist |
| between_runs.died.hazard | 3 | conditioned | CauseOfDeath = hazard |
| between_runs.died.band_1 | 3 | conditioned | FloorReached 1–5 |
| between_runs.died.band_2 | 3 | conditioned | 6–10 |
| between_runs.died.band_3 | 3 | conditioned | 11–15 |
| between_runs.died.band_4 | 3 | conditioned | 16–20 |
| between_runs.died.band_5 | 3 | conditioned | 21–25 (the Weighing's doorstep and floor) |
| between_runs.weighing_loss | 3 | conditioned | any weighing_loss_* cause |
| between_runs.survived.clean_audit | 3 | conditioned | Ending = CleanAudit |
| between_runs.survived.theft | 3 | conditioned | Ending = Theft |
| between_runs.survived.swap | 1 | conditioned | Ending = Swap (endgame-adjacent; possibly the final line of the game) |
| between_runs (fallback) | 6 | conditioned | anything unmatched — always non-empty, always eligible |
| **Total** | **55** | | |

## 4. Selection algorithm (wiring intent for the scheduler era)

1. If any milestone matches RunNumber and its id is not in the fired-set:
   fire it, record it, stop. Milestones outrank everything.
2. Else if died: alternate per run between the cause-family pool and the
   band pool (RunNumber parity is a sufficient alternator); if the chosen
   family has no pool for this run's values, try the other family; then
   weighing_loss if applicable; then fallback.
3. Else (survived): survived pool, then fallback.
4. One line per results screen, always. Empty result = silence (D3).
5. Repeatable-pool freshness is the shuffle-bag scheduler's job (same
   unbuilt dependency as the ribbon; noted, not solved here).

## 5. Guarantees (MISFED clauses)

- Every reachable run shape maps to at least one pool: the fallback pool
  is unconditioned and non-empty, so no run shape dead-ends.
- Band and faction mappings are total functions over today's engine values
  (all 25 species have a faction in entities.yaml; FloorReached is 1–25 by
  construction; every cause string routes to died.*, weighing_loss, or
  fallback).
- No key encodes a contested name: bands are numeric pending #34; faction
  classes come from entities.yaml faction fields, not display names.
- Milestone ids are stable strings recorded in the fired-set — patch-safe
  per HollowmarkMetaData's own design note.

## 6. Register brief for the lines (drafted only after spec approval)

Between-runs is her quietest surface: the run is over, nobody is in danger,
and per v3 she is quieter at run boundaries for a reason the player only
later understands. Weariness that reads as dryness on run 2 and as cost by
run 25. Milestones carry the arc explicitly (run_50 is allowed to be almost
tender). Conditioned pools react to the shape of the loss without recapping
it — the Under-Warden's memo owns the facts; she owns the feeling. No line
recaps stats, no line says "better luck," nothing coaches. Fallback pool is
three lines good enough to be nobody's consolation prize.

## 7. Rulings (closed 2026-07-26)

- Q1: Milestone set {1, 2, 3, 10, 25, 50} approved as proposed.
- Q2: A line always shows. Fallback deepened to 6; D3 amended; budget 55.
- Q3: Resolved immediately per close-as-we-go rule. PR-A adds
  PostRunContext.Ending (EndingType) and populates all four construction
  sites; survived conditioning splits clean_audit / theft / swap.
