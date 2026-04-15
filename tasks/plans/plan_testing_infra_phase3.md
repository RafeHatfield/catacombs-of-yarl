# Plan: Testing Infrastructure Phase 3 -- Analysis Reports

## Status: complete

## Current State
All 5 tasks implemented and verified:
- TASK-001: DungeonSoakReport.Generate() — 6-section plain text report, graceful empty states
- TASK-002: SoakJsonlReader — ReadFromFile + ReadRunsFromFile, malformed-line tolerance
- TASK-003: --report and --jsonl-in flags wired up in Program.cs with correct error cases
- TASK-004: tools/ci-soak-check.sh — executable, jq threshold examples, FAIL_ON_THRESHOLD opt-in
- TASK-005: 8 tests in tests/Balance/DungeonSoakReportTests.cs — all passing

Test count: 1097 → 1105 passing (8 new), 0 broken.
Integration tests confirmed:
- `--dungeon --floors 3 --runs 10 --report` produces full report
- `--dungeon --floors 3 --runs 5 --jsonl /tmp/soak.jsonl && --report --jsonl-in /tmp/soak.jsonl` offline report works

## Goal
Post-run analysis that answers "is the game working as intended?" Generate formatted text reports from soak data (either live from a `DungeonSoakSummary` or offline from a saved JSONL file). Surface anomalies, survival curves, bot efficiency, and death classification in a human-readable format suitable for CI output or developer review.

## What This Unlocks
- One-command balance health check: run soak, get a report, know if something regressed
- CI integration: save JSONL, run offline analysis, fail the build if depth-1 death rate > 15%
- Offline analysis: re-analyze old JSONL files without re-running the soak
- Anomaly detection: identify runs with 0 kills, runs that hit turn limits, unexpected failure patterns

## PoC Reference
- `~/development/rlike/tools/bot_survivability_report.py` -- heal threshold distribution, deaths-with-unused-potions, per-scenario death patterns, markdown rendering
- `~/development/rlike/tools/eco_balance_report.py` -- ecosystem report format, action distribution, outcomes table, markdown + console rendering

## Current C# State (after Phase 1 + 2)
- `DungeonSoakSummary` exists with: SurvivalRate, DeathRateByFloor, FailureTypeCounts, KillerCounts, SurvivalCurve, per-run list
- `DungeonSoakRunResult` has: Outcome, FailureType, FailureDetail, PerFloor, BotSummary (when telemetry enabled)
- `BotRunSummary` has: ActionCounts, ReasonCounts, ContextCounts, AvgHpWhenHealing, DeathsWithUnusedPotions
- JSONL output exists: one line per run, snake_case JSON

## Dependencies
- Phase 1 (TASK-001 through TASK-007): `DungeonSoakSummary`, JSONL output
- Phase 2 (TASK-001 through TASK-006): `BotRunSummary` in JSONL output (for bot efficiency section)
- Phase 2 is soft dependency: report should degrade gracefully if `BotSummary` is null (telemetry disabled)

## Tasks

