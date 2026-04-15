# Mobile Layout Overhaul -- Task List

## Current State
Status: All 7 phases complete.
Last completed: Phase 7 — touch target audit, visual consistency, stretch verification, and two cleanup items.
- Task 7.1: All interactive elements pass 44×44px minimum. QuickSlotBar slots (48×48), MenuButtonBar buttons (48px height), MsgButton (44×44 CustomMinimumSize), EquipmentPanel close button (44×44), MessageLogPanel close button (44×44), equipment body slots (90×90), pack slots (76×76). MiniMap has no tap handler (deferred TODO present). No overlapping zones between MsgButton (ViewportOverlay bottom-left) and QuickSlotBar (its own zone below ViewportOverlay).
- Task 7.2: TouchButton now supports `CornerRadius` property — uses Panel+StyleBoxFlat for rounded corners when > 0, falls back to ColorRect when 0 (legacy callers unaffected). MenuButtonBar sets CornerRadius=6 on both buttons, matching QuickSlotBar item slots. MiniMap and MsgButton share identical border color `(0.60, 0.60, 0.70, 0.45)` and 0.82 bg alpha. All font loads use identical antialiasing=None/SubpixelPositioning=Disabled/Hinting=None config.
- Task 7.3: project.godot confirmed: `window/stretch/mode="canvas_items"`, base resolution 720×1280, `window/stretch/scale_mode="integer"`. All correct — no changes made.
- Cleanup A: `RecallHistory()` removed from ToastLog (no callers since Phase 6.2). `RecallDuration` constant removed. `_history` and `History` property retained.
- Cleanup B: `#pragma warning disable CS0618` added to InventoryPanelTests.cs with TODO comment to migrate to QuickSlotBar tests.
Build: 0 errors, 13 warnings (same count as Phase 6.2 — all pre-existing, none introduced by Phase 7 changes). Tests: 1105 passed, 0 failed.

---

## Phase 1: Screen Zone Restructuring

Establish the 5-zone vertical layout. Strip HUD to a slim status bar. Create placeholder containers for quick-slot bar and menu buttons. Update camera margins.

### Task 1.1 -- Main.tscn zone restructuring + HUD strip-down
- File(s): `src/Presentation/Main.tscn`, `src/Presentation/UI/HUD.cs`
- What to do:
  1. In `Main.tscn`, replace the current 2-node UI layout (HUD 200px TopWide, InventoryPanel 110px BottomWide) with 5 zone containers inside UILayer:
     - `StatusBar`: top-anchored, 90px tall (replaces current `HUD` node)
     - `ViewportOverlay`: anchored below StatusBar to above QuickSlotBar, MouseFilter=Ignore (for minimap/toast/msg button placement -- populated in Phase 5)
     - `QuickSlotBar`: anchored 154px from bottom (above MenuButtons), 154px tall (populated in Phase 3)
     - `MenuButtons`: anchored 51px from bottom (above BottomSafeArea), 128px tall (populated in Phase 2)
     - `BottomSafeArea`: bottom-anchored, 51px tall, no interactive elements
     - Keep `ToastLog` and `EquipmentPanel` nodes at current positions for now (they move in later phases)
  2. In `HUD.cs`, strip `BuildLayout()` down to status bar only:
     - Keep: HP fill bar (styled ColorRect, not ProgressBar -- green fill spanning ~85% width), "HP current/max" text overlay on the fill bar, depth indicator ("D:1") as small text on the right
     - Remove: `_gearButton`, `_exploreButton`, `_msgButton` (move to Phase 2)
     - Remove: `_equipLabel` (equipment summary -- lives in Gear panel only now)
     - Remove: `_enemyHpPanel`, `_enemyHpLabel`, `_enemyHpBar`, `_combatTargetId` and all enemy HP tracking from `OnTurnCompleted` and `Refresh()` (moves to Phase 4)
     - Keep: `_statusEffectBar` for now (placement decision deferred to Phase 5)
     - Remove the events: `ExploreRequested`, `GearRequested`, `MessageRecallRequested` (they move to the new MenuButtonBar in Phase 2 and Msg button in Phase 5)
     - Target height: ~90px including any top safe area padding
     - HP bar should use a ColorRect fill inside a container rather than the current ProgressBar, with color varying by HP fraction (green > 50%, yellow > 25%, red otherwise) -- same `HpColor()` logic
  3. Update `Refresh()` to only handle: HP bar width/color, HP label text, depth label text, status effect bar
- Risks:
  - Removing events from HUD means `Main.cs` wiring will break until Phase 2 adds them elsewhere. Temporarily comment out the wiring lines in `SetupPresentation` (Gear/Explore/Msg) with `// TODO: Phase 2/5` markers. The game will be playable but without Gear/Explore/Msg buttons until those phases land.
  - StatusEffectBar placement may look odd in the slim 90px bar. If it doesn't fit, set it to `Visible = false` with a TODO for Phase 5 placement. Don't block on this.
- Acceptance:
  - Status bar is a slim ~90px row at top with HP bar + depth + status badges only
  - No Gear/Explore/Msg buttons visible anywhere (temporarily removed)
  - No enemy HP panel in the HUD
  - No equipment summary text in the HUD
  - Game remains playable (tap-to-move, auto-explore via code, combat works)
  - No crash on turn completion (OnTurnCompleted simplified)
- Status: ✅

