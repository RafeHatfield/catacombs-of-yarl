# Feature: Chests, Signs, and Murals

## Status: complete (pending playtest)

## Current State
- TASK-001 through TASK-014 complete. TASK-012 YAML content was delivered as part of TASK-005/TASK-006 (files populated during registry implementation). 1274 fast tests pass, 0 failures.
- TASK-015 (harness smoke + manual Godot playtest) is the only remaining item — requires a Godot editor run and is not automated.
- Three bug fixes landed this session: auto-explore chest auto-open (AutoExploreSystem NearestWhere guard), identification state lost on floor transition (Main.cs OnFloorTransitionRequested threading), auto-explore equipment stop (CheckInterrupts missing Equippable check).
- Next step: manual Godot playtest — descend 3 floors, open chest, read sign, examine mural. Then close TASK-015 and mark feature complete.

## Overview
Three interactive dungeon features that make floors feel like places, not combat boxes:
- **Chests** — bump to open, drop contents as floor items, sprite swaps to "opened" (261→262).
- **Signs** — bump to read a depth-filtered message. Zero turn cost (PoC behavior).
- **Murals** — bump to examine a unique-per-floor text. Costs a turn. Placed wall-adjacent.

This is the *initial* pass. Explicitly deferred: trapped chests, locked chests, keys, mimics, disarm, detection, search action, and all the existing PoC chest trap payload code. Those are already covered in `tasks/plans/plan_traps_chests_features.md` and will land as a follow-up.

