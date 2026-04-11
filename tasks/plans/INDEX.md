# YARL Implementation Plans — Master Index

Generated from deep audit of Python PoC at ~/development/rlike.
Each plan file captures design intent, key decisions, and PoC reference points.
Status: [ ] Not started | [~] In progress | [x] Complete

## Core Systems Already Ported
- [x] Basic melee combat (D&D accuracy/damage model)
- [x] Equipment slots (weapon/armor/rings)
- [x] Inventory (pickup/drop/equip/unequip)
- [x] Turn controller & player actions
- [x] A* pathfinding
- [x] FOV / visibility
- [x] Floor generation (rooms, corridors)
- [x] HUD & inventory UI
- [x] Monster AI — basic pursuit, item seeking, pickup, use scrolls, drop on death
- [x] Slime monsters — slime + large_slime, split-under-pressure, weapon corrosion
- [x] Floor item pools (YAML-driven loot)
- [x] Depth-scaling spawn weights (from_dungeon_level, DepthWeights, EncounterBudget wired)
- [x] Stat scaling curves (DEFAULT_CURVE + ZOMBIE_CURVE, applied at spawn)

## Plans To Implement (Ordered by Priority / Dependency)

### Tier 1 — Core Mechanics (needed soon)
| Plan | Status | Description |
|------|--------|-------------|
| [plan_identification_system.md](plan_identification_system.md) | [x] | Identified/unidentified items, texture descriptors, mystery sprites, per-run aliases, difficulty tiers |
| [plan_monster_knowledge.md](plan_monster_knowledge.md) | [x] | Progressive monster knowledge (3 tiers), long-press inspect, item inspect panel |
| [plan_status_effects.md](plan_status_effects.md) | [x] | 30+ effects complete. Potions (14 types), throw system, status badges/toasts/tints all done. |
| [plan_player_progression.md](plan_player_progression.md) | [x] | Depth boons complete (16 tests). 3-choose-1 UI deferred. |
| [plan_traps_chests_features.md](plan_traps_chests_features.md) | [ ] | 8 trap types, chests (normal/trapped/locked), signs, murals |

### Tier 2 — Combat Depth
| Plan | Status | Description |
|------|--------|-------------|
| [plan_rings.md](plan_rings.md) | [x] | 16 rings (10 Phase 1, 6 deferred): stat bonuses, regen, speed, free action, teleportation |
| [plan_ranged_combat.md](plan_ranged_combat.md) | [ ] | Range bands, retaliation-first, knockback, special ammo/quiver |
| [plan_spell_wand_scroll_system.md](plan_spell_wand_scroll_system.md) | [x] | 30+ spells, wand charges, scroll effects, spell targeting (Phase 1+2+3 complete; Portal wand complete; single-target targeting UI complete) |
| [plan_faction_system.md](plan_faction_system.md) | [x] | Faction hostility matrix, orc vs undead, emergent combat (impl: plan_faction_system_impl.md) |
| [plan_corpse_necromancer.md](plan_corpse_necromancer.md) | [x] | Corpse entity lifecycle, necromancer + plague_necromancer AI, Raise Dead scroll — Phase 1 (corpse system) + Phase 2 (raise dead resolver, NecromancerAI) complete |

### Tier 3 — World Systems
| Plan | Status | Description |
|------|--------|-------------|
| [plan_doors_secrets_portals.md](plan_doors_secrets_portals.md) | [ ] | Locked doors, secret doors, portal network, key items |
| [plan_monster_specials.md](plan_monster_specials.md) | [~] | Skirmisher leap, orc shaman, orc chieftain, troll regen (corpse/necro extracted to plan_corpse_necromancer) |
| [plan_loot_policy.md](plan_loot_policy.md) | [ ] | Band-based loot distribution, pity system, item category weights |

### Active Implementation Plans
| Plan | Status | Description |
|------|--------|-------------|
| [plan_overnight_phase.md](plan_overnight_phase.md) | [x] | All 5 phases complete: depth boons, wave 4 monsters, wraith life drain, lich soul bolt + AI, identity tests, status immunities |
| [plan_monster_expansion.md](plan_monster_expansion.md) | [x] | 28 monsters in 4 waves complete: Wave 1 orc variants, Wave 2 troll/skeleton/spiders, Wave 3 necromancer/cultist, Wave 4 wraith/lich/troll_ancient/greater_slime/plague_zombie |
| [plan_status_effects_impl.md](plan_status_effects_impl.md) | [x] | Potion system (14 types), throw-anything system, Phase B presentation (badges/toasts/tints) complete. Deferred: bot throw support (TASK-008), harness verification (TASK-010) |
| [plan_throw_system.md](plan_throw_system.md) | [x] | Universal throw: long-press action sheet, Bresenham path, weapon/potion/junk resolution, ThrowAnimator, PlayerAction.ThrowItem |
| [slime_monsters.md](slime_monsters.md) | [x] | slime + large_slime: split-under-pressure, corrosion, weapon materials |
| [depth_scaling_weights.md](depth_scaling_weights.md) | [x] | from_dungeon_level depth weights, EncounterBudget wiring |

### Presentation / Art Direction
| Plan | Status | Description |
|------|--------|-------------|
| [plan_tileset_switching.md](plan_tileset_switching.md) | [ ] | Data-driven tileset YAML, UF + 16bf support, boot-time switching, CLI mapping tool |
| [plan_map_renderer.md](plan_map_renderer.md) | [ ] | IMapRenderer interface, iso + top-down 2D modes, config-driven switching |

### Deferred Feature Plans
| Plan | Status | Description |
|------|--------|-------------|
| [deferred_slime_abilities.md](deferred_slime_abilities.md) | [~] | greater_slime done (overnight build); engulf, hostile_all faction AI, natural damage type, corrosion armor still deferred |

### Tier 4 — Testing & Balance Infrastructure
| Plan | Status | Description |
|------|--------|-------------|
| [plan_bot_personas.md](plan_bot_personas.md) | [ ] | 5 personas: balanced/cautious/aggressive/greedy/speedrunner |
| [plan_testing_mode.md](plan_testing_mode.md) | [ ] | In-game test menu, testing YAML loader, preconfigured test states |
| [plan_balance_pipeline.md](plan_balance_pipeline.md) | [ ] | ETP system, target bands, depth scaling, auto-diagnosis |

### Tier 5 — End Game
| Plan | Status | Description |
|------|--------|-------------|
| [plan_end_game.md](plan_end_game.md) | [ ] | Final boss (Zhyraxion forms), 5 ending paths, victory conditions |
