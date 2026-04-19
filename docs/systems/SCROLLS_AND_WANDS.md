# Scrolls and Wands

**Source:** `config/entities.yaml` → `scrolls:` and `wands:` sections  
**Implementation status:** All listed scrolls and wands fully implemented.  
`scroll_of_raise_dead` / `wand_of_raise_dead` require a corpse within range; effect works when a corpse is present.

---

## Shared Spell System

Scrolls and wands both dispatch through `SpellResolver`. The `spell_id` field routes to the matching handler. Scrolls are single-use consumables; wands have a charge count.

**Targeting modes:**
- `self` — affects caster, no targeting UI
- `auto_closest` — fires at nearest visible enemy automatically
- `aoe_self` — affects all entities within `radius` tiles of caster
- `single_target` — player aims at one visible enemy within `range`
- `location` — player taps a tile; effect lands there
- `portal` — 3-step wand casting (Wand of Portals only)

Scrolls fail silently if `SilencedEffect` is active. Potions bypass silence — wands do not.

---

## Scrolls

Scrolls are single-use. On use, they identify and are consumed.

### Utility / Exploration

| Item ID | Name | Targeting | Effect |
|---|---|---|---|
| `scroll_of_identify` | Scroll of Identify | Self | Identifies 1–3 random unidentified items in inventory |
| `scroll_of_light` | Scroll of Light | Self | Expands FOV radius for several turns (reveals hidden areas) |
| `scroll_of_detect_monsters` | Scroll of Detect Monsters | Self | DetectMonstersEffect: all monsters shown on map for 20 turns |
| `scroll_of_magic_mapping` | Scroll of Magic Mapping | Self | Reveals entire floor layout (all tiles, not entities) |

### Weapon / Armor Enhancement

| Item ID | Name | Targeting | Effect |
|---|---|---|---|
| `scroll_of_enchant_weapon` | Scroll of Enchant Weapon | Self | +1 to-hit and +1 damage_min to equipped weapon |
| `scroll_of_enchant_armor` | Scroll of Enchant Armor | Self | +1 AC to best equipped armour piece |

### Defensive

| Item ID | Name | Targeting | Effect | Duration |
|---|---|---|---|---|
| `scroll_of_shield` | Scroll of Shield | Self | ShieldEffect: +3 AC barrier | 10 turns |
| `scroll_of_haste` | Scroll of Haste | Self | SpeedEffect: +50% extra actions | 30 turns |
| `scroll_of_invisibility` | Scroll of Invisibility | Self | InvisibilityEffect: enemies cannot target you | 30 turns |

### Offensive — AoE / Location

| Item ID | Name | Targeting | Damage / Effect |
|---|---|---|---|
| `scroll_of_lightning` | Scroll of Lightning | Auto-closest (range 5) | 40 damage to nearest visible enemy |
| `scroll_of_earthquake` | Scroll of Earthquake | AoE-self (radius 3) | 20 damage to all visible enemies in radius |
| `scroll_of_fear` | Scroll of Fear | AoE-self (radius 10) | FearEffect (15 turns) on all enemies in radius — they flee |
| `scroll_of_fireball` | Scroll of Fireball | Location (range 10, radius 3) | 25 direct damage + 3t burning ground hazard (base 3 dmg, 3 turns) |
| `scroll_of_dragon_fart` | Scroll of Dragon Fart | Location (range 8) | Dragon fart cloud — ConfusedEffect on targets in area (3 turns) + lingering gas (6 dmg, 5 turns decay) |

### Offensive — Single Target

| Item ID | Name | Targeting | Effect | Duration |
|---|---|---|---|---|
| `scroll_of_confusion` | Scroll of Confusion | Single (range 8) | ConfusedEffect: random movement and attacks | 10 turns |
| `scroll_of_slow` | Scroll of Slow | Single (range 8) | SlowedEffect: acts every other turn | 10 turns |
| `scroll_of_glue` | Scroll of Glue | Single (range 8) | EntangledEffect: rooted in place | 5 turns |
| `scroll_of_rage` | Scroll of Rage | Single (range 8) | EnragedEffect: 2× damage, attacks anyone | 8 turns |
| `scroll_of_yo_mama` | Scroll of Yo Mama | Single (range 10) | AggravatedEffect: permanently fixates on player | Permanent |
| `scroll_of_disarm` | Scroll of Disarm | Single (range 8) | DisarmedEffect: fights barehanded | 3 turns |
| `scroll_of_plague` | Scroll of Plague | Single (range 8) | PlagueEffect: 1 damage/turn | 20 turns |
| `scroll_of_silence` | Scroll of Silence | Single (range 8) | SilencedEffect: cannot use scrolls/wands | 3 turns |
| `scroll_of_aggravation` | Scroll of Unreasonable Aggravation | Single (range 10) | AggravatedEffect: target attacks its own faction | Permanent |

