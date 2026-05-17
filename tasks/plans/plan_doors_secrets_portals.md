# Plan: Doors, Secret Doors, and Portal Network

Status: [x] Complete
PoC reference: map_objects/game_map.py, services/portal_manager.py, config/portal_network.yaml

---

## What Was Built

All door/secret-door/locked-door/portal logic is implemented and tested. The following components are complete:

### Logic Layer (src/Logic/)

**TileKind** (`src/Logic/ECS/TileKind.cs`)
- `TileKind.Door` — closed door: blocks movement/LOS until opened
- `TileKind.DoorOpen` — open door: walkable and LOS-transparent
- `TileKind.LockedDoor` — locked: impassable even with `canPassDoors=true`; requires matching key
- `TileKind.SecretDoor` — renders as wall; passive proximity detection reveals it as `Door`

**GameMap** (`src/Logic/ECS/GameMap.cs`)
- `IsWallTile(x,y)` returns `true` for both `Wall` and `SecretDoor` (critical for autotile renderer)
- `IsDoorTile(x,y)` covers `Door`, `DoorOpen`, `LockedDoor`
- `CanMoveToWith(..., canPassDoors)` — `canPassDoors` only bypasses `Door`, never `LockedDoor`

**KeyItemComponent / LockableComponent** (`src/Logic/ECS/`)
- `KeyItemComponent.LockColorId` — matches key color to door/chest color (0=red … 4=purple)
- `LockableComponent.IsLocked` / `LockColorId` — used for locked chests

**TurnController** (`src/Logic/Core/TurnController.cs`)
- Locked door bump without key → `LockedDoorBumpedEvent` (free action; turn reverted)
- Locked door bump with wrong key → same free-action, key retained
- Locked door bump with matching key → `DoorUnlockedEvent` + `KeyConsumedEvent`; tile → `DoorOpen`; key removed from inventory; `LockedDoors` registry updated
- `CheckSecretDoorDetection()` — 25% chance per adjacent `SecretDoor` per turn; reveals to `Door` + emits `SecretDoorFoundEvent` with flavor hint
- `TryOpenDoor()` — `CanOpenDoors` flag on `Fighter`; monsters with `false` cannot open doors

**EntityPlacer** (`src/Logic/Core/EntityPlacer.cs`)
- `PlaceLockedDoorPair()` — dead-end room door → `LockedDoor`; key placed elsewhere; color offset from chest colors
- `PlaceSecretDoors()` — 20% chance per floor; finds wall between two rooms; changes to `SecretDoor`
- `PlacePortalPairs()` — fixed inter-floor portal pairs with `PortalComponent` destination

**TurnEvents** (`src/Logic/Core/TurnEvent.cs`)
- `LockedDoorBumpedEvent` — emitted when door can't be unlocked
- `DoorUnlockedEvent` — door opened with key
- `KeyConsumedEvent` — key item removed
- `SecretDoorFoundEvent` — proximity reveal; carries `Hint` flavor text

### Presentation Layer (src/Presentation/)

**DungeonRenderer** (`src/Presentation/Map/DungeonRenderer.cs`)
- `SecretDoor` — NOT in Pass 2 overlay list; renders as wall via Pass 1 autotile (correct)
- `LockedDoor` — Pass 2 uses `themeConfig.GetDoorLocked(theme)` sprite
- Locked door key icon overlay (small scaled key in top-right corner, color-tinted)
- `DoorOverlaySprites` tracked separately for FOV modulation
- `LockKeyOverlaySprites` tracked for locked door key icons
- `RefreshLockedChestTints()` in Main.cs re-applies lock tint after `UpdateVisibility` resets to white

**Main.cs** (`src/Presentation/Main.cs`)
- `HandleSecretDoorFound(x,y)` — swaps wall base sprite to floor, adds door overlay sprite
- `HandleDoorUnlocked(x,y)` — removes key icon overlay, swaps locked sprite to open
- `OnTurnCompleted` event loop handles all door events with toast messages:
  - `SecretDoorFoundEvent` → `_toastLog?.AddMessage(secretEvt.Hint)`
  - `LockedDoorBumpedEvent` → "This door is locked. You need a {color} key."
  - `DoorUnlockedEvent` → "The {color} key unlocks the door!"

**GameController.cs** (`src/Presentation/GameController.cs`)
- `TileKindToInspectKey()` maps `LockedDoor` → `"__door_locked"`, `SecretDoor` → `"__secret_door"` for long-press inspect panel

### Tests (`tests/Core/LockedDoorTests.cs`)

Comprehensive coverage including:
- `LockedDoor` non-walkable, correct tile kind, is door tile, `canPassDoors` bypass blocked
- Bump without key → free action + `LockedDoorBumpedEvent`; no key consumed
- Bump with matching key → `DoorUnlockedEvent` + `KeyConsumedEvent`; door opens; turn consumed
- Wrong key → free action; door stays locked; key retained
- `PlaceFloorFeatures` depth 1 → no locked doors
- `PlaceFloorFeatures` depth 2+ → locked door in dead-end room when present
- Lock color offset from chest color ids
- `SecretDoor` non-walkable, counts as wall tile for renderer, can't pass even with `canPassDoors`
- `CheckSecretDoorDetection` eventually reveals adjacent `SecretDoor` → `TileKind.Door`
- Revealed secret door emits non-empty hint text
- Secret door more than 1 tile away is NOT detected
- Monster with `CanOpenDoors=false` cannot open a door
- Monster with `CanOpenDoors=true` does open a door

---

## Deferred

**Projectile/spell blocking by closed doors** — explicitly deferred to `plan_ranged_combat.md`.
Closed doors blocking arrows and spells requires the projectile path trace system, which belongs in that plan.

**Testing level configs (91, 92, 94)** — dropped. Unit tests cover all behaviors; scenario-level test files are not needed.

---

## Original Design Notes (for reference)

Three interrelated world-navigation features: physical doors (blocking/locking), secret passages (hidden doors), and inter-floor portals. Together they make the dungeon feel less procedural and more designed.

### Door Types

| Type | State | Interaction |
|------|-------|-------------|
| `wooden_door` | Open / Closed / Locked | Walk into to open; walk into locked = "It's locked" |
| `locked_door` | Locked (requires key) | Iron key or specific quest key |
| `secret_door` | Hidden (looks like wall) | Passive detection; then treated as normal door |

### Key Items

Keys are consumable (disappear after use). Color-coded (red/blue/green/gold/purple) to match doors and chests.

### Portal Network

`PlacePortalPairs()` places fixed inter-floor portal pairs. `PortalComponent` carries destination floor/position. Walking into a portal tile triggers teleport.
