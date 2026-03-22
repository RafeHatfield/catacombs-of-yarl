# YARL Balance Tuning Cheat Sheet

## A. Rooms feel too spiky in early game

1. Lower ETP for the main offenders.
2. Reduce their spawn chance or delay them to a later band.
3. Optionally tighten B1/B2 budgets in ETP config.
4. Run ETP sanity harness in strict mode.

Aim for:
- Normal rooms: mostly OK.
- Only a few UNDER per band.
- No OVER in normal rooms.

---

## B. Mid/late game feels too flat

1. Slightly increase ETP values for mid-tier monsters.
2. Widen upper budgets for B3-B5 in ETP config.
3. Consider increasing elite-spawn chance in appropriate bands.

Run ETP sanity harness in strict mode.

---

## C. Loot feels too dense

Lower the per-band density multiplier:

| Band | Density Multiplier |
|------|-------------------|
| B1 | 0.35 |
| B2 | 0.45 |
| B3-B5 | 1.0 |

Re-run loot sanity harness. Target: ~0.5-1.5 items/room.

---

## D. Too many / too few healing items

Adjust the healing band multiplier.

- Early bands: use low multipliers to prevent floods.
- Late bands: increase slightly to avoid starvation.

---

## E. Rings appear too early

Shift ring `band_min` upward.

Recommended:
- Common rings -> B2-B3
- Uncommon rings -> B3
- Exotic rings -> B4-B5

---

## F. Pity firing too often

1. Increase pity thresholds.
2. Or increase natural drop rates for categories that fire too often.

Healthy target: **5-15%** pity triggers per category.

---

## G. Removing overpowered drops in early bands

1. Raise `band_min` for those items.
2. Reduce their base weights.

---

## H. Adding more guaranteed spawns

- Add carefully to avoid distorting early-game difficulty.
- Mark rooms as `allow_spike: true` or `role: treasure/miniboss/boss` when appropriate.
- Avoid guaranteed spawns in B1 unless intentional.

---

## I. CI Integration

Run in CI:
- ETP sanity harness (strict mode)
- Loot sanity harness (normal mode)

Treat failures as:
- **Hard errors** for ETP OVER in normal rooms.
- **Warnings** for loot drift.

This prevents silent balance regression.

---

## J. When in doubt

Re-run both harnesses:

### ETP Sanity
- Verifies encounter difficulty curve.
- Flags spikes, invalid rooms, band errors.

### Loot Sanity
- Verifies item pacing.
- Checks pity frequency.
- Finds category droughts or floods.

Together, these harnesses catch 90% of issues before playtesting.