### Movement / Teleport

| Item ID | Name | Targeting | Effect |
|---|---|---|---|
| `scroll_of_teleport` | Scroll of Teleport | Location (range 20) | Moves player to chosen tile; 10% misfire (random tile) |
| `scroll_of_blink` | Scroll of Blink | Location (range 5) | Short teleport, no misfire |

### Necromancy

| Item ID | Name | Targeting | Effect |
|---|---|---|---|
| `scroll_of_raise_dead` | Scroll of Raise Dead | Location (range 5) | Raises a corpse at target tile as a temporary ally |

---

## Wands

Wands have limited charges (randomly chosen from [min_charges, max_charges] at spawn). Each charge is a use. Wands are reusable until depleted. The charge count shows when inspected but is hidden when unidentified.

### Recharging

Each wand has a `recharge_scroll` field naming a scroll `spell_id`. When the player picks up a scroll whose `spell_id` matches the wand's `recharge_scroll` **and** the wand has room below `charge_cap`, the scroll is consumed and the wand gains 1 charge automatically.

Example: Scroll of Lightning recharges the Wand of Lightning (recharge_scroll: "lightning").

### Wand of Portals (Special Case)

The `wand_of_portals` is **infinite** (no charge consumption) and uses the `portal` targeting mode, a 3-step state machine:
1. Cast 1: Places portal entrance at player's tile
2. Cast 2: Player aims at a target tile; places portal exit there
3. Cast 3: Removes both portals and resets the wand

The wand does not appear in floor loot — every player starts with one in their backpack (`DungeonFloorBuilder.CreateDefaultPlayer`).

### Wand Table

| Item ID | Name | Spell | Targeting | Charges | Cap | Recharge Scroll |
|---|---|---|---|---|---|---|
| `wand_of_lightning` | Wand of Lightning | lightning | auto_closest (r5) | 3–6 | 10 | lightning |
| `wand_of_portals` | Wand of Portals | portal | portal | ∞ | — | — |
| `wand_of_confusion` | Wand of Confusion | confusion | single (r8) | 2–5 | 10 | confusion |
| `wand_of_slow` | Wand of Slow | slow | single (r8) | 2–5 | 10 | slow |
| `wand_of_glue` | Wand of Glue | glue | single (r8) | 3–6 | 10 | glue |
| `wand_of_rage` | Wand of Rage | rage | single (r8) | 2–4 | 8 | rage |
| `wand_of_yo_mama` | Wand of Yo Mama | yo_mama | single (r10) | 2–4 | 8 | yo_mama |
| `wand_of_invisibility` | Wand of Invisibility | invisibility | self (30t) | 2–4 | 8 | invisibility |
| `wand_of_haste` | Wand of Haste | haste | self (30t) | 2–4 | 8 | haste |
| `wand_of_fear` | Wand of Fear | fear | aoe-self (r10, 15t) | 2–5 | 10 | fear |
| `wand_of_silence` | Wand of Silence | silence | single (r8, 3t) | 2–5 | 10 | silence |
| `wand_of_raise_dead` | Wand of Raise Dead | raise_dead | location (r5) | 1–3 | 6 | raise_dead |
| `wand_of_fireball` | Wand of Fireball | fireball | location (r10, aoe 3) | 2–4 | 8 | fireball |
| `wand_of_teleportation` | Wand of Teleportation | teleport | location (r20, 10% misfire) | 2–4 | 8 | teleport |
| `wand_of_dragon_farts` | Wand of Dragon Farts | dragon_fart | location (r8) | 2–4 | 6 | dragon_fart |

### Wands Not in Floor Pool

`wand_of_portals` is the only wand excluded from floor loot (player starts with it). All others appear in `floor_item_pool` starting depth 2–6 with lower weights than scrolls.

---

## Loot Distribution

Scrolls appear from depth 1 (common at weight 10–30). Wands appear from depth 2–6 at lower weights (3–8), making them notably rarer than scrolls. Both categories use the `loot_tags.yaml` system for band-based category selection in addition to the floor item pool.

See `LOOT_AND_IDENTIFICATION.md` for band multipliers and category weights.
