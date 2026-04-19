# Plan: Interactive Props, Trap System & Status Interactions

Status: [~] In progress — Phases 1–3 complete, Phase 4 in progress
PoC reference: `~/development/rlike/components/trap.py`, `~/development/rlike/services/movement_service.py` (_apply_trap_effects), `~/development/rlike/config/entities.yaml` (map_traps, bone_pile)
Supersedes: most of `plan_traps_chests_features.md` trap section — chests/signs/murals already complete.

---

## Current State
- Phases 1, 2, 3 complete. All 14 PropAndTrap tests passing + 17 registry tests + 19 resolver tests.
- Key fix: TryInteractFeature now filters to BlocksMovement=true only — floor traps (BlocksMovement=false) skip interaction and are handled by HandleFloorTrapEntry after movement.
- Next: Phase 4 (TASK-013 + TASK-014) — EntityPlacer.PlaceFloorFeatures extension for props and floor traps.

---

## Overview

Three interlocking systems built in sequence:

1. **Destructible props** — barrels, bookshelves, bone piles. Bump to break/search. Sometimes yield loot; sometimes trigger a trap payload; bone piles sometimes rouse a zombie.
2. **Floor traps** — 9 types (8 PoC-canonical + acid trap). Trigger when a creature walks onto the tile. Hidden or visible depending on placement context.
3. **Unified TrapActionResolver** — one resolver for all trap payloads, driven by an action list. Invoked by both walk-over (floor traps) and bump-to-interact (trapped props, trapped chests).
4. **Status effect interactions** — secondary effects that emerge from status combinations: acid suppresses troll regen, bleeding attracts undead, poison transfers on drain attacks, weapon coating from acid/slime. These are in later phases after the trap system is established.

Goal: procedurally-placed interactables that reward curiosity with risk, and a status interaction layer that makes every effect part of a tactical language — both a threat and a potential tool.

---

## PoC Alignment

### PoC-exact (carry forward, do not invent)
- **Trap types and YAML field names** — 8 of the 9 types from `config/entities.yaml` `map_traps:` block. Field names `trap_type`, `is_detectable`, `passive_detect_chance`, `spike_damage`, `spike_bleed_severity`, `spike_bleed_duration`, `web_slow_severity`, `web_duration`, `alarm_faction`, `alarm_radius`, `entangle_duration`.
- **Detection model** — passive detect on entry (before effect fires); if detected, future re-entry auto-avoids. `is_detected`, `is_disarmed`, `detectable`. See `components/trap.py`.
- **Bone pile cosmetic flag** — `is_bone_pile: true` in YAML. The visual prop already exists in `config/props.yaml` as `bones_pile`.

### Deviations from PoC (explicitly flagged)
- **Bone pile mechanics** (DEVIATION) — PoC bone pile is purely cosmetic. We extend it to yield loot OR rouse a zombie on bump. Rouse uses a `spawn_monster` TrapAction — no separate RousePayload type. Approved.
- **Barrels and bookshelves as interactables** — not in PoC. New additions. `RoomPropPlacer` currently places decorative barrel/bookshelf/bones_pile per room archetype; TASK-000c converts these to produce interactive entities so there's a single source of truth (no duplicate decorative + interactive versions on the same floor).
- **Acid trap** (DEVIATION) — 9th trap type. PoC has 8. Motivated by troll regen counter-play. Approved.
- **InnateRegenComponent** (DEVIATION) — troll regen is implemented in our codebase as `RegenerationEffect` status with `RemainingTurns=9999`, shared with ring/potion regen. Acid suppression must not silence ring/potion regen on the player. Solution: introduce `InnateRegenComponent` (non-duration, intrinsic, set on monsters at spawn) that AcidEffect suppresses. Ring and potion regen stay as `RegenerationEffect`. Wraith keeps its existing `life_drain_pct` path unchanged.
- **Unified TrapActionResolver** (DEVIATION from PoC structure) — PoC has two code paths (movement_service and chest logic). We unify: trigger is separate from action.
- **Contextual hidden trap placement** — PoC places traps uniformly. We bias placement toward high-value approaches (altar rooms, dead-end treasure rooms, vault entrances). Some traps remain random.
- **Status interactions** (DEVIATION) — PoC has no cross-system status propagation. Bleeding attraction, poison transfer (wraith drain attack), acid anti-regen are new additions.
- **hole_trap uses DescendEvent** — plan originally defined a `TransitionRequestEvent`. Reviewers flagged this would duplicate the entire existing descent pipeline (skip-monster-turns guard, animation, harness handling). Instead, hole_trap emits `DescendEvent(Cause="hole_trap")`. All existing descent consumers work unchanged.

