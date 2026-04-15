# Plan: Mobile Portrait Layout Overhaul

## Current State
- Status: complete
- All 7 phases complete (20 tasks). Task breakdown: `tasks/mobile_layout_tasks.md`
- Last updated: 2026-04-14
- Next step: none — fully implemented. Device testing (touch target verification) is a nice-to-have.
- Open issues: none (3 risk items from planning were resolved during implementation)

---

## Overview

Restructure the entire HUD/chrome layer to match the mobile portrait layout spec (`docs/YARL_MOBILE_LAYOUT_SPEC.md`). The spec defines 5 screen zones stacked vertically in a 720x1280 portrait viewport: status bar (7%), game viewport (63%), quick-slot bar (12%), menu buttons (10%), bottom safe area (4%). This is a presentation-layer-only change -- no logic layer modifications needed.

## Spec vs. Current State

### What exists and roughly matches

| Element | Current implementation | Notes |
|---------|----------------------|-------|
| HP bar + depth | `HUD.cs` -- top row with HP label, ProgressBar, depth label | Needs restructuring: currently also contains Gear/Explore/Msg buttons and equipment summary that don't belong in the status bar |
| Equipment panel | `EquipmentPanel.cs` -- centered modal overlay with body-slot grid | Mostly matches spec. Needs to become full-screen overlay instead of centered 680x640 modal |
| Toast messages | `ToastLog.cs` -- bottom-left stacking toasts with fade | Mostly matches. Needs left-border color accent per spec. Currently uses uniform dark bg |
| Minimap | `MiniMap.cs` -- top-right of UILayer, 2px/tile | Matches spec position. Needs semi-transparent bg, rounded corners, tap-to-expand |
| Quick-bar (consumables) | `InventoryPanel.cs` -- bottom-anchored 110px strip | Needs to become a full-width row with weapon indicator slot + 5 consumable slots per spec |
| Explore/Gear buttons | `HUD.cs` -- small buttons in top row | Need to move to dedicated menu button zone below quick-bar |
| Msg button | `HUD.cs` -- small button in top row | Needs to become a viewport overlay (bottom-left corner) per spec |
| Status effect badges | `StatusEffectBar.cs` -- row inside HUD | Needs to move -- probably stays in status bar zone or becomes viewport overlay |
| Enemy HP bar | `HUD.cs` -- panel inside HUD (tracked target) | Spec wants floating bars above enemy sprites in the viewport, not in the HUD |

### What needs structural changes

1. **HUD.cs is monolithic** -- currently contains status, enemy HP, buttons, equipment summary, status badges all in one 200px top strip. Needs to be decomposed into separate zone controls.
2. **Main.tscn layout** -- HUD is 200px TopWide, InventoryPanel is 110px BottomWide. These anchors/offsets define the current zone sizes and need to change to match the 5-zone spec.
3. **EquipmentPanel.cs** -- centered 680x640 modal. Spec wants full-screen overlay.
4. **ToastLog placement** -- currently anchored to middle of screen with manual offsets. Needs to anchor to bottom-left of viewport zone.

### What's net new

1. **Weapon indicator** -- far-left slot in quick-bar showing current weapon type with tap-to-toggle. No existing implementation.
2. **Floating enemy HP bars** -- small red bars above enemy sprites in the viewport. Currently enemy HP is shown as a panel inside HUD.cs. Needs new system in EntitySpriteManager or a new overlay.
3. **Msg button as viewport overlay** -- small icon button in bottom-left of viewport zone. Currently a text button in the HUD top row.
4. **Bottom safe area** -- 4% padding for iPhone home indicator. No existing implementation.
5. **Left-border color accent on toasts** -- spec wants colored left border (green/red) on toast messages instead of uniform background.

---

## Phases

### Phase 1: Screen Zone Restructuring

**Goal:** Establish the 5-zone vertical layout in Main.tscn and refactor HUD into a minimal status bar.

