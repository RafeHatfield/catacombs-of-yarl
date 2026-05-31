# plan_end_game_impl.md — The Weighing (implementation)

Implementation task breakdown for `plan_end_game.md` (the design + resolved decisions are canonical there). This file is the build tracker. Status markers: ✅ complete / 🔄 in progress / ⬜ not started.

## Current State (2026-05-31)

**Just completed:** Chunk A foundation. TASK-001 (Weighing type taxonomy) ✅ and TASK-002 (audit scoring function) ✅. New files: `src/Logic/Endgame/WeighingTypes.cs`, `src/Logic/Endgame/AuditScorer.cs`; `cumulative_unprovoked_kills` read-side field + helpers added to `UnderWardenData`. 34 new tests in `tests/Endgame/AuditScorerTests.cs`. Fast suite green (1935 passed / 0 failed / 1 skipped), persistence round-trip confirms the new field serializes through the source-gen context.
**Next step:** TASK-003 — wire the excess-metric write side (run-scoped per-faction unprovoked-kill counter on `GameState`; increment at the combat kill site reusing the provoked/unprovoked distinction; flush into `UnderWarden.cumulative_unprovoked_kills` at run end).
**Open issues:** none blocking. All five viability flags resolved in the design doc. Note: strawman tier/ending thresholds in `AuditScorer` are deliberately un-tuned — TASK-011 (harness balance pass) moves the numbers; the structure is what's locked.

## Build order rationale

Front-load the **pure-logic, harness-testable spine** (Chunk A) before the AI-touching (Chunk B) and presentation/orchestration (Chunk C) work. The spine is the convergence point the whole design rests on ("everything feeds the Weighing"), it has zero Godot dependency, and de-risks the rest by giving the AI/orchestration work a tested foundation to attach to. Matches the project's measure-first philosophy.

---

## Chunk A — Pure-logic spine (no Godot, fully harness-testable)

- ✅ **TASK-001 — Weighing type taxonomy.** `src/Logic/Endgame/`: `EndingType` (None + 3 wins + 3 losses, closed set per decision 8), `GuardianId` (4 faction Guardians + Debt), `GuardianTier` (Allied/Diminished/Neutral/Savage), `WeighingOutcome` (InProgress/Survived/DiedToGuardians/DiedToDebt/Refused), `WeighingConstants` (FinalFloorDepth=25, the three loss cause-code strings). Acceptance: types compile, closed-set tests pass.
- ✅ **TASK-002 — Audit scoring function.** `AuditScorer` (static, deterministic). Per-Guardian tier functions over existing persistence fields + the excess metric, plus `DetermineEnding`. Strawman thresholds from decision 5/6, documented as tunable. Read-side excess field added to `UnderWardenData` (`cumulative_unprovoked_kills`, Dict<string,int>, default-add, no migration). Acceptance: tier-boundary + ending-determination unit tests pass.
- ⬜ **TASK-003 — Excess metric write side.** Run-scoped per-faction unprovoked-kill counter on `GameState`; increment at the combat kill site reusing the existing provoked/unprovoked distinction; flush into `UnderWarden.cumulative_unprovoked_kills` at run end (narrative-event boundary). Acceptance: kill an unprovoked cross-faction monster → counter increments → persists across run end.

## Chunk B — Ally combat AI (touches core targeting)

- ⬜ **TASK-004 — `player_ally` faction.** Add to `FactionRegistry`: not hostile to `player`; mutually hostile with Guardian factions. Tests for the matrix.
- ⬜ **TASK-005 — `ChooseTarget` gate.** Gate the hardcoded "always target the player" branch in `BasicMonsterAI.ChooseTarget` behind `AreHostile(myFaction, "player")`. Core AI change — full-suite regression. Tests: a `player_ally` entity does not target Sasha; Guardians target both Sasha and the ally.
- ⬜ **TASK-006 — Friendly-fire surface.** AoE scrolls, thrown items, cleave/bonus-attack, possession targeting, auto-explore/click pathing must not hit or path through `player_ally` entities. The real-lift sub-task (decision 4c). Per-surface tests.
- ⬜ **TASK-007 — Guardian-possesses-allies.** Warden-of-Wardens savage form flips an ally hostile via `EnragedEffect(HostileToAll)` (NOT PossessionEffect — decision 3); dispel/spell-break restores. Tests.

## Chunk C — Win scaffold + orchestration + endings (floor build + presentation)

- ⬜ **TASK-008 — Win scaffold.** Floor-25 gate (intercept `OnFloorTransitionRequested` / descend), hand-authored arena floor-build, dungeon-mode victory state on `GameState`, win-flush to persistence (`audit_completed`, ending type). Decision 7.
- ⬜ **TASK-009 — Sequential orchestration.** Sub-encounter state machine: audit-narration gates, spawn-on-cue per Guardian (rising as its category is read), the allies-fall-back-before-the-Debt gate, Debt solo phase. The keystone chunk (decision 1). Placeholder Guardian content.
- ⬜ **TASK-010 — Ending + loss routing.** `DetermineEnding` wired to the orchestration outcome; `GameOverScreen` routes on cause-code → correct final memo/epilogue; `weighing_loss_refused` routes from the audit choice (non-death). Decision 8.

## Chunk D — Balance (harness)

- ⬜ **TASK-011 — Guardian scaling balance pass.** Guardian-soak scenarios at varying record states; tune Guardian power + the strawman tier/ending thresholds so the wall is beatable-but-hard at intended skill/gear. Needs the harness; comes after framework + placeholder content.

---

## Content workstream (parallel, theirs — not engineering)

Tracked in `plan_end_game.md` "Content surfaces". Audit dialogue, per-Guardian rise text, ally-fallback lines, six ending texts, Hollowmark through the Weighing. Also: reconcile the held `final_audit` between-runs memos against the Weighing's audit (avoid redundancy) now that the audit shape is locked.