### Intentionally deferred (out of scope this plan)
- Active detection (Search action) — defer to a later plan. Passive detect only here.
- Disarm attempt — defer. Detected traps are simply avoidable.
- Auto-reveal tags (PoC `reveal_tags`) — defer.
- Burning + web fire spread — Phase 2 of a follow-up interactions plan.

---

## Architecture

### Layering
- All new logic is pure C#, Logic layer. Zero Godot references.
- YAML loading through `ContentLoader` + `AotObjectFactory`.
- Presentation handles sprite swaps and toast rendering from TurnEvents.

### Tile IDs (confirmed)

#### Floor traps
| Trap Type | Tile ID | Notes |
|-----------|---------|-------|
| spike_trap | 429 | Confirmed |
| web_trap | 430 | Confirmed |
| gas_trap | 431 | Confirmed |
| fire_trap | 432 | Confirmed |
| alarm_plate | 433 | Confirmed |
| teleport_trap | 434 | Confirmed |
| root_trap | 430 | Shared with web_trap; green modulate `(0.6, 1.0, 0.5, 1.0)` to distinguish |
| hole_trap | 429 | Shared with spike_trap; dark modulate `(0.3, 0.3, 0.4, 1.0)` |
| acid_trap | 431 | Shared with gas_trap; yellow-green modulate `(0.8, 1.0, 0.3, 1.0)` |

Color modulate is a presentation-layer `tile_modulate: [r, g, b, a]` field in floor_traps.yaml. Logic layer ignores it.

#### Destructible props
| Prop | Closed Tile | Open/Resolved Tile | Notes |
|------|-------------|-------------------|-------|
| barrel | 268 | 269 | Sprite swap on break |
| bookshelf | 317 | 317 | No sprite change when searched — stays as 317 |
| bone_pile | 90 | 91 | Scattered variant |

#### Trapped chest
| Feature | Tile | Notes |
|---------|------|-------|
| trapped_chest | 263 | Payload: spike burst (same as spike_trap, fixed). No new chest variants this plan. |

### Components (new)

#### `DestructiblePropComponent` (`Logic/ECS/DestructiblePropComponent.cs`)
```csharp
public sealed class DestructiblePropComponent : IComponent
{
    public Entity? Owner { get; set; }
    /// <summary>"barrel" | "bookshelf" | "bone_pile"</summary>
    public string PropKind { get; init; } = "";
    /// <summary>True once broken/searched. Entity stays on map (broken sprite) but does nothing.</summary>
    public bool IsResolved { get; set; }
    /// <summary>Item entity IDs pre-resolved at floor-gen time. Dropped to player tile on resolve.</summary>
    public List<int> LootEntityIds { get; init; } = new();
    /// <summary>Optional trap payload fired on resolve. Null = no trap.</summary>
    public TrapPayloadComponent? TrapPayload { get; set; }
    /// <summary>Optional rouse: a spawn_monster TrapAction built from the YAML rouse_* fields at placement time. Null = no rouse.</summary>
    public TrapAction? RouseAction { get; set; }
    public int ClosedTileId { get; init; }
    public int OpenTileId { get; init; }
}

// No separate RousePayload record — rouse is a standard TrapAction(Kind="spawn_monster") built from
// the YAML rouse_monster/rouse_radius/rouse_min_depth fields in interactive_props.yaml.
```

#### `FloorTrapComponent` (`Logic/ECS/FloorTrapComponent.cs`)
```csharp
public sealed class FloorTrapComponent : IComponent
{
    public Entity? Owner { get; set; }
    /// <summary>PoC-exact: "spike_trap" | "web_trap" | "alarm_plate" | "root_trap" |
    /// "teleport_trap" | "gas_trap" | "fire_trap" | "hole_trap" | "acid_trap"</summary>
    public string TrapType { get; init; } = "";
    public bool IsDetected { get; set; }
    // IsDisarmed intentionally omitted — disarm is deferred out of scope this plan.
    public bool IsDetectable { get; init; } = true;
    public double PassiveDetectChance { get; init; } = 0.10;
    public TrapPayloadComponent Payload { get; init; } = new();
    public int VisibleTileId { get; init; }
    /// <summary>Presentation-layer color modulate. Null = no modulation.</summary>
    public float[]? TileModulate { get; init; }
    /// <summary>True once triggered — one-shot. Safe to walk over afterward.</summary>
    public bool IsSpent { get; set; }
}
```