**Screen budget (1280px total):**
- Zone 1 -- Status bar: ~90px (7%)
- Zone 2 -- Viewport: ~806px (63%)
- Zone 3 -- Quick-slot bar: ~154px (12%)
- Zone 4 -- Menu buttons: ~128px (10%)
- Zone 5 -- Bottom safe area: ~51px (4%)

Total: ~1229px + rounding = 1280px. The viewport at 806px gives roughly 25 iso tile rows of visibility at the default zoom, which is adequate.

**Files to change:**

1. **`src/Presentation/Main.tscn`**
   - Replace the current 2-node layout (HUD 200px top, InventoryPanel 110px bottom) with 5 zone containers in UILayer
   - Zone names: `StatusBar`, `ViewportOverlay`, `QuickSlotBar`, `MenuButtons`, `BottomSafeArea`
   - ViewportOverlay is a passthrough (MouseFilter=Ignore) that sits over the viewport area for minimap/toast/msg button placement

2. **`src/Presentation/UI/HUD.cs`** -- Major refactor
   - Strip down to status bar only: HP fill bar + current/max text overlay + depth indicator ("D:1")
   - Remove: Gear button, Explore button, Msg button, equipment summary label, enemy HP panel, status effect bar
   - The HP bar becomes a green fill bar spanning most of the width (not a Godot ProgressBar -- a styled ColorRect for the fill bar look described in spec)
   - Depth indicator as small text to the right
   - Target height: ~90px including top safe area padding
   - Keep the `OnTurnCompleted` / `Refresh` methods but remove enemy HP tracking (moves to Phase 4)

3. **`src/Presentation/Main.cs`** -- SetupPresentation changes
   - Update node path references from `UILayer/HUD` to `UILayer/StatusBar` (or keep the name but update anchor/size)
   - Wire quick-slot bar and menu buttons to new zone nodes
   - Remove wiring of Gear/Explore/Msg from HUD events (they move to new locations)
   - Minimap offset changes (currently offset 210px from top to sit below HUD -- needs recalculation for new 90px status bar)

**Acceptance criteria:**
- Status bar is a slim ~90px row at top with HP bar + depth only
- Game viewport fills ~63% of screen height
- Quick-slot bar zone exists (can be empty initially)
- Menu button zone exists (can be empty initially)
- Bottom safe area padding present
- Game remains playable (tap-to-move works, camera centers correctly)
- Minimap renders in correct position (top-right of viewport zone, not overlapping status bar)

**Risks:**
- Viewport size reduction from ~80% to ~63% changes the amount of visible map. Camera centering logic in `PlayerCamera.cs` uses `GetViewport().GetVisibleRect()` which returns the full window -- but the viewport zone is smaller. May need to constrain the camera to account for UI overlap, or the spec may be fine since the viewport is the game world rendered across the full window with UI overlaid on top. Need to verify: does the game render under the HUD currently, or is the viewport actually smaller?
- Current HUD at 200px + InventoryPanel at 110px = 310px of chrome on a 1280px screen leaves 970px (~76%) for viewport. The spec wants 63% = 806px of clear viewport + overlays. The difference is that the spec moves chrome _below_ the viewport (quick-bar + menu buttons = 282px below). So the actual rendering approach doesn't change -- the game world renders full-screen and UI layers sit on top via CanvasLayer.

---

### Phase 2: Menu Buttons Zone

**Goal:** Create the two-button row (Gear + Explore) in the menu button zone.

**Files to change:**

1. **New file or inline in Main.cs** -- `MenuButtonBar` control (or build inline like current HUD approach)
   - Two wide TouchButton instances side by side, each ~34px tall, rounded corners
   - "Gear" button: opens equipment panel overlay
   - "Explore" button: triggers auto-explore
   - Full-width layout, each button gets ~half screen width
   - Minimum touch target: 44pt height (34px seems too small -- may need 44px+ to meet HIG)
   - Wire events: GearRequested, ExploreRequested

2. **`src/Presentation/Main.cs`**
   - Wire menu button events to GameController / EquipmentPanel (moved from HUD)
   - Update `SetAutoExploreActive` to target the new Explore button location

3. **`src/Presentation/UI/HUD.cs`**
   - Confirm Gear/Explore/Msg buttons fully removed (done in Phase 1)

