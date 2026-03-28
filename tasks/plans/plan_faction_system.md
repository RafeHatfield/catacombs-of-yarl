# Plan: Faction System

Status: [ ] Not started
PoC reference: components/faction.py, entities.yaml (faction tags)

---

## What It Is

Monsters are tagged with factions. Faction hostility rules control which entities fight each other, creating emergent dynamics where the player isn't always fighting every monster. Orcs and undead fight each other. Neutral creatures attack anything. Bosses have their own rules.

---

## Faction Types

| Faction | Description |
|---------|-------------|
| `orc` | Humanoid orc warriors; hostile to undead |
| `undead` | Reanimated dead; hostile to everything non-undead |
| `neutral` | Unaligned; hostile to player only (unless provoked) |
| `boss` | Final encounter creatures; hostile to player specifically |
| Custom | Named factions for specific rooms/encounters |

---

## Hostility Matrix

Default rules:
- **Orc vs Undead**: Hostile (they fight each other)
- **Undead vs non-Undead**: Hostile (they attack orcs, player, neutral)
- **Neutral vs Player**: Hostile by default
- **Neutral vs Orc**: Not hostile (until attacked)
- **Same faction**: Never hostile to each other

This creates scenarios like:
- Player walks into a room with orcs fighting undead — do you let them weaken each other?
- Player uses invisibility to sneak past while orc/undead battle plays out
- Strategic use of teleport scroll to drop orcs into undead territory

---

## Faction Hostility Configuration

```yaml
faction_hostility:
  orc:
    hostile_to: [undead, player]
  undead:
    hostile_to: [orc, player, neutral]
  neutral:
    hostile_to: [player]
  boss:
    hostile_to: [player]
```

Per-room overrides can force hostility (e.g., an orc stronghold where all creatures fight each other).

---

## AI Target Selection

When a monster selects a target:
1. Check entities in FOV
2. Filter to entities whose faction is in monster's `hostile_to` list
3. Target nearest hostile entity
4. If multiple valid targets at same distance: prefer player (player is always high priority)

This means an orc will attack an adjacent undead if it's closer than the player.

---

## Faction-Based Kill Tracking

Kill metrics tagged by target faction:
- `kills_vs_orc`, `kills_vs_undead`, `kills_vs_neutral`
- Also: `monster_kills_vs_orc` (cross-faction kills, not just player kills)

Enables scenarios testing "do orcs kill undead without player help?"

---

## Ring Leader / Minion AI

Certain monsters are designated "leaders" for their faction in a room:
- **Orc Chieftain**: Leader of orc faction in room; nearby orcs act more coordinated
- When leader dies, faction AI becomes less effective (morale break)
- Leader designation is per-encounter, not per-entity-type

---

## Non-Aggression Pacts (Rare)

Specific faction pairs can be configured as non-hostile:
```yaml
faction_pacts:
  - factions: [spider, neutral]
    type: non_hostile
```

Used for puzzle rooms where normally-hostile creatures coexist for narrative reasons.

---

## Faction and the Player

Player has no faction tag — the player is treated as a valid target by all hostile factions. Player cannot "join" a faction (yet). Future boon/item ideas (deferred):
- Amulet of Orcish Truce — orcs temporarily non-hostile
- Ring of Undead Command — undead non-hostile (but may be OP)

---

## Implementation Notes

- `FactionComponent` on monster entities with `FactionId` string
- `FactionRegistry` loads hostility matrix from YAML
- `TargetSelector.GetHostileTargets(entity, visibleEntities)` filters by faction rules
- Per-room faction overrides via level template
- No faction component needed on player (player is universal target)

---

## C# Port Checklist

- [ ] `FactionComponent` with `FactionId` (string, YAML-defined)
- [ ] `FactionRegistry` loading `faction_hostility` from YAML
- [ ] Monster AI target selection respects faction hostility
- [ ] Cross-faction combat (orc hits undead, undead hits orc)
- [ ] Per-room faction hostility overrides in level templates
- [ ] Faction-based kill tracking in metrics/statistics
- [ ] Faction tag on all monster entity definitions in entities.yaml
- [ ] Test scenario: faction_hostility_verification (testing level 96)
