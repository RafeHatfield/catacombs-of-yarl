# Armour

**Source:** `config/entities.yaml` → `armor:` section  
**Implementation status:** Fully implemented. Enchantment (+1 AC via Scroll of Enchant Armor) is live.

---

## Armour Pieces

Four equipment slots: `head`, `chest`, `off_hand`, `feet`. No `legs` slot currently.

| Item ID | Name | Slot | AC Bonus | Type | Band |
|---|---|---|---|---|---|
| `leather_helmet` | Leather Helmet | head | +1 | Light | B1–B3 |
| `leather_armor` | Leather Armor | chest | +2 | Light | B1–B3 |
| `studded_leather` | Studded Leather | chest | +3 | Light | B2–B5 |
| `chain_mail` | Chain Mail | chest | +4 | Medium | B2–B5 |
| `scale_mail` | Scale Mail | chest | +5 | Medium | B3–B5 |
| `shield` | Shield | off_hand | +2 | Light | B1–B3 |
| `leather_boots` | Leather Boots | feet | +1 | Light | B1–B3 |

## Armor Types

`armor_type` field is defined (`light`, `medium`) but not yet mechanically differentiated. Reserved for a future system (e.g., encumbrance, stealth penalty). Currently only AC bonus matters.

## Enchantment

`scroll_of_enchant_armor` applies `enhance_armor` spell. Effect: +1 `armor_class_bonus` to the best equipped armour piece (chest slot preferred if equipped, otherwise highest-AC equipped item). Stacks with no cap.

## Monster Drops

Orcs spawn with armour via their equipment pool:
- `chest`: leather_armor (weight 100, 50% spawn chance)

Other monsters do not spawn with armour currently.

## Floor Item Pool

Armour appears in `floor_item_pool` with depth gates:
- B1 (depth 1–15): leather_armor (w30), shield (w25), leather_helmet (w20), leather_boots (w20)
- B2+ (depth 2): studded_leather (w20)
- B3+ (depth 3): chain_mail (w15), scale_mail (w10)

Items with `max_depth` set age out of the pool at higher depths, making early armour (leather) progressively rarer as the dungeon deepens.

## Notes

- No rings with armour-modifying effects currently. Ring of Protection gives flat AC bonus via `BaseDefense` stat, separate from armour AC.
- No cursed/blessed armour system.
- Armour types (`light`/`medium`) are defined but the system awaiting heavy armour and potential movement restrictions.