**Acceptance criteria:**
- Two buttons visible below the quick-slot bar
- Gear opens equipment panel
- Explore triggers auto-explore, button shows "Exploring..." state
- Both buttons have >= 44pt touch targets
- Buttons don't overlap with quick-slot bar or bottom safe area

**Note on spec ambiguity:** The spec says buttons are ~34px tall but Apple HIG requires 44pt minimum. Implementation should use 44px minimum. At 128px zone height, two rows aren't needed -- a single row of two buttons at 48px + padding fits.

---

### Phase 3: Quick-Slot Bar Refactor

**Goal:** Replace the current InventoryPanel with a scrollable consumable strip + weapon indicator.

**Design decisions (confirmed):**
- Auto-populate: bar shows all consumables and wands in inventory order. No manual slot assignment.
- Scrollable horizontal row: ~44px slots, swipe to reveal overflow. Works for any inventory size.
- No empty-slot placeholders ("+" icons) — the bar simply shows what you have.
- Weapon indicator slot on far left with a separator line.

**Files to change:**

1. **`src/Presentation/UI/InventoryPanel.cs`** -- Major refactor (or replace entirely as `QuickSlotBar.cs`)
   - Far-left: weapon indicator slot (~44x44px) with 1px separator line on the right
     - Shows current MainHand weapon icon + truncated name label below
     - Tap: no-op stub with toast "Ranged toggle coming soon" (ranged combat not yet implemented)
     - Long-press: open weapon detail via ActionSheet/InspectPanel
   - Scrollable HBoxContainer filling remaining width, containing all consumable/wand slots
     - Each slot ~44x44px, rounded corners (6px radius)
     - Colored background tint by item type (red-ish for health potions, blue for mana/arcane, etc.)
     - Item icon centered in slot
     - Quantity badge in bottom-right corner (stack count for potions; charges for wands; none for scrolls)
     - Tap: use item (existing ItemTapped event)
     - Long-press: show item details (existing ItemLongPressed event)
   - No empty slot placeholders — bar content = inventory content

2. **`src/Presentation/Main.cs`**
   - Update InventoryPanel/QuickSlotBar creation and wiring in SetupPresentation
   - Update node path if class is renamed

3. **`src/Presentation/GameController.cs`**
   - `HandleInventoryTap` routes item use — should work unchanged
   - Add stub handler for weapon indicator tap (toast message)

**Acceptance criteria:**
- Weapon indicator visible on far left with separator, shows current weapon icon and name
- All consumables and wands visible in scrollable row with correct icons and quantity badges
- Tap a slot to use the item
- Long-press shows item details
- Swiping reveals overflow items
- Quick-bar refreshes correctly after item use, pickup, and drop
- Weapon indicator tap shows stub toast (no crash)

**Dependency:** Weapon toggle functionality deferred to ranged combat plan. Indicator is display-only for now.

---

### Phase 4: Floating Enemy HP Bars

**Goal:** Replace the HUD-embedded enemy HP panel with small red bars floating above enemy sprites in the viewport.

**Files to change:**

1. **`src/Presentation/Entities/EntitySpriteManager.cs`** -- Add floating HP bar management
   - For each monster that has taken damage (Hp < MaxHp), draw a small red ProgressBar or ColorRect above their sprite
   - Bar appears only when damaged -- don't clutter peaceful rooms
   - Proportional fill showing remaining HP
   - No text -- just the bar
   - Bars need to update position when sprites move (turn animation)
   - Bars need to hide when monster leaves FOV or dies

   Alternative approach: a new `FloatingHpBarOverlay` class that manages bar nodes on the EntityLayer, positioned relative to entity sprites. This keeps EntitySpriteManager focused on sprite management.

2. **`src/Presentation/UI/HUD.cs`** -- Remove enemy HP panel code
   - Remove `_enemyHpPanel`, `_enemyHpLabel`, `_enemyHpBar`, `_combatTargetId`
   - Remove enemy HP tracking from `OnTurnCompleted`
   - Simplify `Refresh()` to status bar only

