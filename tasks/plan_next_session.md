# Next Session Priorities (post 2026-03-28)

## State as of end of extended 2026-03-28 session

- 454 tests passing
- Equipment/inventory UX: complete (quickbar + equipment panel with body map)
- Entity ID collision bug: fixed via ReIdMonsterEquipment
- Floor item pool pipeline: live (13 new items, 40% flat spawn rate)
- Monster drops: fixed — ItemSpriteManager creates sprites on DropEvent
- Auto-explore: stair interrupt removed — stairs never interrupt exploration
- Equipment panel: shows HP/ATK/HIT/AC stats line
- DungeonFloorBuilder no-guaranteed-spawns path: fixed to pass items+floorItemPool
- **Item pickup bug**: fixed — FindMonsterAt now bypasses stale AliveMonsters cache
- **Grey screen on floor transition**: fixed — PlayerCamera.Update kills tween before snapping
- **Monster naming**: fixed — orc and zombie both have name: fields in entities.yaml
- **Zombie spawn depth**: fixed — min_depth: 10 in entities.yaml matches PoC
- **Weighted spawn system**: live — SpawnWeight field + weighted FillRooms selection

---

## Priority 1 — More PoC monsters

### 1a. Add missing monster types
PoC has monsters that don't exist yet in C#. Port in depth order:
- **slime**: depth 2+, weight 20→40→60 at depths 2/4/6. Mindless, no seek_items, bludgeoning vulnerability.
- **large_slime**: depth 3+, weight 5→15→25 at depths 3/5/7. Splits into 2 slimes on death (optional/deferred).
- **giant_spider**: depth 8+, weight 15→30→45 at depths 8/11/14.
- **troll** (= orc_brute analogue): currently orc_brute has fixed weight 15. PoC troll goes 15→30→60 at depths 3/5/7.

### 1b. Depth-scaling weights
Current C# system uses fixed YAML weights. PoC uses `from_dungeon_level` tables.
Two approaches:
  a) Simple: add `min_depth_2`, `weight_2`, etc. to YAML — ugly
  b) Better: add `spawn_weight_table: [[20, 2], [40, 4], [60, 6]]` to YAML, computed in ContentLoader/EntityPlacer at each depth
Recommend option (b). Check PoC `random_utils.py:from_dungeon_level` for reference implementation.

---

## Priority 2 — Deferred loot systems

See `memory/project_deferred_loot_systems.md` for full detail.

### 2a. Pity system (floor item spawning)
Replace flat 40% in `EntityPlacer.FillRooms` with PoC band-density scaling (B1=0.35x, B2=0.45x, B3+=1.0x).
Add rolling window of floor outcomes to GameState for pity bias.
**TODO comment already in place** in `EntityPlacer.FillRooms`.

### 2b. Rarity tiers (monster drops)
Implement `RarityRoller` in `TurnController.DropMonsterLoot`.
Tiers: Common/Uncommon/Rare/Legendary — stat bonuses based on monster ETP + depth.
**TODO comment already in place** in `TurnController.DropMonsterLoot`.

---

## Priority 3 — Visual polish

### 3a. Tile variety
Current floors all look the same gray. Check if Oryx has floor variants for variation.

### 3b. HUD enemy label truncation
Name might render truncated in HUD. Check label width / clip settings.

---

## Priority 4 — Balance validation

Run scenario harness at depths 1-3 with monster equipment drops live.
Confirm Death% stays in target bands. Monster gear drops are now visible to the player —
may affect encounter feel (orcs drop club/dagger/leather armor).

---

## Priority 5 — Gameplay depth

### 5a. Multiple monsters per room
`max_monsters_per_room` is still TEMP:1 in level_templates.yaml — restore to 2-3.
Run harness to confirm Death% after change.

### 5b. Unified consumable + equipment pool
TODO in EntityPlacer.FillRooms — merge the separate consumable and equipment passes
into a single depth-filtered pool once band-density scaling is in.

---

## Known deferred

- Character sheet / XP / leveling
- Item identification system
- Wand charges
- Partial stack drops
- GUT-based full UI E2E tests
- Monster CanUseItems=true for specific types (once balance validated)
- Pop-up confirm before pathing to stairs ("Descend to depth N?")
- large_slime split-on-death mechanic
