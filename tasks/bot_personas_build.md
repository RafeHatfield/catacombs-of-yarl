# Bot Personas Build Task File

## Current State

Implementation complete through TASK-011. 1873 tests passing (was 1838).
TASK-012 requires manual Godot testing — not available in this session.

Next: mark for review. TASK-012 needs to be done when Godot is available.

---

## Tasks

- [x] TASK-001: Introduce `BotPersonaConfig` record + 5 hardcoded defaults
  - Status: complete
  - Files changed:
    - `src/Logic/Balance/BotPersonaConfig.cs` (new)
    - `src/Logic/Balance/BotPersonaRegistry.cs` (new)
    - `src/Logic/Balance/ScenarioHarness.cs` (BotConfig: const → static readonly)
    - `tests/Balance/BotPersonaConfigTests.cs` (new, 15 tests)
  - Notes: BotConfig.HealThreshold and PanicThreshold changed from `const double` to `static readonly double`. Safe because they were never used as compile-time constants.

- [x] TASK-002: YAML loader for `config/bot_personas.yaml`
  - Status: complete
  - Files changed:
    - `config/bot_personas.yaml` (new)
    - `src/Logic/Content/BotPersonaLoader.cs` (new)
    - `src/Logic/Balance/BotPersonaRegistry.cs` (LoadFromFile added)

- [x] TASK-003: Refactor `BotBrain.Decide` to accept `BotPersonaConfig`
  - Status: complete
  - Files changed:
    - `src/Logic/Balance/BotBrain.cs` (full rewrite: static class → sealed class with instance mode)
    - `src/Logic/Balance/BotTelemetry.cs` (Persona field added to BotDecisionRecord, BotDecisionContext, BotRunSummary)
    - `src/Logic/Balance/RunMetrics.cs` (WasAborted field added)
    - `src/Logic/Balance/OutcomeClassifier.cs` (Aborted outcome + FailureAborted constant)
    - `src/Logic/Balance/ScenarioHarness.cs` (3-way dispatch, instance BotBrain, AbortRun handling)
    - `src/Logic/Balance/DungeonRunHarness.cs` (instance BotBrain, AbortRun, persona field)
    - `src/Logic/Balance/DungeonSoakRunResult.cs` (WasAborted and Persona fields)
  - Notes:
    - Panic heal now requires 2+ adjacent enemies (aligning to PoC). This caused depth5_zombie_fine death rate drift (+18pp). Baseline updated — new behavior is PoC-correct.
    - Engagement distance NOT applied to rule 6 (move toward) for non-avoid-combat personas. Without an EXPLORE state, applying the distance cap would freeze the bot on large dungeon floors where all enemies start far away.
    - For avoid-combat personas (cautious, speedrunner), enemies beyond engagement distance are ignored (bot waits) — matching PoC.
    - Baseline updated: `dotnet run --project tools/Harness -- --suite --fast --update-baseline`

- [x] TASK-004: STUCK detection + AbortRun
  - Status: complete (implemented within TASK-003 refactor)
  - Files changed: see TASK-003
  - Notes:
    - Drop threshold: 8. Counter does NOT reset after drop — keeps climbing to abort threshold.
    - Abort threshold: 15.
    - Static path: no stuck detection (transient instance per call). Instance path: stuck state persists across turns.
    - `tests/Balance/BotBrainStuckTests.cs` (new, 6 tests)

- [x] TASK-005: Persona field in telemetry
  - Status: complete (implemented within TASK-003)
  - Notes: BotDecisionRecord.Persona, BotDecisionContext.Persona (with default "balanced"), BotRunSummary.Persona all added.

- [x] TASK-006: `--persona` flag + instance wiring
  - Status: complete
  - Files changed:
    - `tools/Harness/Program.cs` (--persona and --bot-report flags, resolve persona, wire through)
    - `src/Logic/Balance/ScenarioRunner.cs` (RunFromFile gains persona parameter)
  - Notes: YAML player_bot wins over CLI persona for ranged_net_arrow scenarios (3-way dispatch in ScenarioHarness).

