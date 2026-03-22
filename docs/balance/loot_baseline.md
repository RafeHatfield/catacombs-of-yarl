# Loot Distribution Baseline

## Balance Targets

| Band | Depths | Items/room | Healing/room | Rare/room |
|------|--------|-----------|--------------|-----------|
| B1 | 1-5 | 5-8 | 0.7-1.2 | 0-0.1 |
| B2 | 6-10 | 6-9 | 0.8-1.5 | 0.1-0.3 |
| B3 | 11-15 | 8-10 | 0.5-1.0 | increasing |
| B4 | 16-20 | 8-10 | 0.5-1.0 | increasing |
| B5 | 21-25 | 8-10 | 0.5-1.0 | ~0.5 |

## Band Multipliers Applied

**Item density:**
| Band | Multiplier |
|------|-----------|
| B1 | 0.35 |
| B2 | 0.45 |
| B3-B5 | 1.0 |

**Healing weight:**
| Band | Multiplier |
|------|-----------|
| B1 | 0.25 |
| B2 | 0.35 |
| B3 | 1.0 |
| B4-B5 | 1.1 |

**Rare item weight:**
| Band | Multiplier |
|------|-----------|
| B1 | 0.05 |
| B2 | 0.15 |
| B3 | 0.5 |
| B4 | 0.8 |
| B5 | 1.0 |

## Baseline Results (2025-11-29)

### Normal Mode Baseline

| Band | Test Depth | Items/room | Healing/room | Rare/room |
|------|-----------|-----------|--------------|-----------|
| B1 | 3 | 0.41 | 0.17 | 0 |
| B2 | 8 | 0.72 | 0.21 | 0 |
| B3 | 13 | 1.35 | 0.29 | 0.15 |
| B4 | 18 | 1.09 | 0.32 | 0.15 |
| B5 | 23 | 1.06 | 0.28 | 0.12 |

## Ring Band Restrictions

All rings now start at B2 or later:

- **B2+ (depth 6+):** protection, regeneration, strength, dexterity, searching, clarity
- **B3+ (depth 11+):** constitution, resistance, might, free_action, luck
- **B4+ (depth 16+):** teleportation, invisibility, wizardry, speed

## Pity System

Pity remains unchanged and acts as a safety net:

- B1: Triggers after 6 rooms without healing
- B2: Triggers after 5 rooms without healing
- B3+: Triggers after 4 rooms without healing

With the healing multiplier reducing natural healing rates, pity will occasionally
trigger to prevent bad-luck streaks. This is intentional.

## Future Improvements

1. **Testing templates:** Consider reducing guaranteed spawns in early testing levels
2. **Healing tuning:** May need to increase healing multiplier if pity triggers too often
3. **Rare progression:** Monitor ring drop rates in actual gameplay
