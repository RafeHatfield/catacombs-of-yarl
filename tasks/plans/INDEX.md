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
| [plan_traps_chests_features.md](plan_traps_chests_features.md) | [x] | Superseded by plan_interactive_props_traps + chests/signs/murals feature. Disarm + active Search deferred. |

### Tier 2 — Combat Depth
| Plan | Status | Description |
|------|--------|-------------|
| [plan_rings.md](plan_rings.md) | [x] | 16 rings (10 Phase 1, 6 deferred): stat bonuses, regen, speed, free action, teleportation |
| [plan_ranged_combat.md](plan_ranged_combat.md) | [x] | Range bands, retaliation-first, knockback, special ammo/quiver. KnockbackService, RangedCombatService, RangedNetArrowBot, 5 scenarios, 33 tests. Harness-validated 2026-05-19. |
| [plan_spell_wand_scroll_system.md](plan_spell_wand_scroll_system.md) | [x] | 30+ spells, wand charges, scroll effects, spell targeting (Phase 1+2+3 complete; Portal wand complete; single-target targeting UI complete) |
| [plan_faction_system.md](plan_faction_system.md) | [x] | Faction hostility matrix, orc vs undead, emergent combat (impl: plan_faction_system_impl.md) |
| [plan_corpse_necromancer.md](plan_corpse_necromancer.md) | [x] | Corpse entity lifecycle, necromancer + plague_necromancer AI, Raise Dead scroll — Phase 1 (corpse system) + Phase 2 (raise dead resolver, NecromancerAI) complete |

### Tier 3 — World Systems
| Plan | Status | Description |
|------|--------|-------------|
| [plan_doors_secrets_portals.md](plan_doors_secrets_portals.md) | [x] | Locked doors, secret doors, portal network, key items |
| [plan_monster_specials.md](plan_monster_specials.md) | [x] | Troll fire suppression, slime engulf, rally lifecycle, orc shaman chant of dissonance — complete (2026-05-20) |
| [plan_loot_policy.md](plan_loot_policy.md) | [x] | Band-based loot distribution, pity system, item category weights — complete |
| [plan_interactive_props_traps.md](plan_interactive_props_traps.md) | [x] | Destructible props (barrel/bookshelf/bone_pile), 9 floor trap types, unified TrapActionResolver, BleedEffect, AcidEffect, weapon acid coating, bot trap avoidance, status interactions. Phase 5 (presentation) deferred. |

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
| [plan_map_renderer.md](plan_map_renderer.md) | [~] | IMapRenderer interface, iso + top-down 2D modes, config-driven switching (Phase 1 complete) |
| [PLAN_mobile_layout.md](PLAN_mobile_layout.md) | [x] | Mobile portrait layout: 5-zone UILayer, QuickSlotBar, MenuButtonBar, FloatingHpBars, MessageLogPanel (all 7 phases complete) |
| [PLAN_topdown_switch.md](PLAN_topdown_switch.md) | [~] | Switch to top-down orthogonal rendering: 16bf 24x24 world tiles, data-driven tile themes, grey dungeon first |
| [PLAN_wall_autotile.md](PLAN_wall_autotile.md) | [x] | Superseded: absorbed into PLAN_dungeon_visual_overhaul Phase 0 (complete) |
| [PLAN_dungeon_visual_overhaul.md](PLAN_dungeon_visual_overhaul.md) | [x] | All 3 phases complete: wall autotile hybrid, room shape variety (6 types), floor composition pipeline. floor_dark/accent/worn tile IDs pending Rafe's sprite survey. |
| [PLAN_room_props_archetypes.md](PLAN_room_props_archetypes.md) | [x] | 15 room archetypes, ~65 prop types, constraint-based placement, YAML-driven config. Renderer integration complete. PROP-009 YAML migration deferred. |
| [PLAN_level_quality_phase2.md](PLAN_level_quality_phase2.md) | [x] | Complete: symmetry, best-of-N, maintenance state, door system (logic+render+FOV), dead-end/grand shrine/vault special rooms. PROP-009 + CORR-001/002/003 deferred. |

### Deferred Feature Plans
| Plan | Status | Description |
|------|--------|-------------|
| [deferred_slime_abilities.md](deferred_slime_abilities.md) | [~] | greater_slime done (overnight build); engulf, hostile_all faction AI, natural damage type, corrosion armor still deferred |

### Tier 4 — Testing & Balance Infrastructure
| Plan | Status | Description |
|------|--------|-------------|
| [plan_testing_infra_phase1.md](plan_testing_infra_phase1.md) | [x] | Dungeon soak CLI: --dungeon mode, DungeonSoakRunResult, outcome classification, JSONL output, multi-run aggregation |
| [plan_testing_infra_phase2.md](plan_testing_infra_phase2.md) | [x] | Bot decision telemetry: BotDecisionRecord, IBotTelemetryRecorder, BotRunSummary, wired into BotBrain.Decide() |
| [plan_testing_infra_phase3.md](plan_testing_infra_phase3.md) | [x] | Analysis reports: DungeonSoakReport generator, JSONL reader for offline analysis, --report flag, CI integration |
| plan_narrative_testing_d1d2.md (no file) | [x] | D1 run transcript (--transcript flag, FormatTranscript), D2 voice-line histogram (VoiceLineHits in soak pipeline + DungeonSoakReport section). 1638 tests. |
| [plan_bot_personas.md](plan_bot_personas.md) | [ ] | 5 personas: balanced/cautious/aggressive/greedy/speedrunner |
| [plan_testing_mode.md](plan_testing_mode.md) | [ ] | In-game test menu, testing YAML loader, preconfigured test states |
| [plan_balance_pipeline.md](plan_balance_pipeline.md) | [ ] | ETP system, target bands, depth scaling, auto-diagnosis |

### Tier 5 — End Game
| Plan | Status | Description |
|------|--------|-------------|
| [plan_end_game.md](plan_end_game.md) | [ ] | Final boss (Zhyraxion forms), 5 ending paths, victory conditions |

### Tier 6 — Under-Warden Story Systems
| Plan | Status | Description |
|------|--------|-------------|
| [plan_cross_run_persistence.md](plan_cross_run_persistence.md) | [x] | Cross-run persistence: all 7 phases complete. 15 namespaces, source-gen JSON, migrations, all arc/catalog mutation APIs, daily seeds. 1528 tests. |
| [plan_possession_system.md](plan_possession_system.md) | [x] | Player possession: Phases 1–7 complete (+ Dispel spell, wraith/lich immunity, Spell-Break wand, VoiceLineRegistry, CatalogEntryRenderer, 3 voice YAML files, wand-kick mechanic, HostAbilityComponent infrastructure — 1631 tests). |
| [plan_under_warden_memos.md](plan_under_warden_memos.md) | [x] | Memo delivery system: MemoRegistry, MemoDeliveryEvaluator, MemoInboxPanel (Phase 4 done). 7 memos drafted; ~23 remaining. |