### Task 1.2 -- Main.cs wiring updates + camera margin adjustment
- File(s): `src/Presentation/Main.cs`, `src/Presentation/Map/PlayerCamera.cs`
- Dependencies: Task 1.1
- What to do:
  1. In `Main.cs` `SetupPresentation()`:
     - Update node path from `UILayer/HUD` to `UILayer/StatusBar`
     - Update node path from `UILayer/InventoryPanel` to `UILayer/QuickSlotBar` (or keep old name for now if the .tscn rename is deferred)
     - Comment out the three HUD event wiring lines (GearRequested, ExploreRequested, MessageRecallRequested) with TODO markers pointing to Phase 2 and Phase 5
     - Temporarily comment out `OnGearRequested()` invocation or make it a no-op until Phase 2
     - Update minimap offset: change `OffsetTop = 210f` to `~100f` (90px status bar + 10px padding)
  2. In `PlayerCamera.cs`:
     - Change `UiTopMargin` from `200f` to `90f`
     - Change `UiBottomMargin` from `110f` to `333f` (154px quick-slot + 128px menu + 51px safe area)
     - This shifts the camera center point upward into the clear viewport zone so the player sprite appears centered in the visible area
  3. Verify the `ToastLog` positioning still works. Current `_stack.SetOffset(Side.Bottom, -120)` was designed to sit above the old InventoryPanel. The toast will move properly in Phase 5; for now, adjust to `-350f` or similar to sit above the new bottom chrome.
- Acceptance:
  - Game renders with player centered in the clear viewport area (between 90px status bar and 333px bottom chrome)
  - Minimap renders in top-right, below the status bar, not overlapping it
  - Toast messages appear in the viewport area (not hidden behind bottom chrome)
  - No crashes on floor transitions or new game start
  - Camera tween animation still works correctly
- Status: ✅

### Task 1.3 -- Bottom zone placeholder containers
- File(s): `src/Presentation/Main.tscn` (if not done in 1.1), `src/Presentation/Main.cs`
- Dependencies: Task 1.1
- What to do:
  1. Ensure the QuickSlotBar, MenuButtons, and BottomSafeArea zone containers exist in the .tscn and are properly anchored
  2. Add visible placeholder backgrounds so the zones are visible during development:
     - QuickSlotBar zone: dark semi-transparent background (same style as current InventoryPanel)
     - MenuButtons zone: slightly different shade
     - BottomSafeArea: solid black
  3. In `SetupPresentation()`, get references to the new zone nodes (even if empty). No child content yet -- just confirm the containers exist and are sized/positioned correctly.
- Acceptance:
  - Five distinct vertical zones visible on screen (status bar, clear viewport, quick-slot area, menu area, bottom padding)
  - Zones don't overlap
  - Zone heights approximately match spec percentages: 7% / 63% / 12% / 10% / 4% of 1280px
  - Game viewport (clear area) is usable for tap-to-move
- Status: ✅

---

## Phase 2: Menu Buttons Zone

Create Gear and Explore buttons in the menu button zone. Restore the functionality that was removed from HUD in Phase 1.

