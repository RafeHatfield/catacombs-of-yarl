# Plan: Doors, Secret Doors, and Portal Network

Status: [ ] Not started
PoC reference: map_objects/game_map.py, services/portal_manager.py, config/portal_network.yaml

---

## What It Is

Three interrelated world-navigation features: physical doors (blocking/locking), secret passages (hidden doors), and inter-floor portals. Together they make the dungeon feel less procedural and more designed.

---

## Door System

### Door Types

| Type | State | Interaction |
|------|-------|-------------|
| `wooden_door` | Open / Closed / Locked | Walk into to open; walk into locked = "It's locked" |
| `locked_door` | Locked (requires key) | Iron key or specific quest key |
| `secret_door` | Hidden (looks like wall) | Revealed by Search action; then treated as normal door |

### Interaction

- **Open door**: Walk into closed door → door opens, player enters tile
- **Locked door**: Walk into → message "The door is locked." If key in inventory → auto-use key → door opens
- **Key types**: `iron_key` (generic, opens any non-quest locked door), quest keys (named, specific door)
- **Doors block projectiles** — closed doors stop arrows, spells. Open doors don't.
- **Monsters open doors** — if a monster can open doors (AI flag), it will. Some can't (mindless undead, slimes).

### Monster Interaction with Doors

```yaml
zombie:
  ai:
    can_open_doors: false   # walks into door forever
orc:
  ai:
    can_open_doors: true    # opens doors, chases player through
```

---

## Secret Doors

### Discovery

- Secret doors look identical to walls until discovered
- **Search action**: Player searches adjacent tile; discovers hidden doors in range
- **Ambient hints**: Wall alignment mismatches, slightly different wall texture (visual hint, not required)
- Once discovered: acts as a normal door (can be opened)

### Placement

- Level generator places secret doors based on configuration
- Always connect to a meaningful space (secret room, shortcut, lore area)
- Testing level 92 dedicated to secret room discovery mechanics

---

## Portal Network

### What It Is

A set of portal pairs (or larger networks) that allow instant travel between points. Portals can be within a floor (short-range) or between floors (long-range). They create optional exploration routes and lore-tied shortcuts.

### Configuration (portal_network.yaml)

```yaml
portals:
  - id: catacombs_entrance
    from: {floor: 1, position: [45, 20]}
    to: {floor: 3, position: [10, 10]}
    locked: true
    key: ancient_key
    description: "A shimmering archway of dark stone"

  - id: lab_shortcut
    from: {floor: 4, position: [22, 14]}
    to: {floor: 4, position: [60, 30]}
    locked: false
```

### Mechanics

- Walking into a portal tile triggers teleport to destination
- **Locked portals**: display "The portal is dormant" until key item is used
- **Network validation**: all portal pairs must be valid at floor-build time (no orphan portals)
- Portals are visual landmarks — large tiles, distinctive sprite

### Teleport Traps vs Portals

Teleport traps are random-destination, uncontrolled. Portals are fixed destinations, discoverable. Both use the same underlying teleport action, but portals require LevelTransition context.

---

## Key Items

```yaml
iron_key:
  description: "A plain iron key. Opens common locks."
  opens: locked_door_generic

ancient_key:
  description: "A key carved from bone. Cold to the touch."
  opens: catacombs_entrance
```

Keys are consumable (disappear after use) unless designed otherwise.

---

## Implementation Notes

- Doors are map entities or tile properties (TBD based on C# arch)
- `SearchAction` scans adjacent tiles for `SecretDoor` component
- Portal tiles have `PortalComponent` with destination floor/position
- `MovementService.TeleportTo()` handles both trap and portal destinations
- Level generator needs `door_generation_config` in YAML (frequency, locked %, secret %)

---

## C# Port Checklist

- [ ] `DoorEntity` (or door tile type) with Open/Closed/Locked states
- [ ] Walk-into interaction (opens normal doors, checks key for locked)
- [ ] `iron_key` item type; auto-use on locked door attempt
- [ ] Quest-key items (specific named keys)
- [ ] `Monster.CanOpenDoors` flag in YAML
- [ ] Secret door tile type (looks like wall until revealed)
- [ ] Search action: scan adjacent tiles, reveal secret doors
- [ ] `PortalComponent` on tiles with destination
- [ ] `portal_network.yaml` loading and validation
- [ ] Portal activation (walk-in → teleport)
- [ ] Locked portal + key requirement
- [ ] Doors blocking projectiles
- [ ] Level generator: door placement, locked %, secret room connections
- [ ] Testing level configs (91, 92, 94)
