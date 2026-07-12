# Weapons

_Last verified: 2026-07-12 against commit 86b6f10_

**Source:** `config/entities.yaml` → `weapons:` section  
**Implementation status:** Fully implemented. Enchantment (+1/+1 via Scroll of Enchant Weapon) is live.

---

## Weapon Stats

Most weapons occupy the `main_hand` slot. Two-handed weapons **are** implemented: items flagged `two_handed: true` in `config/entities.yaml` (e.g. shortbow, longbow) clear the off-hand slot when equipped, so bow + shield is not allowed (`src/Logic/Combat/Equippable.cs` → `TwoHanded`).

| Item ID | Name | Damage | To-Hit | Damage Type | Material | Band |
|---|---|---|---|---|---|---|
| `dagger` | Dagger | 1–4 | +1 | Piercing | Metal | B1–B3 |
| `club` | Club | 1–6 | +0 | Bludgeoning | Wood | B1–B3 |
| `mace` | Mace | 1–6 | +0 | Bludgeoning | Metal | B1–B3 |
| `shortsword` | Shortsword | 1–6 | +0 | Slashing | Metal | B1–B3 |
| `rapier` | Rapier | 1–8 | +1 | Piercing | Metal | B1–B4 |
| `spear` | Spear | 1–8 | +0 | Piercing | Metal | B1–B4 |
| `longsword` | Longsword | 1–8 | +0 | Slashing | Metal | B1–B4 |
| `battleaxe` | Battle Axe | 1–10 | −1 | Slashing | Metal | B2–B5 |
| `greatsword` | Greatsword | 2–12 | −1 | Slashing | Metal | B2–B5 |

## Named / Special Weapons

| Item ID | Name | Damage | To-Hit | Special | Band |
|---|---|---|---|---|---|
| `quickfang_dagger` | Quickfang Dagger | 1–4 | +1 | +18% speed bonus | B2–B5 |
| `keen_dagger` | Keen Dagger | 1–4 | +1 | Crit threshold 19 (normal: 20) | B2–B5 |
| `vicious_shortsword` | Vicious Shortsword | 2–7 | +0 | Elevated base damage | B2–B5 |
| `fine_longsword` | Fine Longsword | 1–8 | +1 | +to-hit over base longsword | B2–B5 |
| `masterwork_longsword` | Masterwork Longsword | 2–9 | +1 | Best base longsword variant | B3–B5 |

## Damage Types

Three types active, each with monster resistance/vulnerability interactions:

- **Piercing** — resisted by nothing currently, cave spider / giant spider attacks use this classification
- **Slashing** — standard melee type
- **Bludgeoning** — effective vs skeletons (vulnerability); zombies resist it in reverse (they resist piercing, not bludgeoning)

Resistance/vulnerability is defined per-monster in `config/entities.yaml` via `damage_resistance` and `damage_vulnerability` fields.

## Enchantment

`scroll_of_enchant_weapon` applies `enhance_weapon` spell. Effect: +1 `to_hit_bonus` and +1 `damage_min` to the currently equipped main_hand weapon. Stacks — no cap in the current implementation. Tracks as a persistent modifier on the `WeaponComponent`.

## Disarm

The `DisarmedEffect` (3 turns, applied by `scroll_of_disarm` / `wand_of_disarm`) forces the target to fight barehanded. Barehanded stats: 1–2 damage, standard accuracy.

## Speed Bonus from Weapons

`quickfang_dagger` grants `speed_bonus: 0.18` via `SpeedBonusTracker.EquipmentRatio`. Combined with ring speed bonuses at equip time. See `COMBAT.md` for the speed/momentum system.

## Floor Item Pool

Weapons appear in the general floor item pool (`floor_item_pool` in `entities.yaml`) with depth gates:
- B1 (depth 1–15): dagger, club, mace, shortsword  
- B2 (depth 2–20): rapier, spear, longsword  
- B3+ (depth 3–25): battleaxe, greatsword  
- Named weapons: B2+ with reduced weights (rarer)

Named weapons also appear in the loot category pool (`loot_tags.yaml`, category `upgrade_weapon`).
