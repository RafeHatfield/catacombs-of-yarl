# Plan: Testing Infrastructure Phase 1 -- Dungeon Soak CLI

## Status: complete

## Goal
Add a `--dungeon` mode to the balance harness that runs the bot through N procedural dungeon floors for M iterations, producing rich per-run outcome data with failure classification. This is the foundation for automated balance regression detection -- "did this change make the bot die more often on floor 3?"

## What This Unlocks
- Automated regression detection for balance changes (death rate spikes by floor)
- Failure classification: know whether deaths are combat deaths, stuck-bot bugs, or turn limit hits
- JSONL output for downstream analysis (Phase 3 reports, CI integration)
- Per-floor survival curves across 100+ runs

## PoC Reference
- `~/development/rlike/engine/soak_harness.py` -- `SoakRunResult` dataclass (fields, `classify_failure()`, `SoakSessionResult`)
- `~/development/rlike/engine/soak_harness.py` -- `run_bot_soak()` orchestration loop
- `~/development/rlike/io_layer/bot_metrics.py` -- `BotRunSummary` (referenced in Phase 2, but shapes the data model here)

## Current C# State
- `DungeonRunHarness.Run(floors, baseSeed)` exists -- runs one bot through N floors, returns `DungeonRunResult`
- `DungeonRunResult` has: Seed, FloorsAttempted, FloorsCompleted, TotalTurns, TotalKills, FinalHp, PlayerDied, PerFloor[]
- `FloorRunMetrics` has: Depth, TurnsTaken, MonstersKilled, PlayerHpAtEnd, PlayerDied, Descended
- `tools/Harness/Program.cs` supports `--scenario`, `--all`, `--json`, `--runs`, `--seed` -- no dungeon mode
- `DungeonRunHarness` uses `MaxTurnsPerFloor = 500` and `DungeonFloorTurnLimit = 2000`
- `DeathEvent` has `ActorId` and `KillerId` -- can identify what killed the player
- `Entity.Name` gives the monster name (e.g. "orc_brute")
- `GameState.PlayerFighter.Hp/MaxHp` for HP fraction at end of run
- `Inventory.Items` + `Consumable.IsHealing` for counting remaining potions

## Dependencies
- None. This is the foundation phase.

## Tasks

### TASK-001: DungeonSoakRunResult data class
- Status: complete
- Layer: logic
- Type: system
- Dependencies: none
- Files to create: `src/Logic/Balance/DungeonSoakRunResult.cs`
- Description: Create the per-run result class with outcome classification. Port the field set from PoC's `SoakRunResult`, adapted for C#'s type system.
- Acceptance criteria:
  - `DungeonSoakRunResult` is a sealed class (not record -- mutable during construction)
  - Fields: `int Seed`, `string Outcome` (enum string: "survived", "died", "stuck", "max_turns", "exception"), `string FailureType` ("none", "death", "max_turns", "stuck", "exception"), `string FailureDetail` (killer name, turn limit detail, or exception message), `int DeepestFloorReached`, `int FloorsCompleted`, `int TotalTurns`, `int TotalKills`, `int FinalHp`, `int FinalMaxHp`, `double FinalHpFraction`, `int PotionsUsed`, `int PotionsRemaining`, `int BoonsAcquired`, `double DurationSeconds`, `IReadOnlyList<FloorRunMetrics> PerFloor`
  - `DurationSeconds`: wall-clock time for the run, captured via `Stopwatch`. Free diagnostic data for detecting performance regressions (e.g. "floor gen time doubled after adding new monster type").
  - `Outcome` uses string constants, not an enum (matches PoC pattern, avoids serialization friction)
  - Class compiles with `dotnet build` (no Godot dependency)