#### `TrapPayloadComponent` (`Logic/ECS/TrapPayloadComponent.cs`)
```csharp
public sealed class TrapPayloadComponent : IComponent
{
    public Entity? Owner { get; set; }
    public List<TrapAction> Actions { get; init; } = new();
}

public sealed class TrapAction
{
    /// <summary>
    /// "damage" | "bleed" | "acid" | "burning" | "poison" | "slow" |
    /// "entangle" | "teleport" | "alert_faction" | "descend" | "spawn_monster"
    /// </summary>
    public string Kind { get; init; } = "";
    public int Amount { get; init; }       // damage amount, severity
    public int Duration { get; init; }     // status effect turns
    public int Radius { get; init; }       // alert_faction / spawn_monster search radius
    public string Target { get; init; } = ""; // faction name, monster type id
}
```

### The Resolver

#### `TrapActionResolver` (`Logic/Combat/TrapActionResolver.cs`)
Pure static resolver. Trigger-agnostic.

```csharp
public static class TrapActionResolver
{
    public static bool Resolve(
        Entity target,
        TrapPayloadComponent payload,
        string source,
        (int X, int Y) originTile,
        GameState state,
        SeededRandom rng,
        List<TurnEvent> events,
        MonsterFactory? monsterFactory = null);
}
```

| Kind | Effect | PoC source |
|------|--------|-----------|
| `damage` | Direct HP damage via Fighter | spike_damage |
| `bleed` | BleedEffect(severity, duration) | spike_bleed_* |
| `acid` | AcidEffect(duration) — suppresses InnateRegenComponent | new |
| `burning` | BurningEffect(DamagePerTurn=3, duration) | fire_trap |
| `poison` | PoisonEffect(duration) | gas_trap |
| `slow` | SlowedEffect(amount, duration) | web_trap |
| `entangle` | EntangledEffect(duration) | root_trap |
| `teleport` | Random walkable tile; emit TeleportEvent(Reason="trap") | teleport_trap |
| `alert_faction` | Find faction monsters in radius, set Alerted target | alarm_plate |
| `descend` | Emit DescendEvent(Cause="hole_trap") — reuses existing descent pipeline | hole_trap |
| `spawn_monster` | Find walkable tile in radius, spawn Target via MonsterFactory | bone_pile |

### New status effects (Phase 6)

#### `BleedEffect` (`Logic/Combat/StatusEffects/BleedEffect.cs`)
- Ticks damage per turn (1–2 HP based on severity, lower than poison)
- Emits `BleedTickEvent` each turn
- Cleared by healing potion at severity 1; requires dedicated anti-bleed at severity 2 (future)
- While active: undead within `BleedAttractionRadius` (default 6) that have no current target switch to pursue the bleeding entity

#### `AcidEffect` (`Logic/Combat/StatusEffects/AcidEffect.cs`)
- Duration-based, no tick damage
- While active on an entity: any `InnateRegenComponent` on that entity is suppressed (regen ticks do nothing). Does NOT suppress player `RegenerationEffect` from rings/potions.
- While active on a weapon (via `WeaponAcidCoating`): next N hits apply AcidEffect to the target
- Sources: acid_trap trigger only this plan (slime link deferred — slime corrosion is weapon DamageMax degradation, a different mechanic)

### Trigger integration

#### Floor trap walk-over
In `TurnController.ResolvePlayerMove`, after MoveEvent emission, before stair/pickup logic:
1. Find FloorTrapComponent at new tile where `!IsSpent && !IsDisarmed`
2. If `IsDetected` → emit `TrapAvoidedEvent`, skip
3. Else roll `PassiveDetectChance`:
   - Success → mark `IsDetected=true`, emit `TrapDetectedEvent`, skip trigger
   - Failure → call `TrapActionResolver.Resolve`, mark `IsSpent=true`
4. Monsters: same helper with `skipPassiveDetect=true`

#### Prop bump-to-interact
Extend `TurnController.TryInteractFeature`:
1. Find `DestructiblePropComponent`. If `IsResolved` → `consumesTurn=false`, return.
2. Set `IsResolved=true`
3. Emit `PropDestroyedEvent`
4. Drop LootEntityIds to player tile; run `TryPickUpItemsAt` (IdentificationRegistry required — thread via GameState or factory, see TASK-009)
5. If `TrapPayload != null` → `TrapActionResolver.Resolve(player, payload, propKind_trap, ...)`
6. If `RouseAction != null` → `TrapActionResolver.Resolve(player, single-action payload wrapping RouseAction, "bone_pile_rouse", ...)`
7. `consumesTurn=true`

### Contextual hidden trap placement

Floor traps are placed in two passes:

