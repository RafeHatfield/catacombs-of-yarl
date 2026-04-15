# Plan: Testing Infrastructure Phase 2 -- Bot Decision Telemetry

## Status: complete

## Current State
All 8 tasks implemented and verified. 1097 tests passing (9 new). JSONL contains `bot_summary` per run. `--verbose` prints action distribution and heal behavior table. Next: Phase 3 (survivability analysis consuming this data).

## Goal
Know *why* the bot died and *how* it spent its turns. Add per-decision telemetry to BotBrain that records action type, reason, HP state, and combat context for every decision. This data powers the survivability analysis in Phase 3 and enables diagnosing bot behavior regressions (e.g. "bot stopped healing at low HP after a code change").

## What This Unlocks
- Action distribution: what fraction of turns does the bot spend attacking vs healing vs moving?
- Heal threshold analysis: at what HP% does the bot actually heal? (compare against BotConfig thresholds)
- Deaths-with-unused-potions metric: the bot had potions but died anyway (heal logic bug or threshold too low)
- Combat context: how many decisions are made in-combat vs exploring?
- Reason distribution: "low_hp_heal" vs "attack_nearest" vs "retreat_choke" -- which decision paths fire most?

## PoC Reference
- `~/development/rlike/io_layer/bot_metrics.py` -- `BotDecisionTelemetry` (16 fields), `BotMetricsRecorder`, `BotRunSummary`
- `~/development/rlike/engine/soak_harness.py` -- how `BotMetricsRecorder` is wired into the run loop
- `~/development/rlike/tools/bot_survivability_report.py` -- how `BotRunSummary` is consumed for heal threshold analysis

## Current C# State
- `BotBrain.Decide(player, fighter, inventory, monsters, map)` returns `BotAction` -- no telemetry hooks
- `BotAction.ActionType` enum: `DoNothing`, `AttackTarget`, `HealSelf`, `MoveToward`, `MoveTo`
- `BotConfig.HealThreshold = 0.30`, `BotConfig.PanicThreshold = 0.15`
- `DungeonRunHarness.Run()` calls `BotBrain.Decide()` in a loop -- this is where the recorder would be wired
- `DungeonRunHarness` also has a separate pathfinding path for floor-clear navigation (not BotBrain) -- these steps should also be recorded as "navigate_to_stair" decisions
- `Inventory.Items` + `Consumable.IsHealing` for counting available healing potions

## Dependencies
- Phase 1 (TASK-001 through TASK-004) must be complete: `DungeonSoakRunResult` and `RunSoak()` exist
- `FloorRunMetrics` enrichment (Phase 1 TASK-005) is helpful but not blocking

## Tasks