### TASK-002: Outcome classification logic
- Status: complete
- Layer: logic
- Type: system
- Dependencies: TASK-001
- Files to create: `src/Logic/Balance/OutcomeClassifier.cs`
- Description: Port `classify_failure()` from PoC's `SoakRunResult.classify_failure()`. Simplified for C# dungeon runs (no auto-explore, no libtcod concerns). The classifier takes the raw `DungeonRunResult` + last `TurnResult` events and produces the outcome/failure_type/failure_detail triple.
- Implementation notes:
  - Input: `DungeonRunResult`, plus the last `TurnResult` from the floor where the run ended (needed to extract the killer from `DeathEvent`)
  - To get the killer name: find the `DeathEvent` where `ActorId == player.Id`, then look up entity by `KillerId` to get `Entity.Name`. Since entities may be dead by run end, the harness must capture the killer name at death time.
  - Outcome classification:
    - Player died (`DungeonRunResult.PlayerDied == true`) -> outcome="died", failure_type="death", failure_detail=killer entity name
    - All floors completed (`FloorsCompleted == FloorsAttempted`) -> outcome="survived", failure_type="none"
    - Turn limit hit on a floor (floor's `TurnsTaken >= MaxTurnsPerFloor` AND not died AND not descended) -> outcome="max_turns", failure_type="max_turns", failure_detail="Floor {depth}: hit {MaxTurnsPerFloor} turn limit"
    - Bot stuck (same as turn limit for now -- revisit in Phase 2 when we have telemetry to distinguish stuck from slow)
    - **Exception during run** -> outcome="exception", failure_type="exception", failure_detail=exception message. Handled in `RunSoak()` (see TASK-004), not by Classify() itself. Classify() only needs the first four outcomes.
  - Static method: `OutcomeClassifier.Classify(DungeonRunResult result, string? killerName) -> (string outcome, string failureType, string failureDetail)`
- Acceptance criteria:
  - `Classify()` returns correct outcome for: death, survival, max_turns
  - Killer name is included in failure_detail for death outcomes
  - Method is a pure function with no side effects
  - Unit test covers all four outcome paths (including a null killerName for death with unknown killer)

### TASK-003: Enrich DungeonRunHarness.Run() to capture death context
- Status: complete
- Layer: logic
- Type: system
- Dependencies: TASK-001, TASK-002
- Files to modify: `src/Logic/Balance/DungeonRunHarness.cs`
- Description: Modify the existing `Run()` method to track additional context needed for `DungeonSoakRunResult`: killer name, potions used, potions remaining, boons acquired. The method must track the killer entity name at the moment of death (before entity cleanup), and count healing potions used/remaining from the event stream and inventory.
- Implementation notes:
  - Track `killerName`: when a `DeathEvent` fires where `ActorId == player.Id`, look up the killer entity in `state.Monsters` using `state.Monsters.FirstOrDefault(m => m.Id == deathEvent.KillerId)?.Name`. Must happen inside the turn loop at the moment of death. Note: dead monsters remain in `state.Monsters` (they are not removed until the next floor) so the lookup works even if the killer died in the same turn.
  - Track `potionsUsed`: count `HealEvent` instances where **`ActorId == player.Id`** across all turn results. Do NOT count all HealEvents -- monsters that carry potions can backfire-heal the player, emitting a HealEvent that isn't a player potion use. The existing `RunMetrics.RecordTurn` has this same bug (no actor filter); do not copy that pattern here.
  - Track `potionsRemaining`: at run end, count items in `state.PlayerInventory` where `item.Get<Consumable>()?.IsHealing == true`.
  - Track `boonsAcquired`: `state.BoonTracker?.BoonsApplied.Count ?? 0` at run end.
  - Do NOT change the return type of `Run()` yet -- just capture the data internally. The new `RunSoak()` method (TASK-004) will use this.
  - Alternative: create a private helper `RunSingle()` that returns `DungeonSoakRunResult` directly, and have the existing `Run()` call it (preserving backward compatibility).
- Acceptance criteria:
  - Existing `DungeonRunTests` still pass (no behavioral change to `Run()`)
  - Killer name is captured when player dies (not null/empty)
  - Potion tracking matches the event stream
  - `dotnet test --filter "Category!=Slow"` passes

### TASK-004: DungeonSoakSummary and RunSoak() method
- Status: complete
- Layer: logic
- Type: system
- Dependencies: TASK-003
- Files to create: `src/Logic/Balance/DungeonSoakSummary.cs`
- Files to modify: `src/Logic/Balance/DungeonRunHarness.cs`
- Description: Add multi-run aggregation. `RunSoak(int floors, int runs, int baseSeed)` runs N dungeon campaigns with seeds `baseSeed + i` (i = 0..runs-1), collecting `DungeonSoakRunResult` per run. Returns `DungeonSoakSummary` with aggregate stats.
- Implementation notes for `DungeonSoakSummary`:
  - Fields: `int RunsAttempted`, `int RunsSurvived`, `double SurvivalRate`, `double AvgFloorsCompleted`, `double AvgTotalTurns`, `double AvgTotalKills`, `IReadOnlyList<DungeonSoakRunResult> Runs`
  - `Dictionary<int, double> DeathRateByFloor` -- key is depth (1-based), value is fraction of runs where player died on that floor
  - `Dictionary<string, int> FailureTypeCounts` -- counts per failure_type string
  - `Dictionary<string, int> KillerCounts` -- counts per killer name (from failure_detail when failure_type=="death")
  - `double[] SurvivalCurve` -- survival_curve[d] = fraction of runs where player reached floor d+1 (0-indexed). E.g. survival_curve[0] = 1.0 (everyone starts floor 1), survival_curve[1] = fraction reaching floor 2.
  - Computed from the list of `DungeonSoakRunResult` via a `ComputeFrom(List<DungeonSoakRunResult>)` static method.
- Implementation notes for `RunSoak()`:
  - Signature: `DungeonSoakSummary RunSoak(int floors, int runs, int baseSeed = 1337)`
  - Seed per run: `baseSeed + i` for i in 0..runs-1 (matches PoC pattern)
  - **Wrap each run in try/catch.** On exception: create a `DungeonSoakRunResult` with `Outcome="exception"`, `FailureType="exception"`, `FailureDetail=ex.Message`, `Seed=baseSeed+i`, `FloorsCompleted=0`. Log to stderr. Continue to next run -- do not abort the whole session.
  - Calls the enriched single-run method from TASK-003 for each run
  - Aggregates via `DungeonSoakSummary.ComputeFrom()`
  - Include `"exception"` in `FailureTypeCounts` aggregation
- Acceptance criteria:
  - `RunSoak(floors: 3, runs: 10, baseSeed: 1337)` returns a valid summary
  - `SurvivalRate` is in [0.0, 1.0]
  - `DeathRateByFloor` keys cover only depths where deaths occurred
  - `SurvivalCurve` is monotonically non-increasing
  - Determinism: `RunSoak(3, 5, 1337)` == `RunSoak(3, 5, 1337)` (same aggregate stats)

### TASK-005: Enrich FloorRunMetrics
- Status: complete
- Layer: logic
- Type: system
- Dependencies: none (can be done in parallel with TASK-001)
- Files to modify: `src/Logic/Balance/DungeonRunHarness.cs` (the `FloorRunMetrics` class is defined here)
- Description: Add fields to `FloorRunMetrics` that the soak report needs per-floor: `PlayerMaxHp` (for HP fraction calculation), `PotionsUsed` (on this floor), and `HitMaxTurns` (bool: did this floor end because of the turn cap rather than descent or death).
- Implementation notes:
  - Add: `int PlayerMaxHp { get; set; }`, `int PotionsUsed { get; set; }`, `bool HitMaxTurns { get; set; }`
  - Set `PlayerMaxHp` from `state.PlayerFighter.MaxHp` at floor end
  - Set `PotionsUsed` by counting `HealEvent` instances in the turn results for this floor
  - Set `HitMaxTurns = (floorTurns >= MaxTurnsPerFloor && !floorMetrics.Descended && !floorMetrics.PlayerDied)`
- Acceptance criteria:
  - Existing `DungeonRunTests` still pass
  - `PlayerMaxHp > 0` for all floor metrics
  - `HitMaxTurns` is true only when the turn cap was the reason the floor ended

### TASK-006: --dungeon CLI mode in Harness
- Status: complete
- Layer: logic (tools)
- Type: system
- Dependencies: TASK-004
- Files to modify: `tools/Harness/Program.cs`
- Description: Add `--dungeon` flag to the harness CLI. When set, runs `DungeonRunHarness.RunSoak()` instead of the scenario harness. Supports existing `--runs` and `--seed` flags plus new `--floors` flag.
- Implementation notes:
  - New flags: `--dungeon` (bool), `--floors N` (default 6)
  - Requires building a `DungeonFloorBuilder` -- needs `ContentLoader`, `LevelTemplateRegistry`, and ALL factories. Reference `DungeonRunTests.Setup()` as the starting point, but note it is incomplete for real gameplay: it omits `SpellItemFactory` and boon loading. The soak results must reflect actual gameplay (wands/scrolls spawn, depth boons apply).
  - Full factory setup required: `ContentLoader.LoadAllFromFile(entitiesPath)` -> `ItemFactory`, `MonsterFactory`, `ConsumableFactory`, `SpellItemFactory`. Also load `config/level_templates.yaml` via `LevelTemplateRegistry.FromFile()`.
  - Load `config/entities.yaml` and `config/level_templates.yaml`
  - Check whether `BoonTable` / `DepthBoonConfig` need to be passed to `DungeonFloorBuilder`. If boon loading requires a separate config, document it here and load it.
  - Print a console table on completion:
    ```
    === YARL Dungeon Soak ({runs} runs, seed {seed}, {floors} floors) ===

    Survival rate: {rate}%
    Avg floors completed: {avg}
    Avg total turns: {avg}

      Depth   Death%   Avg Turns   Avg Kills   Survival%
      -----   ------   ---------   ---------   ---------
          1    12.0%        45.3         3.2      88.0%
          2    18.0%        52.1         4.1      72.2%
          ...

    Failure Types:
      death: 42
      max_turns: 3
      stuck: 1

    Top Killers:
      orc_brute: 15
      orc_chieftain: 12
      zombie: 8
    ```
  - Validate that `--dungeon` and `--scenario`/`--all` are mutually exclusive
  - Default runs: 100 (not from YAML -- dungeon mode has no scenario YAML)
- Acceptance criteria:
  - `dotnet run --project tools/Harness -- --dungeon --floors 3 --runs 10 --seed 1337` produces the table output
  - `dotnet run --project tools/Harness -- --dungeon --help` (or just `--help`) mentions the new flags
  - Mutually exclusive: `--dungeon --scenario foo` prints an error
  - Exit code 0 on success

### TASK-007: --jsonl output flag
- Status: complete
- Layer: logic (tools)
- Type: system
- Dependencies: TASK-006
- Files to modify: `tools/Harness/Program.cs`
- Files to create: (serialization may be inline in Program.cs or a small helper)
- Description: Add `--jsonl <path>` flag that writes one JSON line per run to the specified file. Each line is the JSON serialization of `DungeonSoakRunResult`. Works for `--dungeon` mode. Creates parent directories if needed.
- Implementation notes:
  - Use `System.Text.Json.JsonSerializer.Serialize()` per run result
  - Serialize `PerFloor` as a nested array of objects
  - **Property naming**: use `JsonNamingPolicy.SnakeCaseLower` for property names. **IMPORTANT**: Set `DictionaryKeyPolicy = null` (not SnakeCaseLower). Dictionary keys like `"Attack"` and `"orc_brute"` are data values, not property names -- applying SnakeCaseLower would mangle them (e.g. `"Attack"` -> `"attack"`), breaking downstream analysis that keys on action type names.
  - **Stream writes, do not batch.** Write and flush each line immediately after each run completes. A 1000-run soak can take 10+ minutes; batching loses all data on Ctrl-C or crash. Use a `StreamWriter` opened at start, flushed after each `WriteLine()`. Phase 3's `SoakJsonlReader` already handles partial/malformed files.
  - Also support `--jsonl` with `--all` mode: write one line per scenario with the `AggregatedMetrics` serialized as JSON
  - Ensure `reports/` directory exists (create if needed via `Directory.CreateDirectory`)
- Acceptance criteria:
  - `dotnet run --project tools/Harness -- --dungeon --floors 3 --runs 5 --jsonl reports/test_soak.jsonl` creates the file
  - Each line is valid JSON parseable by `JsonDocument.Parse()`
  - File has exactly N lines where N = number of runs
  - Property names are snake_case (e.g. `floors_completed`, not `FloorsCompleted`)
  - `--jsonl` without a path argument prints an error

### TASK-008: Unit tests for Phase 1
- Status: complete
- Layer: logic
- Type: test
- Dependencies: TASK-004, TASK-005
- Files to create: `tests/Balance/DungeonSoakTests.cs`
- Description: Test the new soak infrastructure. Focus on determinism, outcome classification, and data integrity.
- Tests to write:
  1. **Determinism**: `RunSoak(3, 5, 1337)` produces identical `SurvivalRate`, `AvgFloorsCompleted`, and per-run outcomes when called twice
  2. **OutcomeClassifier -- death**: Given a `DungeonRunResult` with `PlayerDied=true` and killer name "orc_brute", classifier returns outcome="died", failure_detail contains "orc_brute"
  3. **OutcomeClassifier -- survived**: Given a result where `FloorsCompleted == FloorsAttempted`, returns outcome="survived"
  4. **OutcomeClassifier -- max_turns**: Given a result where a floor has `HitMaxTurns=true`, returns outcome="max_turns" (or "stuck")
  5. **SurvivalCurve monotonic**: `RunSoak(5, 20, 1337)` produces a survival curve where each entry is <= the previous
  6. **FloorRunMetrics enrichment**: After a soak run, `PlayerMaxHp > 0` for all floor metrics
  7. **JSONL round-trip**: Serialize a `DungeonSoakRunResult` to JSON, deserialize back, verify key fields match (seed, outcome, floors_completed)
- Acceptance criteria:
  - All tests pass with `dotnet test --filter "Category!=Slow"`
  - Tests do not require Godot
  - Tests tagged `[Category("Slow")]` if they run 20+ bot iterations

## Files Summary

### New files
- `src/Logic/Balance/DungeonSoakRunResult.cs` -- per-run result with outcome classification
- `src/Logic/Balance/OutcomeClassifier.cs` -- failure classification logic
- `src/Logic/Balance/DungeonSoakSummary.cs` -- multi-run aggregation
- `tests/Balance/DungeonSoakTests.cs` -- unit tests

### Modified files
- `src/Logic/Balance/DungeonRunHarness.cs` -- enrich `Run()`, add `RunSoak()`, enrich `FloorRunMetrics`
- `tools/Harness/Program.cs` -- add `--dungeon`, `--floors`, `--jsonl` flags

## Risks and Open Decisions
1. **Seed strategy**: PoC uses `baseSeed + i`. This gives adjacent seeds which may produce correlated RNG sequences. Alternative: `baseSeed + i * 1_000_003` (prime gap). Decision: use `baseSeed + i` for simplicity, matching PoC. Can change later if correlation is observed.
2. **Stuck vs max_turns**: Without bot telemetry (Phase 2), these are indistinguishable. For now, classify both as "max_turns" with a note in failure_detail. Phase 2 can refine.
3. **Performance**: 100 runs x 6 floors = ~600 floor generations. On M1 Mac, each floor takes ~10-50ms for generation + ~100-500ms for bot play. Total: ~1-5 minutes for a full soak. Acceptable for CLI, may need parallelization for CI if slower.
4. **Killer name capture**: Must be done inside the turn loop at death time. If we wait until after the loop, the entity list may be stale. TASK-003 must handle this carefully.
