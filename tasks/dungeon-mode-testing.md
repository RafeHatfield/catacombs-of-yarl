# Feature: Dungeon-Mode Testing Scenarios + Seed Fix

## Status: needs-review

## Overview

Two related fixes that improve the testing and gameplay experience:

1. **Fixed seed bug**: Every new game is identical because `Main.cs:74` hardcodes `_baseSeed = 1337`. New games should use `Random.Shared.Next()` while preserving deterministic replay via the stored seed.

2. **Dungeon-mode testing scenarios**: Test scenarios in `config/testing/` always route through `GameStateFactory.FromScenario()` -- a flat arena with no worldgen. We need a `dungeon_mode: true` flag on `ScenarioDefinition` so test scenarios can run on a real procedural floor with guaranteed item/monster injections via `DungeonFloorBuilder`. The full `guaranteed_spawns` pipeline already exists (lines 117-221 of `DungeonFloorBuilder.Build()`).

3. **Critical prerequisite**: `EntityPlacer.PlaceGuaranteedSpawns` cannot resolve scrolls or wands -- it only knows about `MonsterFactory`, `ItemFactory`, and `ConsumableFactory`. Scroll/wand items in `guaranteed_spawns` silently fail. Must fix before dungeon-mode testing is useful.

## Reference

- `src/Logic/Balance/ScenarioDefinition.cs` -- scenario YAML model, needs `dungeon_mode` + `guaranteed_spawns` fields
- `src/Logic/Balance/LevelOverride.cs` -- `GuaranteedSpawns`, `SpawnEntry` types (reuse these, don't duplicate)
- `src/Logic/Core/DungeonFloorBuilder.cs` -- `Build()` method, `CreateDefaultPlayer()`, guaranteed_spawns flow
- `src/Logic/Core/EntityPlacer.cs` -- `PlaceGuaranteedSpawns` (missing SpellItemFactory), `FillRooms` (has it)
- `src/Logic/Core/GameStateFactory.cs` -- `FromScenario()` (flat arena path, unchanged)
- `src/Logic/Content/LevelTemplateRegistry.cs` -- `FromYaml()`, private constructor (needs public factory from dict)
- `src/Logic/Content/AotObjectFactory.cs` -- AOT type registration (any new YAML-deserialized types must register)
- `src/Presentation/Main.cs` -- `LaunchTestScenario()`, `StartDungeon()`, `OnNewGameRequested()`, `_baseSeed`
- `config/testing/scenario_testing_full.yaml` -- current flat-arena scenario to be rewritten as dungeon-mode

## Key Decisions (already made)

1. `dungeon_mode: bool` and `guaranteed_spawns: GuaranteedSpawns?` live on `ScenarioDefinition` itself -- no companion file.
2. In `LaunchTestScenario()`: when `dungeon_mode: true`, construct a temporary `DungeonFloorBuilder` with a single-depth `LevelTemplateRegistry` built from the scenario's `GuaranteedSpawns`.
3. Player stats in dungeon mode use `CreateDefaultPlayer()` -- no stat override from scenario YAML.
4. `EntityPlacer.PlaceGuaranteedSpawns` must accept `SpellItemFactory?` to resolve scrolls/wands.
5. Seed: `Random.Shared.Next()` on new game, log it, store on `GameState` (already accessible via `Rng.Seed`).

## Tasks

- [x] TASK-001: Fix EntityPlacer.PlaceGuaranteedSpawns to resolve scrolls and wands
  - Status: complete
  - Files changed: `src/Logic/Core/EntityPlacer.cs`, `src/Logic/Core/DungeonFloorBuilder.cs`
  - Notes: Added `SpellItemFactory? spellItems = null` parameter to `PlaceGuaranteedSpawns`. Resolution order in the items loop: `spellItems.CreateScroll()` → `spellItems.CreateWand()` → `consumables.Create()`. Updated `DungeonFloorBuilder.Build()` to pass `_spellItemFactory`. Tests covering all three cases added in `DungeonModeScenarioTests.cs`.

- [x] TASK-002: Add dungeon_mode and guaranteed_spawns fields to ScenarioDefinition
  - Status: complete
  - Files changed: `src/Logic/Balance/ScenarioDefinition.cs`
  - Notes: Added `DungeonMode` (bool, default false) and `GuaranteedSpawns` (GuaranteedSpawns?, default null). No AOT registration changes needed — `GuaranteedSpawns` and `SpawnEntry` were already in the factory. Tests for backward compat and new field deserialization in `DungeonModeScenarioTests.cs`.

- [x] TASK-003: Add public factory method to LevelTemplateRegistry for programmatic construction
  - Status: complete
  - Files changed: `src/Logic/Content/LevelTemplateRegistry.cs`
  - Notes: Added `public static LevelTemplateRegistry FromSingleDepth(int depth, LevelOverride levelOverride)`. Tests for correct depth routing and null-return for unconfigured depths in `DungeonModeScenarioTests.cs`.

- [x] TASK-004: Fix _baseSeed so every new game is unique
  - Status: complete
  - Files changed: `src/Presentation/Main.cs`
  - Notes: Added `_baseSeed = Random.Shared.Next()` + `GD.Print` in `OnNewGameRequested()`. `LaunchTestScenario` is unchanged — it uses the existing `_baseSeed` (1337 by default at startup) for determinism. `StartDungeon()` formula unchanged.

- [x] TASK-005: Wire dungeon_mode scenarios through DungeonFloorBuilder in LaunchTestScenario
  - Status: complete
  - Files changed: `src/Presentation/Main.cs`
  - Notes: Added `_spellItemFactory` field. `InitFactories()` now creates it and passes it to `_floorBuilder` (fixing the existing scroll/wand floor loot bug in normal dungeon mode too). `LaunchTestScenario` checks `scenario.DungeonMode` and branches: true path builds LevelOverride with 60×40×20-room parameters, creates a temp DungeonFloorBuilder, and calls Build(); false path is unchanged. Temporary builder receives all four factories including spellItemFactory.

- [x] TASK-006: Rewrite scenario_testing_full.yaml as a dungeon-mode scenario
  - Status: complete
  - Files changed: `config/testing/scenario_testing_full.yaml`
  - Notes: Rewrote to use `dungeon_mode: true` with `guaranteed_spawns` (mode: additional). Same item/monster manifest as before, redistributed into monsters/items/equipment lists. Player stat block removed — uses CreateDefaultPlayer(). Orc count reduced to 4 (was 8) since mode=additional will add procedural orcs on top. Map parameters come from LaunchTestScenario hardcoded defaults (60×40, 20 rooms).

- [x] TASK-007: Add integration test for dungeon-mode scenario loading
  - Status: complete
  - Files changed: `tests/Core/DungeonModeScenarioTests.cs` (new file)
  - Notes: Added 11 tests covering: ScenarioDefinition field defaults, YAML deserialization of dungeon_mode scenarios, backward compat, LevelTemplateRegistry.FromSingleDepth routing, procedural floor verification, each guaranteed spawn type independently, and a full E2E pipeline test. All tests are in the fast suite (no Category annotation). 827 tests pass total (up from 781).

## Risks and Open Questions

1. **SpellItemFactory not created in InitFactories**: `Main.cs:InitFactories()` creates `MonsterFactory`, `ItemFactory`, `ConsumableFactory` but NOT `SpellItemFactory`. The `_floorBuilder` is constructed without it (line 317). This means scroll/wand floor loot is already broken in normal dungeon mode -- `FillRooms` receives `spellItems: null` and silently skips spell items in the floor loot pool. TASK-005 must fix this for both the dungeon-mode testing path AND the existing `StartDungeon` path. The `ContentBundle` (from `ContentLoader.LoadAll`) should already contain spell definitions -- verify this during implementation.

2. **Generation parameters for dungeon-mode test scenarios**: The default map is 120x80 with 150 rooms -- too large for a test scenario. The scenario should specify smaller parameters. Since `GenerationParameters` lives on `LevelOverride`, the temporary `LevelOverride` constructed in TASK-005 should include a `Parameters` block with reduced dimensions. The scenario YAML should be able to specify these (add `generation_parameters: GenerationParameters?` to ScenarioDefinition, or hardcode sensible defaults in LaunchTestScenario). Decision: hardcode small defaults (60x40, 20 rooms) in `LaunchTestScenario` for now. If needed later, add parameters to ScenarioDefinition.

3. **Backward compatibility**: All existing test scenarios (`test_portal_wand.yaml`, `test_scrolls_auto.yaml`, etc.) use the flat-arena format and must continue working without modification. The `dungeon_mode` field defaults to `false`, so this is safe by construction.

4. **AotObjectFactory**: `GuaranteedSpawns`, `SpawnEntry`, and `List<SpawnEntry>` are already registered. No new types needed unless we add `GenerationParameters` to `ScenarioDefinition` (deferred per risk #2).
