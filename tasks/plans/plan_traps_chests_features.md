# Plan: Traps, Chests, and Dungeon Features

Status: [x] Complete — superseded by plan_interactive_props_traps.md (9 trap types, floor hazards) and the chests/signs/murals feature (session 2026-04-18b). Disarm action and active Search deferred and noted in plan_interactive_props_traps.
PoC reference: components/trap.py, level_templates.yaml

---

## What It Is

Interactive dungeon features beyond monsters and items. Traps create hazard and tactical decisions. Chests are loot containers. Signs and murals deliver lore. Together these make floors feel like real places instead of just combat arenas.

---

## Trap System

### Detection

- **Passive detection** — 25% chance when a character ENTERS a trapped tile (before effect fires)
  - Success: "You notice a spike trap just in time!" — player can choose to step back or disarm
  - Failure: trap fires
- **Active detection** — Search action on adjacent tile; reveals all traps in range
- Monsters never detect traps (they always trigger them) — unless they're trap-aware (special AI flag)

### Disarm

After detection:
- Player can attempt disarm: opposed check (player DEX vs trap DC)
- Success: trap is removed, may yield crafting component (future)
- Failure: trap fires anyway

### Trap Types

| Trap | Effect | Notes |
|------|--------|-------|
| `spike_trap` | Direct physical damage + BleedEffect | Most common |
| `web_trap` | Applies SlowedEffect or EntangledEffect | Spider-themed floors |
| `alarm_plate` | Alerts all monsters in room | No damage, but devastating |
| `root_trap` | Applies EntangledEffect (complete immobilize) | |
| `teleport_trap` | Random relocation within floor | Separates player from gear/allies |
| `fire_trap` | BurningEffect + creates fire hazard tile | |
| `gas_trap` | PoisonEffect + creates poison gas cloud | |
| `hole_trap` | Drops player to next depth | Skip floors, lose control |

### Trapped Chests

Chests can also be trapped (spike variant common). Same detection/disarm rules. If disarmed successfully, chest opens normally.

### YAML Configuration

```yaml
spike_trap:
  damage: 1d8
  effect: bleed
  effect_duration: 3
  dc: 12          # disarm difficulty
  detection_chance: 0.25
```

---

## Chest System

### Chest Types

| Type | Contents | Notes |
|------|---------|-------|
| Standard chest | Loot per floor band | Most common |
| Trapped chest | Loot + spike trap on open | Visible on floor (no detection needed) |
| Locked chest | Loot (better than standard) | Requires matching key |
| Boss chest | Guaranteed quality loot | Spawned in boss rooms |
| Mimic | MONSTER — attacks when opened | Rare, late game |

### Opening a Chest

- Walk into it (or tap — mobile) to interact
- Trapped: DC 10 passive notice (same as traps), or just take the hit
- Locked: "This chest is locked." — needs key in inventory
- Contents generated at floor creation (not when opened) — but revealed on open

### Chest Loot Generation

Uses the same loot policy as floor items, but typically at a higher rarity band. Boss chests are guaranteed to contain at least one equipment upgrade.

---

## Signs / Signposts

Simple environmental storytelling:
- Walk into (or tap) to read
- Display message in a dialog popup
- Used for: navigation hints ("The stairway lies to the east"), lore, warnings, hints

YAML:
```yaml
sign:
  message: "Beware the catacombs below. None return."
```

---

## Murals / Inscriptions

More elaborate lore delivery:
- Stone wall engravings on specific room walls
- Discovered by Search action (same as secret doors)
- Longer text, supports multi-page display
- Used for: boss backstory, world lore, secret hints (Zhyraxion's name, rituals)

---

## Corpses (Related Feature)

When monsters die, they leave corpses on the tile. Corpse system is primarily for necromancer mechanics (see monster_specials plan) but also:
- Player can loot monster corpses (if monster had equipped items)
- Corpses block movement (can be walked through after N turns as they decay)
- Visual: dead entity sprite on tile

---

## Level Template Integration

Special dungeon features are placed via `level_templates.yaml`:

```yaml
level: 5
guaranteed_spawns:
  - type: chest_locked
    room: treasure_vault
  - type: sign
    position: [12, 8]
    message: "She waits at the end."
  - type: spike_trap
    position: [15, 10]
```

Testing levels 91-99 are specifically for testing these features:
- Level 91: Door/key testing
- Level 92: Secret room discovery
- Level 93: Trap placement and detection
- Level 94: Stair mechanics

---

## C# Port Checklist

- [ ] `TrapComponent` with type, DC, detection chance, effect
- [ ] Passive detection on tile entry (before effect fires)
- [ ] Active detection via Search action
- [ ] Disarm attempt (DEX check vs DC)
- [ ] All 8 trap types + their effects (needs status effects system first)
- [ ] `ChestEntity` with type (standard/trapped/locked/boss)
- [ ] Chest interaction (tap/walk-into)
- [ ] Locked chest + key item type
- [ ] Chest loot generation (using loot policy system)
- [ ] `SignEntity` with message + interaction
- [ ] `MuralComponent` on wall tiles + Search reveal
- [ ] Corpse entity (placed on monster death)
- [ ] Corpse decay timer
- [ ] YAML: trap definitions with DC/damage/effects
- [ ] Level template: guaranteed feature placement
- [ ] Testing scenarios for each trap type (identity tests)