### TASK-001: BotDecisionRecord struct
- Status: complete
- Files changed: `src/Logic/Balance/BotTelemetry.cs` (created)
- Layer: logic
- Type: system
- Dependencies: none
- Files to create: `src/Logic/Balance/BotTelemetry.cs`
- Description: Define the per-decision telemetry record. Port from PoC's `BotDecisionTelemetry`, adapted for C#. Use a readonly record struct for zero-allocation per-decision overhead.
- Implementation notes:
  - Fields (port from PoC, trimmed to what C# BotBrain actually knows):
    - `int TurnNumber` -- game turn when this decision was made
    - `int FloorDepth` -- current dungeon depth (1-based)
    - `string ActionType` -- "Attack", "Heal", "MoveToward", "MoveTo", "Wait", "Descend", "NavigateToStair"
    - `string Reason` -- human-readable reason string, e.g. "panic_heal", "threshold_heal", "attack_lowest_hp", "move_to_nearest", "retreat_to_choke", "navigate_stair", "floor_clear_wait"
    - `double HpFraction` -- player HP / MaxHP at decision time (0.0 to 1.0)
    - `int VisibleEnemies` -- count of alive monsters (proxy for "visible" since scenarios have full visibility)
    - `int AdjacentEnemies` -- count of alive monsters within Chebyshev distance 1
    - `int HealingPotionsAvailable` -- count of healing potions in inventory
    - `bool InCombat` -- true if adjacent enemies > 0
    - `bool LowHp` -- true if HpFraction <= BotConfig.HealThreshold
  - Use `readonly record struct` for value semantics and minimal allocation
  - All fields are init-only (set at creation time, immutable after)
- Acceptance criteria:
  - Struct compiles, has all listed fields
  - Can be created via `new BotDecisionRecord { TurnNumber = 1, ... }` syntax
  - No Godot dependencies

### TASK-002: IBotTelemetryRecorder interface and implementation
- Status: complete
- Files changed: `src/Logic/Balance/BotTelemetry.cs`
- Layer: logic
- Type: system
- Dependencies: TASK-001
- Files to modify: `src/Logic/Balance/BotTelemetry.cs` (add to same file)
- Description: Define the recorder interface and a concrete in-memory implementation. The interface allows the harness to inject telemetry collection without BotBrain depending on a specific recorder class.
- Implementation notes:
  - Interface `IBotTelemetryRecorder`:
    - `void Record(BotDecisionRecord decision)`
    - `BotRunSummary Summarize()`
    - `IReadOnlyList<BotDecisionRecord> Decisions { get; }`
  - Class `BotTelemetryRecorder : IBotTelemetryRecorder`:
    - Backs `Record()` with a `List<BotDecisionRecord>`
    - `Summarize()` computes `BotRunSummary` from collected decisions
    - Thread-safety: not needed (single-threaded bot loop)
  - Match PoC's `BotMetricsRecorder` pattern: `enabled` flag is implicit (null recorder = disabled; inject recorder = enabled)
- Acceptance criteria:
  - `Record()` appends to internal list
  - `Decisions` returns the full list
  - `Summarize()` returns valid `BotRunSummary` (see TASK-003)
  - Recording 10,000 decisions takes < 10ms (simple list append)

### TASK-003: BotRunSummary class
- Status: complete
- Files changed: `src/Logic/Balance/BotTelemetry.cs`
- Notes: DeathsWithUnusedPotions is computed in RunSingle() post-summarize so it correctly gates on whether the run ended in death (ComputeFrom() can't know that).
- Layer: logic
- Type: system
- Dependencies: TASK-001
- Files to modify: `src/Logic/Balance/BotTelemetry.cs` (add to same file, or separate file if it grows)
- Description: Aggregate stats computed from a run's decision records. Port from PoC's `BotRunSummary`.
- Implementation notes:
  - Fields:
    - `int TotalDecisions` -- total decisions recorded
    - `int FloorsVisited` -- distinct floor depths seen
    - `Dictionary<string, int> ActionCounts` -- count per ActionType string
    - `Dictionary<string, int> ReasonCounts` -- count per Reason string
    - `Dictionary<string, int> ContextCounts` -- count of: "in_combat", "exploring", "low_hp", "floor_clear"
    - `double AvgHpWhenHealing` -- average HpFraction across all Heal decisions
    - `int HealDecisions` -- count of heal actions (for computing avg)
    - `int DeathsWithUnusedPotions` -- 0 or 1 for a single run: if the run ended in death and `HealingPotionsAvailable > 0` on the last decision, this is 1
  - Context classification (from each decision record):
    - "in_combat" if `InCombat == true`
    - "exploring" if `InCombat == false && ActionType != "Descend"`
    - "low_hp" if `LowHp == true`
    - "floor_clear" if `VisibleEnemies == 0`
  - `AvgHpWhenHealing`: sum of HpFraction for all Heal decisions / count of Heal decisions
  - Serializable with `System.Text.Json` (dictionaries serialize as JSON objects)
- Acceptance criteria:
  - Given 100 decision records with known action types, `ActionCounts` sums correctly
  - `AvgHpWhenHealing` is accurate to 2 decimal places
  - `ContextCounts["in_combat"]` + other contexts may overlap (a decision can be both in_combat and low_hp)
  - JSON serialization produces valid output with snake_case property names

### TASK-004: Add telemetry to BotBrain.Decide()
- Status: complete
- Files changed: `src/Logic/Balance/BotBrain.cs`
- Notes: Used BotDecisionContext? as planned. EmitDecision() helper does one null check; CountHealingPotions() is a private helper on BotBrain (mirrors the one in DungeonRunHarness but scoped to BotBrain's needs).
- Layer: logic
- Type: system
- Dependencies: TASK-001, TASK-002
- Files to modify: `src/Logic/Balance/BotBrain.cs`
- Description: Add an optional `IBotTelemetryRecorder? recorder` parameter to `BotBrain.Decide()`. At each decision point, emit a `BotDecisionRecord` with the appropriate reason string. When `recorder` is null (default), zero overhead -- no allocation, no branching beyond the null check.
- Implementation notes:
  - Change signature: `public static BotAction Decide(Entity player, Fighter playerFighter, Inventory? inventory, List<Entity> monsters, GameMap map, IBotTelemetryRecorder? recorder = null)`
  - Default parameter means ALL existing callers (ScenarioHarness, DungeonRunHarness, tests) continue to work without changes.
  - Add a helper: `private static void EmitDecision(IBotTelemetryRecorder? recorder, ...)` that early-returns on null.
  - Reason strings for each decision path:
    - Panic heal: `"panic_heal"` (HP <= 15%)
    - Threshold heal: `"threshold_heal"` (HP <= 30%)
    - Retreat to choke: `"retreat_to_choke"`
    - Attack adjacent (focus fire): `"attack_lowest_hp"`
    - Move toward nearest: `"move_to_nearest"`
    - No action (no alive monsters): `"no_targets"`
  - Additional context needed at emit time (`TurnNumber`, `FloorDepth`) is NOT available in the current `Decide()` signature. Rather than adding loose optional parameters (which would give `Decide()` 8 parameters and invite further bloat), wrap the telemetry context in a `BotDecisionContext?` struct:
    ```csharp
    public readonly record struct BotDecisionContext(
        IBotTelemetryRecorder Recorder,
        int TurnNumber,
        int FloorDepth
    );
    ```
  - Revised signature: `public static BotAction Decide(Entity player, Fighter playerFighter, Inventory? inventory, List<Entity> monsters, GameMap map, BotDecisionContext? context = null)`
  - When `context` is null, no telemetry is emitted (same behavior as before -- all existing callers pass nothing and are unaffected).
  - When `context` is non-null, emit one `BotDecisionRecord` per call using `context.Value.Recorder`.
  - `BotDecisionContext` lives in `BotTelemetry.cs` alongside the other telemetry types.
  - This struct is the extension point: future context fields (persona, difficulty modifier, etc.) are added to `BotDecisionContext` without changing the `Decide()` signature again.
- Acceptance criteria:
  - `BotBrain.Decide(player, fighter, inventory, monsters, map)` still works (no context, backward compat)
  - `BotBrain.Decide(player, fighter, inventory, monsters, map, new BotDecisionContext(recorder, 5, 2))` emits exactly one decision record per call
  - Reason string is never empty when context is non-null
  - HpFraction in the record matches `playerFighter.Hp / playerFighter.MaxHp`
  - AdjacentEnemies count matches actual adjacent alive monsters
  - HealingPotionsAvailable count matches inventory scan

### TASK-005: Wire recorder into DungeonRunHarness
- Status: complete
- Files changed: `src/Logic/Balance/DungeonRunHarness.cs`, `src/Logic/Balance/DungeonSoakRunResult.cs`, `src/Logic/Balance/ScenarioHarness.cs`
- Notes: BotSummary typed as BotRunSummary? (replaced object? stub). enableTelemetry param on RunSingle() defaults to false for legacy Run(); RunSoak() always passes true. BuildNavigateRecord() helper emits NavigateToStair/Descend decisions from the harness path. TurnNumber is totalTurns + floorTurns + 1 for monotonic cross-floor ordering.
- Layer: logic
- Type: system
- Dependencies: TASK-004, Phase 1 TASK-003/004
- Files to modify: `src/Logic/Balance/DungeonRunHarness.cs`
- Description: When running soak mode, create a `BotTelemetryRecorder` per run, pass it to `BotBrain.Decide()` calls, and include the `BotRunSummary` in `DungeonSoakRunResult`.
- Implementation notes:
  - Add `bool enableTelemetry = false` parameter to `RunSoak()` (or the internal single-run method)
  - When telemetry enabled:
    - Create `new BotTelemetryRecorder()` at start of each run
    - Pass to every `BotBrain.Decide()` call with `turnNumber: state.TurnCount, floorDepth: depth`
    - Also record decisions for the "navigate to stair" path (when `IsFloorClear`): emit with ActionType="NavigateToStair", Reason="navigate_stair"
    - At run end: `recorder.Summarize()` -> store in `DungeonSoakRunResult.BotSummary`
  - Add `BotRunSummary? BotSummary` field to `DungeonSoakRunResult` (optional -- null when telemetry disabled)
  - When telemetry disabled: pass `null` context, no overhead
  - Telemetry is always enabled in soak mode (no reason to run 100 iterations without it)
  - **Also wire through ScenarioHarness**: `ScenarioHarness.RunOnce()` also calls `BotBrain.Decide()`. Pass an optional `BotDecisionContext?` through `RunOnce()` and the public `Run()` method so scenario runs can also capture telemetry. This avoids a second pass over `ScenarioHarness` later. The scenario harness's `AggregatedMetrics` does not need to carry `BotRunSummary` yet -- but the recorder should be injectable for callers who want it.
- Acceptance criteria:
  - `RunSoak(3, 5, 1337)` with telemetry enabled: every `DungeonSoakRunResult.BotSummary` is non-null
  - `BotSummary.TotalDecisions > 0` for every run
  - `BotSummary.ActionCounts` contains at least "Attack" and "MoveToward" keys (bot always does both)
  - Existing `Run()` method still works without telemetry (no recorder passed)
  - Performance: telemetry adds < 5% overhead to soak run time

### TASK-006: Include BotRunSummary in JSONL output
- Status: complete
- Files changed: `tools/Harness/Program.cs` (no code change needed — existing soakOptions already had DictionaryKeyPolicy=null and DefaultIgnoreCondition=WhenWritingNull; changing BotSummary from object? to BotRunSummary? in the model was sufficient)
- Layer: logic (tools)
- Type: system
- Dependencies: TASK-005, Phase 1 TASK-007
- Files to modify: `tools/Harness/Program.cs`
- Description: When `--jsonl` is used with `--dungeon`, include the `bot_summary` object in each JSON line. Contains `action_counts`, `reason_counts`, `context_counts`, `avg_hp_when_healing`, `total_decisions`.
- Implementation notes:
  - `DungeonSoakRunResult` already has `BotSummary` from TASK-005
  - JSON serialization via `System.Text.Json` with `JsonNamingPolicy.SnakeCaseLower`
  - The `BotRunSummary` serializes as a nested object: `"bot_summary": { "total_decisions": 142, "action_counts": {"Attack": 45, "Heal": 8, ...}, ... }`
  - When `BotSummary` is null (telemetry disabled), the field should be omitted from JSON (use `JsonIgnoreCondition.WhenWritingNull`)
- Acceptance criteria:
  - JSONL lines include `bot_summary` when telemetry is enabled
  - `bot_summary.action_counts` is a valid JSON object
  - `bot_summary.avg_hp_when_healing` is a number (not NaN -- guard division by zero)
  - Round-trip: parse the JSON line, extract `bot_summary.total_decisions`, verify it matches

### TASK-007: --verbose flag for action distribution table
- Status: complete
- Files changed: `tools/Harness/Program.cs`
- Notes: PrintBotVerbose() aggregates across all runs. Uses OutcomeClassifier.Died constant for death count. DeathsWithUnusedPotions is already correctly scoped to death-runs in RunSingle().
- Layer: logic (tools)
- Type: system
- Dependencies: TASK-005
- Files to modify: `tools/Harness/Program.cs`
- Description: When `--dungeon --verbose` is used, print additional detail after the main soak table: aggregate action distribution across all runs, average HP when healing, and deaths-with-unused-potions count.
- Implementation notes:
  - Aggregate across all runs: sum each `BotRunSummary.ActionCounts` into a total, compute fractions
  - Print table:
    ```
    Bot Action Distribution (across all runs):
      Attack:          42.3%  (12,450 decisions)
      MoveToward:      35.1%  (10,330 decisions)
      Heal:             8.2%  (2,410 decisions)
      NavigateToStair: 12.1%  (3,560 decisions)
      MoveTo:           2.3%  (680 decisions)

    Heal Behavior:
      Avg HP% when healing: 27.3%
      Deaths with unused potions: 4 / 42 deaths (9.5%)
    ```
  - Skip if no telemetry data (all `BotSummary` are null)
- Acceptance criteria:
  - `--verbose` without `--dungeon` is ignored (or applies to scenario output as before)
  - Action percentages sum to ~100% (rounding)
  - "Deaths with unused potions" only counts runs where outcome is "died"

### TASK-008: Unit tests for Phase 2
- Status: complete
- Files changed: `tests/Balance/BotTelemetryTests.cs` (created — 10 tests, 9 pass in fast suite, 1 [Category("Slow")] integration test)
- Notes: CON 10 used in all test states so MaxHp == BaseMaxHp — clean HP fraction math. Fighter.MaxHp is computed, not settable; tests set HP by reducing fighter.Hp after construction.
- Layer: logic
- Type: test
- Dependencies: TASK-004, TASK-005
- Files to create: `tests/Balance/BotTelemetryTests.cs`
- Description: Test telemetry recording, summary computation, and BotBrain integration.
- Tests to write:
  1. **Recorder captures decisions**: Create recorder, call `Record()` 5 times with known data, verify `Decisions.Count == 5`
  2. **BotBrain with null recorder**: `BotBrain.Decide()` with `recorder: null` still returns correct actions (no crash, no NRE)
  3. **BotBrain with recorder**: Set up a simple combat state (player + 1 monster adjacent), call `Decide()` with recorder, verify exactly 1 decision recorded with ActionType="Attack"
  4. **BotBrain heal reason**: Set up player at 20% HP with healing potion, no adjacent enemies. Call `Decide()` with recorder. Verify reason is "threshold_heal" and HpFraction is ~0.2.
  5. **Summary action counts**: Record 10 Attack + 5 Heal + 3 MoveToward decisions. Verify `Summarize().ActionCounts["Attack"] == 10`
  6. **Summary avg HP when healing**: Record 3 heal decisions at HpFraction 0.15, 0.25, 0.30. Verify `AvgHpWhenHealing ~= 0.233`
  7. **Summary context counts**: Record 5 decisions with InCombat=true, 3 with InCombat=false. Verify `ContextCounts["in_combat"] == 5`
  8. **Soak with telemetry**: `RunSoak(2, 3, 1337)` with telemetry enabled -- every run has non-null BotSummary with TotalDecisions > 0
- Acceptance criteria:
  - All tests pass with `dotnet test --filter "Category!=Slow"`
  - Tests do not require Godot
  - No test depends on specific combat outcomes (use deterministic seed where needed)

## Files Summary

### New files
- `src/Logic/Balance/BotTelemetry.cs` -- `BotDecisionRecord`, `IBotTelemetryRecorder`, `BotTelemetryRecorder`, `BotRunSummary`
- `tests/Balance/BotTelemetryTests.cs` -- unit tests

### Modified files
- `src/Logic/Balance/BotBrain.cs` -- add optional recorder + reason strings to `Decide()`
- `src/Logic/Balance/DungeonRunHarness.cs` -- wire recorder into run loop
- `src/Logic/Balance/DungeonSoakRunResult.cs` -- add `BotRunSummary? BotSummary` field
- `tools/Harness/Program.cs` -- `--verbose` flag, BotSummary in JSONL

## Risks and Open Decisions
1. **Signature bloat**: Resolved by using `BotDecisionContext?` struct. Callers that don't need telemetry pass nothing (default null). Future context fields are added to the struct without changing the `Decide()` signature.
2. **Reason string stability**: These strings become part of the data format (JSONL, reports). Changing them later breaks downstream parsing. Mitigate: use string constants, document them. Not an enum because new reasons can be added without breaking serialization.
3. **NavigateToStair telemetry**: The stair-navigation path in `DungeonRunHarness` is NOT inside `BotBrain.Decide()` -- it's in the harness loop itself. Must emit telemetry manually from the harness for these decisions. This is a harness concern, not a BotBrain concern.
4. **HealingPotionsAvailable counting**: Requires scanning the full inventory every decision. For a 10-item inventory, this is trivial. But if inventory grows or scanning becomes expensive, consider caching. Not a concern at current scale.