3. **`src/Presentation/Main.cs`**
   - Create and wire the floating HP bar system in SetupPresentation
   - Update OnTurnCompleted to refresh floating bars

**Acceptance criteria:**
- Damaged monsters show a small red bar above their sprite
- Full-HP monsters show no bar
- Bar disappears when monster dies or leaves FOV
- Bar updates correctly during combat
- No enemy HP display remains in the HUD/status bar

**Risks:**
- Performance with many monsters. Each bar is a Control node on a CanvasLayer (UILayer) or a Node2D on EntityLayer. Using Node2D on EntityLayer is simpler -- the bar moves with the camera automatically. But it needs to be positioned in world space above the sprite.
- EntitySpriteManager already tracks sprite positions. The bar can be a child of the entity sprite node, offset upward by sprite height.

---

### Phase 5: Viewport Overlays (Minimap, Msg Button, Toast Restyle)

**Goal:** Position minimap, message button, and toasts correctly within the viewport zone. Restyle toasts with left-border accent.

**Files to change:**

1. **`src/Presentation/UI/MiniMap.cs`**
   - Add semi-transparent background (currently draws bg in `_Draw` -- needs rounded corners)
   - Add 0.5px border
   - Add tap-to-expand (full map view -- can be deferred to future phase)
   - Verify positioning: top-right of viewport zone (below status bar)

2. **`src/Presentation/Main.cs`**
   - Minimap offset: currently `OffsetTop = 210f` to sit below 200px HUD. With 90px status bar, change to ~100f
   - Create Msg button as a viewport overlay: semi-transparent background, ~32x32px, rounded corners, bottom-left of viewport zone
   - Wire Msg button to `_toastLog.RecallHistory()`

3. **`src/Presentation/UI/ToastLog.cs`**
   - Add left-border color accent to toast style
     - Green left border for positive events (heals, kills, buffs)
     - Red left border for danger events (damage taken, debuffs, death)
     - Gray/neutral for miss, expire, etc.
   - Adjust the `_toastStyle` StyleBoxFlat to add `BorderWidthLeft` and `BorderColor`
   - Need to create per-category styles instead of one shared style, or set border color per toast
   - Adjust positioning: bottom-left of viewport zone, above the Msg button

4. **`src/Presentation/UI/StatusEffectBar.cs`**
   - Decide placement: either stays in the slim status bar (if it fits) or moves to a viewport overlay position
   - Current implementation is a horizontal badge row -- could sit just below the status bar as a thin overlay

**Acceptance criteria:**
- Minimap has semi-transparent bg, rounded corners, correct position below status bar
- Msg button visible in bottom-left of viewport zone with icon styling
- Toasts show colored left border (green for positive, red for danger)
- Toast positioning doesn't overlap with Msg button or quick-slot bar
- Status effect badges visible and not clipped

---

### Phase 6: Full-Screen Panel Overlays

**Goal:** Make Equipment, Message History, and Explore panels open as full-screen overlays instead of centered modals.

**Files to change:**

1. **`src/Presentation/UI/EquipmentPanel.cs`**
   - Change `_panelContainer` from centered 680x640 to full-screen
   - Keep existing content layout (stats, body-slot grid, "IN PACK" list)
   - Add close button (X) in top-right, 44pt minimum touch target (already exists at 44x44)
   - Ensure scroll for "IN PACK" section if many items

2. **Message History panel** -- net new
   - Full-screen overlay showing scrollable message history
   - Triggered by Msg button
   - Currently `RecallHistory()` just re-shows recent toasts. Spec wants a full message log panel.
   - Could extend `CombatLog.cs` or build a new `MessageLogPanel.cs`
   - Close button (X) in top-right

3. **Explore panel** -- evaluate if needed
   - Spec mentions "Explore button opens exploration/autoexplore options"
   - Currently Explore button just toggles auto-explore on/off
   - If no options are needed yet, keep the toggle behavior on the button itself

**Acceptance criteria:**
- Equipment panel fills the full screen when opened
- Close button works and is large enough for touch
- Message history shows scrollable log of past events
- All panels dismiss cleanly and return to gameplay

