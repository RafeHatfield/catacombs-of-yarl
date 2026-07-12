# Work Discovery Inventory — 2026-07-12

**Phase 1 (read-only). No merges, rebases, deletes, or file changes were made.**

- Repo: `rafehatfield/catacombs-of-yarl`
- `origin/main` HEAD: **`8a4b2ec`** — `docs(balance): correct FIND-003 -> FIND-004 …` (2026-06-07)
- Method: `git fetch --all --prune --tags`, remote-branch ahead/behind, GitHub API PR/tag enumeration, hidden `refs/pull/*/head` fetch, `git ls-remote`, local sweep.

## TL;DR

The public `main` snapshot is **not** missing the narrative/voice content the design review thought was absent — `config/voice_lines/`, `config/under_warden/`, `config/floor_traps.yaml` (9 trap types), and the endgame Weighing system are **already on main**. The review was misled by drifted docs, which is Phase 2's job.

Real unmerged work is concentrated in **two branches**, both forking cleanly from the current `main` HEAD (merge-base = `8a4b2ec` for both, 0 commits behind):

| Branch | Ahead | Tip | Last commit | Nature | Recommendation |
|---|---|---|---|---|---|
| `balance/0c-foundation` | **26** | `eef3077` | 2026-07-02 | LLM-testing + balance-instrumentation feature set (18k+ LOC, 164 files). Tip is **WIP**. | **Rebase then merge** — but verify build/tests first (tip is self-labeled `wip:`). |
| `claude/yarl-catacombs-review-o5ixc8` | **1** | `6d71b88` | 2026-07-06 | **Unbreaks CI** (broken since 2026-05-22) + review roadmap. | **Merge first, priority.** |

There are **no** open/closed PRs, **no** closed-unmerged PRs, **no** hidden PR refs, **no** tags, **no** stashes, and **no** uncommitted local work.

---

## 1. Remote branches (`git branch -r`, ahead/behind vs `origin/main`)

Only three refs exist under `refs/heads/` (confirmed by full `git ls-remote`):

| Branch | SHA | Last commit | Ahead | Behind |
|---|---|---|---|---|
| `origin/main` | `8a4b2ec` | 2026-06-07 | — | — |
| `origin/balance/0c-foundation` | `eef3077` | 2026-07-02 | 26 | 0 |
| `origin/claude/yarl-catacombs-review-o5ixc8` | `6d71b88` | 2026-07-06 | 1 | 0 |

Both non-main branches are **strictly ahead** (main is their ancestor) — clean linear descendants, no divergence to reconcile.

## 2. Pull requests (GitHub API, all states, limit 200)

**None.** `list_pull_requests(state=all)` returned `[]`. No open, closed, or merged PRs have ever existed on this repo. Therefore there are no closed-but-unmerged PRs to flag.

## 3. Hidden PR refs (`refs/pull/*/head`)

`git fetch origin '+refs/pull/*/head:refs/remotes/pr/*'` matched **zero refs** (consistent with §2 — no PRs were ever opened). Nothing hiding here.

## 4. Full `git ls-remote origin`

```
8a4b2ec  HEAD
eef3077  refs/heads/balance/0c-foundation
6d71b88  refs/heads/claude/yarl-catacombs-review-o5ixc8
8a4b2ec  refs/heads/main
```
No tags, no odd namespaces, nothing uncovered above. `list_tags` API also returned `[]`.

## 5. Local sweep (fresh clone)

