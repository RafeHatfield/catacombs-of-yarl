# Plan: Player Progression (Depth Boons)

Status: [ ] Not started
PoC reference: balance/depth_boons.py, components/statistics.py
Doctrine: docs/PLAYER_PROGRESSION_DOCTRINE.md

---

## Decision: No XP System

**XP leveling is rejected.** The authoritative design is in
`docs/PLAYER_PROGRESSION_DOCTRINE.md`, which should be read before
touching this plan. The short version:

- XP creates grind incentives and untestable run variance.
- Kill-count power makes the scenario harness unable to produce stable
  depth baselines (every probe would need a full run history).
- Depth boons are deterministic (one per depth, not kill-dependent),
  which means scenarios can assume a known boon budget at any depth.

XP was present as dead code in the Python PoC. It was never wired to
balance data. A/B testing with the PoC's depth boon system showed boons
suppress Death% by 10-20% at depths 4-6 relative to a no-boon baseline.
That data is the reason depth boons won.

If XP is ever revisited, the doctrine's Section 7.1 defines the only
acceptable form: XP as a boon-unlock accelerator (e.g., see 4 choices
instead of 3), never as a direct stat track.

---

## What This Plan Builds

**Phase 1 (current):** Fixed boon table, depths 1-5. One boon per depth,
automatically applied on first arrival. No UI selection, no RNG. Exactly
what the PoC shipped.

**Phase 2 (deferred):** 3-choose-1 selection UI. At depth N, offer 3 boons
from a depth-band pool; player picks 1. Requires a boon pool design,
boon selection UI, and a scenario harness that can force specific
selections. Do NOT implement Phase 2 now.

---

## Phase 1: Proven Boon Table (PoC, depths 1-5)

These values are proven from the Python PoC (`balance/depth_boons.py`).
Do not change them without running the depth pressure validation protocol
in Section 4 of the doctrine.

| Depth | Boon ID | Display Name | Effect |
|-------|---------|--------------|--------|
| 1 | `fortitude_10` | Fortitude | +10 max HP; immediate heal for 10 HP |
| 2 | `accuracy_1` | Keen Eye | +2 accuracy (to-hit chance) |
| 3 | `defense_1` | Iron Skin | +1 defense (reduces incoming damage) |
| 4 | `damage_1` | Cruel Blow | +1 minimum damage on all attacks |
| 5 | `resilience_5` | Resilience | +10 max HP; immediate heal for 10 HP |

Depths 6+ have no boon mapping in the PoC. When Phase 2 pools are
designed, they will cover deeper bands. Until then, first arrival at
depth 6+ awards no boon and is silently a no-op.

### YAML Definition

Boons are defined in a dedicated YAML block (not embedded in
entities.yaml). Location TBD — likely `config/depth_boons.yaml`:

```yaml
depth_boons:
  1: {id: fortitude_10, display_name: "Fortitude", hp_bonus: 10, immediate_heal: 10}
  2: {id: accuracy_1,   display_name: "Keen Eye",  accuracy_bonus: 2}
  3: {id: defense_1,    display_name: "Iron Skin",  defense_bonus: 1}
  4: {id: damage_1,     display_name: "Cruel Blow", min_damage_bonus: 1}
  5: {id: resilience_5, display_name: "Resilience", hp_bonus: 10, immediate_heal: 10}
```

---

## Trigger Rule

```
On entering depth D for the first time this run:
  If visited_depths[D] == false:
    Set visited_depths[D] = true
    Look up boon for depth D
    If boon exists: apply it permanently, log it to boons_applied
    Show message: "You feel a surge of power as you descend deeper. [Boon name]."
  Else:
    No-op (ascending and re-entering depth D never re-grants the boon)
```

The `visited_depths` flag is a boolean set, not a counter. Set once,
never cleared. This is the complete anti-farming mechanism — there is
no secondary enforcement because there is no mechanism to reset.

---

## C# Implementation Tasks

### Prerequisites (must exist before building this)

- [ ] **PRE-1:** Monster roster expansion sufficient to populate depths 4-6
      with at least 3-4 distinct monster types. The depth 4-5 boons
      (`damage_1`, `resilience_5`) only make sense to validate if the
      encounter pressure at those depths is representative.

- [ ] **PRE-2:** Ring and neck equipment slots exist (or at least a clear
      plan for them). Some future Phase 2 boons are likely to interact
      with equipment slots. Phase 1 doesn't need rings, but the
      `BoonComponent` design should not make rings awkward to add later.

### Phase 1 Implementation Tasks

- [ ] **BOON-001:** `BoonDefinition` record in Logic layer.
      Fields: `BoonId`, `DisplayName`, `HpBonus`, `ImmediateHeal`,
      `AccuracyBonus`, `DefenseBonus`, `MinDamageBonus`.
      All numeric fields default to 0. No Godot dependency.