---

### Phase 7: Polish and Touch Target Audit

**Goal:** Final pass ensuring all interactive elements meet 44pt minimum and visual styling matches spec.

**Files to change:**

1. All UI files -- audit touch target sizes
   - Quick-slot bar slots: spec says 42x42px which is close to 44pt. May need slight increase.
   - Menu buttons: ensure >= 44px height
   - Minimap expand area
   - Msg button: 32x32 per spec, but needs 44pt touch target (visual can be 32x32, hit area 44x44)

2. **Visual style consistency**
   - Dark theme throughout (dark navy/charcoal backgrounds) -- verify all panels
   - Semi-transparent overlays for viewport elements
   - Monospace font for numerical values (HP, depth, quantities)
   - Verify pixel font rendering at all sizes

3. **`src/Presentation/UI/TouchButton.cs`**
   - May need a visual-size vs hit-area split for small buttons (Msg, minimap)

**Acceptance criteria:**
- All interactive elements have >= 44pt touch targets
- Visual styling consistent across all zones
- No overlapping touch targets
- Works correctly on 720x1280 viewport with integer stretch scaling

---

## Dependencies

```
Phase 1 (zones) ──> Phase 2 (menu buttons)
Phase 1 (zones) ──> Phase 3 (quick-slot bar)
Phase 1 (zones) ──> Phase 5 (viewport overlays)
Phase 1 (zones) ──> Phase 4 (floating HP bars) -- independent of other phases
Phase 2 + Phase 3 ──> Phase 6 (full-screen panels)
All phases ──> Phase 7 (polish audit)
```

Phases 2, 3, 4, and 5 can proceed in parallel after Phase 1.

## Risks and Decisions

### Risk: Viewport rendering vs. zone layout
The current architecture renders the game world full-screen on `GameView` (Node2D) and overlays UI via `UILayer` (CanvasLayer layer=10). The 5-zone layout described in the spec is conceptual -- the actual implementation is likely to keep the same rendering approach (full-screen game world + overlaid UI zones). The "63% viewport" means 63% of the screen is clear of persistent chrome, not that the viewport is physically resized. Confirm this assumption before Phase 1 implementation.

### Risk: Camera centering with reduced clear viewport
`PlayerCamera.Update()` centers the player in the full viewport. With chrome covering ~37% of the screen (top + bottom), the player may appear off-center relative to the clear area. May need a camera offset to shift the player sprite upward into the clear viewport center.

### Risk: Minimap tap-to-expand
The spec mentions tap-to-expand for the minimap but gives no details on the expanded view. Recommend deferring full map view to a future task and noting it as planned.

### Risk: Weapon toggle (Phase 3)
Ranged combat is not implemented (`plan_ranged_combat.md` is not started). The weapon indicator can show the current weapon but toggle functionality should be stubbed with a toast message until ranged combat lands.

### Decision: InventoryPanel refactor vs. new class
`InventoryPanel.cs` could be refactored in place or replaced with a new `QuickSlotBar.cs` class. Given how different the spec layout is from the current strip, a new class may be cleaner. The old class handles consumable filtering and long-press correctly -- that logic should carry over.

### Decision: Floating HP bar implementation
Two approaches:
1. **Child of entity sprite** -- bar is a Node2D child of the Sprite2D, offset upward. Moves with camera automatically. Simple. But CanvasLayer UI text wouldn't apply.
2. **Separate overlay system** -- new class manages bar nodes on EntityLayer, synced with entity positions each frame. More control over visibility/animation.

Recommend approach 1 (child of sprite) for simplicity. A small ColorRect doesn't need CanvasLayer text features.

### Decision: StatusEffectBar placement
Three options:
1. Keep in status bar zone (may crowd the slim 90px bar)
2. Move to viewport overlay (below status bar)
3. Show in quick-slot bar zone (near the action)

Recommend option 2: a thin row just below the status bar, overlaying the viewport. Only visible when effects are active, so it doesn't permanently reduce viewport space.