- `git status --ignored -- config docs`: **clean** (working tree clean, no ignored content).
- `git stash list`: **empty**.
- Unpushed local commits: **none** (working branch `claude/work-discovery-doc-audit-zj381j` sits at `8a4b2ec` = main; note origin's copy of this branch was pruned/deleted at fetch).

---

## Per-item detail & recommendations

### A. `claude/yarl-catacombs-review-o5ixc8` — `6d71b88` (1 commit) → **MERGE FIRST**

`fix: unbreak CI + clean-machine builds; resolve FIND-004; world-class review & roadmap`

Diffstat (5 files, +269/−6):
- `.github/workflows/balance.yml` — target `dotnet restore CatacombsOfYarl.sln` (bare restore hit MSB1011: two root `.sln` files).
- `nuget.config` — drop mac-only `godot-local` source (NU1301 on any other machine).
- `tests/CatacombsOfYarl.Tests.csproj` — pin NUnit 4.3.2 / adapter 4.6.0 / test-sdk 17.11.1 / analyzers 4.4.0 (floating `4.*` broke compile with CS0121).
- `docs/balance/balance_findings.md` — +37 lines: FIND-005 resolving FIND-004 (no hidden damage reduction; the "10× ttd gap" was a rounds-vs-hits units mismatch).
- `tasks/plans/plan_world_class_review_2026_07.md` — +225 lines: prioritized review roadmap.

**Verified against main:** main's "Balance Suite" workflow has concluded `failure` on **every** push from 2026-05-22 through the latest (2026-06-08) — no tests or balance gate have run green in ~6 weeks. This branch is the fix.

**Recommendation: rebase-then-merge (or fast-forward) into main first.** It is small, self-contained, verified end-to-end on clean Linux per its commit body (restore → 2040 fast tests pass → `--suite 15/15`), and it restores the CI signal that any subsequent merge (esp. branch B) needs. Merging this before B also resolves the one file both branches touch (see conflict note below).

### B. `balance/0c-foundation` — `eef3077` (26 commits) → **REBASE THEN MERGE, after verifying the WIP tip**

164 files, **+18,223 / −277**. The largest reservoir of unmerged work. Grouped:

**New tools / subsystems (src + tools):**
- **LLM Player** — `tools/Harness/LlmPlayer/{AnthropicTurnClient,LlmBotBrain,LlmPlayerConfig}.cs` (+749), `config/llm_player/{reader,system_explorer}.yaml`, Harness `Program.cs` (+257). Hybrid decision mode + Haiku API integration + enriched transcripts.
- **Analyst tool** — new `tools/Analyst/` project (12 files, ~2,600 LOC): `Rubric`, `BugDetector`, `PredicateExpression`, `TraceRenderer`, `RunReporter`, `AggregateReport`, `BatchAnalyzer`, `Program`, etc.
- **Transcript enrichment** — `src/Logic/Balance/Transcript/{TranscriptRecorder,TurnEventJsonConverter}.cs`, `TurnEvent.cs` (+45), `TurnController.cs` (+95).
- **Weighing instrumentation** — `WeighingOrchestrator.cs` (+154), `tests/Endgame/WeighingInstrumentationTests.cs` (+396).
- **Floor-health classifier / lever attribution** — src + `tests/Balance/{FloorHealthClassifier,FloorHealthReport,LeverAttributionClassifier,ThreatArchetypeTagging,SoakBaseline,StagedStart,GearProfile,TargetTableLoader}Tests.cs`.

**Content / config that is ABSENT from main (the flagged paths):**
- `config/rubric/` — **5 files** (`v1.yaml`, `contracts.md`, `silent-failure-inventory.md`, `voice-anti-tell-lint.md`, `voice-register-spec.md`). Not on main.
- `docs/llm-testing/` — **5 files** (`00-overview.md`, `plan-analyst.md`, `plan-player.md`, `shared-transcript-schema.md`, `analyst-production-readiness.md`). Not on main.
- `config/balance/{gear_profiles,target_table}.yaml`; `docs/balance/{b1_engagement_calibration,balance_strategy,migration_loss_audit,threat_archetypes}.md`; `docs/story/THE_UNDER_WARDEN_story.md`.
- **51 new `config/levels/` scenarios** — B1 loadout characterization (naked/leather × dagger/sword/CD-potion × 2–5 orcs), orc-density ladder, troll HP×regen grid (h36–h48 × r0–r4), brute/chieftain diagnostics.

**Balance tuning in `config/entities.yaml`** (the only `M` to a shared content file): orc HP 28→40, orc `main_hand` spawn 0.75→1.00, troll HP 30→48, plus `threat_archetype` tags (baseline/escalator/spike) across orc variants and troll. This is a deliberate balance change — merging it **alters game balance on main**, so it wants harness re-validation, not a blind merge.

**Recommendation: rebase onto main, then merge — but do not merge as-is.** Two cautions:
1. The tip commit `eef3077` is self-labeled **`wip:`** (stuck detection, trace renderer, weighing instrumentation, rubric docs). Confirm the branch builds and the fast suite is green on top of the (fixed) CI before merging. Ideally merge branch A first so there is a working CI to validate against.
2. It carries a real balance change (entities.yaml). Per project rule "balance is measured, not guessed," run the harness on the new/existing scenarios and compare to target bands before locking it into main.

### C. Suspected boss/NPC entities — **NOT RECOVERABLE from the remote (never pushed, or never built)**

The design review expected NPCs **borrek, vesh, hael** and bosses **warden_of_reven, tide_hunger, hollow_king, weigher** as content. Searching **all three refs** across `config/`, `src/`, `docs/`:

- **`warden_of_reven`, `tide_hunger`, `hollow_king`**: appear **only** in narrative design docs under `docs/story/` — **no code, no entity definition, on any ref.**
- **`weigher`**: story docs only.
- **`borrek`, `vesh`, `hael`**: referenced as narrative names in endgame code already on main (`src/Logic/Persistence/Migrations.cs`, `src/Logic/Endgame/{AuditScorer,WeighingOrchestrator}.cs`) and in `config/voice_lines/possession.yaml` — but **not** as spawnable entities in `config/entities.yaml` on any ref.

**Conclusion:** there are **no entity/boss definitions** for these anywhere on the surviving remote. If such content was ever authored, it was never pushed and — per the task's framing (origin machine gone) — is unrecoverable. Flagging explicitly so it is not assumed to be "hiding on a branch." (This is a content gap to decide on, not a merge candidate.)

### D. Content already on main (design review's "missing content" — it isn't)

Present and identical on `origin/main` (word counts of YAML content):

| Path | Word count |
|---|---|
| `config/under_warden/cause_display_names.yaml` | 207 |
| `config/under_warden/memos.yaml` | 2,531 |
| `config/voice_lines/catalog_past_selves.yaml` | 405 |
| `config/voice_lines/hollowmark.yaml` | 254 |
| `config/voice_lines/possession.yaml` | 979 |
| `config/voice_lines/quipping_shade.yaml` | 211 |
| `config/voice_lines/weighing_audit.yaml` | 5,270 |
| **voice + memo total** | **~9,857 words** |

`config/floor_traps.yaml` is on main with **9 trap types** (spike, web, gas, fire, alarm_plate, teleport, root, hole, acid). The Weighing endgame system is on main (16 src files match `Weighing`). These are the systems the drifted docs wrongly call "not built" — the substance of Phase 2, not a recovery target.

---

## Merge-ordering note

The two branches overlap on exactly **one** file: `tests/CatacombsOfYarl.Tests.csproj` (A pins test-package versions; B bumps the test project for new Analyst/LLM tests). Merge **A first** (it establishes the pinned, CI-green baseline), then rebase **B** onto the result so B's csproj additions layer on top of A's pins rather than fighting them.

## Summary recommendations

| Item | SHA | Recommendation |
|---|---|---|
| `claude/yarl-catacombs-review-o5ixc8` | `6d71b88` | **Merge first** (unbreaks CI; small, verified). |
| `balance/0c-foundation` | `eef3077` | **Rebase then merge** after: (a) A is merged, (b) branch builds & fast suite green on fixed CI, (c) harness re-validates the entities.yaml balance change. Tip is WIP — treat as needing a green-up commit. |
| Bosses/NPCs (warden_of_reven, tide_hunger, hollow_king, weigher; borrek/vesh/hael as entities) | — | **Not on any ref — unrecoverable.** Content decision, not a merge. |
| voice_lines / under_warden / floor_traps / Weighing | — | **Already in main.** No action. Feeds Phase 2 doc reconciliation. |

**STOP — awaiting your merge decisions. No Phase 2 work until you respond.**
