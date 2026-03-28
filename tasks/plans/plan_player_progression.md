# Plan: Player Progression (XP, Leveling, Depth Boons)

Status: [ ] Not started
PoC reference: components/level.py, balance/depth_boons.py

---

## What It Is

Two progression systems running in parallel:
1. **XP & Leveling** — killing monsters grants XP, leveling up improves stats
2. **Depth Boons** — fixed passive bonuses granted on first arrival at each dungeon depth

These are intentionally separate. Leveling is earned through combat. Boons are guaranteed exploration rewards — they incentivize pushing deeper.

---

## XP & Leveling

### XP Formula

XP per kill = monster's base XP value (defined in entities.yaml)

Thresholds:
- Level 2: 200 XP
- Level N: 200 + (N-2) * 150 XP (cumulative)

So: L2=200, L3=350, L4=500, L5=650...

### Stat Gains Per Level

- Max HP: +`CON_modifier * 1` HP (e.g., CON 14 = +2 modifier = +2 HP/level)
- Optionally: one perk/ability unlock at levels 3 and 5+
- No accuracy/damage gain from leveling — that comes from equipment and boons

### Level Up Message

"You feel stronger! You reach level N." + stat gains displayed.

### XP Sources

- Monster kills only (no XP for traps, exploration, etc.)
- Faction affiliation doesn't change XP (orc grunt gives same XP regardless of faction context)

---

## Depth Boons System

### Core Design

One fixed boon, automatically applied on **first arrival** at each depth. No choice, no UI, no RNG. Guaranteed reward for pushing forward.

| Depth | Boon ID | Effect |
|-------|---------|--------|
| Depth 1 | `fortitude_10` | +10 max HP, immediate heal for 10 |
| Depth 2 | `accuracy_1` | +2 accuracy (improves hit probability) |
| Depth 3 | `defense_1` | +1 defense (AC) |
| Depth 4 | `damage_1` | +1 minimum damage on all attacks |
| Depth 5 | `resilience_5` | +10 max HP, immediate heal for 10 |

### Timing

- Granted immediately on stepping onto depth for the first time
- "You feel a surge of power as you descend deeper." + boon description
- NOT re-granted on return visits or re-entering the depth via stairs

### Why This Works

- Eliminates the "I already knew what my character would be at depth 5" problem
- Creates a pacing hook: if you're struggling at depth 3, you know boon 3 is coming soon
- No choice paralysis — no "which of 4 options do I pick?"
- Deferred: future boon **selection** could be a separate feature (pick one of 3), but that comes later

### Boon Tracking

`Statistics` component tracks which boons have been applied. Prevents double-application.

```yaml
depth_boons:
  depth_1: {id: fortitude_10, hp_bonus: 10, immediate_heal: 10}
  depth_2: {id: accuracy_1, accuracy_bonus: 2}
  depth_3: {id: defense_1, defense_bonus: 1}
  depth_4: {id: damage_1, min_damage_bonus: 1}
  depth_5: {id: resilience_5, hp_bonus: 10, immediate_heal: 10}
```

---

## Character Statistics Component

Tracks lifetime stats (not just current run stats):

- Kills by monster type
- Damage dealt / damage received
- Items used
- Depths visited (for boon tracking)
- Boons applied (set of boon IDs)
- Death count (if permadeath off)

This feeds both the post-game summary and the harness metrics.

---

## Future: Perk System (Deferred)

Phase 23 in PoC had boon selection UI deferred. Future version:
- At depth thresholds, offer 3 boon options to pick from
- Boon pool per depth category (combat/survival/utility)
- Different builds feel different based on choices

Do NOT implement this yet. The fixed boon table is the current design.

---

## C# Port Checklist

- [ ] `LevelComponent` on player entity (current XP, level, XP to next)
- [ ] XP field in `entities.yaml` per monster type
- [ ] `GainXP(amount)` method; level-up check
- [ ] HP gain on level-up (CON modifier formula)
- [ ] Level-up message + stat display
- [ ] `DepthBoon` YAML definitions (6 boons, depths 0-5)
- [ ] Boon application on first depth arrival
- [ ] `Statistics.AppliedBoons` hash set (prevent double-apply)
- [ ] Boon effect integration: HP bonus, accuracy, defense, min damage
- [ ] "First arrival" detection (DungeonFloor tracks visited set)
- [ ] Boon message display ("You feel a surge of power...")
- [ ] Statistics component for lifetime tracking
- [ ] Harness: boon application metrics
