# plan_end_game_impl.md — The Weighing (implementation)

Implementation task breakdown for `plan_end_game.md` (the design + resolved decisions are canonical there). This file is the build tracker. Status markers: ✅ complete / 🔄 in progress / ⬜ not started.

## Current State (2026-06-06)

**Just completed:** Full Weighing implementation — framework (Chunks A–C) + audit content. The Weighing is functional, voiced, and ready for balance tuning and presentation polish. Full suite **2023 fast + 30 slow, 0 failed.** Presentation builds.

**What's built:**
- Chunks A–C: audit spine (scoring, excess metric, GuardianTier), ally combat (`player_ally` faction, friendly-fire guards, `GuardianAbilities`), win scaffold (Tribunal Hall arena, `WeighingOrchestrator`, 6 endings, Debt choice gate Force/Self/Refuse)
- Audit content: opening + Warden/Oathkeeper/Auditor's Own/Assembly beats (4 tiers each) + Debt terms (Lady's terms, Anik, Hollowmark threshold) + 4 resolutions (CleanAudit, Swap, Theft, LossRefused) all in `weighing_audit.yaml`, wired via `WeighingAuditRegistry`
- `WeighingDialogueEvent` / `DebtChoiceGateEvent` pipeline; resolution dialogue fires before `WeighingResolvedEvent`
- Refused-Sasha: no corpse (log `WeighingRefusals` instead); Swap is always a choice at the gate regardless of record cleanness

**Review + enablement pass (2026-06-06, `a182fa5` + pending docs):** pre-balance code review closed 4 findings. (1) Headless soft-lock fixed — the Weighing now runs without persistence (default audit) and without UI: `GameState.WeighingAuditOverride` drives exact tiers, `GameState.WeighingHeadlessGatePolicy` (Force/Swap/Refuse) resolves the Debt choice. (2) Excess metric switched to **per-run** (this descent, not lifetime) for both the Auditor's Own and the Oathkeeper fine scaling — `AuditScorer.Score` reads the live `RunAggressionTally`; a clean descent reads clean regardless of career total. (3) Savage Warden ally-flip **wired** (Option C, lingering curse): the Savage Warden arms a curse that turns the next ally to rise (enraged, Dispel-reversible) — was previously dormant. (4) Test gaps closed. Tech debt filed in `tech_debt_2026_06_06.md` (DEBT-014–019; DEBT-014 = keep `CumulativeUnprovokedKills` inert for future career-cruelty content).

**Next step — TASK-011 (balance pass): GO.** The hold is released — content landed, the harness can run the Weighing headlessly, and the metric measures the right thing. Tune Guardian + Debt placeholder stats (`WeighingOrchestrator.StatsFor`, `SpawnDebtCombatant`) and the strawman tier thresholds (`AuditScorer`) so each wall is beatable-but-hard. Target output (per `project_weighing_balance_pass` memory): per-tier time-to-resolution + win-rate across **clean / heavy-no-ally / heavy-with-ally / all-savage**; the heavy-with-ally state (enraged former ally mid-gauntlet) is a distinct shape needing its own scenario.

**Remaining content (yours):** 2 combat-death ending texts (LossGuardians, LossDebt-in-combat), ally-fallback lines (`AlliesFellBackEvent`), Refuse/Swap choice UI button copy.

**Remaining presentation tails:** Blocking `WeighingDialoguePanel` (currently toasts), `DebtChoiceGateEvent` buttons (currently toast), GameOverScreen epilogue routing per ending cause.