- [x] TASK-007: `--bot-report` (survivability matrix)
  - Status: complete
  - Files changed:
    - `tools/Harness/BotSurvivabilityReport.cs` (new)
    - `tools/Harness/Program.cs` (--bot-report mode, --matrix flag)
  - Notes: cautious and speedrunner show 0% death rate in arena scenarios (avoid_combat personas never engage). This is expected behavior — they hit the turn limit rather than fight.

- [x] TASK-008: Comprehensive persona behavior tests
  - Status: complete
  - Files changed:
    - `tests/Balance/BotBrainPersonaTests.cs` (new, 9 tests)
    - `tests/Balance/BotBrainStuckTests.cs` (new, 6 tests)

- [x] TASK-009: BotPlayerDriver Godot node + injection point
  - Status: complete
  - Files changed:
    - `src/Presentation/GameController.cs` (SubmitBotAction public method added)
    - `src/Presentation/Bot/BotPlayerDriver.cs` (new)
    - `src/Logic/Balance/BotActionConverter.cs` (new — extracted from DungeonRunHarness)
    - `src/Logic/Balance/DungeonRunHarness.cs` (refactored to use BotActionConverter)

- [x] TASK-009b: BotPlayerDriver exploration + floor-clear logic
  - Status: complete (implemented in BotPlayerDriver.cs)
  - Notes:
    - Visible-monster filtering: only passes monsters visible in FOV to BotBrain.Decide
    - Floor-clear → Descend: when AliveMonsters.Count == 0 and player on stair → Descend
    - Auto-explore integration: StartAutoExplore() used (not PlayerAction.AutoExplore which doesn't exist)
    - Game-over: Disable() called on IsGameOver

- [x] TASK-010: F4 hotkey + debug-menu + HUD
  - Status: complete
  - Files changed:
    - `src/Presentation/Main.cs` (BotPlayerDriver instantiation, F4/F5/F6 handlers)
    - `src/Presentation/Bot/BotModeHud.cs` (new)
  - Notes: Driver only instantiated when OS.IsDebugBuild(). F4 toggles, F5 cycles personas, F6 cycles speeds.

- [x] TASK-011: Full 5×15 matrix run
  - Status: complete
  - Files changed:
    - `reports/bot_survivability_v1.md` (new — 5×15 table committed)
  - Notes:
    - cautious and speedrunner show 0% death on all 15 scenarios (avoid_combat=true personas hit turn limit in arena scenarios, never engage)
    - aggressive shows higher death rates than balanced on depth3_orc_brutal and depth5_zombie variants as expected
    - greedy behaves identically to balanced (no floor loot in these arena scenarios, LootPriority only affects potion search radius)
    - depth5_zombie_keen at 94% death rate for balanced/aggressive/greedy — this scenario is extremely lethal even with the fine weapon

- ⬜ TASK-012: Manual smoke test (requires Godot)
  - Status: not started — requires Godot editor to run
  - Note: Graphical bot mode code is complete. Once Godot is available:

## Manual Smoke Test Checklist (TASK-012)

_To be completed when Godot testing is available._

- [ ] Bot mode toggles on with F4. HUD appears.
- [ ] Bot moves and attacks on each timer tick.
- [ ] Bot drinks a potion when low HP (visible in HUD + toast log).
- [ ] Bot descends a staircase when the floor is clear.
- [ ] Bot survives at least one floor transition without crash.
- [ ] Persona swap via F5 changes behavior visibly within 5 turns.
- [ ] Speed swap via F6 changes tick rate visibly.
- [ ] Toggling off returns control to human input (tap an adjacent tile, see the player move).

---

## Key Design Decisions

- Manhattan distance for CombatEngagementDistance (matching PoC). Rest of BotBrain uses Chebyshev.
- Engagement distance NOT applied as a movement gate for non-avoid-combat personas — prevents freeze on large dungeon floors.
- Panic heal requires 2+ adjacent enemies (PoC-correct). This changed balanced behavior from the old implementation. Baseline updated.
- Stuck counter does NOT reset when dropping target — keeps climbing to abort threshold (15).
- Static BotBrain.Decide: no stuck detection (transient instance per call). Instance path: persists.
- Cautious/speedrunner in arena scenarios: 0% death by hitting turn limit (expected — avoid_combat=true).
