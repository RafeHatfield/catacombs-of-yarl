# Systems Documentation Index

Developer reference for all implemented game systems. These documents describe what is built, not what players see — mechanics, exact values, implementation status.

| Document | Contents |
|---|---|
| [WEAPONS.md](WEAPONS.md) | All weapons, damage types, named weapons, enchantment |
| [ARMOUR.md](ARMOUR.md) | All armour pieces, slots, AC values, enchantment |
| [POTIONS.md](POTIONS.md) | All potions — healing, buff, debuff, dual-mode, throw mechanics |
| [SCROLLS_AND_WANDS.md](SCROLLS_AND_WANDS.md) | All scrolls and wands, spell system, charges, recharging, Wand of Portals |
| [RINGS.md](RINGS.md) | All rings — Phase 1 (implemented) vs Phase 2 (stubs), depth availability |
| [MONSTERS.md](MONSTERS.md) | All monsters — stats, AI types, factions, special abilities, depth gates |
| [STATUS_EFFECTS.md](STATUS_EFFECTS.md) | All status effects with exact durations, damage, and sources |
| [COMBAT.md](COMBAT.md) | Combat resolution, damage types, crits, speed/momentum system |
| [MAP_GENERATION_AND_PROPS.md](MAP_GENERATION_AND_PROPS.md) | Floor generation parameters, tile types, props catalogue, signposts, murals, chests |
| [LOOT_AND_IDENTIFICATION.md](LOOT_AND_IDENTIFICATION.md) | Loot categories, band multipliers, pity system, identification mechanics |
| [GROUND_HAZARDS.md](GROUND_HAZARDS.md) | Fire and poison gas hazards, decay formula, timing rules (note: no traps yet) |
| [DEPTH_BANDS_AND_BOONS.md](DEPTH_BANDS_AND_BOONS.md) | Band structure, boon awards, ETP budgets, monster unlock depths |

## Implementation Status Summary

**Fully implemented:**
All weapons, armour, potions, scrolls, wands (except stubs noted), 10 of 15 rings, all monsters, all status effects, combat system, map generation, props, loot system, identification system, ground hazards, depth bands and boons.

**Stubs / Partially Implemented:**
- Rings: 5 Phase 2 rings (resistance, clarity, invisibility, searching, wizardry, luck) — equippable but no effect
- `scroll_of_raise_dead` / `wand_of_raise_dead` — functional but requires a corpse; corpse system is live
- Item stacking — not implemented (each item is a separate entity)

**Not Yet Built:**
- Traps (ground hazards exist as a partial substitute)
- Rarity tiers (common/rare/legendary)
- Blessed/cursed items
- Hunger/food system
- Shop system
- Resistance system (fire/cold/poison immunity)
- Amulets
