# Plan: Loot Policy and Pity System

Status: [ ] Not started (stubs exist, not functional)
PoC reference: balance/loot_tags.py (~27,755 lines), config/loot_policy.yaml

---

## What It Is

A band-based loot distribution system with a pity mechanic. Prevents item droughts, ensures the right categories of items appear at the right depths, and keeps item variety feeling intentional rather than random.

Note: Basic stubs are in the codebase from the floor item pool work. This plan covers making them functional with the full policy system.

---

## Item Categories (Loot Tags)

Every item belongs to one or more loot categories:

| Category | Examples |
|----------|---------|
| `healing` | Healing potion, wand of healing, regeneration ring |
| `escape` | Teleport scroll, invisibility potion, slow scroll |
| `identification` | Identify scroll |
| `equipment_upgrade` | Weapons, armor, enhancement scrolls |
| `offensive_consumable` | Fireball scroll, lightning bolt wand |
| `utility` | Confusion potion, root potion |

An item can be in multiple categories (e.g., enhance_weapon scroll is both `identification` and `equipment_upgrade`).

---

## Band-Based Distribution (B1–B5)

Five bands corresponding to dungeon depth ranges:

| Band | Depths | Healing EV | Escape EV | ID EV | Upgrade EV |
|------|--------|-----------|-----------|-------|-----------|
| B1 | 1–2 | 2.5 | 1.5 | 1.0 | 0.5 |
| B2 | 3–4 | 2.0 | 1.5 | 1.5 | 1.0 |
| B3 | 5–6 | 1.5 | 1.5 | 1.5 | 1.5 |
| B4 | 7–8 | 1.0 | 1.5 | 1.8 | 2.5 |
| B5 | 9–10 | 0.5 | 1.5 | 2.0 | 3.0 |

"EV" = expected value of items in this category per floor. So B1 healing EV of 2.5 means roughly 2-3 healing items per floor on average.

**Healing tapers** — early floors favor healing (player learning the game), late floors favor equipment.
**Escape stays flat** — escape items are consistently valuable throughout.
**Equipment scales up** — late game is about gear optimization.

---

## Pity System

Prevents droughts: if a category hasn't appeared in N floors, the system biases or forces it.

### Parameters

- **Tracking window**: 3 floors
- **Soft bias threshold**: If category has had 0 items in last 3 floors → weight multiplied by 2x
- **Hard inject threshold**: If category has had 0 items in last 5 floors → inject 1 item of that category guaranteed, regardless of normal roll

### Why

Without pity: RNG variance means a player can go 5 floors without seeing a single healing item. That's frustrating and can feel unfair even on hard difficulty. Pity smooths variance without eliminating it.

---

## Loot Policy YAML Structure

```yaml
bands:
  B1:
    floor_range: [1, 2]
    categories:
      healing:
        ev: 2.5
        item_pool: [healing_potion, wand_of_healing]
      escape:
        ev: 1.5
        item_pool: [teleport_scroll, potion_of_invisibility]
      identification:
        ev: 1.0
        item_pool: [identify_scroll]
      equipment_upgrade:
        ev: 0.5
        item_pool: [longsword, chain_mail, enhance_weapon_scroll]

pity:
  tracking_window: 3
  soft_bias_multiplier: 2.0
  hard_inject_floor_threshold: 5
```

---

## Loot Controller Responsibilities

1. Determine current depth band
2. For each item category, roll against EV to decide count
3. Select specific items from category's item pool (weighted)
4. Apply pity adjustments (category drought detection)
5. Place items in floor rooms (distribution varies by floor template)

### Placement Distribution

- Normal floors: random placement in random rooms
- Boss floors: boss chest gets highest-value item
- Treasure vault rooms: concentrated placement

---

## Item Rarity Within Category

Within a category's item pool, items have weights:

```yaml
equipment_upgrade:
  item_pool:
    longsword: {weight: 10}
    keen_longsword: {weight: 5}
    masterwork_longsword: {weight: 2}
    fine_longsword: {weight: 1}
```

Higher rarity items appear less often but do appear (not locked behind gates).

---

## Integration With Floor Item Pools

The current `FloorItemPoolEntry` stubs in the codebase define per-floor item pools. The full policy system sits on top: the band system determines WHAT categories appear, and the floor pools determine WHICH specific items from those categories.

---

## C# Port Checklist

- [ ] Item category tags in entities.yaml (each item tagged with loot categories)
- [ ] `LootPolicy` YAML with band definitions and pity config
- [ ] `LootController.GenerateFloorLoot(depth)` — main entry point
- [ ] Band lookup from depth
- [ ] EV-based item count rolls per category
- [ ] Weighted selection within category's item pool
- [ ] `PityTracker` — per-run, per-category drought tracking
- [ ] Soft bias: multiply weights on drought
- [ ] Hard inject: force-add item on extended drought
- [ ] Floor placement (room assignment for generated items)
- [ ] Boss chest: highest value item from equipment_upgrade
- [ ] Harness metrics: loot_category_counts per floor, pity_triggers
- [ ] Test scenario: loot_soft_bias, loot_hard_inject (testing level 98)
