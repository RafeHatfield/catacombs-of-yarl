# Milestone: Visual Foundation

**Status:** PLANNING
**Created:** 2026-03-24
**Priority:** High — needed to evaluate iso vs 2D presentation decision

Two parallel tracks: tileset coherence (quick visual win, Presentation only) and items on floor (gameplay + visual, needs Logic + Presentation). Camera deadzone is a separate quick build tracked in the visibility-movement-exploration plan.

---

## Context

The game is functional but the iso presentation isn't showing its best self yet:
1. Random tile variation (1-of-7 per tile) reads as visual noise — rooms look incoherent
2. No items on the floor means auto-explore has nothing to find, and the dungeon feels empty
3. These two together are blocking the iso vs 2D decision

The tileset (Oryx) is much richer than currently used. The fix is not "add more variety" — it's "be more intentional with variety." Room-consistent theming + sparse accents will look dramatically better.

Items on floor provides the first real reason to explore. Auto-explore interrupt "new item in unexplored area" is already stubbed.

---

## Track A: Tileset Coherence

**Goal:** Rooms look intentional. Different areas feel distinct. Decorative details reward exploration.

### A.1 Room-based theming in DungeonRenderer

Currently `DungeonRenderer.Render` picks tile variants by `PositionHash(x, y) % 7`. Replace with room-aware selection.

**The problem:** `DungeonRenderer` only receives `GameMap` — it doesn't know room boundaries. Two options:
- Pass `GeneratedMap` (which has `Rooms` list) to `Render`
- Store room theme per tile in `GameMap` itself

**Recommendation:** Add a `TileTheme` enum to the Logic layer and a `_theme[,]` array to `GameMap`. `DungeonFloorBuilder` assigns themes to rooms when carving them. `DungeonRenderer` reads `GetTileTheme(x, y)` to select sprites. This is clean and keeps the renderer dumb.

**`TileTheme` enum** (Logic layer, `src/Logic/ECS/TileTheme.cs`):
```csharp
public enum TileTheme
{
    Grey,    // Default dungeon — grey stone
    Crypt,   // Darker, more ornate — deeper floors
    Moss,    // Overgrown — very deep / outdoor adjacent
    Dirt,    // Earthy — caves, natural areas
    Wood,    // Wooden floors — taverns, barracks (future)
}
```

**`GameMap` additions:**
```csharp
private readonly TileTheme[,] _theme;  // initialized to Grey

public TileTheme GetTileTheme(int x, int y) =>
    InBounds(x, y) ? _theme[x, y] : TileTheme.Grey;

public void SetTileTheme(int x, int y, TileTheme theme)
{
    if (InBounds(x, y)) _theme[x, y] = theme;
}
```

**`DungeonFloorBuilder` room theming:**
When carving a room, assign a theme based on depth:
- Depth 1-3: mostly Grey, rare Crypt accent room (10% chance)
- Depth 4-6: mostly Crypt, rare Moss accent room
- Depth 7+: mostly Moss, rare Crypt accent room
- Corridors: always Grey/Dirt (inherit from connecting room or force Dirt)

Each room gets ONE theme assigned to all its tiles when carved.

### A.2 Floor tile selection rules (DungeonRenderer)

Per-tile selection within a themed room:
- **85% primary tile** (e.g. `tileA` for Grey rooms) — selected when `PositionHash(x,y) % 20 >= 3`
- **15% accent tile** (e.g. `tileB` or `tileC`) — the rest
- No 7-variant random spread — max 2-3 variants per theme

**Theme → floor tile mapping:**
```
Grey  → primary: floor_tileA  | accent: floor_tileB (rare tileC for large rooms)
Crypt → primary: floor_tileD  | accent: floor_tileE
Moss  → primary: floor_tileF  | accent: floor_tileG (or dirtA in natural zones)
Dirt  → primary: floor_dirtA  | accent: floor_dirtB
Wood  → primary: floor_wood   | accent: floor_tileA (wood + stone border)
```