## Reference
- Existing plan: `tasks/plans/plan_traps_chests_features.md` (full scope; this task file is the slice we're building now)
- Design doc: `docs/DESIGN_PRINCIPLES.md` (logic/presentation split, ECS)
- Python prototype:
  - `~/development/rlike/components/chest.py` — ChestState, open() flow, loot generation
  - `~/development/rlike/components/signpost.py` — sign_type, read()
  - `~/development/rlike/components/mural.py` — examine(), mural_id tracking
  - `~/development/rlike/services/mural_manager.py` — per-floor uniqueness
  - `~/development/rlike/config/signpost_messages.yaml` — 5 categories + depth gates
  - `~/development/rlike/config/murals_inscriptions.yaml` — mural pool
- Existing code patterns to match:
  - `src/Logic/ECS/Stair.cs` — simple tag component on an Entity (our closest existing analog)
  - `src/Logic/Core/TurnController.cs` ResolvePlayerMove + TryOpenDoor — bump-interaction pattern
  - `src/Presentation/Map/DungeonRenderer.cs` DoorOverlaySprites + Pass 2 — sprite-swap pattern for chest open
  - `src/Logic/Core/EntityPlacer.cs` FillRooms — per-room placement loop
- Sprite IDs (Oryx 16bf world_24x24):
  - Chest closed 261, chest open 262 (trapped 263 deferred, empty 264 deferred)
  - Signpost plain 4035 (used for signs AND murals in this pass)

## Architecture Decisions (locked in)

1. **Storage: `GameState.Features: List<Entity>`** — new list alongside `Monsters` and `FloorItems`. Features differ from monsters (no Fighter, no AI) and from floor items (they block movement and persist through interaction). Keeping them separate makes turn resolution and rendering ownership obvious. Floor transition clears the list.

2. **Detection: component presence.** `ChestComponent`, `SignpostComponent`, `MuralComponent` on the Feature entity. `TurnController.ResolvePlayerMove` gains a single `TryInteractFeature` branch before `MoveToward`, mirroring `TryOpenDoor`.

3. **Rendering: DungeonRenderer Pass 5 + `TileLayer.FeatureOverlaySprites: Dictionary<(int,int), Node2D>`** — same pattern as `DoorOverlaySprites`. On chest open, the presentation layer swaps the texture at the cell key (same API surface as `DoorOpenedEvent` handling). No new Godot manager class. Sprites are Sprite2D, not Area2D — interaction is purely bump-driven in the logic layer, so presentation only needs visuals.

4. **Free-action signs: early return in `ResolvePlayerMove`.** Emit `SignpostReadEvent`, skip the `MoveEvent` emission, and set a `freeAction` flag that tells `ProcessTurn` to skip `state.TurnCount++` increment for this action only. Mirrors how `ResolveDescend`'s DescendEvent short-circuits monster turns.

5. **Content generation: reuse existing factories.**
   - Chest loot: `FloorItemPoolEntry` depth-filtered pool + `SpellItemFactory` / `ItemFactory` / `ConsumableFactory`, identical to EntityPlacer's floor-drop path.
   - Sign messages: new `SignpostMessageRegistry` loaded from `config/signpost_messages.yaml`, filtered by depth and sign_type.
   - Mural messages: new `MuralRegistry` + per-floor `MuralTracker` on `GameState` for uniqueness.

6. **Placement: extend `EntityPlacer.FillRooms`.** After monster/item loops, a new feature pass: 1 chest per floor (random non-player room), 0–2 signs per floor (random walkable tiles in non-player rooms), 0–1 mural per floor (wall-adjacent tile in a non-player room). Not scaled by room — *floor-level* quotas to keep frequency predictable.

## Open Questions / Risks

- **Bump-to-read vs. tap-to-read on mobile.** PoC uses bump. For this pass: bump-only. Mobile tap on a feature cell can fall through to the same `TryInteractFeature` path when we build the input layer. Note for future presentation work.
- **Chest "empty" sprite (264).** Deferred. After open we use 262 (open/looted). If we later want chest-empty distinction, add a second swap after pickup.
- **Mural sprite parity.** Using signpost sprite 4035 for murals in this pass. Replace when we have a proper mural sprite. Flag in TASK-010 acceptance.
- **YAML schema.** Message YAML follows PoC shape loosely; see TASK-005 and TASK-006 for exact schema. No versioning yet — add when content count justifies it.
- **Sign free-action cost side effects.** Because signs skip TurnCount++, they *also* skip: DOT ticks, monster turns, momentum reset, regeneration tick. Per PoC, this is desired (reading a sign is "looking," not a turn). Confirmed correct — flag only if design changes.
- **Chest blocks path during auto-explore.** AutoExplore treats chests as blocking (good — player must decide). AutoExplore should *not* auto-open chests. Confirm in TASK-014.

---

## Tasks

- [x] TASK-001: Add feature components and turn events
  - Status: complete
  - Files: src/Logic/ECS/ChestComponent.cs, SignpostComponent.cs, MuralComponent.cs, ChestLootStash.cs; src/Logic/Core/TurnEvent.cs
  - Layer: logic
  - Type: system
  - Dependencies: none
  - Files:
    - NEW `src/Logic/ECS/ChestComponent.cs` — fields: `bool IsOpen`, `List<string> LootItemIds` (resolved item IDs stored at floor-gen time; generated on open is also acceptable but resolving up-front makes determinism cleaner)
    - NEW `src/Logic/ECS/SignpostComponent.cs` — fields: `string Message`, `string SignType` ("lore"|"warning"|"humor"|"hint"|"directional"), `bool HasBeenRead`
    - NEW `src/Logic/ECS/MuralComponent.cs` — fields: `string Text`, `string MuralId`, `bool HasBeenExamined`
    - EDIT `src/Logic/Core/TurnEvent.cs` — add `ChestOpenedEvent { int X, Y; List<int> DroppedItemIds }`, `SignpostReadEvent { int X, Y; string Message; string SignType }`, `MuralExaminedEvent { int X, Y; string Text; string MuralId }`
  - Acceptance criteria:
    - All three components compile, are sealed, and implement `IComponent`
    - Event classes are `sealed : TurnEvent`, use `init` setters
    - Zero Godot dependencies
    - Fast suite passes: `dotnet test --filter "Category!=Slow"`

- [x] TASK-002: Add `GameState.Features` list and clearing hook
  - Status: complete
  - Files: src/Logic/Core/GameState.cs
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001
  - Files:
    - EDIT `src/Logic/Core/GameState.cs` — add `public List<Entity> Features { get; } = new();` with XML doc stating features persist (with `IsOpen`/`HasBeenRead`/`HasBeenExamined` state on their components) until floor transition. Clearing is done by building a new GameState via `DungeonFloorBuilder`, same as `Monsters`/`FloorItems`.
  - Acceptance criteria:
    - `Features` list exists and is populated by default to an empty list
    - XML doc explains membership contract (blocking interactive entities: chests, signs, murals)
    - No existing tests break

- [x] TASK-003: Feature factory for creating entity instances
  - Status: complete
  - Files: src/Logic/Content/FeatureFactory.cs
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001
  - Files:
    - NEW `src/Logic/Content/FeatureFactory.cs` — three static methods:
      - `CreateChest(int x, int y, EntityIdAllocator ids, List<string> lootItemIds)` → Entity (name "Chest", blocksMovement=true, ChestComponent)
      - `CreateSignpost(int x, int y, EntityIdAllocator ids, string message, string signType)` → Entity (name "Signpost", blocksMovement=true, SignpostComponent)
      - `CreateMural(int x, int y, EntityIdAllocator ids, string text, string muralId)` → Entity (name "Mural", blocksMovement=true, MuralComponent)
  - Acceptance criteria:
    - Each returned entity has the correct component and `BlocksMovement=true`
    - Unit tests verify component presence and field values

- [x] TASK-004: TurnController bump-interaction path
  - Status: complete
  - Files: src/Logic/Core/TurnController.cs
  - Notes: TryInteractFeature added; freeAction out-param threads from TryInteractFeature→ResolvePlayerMove→ResolvePlayerAction→ProcessTurn. Key bug: consumesTurn=false means freeAction=true — needed explicit negation (freeAction = !consumesTurn). Monster turn skip wired via !freeAction gate.
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001, TASK-002
  - Files:
    - EDIT `src/Logic/Core/TurnController.cs`:
      - New private `TryInteractFeature(GameState state, int x, int y, List<TurnEvent> events, out bool consumesTurn)` that checks `state.Features` for an entity at (x,y), inspects its component, and returns true if handled.
      - Chest: if `IsOpen` already, return true handled (no event, consumesTurn=true, bump is blocked by the chest entity itself). If closed, set `IsOpen=true`, drop loot items to FloorItems at the chest cell (add to `state.FloorItems`, call `state.Map.RegisterEntity`), emit `ChestOpenedEvent`, consumesTurn=true.
      - Signpost: set `HasBeenRead=true`, emit `SignpostReadEvent`, consumesTurn=**false**.
      - Mural: set `HasBeenExamined=true`, emit `MuralExaminedEvent`, consumesTurn=**true**.
    - Call `TryInteractFeature` in `ResolvePlayerMove` **before** `MoveToward`, parallel to the existing `TryOpenDoor`/`TryOpenDoorOnPath` checks. The feature is at the destination tile (same contract as door check).
    - Thread a `bool freeAction` flag back up to `ProcessTurn` (new overload return value on `ResolvePlayerAction` or out-param) so that when a sign is read, `state.TurnCount++` does NOT fire for this action. Cleanest approach: hoist the `TurnCount++` to after action resolution and gate it on `!freeAction`. Also skip `RecomputeFov`, status ticks, monster turns, environment tick for free actions — but FOV can still be recomputed (cheap and harmless; optional).
  - Acceptance criteria:
    - Walking into a closed chest: chest opens, loot appears as floor items at chest cell, ChestOpenedEvent emitted, turn count increments, monsters act.
    - Walking into an open chest: blocked (no move, no event for the chest, but bump still consumes turn like any wall bump — match existing wall-bump semantics which is: no event, no turn. Actually confirm: wall bump consumes no turn. So open-chest bump consumes no turn either. Update test accordingly.)
    - Walking into a sign: SignpostReadEvent emitted, TurnCount unchanged, monsters do NOT act, player does NOT move.
    - Walking into a mural: MuralExaminedEvent emitted, TurnCount increments, monsters act, player does NOT move.
    - Existing door-bump tests still pass.
    - New NUnit tests cover all four interaction cases.

- [x] TASK-005: Signpost message registry + YAML
  - Status: complete
  - Files: config/signpost_messages.yaml, src/Logic/Content/SignpostMessageRegistry.cs
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001
  - Files:
    - NEW `config/signpost_messages.yaml` — port relevant messages from PoC `~/development/rlike/config/signpost_messages.yaml`. Schema: top-level `messages: { lore: [{text, min_depth?, max_depth?}], warning: [...], humor: [...], hint: [...], directional: [...] }`. Include 5–10 messages per category for the first pass.
    - NEW `src/Logic/Content/SignpostMessageRegistry.cs` — loader (YamlDotNet, same pattern as `PropRegistry`) + `GetRandomMessage(string signType, int depth, SeededRandom rng)` → `(string message, string signType)`. Falls back to a neutral placeholder if no messages match.
  - Acceptance criteria:
    - YAML deserializes cleanly at startup
    - Depth gating works: `min_depth=3` messages excluded at depth 1
    - Unit test: deterministic selection for a given seed
    - Graceful fallback when pool is empty (returns a hardcoded "The signpost is worn smooth." string rather than throwing)

- [x] TASK-006: Mural registry + YAML + per-floor tracker
  - Status: complete
  - Files: config/murals_inscriptions.yaml, src/Logic/Content/MuralRegistry.cs, src/Logic/Core/MuralTracker.cs, src/Logic/Core/GameState.cs
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001
  - Files:
    - NEW `config/murals_inscriptions.yaml` — port lore from PoC. Schema: `murals: [{id, text, min_depth?, max_depth?}]`. 10–15 entries for first pass.
    - NEW `src/Logic/Content/MuralRegistry.cs` — loads YAML, exposes `GetAllForDepth(int depth)` → `IReadOnlyList<(string id, string text)>`.
    - NEW `src/Logic/Core/MuralTracker.cs` — per-run tracker: `Dictionary<int floor, HashSet<string> usedMuralIds>`, method `GetUniqueMuralForFloor(int depth, MuralRegistry registry, SeededRandom rng)` that picks an unused mural for this floor and records the selection. Pool reset when exhausted.
    - EDIT `src/Logic/Core/GameState.cs` — add `public MuralTracker? MuralTracker { get; init; }` (nullable; null in scenario mode).
  - Acceptance criteria:
    - YAML deserializes cleanly
    - Two murals placed on the same floor never share a muralId (assert in unit test with small pool)
    - Unused murals carry forward across floors (tracker is per-run, not per-floor-cleared)
    - Fast suite passes

- [x] TASK-007: Chest loot generation helper
  - Status: complete
  - Files: src/Logic/Balance/ChestLootGenerator.cs
  - Layer: logic
  - Type: system
  - Dependencies: TASK-001, TASK-003
  - Files:
    - NEW `src/Logic/Content/ChestLootGenerator.cs` — static method `Generate(int depth, SeededRandom rng, IReadOnlyList<FloorItemPoolEntry> floorItemPool, SpellItemFactory? spellItems, ItemFactory? items, ConsumableFactory consumables, IdentificationRegistry? registry, AppearancePool? pool, Difficulty difficulty, EntityIdAllocator ids)` → `List<Entity>`. Rolls 2–3 items from the depth-filtered floor pool, resolving each via SpellItemFactory → ItemFactory → ConsumableFactory fallback chain (identical to EntityPlacer's floor-drop path).
  - Acceptance criteria:
    - Returns 2–3 resolved item entities at depth 1
    - Items have allocator-assigned IDs, appropriate for `state.FloorItems`
    - Deterministic for a given seed
    - Unit test with a stub pool asserts count, ID uniqueness, and component presence

- [x] TASK-008: Extend EntityPlacer for feature placement
  - Status: complete
  - Files: src/Logic/Core/EntityPlacer.cs (PlaceFloorFeatures + FindWallAdjacentPosition), src/Logic/Core/DungeonFloorBuilder.cs (PlaceFloorFeatures call + MuralTracker carry-forward)
  - Notes: Bug fixed — rng.Next() called with 0 args (invalid); changed to rng.Next(int.MaxValue) for OrderBy shuffle.
  - Layer: logic
  - Type: system
  - Dependencies: TASK-003, TASK-005, TASK-006, TASK-007
  - Files:
    - EDIT `src/Logic/Core/EntityPlacer.cs` — add a new method `PlaceFloorFeatures(GeneratedMap map, MonsterFactory _, ... FeatureFactory, ChestLootGenerator deps, SignpostMessageRegistry, MuralRegistry, MuralTracker, depth, ids)` → `List<Entity>`. Floor-level quotas:
      - 1 chest per floor (chance 100% at first; tunable later), placed in a random non-player room at a reachable free cell.
      - 0–2 signs per floor (roll: 50/35/15 for 0/1/2), placed at random free cells in non-player rooms.
      - 0–1 mural per floor (40% chance), placed wall-adjacent (cell must have at least one cardinal wall neighbor), non-player room.
    - Register each created feature entity with `map.Map.RegisterEntity(...)` and return them.
    - EDIT `DungeonFloorBuilder.cs` — inject `SignpostMessageRegistry` + `MuralRegistry` via constructor (nullable), call `EntityPlacer.PlaceFloorFeatures(...)` after `FillRooms`, assign returned list to `state.Features`. Copy `MuralTracker` from old state or construct on first floor.
  - Acceptance criteria:
    - Running the full dungeon produces floors with 1 chest, 0–2 signs, 0–1 mural on average
    - No feature overlaps with player spawn, stairs, monsters, items, or another feature
    - Murals are always wall-adjacent (test with a generated map asserting adjacency)
    - Scenario mode is unaffected (no feature placement — scenarios never call this)

- [x] TASK-009: Wire registries into game startup
  - Status: complete
  - Files: src/Presentation/Main.cs (InitFactories loads signpost + mural YAML; OnFloorTransitionRequested passes muralTracker), src/Logic/Core/DungeonFloorBuilder.cs (constructor params + Build muralTracker param)
  - Layer: logic
  - Type: system
  - Dependencies: TASK-005, TASK-006, TASK-008
  - Files:
    - EDIT `src/Presentation/GameController.cs` (or wherever DungeonFloorBuilder is constructed for the actual game) — load `SignpostMessageRegistry`, `MuralRegistry` at startup, pass to `DungeonFloorBuilder`.
    - EDIT harness `tools/Harness/` — pass `null` for both registries (scenarios don't use features).
  - Acceptance criteria:
    - Fresh game launch populates features on floor 1
    - Harness runs unchanged
    - No null-ref errors when registries are null (all paths guard)

- [x] TASK-010: DungeonRenderer Pass 5 — feature sprites
  - Status: complete
  - Files changed: src/Presentation/Map/DungeonRenderer.cs
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-001
  - Files:
    - EDIT `src/Presentation/Map/DungeonRenderer.cs`:
      - Add `TileLayer.FeatureOverlaySprites: Dictionary<(int X, int Y), Node2D>` (mirrors `DoorOverlaySprites`).
      - Render.cs — new `IReadOnlyList<Entity>? features` parameter. After Pass 4 (props), Pass 5 walks features and creates a Sprite2D per feature using the Oryx tile IDs: chest closed=261, chest open=262 if `IsOpen`, signpost=4035, mural=4035 (placeholder). Use the same `themeConfig.GetPropTileById` or equivalent tile lookup already used for props.
      - Track sprite in `FeatureOverlaySprites[(x,y)]`.
      - Features are FOV-modulated in `UpdateVisibility` — add iteration over `FeatureOverlaySprites` alongside `DoorOverlaySprites`.
    - EDIT caller in `GameController.cs` — pass `state.Features` to `DungeonRenderer.Render`.
  - Acceptance criteria:
    - Features render on the visible dungeon
    - FOV modulation (unseen/explored/visible) applies correctly
    - No regression in door/prop rendering (visual smoke check via manual run)

- [x] TASK-011: Chest sprite swap on open + toast/log on interact
  - Status: complete
  - Files changed: src/Presentation/Main.cs
  - Layer: presentation
  - Type: system
  - Dependencies: TASK-004, TASK-010
  - Files:
    - EDIT `src/Presentation/Animation/TurnAnimator.cs` (or wherever events drive animations):
      - Handle `ChestOpenedEvent` — swap the sprite at `FeatureOverlaySprites[(X,Y)]` texture from 261 to 262. Add a toast/log line "You open the chest!" and list dropped items.
      - Handle `SignpostReadEvent` — toast with the message text, styled by sign_type (color coding per PoC: lore=info, warning=red, humor=cyan, hint=yellow, directional=gray).
      - Handle `MuralExaminedEvent` — toast (or dialog; toast is fine for first pass) with mural text, distinct style.
  - Acceptance criteria:
    - Visually confirm chest 261→262 swap
    - Messages appear in the log/toast
    - No Godot errors

- [x] TASK-012: YAML content — initial messages and murals
  - Status: complete
  - Layer: logic
  - Type: scenario
  - Dependencies: TASK-005, TASK-006
  - Files:
    - `config/signpost_messages.yaml` — populate per schema. Start with ~6 messages per category = 30 total. Port from PoC where sensible; write new if PoC is too narrative-specific.
    - `config/murals_inscriptions.yaml` — ~15 mural entries, depth 1–10 distributed. Zhyraxion/Aurelyn lore is PoC-specific — either port or replace with catacombs-generic lore.
  - Acceptance criteria:
    - YAML deserializes; registry loads without warnings
    - Content passes Rafe's sniff test (tone matches the game — this is content, flag for review)

- [x] TASK-013: NUnit tests for feature interactions
  - Status: complete
  - Files: tests/Logic/Features/FeatureInteractionTests.cs (19 tests, all pass)
  - Layer: logic
  - Type: test
  - Dependencies: TASK-001 through TASK-008
  - Files:
    - NEW `tests/Logic/Features/ChestTests.cs`:
      - Closed chest bump → opens, drops loot to FloorItems, emits ChestOpenedEvent, turn advances.
      - Open chest bump → blocked, no event.
      - Monster cannot interact with chest (AI should route around blocking features; test monster path doesn't open chest).
    - NEW `tests/Logic/Features/SignpostTests.cs`:
      - Bump a sign → SignpostReadEvent, TurnCount unchanged, monster did not move, player did not move.
      - Sign message matches registry selection for the seed.
    - NEW `tests/Logic/Features/MuralTests.cs`:
      - Bump mural → MuralExaminedEvent, TurnCount advanced, HasBeenExamined=true.
      - Place two murals on the same floor → unique IDs.
      - Exhaust pool → tracker resets and allows reuse.
  - Acceptance criteria:
    - `dotnet test --filter "Category!=Slow"` passes with the new tests
    - Each test is deterministic (seeded RNG)

- [x] TASK-014: AutoExplore integration check
  - Status: complete
  - Files changed: src/Logic/Core/AutoExploreSystem.cs, tests/Logic/AutoExploreTests.cs
  - Notes: DijkstraMap ignores entities (traverses feature cells), but A* correctly blocks pathing through them. The gap was that NearestWhere could select a feature cell as the target destination (since A* uses ignoreEntityAtDest=true). Fixed by adding !map.IsBlocked(x,y) to NearestWhere predicates in FindAndSetPath. New test AutoExplore_DoesNotAutoOpen_ChestInPath verifies the fix.
  - Layer: logic
  - Type: test
  - Dependencies: TASK-004
  - Files:
    - `src/Logic/AI/AutoExploreSystem.cs` — verify its pathfinding treats Features as blocking (they should; they set `BlocksMovement=true` and are registered on the map). Stop autoexplore when a feature is in the intended step path — same behavior as an item or door currently has (confirm).
    - Add a test in `tests/Logic/AI/AutoExploreTests.cs`: place a chest between player and unexplored area → autoexplore stops before it (does not auto-open).
  - Acceptance criteria:
    - AutoExplore never auto-opens chests
    - AutoExplore halts gracefully when a feature blocks the path
    - Existing autoexplore tests still pass

- [ ] TASK-015: Harness smoke run + manual playtest pass
  - Status: pending
  - Layer: both
  - Type: analysis
  - Dependencies: TASK-009, TASK-011
  - Files:
    - Run `dotnet run --project tools/Harness -- --scenario <any-dungeon-scenario-or-skip> --runs 50` — confirm no regressions in DMG/Enc, Death%, H_PM, H_MP.
    - Manual Godot run: descend 3 floors, open a chest, read a sign, examine a mural. Check: loot picks up on walk-over, sign message appears, mural text appears, no crashes.
  - Acceptance criteria:
    - Harness metrics within 5% of prior run (features don't affect combat balance; deviations are noise or bugs)
    - Manual pass: 3/3 feature types work end-to-end
    - No error logs in Godot console

---

## Out of Scope (deferred; already planned in `plan_traps_chests_features.md`)

- Trapped chest variants (263) + spike/poison/gas trap payloads
- Locked chests + key items
- Mimic chests
- Search action / passive trap detection
- Disarm DC rolls
- Chest empty (264) distinction from open (262)
- Multi-page mural dialog UI
- Identification tied to chest opening
- Mural sprite asset (using signpost placeholder for now)
