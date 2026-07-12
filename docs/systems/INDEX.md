# Systems Documentation Index

_Last verified: 2026-07-12 against commit 86b6f10_

Developer reference for all implemented game systems. These documents describe what is built, not what players see — mechanics, exact values, implementation status.

| Document | Contents |
|---|---|
| [WEAPONS.md](WEAPONS.md) | All weapons, damage types, named weapons, enchantment |
| [ARMOUR.md](ARMOUR.md) | All armour pieces, slots, AC values, enchantment |
| [POTIONS.md](POTIONS.md) | All potions — healing, buff, debuff, dual-mode, throw mechanics |
| [SCROLLS_AND_WANDS.md](SCROLLS_AND_WANDS.md) | All scrolls and wands, spell system, charges, recharging, Wand of Portals |
| [RINGS.md](RINGS.md) | All 16 rings — 10 functional vs 6 no-op stubs, depth availability |
| [MONSTERS.md](MONSTERS.md) | All monsters — stats, AI types, factions, special abilities, depth gates |
| [STATUS_EFFECTS.md](STATUS_EFFECTS.md) | All status effects with exact durations, damage, and sources |
| [COMBAT.md](COMBAT.md) | Combat resolution, damage types, crits, speed/momentum system |
| [MAP_GENERATION_AND_PROPS.md](MAP_GENERATION_AND_PROPS.md) | Floor generation parameters, tile types, props catalogue, signposts, murals, chests |
| [LOOT_AND_IDENTIFICATION.md](LOOT_AND_IDENTIFICATION.md) | Loot categories, band multipliers, pity system, identification mechanics |
| [GROUND_HAZARDS.md](GROUND_HAZARDS.md) | Fire and poison gas hazards, decay formula, timing rules (distinct from placed traps — see below) |
| [DEPTH_BANDS_AND_BOONS.md](DEPTH_BANDS_AND_BOONS.md) | Band structure, boon awards, ETP budgets, monster unlock depths |

## Implementation Status Summary

_Regenerated from code at commit 86b6f10 (file references are the evidence)._

**Fully implemented:**
- Weapons — all, including two-handed weapons/bows that clear the off-hand slot (`src/Logic/Combat/Equippable.cs`, `config/entities.yaml` `two_handed`)
- Armour, potions, scrolls, wands (except the corpse-gated raise-dead spells noted below)
- Monsters, status effects, combat system (crits, speed/momentum), map generation, props, room archetypes, loot system, identification system, depth bands and boons
- Ground hazards (fire / poison gas)
- **Traps** — 9 types in `config/floor_traps.yaml` (spike, web, gas, fire, alarm_plate, teleport, root, hole, acid), placed by the floor generator via `FloorTrapRegistry` (`src/Logic/Core/DungeonFloorBuilder.cs`), triggered through `src/Logic/Combat/TrapActionResolver.cs` from `TurnController`
- **Damage-type resistance / vulnerability** — `src/Logic/Combat/DamageModifiers.cs` (resistance halves, vulnerability doubles), wired to monsters via `damage_resistance` / `damage_vulnerability` in `config/entities.yaml` and applied in `src/Logic/Combat/CombatResolver.cs`
- **Item stacking** — implemented for consumables (`Consumable.StackSize`, decrements on use) and ammo (`ItemDefinition.stack_size`, e.g. fire_arrow=10); equipment is non-stackable by nature
- Rings — 10 of 16 functional (see RINGS.md)

**Stubs / Partially Implemented:**
- Rings: 6 no-op stubs — resistance, clarity, invisibility, searching, wizardry, luck. Equip/unequip works but the effect is a no-op (their `RingEffectKind` is not handled in `TurnController`). Note: `ring_of_resistance` is a stub even though the resistance combat mechanic above is live — the ring simply doesn't apply it yet.
- `scroll_of_raise_dead` / `wand_of_raise_dead` — functional but requires a corpse; corpse system is live (`src/Logic/AI/NecromancerAI.cs`, `LichAI.cs`)
- `armor_type` (light/medium) — stored on items but not mechanically differentiated; only AC bonus matters (`src/Logic/Combat/Equippable.cs`)

**Not Yet Built:** (verified absent — no code or config)
- Rarity tiers (common/rare/legendary) — no enum, field, or stub in code
- Blessed/cursed items
- Hunger/food system
- Shop system
- Amulets — the Neck/amulet equip slot exists but there are no amulet items
- Return-to-previous-floor ascent — a stair-up tile is placed but ascending back up is not wired
