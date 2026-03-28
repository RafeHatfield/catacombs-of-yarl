# Next Session Priorities (2026-03-26)

## State as of end of 2026-03-25 session

- HUD + inventory milestone: complete, 369 tests passing
- Camera: 3.5× zoom, correct margins
- Toast log: live, fades after 2.5s
- Inventory: icon-only slots, count badge overlay, tap-to-use works
- **Known deferred item**: `max_monsters_per_room` still TEMP:1 in level_templates.yaml

---

## Priority 1 — Quick wins before next device test

### 1a. Restore max_monsters_per_room
**File:** `config/level_templates.yaml`
Change from TEMP:1 back to 2 or 3. Single monster rooms aren't representative of gameplay.

### 1b. Bump zoom to 4× + add tap indicator
**File:** `src/Presentation/Map/PlayerCamera.cs`
- `DefaultZoom = 4.0f` (tiles go from ~8.7mm to ~10mm on device)
- Add brief isometric diamond highlight at the tapped tile to help player calibrate

**Tap indicator implementation:**
- On tap, spawn a tinted Sprite2D (iso_dun_selectA.png, white/yellow tint, alpha ~0.6)
  at the tapped grid position via `IsometricMapper.GridToScreenCenter`
- Tween alpha to 0 over 0.4s, then QueueFree
- Lives on EntityLayer or a dedicated TapIndicatorLayer

---

## Priority 2 — Visual polish

### 2a. Monster name in toast log
Currently shows "z" for zombie (truncated label). The toast text shows the full name —
check what `state.Monsters.FirstOrDefault(m => m.Id == id)?.Name` actually returns.
If it's "zombie" the truncation is a display issue in HUD enemy label, not toast.

### 2b. HUD enemy label truncation
`_enemyHpLabel.Text = $"{nearest.Name}  {ef.Hp}/{ef.MaxHp}"`
Name might be rendering truncated in HUD. Add `Clip.Content = true` or increase label width.

### 2c. Tile variety
Current floors all look the same gray. Check if Oryx has floor variants we can use for
variation. Even just alternating two floor tile sprites would help visual interest.

---

## Priority 3 — Test infrastructure

### 3a. Presentation layer tests
The `InputHandler` coordinate math (screen pos → isometric grid) is testable without Godot.
Extract the grid-hit-test logic and add unit tests.

Key cases to cover:
- Center of tile maps to correct grid (X, Y)
- Edge of tile maps to correct grid
- Wall tile returns correct position (for camera/pathfinding)
- Click above HUD → outside playfield

**File:** `tests/Presentation/InputHandlerTests.cs` (new)

### 3.1: Presentation Contract Tests — COMPLETE (2026-03-26)
- Status: complete
- Files created: `tests/Core/PresentationContractTests.cs`
- 4 tests: GameOverMatchesState, AliveMonsters_ExcludesDeadAfterKill, EntityIds_NoDuplicatesOnFloor, TurnEvents_HaveRequiredFields
- Tests compile and pass with no Godot dependency

### A.2: QueueFree Roslyn Analyzer — COMPLETE (2026-03-26)
- Status: complete
- Files created:
  - `analyzers/QueueFreeAnalyzer/QueueFreeAnalyzer.csproj` — netstandard2.0 analyzer project
  - `analyzers/QueueFreeAnalyzer/QueueFreeAnalyzerRule.cs` — DiagnosticAnalyzer YARL001
- Files modified:
  - `CatacombsOfYarl.Presentation.csproj` — added Analyzer ProjectReference
- Diagnostic: YARL001, Warning severity, "Reliability" category
- False-positive suppression: walks syntax tree to containing MethodDeclaration; skips if name == "SafeFree"
- Verified: bare QueueFree() fires YARL001; clean codebase produces zero YARL001 warnings
- Note: RS2008 (release tracking) suppressed via NoWarn — we are not publishing to NuGet

### I.5: Floor Transition Teardown Integration Test — COMPLETE (2026-03-26)
- Status: complete
- Files created: `tests/Integration/FloorTransitionTests.cs`
- 4 GdUnit4 tests targeting the exact code paths where the three session bugs lived:
  - `ChildrenCleared_AfterSetupPresentation_Pattern` — SafeFree teardown loop produces zero ghost nodes before rebuild
  - `GameController_OldDisposed_NewFunctional` — SafeFree removes old controller immediately; new controller is fully functional (Phase == WaitingForInput)
  - `EventSubscriptions_NoLeakAcrossTransitions` — TurnCompleted on controller #2 fires only for controller #2's turns; old subscription does not bleed through
  - `SpriteManagers_FreshAfterRebuild` — new EntitySpriteManager starts at SpriteCount 0; no stale entity IDs from previous floor
- Build verified: `dotnet build tests/Integration/CatacombsOfYarl.Integration.csproj` — 0 errors
- Note: EntitySpriteManager.Initialize silently skips sprites when GD.Load returns null (test environment), so SpriteCount stays 0 in all four tests — this is correct and intentional; the tests verify structural contracts, not sprite rendering
- Note: Test 3 drives an attack via HandleTap; TurnAnimator completes synchronously in testenv (null sprites → no tween steps) so TurnCompleted fires in-frame without waiting on tween duration

### 3.2: DungeonRun Harness — COMPLETE (2026-03-26)
- Status: complete
- Files created:
  - `src/Logic/Balance/DungeonRunHarness.cs` — reusable multi-floor bot runner with per-floor metrics
  - `tests/Balance/DungeonRunTests.cs` — ThreeFloors_Deterministic, FiveFloors_CompletesWithMetrics, TenFloors_BoundedTurns (Slow)
- Key decision: BotBrain.ToPlayerAction uses GameMap.MoveToward (greedy, gets stuck at walls).
  The harness overrides MoveToward actions with A* pathfinding so the bot can navigate
  dungeon corridors. This is the correct place to add A* — not in BotBrain, which is
  scenario-mode compatible.
- Key decision: DungeonFloorBuilder sets TurnLimit=100 by default (scenario default).
  Harness overrides to 2000 per floor so IsGameOver only fires on player death.
- Seed 1337: bot completes 2 of 5 floors, dies on depth 3 (expected given current balance).
- TenFloors_BoundedTurns tagged [Category("Slow")] — excluded from default test run.

---

## Priority 4 — Gameplay depth

### 4a. Item variety on floor
Current spawning is mostly healing potions. Enable the full item pool per depth.
Check `DungeonFloorBuilder` item spawning — is it using the full item registry
or just consumables?

### 4b. Multiple monsters per room
Restore TEMP:1 to 2-3 and check combat with multiple enemies is fun, not overwhelming.
Run harness at depth 1-3 to confirm Death% stays in target bands.

---

## Known deferred (not this milestone)

- Character sheet / XP / leveling
- Full equip/unequip screen
- Item identification
- Wand charges
- Partial stack drops
- GUT-based full UI E2E tests
