# Loot and Identification

_Last verified: 2026-07-12 against commit 86b6f10_

**Sources:** `config/loot_tags.yaml`, `config/loot_policy.yaml`, `config/entities.yaml` → `floor_item_pool:`, `src/Logic/Content/LootTagRegistry.cs`, `src/Logic/Content/IdentificationRegistry.cs`  
**Implementation status:** Both systems fully implemented.

---

## Identification System

### Overview

Unidentified items show a randomized appearance instead of their real name. Appearances are shuffled once at game start and persist for the entire run. Identifying an item reveals its true name to all copies — finding a second "red potion" when the first was identified as Healing Potion shows it already identified.

### Identification Methods

1. **Use the item** — using a scroll or potion identifies it immediately (even if the effect was harmful)
2. **Scroll of Identify** — identifies 1–3 randomly selected unidentified items in inventory without consuming them
3. **Pre-identification** — some items start identified based on difficulty setting (see below)

### Difficulty Settings

Controlled by `difficulty` field in `game_settings.yaml` (easy/medium/hard):

| Category | Easy | Medium | Hard |
|---|---|---|---|
| Potions | ~80–90% pre-IDed | ~30–50% | ~0–5% |
| Scrolls | ~80–90% pre-IDed | ~30–50% | ~0–5% |
| Rings | ~90% pre-IDed | ~40% | 0% |
| Wands | ~75% pre-IDed | ~30% | 0% |

### Item Categories for Identification

- **Potions** and **Scrolls**: Random appearance strings (colours, labels) shuffled per run
- **Rings**: "ring of [material]" (gold ring, silver ring, etc.)
- **Wands**: "smooth wand", "knobbly stick", etc.
- Weapons and armour are always identified (they're tangible objects the player can examine)

---

## Loot Generation — Two Systems

Items appear via two independent systems that run together:

### System 1: Floor Item Pool

The `floor_item_pool` in `entities.yaml` is a flat weighted list. Every room attempts to spawn items; the pool filters by depth (`min_depth`, `max_depth`) then does weighted random selection.

This pool handles all item types: weapons, armour, scrolls, wands, potions, rings. It's the simpler of the two systems — just depth-filtered weights.

### System 2: Loot Category System (loot_tags.yaml)

The category system adds structured category-level probability. It selects a *category* first (healing, defensive, panic, offensive, utility, upgrade_weapon, upgrade_armor, rare) then picks an item within that category.

**Band multipliers** adjust effective weights per category per band:

| Band | Depths | Item Density | Healing Weight | Rare Weight |
|---|---|---|---|---|
| B1 | 1–5 | 0.35× | 0.25× | 0.05× |
| B2 | 6–10 | 0.45× | 0.35× | 0.15× |
| B3 | 11–15 | 1.0× | 1.0× | 0.50× |
| B4 | 16–20 | 1.0× | 1.1× | 0.80× |
| B5 | 21–25 | 1.0× | 1.1× | 1.0× |

### Pity System

If the player goes too many rooms without a healing item, a healing item is guaranteed on the next room's spawn. Thresholds by band:
- B1: every 6 rooms
- B2: every 5 rooms
- B3+: every 4 rooms

---

## Category Weights (loot_tags.yaml)

Items within each category have relative weights. Higher weight = more likely when that category is chosen.

### Healing Category
| Item | Weight | Bands |
|---|---|---|
| healing_potion | 10.0 | B1–B5 |
| potion_of_regeneration | 3.0 | B2–B5 |
| antidote_potion | 2.0 | B3–B5 |

### Defensive Category
| Item | Weight | Bands |
|---|---|---|
| potion_of_protection | 4.0 | B1–B5 |
| scroll_of_shield | 4.0 | B1–B5 |

### Panic Category (escape/evasion)
| Item | Weight | Bands |
|---|---|---|
| scroll_of_teleport | 5.0 | B1–B5 |
| scroll_of_blink | 4.0 | B1–B5 |
| scroll_of_haste | 4.0 | B1–B5 |
| scroll_of_invisibility | 3.0 | B2–B5 |
| potion_of_speed | 2.5 | B2–B5 |
| potion_of_invisibility | 2.5 | B2–B5 |
| potion_of_heroism | 2.0 | B2–B5 |
| wand_of_invisibility | 1.5 | B2–B5 |
| wand_of_haste | 1.5 | B2–B5 |
| wand_of_teleportation | 1.5 | B2–B5 |

### Offensive Category (damage)
Scrolls: lightning (5.0), fear (5.0), earthquake (3.0), rage (3.0), yo_mama (2.5), dragon_fart (2.5), fireball (5.0 at B3+), raise_dead (2.0), plague (1.5 at B4+)  
Wands: lightning (2.0), fireball (2.0), fear (1.5), rage (1.0), yo_mama (1.0), dragon_farts (1.0), raise_dead (1.5)  
Potions: fire_potion (2.0), sunburst_potion (1.5)

### Utility Category
Scrolls: identify (4.0), light (3.0), detect_monsters (3.0), magic_mapping (2.5), confusion (5.0), slow (4.0), glue (4.0), disarm (3.0), silence (2.5), aggravation (1.5 at B3+)  
Wands: confusion (1.5), slow (1.5), glue (1.5), silence (1.5)  
Potions (debuffs, throw at enemies): weakness (2.5), slowness (2.5), blindness (2.0), paralysis (1.5), tar (2.0), root (1.5)

### Upgrade Weapon Category
Scroll of Enchant Weapon (3.0) + all weapons with weights (see `WEAPONS.md`)

### Upgrade Armor Category
Scroll of Enchant Armor (3.0) + all armour pieces with weights (see `ARMOUR.md`)

### Rare Category (Rings)
All rings, weights 0.3–0.6, band-gated. See `RINGS.md` for band availability.

---

## Key Balance Numbers (Observed)

From baseline harness runs:

| Band | Test Depth | Items/room | Healing/room | Rare/room |
|---|---|---|---|---|
| B1 | 3 | 0.41 | 0.17 | 0 |
| B2 | 8 | 0.72 | 0.21 | 0 |
| B3 | 13 | 1.35 | 0.29 | 0.15 |
| B4 | 18 | 1.09 | 0.32 | 0.15 |
| B5 | 23 | 1.06 | 0.28 | 0.12 |

Target bands: B1 5–8 items/room (not yet met — early game is intentionally lean), B3+ 8–10 items/room.

---

## Deferred Systems

- **Rarity tiers** (common/uncommon/rare/legendary) — not built. No rarity enum, field, or stub exists in code or config (verified against `src/Logic` and `config/`).
- **Pity system for weapons/armour** — PoC had separate pity tracking for gear categories; C# version has healing pity only.
- **Item stacking** — *implemented* for consumables (`Consumable.StackSize`, decrements on use) and ammo (`ItemDefinition.stack_size`). Equipment remains one-entity-per-item by nature. (This "Deferred Systems" entry is retained only to note that general/arbitrary stacking beyond consumables+ammo is not a goal.)
