# Potions

_Last verified: 2026-07-12 against commit 86b6f10_

**Source:** `config/entities.yaml` → `consumables:` section  
**Implementation status:** All potions fully implemented. Throw mechanics live for dual-mode potions.

---

## Mechanics Overview

Potions route through `SpellResolver` just like scrolls and wands. The key flag `is_potion: true` bypasses the `SilencedEffect` gate — potions work even when silenced.

**Drink-only potions:** Tapping the potion immediately applies the drink effect to self.  
**Dual-mode potions (throw_spell_id set):** Tapping enters targeting mode. Tapping self drinks; tapping an enemy/tile throws. The throw effect is usually the enemy-targeting version of the same status.  
**Throw-only potions (fire_potion):** Always enters targeting mode; there is no useful drink effect.

Potions are consumed on use (single-use, unlike wands). They respect the identification system — unidentified potions show a colour/description until used.

---

## Healing Potions

| Item ID | Name | Effect | Notes |
|---|---|---|---|
| `healing_potion` | Healing Potion | Heals 40 HP | Drink-only. B1+. Most common consumable. |
| `potion_of_regeneration` | Potion of Regeneration | Regeneration effect (2 HP/turn, 20 turns) | Drink-only. B2+ (depth 6+). Slow heal over time. |
| `antidote_potion` | Antidote Potion | Cures plague | Drink-only. B3+ (depth 11+). Only way to cure Plague status from Plague Necromancer/Zombie hits. |

---

## Buff Potions (Drink-Only)

Safe to drink unidentified. No throw effect — tapping immediately drinks.

| Item ID | Name | Effect | Duration |
|---|---|---|---|
| `potion_of_speed` | Potion of Speed | Haste (speed bonus +50%, extra actions) | 20 turns |
| `potion_of_protection` | Potion of Protection | ProtectionEffect (+3 AC) | 50 turns |
| `potion_of_invisibility` | Potion of Invisibility | InvisibilityEffect (monsters can't target you) | 30 turns |
| `potion_of_heroism` | Potion of Heroism | HeroismEffect (+3 to-hit, +3 damage) | 30 turns |

---

## Debuff Potions (Dual-Mode)

**Dangerous if drunk unidentified.** Tapping these enters targeting mode — tap enemy to throw (useful), tap self to drink (harmful). The throw spell affects a single target enemy.

| Item ID | Name | Drink Effect | Throw Effect | Duration |
|---|---|---|---|---|
| `potion_of_weakness` | Potion of Weakness | WeaknessEffect on self (−power to damage) | WeaknessEffect on target | 30 turns |
| `potion_of_slowness` | Potion of Slowness | SluggishEffect on self (half speed) | SluggishEffect on target | 20 turns |
| `potion_of_blindness` | Potion of Blindness | BlindedEffect on self (−4 accuracy) | BlindedEffect on target | 15 turns |
| `potion_of_paralysis` | Potion of Paralysis | ImmobilizedEffect on self (3–5 turns, random) | ImmobilizedEffect on target | 3–5 turns |
| `tar_potion` | Tar Potion | SlowedEffect on self (half speed, different from sluggish) | SlowedEffect on target | 10 turns |

Throw range: 10 tiles for all dual-mode potions.

---

## Special / Dual-Effect Potions

These have a useful drink effect AND a useful throw effect (different effects, not self-harm vs enemy-harm).

| Item ID | Name | Drink Effect | Throw Effect | Duration |
|---|---|---|---|---|
| `root_potion` | Root Potion | BarkskinEffect on self (+3 AC, "tough bark skin") | EntangledEffect on target (rooted) | Drink: 10t / Throw: 3t |
| `sunburst_potion` | Sunburst Potion | FocusedEffect on self (+3 accuracy) | BlindedEffect on target | Drink: 8t / Throw: 3t |

---

## Throwable / Offensive Potions

| Item ID | Name | Effect | Notes |
|---|---|---|---|
| `fire_potion` | Fire Potion | BurningEffect on target (3 damage/turn, 4 turns) | Throw-only. No useful drink. Single target, range 10. |

---

## Depth / Availability

| Band | Depths | Potions Available |
|---|---|---|
| B1 | 1–5 | healing_potion, potion_of_protection |
| B2 | 6–10 | + speed, regeneration, invisibility, heroism, all debuff/special/fire potions |
| B3 | 11–15 | + antidote_potion |

---

## Identification System Integration

Potions appear with randomized colour descriptions until identified (per difficulty setting). Using a potion identifies it for the rest of the run. `scroll_of_identify` can identify them without consuming. See `LOOT_AND_IDENTIFICATION.md`.