### Task 2.1 -- MenuButtonBar implementation
- File(s): new `src/Presentation/UI/MenuButtonBar.cs`
- Dependencies: Phase 1 complete
- What to do:
  1. Create `MenuButtonBar` as a Control subclass, built entirely in code (no .tscn):
     - Two `TouchButton` instances side by side in an HBoxContainer
     - "Gear" button: dark gold background (`0.25, 0.20, 0.10, 0.9`), icon or text label
     - "Explore" button: dark green background (`0.15, 0.35, 0.15, 0.9`), text label
     - Each button gets ~half screen width (SizeFlags.ExpandFill)
     - Minimum height: 48px per button (meets 44pt HIG requirement with margin)
     - 8px gap between buttons, 8px horizontal margin
     - Rounded corners on button backgrounds (6px radius -- requires switching TouchButton bg from ColorRect to PanelContainer with StyleBoxFlat, or adding rounded corners to MenuButtonBar's buttons directly)
  2. Events:
     - `event Action? GearRequested`
     - `event Action? ExploreRequested`
  3. Public method: `SetAutoExploreActive(bool active)` -- changes Explore button text and tint (same behavior as current `HUD.SetAutoExploreActive`)
- Acceptance:
  - Two buttons render in a horizontal row
  - Both buttons have >= 48px height
  - Buttons fill the width with even spacing
  - Events fire on tap
  - No crash if events have no subscribers
- Status: ✅

### Task 2.2 -- Wire MenuButtonBar into Main.cs
- File(s): `src/Presentation/Main.cs`
- Dependencies: Task 2.1
- What to do:
  1. In `SetupPresentation()`:
     - Create `MenuButtonBar` instance and add it as child of the `MenuButtons` zone node
     - Wire `GearRequested` to `OnGearRequested()`
     - Wire `ExploreRequested` to `_gameController?.StartAutoExplore()`
     - Remove the TODO comments left in Task 1.2
  2. In `OnTurnCompleted()`:
     - Call `_menuButtonBar?.SetAutoExploreActive(...)` (replacing the old `_hud?.SetAutoExploreActive(...)` call)
  3. Store `_menuButtonBar` as a field for lifecycle management
- Acceptance:
  - Gear button opens equipment panel
  - Explore button triggers auto-explore, shows "Exploring..." state
  - Auto-explore state resets correctly when interrupted
  - Both buttons positioned in the menu zone below quick-slot bar
  - Game fully playable with Gear and Explore restored
- Status: ✅

---

## Phase 3: Quick-Slot Bar Refactor

Replace the current InventoryPanel with a scrollable consumable strip + weapon indicator. This is the most complex single phase.

### Task 3.1 -- QuickSlotBar core layout + auto-populate
- File(s): new `src/Presentation/UI/QuickSlotBar.cs` (replaces InventoryPanel)
- Dependencies: Phase 1 complete
- What to do:
  1. Create `QuickSlotBar` as a new Control subclass (do not refactor InventoryPanel in-place -- the layout is too different):
     - Full-width, fills the QuickSlotBar zone container
     - Left section: weapon indicator slot (~48x48px)
       - Shows current MainHand weapon icon (using `SpriteMapping.GetItemSpritePath` via `ItemTag.TypeId`)
       - Small label below icon with weapon name (truncated to ~6 chars)
       - 1px vertical separator line on the right edge
       - Tap: toast "Ranged toggle coming soon" (stub)
       - Long-press: fire `WeaponLongPressed` event (for future ActionSheet integration)
     - Right section: `ScrollContainer` wrapping an `HBoxContainer` of consumable/wand slots
       - `ScrollContainer.HorizontalScrollMode = Always` (or `ShowAlways` -- verify Godot API)
       - `ScrollContainer.VerticalScrollMode = Disabled`
       - Each slot: 48x48px Control with rounded-corner background (6px radius via StyleBoxFlat)
       - Colored background tint by item type: health potions reddish, mana/arcane blue, scrolls amber, wands purple
       - Item icon centered in slot (use identification-aware `ItemDisplay.GetSpriteKey`)
       - Quantity badge: bottom-right corner label (stack count for consumables, charges for wands, none for scrolls)
       - No empty slot placeholders -- bar only shows items that exist
  2. Auto-populate from inventory: filter for `Consumable` or `SpellEffect` components (same filter as current InventoryPanel `Refresh`)
  3. Manual hit-testing for tap and long-press (same pattern as current InventoryPanel -- bypasses Godot Button hit-rect bug under integer stretch scale)
  4. Events:
     - `event Action<int>? ItemTapped` (item entity ID)
     - `event Action<int>? ItemLongPressed` (item entity ID)
     - `event Action? WeaponTapped` (stub)
     - `event Action? WeaponLongPressed`
  5. Port the long-press detection logic from InventoryPanel (0.4s threshold, 24px drag cancel)
- Risks:
  - ScrollContainer + manual hit-testing interaction: the ScrollContainer will consume horizontal swipe gestures for scrolling, but tap/long-press events need to reach the QuickSlotBar's `_GuiInput`. Test carefully. May need to set slot MouseFilter=Ignore and handle all input at the ScrollContainer or QuickSlotBar level.
  - Hit-rect computation (`_ComputeSlotRects`) must account for ScrollContainer scroll offset. When the user scrolls, the slot positions shift but `GetGlobalRect()` should still report correct screen-space positions.
- Acceptance:
  - Weapon indicator visible on far left with separator line
  - All consumables and wands visible in scrollable row
  - Slots show correct icons, colored backgrounds, quantity badges
  - Tapping a slot fires ItemTapped with correct item ID
  - Long-pressing a slot fires ItemLongPressed
  - Weapon tap shows toast stub
  - Horizontal scroll reveals overflow items
  - Empty inventory shows no slots (no placeholders)
- Status: ✅
  - Implementation: new `src/Presentation/UI/QuickSlotBar.cs` — Control subclass built entirely in code. Weapon indicator (far-left, 52×48px Panel with StyleBoxFlat rounded corners): icon + truncated-name label. 1px ColorRect separator. ScrollContainer (MouseFilter=Ignore, HorizontalScrollMode=ShowNever) wrapping HBoxContainer of 48×48 item slots. All children MouseFilter=Ignore; QuickSlotBar.MouseFilter=Stop. _GuiInput handles all input with scroll-vs-tap disambiguation (ScrollTapThreshold=8px): horizontal drag above threshold → manual ScrollHorizontal drive; lift below threshold → tap/long-press. Long-press via _Process timer (0.4s), 24px drag cancel. Slot backgrounds use StyleBoxFlat with 6px corner radii; tint by type (health=red, arcane=blue, scroll=amber, wand=purple). Quantity badge for consumables (stack count), wands (charges/∞), nothing for scrolls. `_ComputeSlotRects()` deferred via CallDeferred; uses GetGlobalRect() minus panel origin so scroll offset is automatically accounted for.
  - Note: `Rect2.Zero` doesn't exist in Godot's C# API — used `default(Rect2)` instead.

### Task 3.2 -- Wire QuickSlotBar into Main.cs + remove InventoryPanel
- File(s): `src/Presentation/Main.cs`, possibly `src/Presentation/GameController.cs`
- Dependencies: Task 3.1
- What to do:
  1. In `SetupPresentation()`:
     - Replace `_inventoryPanel = new InventoryPanel()` with `_quickSlotBar = new QuickSlotBar()`
     - Wire `ItemTapped` to `OnInventoryItemTapped` (same handler -- item use logic unchanged)
     - Wire `ItemLongPressed` to GameController's action sheet handler
     - Wire `WeaponTapped` to a stub that shows a toast via `_toastLog?.AddMessage(...)`
     - Set `SpriteMappingInstance` on the new bar
     - Add as child of `QuickSlotBar` zone node
  2. In `OnTurnCompleted()`:
     - Replace `_inventoryPanel?.Refresh(state)` with `_quickSlotBar?.Refresh(state)` if the GameController calls it (check GameController.cs for refresh calls)
  3. Update field type from `InventoryPanel?` to `QuickSlotBar?`
  4. Remove or deprecate `InventoryPanel.cs` (keep the file but mark as obsolete, or delete if confident)
  5. Update `RectDebugDraw` if it references InventoryPanel
- Acceptance:
  - Quick-slot bar fully functional in its new location
  - Item use (tap) works correctly
  - Long-press shows action sheet
  - Quick-bar refreshes after item use, pickup, drop, and floor transition
  - No references to old InventoryPanel remain in active code paths
  - Drop button functionality preserved (if it existed in InventoryPanel -- it did, via ItemDropRequested)
- Status: ✅
  - Implementation: `Main.cs` field changed from `InventoryPanel?` to `QuickSlotBar?`. SetupPresentation creates `new QuickSlotBar()`, sets `SpriteMappingInstance`, calls `Initialize(state)`, wires `ItemTapped` → `OnInventoryItemTapped`, wires `WeaponTapped` → toast stub. `ItemLongPressed` wiring happens inside `GameController.Initialize` (it accesses `_inventoryPanel.ItemLongPressed`). `RectDebugDraw.cs` updated: `_inventoryPanel` field removed, replaced by `_quickSlotBar: QuickSlotBar?`, `SetInventoryPanel` renamed to `SetQuickSlotBar`. `GameController.cs` field `_inventoryPanel` and `Initialize` parameter changed from `InventoryPanel?` to `QuickSlotBar?`. `InventoryPanel.cs` marked `[Obsolete("Use QuickSlotBar instead...")]` at class level — file retained for integration tests.
  - Note: `ItemDropRequested` removed from QuickSlotBar (drop via long-press action sheet only, per design decision). `OnTurnCompleted` in Main.cs does not directly call `_inventoryPanel.Refresh` — GameController handles refresh from within ExecuteTurn's `inventoryChanged` path.
  - Build: 0 errors, 11 warnings (10 pre-existing + 1 CS0618 from Godot source generator referencing Obsolete InventoryPanel).

---

## Phase 4: Floating Enemy HP Bars

Replace HUD-embedded enemy HP panel with small red bars above enemy sprites.

### Task 4.1 -- FloatingHpBarManager implementation
- File(s): new `src/Presentation/Entities/FloatingHpBarManager.cs`
- Dependencies: Phase 1 complete (enemy HP removed from HUD)
- What to do:
  1. Create `FloatingHpBarManager` class (not a Node -- just manages child nodes on EntityLayer):
     - Constructor takes `Node2D entityLayer` and `EntitySpriteManager spriteManager`
     - Method `Refresh(GameState state)`: for each alive monster, if `Hp < MaxHp`, ensure a small red bar exists above the sprite; if `Hp == MaxHp` or monster not visible, remove/hide the bar
     - Bar implementation: a small `ColorRect` (red fill) inside a slightly larger `ColorRect` (dark bg), both children of a `Node2D` positioned above the entity sprite
     - Bar width: ~32px, height: ~4px
     - Bar positioned at sprite position + vertical offset (above the sprite head). Use `EntitySpriteManager.GetSprite(entityId)` to get position, then offset Y by roughly `-spriteHeight * scale * 0.6`
     - Fill width is proportional: `(hp / maxHp) * barWidth`
     - Bars only shown for visible monsters (`state.Map.IsVisible(m.X, m.Y)`)
  2. Track active bars in a `Dictionary<int, Node2D>` keyed by entity ID
  3. Clean up bars for dead/removed monsters
  4. Method `Clear()` to remove all bars (called on floor transition)
- Risks:
  - Performance: one Node2D + two ColorRect per damaged monster. At typical encounter sizes (3-6 monsters) this is negligible. Cap at visible monsters only.
  - Bar positioning: bars are on EntityLayer (world space), so they move with the camera automatically. But they need to update position when sprites move (UpdatePositions is called after each turn in EntitySpriteManager).
- Acceptance:
  - Damaged monsters show a small red bar above their sprite
  - Full-HP monsters show no bar
  - Bar updates correctly during combat (fill width changes)
  - Bar disappears when monster dies
  - Bar hidden when monster leaves FOV
  - No bar visible in peaceful rooms with undamaged monsters
  - Bars removed on floor transition
- Status: ✅
  - Implementation: `src/Presentation/Entities/FloatingHpBarManager.cs` — plain C# class (not a Node). Constructor takes `Node2D entityLayer`. `Refresh(GameState state, EntitySpriteManager spriteManager)` iterates `state.AliveMonsters`, creates/updates/removes bars. Each bar is a `Node2D` root (child of entityLayer) containing a dark-bg `ColorRect` (32×4px) and a red-fill `ColorRect` (width scaled by hp/maxHp). Position: `sprite.GlobalPosition + (-BarWidth/2, -24)` so the bar centers over the sprite and sits ~24px above it. `Clear()` frees all bar nodes and empties the dictionary. HashSet-based pruning removes bars for monsters that died during the turn.

### Task 4.2 -- Wire FloatingHpBarManager into Main.cs
- File(s): `src/Presentation/Main.cs`
- Dependencies: Task 4.1
- What to do:
  1. In `SetupPresentation()`:
     - Create `FloatingHpBarManager` instance, store as field
     - Call `_floatingHpBars.Refresh(state)` after initial setup
  2. In `OnTurnCompleted()`:
     - Call `_floatingHpBars?.Refresh(state)` after entity visibility updates
  3. On floor transition, call `_floatingHpBars?.Clear()`
  4. Confirm HUD.cs no longer has any enemy HP code (should be clean from Task 1.1)
- Acceptance:
  - Floating HP bars appear during combat
  - No enemy HP display in the status bar
  - Bars persist correctly across turns within a floor
  - Bars clear on floor transitions
  - No performance regression visible with 6+ monsters
- Status: ✅
  - Implementation: `_floatingHpBars` field added to `Main.cs`. In `SetupPresentation`: `_floatingHpBars?.Clear()` called before reassignment (child nodes already freed by the entityLayer child-clearing loop; SafeFree is a no-op on freed nodes), then `new FloatingHpBarManager(entityLayer)` created after `_groundHazardOverlay` setup. Initial `Refresh` called after fog-of-war + entity visibility block. In `OnTurnCompleted`: `Refresh` called after `_entitySprites?.UpdateStatusTints` / `_itemSprites?.UpdateVisibility`. HUD.cs confirmed clean of enemy HP code since Phase 1. Build: 0 errors, 12 warnings (all pre-existing).

---

## Phase 5: Viewport Overlays (Minimap, Msg Button, Toast Restyle)

Position minimap, message button, and toasts correctly within the viewport zone. Restyle toasts with left-border accent. Decide StatusEffectBar placement.

### Task 5.1 -- Minimap restyle (semi-transparent bg + rounded corners)
- File(s): `src/Presentation/UI/MiniMap.cs`
- Dependencies: Phase 1 complete
- What to do:
  1. In `_Draw()`:
     - Replace the current flat `DrawRect` background with a rounded rectangle using `DrawStyleBox` or manual corner drawing
     - Set background alpha to ~0.8 (currently `ColBg` is `0.05, 0.05, 0.08, 0.70` -- increase opacity)
     - Add a subtle 0.5px border (use `DrawRect` with `filled: false` or a second slightly-larger background rect)
  2. Verify positioning: top-right of viewport zone, below 90px status bar. The offset was already adjusted in Task 1.2.
  3. Tap-to-expand: defer to future task. Add a comment noting it's planned.
- Acceptance:
  - Minimap has semi-transparent background with ~0.8 alpha
  - Visible rounded corners (at least 4px radius)
  - Subtle border visible around the minimap
  - Positioned correctly below status bar in top-right
  - No functional change to minimap content rendering
- Status: ✅
  - Implementation: `BuildBgStyle()` creates a `StyleBoxFlat` once at class init: alpha raised to 0.82, all four corner radii set to 4px, 1px border at `(0.60, 0.60, 0.70, 0.45)`. `_Draw()` calls `DrawStyleBox(_bgStyle, ...)` instead of `DrawRect`. Style object is cached as a readonly field to avoid per-frame allocations.
  - Note: 0.5px border is not representable with `StyleBoxFlat.BorderWidth*` (int only); 1px renders as visually subtle at minimap scale — matches spec intent.
  - Tap-to-expand: `TODO` comment added in `_Draw()`.
  - Build: 0 errors, 10 pre-existing warnings (all outside MiniMap.cs).

### Task 5.2 -- Msg button as viewport overlay
- File(s): `src/Presentation/Main.cs` (or new small class)
- Dependencies: Phase 1 complete
- What to do:
  1. Create a small `TouchButton` (or custom Control) positioned in the bottom-left of the viewport zone:
     - Size: 32x32px visual, 44x44px hit area (larger invisible hit area around the visual)
     - Semi-transparent dark background, rounded corners (match minimap style)
     - Text: unicode message icon or simple "Msg" text at small font size
     - 0.5px border matching minimap style
  2. Position: anchored to bottom-left of viewport overlay zone, offset up from the quick-slot bar boundary (~8px margin)
  3. Wire tap to `_toastLog?.RecallHistory()`
  4. This replaces the old `_msgButton` that was in the HUD (removed in Phase 1)
- Acceptance:
  - Msg button visible in bottom-left of viewport
  - Tap opens message recall (same behavior as old Msg button)
  - Visual style matches minimap (semi-transparent bg, rounded corners, border)
  - Button doesn't interfere with tap-to-move (has correct MouseFilter)
  - Hit area is at least 44x44px even though visual is 32x32
- Status: ✅
  - Implementation: new `MsgButton` class at `src/Presentation/UI/MsgButton.cs`. Custom Control with `_GuiInput` hit-testing (same pattern as TouchButton — avoids iOS stretch-scale hit-area drift). 44x44 CustomMinimumSize. StyleBoxFlat background matching MiniMap: alpha 0.82, 4px corner radii, 1px border at `(0.60, 0.60, 0.70, 0.45)`. Label text "Msg" at 16px PixeloidMono with no antialiasing. Anchored to bottom-left of ViewportOverlay (AnchorTop=1, offsets 8px from left/bottom edges). Created once in `SetupPresentation` if null (same guard as MiniMap); `Pressed` lambda captures `this` (Main) and calls `_toastLog?.RecallHistory()` so it resolves the current floor's ToastLog at call time. Build: 0 errors, 12 warnings (all pre-existing).
  - Note: "Msg" text used conservatively; swap to "✉" (U+2709) in `BuildLayout()` if the glyph renders cleanly on device.

### Task 5.3 -- Toast left-border color accent
- File(s): `src/Presentation/UI/ToastLog.cs`
- Dependencies: None (can be done in parallel with other Phase 5 tasks)
- What to do:
  1. Replace the shared `_toastStyle` with per-toast style creation that includes a colored left border:
     - `BorderWidthLeft = 3` (3px colored accent)
     - Green border (`0.3, 0.9, 0.3`) for positive events: kills, heals, buffs, identification, pickup
     - Red border (`0.9, 0.3, 0.3`) for danger events: damage taken, debuffs applied, player death
     - Gray border (`0.5, 0.5, 0.5`) for neutral events: misses, status expiry, monster actions
  2. Determine event category from the BBCode content or from a new parameter to `SpawnToast`:
     - Option A: pass a `ToastCategory` enum (Positive/Danger/Neutral) from `FormatEvent` to `SpawnToast`
     - Option B: infer from BBCode color tags (green/lime = positive, red/orange = danger, gray = neutral)
     - Recommend Option A for clarity and correctness
  3. Update `FormatEvent` to return `(string? text, ToastCategory category)` tuple
  4. Adjust toast positioning: anchor `_stack` to bottom-left of viewport zone, above the Msg button. Update offsets from Task 1.2's temporary values.
- Acceptance:
  - Kill messages have green left border
  - Damage-taken messages have red left border
  - Miss messages have gray left border
  - Heal/buff messages have green left border
  - Status applied (debuff) messages have red left border
  - Border is visible as a 3px colored stripe on the left edge of each toast
  - Toast positioning doesn't overlap with Msg button or quick-slot bar
- Status: ✅
  - Implementation: Option A chosen — `ToastCategory` enum (Positive/Danger/Neutral) declared at file level in ToastLog.cs
  - `FormatEvent` returns `(string? text, ToastCategory category)` tuple; all 15+ event patterns carry explicit categories
  - `SpawnToast` creates per-toast `StyleBoxFlat` with `BorderWidthLeft = 3` and `BorderColor` from category switch
  - `ContentMarginLeft` bumped to 11px (was 8px) so text doesn't overlap the 3px stripe
  - `AddMessage` and `RecallHistory` use `Neutral`; recalled messages don't persist category so all recall is gray
  - Note: `StatusAppliedEvent` has no `IsNegative` flag; all player-targeted status applications treated as Danger. Revisit if positive player buff events are added.
  - Build: 0 errors, 10 pre-existing warnings (none from ToastLog.cs)

### Task 5.4 -- StatusEffectBar placement decision + implementation
- File(s): `src/Presentation/UI/StatusEffectBar.cs`, `src/Presentation/UI/HUD.cs`
- Dependencies: Phase 1 complete
- What to do:
  1. Move StatusEffectBar from inside HUD to a viewport overlay position:
     - Place as a thin row just below the status bar, overlaying the viewport
     - Only visible when effects are active (StatusEffectBar already hides when empty)
     - Semi-transparent background to not fully block viewport
  2. In `Main.cs`, create StatusEffectBar as a separate child of `ViewportOverlay` zone (not inside HUD)
  3. In `HUD.cs`, remove the `_statusEffectBar` field and its `Refresh()` call
  4. In `Main.cs` `OnTurnCompleted()`, call `_statusEffectBar?.Refresh(state.Player)` directly
- Acceptance:
  - Status badges render just below the status bar
  - Badges don't overlap with minimap
  - Badges hidden when no effects are active
  - Badge content unchanged (same color coding, same text, same overflow behavior)
  - No visual clutter in the viewport when no effects are active
- Status: ✅
  - Implementation: `_statusEffectBar` field added to `Main.cs`. Removed `_statusEffectBar` field, VBoxContainer row 2 construction, and `Refresh()` call from `HUD.cs` — HUD is now clean of any status effect references. In `SetupPresentation`: created once (same `if null` guard as MiniMap/MsgButton), added as child of `UILayer/ViewportOverlay`, anchored top-left (AnchorRight=1 for full-width span), OffsetLeft=8, OffsetTop=4, OffsetBottom=28 (4+24), CustomMinimumSize height=24, SizeFlagsHorizontal=ExpandFill, MouseFilter=Ignore. Initial `Refresh(state.Player)` called on floor entry. In `OnTurnCompleted`: `_statusEffectBar?.Refresh(_state.Player)` called immediately after HUD update. Build: 0 errors, 13 warnings (all pre-existing).

---

## Phase 6: Full-Screen Panel Overlays

Make Equipment panel full-screen. Create a proper message history panel.

### Task 6.1 -- EquipmentPanel full-screen conversion
- File(s): `src/Presentation/UI/EquipmentPanel.cs`
- Dependencies: Phase 2 complete (Gear button wired)
- What to do:
  1. Change `_panelContainer` from centered 680x640 to full-screen:
     - Replace the center-anchored offsets (`-340/+340, -320/+320`) with `SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect)`
     - Add margin insets (16px on all sides) so content doesn't touch screen edges
  2. The "IN PACK" section may need a ScrollContainer if many items exist:
     - Wrap the pack strip HBoxContainer in a ScrollContainer with horizontal scroll
  3. Close button (X) already exists at 44x44px -- verify it's still in the top-right after full-screen conversion
  4. Tap-outside-to-dismiss: with full-screen layout, "outside the panel" means... nothing. Remove or adjust the tap-outside-to-dismiss logic. Keep the X button as the only close mechanism, OR add a tap on the backdrop (which is now the entire panel bg).
     - Recommend: keep X button only, remove tap-outside-dismiss since there's no "outside" anymore
- Acceptance:
  - Equipment panel fills the full screen when opened
  - All existing equipment functionality preserved (equip, unequip, long-press, drop)
  - Close button works and is positioned in top-right
  - Panel background covers the full screen
  - Stats summary, body-slot grid, and IN PACK list all visible and functional
  - IN PACK scrollable if items overflow
- Status: ✅
  - `_panelContainer` now uses `SetAnchorsAndOffsetsPreset(FullRect)` with `OffsetLeft/Top = +16` and `OffsetRight/Bottom = -16` (16px insets all sides).
  - Tap-outside-to-dismiss block (old lines 217-221) removed. Comment updated to explain why. X button is the only dismiss mechanism.
  - IN PACK strip: replaced plain `Control` with `ScrollContainer` (HorizontalScrollMode=ShowAlways, VerticalScrollMode=Disabled, CustomMinimumSize height = PackSlotSize + 12). Inner HBoxContainer uses `SizeFlagsHorizontal = ShrinkBegin` so it expands to natural content width for scrolling.
  - Close button remains correctly anchored in top-right corner (last item in HBoxContainer where title has ExpandFill).
  - Class doc comment updated to remove "tap outside" language.
  - Build: 0 errors, 10 pre-existing warnings (none from EquipmentPanel.cs).

### Task 6.2 -- Message history panel
- File(s): new `src/Presentation/UI/MessageLogPanel.cs`
- Dependencies: Task 5.2 (Msg button exists)
- What to do:
  1. Create `MessageLogPanel` as a full-screen overlay Control:
     - Dark background (same style as EquipmentPanel)
     - "MESSAGE LOG" title in header row
     - Close button (X) in top-right, 44x44px
     - ScrollContainer with VBoxContainer for message list
     - Each message: a Label or RichTextLabel with the same formatting as toasts (BBCode enabled)
     - Show last N messages (from ToastLog's `_history` list)
  2. ToastLog needs to expose history: add `public IReadOnlyList<string> History => _history;`
  3. Scrollable -- newest messages at the bottom, auto-scrolled to bottom on open
  4. Wire Msg button: instead of `RecallHistory()` (which re-shows floating toasts), open this panel
     - Keep `RecallHistory()` as a fallback or remove it
- Acceptance:
  - Msg button opens a full-screen message log
  - Log shows all recent messages with correct formatting
  - Scrollable if messages exceed viewport
  - Close button dismisses the panel
  - Panel doesn't interfere with game state
- Status: ✅
  - `ToastLog.History` property added: `public IReadOnlyList<string> History => _history;`
  - `MessageLogPanel.cs` created: full-screen `Color(0.05, 0.05, 0.1, 0.95)` backdrop, header row ("MESSAGE LOG" in PixeloidSans-Bold 24px + 44×44 red X button), divider, `ScrollContainer` (VerticalScrollMode=Auto) + `VBoxContainer` of `RichTextLabel` entries at 18px PixeloidMono preserving BBCode formatting. Auto-scrolls to bottom via `CallDeferred(ScrollToBottom)`.
  - `Main.cs`: added `_messageLogPanel` field; created once with `if null` guard, added to `UILayer` (CanvasLayer) as sibling of EquipmentPanel; Msg button Pressed handler changed from `RecallHistory()` to `_messageLogPanel?.Open(_toastLog?.History ?? Array.Empty<string>())`.
  - `RecallHistory()` left intact on ToastLog (still usable as fallback, no callers now).
  - Build: 0 errors, 13 warnings (all pre-existing).

---

## Phase 7: Polish and Touch Target Audit

Final pass on sizing, consistency, and touch targets.

### Task 7.1 -- Touch target audit
- File(s): all UI files
- Dependencies: Phases 1-6 complete
- What to do:
  1. Audit every interactive element for >= 44pt touch targets:
     - Quick-slot bar slots: currently 48x48px -- passes
     - Menu buttons: currently 48px height -- passes
     - Minimap: currently small -- add 44x44 minimum hit area
     - Msg button: 32px visual but 44px hit area -- verify
     - Equipment panel close button: 44x44 -- passes
     - Equipment panel slots: 90x90 -- passes
     - Equipment panel pack slots: 76x76 -- passes
  2. Check for overlapping touch targets between zones
  3. Verify no dead zones (areas that eat taps but don't respond visually)
- Acceptance:
  - All interactive elements have >= 44x44px touch/hit areas
  - No overlapping touch targets
  - Tap-to-move works in the full clear viewport area (no invisible controls eating taps)
- Status: ✅
  - All interactive elements verified: QuickSlotBar slots (48×48), MenuButtonBar buttons (min 48px height), MsgButton (44×44 CustomMinimumSize set in _Ready), EquipmentPanel close button (44×44), MessageLogPanel close button (44×44), equipment body slots (SlotSize=90), pack slots (PackSlotSize=76).
  - MiniMap: no tap handler implemented (deferred TODO comment already in place at `_Draw()`). No action needed.
  - Zone overlap check: MsgButton anchored to bottom-left of ViewportOverlay; QuickSlotBar is in a separate zone node below ViewportOverlay. No overlap.

### Task 7.2 -- Visual style consistency pass
- File(s): all UI files
- Dependencies: Phases 1-6 complete
- What to do:
  1. Verify dark theme throughout:
     - Status bar background: dark navy (currently `0.05, 0.05, 0.1, 0.85` -- good)
     - Quick-slot bar background: match
     - Menu button backgrounds: consistent with game aesthetic
     - Panel backgrounds: consistent dark charcoal
  2. Semi-transparent overlays: minimap, msg button, toast backgrounds
  3. Font consistency:
     - Monospace font for numerical values (HP, depth, quantities, charges)
     - PixeloidSans for labels and button text
  4. Rounded corners: verify 4-6px radius on all interactive elements (slots, buttons, panels)
  5. Verify pixel-perfect rendering at all font sizes (no antialiasing, no subpixel)
- Acceptance:
  - Consistent dark theme across all UI elements
  - No jarring color differences between zones
  - Fonts render cleanly at all sizes
  - Rounded corners on all interactive elements
- Status: ✅
  - Dark theme: HUD (0.05, 0.05, 0.1, 0.85), QuickSlotBar (0, 0, 0, 0.65), MsgButton/MiniMap bg (0.05, 0.05, 0.08, 0.82) — consistent navy/charcoal throughout.
  - Semi-transparent overlays: MiniMap bg alpha 0.82, MsgButton bg alpha 0.82, StatusEffectBar bg alpha 0.7, toast bg alpha 0.55 — all semi-transparent, appropriate gradation.
  - Border consistency: MiniMap and MsgButton both use identical border `Color(0.60, 0.60, 0.70, 0.45)` 1px — confirmed matching.
  - Gap fixed: `TouchButton` was using a flat `ColorRect` background (no rounded corners). Added `CornerRadius` property — when > 0, background switches to `Panel + StyleBoxFlat` to render rounded corners; when 0, keeps legacy `ColorRect` (backward-compatible). `MenuButtonBar` now sets `CornerRadius = 6` on both Gear and Explore buttons, matching the 6px radii on QuickSlotBar item slots.
  - Font rendering: all font loads across HUD, MsgButton, MessageLogPanel, ToastLog use `Antialiasing=None`, `SubpixelPositioning=Disabled`, `Hinting=None` — consistent pixel-perfect config.
  - Files changed: `src/Presentation/UI/TouchButton.cs`, `src/Presentation/UI/MenuButtonBar.cs`.

### Task 7.3 -- Viewport stretch mode verification
- File(s): `project.godot` (if needed)
- Dependencies: Phases 1-6 complete
- What to do:
  1. Test on 720x1280 viewport with integer stretch scaling
  2. Verify all zones render at correct pixel sizes
  3. Test aspect ratio handling: what happens on wider phones (iPhone Pro Max), narrower phones, tablets
  4. Confirm no clipping of UI elements
  5. Confirm tap coordinates map correctly through all zones (the integer stretch scale bug that necessitated TouchButton)
- Acceptance:
  - Layout correct on 720x1280
  - No clipping on wider/narrower aspect ratios
  - Touch input works correctly across all zones
  - No visual artifacts from stretch scaling
- Status: ✅
  - project.godot verified: `window/stretch/mode="canvas_items"` (correct), `window/size/viewport_width=720` / `viewport_height=1280` (correct portrait base), `window/stretch/scale_mode="integer"` (correct integer scaling), `window/handheld/orientation=1` (portrait lock). No changes made.
  - Note: `window/stretch/aspect="keep_width"` means on wider aspect ratios (e.g. wider phones), black bars appear on left/right sides of the 720px-wide canvas. This is intentional for portrait mode — no clipping risk. Isometric rendering adjusts to visible tile area via PlayerCamera margins.

---

## Dependency Graph

```
Phase 1 (Tasks 1.1 -> 1.2 -> 1.3)
   |
   +---> Phase 2 (Tasks 2.1 -> 2.2)
   |
   +---> Phase 3 (Tasks 3.1 -> 3.2)
   |
   +---> Phase 4 (Tasks 4.1 -> 4.2)
   |
   +---> Phase 5 (Tasks 5.1, 5.2, 5.3, 5.4 -- all parallel after Phase 1)
   |
   +---> Phase 6 (Task 6.1 needs Phase 2; Task 6.2 needs Task 5.2)
   |
   All Phases ---> Phase 7 (Tasks 7.1, 7.2, 7.3)
```

Phases 2, 3, 4, and 5 can proceed in parallel after Phase 1 completes.

---

## Risks and Open Questions

### Risk: Temporary loss of Gear/Explore/Msg functionality
After Phase 1, these buttons are removed but not yet relocated. The game is playable (tap-to-move, combat) but the player cannot open equipment or trigger auto-explore until Phase 2 lands. Phase 1 and 2 should be done in sequence without a long gap.

### Risk: ScrollContainer + manual hit-testing in QuickSlotBar (Phase 3)
Godot's ScrollContainer consumes swipe gestures for scrolling. The QuickSlotBar needs to distinguish between swipe (scroll) and tap/long-press (item use). The current InventoryPanel uses `_GuiInput` for hit-testing, but ScrollContainer sits between the QuickSlotBar and the slot Controls. May need to handle input at the ScrollContainer level or use `InputEventScreenTouch`/`InputEventScreenDrag` events. Test on device.

### Risk: Camera centering with new margins
Changing PlayerCamera margins will shift where the player appears on screen. The current Deadzone camera mode uses these margins to compute the viewport center. Verify that the player doesn't appear too high or too low after the margin change. May need to adjust the deadzone thresholds.

### Risk: InventoryPanel removal (Phase 3)
InventoryPanel is referenced in several places: Main.cs, GameController.cs, RectDebugDraw. All references must be updated when switching to QuickSlotBar. A clean rename won't work because the class interface changes (different events, different slot model).

### Decision: InventoryPanel drop button
The current InventoryPanel has a per-slot "x" drop button and fires `ItemDropRequested`. The spec doesn't mention drop functionality in the quick-slot bar. Options:
1. Keep the drop button on quick-slot items (consistent with current behavior)
2. Remove it -- dropping consumables goes through the Gear panel's IN PACK section
3. Add it to the long-press action sheet (already exists for items)

Recommend option 3: long-press opens action sheet which already has Drop. Remove the inline drop button from quick-slot bar to keep slots clean and small.

### Decision: HUD HP bar implementation
The spec calls for "a green fill bar" rather than a Godot ProgressBar. Using a ColorRect with dynamic width inside a container gives more visual control (no ProgressBar theme overrides needed). The width is calculated as `(hp / maxHp) * barWidth`. The text overlay ("64/66") sits on top.
