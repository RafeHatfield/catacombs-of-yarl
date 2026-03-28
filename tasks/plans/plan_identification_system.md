# Plan: Identification System

Status: [ ] Not started
PoC reference: config/game_constants.yaml, components/item_functions.py

---

## What It Is

Items are generated with hidden identity. Player sees "Blue Potion" or "Strange Wand" until they identify it. Once identified in a run, all items of that type show their true name. Identification persists across runs (meta-progression) after first win.

## Item Types Subject to Identification

- **Potions** — healing, invisibility, speed, protection, confusion, teleport, slow, rage, shield, root, reflex, sunburst
- **Scrolls** — identify, enhance_weapon, lightning, fireball, dragon_fart, confusion, disarm, silence
- **Wands** — stored spell types with charges
- **Rings** — Ring of Strength, Dexterity, Constitution (all start unidentified)

Weapons and armor are ALWAYS identified by name (but not their enchantment level — that's a separate mechanic, e.g. "longsword" vs "+2 longsword").

## Identification Methods

1. **Use it** — drinking an unknown potion identifies it (you learn what it was, possibly after suffering the effect)
2. **Identify scroll** — explicitly identify any item in inventory
3. **Lore / shop** — not yet in scope
4. **Testing mode** — all items identified (configurable)

## Difficulty Tiers (from game_constants.yaml)

| Tier | Scrolls pre-ID | Potions pre-ID | Rings pre-ID | Wands pre-ID |
|------|---------------|----------------|--------------|--------------|
| Easy | 80% | 80% | 90% | 60% |
| Medium | 40% | 50% | 40% | 30% |
| Hard | 5% | 5% | 0% | 0% |

Default difficulty = Medium.

## Per-Run Alias System

Each run, each unidentified item type gets a random alias ("Bubbling Potion", "Crinkled Scroll"). The same item type always has the same alias within a run. Aliases shuffle each new run.

- Alias pool defined in YAML (colors for potions, adjectives for scrolls, materials for wands)
- Deterministic assignment from run seed

## Master Toggle

`identification_system_enabled: true` in game_constants.yaml. When false, all items show their true name from spawn. Useful for accessibility/testing.

## Meta-Progression (Post-Win)

- After first win: common items auto-identify
- Optionally: scrolls of identify become less necessary (the game gets "easier to read")
- YAML flag controls which categories persist

## Key Design Decisions

- Identification creates tension around resource use vs safety
- Dangerous potions (confusion, slow) are traps for the unwary
- Easy mode reducing unknown items is an accessibility dial, not a cheat
- Wands with unknown charges create a "do I risk it?" moment

## Implementation Notes

- `ItemEntity` needs `IsIdentified` flag and `Alias` string
- `ItemRegistry` (or equivalent) tracks per-run identified types
- Separate from `ItemType` definition (which always knows the true stats)
- Save/load must persist which types have been identified this run
- UI: item list shows alias if unidentified, true name if identified
- After identifying: broadcast "You realize this was a Potion of Healing!" message

## C# Port Checklist

- [ ] `IdentificationRegistry` — per-run state, which types are known
- [ ] `AliasPool` — YAML-driven random aliases per category
- [ ] `ItemEntity.IsIdentified` property
- [ ] Identification on use (potion drank = identified)
- [ ] Identify scroll targeting (pick item from inventory, reveal it)
- [ ] Difficulty tier seeding (pre-identified % from constants)
- [ ] UI display: alias vs true name
- [ ] Meta-progression hook (post-win persistence) — can defer to late development