### TASK-001: DungeonSoakReport generator
- Status: complete
- Layer: logic
- Type: analysis
- Dependencies: Phase 1 complete, Phase 2 complete (soft)
- Files to create: `src/Logic/Balance/DungeonSoakReport.cs`
- Description: Generate a multi-section text report from a `DungeonSoakSummary`. Port the report structure from PoC's `bot_survivability_report.py` and `eco_balance_report.py`, unified into a single dungeon-focused report.
- Implementation notes:
  - Static method: `string Generate(DungeonSoakSummary summary)`
  - Report sections (rendered as plain text with ASCII tables):

    **1. Overview**
    ```
    === YARL Dungeon Soak Report ===
    Runs: 100 | Floors: 6 | Base Seed: 1337
    Survival Rate: 34.0%
    Avg Floors Completed: 3.8 / 6
    Avg Total Turns: 187.4
    ```

    **2. Survival Curve**
    ```
    Survival Curve:
      Floor 1:  100.0%  ########################################
      Floor 2:   88.0%  ###################################
      Floor 3:   72.0%  #############################
      Floor 4:   51.0%  ####################
      Floor 5:   38.0%  ###############
      Floor 6:   34.0%  ##############
    ```
    Bar chart using `#` characters, max width 40. Each line shows `survival_curve[depth]`.

    **3. Death Classification**
    ```
    Death Classification (66 deaths):
      Failure Type        Count    %
      ------------------  -----  ------
      death                 58   87.9%
      max_turns              5    7.6%
      stuck                  3    4.5%

    Top Killers (combat deaths):
      orc_brute            15   25.9%
      orc_chieftain        12   20.7%
      zombie                8   13.8%
      skeleton_warrior      6   10.3%
      (others)             17   29.3%
    ```
    Show top 5 killers, collapse rest into "(others)".

    **4. Floor Efficiency**
    ```
    Floor Efficiency:
      Depth   Avg Turns   Avg Kills   Avg HP End   Death%
      -----   ---------   ---------   ----------   ------
          1       45.3         3.2        42/55     12.0%
          2       52.1         4.1        31/55     16.0%
          3       61.7         5.3        22/60      8.0%
          ...
    ```
    Computed from per-run `PerFloor` data. Only include floors that were actually attempted.

    **5. Bot Efficiency** (only when BotSummary data available)
    ```
    Bot Efficiency:
      Action Distribution:
        Attack:          42.3%
        MoveToward:      35.1%
        Heal:             8.2%
        NavigateToStair: 12.1%
        Other:            2.3%

      Heal Behavior:
        Avg HP% when healing: 27.3%  (target: 15-30%)
        Deaths with unused potions: 4 / 58 combat deaths (6.9%)
    ```
    Flag if `AvgHpWhenHealing` is above 35% (healing too early, wasting potions) or below 10% (healing too late, dying with potions).

    **6. Anomalies**
    ```
    Anomalies:
      - 3 runs hit max turn limit (possible stuck bot)
      - 1 run had 0 kills (bot may not have engaged enemies)
      - Run #47 (seed 1384): died on floor 1 with 3 healing potions remaining
    ```
    List any runs where:
    - `TotalKills == 0`
    - `FailureType == "max_turns"` or `"stuck"`
    - Died with `PotionsRemaining >= 2` (significant waste)
    - Survived all floors with `FinalHpFraction < 0.1` (barely survived)

  - The report is a single string. No file I/O in this method. The caller writes it.
  - Degrade gracefully: if `BotSummary` is null on all runs, skip section 5 with a note: "(Bot telemetry not available -- run with --telemetry to enable)"

- Acceptance criteria:
  - Given a `DungeonSoakSummary` with 10 runs, `Generate()` produces a non-empty string
  - All 6 sections are present (or gracefully omitted with explanation)
  - Survival curve bars are proportional and max width 40
  - Death classification percentages sum to 100% (within rounding)
  - Floor efficiency only shows floors that were actually attempted
  - No exceptions when summary has 0 deaths, 0 kills, or all runs survived

### TASK-002: JSONL reader for offline analysis
- Status: complete
- Layer: logic
- Type: system
- Dependencies: Phase 1 TASK-007 (JSONL format)
- Files to create: `src/Logic/Balance/SoakJsonlReader.cs`
- Description: Read a JSONL file produced by `--jsonl` and reconstruct `DungeonSoakSummary` from it. This enables offline re-analysis of saved soak data without re-running the harness.
- Implementation notes:
  - Static method: `DungeonSoakSummary ReadFromFile(string path)`
  - Read file line by line, deserialize each line to `DungeonSoakRunResult` using `System.Text.Json`
  - Must handle snake_case property names (match the output format from Phase 1 TASK-007)
  - Use `JsonSerializerOptions` with `PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower` and `PropertyNameCaseInsensitive = true`
  - After reading all runs, call `DungeonSoakSummary.ComputeFrom()` to aggregate
  - Error handling: skip malformed lines with a warning to stderr, don't crash the whole read
  - Also provide: `IEnumerable<DungeonSoakRunResult> ReadRunsFromFile(string path)` for streaming access