- [ ] **BOON-002:** `DepthBoonConfig` — typed YAML deserialization class.
      Maps depth (int) to `BoonDefinition`. Loaded by `ContentLoader`.
      Deserializes from `config/depth_boons.yaml`.

- [ ] **BOON-003:** `BoonComponent` on player entity.
      Fields: `HashSet<int> VisitedDepths`, `List<string> BoonsApplied`.
      No `disable_depth_boons` flag needed for Phase 1 (harness can
      inject via scenario setup instead). Add `DisableDepthBoons` bool
      if harness wiring requires it.

- [ ] **BOON-004:** `BoonSystem.ApplyDepthBoonIfEligible(Entity player, int depth)`.
      Pure Logic layer. Returns the applied `BoonDefinition?` or null.
      Side effects: mutates `FighterComponent` stats, appends to
      `BoonsApplied`, marks `VisitedDepths`. Raises on unknown boon ID.

- [ ] **BOON-005:** Wire `BoonSystem` into `TurnController` or
      `GameState.DescendFloor()` — wherever floor transitions are
      resolved. Must fire before the first turn on the new depth.

- [ ] **BOON-006:** Boon message in `TurnEvent` stream. Add a
      `DepthBoonEvent(BoonDefinition boon)` event variant. Presentation
      layer converts it to a toast: "You feel a surge of power as you
      descend deeper. Fortitude: +10 max HP."

- [ ] **BOON-007:** Carry-forward in `PlayerCarryForward`.
      `BoonComponent` state (both `VisitedDepths` and `BoonsApplied`)
      must persist across floor transitions. The applied stat effects
      already persist via `FighterComponent` carry-forward, but the
      tracking state must not be reset.

- [ ] **BOON-008:** Scenario harness support. The harness scenario YAML
      must be able to pre-grant a boon set to bypass the depth-trigger:
      ```yaml
      player:
        boons: ["fortitude_10", "accuracy_1"]
      ```
      This grants the listed boons at scenario init without requiring
      the player to have visited those depths. Required for isolated
      boon pressure testing.

- [ ] **BOON-009:** Harness metrics export. `BoonComponent.BoonsApplied`
      must be included in the JSON export from each run. Enables A/B
      probes (boons-on vs boons-off) at depth 4-6 to validate the
      10-20% Death% suppression result from the PoC.

- [ ] **BOON-010:** Unit tests.
      - Boon applies on first arrival, not on return visit.
      - All 5 boon IDs apply correct stat mutations (verify FighterComponent
        fields post-apply).
      - `BoonsApplied` list reflects applied boons.
      - Double-apply guard works (return to depth, no re-grant).
      - Scenario-injected boons bypass depth-trigger (BOON-008 path).
      - Unknown boon ID raises (fail loud, not silent).

- [ ] **BOON-011:** Harness depth pressure validation.
      Run depth 4 and depth 5 probe scenarios with and without boon
      pre-grant. Confirm H_PM, H_MP, and Death% remain within target
      bands from the doctrine (Section 4.1). This is non-negotiable
      before merging.

---

## What Must NOT Be Built

- No XP field on monsters. No `LevelComponent`. No `GainXP()` method.
- No HP gain on level-up (there are no levels).
- No boon selection UI (Phase 2, deferred).
- No boon pool expansion beyond depth 5 (Phase 2).
- No boon synergies or compound effects (deferred).
- No percentage-based boons (doctrine Section 5.3 forbids them).
- No tiny stat increments. +1 HP is not a boon. Minimum measurable unit
  is +8-10 HP for survivability boons. See doctrine Section 3.D.

---

## Deferred: 3-Choose-1 Selection UI (Phase 2)

When the time comes, Phase 2 requires:

1. A boon pool per depth band (not a 1:1 depth mapping).
2. A seeded draw of 3 boons from the pool for the entered depth's band.
3. A selection UI (mobile-friendly — tap to choose).
4. Scenario harness support for forcing a specific selection.
5. Pressure model validation for every new boon in the pool.

The Phase 1 fixed table scaffolds this cleanly: `VisitedDepths`,
`BoonsApplied`, and the harness injection mechanism are all reusable.
Phase 2 replaces the 1:1 depth→boon lookup with a pool draw and adds
a UI step before application.

---

## Balance Validation Protocol

Before any boon ships, run the protocol from doctrine Section 4.3:

1. Define the boon's expected pressure impact (which invariants shift?).
2. Create a clone of the relevant depth probe scenario; pre-grant the boon.
3. Run under `seed_base=1337`, collect H_PM / H_MP / Death%.
4. Confirm invariants remain within target bands (doctrine Section 4.1).
5. Test worst-case synergy: all 5 boons active, run depth 4 and 5 probes.
6. Midgame probe (depth 4) must pass with accumulated boons from depths 1-3.

This is mandatory. No boon merges without these results attached to the PR.