**Open issues:** none blocking. Strawman tier thresholds in `AuditScorer` are tunable (TASK-011). Trim pass on Debt dialogue content needed once it pages in-game (Lady's first two pages are prime targets).

**Refused-Sasha resolved (2026-06-01):** a refusal is NOT a death — it records no past-Sasha corpse (a living man's body doesn't belong in the catalog of the dead). `Main.OnGameEnded` suppresses corpse-creation on the `weighing_loss_refused` cause and instead increments `UnderWarden.WeighingRefusals`. Future content: the Under-Warden can reference prior refusals (a memo/audit line — "the visiting party has declined before; the case remains open"). No past-Sasha schema work.

**Direction (2026-06-06): balance leads now.** The content-first hold (2026-06-01, below) is lifted — the audit spine landed, so Guardian-soak can tune against real narration rhythm. Refocusing on balance per the project's north star (measured, not guessed). TASK-011 + a Weighing-soak scenario set is the active workstream.

**Superseded — content-first hold (2026-06-01):** Rafe+Claude-Chat draft the audit dialogue first (the spine), then per-Guardian rise text (per tier), ally-fallback lines, six ending texts, Hollowmark through the Weighing — written against the locked rise order, anchors, and the orchestration events (`GuardianRoseEvent`/`AlliesFellBackEvent`/`DebtRoseEvent`/`WeighingResolvedEvent`). TASK-011 balance pass was HELD until content landed. (Spine is now in; hold lifted.)

**TASK-003 detail (on the record):** "unprovoked" = victim never attacked Sasha's side this run. Sticky `HasAttackedPlayerTag` on monsters, set in `TurnController.UpdateKnowledge` on any attack against the player OR a player-ally (hit or miss; never cleared). Player kill of an un-tagged monster → run-scoped `RunAggressionTally` on the player (carried across floors, fresh per run) → flushed to `UnderWarden.cumulative_unprovoked_kills` at run end. **Revived the dead orc-rep Hostile transition** (`UnprovokedOrcKillsThisRun` now reads the tally — single source of truth).

**Possession loophole (closed):** a kill counts as Sasha's even through a host he is possessing (`ExcessKillEvaluator.DealtByPlayer`: own body OR `PossessionEffect{PlayerInitiated, possessor==player}`). Hosts possessed by anything else (WardenInitiated, NPC-on-NPC, enraged allies) do NOT count. Predicate is still victim-provoked; only the killer-identity gate widened. See memory `project_unprovoked_kill_definition`.

## Build order rationale

Front-load the **pure-logic, harness-testable spine** (Chunk A) before the AI-touching (Chunk B) and presentation/orchestration (Chunk C) work. The spine is the convergence point the whole design rests on ("everything feeds the Weighing"), it has zero Godot dependency, and de-risks the rest by giving the AI/orchestration work a tested foundation to attach to. Matches the project's measure-first philosophy.

---

## Chunk A — Pure-logic spine (no Godot, fully harness-testable)

- ✅ **TASK-001 — Weighing type taxonomy.** `src/Logic/Endgame/`: `EndingType` (None + 3 wins + 3 losses, closed set per decision 8), `GuardianId` (4 faction Guardians + Debt), `GuardianTier` (Allied/Diminished/Neutral/Savage), `WeighingOutcome` (InProgress/Survived/DiedToGuardians/DiedToDebt/Refused), `WeighingConstants` (FinalFloorDepth=25, the three loss cause-code strings). Acceptance: types compile, closed-set tests pass.
- ✅ **TASK-002 — Audit scoring function.** `AuditScorer` (static, deterministic). Per-Guardian tier functions over existing persistence fields + the excess metric, plus `DetermineEnding`. Strawman thresholds from decision 5/6, documented as tunable. Read-side excess field added to `UnderWardenData` (`cumulative_unprovoked_kills`, Dict<string,int>, default-add, no migration). Acceptance: tier-boundary + ending-determination unit tests pass.
- ✅ **TASK-003 — Excess metric write side.** Sticky `HasAttackedPlayerTag` (monster, set on monster→player attack) + run-scoped `RunAggressionTally` (player, carried across floors). Detection in `TurnController.UpdateKnowledge`; flush at run end in `Main.OnGameEnded`. Revives the dead orc-rep Hostile transition (`UnprovokedOrcKillsThisRun` now reads the tally). 6 tests in `tests/Endgame/UnprovokedKillTrackingTests.cs`. NOTE: the predicate ("never attacked you") had no existing distinction to reuse — it was net-new and is a design decision (see Current State / memory).

## Chunk B — Ally combat AI (touches core targeting) — ✅ COMPLETE

- ✅ **TASK-004 — `player_ally` faction.** `FactionRegistry`: `IsPlayerSide`, `PlayerFaction`/`PlayerAllyFaction` consts; ally friendly to player+allies, mutually hostile with all monster factions; target priorities (monster→ally 8, ally→monster 6). Tests in `tests/Endgame/PlayerAllyFactionTests.cs`.
- ✅ **TASK-005 — `ChooseTarget` gate.** Player candidate gated behind `AreHostile(myFaction, "player")`; faction-aware fallback (allies return self-sentinel → Decide idles). Allies fight monsters, never Sasha; monsters can target allies; allies ignore each other. Full suite regression clean.
- ✅ **TASK-006 — Friendly-fire surface.** Audited every harm site. Auto-targeting vectors fixed (player-side caster skips player-side targets): AoE (`ResolveEarthquake`), nearest-enemy auto-target (`FindClosestVisibleEnemy`), possession validity (`IsValidTarget` rejects player-side). Movement doesn't bump-attack (ally blocks the tile); momentum bonus attack reuses the chosen defender (no auto-retarget); throw is single-tile + user-aimed — all non-vectors, documented. A *turned* (enraged) ally loses friendly-fire protection.
- ✅ **TASK-007 — Guardian-possesses-allies.** `GuardianAbilities.TurnAllyHostile` applies `EnragedEffect` (HostileToAll) — NOT PossessionEffect (decision 3). Verified: enraged ally targets Sasha; spell-break (Dispel) removes the enrage and restores player_ally behavior; turned ally is AoE-able. Aggression set-site extended to "attacked player OR ally".

## Chunk C — Win scaffold + orchestration + endings (floor build + presentation)

- ✅ **TASK-008 — Win scaffold.** Dungeon victory state (`GameState.Ending`/`IsDungeonVictory`; `IsGameOver` fires on terminal ending), `WeighingConstants.IsWeighingFloor`, ASCII arena loader (`WeighingArena`/`WeighingArenaLoader`), the authored Tribunal Hall (`WeighingArenaDefinition`), the floor-25 gate + `BuildWeighingArena`, and the win-flush in `Main.OnGameEnded`. 14 tests in `tests/Endgame/WinScaffoldTests.cs`.
- ✅ **TASK-009 — Sequential orchestration.** `WeighingOrchestrator` (+ `WeighingState`, phase machine, events): begin-on-first-turn, rise-in-order at anchors/tiers, allied-vs-hostile, allies-fall-back, Debt-alone, resolve→ending. Hooked into `TurnController`. Placeholder Guardian stats. 11 tests in `tests/Endgame/WeighingOrchestratorTests.cs`.
- ✅ **TASK-010 — Ending + loss routing (logic).** `DetermineEnding` wired to the orchestration outcome; `GameState.Ending` set; loss cause-codes set on `PlayerDeathCause` (`weighing_loss_guardians/debt/refused`); `Refuse`/`ChooseSwap` mechanics. Presentation epilogue/dialogue routing is the content/UI tail (see Current State).
- ⬜ **TASK-009 — Sequential orchestration.** Sub-encounter state machine: audit-narration gates, spawn-on-cue per Guardian (rising as its category is read), the allies-fall-back-before-the-Debt gate, Debt solo phase. The keystone chunk (decision 1). Placeholder Guardian content.
- ⬜ **TASK-010 — Ending + loss routing.** `DetermineEnding` wired to the orchestration outcome; `GameOverScreen` routes on cause-code → correct final memo/epilogue; `weighing_loss_refused` routes from the audit choice (non-death). Decision 8.

## Chunk D — Balance (harness)

- ⬜ **TASK-011 — Guardian scaling balance pass.** Guardian-soak scenarios at varying record states; tune Guardian power + the strawman tier/ending thresholds so the wall is beatable-but-hard at intended skill/gear. Needs the harness; comes after framework + placeholder content.

---

## Content workstream (parallel, theirs — not engineering)

Tracked in `plan_end_game.md` "Content surfaces". Audit dialogue, per-Guardian rise text, ally-fallback lines, six ending texts, Hollowmark through the Weighing. Also: reconcile the held `final_audit` between-runs memos against the Weighing's audit (avoid redundancy) now that the audit shape is locked.