- Acceptance criteria:
  - Round-trip: write JSONL via harness, read via `SoakJsonlReader`, summary matches original
  - Handles empty file (returns summary with 0 runs)
  - Handles file with 1 malformed line among 99 valid lines (reads 99, warns about 1)
  - Handles missing `bot_summary` field gracefully (sets it to null)

### TASK-003: --report flag in harness CLI
- Status: complete
- Layer: logic (tools)
- Type: system
- Dependencies: TASK-001, TASK-002
- Files to modify: `tools/Harness/Program.cs`
- Description: Add `--report` flag that generates the text report. Two modes: (a) inline after a `--dungeon` soak run, (b) offline from a saved JSONL via `--jsonl-in <path>`.
- Implementation notes:
  - `--report` with `--dungeon`: after soak completes, generate and print the report to stdout
  - `--report` with `--jsonl-in <path>`: read the JSONL file, generate report, print to stdout. No soak run needed.
  - `--report --jsonl-in reports/soak.jsonl > reports/soak_report.txt` for saving to file
  - `--jsonl-in` without `--report` is an error (what would you do with the data?)
  - `--report` with `--jsonl-in` and `--dungeon` is an error (pick one data source)
  - Combine with `--jsonl <path>`: `--dungeon --report --jsonl reports/soak.jsonl` runs soak, saves JSONL, prints report
- Acceptance criteria:
  - `dotnet run --project tools/Harness -- --dungeon --floors 3 --runs 10 --report` prints the full report
  - `dotnet run --project tools/Harness -- --report --jsonl-in reports/soak.jsonl` reads JSONL and prints report
  - Report output goes to stdout (can be piped/redirected)
  - Conflicting flags produce a clear error message

### TASK-004: CI integration documentation
- Status: complete
- Layer: both (documentation + example script)
- Type: analysis
- Dependencies: TASK-003
- Files to create: `tools/ci-soak-check.sh` (example script, not a doc file)
- Description: Create a small shell script that demonstrates CI integration: run the dungeon soak, check for regressions, exit non-zero if thresholds are exceeded. This is a working reference, not just documentation.
- Implementation notes:
  - Script: `tools/ci-soak-check.sh`
    ```bash
    #!/bin/bash
    # CI soak regression check
    # Exit non-zero if any regression threshold is exceeded.
    set -euo pipefail

    FLOORS=6
    RUNS=100
    SEED=1337
    REPORT_DIR=reports
    mkdir -p "$REPORT_DIR"

    echo "Running dungeon soak: $RUNS runs, $FLOORS floors, seed $SEED"
    dotnet run --project tools/Harness -- \
        --dungeon --floors $FLOORS --runs $RUNS --seed $SEED \
        --jsonl "$REPORT_DIR/ci_soak.jsonl" \
        --report > "$REPORT_DIR/ci_soak_report.txt"

    echo "Report saved to $REPORT_DIR/ci_soak_report.txt"
    cat "$REPORT_DIR/ci_soak_report.txt"

    # Check thresholds (grep the report output)
    # Floor 1 death rate should be < 15%
    # Overall survival rate should be > 20%
    # TODO: parse JSONL with jq for precise threshold checks
    ```
  - Add comments explaining what thresholds to check and how to parse JSONL with `jq`
  - Include example `jq` commands for extracting key metrics:
    ```bash
    # Survival rate (% of runs where outcome == "survived")
    jq -s '([.[] | select(.outcome == "survived")] | length) as $survived | (length) as $total | ($survived / $total * 100)' reports/ci_soak.jsonl

    # Floor 1 death rate (% of runs where player died on floor 1)
    jq -s '([.[] | select(.per_floor[0].player_died == true)] | length) as $died | (length) as $total | ($died / $total * 100)' reports/ci_soak.jsonl

    # Count of exception outcomes (should be 0)
    jq -s '[.[] | select(.outcome == "exception")] | length' reports/ci_soak.jsonl
    ```
    NOTE: The naive form `[.[] | select(...)] | length / length` always evaluates to 1.0 (divides filtered count by filtered count). Always use the `as $var` form above to capture numerator and denominator separately.
  - Do NOT create a markdown documentation file. The script IS the documentation.