**Pass 1: Contextual traps** (~70% of floor's trap budget)
Placed in approaches to high-value areas. "Approach" = the 1-2 tiles immediately before or inside:
- Rooms containing an altar
- Dead-end rooms (already reward-biased in EntityPlacer)
- Rooms containing a chest
- Corridors leading to a vault/feature-heavy room

These traps have lower `passive_detect_chance` (0.05–0.08) than random traps — the player is focused on the prize, not the floor. The sense is "of course there's a spike trap in front of the altar."

**Pass 2: Random traps** (~30% of budget)
Scattered in non-player rooms, corridors, mid-room tiles. Normal `passive_detect_chance` (0.10–0.20). These provide the "anywhere is dangerous" texture.

Depth-gated trap pool (both passes):
- Depth 1–2: spike, web only
- Depth 3–5: + alarm, root, gas, acid
- Depth 6+: + fire, teleport, hole (hole at lowest weight, ≤1 per floor)

### YAML schema

#### `config/interactive_props.yaml`
```yaml
interactive_props:
  barrel:
    closed_tile_id: 268
    open_tile_id: 269
    loot:
      weights: { potion: 60, scroll: 10, nothing: 30 }
      min_depth: 1
    trap_chance: 0.15
    trap_table:
      - { weight: 60, payload: fire_burst_small }
      - { weight: 40, payload: spike_burst_small }
  bookshelf:
    closed_tile_id: 317
    open_tile_id: 317          # no visual change when searched
    loot:
      weights: { scroll: 20, nothing: 80 }
      min_depth: 1
    trap_chance: 0.0           # never trapped
  bone_pile:
    closed_tile_id: 90
    open_tile_id: 91
    loot:
      weights: { weapon: 30, armor: 30, nothing: 40 }
      min_depth: 1
    rouse_chance: 0.35
    rouse_monster: zombie
    rouse_radius: 4
    rouse_min_depth: 2         # no rouse at depth 1

trap_payloads:
  fire_burst_small:
    actions:
      - { kind: damage, amount: 4 }
      - { kind: burning, duration: 4 }
  spike_burst_small:
    actions:
      - { kind: damage, amount: 6 }
      - { kind: bleed, amount: 1, duration: 3 }
  spike_burst_chest:           # trapped chest payload — spike burst, no bleed
    actions:
      - { kind: damage, amount: 5 }
```

#### `config/floor_traps.yaml`
```yaml
floor_traps:
  spike_trap:
    visible_tile_id: 429
    is_detectable: true
    passive_detect_chance: 0.10
    actions:
      - { kind: damage, amount: 7 }
      - { kind: bleed, amount: 1, duration: 3 }
  web_trap:
    visible_tile_id: 430
    is_detectable: true
    passive_detect_chance: 0.15
    actions:
      - { kind: slow, duration: 5, amount: 1 }
  gas_trap:
    visible_tile_id: 431
    is_detectable: true
    passive_detect_chance: 0.12
    actions:
      - { kind: poison, duration: 6 }
  fire_trap:
    visible_tile_id: 432
    is_detectable: true
    passive_detect_chance: 0.12
    actions:
      - { kind: burning, duration: 4 }
  alarm_plate:
    visible_tile_id: 433
    is_detectable: true
    passive_detect_chance: 0.20
    actions:
      - { kind: alert_faction, target: orc, radius: 8 }
  teleport_trap:
    visible_tile_id: 434
    is_detectable: true
    passive_detect_chance: 0.15
    actions:
      - { kind: teleport }
  root_trap:
    visible_tile_id: 430
    tile_modulate: [0.6, 1.0, 0.5, 1.0]   # green tint to distinguish from web
    is_detectable: true
    passive_detect_chance: 0.10
    actions:
      - { kind: entangle, duration: 3 }
  hole_trap:
    visible_tile_id: 429
    tile_modulate: [0.3, 0.3, 0.4, 1.0]   # dark blue-grey tint
    is_detectable: true
    passive_detect_chance: 0.08
    actions:
      - { kind: descend }
  acid_trap:
    visible_tile_id: 431
    tile_modulate: [0.8, 1.0, 0.3, 1.0]   # yellow-green tint
    is_detectable: true
    passive_detect_chance: 0.12
    actions:
      - { kind: damage, amount: 4 }
      - { kind: acid, duration: 8 }
```

### TurnEvents (new)
```csharp
public sealed class PropDestroyedEvent : TurnEvent {
    public int X { get; init; }
    public int Y { get; init; }
    public string PropKind { get; init; } = "";
    public IReadOnlyList<int> DroppedItemIds { get; init; } = Array.Empty<int>();
    public bool TrapFired { get; init; }
    public bool MonsterRoused { get; init; }
}
public sealed class TrapTriggeredEvent : TurnEvent {
    public int TargetId { get; init; }
    public int X { get; init; }
    public int Y { get; init; }
    public string Source { get; init; } = "";
    public IReadOnlyList<string> ActionKinds { get; init; } = Array.Empty<string>();
}
public sealed class TrapDetectedEvent : TurnEvent {
    public int X { get; init; }
    public int Y { get; init; }
    public string TrapType { get; init; } = "";
}
public sealed class TrapAvoidedEvent : TurnEvent {
    public int X { get; init; }
    public int Y { get; init; }
    public string TrapType { get; init; } = "";
}
public sealed class MonsterRousedEvent : TurnEvent {
    public int SpawnedEntityId { get; init; }
    public string MonsterType { get; init; } = "";
    public int OriginX { get; init; }
    public int OriginY { get; init; }
}
// No new TransitionRequestEvent — hole_trap emits DescendEvent(Cause="hole_trap").
// The existing DescendEvent gains a Cause field (string, default "player") if not already present.
// All existing descent pipeline consumers (skip-monster-turns guard, animation, harness)
// handle it unchanged; they may inspect Cause to suppress player-action prompts.
public sealed class BleedTickEvent : TurnEvent {
    public int ActorId { get; init; }
    public int Damage { get; init; }
}
public sealed class StatusTransferredEvent : TurnEvent {
    public int SourceId { get; init; }
    public int TargetId { get; init; }
    public string EffectKind { get; init; } = ""; // "poison", "bleed"
}
public sealed class RegenSuppressedEvent : TurnEvent {
    public int ActorId { get; init; }
}
public sealed class WeaponAcidCoatedEvent : TurnEvent {
    public int WeaponId { get; init; }
    public int HitsRemaining { get; init; }
}
```

---

## Phase Breakdown

### Phase 0 — Content & tile confirmation (no code)
- [x] TASK-000: Tile IDs confirmed. See tile table above. All resolved.
- [x] TASK-000b: Bookshelf behavior confirmed: tile 317, no visual change when searched.
- [ ] TASK-000c: **Convert `RoomPropPlacer` to delegate to `EntityPlacer`.** `RoomPropPlacer.cs` currently places decorative barrel/bookshelf/bones_pile entries per room archetype. After TASK-009/013 land, these must be removed from `RoomPropPlacer` and all prop placement routed through `EntityPlacer.PlaceFloorFeatures`. Prevents duplicate decorative + interactive versions on the same floor.
  - Do this AFTER Phase 4 (TASK-013) so interactive placement is stable before removing the old path.
  - Acceptance: no barrel/bookshelf/bone_pile tile placed by `RoomPropPlacer`; counts verified by existing placement tests.

### Phase 1 — Core components + resolver
- [x] TASK-001: Create `DestructiblePropComponent`, `FloorTrapComponent`, `TrapPayloadComponent`, `TrapAction` in `src/Logic/ECS/`. No separate RousePayload — rouse is a `TrapAction(Kind="spawn_monster")`.
  - Status: complete

- [x] TASK-002: Add new TurnEvents to `Logic/Core/TurnEvent.cs` (all events listed in Architecture section — PropDestroyedEvent through WeaponAcidCoatedEvent).
  - Status: complete. BleedTickEvent/RegenSuppressedEvent do not re-declare ActorId (inherited from TurnEvent).

- [x] TASK-003: Implement `TrapActionResolver.Resolve` covering all 11 action kinds.
  - Status: complete. 19 tests passing.

### Phase 2 — YAML content + registries + factory
- [x] TASK-004: YAML DTO classes in `src/Logic/Content/InteractivePropsDefinitions.cs`.
  - Status: complete

- [x] TASK-005: Register all new DTOs in `AotObjectFactory`.
  - Status: complete. 19 registrations added.

- [x] TASK-006: Write `config/interactive_props.yaml`.
  - Status: complete

- [x] TASK-007: Write `config/floor_traps.yaml`.
  - Status: complete

- [x] TASK-008: Create `InteractivePropsRegistry` and `FloorTrapRegistry`. Wire into `ContentLoader`.
  - Status: complete. 17 registry tests passing.

- [x] TASK-009: Extend `FeatureFactory` with `CreateDestructibleProp` and `CreateFloorTrap`.
  - Status: complete. Loot threading via optional factory params (not constructor injection).

### Phase 3 — Trigger integration (TurnController)
- [x] TASK-010: Extend `TurnController.TryInteractFeature` with `DestructiblePropComponent` branch.
  - Status: complete. Key fix: TryInteractFeature filters to BlocksMovement=true to avoid matching floor traps.

- [x] TASK-011: Add floor-trap walk-over check in `TurnController.ResolvePlayerMove`. New `HandleFloorTrapEntry` helper.
  - Status: complete. 14 Phase-3 tests passing.

- [x] TASK-012: Monster walk-over: call `HandleFloorTrapEntry` with `skipPassiveDetect=true` from monster move processing.
  - Status: complete. Monster trap trigger tests passing.

### Phase 4 — Placement
- [ ] TASK-013: Extend `EntityPlacer.PlaceFloorFeatures` — destructible props (barrels, bookshelves, bone piles) with depth-scaled counts and room-tag biases. Pre-resolve loot entities at placement time.
  - Counts (per floor): barrels 1–4, bookshelves 0–2, bone piles 0–3
  - Bone piles: weighted higher in crypt/undead-themed rooms, depth ≥ 2 for rouse
  - Bookshelves: prefer library/wizard rooms; scale up with depth
  - Acceptance: NUnit: prop counts within range, bone pile depth gate, seeded determinism.

- [ ] TASK-014: Extend `EntityPlacer.PlaceFloorFeatures` — floor traps with contextual placement.
  - Two-pass algorithm: contextual (~70% budget) + random (~30%). See contextual placement section above.
  - Depth-gated pool; hole_trap ≤1 per floor starting depth 6.
  - Acceptance: NUnit: `PlaceFloorTraps_Depth1_OnlySpikeAndWeb`, `PlaceFloorTraps_Depth6_IncludesHole`, `PlaceFloorTraps_ContextualBiasAltarRoom`, `PlaceFloorTraps_AvoidsPlayerRoom`, determinism.

### Phase 5 — Presentation wiring
- [ ] TASK-015: Presentation layer listens for `PropDestroyedEvent` (swap sprite), `TrapDetectedEvent`/`TrapTriggeredEvent` (toast/overlay). Apply `tile_modulate` from FloorTrapComponent to trap tile rendering.
  - Acceptance: manual Godot run. Barrel visually cracks. Detected trap shows sprite with correct colour tint. Trigger shows red flash/toast.

### Phase 6 — BleedEffect and AcidEffect (new status effects)
- [ ] TASK-016: Implement `BleedEffect` in `src/Logic/Combat/StatusEffects/BleedEffect.cs`.
  - Fields: Severity (1–2), Duration, DamagePerTick (1 at sev 1, 2 at sev 2)
  - Tick: emit `BleedTickEvent`, apply damage, decrement duration
  - Attraction: each tick, find undead within `BleedAttractionRadius` (6) with no current target → set Alerted toward bleeding entity. Only fires if severity ≥ 1. This is a passive AI modifier, not a separate event.
  - Cleared normally by duration expiry; healing potion clears sev 1 bleed (add to potion resolver).
  - Acceptance: NUnit: `BleedEffect_TicksDamage`, `BleedEffect_AttractsUndead_WithinRadius`, `BleedEffect_HealingPotionClearsSev1`, `BleedEffect_ExpiresAfterDuration`.

- [ ] TASK-017: Implement `AcidEffect` in `src/Logic/Combat/StatusEffects/AcidEffect.cs`.
  - Duration-based, no tick damage.
  - While active: suppress `InnateRegenComponent` on the same entity. Emit `RegenSuppressedEvent` when regen is blocked. Player `RegenerationEffect` (from rings/potions) is unaffected.
  - Acceptance: NUnit: `AcidEffect_SuppressesInnateRegen`, `AcidEffect_ExpiresAndRegenResumes`, `AcidEffect_DoesNotSuppressPlayerRegenerationEffect`.

- [ ] TASK-018: Wire BleedEffect and AcidEffect into `TrapActionResolver` (replace stubs from TASK-003).
  - Also wire into existing `StatusEffectProcessor.ProcessTurn` tick loop.
  - Acceptance: full resolver tests now exercise real effects, not stubs.

### Phase 7 — Status interactions
- [ ] TASK-019: **Poison transfer on drain attacks.**
  - Add `TransfersEffectsOnHit: bool` flag to monster attack definition YAML (combat.yaml or entities.yaml). Wraith gets this (only drain-attack monster currently available; vampire deferred until added).
  - In combat resolution: when attacker has `TransfersEffectsOnHit=true` and target has active poison/bleed, clone the effect onto the attacker. Emit `StatusTransferredEvent`.
  - Acceptance: NUnit: `WraithDrainsPoisonedPlayer_WraithGetsPoison`, `StatusTransfer_OnlyOnDrainAttacks`, `StatusTransfer_DoesNotDuplicateOnAttacker`.

- [ ] TASK-020: **Acid weapon coating from acid trap.**
  - When player triggers acid_trap (walk-over, not killed), check if player has an equipped weapon. If so, mark weapon with `WeaponAcidCoating { HitsRemaining: 4 }` component. Emit `WeaponAcidCoatedEvent`.
  - In combat resolution: when weapon has `WeaponAcidCoating` and hit lands, apply `AcidEffect(duration: 6)` to target. Decrement `HitsRemaining`. Remove component at 0.
  - NOTE: slime corrosion is NOT linked here. Slime corrosion permanently degrades weapon DamageMax — it's a different mechanic (player debuff, not a coating). The acid coating path is acid_trap only this plan.
  - Acceptance: NUnit: `AcidTrap_CoatsWeapon`, `CoatedWeapon_AppliesAcidOnHit`, `CoatedWeapon_ExpiresAfterNHits`, `CoatedWeapon_SuppressesTrollInnateRegen`.

- [ ] TASK-021: **Bleeding attraction integration test.**
  - Scenario: player with bleed, 4 undead at varying distances. Confirm only those within radius switch to alerted. Confirm non-undead are unaffected.
  - Acceptance: NUnit scenario test; integration with Phase 6 BleedEffect. Not a new system — verifies the AI hook from TASK-016 works end-to-end in a real game state.

### Phase 7b — Bot and auto-explore integration
- [ ] TASK-026: **BotBrain trap avoidance.** Detected, non-spent floor traps must be treated as impassable (or very high cost) in BotBrain's A* pathfinding. Without this, bot-driven harness runs will trigger traps at a rate that inflates Death% and corrupts balance metrics.
  - Implementation: in BotBrain's A* cost function, check if the candidate tile hosts a `FloorTrapComponent` where `IsDetected && !IsSpent`. If so, return a cost of `int.MaxValue / 2` (passable in extremis but never chosen when alternatives exist).
  - Acceptance: NUnit: `BotBrain_RoutesAroundDetectedTrap`; harness scenario with seeded trap on optimal path, bot takes alternate route.

- [ ] TASK-027: **AutoExplore `TrapDetectedEvent` interrupt.** When auto-explore is running and a `TrapDetectedEvent` is emitted (passive detect fires mid-explore), auto-explore should pause so the player sees the message. Resume on next input.
  - Implementation: in the auto-explore controller, add `TrapDetectedEvent` to the set of events that interrupt exploration (same pattern as chest/sign interrupts).
  - Acceptance: NUnit: auto-explore step that detects a trap emits the event and halts the explore loop.

### Phase 8 — Test scenarios + harness verification
- [ ] TASK-022: Author identity scenarios in `config/levels/`:
  - `scenario_barrel_loot_identity.yaml` — barrel with guaranteed loot, no trap. Asserts item appears.
  - `scenario_bone_pile_rouse_identity.yaml` — bone_pile with forced rouse at depth 2, zombie spawns.
  - `scenario_spike_trap_identity.yaml` — player walks onto spike trap, takes damage + bleed.
  - `scenario_acid_trap_troll_identity.yaml` — player hits acid trap, weapon coated, hits troll, regen suppressed.
  - `scenario_bleed_undead_attract_identity.yaml` — player bled, undead in radius switch to alerted.

- [ ] TASK-023: Run harness depth scenarios (depth1–depth6) — confirm no regressions in H_PM, H_MP, Death% (±1%).

- [ ] TASK-024: Harness Death% comparison: traps enabled vs disabled at depth 3–6. If Death% rises >8pp at any depth, flag for tuning (trap count reduction or damage reduction). Capture acid-on-troll effect: H_PM for troll encounters should improve when acid trap present at depth 4–6.

- [ ] TASK-025: Update `tasks/plans/INDEX.md` — mark relevant rows, add this plan.

---

## AotObjectFactory Registrations
```
InteractivePropsFile
InteractivePropDefinition
PropLootConfig
Dictionary<string, InteractivePropDefinition>
TrapPayloadDefinition
TrapActionDefinition
List<TrapActionDefinition>
Dictionary<string, TrapPayloadDefinition>
FloorTrapsFile
FloorTrapDefinition
Dictionary<string, FloorTrapDefinition>
Dictionary<string, int>        // loot weight buckets
Dictionary<string, float[]>    // tile_modulate (if parsed as dict)
// ECS components (forward-safety):
DestructiblePropComponent
FloorTrapComponent
TrapPayloadComponent
```

---

## Open Questions / Risks

### Open questions
1. **Trapped chest payload** — confirmed: spike burst payload (`spike_burst_chest`). No new chest subtypes this plan.
2. **Alarm plate re-trigger** — confirmed one-shot for now. May revisit if playtesting shows it feels wrong.
3. **Hole trap depth** — confirmed: depth 6+, max 1 per floor.
4. **BleedEffect and healing potions** — severity 1 cleared by healing potion. Severity 2 (future): dedicated item. Confirm severity 2 is out of scope this plan.

### Balance risks
- **Death% spike from traps** — TASK-024 measures this. Expected: small increase at depth 3–6. Acceptable threshold: ≤8pp increase. Mitigation: reduce trap count or passive detect chance before Death% target is hit.
- **Bleed attraction stacking** — if player has bleed AND is in a crypt-heavy room, 5+ undead may swarm simultaneously. Guard: cap at 2–3 undead alerted per bleed tick. Add `BleedAttractionCapPerTick: 2` config field.
- **Acid coating too powerful** — if weapon coating suppresses troll regen for 4 hits × 6 turn acid duration = very long regen suppression. Ensure AcidEffect duration (6 turns) is shorter than troll regen interval so troll gets some healing back between coated hits. Tune in TASK-024.
- **Loot inflation from props** — bookshelves at 20% scroll rate + barrels at 70% item rate. Should feel like a bonus, not guaranteed supply. Monitor scroll availability in harness.

### Architectural risks
- **spawn_monster recursion** — spawned zombie walks onto a trap, triggers it, resolver fires. Guard: mark trap `IsSpent=true` BEFORE calling Resolve.
- **Determinism in placement** — use sorted room iteration everywhere. No dictionary enumeration in EntityPlacer prop/trap loops.
- **Hidden trap rendering** — presentation must query `FloorTrapComponent.IsDetected` before choosing tile. Trap sprite only shown when detected. If tile is always rendered regardless, detection system is defeated.
- **Acid coating + slime interaction ordering** — if player kills slime AND steps on acid trap same turn (unlikely but possible), two WeaponAcidCoating components could race. Guard: `WeaponAcidCoating` is a single component; check for presence before setting, take the higher `HitsRemaining`.
- **DescendEvent.Cause field** — confirm `DescendEvent` already has or can accept a `Cause: string` field. If not, add one (default "player"). Presentation and harness may use Cause="hole_trap" to suppress confirmation prompts and adjust metrics tagging.

### Test coverage gaps to flag
- Alarm plate: dedicated NUnit for "monster in radius switches to Alerted state."
- Bone pile rouse when no free tile in radius: resolver no-ops cleanly, no crash.
- BleedEffect on a monster (can monsters bleed?): define policy — yes for undead-themed monsters, no for constructs/slimes. Add a `CanBleed: bool` field (default true) to monster definition YAML. Slimes and constructs set `can_bleed: false`. TASK-016 tests must cover `BleedEffect_IgnoredOnCanBleedFalseEntity`.

### Deferred out of scope this plan
- Disarm: detect-only this plan. No disarm action or mechanic.
- Active Search action for traps: passive detection only.
- Burning + web fire spread.
- Vampire (and other future drain attackers): wraith is the only drain monster for TASK-019; add others when the monsters exist.

---

## Tactical opportunity table (design intent reference)

| Trap | Against player | Intentional player use |
|------|---------------|----------------------|
| spike | damage + bleed | lure monster, trigger bleed-attraction chain |
| web | slow | trap fast monster, buy distance |
| gas | poison | contaminate vampire's approach corridor |
| fire | burning | lure monster cluster into fire tile |
| alarm | herd orcs | concentrate into a chokepoint you control |
| teleport | scatter | escape when cornered |
| root | entangle | lock monster while you flee/heal |
| hole | forced descent | escape a floor that's gone badly |
| acid | damage + weapon coat | pre-coat before troll fight |

---

## Success Criteria

- All 9 floor trap types placed and resolved by unified `TrapActionResolver`.
- Barrels, bookshelves, bone piles interact via bump-to-break, same resolver path.
- BleedEffect and AcidEffect fully implemented with secondary interactions.
- Poison transfers to wraith on drain attack. Acid-coated weapon suppresses troll innate regen.
- Bleeding attracts nearby undead (radius 6, cap 2/tick).
- `dotnet test --filter "Category!=Slow"` — all new NUnit tests green; existing suite unregressed.
- Identity scenarios deterministic (same seed = same events).
- Harness Death% within ±8pp of pre-trap baseline or tuning applied + documented.
- No Godot imports in any new Logic file.
- All new YAML types registered in `AotObjectFactory`.
