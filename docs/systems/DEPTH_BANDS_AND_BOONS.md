# Depth Bands and Boons

_Last verified: 2026-07-12 against commit 86b6f10_

**Sources:** `config/depth_boons.yaml`, `config/level_templates.yaml`, `src/Logic/Balance/PressureModel.cs`  
**Implementation status:** Depth bands fully implemented. Boon system implemented for bands 1–5. Boons awarded at the start of each new band.

---

## Depth Band Structure

The dungeon is divided into 5 bands of 5 floors each:

| Band | Depths | Theme |
|---|---|---|
| B1 | 1–5 | Introduction — gentle, gear-sparse, single monsters |
| B2 | 6–10 | Escalation — composition variety, more loot, first rings |
| B3 | 11–15 | Midgame — full loot density, rings available, higher ETP |
| B4 | 16–20 | Late game — tactical depth, gear optimization phase |
| B5 | 21–25 | Endgame — maximum monster density, full ring rate |

---

## Depth Boons

The player receives one boon when entering a new band (depths 1, 6, 11, 16, 21). Boons are permanent passive stat improvements.

| Band | Boon ID | Display Name | Effect |
|---|---|---|---|
| B1 (depth 1) | fortitude_10 | Fortitude | +10 max HP, heals 10 HP immediately |
| B2 (depth 6) | accuracy_1 | Keen Eye | +2 accuracy (to-hit bonus) |
| B3 (depth 11) | defense_1 | Iron Skin | +1 defense (reduces damage taken) |
| B4 (depth 16) | damage_1 | Cruel Blow | +1 minimum damage |
| B5 (depth 21) | resilience_5 | Resilience | +10 max HP, heals 10 HP immediately |

Boons are cumulative — by the time the player reaches B5, they have all 5 boons active simultaneously.

---

## Encounter Budget Scaling (ETP)

ETP (Encounter Threat Points) is the total monster value budget for a floor. The floor builder fills rooms with monsters until the budget is consumed.

| Band | ETP Max |
|---|---|
| B1 | 50 |
| B2 | 120 |
| B3 | 180 |
| B4 | 240 |
| B5 | 300 |

`allow_spike: false` means no single encounter can dominate the budget. The builder distributes monsters across multiple rooms.

---

## Loot Band Multipliers

See `LOOT_AND_IDENTIFICATION.md` for full breakdown. In summary, B1 is intentionally sparse (0.35× item density), ramping to 1.0× from B3 onwards.

---

## Pressure Model

The `PressureModel` system tracks whether the player's combat metrics (H_PM, H_MP, Death%) are within acceptable target bands per depth. This is a balance tooling concept — the scenario harness uses it to validate that monster difficulty stays within design targets as depth increases. Not player-visible.

Target bands are defined in `src/Logic/Balance/PressureModel.cs` and validated by the scenario runner in `tools/Harness`.

---

## Monster Depth Availability

Monster `min_depth` and `depth_weights` control when new species appear:

| Depth | New Spawners Unlock |
|---|---|
| 1 | orc, orc_brute (low weight) |
| 2 | skeleton, cave_spider, fire_beetle, slime |
| 3 | web_spider, orc_brute (increased weight), large_slime |
| 4 | troll |
| 5 | necromancer |
| 7 | plague_necromancer |
| 8 | giant_spider |
| 10 | zombie |
| 12 | greater_slime, cultist_blademaster |
| 13 | plague_zombie |
| 15 | wraith, troll_ancient |
| 18 | lich |