- Acceptance criteria:
  - Script is executable (`chmod +x`)
  - Script runs successfully from the project root
  - Comments explain each threshold and why it matters
  - jq examples are syntactically correct

### TASK-005: Unit tests for Phase 3
- Status: complete
- Layer: logic
- Type: test
- Dependencies: TASK-001, TASK-002
- Files to create: `tests/Balance/DungeonSoakReportTests.cs`
- Description: Test report generation and JSONL round-trip.
- Tests to write:
  1. **Report from synthetic data**: Create a `DungeonSoakSummary` with 5 hand-crafted runs (2 survived, 2 died, 1 max_turns). Generate report. Verify it contains "Survival Rate: 40.0%", "max_turns" in death classification, and all 6 sections.
  2. **Report with zero deaths**: All 5 runs survived. Report should show 100% survival, empty death classification section (or "No deaths recorded"), and no anomalies.
  3. **Report with no telemetry**: All `BotSummary` are null. Report should skip bot efficiency section with explanatory note.
  4. **Report survival curve monotonic**: Generate report, parse the survival curve percentages from the text, verify they are non-increasing.
  5. **JSONL round-trip**: Create 5 `DungeonSoakRunResult` objects, serialize to JSONL temp file, read back via `SoakJsonlReader`, verify field equality (seed, outcome, floors_completed, total_turns for each).
  6. **JSONL with BotSummary**: Round-trip a result that includes `BotSummary` with ActionCounts. Verify the dictionary survives serialization.
  7. **JSONL malformed line handling**: Write a file with 3 valid lines and 1 garbage line. `ReadFromFile()` returns summary with 3 runs, does not throw.
  8. **Report anomaly detection**: Create a run with 0 kills, another with max_turns failure, another dying with 3 potions remaining. Verify all three appear in the anomalies section.
- Acceptance criteria:
  - All tests pass with `dotnet test --filter "Category!=Slow"`
  - No Godot dependency
  - Tests use temp files (cleaned up in teardown) for JSONL round-trip tests
  - Synthetic data construction is clear and reusable

## Files Summary

### New files
- `src/Logic/Balance/DungeonSoakReport.cs` -- report generator
- `src/Logic/Balance/SoakJsonlReader.cs` -- JSONL reader for offline analysis
- `tools/ci-soak-check.sh` -- CI integration example script
- `tests/Balance/DungeonSoakReportTests.cs` -- unit tests

### Modified files
- `tools/Harness/Program.cs` -- `--report`, `--jsonl-in` flags

## Risks and Open Decisions
1. **Report format stability**: The text report is for human consumption, not machine parsing. CI threshold checks should use JSONL + jq, not grep on the report. The report format can change freely.
2. **JSONL schema evolution**: If Phase 1 or Phase 2 field names change, the reader must handle old JSONL files gracefully. Mitigate: use `JsonIgnoreCondition.WhenWritingNull` and `PropertyNameCaseInsensitive = true`. Unknown fields are silently ignored by default in System.Text.Json.
3. **Large JSONL files**: 100 runs x ~2KB/line = ~200KB. Not a concern. 10,000 runs = ~20MB. Still fine for streaming reads. No need for chunked reading at current scale.
4. **jq dependency for CI**: The CI script examples use jq for threshold checks. This is standard on most CI environments (GitHub Actions, CircleCI, etc.) but could be replaced with a dotnet tool if needed. Keep it simple for now.
5. **Report sections dependent on data availability**: The report must not crash if soak data is sparse (0 runs, 0 deaths, no telemetry). Every section must have a graceful empty state. TASK-005 tests this explicitly.