### A.3 Wall family per theme

Replace `WallVariants = { greyA..greyG }` (all random) with theme-matched walls:
```
Grey  → wall_greyA primary, greyB accent, rare grey_cracked (2% chance)
Crypt → wall_cryptA primary, cryptB accent, rare crypt_cracked
Moss  → wall_mossA primary, mossB accent, rare moss_cracked
```

Cracked wall variants appear at low frequency based on `PositionHash` — adds wear without chaos.

### A.4 Depth-based wall family defaults

`DungeonFloorBuilder` sets room themes. Wall theme follows floor theme (same `TileTheme` value drives both). The renderer maps `TileTheme` → wall family name.

### A.5 Decorative detail overlays (optional, low priority)

The tileset has bones (A/B/C) and blood (A/B/C) overlays. These can be placed as a third render pass:
- `bones` — 2% chance on any floor tile in rooms (not corridors)
- `blood` — 1% chance, slightly higher near where monsters spawned (position proximity to spawn points)
- `torch_left` / `torch_right` — placed on wall tiles adjacent to room interiors, sparse (1 per room average)

These are cosmetic only. Implement as a third pass in `DungeonRenderer.Render` if time allows, defer otherwise.

### Files changed (Track A)
```
src/Logic/ECS/TileTheme.cs             — new enum
src/Logic/ECS/GameMap.cs               — _theme[,] array + GetTileTheme/SetTileTheme
src/Logic/Core/DungeonFloorBuilder.cs  — assign room themes on carve
src/Presentation/Map/DungeonRenderer.cs — theme-aware tile selection
```

No test changes required — purely visual.

---

## Track B: Items on the Floor

**Goal:** Items spawn visibly in dungeon rooms. Player can pick them up by walking over them or tapping. Auto-explore stops when a new item is spotted.

### B.1 What items spawn

Use the existing `ItemFactory` and `ConsumableFactory`. `DungeonFloorBuilder` already has `EntityPlacer` which handles guaranteed spawns and procedural fill. Items to spawn per floor:
- 1-2 consumables (healing potions) — guaranteed, placed in rooms
- 0-1 equipment (weapon or armor) — procedural, depth-scaled rarity
- Deeper floors: more items, better quality

This is already partially specified in `config/level_templates.yaml` — extend it there rather than hardcoding in C#.

### B.2 Item entity visual component

Items on the floor need a visual marker. No item art assets exist yet in `assets/`. Two options:
- **Option A (placeholder)**: Colored `ColorRect` or simple colored sprite. Consumables = green circle, equipment = gold square.
- **Option B (tileset)**: Use `iso_dun_selectA.png` as a generic "item here" indicator with a color tint per item type.

**Recommendation: Option B.** `selectA` is designed as an isometric tile overlay — it'll look intentional rather than placeholder-ish. Tint with `Modulate`:
- Consumable (potion): `new Color(0.2f, 0.8f, 0.2f)` — green
- Weapon: `new Color(0.8f, 0.6f, 0.1f)` — gold
- Armor: `new Color(0.4f, 0.6f, 0.9f)` — blue

When proper item art assets arrive, swap in the real sprites — the tint-based system extends naturally.

### B.3 ItemSpriteManager (Presentation)

New class `src/Presentation/Entities/ItemSpriteManager.cs`:
- Tracks item entities with floor sprites
- `Initialize(GameState state)` — create sprites for all floor items
- `UpdateVisibility(GameState state)` — show/hide based on FOV (items are hidden in unexplored areas)
- `RemoveItem(int entityId)` — called when item is picked up

`Main.cs` owns `_itemSprites`, initializes in `SetupPresentation`, updates in `OnTurnCompleted`.

### B.4 Item entity identification

Currently `Entity` has no way to identify "is this an item on the floor." Options:
- Check for `Item` component (already exists in Logic)
- Check for `Consumable` component
- Add `IsFloorItem` flag to Entity

