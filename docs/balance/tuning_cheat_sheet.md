# YARL Balance Tuning Cheat Sheet

> **For the full operational workflow — commands, drift thresholds, how to diagnose a WARN/FAIL — see [`BALANCE_PIPELINE_PLAYBOOK.md`](BALANCE_PIPELINE_PLAYBOOK.md).**

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

CI runs automatically on every PR (`.github/workflows/balance.yml`):

```bash
dotnet run --project tools/Harness -- --suite   # blocks PR if FAIL
dotnet run --project tools/Harness -- --etp-sanity --strict
```

Treat failures as:
- **Hard block** for `--suite` FAIL (balance regression).
- **Hard block** for ETP `--etp-sanity --strict` OVER in normal rooms.

See `BALANCE_PIPELINE_PLAYBOOK.md` for drift thresholds and how to investigate.

---

## J. When in doubt

```bash
# Quick check (2 min)
dotnet run --project tools/Harness -- --suite --fast

# Diagnose a specific depth
dotnet run --project tools/Harness -- --suite --out-dir /tmp/run
dotnet run --project tools/Harness -- --depth-report --in /tmp/run

# Check encounter budgets
dotnet run --project tools/Harness -- --etp-sanity --verbose
```

See `BALANCE_PIPELINE_PLAYBOOK.md` for full command reference and interpretation guide.
