# Mid-Run Save: Private-Field & Id-Reference Audit (M1.4 4a.3)
Generated 2026-07-16 by a reflection pass over all **84** registered concrete `IComponent` types.
This feeds the GameState-save field classification and the S2 determinism soak: any component
state that is mutable after construction and not serialized would silently diverge on load.

Method: enumerate every non-public instance field (excluding compiler `k__BackingField`s — those
belong to auto-properties, which the completeness gate already round-trips) and classify:
- **COVERED** — serialized via the component's DTO (directly or through a serializer accessor).
- **DERIVED** — recomputed on load from covered state; need not be serialized.
- **DEAD** — provably never read after construction.

The completeness gate (`MidRunComponentGateTests`) covers all **public** component state by
round-trip + sentinel. This audit closes its known blind spot: **private** fields with no public
property, which the gate cannot see.

## Private instance fields (all 84 types → 6 private fields)

| Component | Private field | Type | Class | Justification |
|---|---|---|---|---|
| `Inventory` | `_items` | `List<Entity>` | COVERED | Serialized via `Items` → `InventoryDto.ItemIds`; rebuilt with `Add` on load. |
| `SpeedBonusTracker` | `_attackCounter` | `int` | COVERED | Exposed via `AttackCounter`; restored via `RestoreMomentum` (4a.2). Drives bonus-attack cadence. |
| `SpeedBonusTracker` | `_lastTargetId` | `int` | COVERED | Exposed via `LastTargetId`; restored via `RestoreMomentum` (4a.2). Momentum reset key. |
| `StatusImmunityComponent` | `_immunities` | `HashSet<string>` | COVERED | Exposed via `Immunities`; reconstructed through the constructor (4a.2). |
| `AutoExploreState` | `_positionHistory` | `(int,int)[6]` | COVERED | **Gap surfaced by this audit, fixed in this PR:** oscillation-detection ring buffer, read after construction (`IsOscillating`). Now `PositionHistorySnapshot` / `RestorePositionHistory` + `AutoExploreStateDto.PositionHistory`. |
| `AutoExploreState` | `_positionCount` | `int` | COVERED | Implicit in the serialized `PositionHistory` length (0–6); restored by `RestorePositionHistory`. |

**Result: 0 open gaps.** Every private field is COVERED. No DERIVED or DEAD fields were found;
no field required a STOP-flag-and-wait (the one gap was low-risk and in-scope, so it was fixed
rather than deferred — called out above and in the PR).

## Id-typed reference fields (closure reasoning)

The reachability closure must traverse to every entity reachable **by id** from a root, not just
list members. Entity *object* references (Equipment's 9 slots, `Inventory.Items`,
`ChestLootStash.Items`, `PortalCastStateComponent.PendingEntrance`) are already traversed as
container children (4a.2). The remaining int-id fields were classified:

| Field | References | Traverse? |
|---|---|---|
| `DestructiblePropComponent.LootEntityIds` (`List<int>`) | pre-generated loot entities in NO floor list until the prop opens | **Reachable** — the same entities are held as objects in the prop's `ChestLootStash` (`EntityPlacer` stashes them), so the closure reaches them through that container. The id list is a mirror. Validated by `MidRunReachabilityTests`. |
| `PossessionEffect.{PossessorEntityId,OriginatorBodyId}`, `PortalComponent.LinkedPortalId`, `OrcShamanComponent.ChantTargetEntityId`, `DissonantChantEffect.ChantingShamanId`, `RallyEffect.ChieftainId`, `TauntedEffect.TauntTargetId`, `SpeedBonusTracker.LastTargetId`, `AutoExploreState.Known*Ids` | player / monsters / portals / features — all in a top-level GameState list | No traversal needed; the referenced entities are roots. These stay plain int data. |
| `*.{ClosedTileId,OpenTileId,VisibleTileId,TileId,LockColorId}` | tile / lock-colour ids, NOT entity ids | N/A — not entity references. |

**Closure conclusion:** with GameState-save rooting every entity list + the player, and 4a.2's
container-child traversal, the table is complete. No new id-traversal code is required for the
known surface; the reachability rule is enforced and tested at the serializer level here, and will
get the full build→save→load→open-chest integration test with GameState SaveMidRun/LoadMidRun.