**Recommendation:** Items on the floor have either an `Item` component or `Consumable` component. `ItemSpriteManager` checks both. No new flag needed.

### B.5 Pick-up interaction

**Walk-over (primary):** After each player move, check if player is standing on a tile with a floor item → auto-pick up. Implemented in `TurnController.ResolvePlayerMove` or as a post-move check.

**Tap-to-pick-up:** `InputHandler` already handles tap-on-entity. Add item pickup as an `ActionKind.PickUp` action. `TurnController` handles it.

**Inventory:** `Player.Get<Inventory>()` already exists. Add item to inventory, remove from `GameState.FloorItems` (new list), fire `PickUpEvent`.

**`GameState` addition:**
```csharp
public List<Entity> FloorItems { get; } = new();  // Items sitting on the floor
```
`DungeonFloorBuilder` populates this. `TurnController` removes from it on pickup.

### B.6 Auto-explore interrupt for new items

`AutoExploreSystem.CheckInterrupts` already has the architecture. Add:

```csharp
// New item in unexplored area (not in explored snapshot at activation)
foreach (var item in state.FloorItems)
    if (state.Map.IsVisible(item.X, item.Y)
        && !ae.ExploredSnapshot.Contains((item.X, item.Y)))
        return "Item found";
```

This uses the existing two-pass explored snapshot logic — won't interrupt for items in already-known areas.

### B.7 TurnEvent additions
```csharp
public sealed class PickUpEvent : TurnEvent
{
    public int ActorId { get; init; }
    public int ItemId { get; init; }
    public string ItemName { get; init; } = "";
}
```

### B.8 Level templates update

In `config/level_templates.yaml`, add guaranteed floor items to depth 1+ templates. Use existing `guaranteed_spawns` mechanism with `type: "consumable"` and `type: "item"` entries.

### Files changed (Track B)
```
src/Logic/ECS/TurnEvent.cs             — PickUpEvent
src/Logic/Core/PlayerAction.cs         — ActionKind.PickUp
src/Logic/Core/GameState.cs            — FloorItems list
src/Logic/Core/TurnController.cs       — walk-over pickup, PickUp action
src/Logic/Core/DungeonFloorBuilder.cs  — populate FloorItems
src/Logic/Core/AutoExploreSystem.cs    — item interrupt condition
src/Presentation/Entities/ItemSpriteManager.cs — new
src/Presentation/GameController.cs    — pass PickUp event to sprite removal
src/Presentation/Main.cs              — _itemSprites field, wiring
config/level_templates.yaml           — add floor item entries
```

---

## Sequencing

```
Track A (Tileset)    — no logic changes except TileTheme enum + GameMap field
                       Purely visual. Can build immediately, independently.

Track B (Items)      — touches Logic and Presentation
                       Build after Track A confirms the visual direction.
                       Estimated: 2-3 builder sessions.
```

Build Track A first: it's quick and has the highest visual impact per hour. If the iso presentation looks significantly better with coherent theming, that informs whether Track B is worth investing in for the iso path.

---

## Acceptance Criteria

**Track A:**
- [ ] Rooms have consistent floor tile themes within each room
- [ ] Different room types use visibly different floor/wall palettes
- [ ] Wall cracked variants appear sparsely (visual wear)
- [ ] Corridors visually distinct from rooms
- [ ] Depth 1 looks like stone dungeon, not random noise

**Track B:**
- [ ] Items (potions, weapons) visible as floor sprites in rooms
- [ ] Items hidden in unexplored areas (FOV-gated)
- [ ] Player auto-picks up by walking over item
- [ ] Pick-up logged in combat log
- [ ] Auto-explore stops when new item spotted in unexplored area
- [ ] Item disappears from floor when picked up

---

## Out of Scope

- Real item art sprites (placeholder tint approach sufficient for eval)
- Item drop on monster death (future: loot system)
- Shops or special item rooms
- Torch animation (torches are static overlays for now)
- Grass / outdoor floor themes (future: outdoor levels)
