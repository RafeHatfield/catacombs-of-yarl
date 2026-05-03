# Plan: Possession System

**Status:** [ ] Not started — spec only, no implementation in this pass.
**Spec version:** 1.2 (2026-04-26). All open questions resolved; Phase 0 closed; Phases 1–4 unblocked. Phase 5 depends on cross-run persistence schema landing in parallel.

- v1.2 (2026-04-26): §8.2 internal contradiction fixed. Possession-induced host deaths now route through a dedicated `PossessionSystem.OnPossessionInducedHostDeath` pipeline that bypasses the standard `OnDeath` flow entirely — making the `RecordKilled` / XP / faction-rep-trigger suppression explicit at the call site. Same pipeline absorbs the §8.5 WardenInitiated corpse-collapse path. §14 method list and TurnController integration notes updated.
- v1.1 (2026-04-26): Initial resolution pass — all ten OQs resolved.
**Drives:** `the_under_warden_v3.md` Signature Moment #2 ("I wore a Hall Warden to the altar"), Tactical Interaction #15 (possession itself), Tactical Interaction #23 (spell-break dispels possessed past-Sasha), the philosophical premise of the Swap ending.
**Sequencing:** Build third, after cross-run persistence and Hollowmark ribbon (per v3 §N).

### v1.1 resolution log (applied inline, decision log at §16)

- **OQ-1:** No HP threshold for valid possession targets. Drain clock + visibility rule supply tactical commitment; HP gate is redundant and conflicts with Signature Moment #2.
- **OQ-2:** Option A — phantom `(X,Y)` on the effect. No transient wand entity.
- **OQ-3:** Picks up freely; items go to Sasha's inventory; keep on exit.
- **OQ-4:** Wraith and lich keep `"possessed"` immunity. Hall Wardens, Oathbreakers, Honored Dead do not.
- **OQ-5:** Auto-explore disabled during Active. Click-to-move stays available.
- **OQ-6:** Modified safety rail — drain alone cannot kill the home body; monster damage can.
- **OQ-7:** No Hall Warden kill credit on Variant 3 dispel. `RecordTrait("past_self", "freed")` on a hidden pseudo-species; backs a future "Freed Past-Selves" catalog page.
- **OQ-8:** Documented behavior; emergent.
- **OQ-9 (new — host-died knowledge unlock):** Host-died drops to `RecordEngaged` only. Voluntary exit after ≥5 turns is the unique Tier-3-unlock path.
- **OQ-10 (new — camera on forced exits):** Voluntary exit tweens; forced exits snap.

---

## Goals

1. Define the cross-system contract for **possession-as-a-status-effect** so that spell-break, past-Sasha Variant 3, and player-initiated possession all compose through one primitive.
2. Specify a state machine, targeting rules, visibility constraint, and HUD layout that fits a portrait phone screen — v3's load-bearing UX claim.
3. Specify integration points without picking final balance numbers. Knobs identified, defaults proposed, harness validation strategy described.

## Non-goals

- Implementation. No code in this pass.
- Hollowmark voice-line authoring. Triggers are listed; lines are content.
- Cross-run persistence schema. Past-Sasha records belong to that doc; this spec only consumes them.
- Final balance numbers (drain rate, range, duration cap). Tunable knobs are flagged.
- Cursed items. Out of v1 scope; spell-break uses listed in v3 do not require it.

---

## §1. The cross-system contract — `PossessionEffect`

**The single primitive. Everything composes through this.**

`PossessionEffect` is an `IStatusEffect` applied to a **host body** (the body being possessed, not the originating entity). The same effect type is used regardless of source — player Hollowmark-channel, Under-Warden bureaucratic possession, or any future system that wants the verb.

### Contract

| Property | Type | Notes |
|---|---|---|
| `EffectName` | `string` | Constant `"possessed"`. Used for immunity keys, voice-line triggers, status badge. |
| `RemainingTurns` | `int` | Effective duration before forced-exit (default proposal: 999, i.e. effectively unbounded; exit is condition-driven, not duration-driven). Tunable. |
| `IsPermanent` | `bool` | `false`. Even though duration is large by default, the effect *can* expire if a designer wants to author a duration-capped possession. The default value just makes it not-the-primary-exit-mechanism. |
| `PossessorEntityId` | `int` | The soul currently wearing this body. For player possession: `state.Player.Id`. For Under-Warden possession: a sentinel value (e.g. `-2`) since the Warden is not a tile-resident entity. |
| `OriginatorBodyId` | `int?` | The home body the possessor came from. For player possession: the catatonic Sasha's entity ID. For Under-Warden possession of a past-Sasha corpse: `null` (no home body — the Warden's authority is ambient). |
| `DrainPerTurn` | `int` | HP/turn drained from `OriginatorBodyId` while this effect is active. Player possession: tunable (default proposal: 1 HP/turn at floors 1–8, 2 HP/turn at floors 9–16, 3 HP/turn at floors 17–25). Under-Warden possession: 0 (no home body to drain). |
| `Source` | `enum PossessionSource` | `PlayerInitiated` or `WardenInitiated`. Drives a few dispel-side and HUD-side branches. |
| `EnteredTurn` | `int` | The `state.TurnCount` at which possession began. Used for diagnostics, knowledge-unlock thresholds, and Hollowmark idle-warning timing. |

### Application rules

- Apply via `StatusEffectProcessor.ApplyEffect<PossessionEffect>(host, duration)` extended with the constructor fields. Prior art: `PlagueEffect` similarly carries `DamagePerTurn` set after application.
- A host can carry **at most one** `PossessionEffect` at a time. Re-application is a logic error; assert and ignore (the second possession should never be triggered against an already-possessed target).
- **Status immunity key:** `"possessed"`. Add to `StatusEffectProcessor.EffectImmunityKeys`. Per `StatusImmunityComponent.cs` and `MONSTERS.md`, `wraith` and `lich` already carry custom immunity lists. Default proposal: wraiths immune (incorporeal, no body to wear), liches immune (sealed by undeath), all other monsters susceptible.

### Removal rules

`PossessionEffect` is removed in exactly four ways. No other code path may remove it.

1. **Voluntary exit by possessor** — `PossessionSystem.ExitVoluntary(state)` removes it.
2. **Visibility / range break** — `PossessionSystem.CheckVisibilityConstraint(state)` removes it at end-of-turn when host is too far or out of LOS from the home body.
3. **Host death** — host's `Fighter.Hp` reaches 0 during host's own turn or in response to damage taken; `PossessionSystem.OnHostDied` removes it as part of the death pipeline.
4. **Spell-break (`Dispel`)** — the new Dispel spell removes any `IStatusEffect` from a target within range. When the target's `PossessionEffect` is removed by Dispel, `PossessionSystem.OnPossessionDispelled` fires the appropriate post-effects (different by `Source`).

`StatusEffectProcessor.ProcessTurnEnd` may **not** remove `PossessionEffect` via duration decrement except in the rare designer-authored duration-capped case (`RemainingTurns > 0` and not `int.MaxValue`-ish). Default install of the effect uses a sentinel large value to keep duration tick a no-op.

### Why this primitive composes everything

- **Player-initiated possession** = `PossessionSystem.Enter(host)` applies `PossessionEffect{ Source = PlayerInitiated, PossessorEntityId = state.Player.Id, OriginatorBodyId = state.Player.Id, DrainPerTurn = depth-scaled }`.
- **Under-Warden possession of a past-Sasha corpse** = the corpse spawn (driven by past-Sasha persistence record + Variant 3 rules) attaches `PossessionEffect{ Source = WardenInitiated, PossessorEntityId = -2, OriginatorBodyId = null, DrainPerTurn = 0 }` to the corpse-Hall-Warden entity at floor build time.
- **Hollowmark's spell-break** = the new `Dispel` spell handler in `SpellResolver.cs` removes any one `IStatusEffect` from the target within 5 tiles. When that effect happens to be `PossessionEffect`, the dispatch lands in `PossessionSystem.OnPossessionDispelled`, which branches on `Source` to either return Sasha to his home body (player path) or collapse the corpse inert and trigger Variant 3 loot (Warden path).

This means **Variant 3 requires zero bespoke code**. Spec it in Variant 3's plan as "spawn a Hall Warden with `PossessionEffect{ Source = WardenInitiated }` attached." Spell-break on it composes through the same primitive that handles voluntary player exit.

---

## §2. State machine

```
┌──────────┐  enter targeting   ┌───────────┐  confirm tap   ┌──────────────┐
│   Idle   │──────────────────▶│ Targeting │───────────────▶│ Active       │
│ (normal  │                   │           │                │ (controlling │
│  play)   │◀──────────────────│           │                │  host)       │
└──────────┘  cancel targeting └───────────┘                └──────┬───────┘
     ▲                                                             │
     │                                                             │
     │      ┌──────────────────────────────────────────────────────┤
     │      │                                                      │
     │  ┌───┴───┐    voluntary    ┌────────┐   visibility broken   │
     └──│ Exit  │◀────────────────│ Active │───────────────────────┤
        │       │   host died     │        │   home body died      │
        │       │◀────────────────│        │───────────────────────┤
        │       │   dispelled     │        │   Marya floor-silence │
        │       │◀────────────────│        │   trigger? (no — UI)  │
        └───┬───┘                 └────────┘                       │
            │                                                      │
            │ post-exit cleanup                                    │
            ▼                                                      │
        Idle ◀─────────────────────────────────────────────────────┘
```

### States

| State | Player input is targeting | What entity is the "controlled entity" (see §9) | When entered |
|---|---|---|---|
| **Idle** | n/a | `state.Player` | Default. After every Exit transition. |
| **Targeting** | Yes — taps on a candidate host show a confirm/cancel UI | `state.Player` (still) | Player taps the new "Possess" action button. Free action — no turn cost yet. |
| **Active** | No | The host entity (the one carrying `PossessionEffect`) | Player confirms the target tap. Costs the player's turn. |
| **Exit** | n/a | Transient — same turn as the trigger | Any of the four removal causes (§1). Resolves in the same turn the trigger fires. |

### Transitions

| From | To | Trigger | Turn cost | Side effects |
|---|---|---|---|---|
| Idle | Targeting | Player taps "Possess" action button | 0 (free action) | Open targeting overlay. Highlight valid targets (§3). |
| Targeting | Idle | Player taps "Cancel" / outside valid target | 0 (free action) | Close overlay. No effect. |
| Targeting | Active | Player taps a valid target | **1 (turn cost)** | Apply `PossessionEffect` to host. Mark home body as `UnattendedBodyTag`. Switch controlled entity. Fire Hollowmark voice trigger `possession_enter`. |
| Active | Exit (Voluntary) | Player taps "Exit Possession" action button | 0 (free action) | Per §8.1 cleanup. Hollowmark `possession_exit_voluntary`. |
| Active | Exit (Visibility) | End-of-turn check fails (§4) | 0 (passive — no extra turn cost beyond the move that broke visibility) | Per §8.3 cleanup. Hollowmark `possession_exit_visibility`. |
| Active | Exit (HostDied) | Host's `Fighter.Hp <= 0` | 0 | Per §8.2 cleanup. Hollowmark `possession_exit_host_died`. |
| Active | Exit (HomeBodyDied) | Home body's `Fighter.Hp <= 0` | 0 | Per §8.4 cleanup. Hollowmark `possession_exit_home_body_died`. **Then** game-over check fires (per §8.4). |
| Active | Exit (Dispelled) | `PossessionSystem.OnPossessionDispelled` invoked by Dispel spell | 0 | Per §8.5 cleanup. Hollowmark `possession_dispelled` (player path) or `past_sasha_freed` (Warden path). |

The state is **not** stored on the player — it's derivable from `state.Player.Get<PossessionEffect>()` being null vs. the host (§9). No separate "possession state" component on the player.

---

## §3. Targeting rules

### Valid targets

A tile is a valid possession target if **all** are true:

1. The tile contains an `Entity` with `Fighter` and `AiComponent`.
2. The entity is alive (`Fighter.IsAlive == true`).
3. The entity does **not** have `StatusImmunityComponent` listing `"possessed"`. (Wraith, lich proposal — see §1.)
4. The entity does **not** have a `CorpseComponent` — possessing a true corpse uses Raise Dead, not Possess.
5. The entity does **not** already have a `PossessionEffect`.
6. The entity is within **possession range** (default proposal: 5 tiles, Chebyshev — same as spell-break range, intentional symmetry. Tunable knob.) of `state.Player`.
7. Line of sight from `state.Player` to the entity exists. Use `state.Map.IsVisible(target.X, target.Y)` — same FOV check as scroll/wand targeting in `SpellResolver.FindClosestVisibleEnemy`.

**No HP threshold.** Possession works on full-HP targets. Tactical commitment is supplied by the drain clock (§7) and the visibility rule (§4); a separate HP gate would do redundant work and would block Signature Moment #2 (a healthy Hall Warden walked to the altar). Resolved per OQ-1.

### Targeting UI

- New `PlayerAction.ActionKind.Possess` (entry into targeting) and one new dispatched action shape: `PlayerAction.Possess(Entity target)` — the confirmed-target form, fired when the player commits.
- Targeting overlay reuses `TargetingOverlay.cs` (already exists for single-target spells). Highlight rules:
  - Green ring on valid targets.
  - Red ring on invalid-because-immune (wraith/lich).
  - No ring on out-of-range or out-of-LOS targets — they fall outside the targeting reticle's reach the same way a scroll target would.
- Confirm-on-tap. Cancel by tapping outside the targeting overlay or pressing the action-bar Cancel button.
- Free action to enter and cancel targeting. Confirming costs the turn.

---

## §4. The 4-tile visibility rule

**v3 §H/I, load-bearing UX fix.** The host must remain within 4 tiles (Chebyshev — proposed, tunable) of the home body, with line of sight, **at end-of-turn**.

### Algorithm

End of every turn (player turn + every monster turn that may have moved either the host or the home body), `PossessionSystem.CheckVisibilityConstraint(state)` runs:

```
if no PossessionEffect active → return
host = entity carrying PossessionEffect with Source == PlayerInitiated
home = entity with id == effect.OriginatorBodyId
if home == null or !home.Fighter.IsAlive → handled by §8.4
if Chebyshev(host, home) > MAX_POSSESSION_DISTANCE → fire ExitVisibility
if !state.Map.HasLineOfSight(host.X, host.Y, home.X, home.Y) → fire ExitVisibility
```

`HasLineOfSight` is a Bresenham trace over `state.Map.IsTransparent` — same primitive as FOV computation. If the engine doesn't expose it as a public method on `GameMap`, add one — it's a 10-line method already implied by `FovComputer.cs`.

### Tunable knobs

| Knob | Default proposal | Notes |
|---|---|---|
| `MAX_POSSESSION_DISTANCE` | 4 | v3's number. Phone-screen-legibility constraint. |
| Distance metric | Chebyshev | Match existing engine convention (combat adjacency, scroll AoE, knowledge-system threat). |
| LOS required | true | Without LOS, possession at 4 tiles around a corner is the same legibility problem as v2's arbitrary-position. |
| Warning threshold | distance == MAX (i.e. one move away from break) | Hollowmark fires `possession_out_of_sight_imminent` voice trigger when host moves to the edge of range. |

### Harness validation

Add a possession-soak scenario: place a player + a possessable host + a home-body-targeting monster, possess, run for N turns, measure (a) average turns until forced exit by visibility, (b) home-body-deaths-per-N-possessions. Sweep `MAX_POSSESSION_DISTANCE` over {3, 4, 5, 6} and pick the value where (a) is ~6–10 turns at floors 9–16 and (b) is ~5–10% — i.e. the player is rewarded for thinking about both bodies but is not punished by random adjacent-host wandering.

---

## §5. The catatonic home body — `UnattendedBodyTag`

When possession enters Active, the home body gets `UnattendedBodyTag` (new tag component, sibling of `FreeActionTag`). The tag drives several engine-side behaviors.

### Behavior of the tagged body

| Aspect | Behavior |
|---|---|
| **Faction targeting** | The home body remains `"player"` faction. Per `FactionRegistry.AreHostile`, all monster factions remain hostile to it. Monsters with `BasicMonsterAI` will path-and-attack toward it the same as toward a normal player. |
| **AI target priority** | `BasicMonsterAI.ChooseTarget` sees the home body as the player (it *is* `state.Player`). Other monsters in range may still target the host depending on faction (host's adopted faction — see §6). |
| **Movement** | None. Home body does not act on its own turn — `TurnController.ProcessTurn` does not invoke any AI on `state.Player`. The unattended body is purely passive: it occupies a tile, it can take damage, it can die. |
| **Status effects** | Continue to tick via `StatusEffectProcessor` as normal. A poisoned home body keeps taking poison damage during possession. |
| **Drain** | `PossessionEffect.DrainPerTurn` HP is removed from the home body each turn the effect is active. Damage is applied at end-of-host-turn (per §7). |
| **Combat with monsters** | Home body cannot retaliate. It has no actions. Monsters attacking it deal full damage with no counter-attack, no equipment-based defense roll changes — same `CombatResolver.ResolveAttack` as normal, but the body's `Fighter` answers the defense roll without acting. |
| **Items / equipment** | Equipment stays equipped. AC contributes to defense rolls when monsters attack the body. Inventory is locked — the player cannot use items "on" the unattended body remotely; the controlled entity is the host. |
| **Pickup** | If a monster steps onto the home body's tile (won't happen for `Fighter`-bearing entities since `BlocksMovement`), the body is unaffected. |

### Hollowmark's positional rules

Per v2: Hollowmark stays with the home body (the wand sits in Sasha's belt while he's away; Hollowmark's voice routes through Sasha's soul, which is in the host).

**Engineering implication:** the wand entity's location is the home body's location. There is no separate "wand entity." The wand exists as an item in `state.Player.Inventory` — its positional reality is the home body's tile. Per v2:

> Hollowmark cannot be picked up by enemies (she rejects them — anyone who tries to grab her takes 1d4 cold damage and drops her), but she can be **kicked** to a different tile

This implies Hollowmark *does* exist as a discrete map entity during possession. **Open question (§16, OQ-2):** does the engine spawn a transient `WandSpilledEntity` at the home body's tile when possession enters, and remove it on exit? Or is the kick effect modeled as a damage tag on the home body's tile that monsters can interact with via a special AI behavior?

The simplest defensible answer: spawn no transient entity. Implement "kick" as a behavior of `BasicMonsterAI`: when adjacent to an `UnattendedBodyTag`'d entity, with the home body protected by the kick-mechanic flag, the monster has a 1-in-N chance per turn to kick — which displaces a phantom "wand position" tile (stored as `(X, Y)` on the `PossessionEffect` itself, defaulting to the home body's tile) by 1–3 tiles in a random direction. If the phantom wand position drifts more than `MAX_POSSESSION_DISTANCE` from the host (not the home body), spell-break and other Hollowmark-mediated abilities are suppressed until the player un-possesses and recovers her.

This is a tunable layer of engineering that v2/v3 both gesture at without specifying. Mark **OQ-2** for design judgment.

### Death of the home body

Per §8.4 — possession ends in `Exit (HomeBodyDied)`, then a player-game-over check fires immediately. Sasha-the-soul is now disembodied; per v3 the Hollowmark binding pulls him back to the vineyard. From the engine's perspective: it's a death. Reactive epilogue text on the GameOverScreen reads the cause as `"home_body_killed_during_possession"`.

---

## §6. The host body during Active possession

### Stat composition

**Sasha's stats stand. Host's abilities are accessible. Host's faction tag protects.**

| Stat / system | Whose value applies? |
|---|---|
| `Fighter.Hp` / `MaxHp` / `BaseDefense` / `Power` / `DamageMin/Max` / accuracy / evasion / `Strength/Dexterity/Constitution` | **Host's own.** The host is the body — its toughness, its arms, its reflexes. Sasha's expertise rides them, but the body is the body. |
| Equipment slots (weapon, armour, rings) | **Host's own** (per `MonsterEquipmentSpawner`). The player does not bring Sasha's gear into the host body. |
| Inventory access | **Sasha's** — the inventory belongs to the player entity, but the player can use items "as Sasha." Items consumed (potions, scrolls) fire from Sasha's inventory list and apply to the host (the controlled entity). Diegetically: Sasha's hand is the host's hand. |
| Hollowmark verbs (portals, spell-break, overnight-ID) | **Sasha's** — the wand is bound to the soul, not the body. Portals open through the host's hand. Spell-break dispels through the host's hand. |
| Status effects | **Host's own** continue ticking. Status effects from items the player uses apply to the controlled entity (host). |
| Faction (for AI target selection) | **Host's adopted faction.** Per the "wear an enemy's body to walk past their friends" beat. Same-faction monsters do not target the host. The host's `AiComponent.Faction` value (e.g., `"orc"` for an orc body) is read by `BasicMonsterAI.ChooseTarget` exactly as it would for a free-roaming orc. The home body is still `"player"` and remains hostile to everyone. |
| Player-faction allies (raised dead, etc.) | They follow the home body (player faction), not the host. They will not attack the host because the host's faction may be neutral-to-them, but they also won't follow the host. |
| Movement speed / momentum | **Host's own.** Wraith-speed possession is a real thing. SpeedBonus reads from host. Momentum tracker is the host's. |
| Special abilities (Soul Bolt for liches, Rally for chieftains, etc.) | **Host's own** — but liches and chieftains are immune to possession by default (§1), so this is academic for the named cases. Hall Wardens have grapple-class abilities; possessing one means wielding them. This is the Signature Moment. |

### Implementation: "controlled entity" abstraction

Today, `state.Player` is the singular reference. `state.PlayerFighter` and `state.PlayerInventory` lock to it. This needs to become "the entity the player is currently controlling."

**Proposed seam:** add `state.ControlledEntity` (read-only computed property):

```
public Entity ControlledEntity =>
    Monsters.FirstOrDefault(m => m.Get<PossessionEffect>()?.Source == PossessionSource.PlayerInitiated
                                  && m.Get<PossessionEffect>()?.PossessorEntityId == Player.Id)
    ?? Player;
```

`state.PlayerFighter` stays as-is (always the home body's Fighter — needed for game-over checks, drain damage). Add `state.ControlledFighter => ControlledEntity.Get<Fighter>()` for movement/combat resolution from within the host.

`TurnController.ResolvePlayerAction` switches against `state.ControlledEntity` instead of `state.Player` for: Move, Attack, UseItem, ThrowItem, CastSpell. Inventory access (UseItem, ThrowItem, CastSpell) reads `state.Player.Get<Inventory>()` because Sasha's inventory is the player's inventory regardless of which body Sasha is wearing.

### What the host can do

| Action | Allowed during possession? |
|---|---|
| Move | Yes. Movement budget = host's. Speed/momentum = host's. |
| Melee attack | Yes. Weapon = host's equipped weapon. Stats = host's. Hit roll uses host's accuracy. |
| Use item from inventory | Yes. Items resolve on the controlled entity (host). |
| Cast spell from a scroll/wand | Yes. Caster = host (so AoE-self centers on host, range starts from host). Hollowmark verbs (portals, spell-break) are scrolls/wands resolving from the host. |
| Throw item | Yes. Origin = host's tile. |
| Equip / unequip items | **No.** Equipment changes are blocked during possession. (Sasha cannot put on the orc's chestplate; he's borrowing the orc's body.) Block at `TurnController` dispatch — return a blocked-action event. |
| Pick up items | **Open question (§16, OQ-3)** — does the host pick up items that go into Sasha's inventory? Or only item types relevant to the host (weapons/armour the host can use)? Cleanest answer: yes, pick up freely; items go to Sasha's inventory; he keeps them on exit. |
| Drop items | Yes (from Sasha's inventory). |
| Descend stairs | **No.** Block — possession-while-on-stairs is a state we don't want to support in v1. |
| Exit possession | Yes (free action). |

### What the host's species-specific abilities do

- Orc Chieftain Rally: while possessing one, the player can "issue rally" (fires `RallyEffect` to nearby orcs) — but the chieftain is in `StatusImmunityComponent`'s default-immunity list (§1), so this is moot unless we relax the immunity. **Open question (§16, OQ-4)**: do we relax immunity for "elite" host bodies (chieftain, lich, wraith) at all?
- Hall Warden grapple (new monster, see `the_under_warden_v3` Hall Warden spec): the player can grapple opponents, executing the grapple ability through the action bar. Implementation: when the controlled entity is a Hall Warden, the action bar adds the Warden's special abilities as new buttons. `MonsterAbility.cs` (does not yet exist) becomes the data interface; per-host-species ability lists are loaded from `entities.yaml` monster definitions.

---

## §7. The drain clock

### Mechanics

- `PossessionEffect.DrainPerTurn` is the per-turn HP loss applied to the home body during Active possession.
- Tick fires at **end of host-controlled turn** (the player's turn while possessing). One tick per player turn — not per monster turn.
- Damage is applied to the home body's `Fighter` directly. It is **not** a `DotDamageEvent` — it's a possession-specific event (`PossessionDrainEvent`) so the UI can render it differently from poison/burn.
- Drain bypasses Defense and damage-resistance rolls. It is the cost of being out of the body, paid in flesh.
- Drain **does not** wake `SleepEffect` (per the existing rule that DOT damage doesn't wake sleep). The home body can be magically asleep during possession; this is fine and tactical.

### Default proposal (tunable knobs, validated by harness)

| Floor band | Drain per turn | Rationale |
|---|---|---|
| 1–8 (Reven Crypt + Boundary) | 1 HP/turn | Possession is a feature, not a finisher. Player can hold a possession for ~30+ turns with full HP. |
| 9–16 (Dimhalls + Weighing) | 2 HP/turn | Mid-game pressure. Possession lasts 15–25 turns. |
| 17–25 (Inner Court) | 3 HP/turn | Endgame possession is a high-stakes tactical commitment. ~10–18 turns. |

These are *floors*, not *bands* — the `state.CurrentDepth` already reads cleanly. Wire via a `PossessionConfig.DrainPerTurnByDepth(int depth)` method.

### Forced-exit thresholds — drain cannot kill the home body, but combat can

Per OQ-6 resolution: **drain alone cannot reduce the home body to ≤0 HP.** Monster damage, status effect ticks, and traps applied to the home body can.

- When the home body's `Fighter.Hp` falls below a warning threshold (default proposal: 25%), Hollowmark fires `home_body_near_death`. Single warning per possession event.
- When drain would tick the home body to **≤ 0 HP**: suppress the tick (clamp HP to 1), fire `home_body_critical_forced_exit`, and resolve possession as `Exit (Voluntary)` immediately. The home body remains at 1 HP. Diegetically: Hollowmark pulls Sasha out before her span pays for the body dying. The forced-exit consumes no extra turn beyond the host-turn that would have ticked drain.
- When **monster damage** (or status DOT, trap damage) takes the home body to ≤ 0 HP: that death stands. `Exit (HomeBodyDied)` fires per §8.4 and the run ends.

This preserves stakes — the player can die during possession, but only to a real threat in the world, not to their own clock. A kamikaze possession that ignores the home body still kills you, because monsters will reach the body and kill it. The clock is pressure, not the executioner.

Hardmode toggle (settings) disables the drain-suppression rail entirely — drain alone can kill the home body, and the run can end on the clock alone. Default off.

---

## §8. Exit conditions — full enumeration

Each exit type has different consequences. Numbered to match the state machine (§2).

### §8.1. Exit (Voluntary)

Trigger: Player taps the "Exit Possession" action button.
Turn cost: 0 (free action — designed deliberately so the player can always pull out without committing a turn).
Cleanup:
1. Remove `PossessionEffect` from host.
2. Remove `UnattendedBodyTag` from home body.
3. `state.ControlledEntity` reverts to `state.Player`.
4. Record species-knowledge unlock (§11) — voluntary exit always counts as "successful possession."
5. Fire `PossessionExitedEvent { Reason = "voluntary", HostEntityId = host.Id }`.
6. Hollowmark voice trigger: `possession_exit_voluntary`.

### §8.2. Exit (HostDied)

Trigger: Host's `Fighter.Hp` reaches 0 — from any source (player damage, monster damage, DOT tick, trap).
Turn cost: 0 (resolved in the same turn the killing blow lands).

**Routing.** Possession-induced host deaths do **not** run the standard death pipeline. The death router checks `entity.Has<PossessionEffect>()` before dispatching: if true, it calls `PossessionSystem.OnPossessionInducedHostDeath(host, state, killer, reason: "host_died")` and **bypasses** the standard `OnDeath` flow entirely. This is the option-2 design from the v1.1 review — the suppression is explicit at the call site, not hidden inside `RecordKilled`.

Cleanup, performed by the dedicated pipeline:
1. Equipment drops via `MonsterEquipmentSpawner`'s standard drop logic (gear hits the floor for the player to recover).
2. `DeathEvent` is emitted for VFX and turn-event flow — same shape as a normal kill so the presentation layer doesn't branch.
3. **Skipped** by this pipeline (the load-bearing reason it exists):
   - `MonsterKnowledgeSystem.RecordKilled` — the player did not kill the host species, only held it.
   - XP award to the player — no kill, no XP, regardless of who landed the killing blow.
   - Faction-reputation kill triggers (e.g., the v3 §M-prime "3 killed Iron-Orcs unprovoked → Hostile" counter) — possession-induced deaths do not increment them.
4. `PossessionEffect` is removed before the entity is converted to a corpse (effect lives on `Fighter`-bearing entities, not corpses).
5. Remove `UnattendedBodyTag` from home body.
6. `state.ControlledEntity` reverts to `state.Player`.
7. Knowledge: pipeline calls `RecordEngaged(speciesId)` — engagement-tier only, no trait unlock (per OQ-9). Voluntary exit after ≥5 turns is the unique deepest-knowledge path; losing the host does not reward catalog completion.
8. Fire `PossessionExitedEvent { Reason = "host_died" }`.
9. Hollowmark voice trigger: `possession_exit_host_died`.
10. Camera: **snap** to home body (not tween — per OQ-10).

### §8.3. Exit (Visibility / Range)

Trigger: End-of-turn `CheckVisibilityConstraint` returns "broken."
Turn cost: 0 (no extra cost — the move that broke visibility already cost its turn).
Cleanup:
1. Remove `PossessionEffect` from host.
2. Remove `UnattendedBodyTag` from home body.
3. `state.ControlledEntity` reverts to `state.Player`.
4. **Host becomes hostile again** — the `AiComponent.Faction` snaps back to its original value. (It never actually changed; faction was always the host's own per §6. The behavior change is that the host now treats the player's home body as hostile via faction matrix, since the player and host are different factions again.)
5. The host does **not** get a free attack on the home body — the host AI picks a target on its next turn. This gives the player a turn of breathing room to either re-engage or reconsider.
6. Knowledge unlock: `RecordEngaged(speciesId)` — counts as engagement (the player held the body for at least one turn). No trait unlock.
7. Fire `PossessionExitedEvent { Reason = "visibility_broken" }`.
8. Hollowmark voice trigger: `possession_exit_visibility`.
9. Camera: **snap** to home body (not tween — per OQ-10).

### §8.4. Exit (HomeBodyDied)

Trigger: Home body's `Fighter.Hp` reaches 0 from **monster attack, status effect DOT, or trap damage** — not from drain. (Drain is rail-suppressed at ≤1 per §7 / OQ-6 in default mode. In hardmode, drain *can* trigger this state.)
Turn cost: 0.
Cleanup:
1. Remove `PossessionEffect` from host (it has no possessor anymore — Sasha is gone).
2. **Game over fires immediately.** `state.IsGameOver` returns true via the standard `!PlayerFighter.IsAlive` path.
3. The host body remains alive on the map. (Diegetically: empty husk, returns to its prior owner. Mechanically: the body resumes its original AI behavior on the next turn — which is moot because the run is over.)
4. `GameOverScreen` reads cause as `"home_body_killed_during_possession"`. Reactive epilogue text per v3's death-epilogue spec acknowledges the specific death (Hollowmark's `home_body_lost_run_over` voice line on the death screen).
5. Camera: moot (game over screen replaces the gameplay camera).

### §8.5. Exit (Dispelled)

Trigger: `Dispel` spell removes `PossessionEffect` from host.
Turn cost: 0 (the Dispel spell already cost its caster's turn).
Cleanup branches on `PossessionEffect.Source`:

**`Source == PlayerInitiated`** (player's own possession was dispelled — by an enemy lich, a hypothetical anti-possession trap, or a future debuff):
1. Remove `PossessionEffect` from host.
2. Remove `UnattendedBodyTag` from home body.
3. `state.ControlledEntity` reverts to `state.Player`.
4. Apply `DisorientationEffect` (3 turns) to the player — being yanked out of a body is jarring. Reuse the existing effect.
5. Knowledge unlock: yes.
6. Hollowmark: `possession_dispelled`.

**`Source == WardenInitiated`** (Hollowmark dispelled the Under-Warden's grip on a past-Sasha corpse — the v3 §E-prime Variant 3 beat):
1. Set `host.Fighter.Hp = 0` (the dispel collapses the body).
2. Route through `PossessionSystem.OnPossessionInducedHostDeath(host, state, killer: state.Player, reason: "warden_dispelled")` — the same dedicated pipeline as §8.2. Standard death is bypassed; the pipeline runs equipment drops via `MonsterEquipmentSpawner`, emits the `DeathEvent`, and skips `RecordKilled` / XP / faction-reputation kill triggers per OQ-7. The Hall Warden species gets no kill credit because the player did not kill a Hall Warden — they freed a past-self.
3. Gear that drops is the past-Sasha's gear from the persistence record (the corpse-host was spawned with that gear equipped — see §12).
4. Override the engagement-recording: instead of `RecordEngaged(speciesId)` for the Hall Warden, the pipeline records `RecordTrait("past_self", "freed")` on the hidden `"past_self"` pseudo-species. Backs the future "Freed Past-Selves" catalog page (one entry per dispelled past-Sasha — long-tail content for engaged players, costs nothing now).
5. Hollowmark: `past_sasha_freed` — the load-bearing voice line. *"That wasn't you anymore, Boss. You can have the gear back now."*

This is the Variant 3 beat. **Zero bespoke code beyond the branch on `Source`.** Both paths ride the Dispel primitive and the death pipeline.

---

## §9. Input re-routing

### What changes

| Where today | Where during possession |
|---|---|
| `state.Player` is the action target for Move, Attack, UseItem, CastSpell, ThrowItem | `state.ControlledEntity` is the target — host while Active, player otherwise |
| `state.PlayerFighter` is the only Fighter that matters | `state.PlayerFighter` still answers game-over, drain damage. `state.ControlledFighter` answers combat & movement. |
| `state.PlayerInventory` is `state.Player.Inventory` | Stays the same — Sasha keeps his inventory regardless of body. |
| `state.Player.X / .Y` is camera focus + FOV center | `state.ControlledEntity.X / .Y` is camera focus + FOV center. The camera follows the controlled body. |

### TurnController dispatch changes

`TurnController.ResolvePlayerAction` (line 203 in `TurnController.cs`) currently dispatches actions assuming `state.Player` is always the source. Add a one-line preamble:

```
Entity actor = state.ControlledEntity;
```

…and switch most case branches to operate on `actor` instead of `state.Player`. Specific branches:

| Action kind | Use `actor` | Use `state.Player` |
|---|---|---|
| `Move`, `Attack`, `UseItem`, `ThrowItem`, `CastSpell` | ✓ (the body acting) | — |
| `EquipItem`, `UnequipItem` | — | ✗ block during possession (§6) |
| `DropItem` | — | ✓ — Sasha drops from his inventory (always the player's) |
| `Descend` | — | ✗ block during possession |
| `Wait` | ✓ | — |

### New action kinds

Add to `PlayerAction.cs`:

```
public enum ActionKind { /* existing... */, EnterPossessionTargeting, Possess, ExitPossession }

public static PlayerAction Possess(Entity host) => new(ActionKind.Possess, target: host);
public static PlayerAction ExitPossession() => new(ActionKind.ExitPossession);
public static PlayerAction EnterPossessionTargeting() => new(ActionKind.EnterPossessionTargeting);
```

`EnterPossessionTargeting` is a free action that opens the targeting overlay — no turn consumed, similar to the gear screen being a free action per existing engine convention.

### Action queue interruption

If possession ends mid-action (e.g., visibility breaks at the start of the host's turn before the player taps anything), the **player's queued action for that turn is consumed and re-targeted to the home body**. Concretely: when `Exit (Visibility)` fires on end-of-turn after the host moved, the *next* turn the player taps a Move action, that action targets the home body (the player has already reverted to controlling the home body before that turn opens).

There is no in-flight action to cancel. The state machine resolves between turns, not mid-turn.

### Auto-explore and click-to-move

Both currently feed `state.Player` as the moving entity. They should feed `state.ControlledEntity` during possession. **Open question (§16, OQ-5)**: do we want auto-explore disabled during possession (it's a tactical state, not a navigation state)? Cleanest answer: yes, disable auto-explore while `PossessionEffect` is active on any monster. Click-to-move stays available — the player should be able to walk the host around without combat awareness penalties.

---

## §10. HUD layout on a portrait phone screen

The 4-tile rule guarantees both bodies fit in a single screen-worth of dungeon at standard zoom. The HUD layout has to support that visual contract.

### Two-bar HP layout

Replace the single HP bar (`HUD.cs`) during possession with a **stacked dual HP bar**:

```
┌─────────────────────────────────────────┐
│  SASHA (home)  ████████░░░░░░░  17/30   │  ← drained per turn, red tint when ≤ 25%
│  ORC  (host)   ██████████████░  42/45   │  ← host's HP, normal tint
│  Possession: 6 turns | Drain: 2/turn    │  ← contextual line, only during Active
└─────────────────────────────────────────┘
```

When idle, the layout collapses to a single bar (Sasha's), preserving the existing minimal HUD.

### Active-controlled-entity indicator

A small icon next to the active HP bar shows **which body the player is currently controlling**. Two sprites:
- A small Sasha-portrait when controlling the home body (idle state).
- A small mask-icon overlaid on the host's species sprite when in Active possession.

### Visibility-warning indicator

When the host moves to a tile at `MAX_POSSESSION_DISTANCE` from the home body (the edge of the rule), the host HP bar pulses yellow and Hollowmark's ribbon fires `possession_out_of_sight_imminent`. One-turn warning before forced exit.

### Action bar replacement

While Active, the action bar adds:
- "Exit Possession" button (free action).
- Any host-species-specific ability buttons (e.g., Hall Warden Grapple) — pulled from a future `MonsterAbility` data structure on the monster definition.

While Targeting, the action bar shows:
- "Cancel" button.

### Where this lives

- `HUD.cs` — extend to read `state.ControlledEntity` and `state.PlayerFighter` separately, render both bars when `Player != ControlledEntity`.
- `QuickSlotBar.cs` and `MenuButtonBar.cs` — add the Possess action button (idle), Exit Possession button (Active), Cancel button (Targeting) per state.
- New `PossessionOverlay.cs` (small) — renders the dual-HP-bar block during Active. Shown above the standard message log.

### Camera

The camera follows `state.ControlledEntity`. On exit, camera behavior depends on the exit type (per OQ-10):

- **Voluntary exit (§8.1):** tween back to the home body. The player chose the moment; they can absorb the transition.
- **Forced exits (§8.2 host-died, §8.3 visibility, §8.5 dispelled):** **snap** to the home body. A tween on a forced exit risks a phone-screen camera lurch that intersects the next tap and causes mistaps. Snap is instant; the player's next tap lands cleanly on the home body's position.
- **Home body died (§8.4):** moot — game over screen replaces gameplay camera.

---

## §11. Species-knowledge unlock

`MonsterKnowledgeSystem.RecordTrait` is the integration point. Possession-as-knowledge maps cleanly:

### Trigger rules

Per OQ-9 resolution: **voluntary exit after ≥ 5 turns is the unique deepest-knowledge path.** Host-died and forced-exit paths are engagement-tier only — losing or being yanked out does not reward catalog completion.

| Possession outcome | Knowledge effect |
|---|---|
| Voluntary exit after ≥ 5 turns | `RecordTrait(speciesId, "possessed_by_player")`. Per `MonsterKnowledgeEntry.Tier`, traits unlock Tier 3 (Understood) immediately. **The unique Tier-3-unlock path.** |
| Voluntary exit after < 5 turns | `RecordEngaged(speciesId)`. No trait, no Tier 3 unlock. |
| Host died during possession (§8.2) | `RecordEngaged(speciesId)`. **No trait, no kill credit.** Holding a body to its death does not deepen knowledge. |
| Visibility exit (§8.3) | `RecordEngaged(speciesId)`. |
| Dispelled, `Source == PlayerInitiated` (§8.5) | `RecordEngaged(speciesId)`. |
| Dispelled, `Source == WardenInitiated` (§8.5 / Variant 3) | `RecordTrait("past_self", "freed")` on the hidden `"past_self"` pseudo-species. **No Hall Warden credit** (per OQ-7). |

### What the player sees

After a possession-induced Tier 3 unlock, the inspect panel for that species shows the full `MonsterInfoView` — special warnings, advice line, all stat labels — exactly as if the player had killed the species enough times to organically reach Tier 3. From the player's perspective: *"I wore an orc, on purpose, until I learned what I came to learn, and now I know orcs."* The verb is intentional; the unlock follows.

The 5-turn threshold is tunable. If reduced to 1, possession trivially unlocks all species (defeats voluntary-≥5 as the design statement); if raised to 10, Tier 3 unlocks become harder to earn through possession than through repeated kills (defeats the verb). 5 is the proposal.

---

## §12. Past-Sasha Variant 3 — composition only

This section is short on purpose. The whole point of §1's contract is that Variant 3 needs no new code.

### Variant 3 spawn (handled in past-Sasha plan, not here)

The past-Sasha persistence record (cross-run schema) includes:
- `cause_of_death: "under_warden"` (the Variant 3 trigger)
- `floor` (where it died)
- `gear_carried` (item IDs Sasha had at death)

When `DungeonFloorBuilder.Build` constructs a floor where the persistence record matches `cause_of_death == "under_warden"` AND the floor matches `floor`, it spawns a Hall Warden-class entity at a chosen tile in the corresponding region, with:
- `MonsterDefinition` of the Hall Warden type.
- `gear_carried` items spawned and equipped via `MonsterEquipmentSpawner`.
- A `PossessionEffect{ Source = WardenInitiated, PossessorEntityId = -2, OriginatorBodyId = null, DrainPerTurn = 0, RemainingTurns = int.MaxValue }` attached at spawn time.

### Variant 3 dispel

When the player casts Hollowmark's spell-break on this entity:
1. `Dispel` spell handler in `SpellResolver` removes the `PossessionEffect` from the target.
2. `StatusEffectProcessor.RemoveEffect` calls `PossessionSystem.OnPossessionDispelled(host, effect, state)`.
3. The `Source == WardenInitiated` branch (§8.5) collapses the host inert: `Fighter.Hp = 0`, standard death pipeline, gear drops.
4. Hollowmark voice trigger `past_sasha_freed` fires.

That is the entire Variant 3 implementation footprint, post-primitive.

The `gear_carried` field is the past-Sasha's gear from the persistence record. `MonsterEquipmentSpawner` already places items via the standard equipment-spawn flow; the spawn data just comes from a different source (cross-run record) instead of the `MonsterDefinition.SpawnEquipment` field.

---

## §13. Hollowmark voice-line trigger taxonomy

The ribbon system listens for these triggers. **Lines themselves are content (Rafe + Claude Chat authoring) — this section is the schema only.**

| Trigger ID | Fires when | Frequency cap | Per-species variants? |
|---|---|---|---|
| `possession_enter` | State enters Active | Once per possession event | Yes — per host species (~25 species worth of variants, per v2 trigger taxonomy) |
| `possession_drain_warning_25` | Home body Hp falls to 25% during possession | Once per possession event | No |
| `possession_drain_warning_10` | Home body Hp falls to 10% during possession | Once per possession event | No |
| `possession_out_of_sight_imminent` | Host reaches edge of `MAX_POSSESSION_DISTANCE` | Once per turn at the edge — debounced so it doesn't fire on every wiggle | No |
| `possession_exit_voluntary` | §8.1 | Once per event | No |
| `possession_exit_host_died` | §8.2 | Once per event | Yes — per species (different commentary for "I lost the orc" vs "I lost the Hall Warden") |
| `possession_exit_visibility` | §8.3 | Once per event | No |
| `possession_exit_home_body_died` | §8.4 — fires on the death screen | Once per event | No (game over) |
| `possession_dispelled` | §8.5, `Source == PlayerInitiated` | Once per event | No |
| `home_body_attacked_during_possession` | Home body takes damage from a monster attack while in Active | Once per possession event (first hit only — repeated would spam) | No |
| `home_body_near_death` | Home body reaches 1 HP (drain safety rail, §7) | Once per event | No |
| `home_body_critical_forced_exit` | Drain safety rail fires the auto-exit | Once per event | No |
| `past_sasha_freed` | §8.5, `Source == WardenInitiated` | Once per past-Sasha encounter | No (it's already a one-shot per past-Sasha record) |
| `wand_kicked_away` | Phantom wand position drifts past `MAX_POSSESSION_DISTANCE` from host (§5, OQ-2 dependent) | Once per kick | No |
| `host_first_seen_in_possession` | Possessing a species for the first time ever in this run | Once per species per run | Yes — per species |
| `species_knowledge_unlocked_via_possession` | Tier 3 unlock fires from a possession exit (§11) | Once per species per run | Yes — per species |

The first-seen-in-possession and species-unlock triggers are the load-bearing per-species lines — they're what make "the time I wore a Hall Warden" feel like a Moment.

---

## §14. New components, types, and files

### New files

| Path | Contents |
|---|---|
| `src/Logic/Combat/StatusEffects/PossessionEffect.cs` | `PossessionEffect : IStatusEffect` with all fields from §1. |
| `src/Logic/ECS/UnattendedBodyTag.cs` | Marker tag. Sibling pattern of `FreeActionTag`. |
| `src/Logic/Core/PossessionSystem.cs` | Static class. Sibling of `PortalSystem.cs`. Methods: `EnterPossessionTargeting`, `IsValidTarget`, `Enter`, `ExitVoluntary`, **`OnPossessionInducedHostDeath`** (single dedicated death pipeline — entry point for both §8.2 and §8.5 WardenInitiated; bypasses standard `OnDeath`, runs gear drops + DeathEvent, skips `RecordKilled` / XP / faction-rep kill triggers, calls the appropriate `RecordEngaged` or `RecordTrait`), `OnPossessionDispelled`, `CheckVisibilityConstraint`, `ApplyDrainTick`, `OnHomeBodyKilled`. |
| `src/Logic/Core/PossessionConfig.cs` | Static config: `DrainPerTurnByDepth`, `MaxPossessionDistance`, `KnowledgeUnlockTurnThreshold`, etc. Tunable knobs in one place. |
| `src/Presentation/UI/PossessionOverlay.cs` | The dual-HP-bar HUD widget per §10. |

### Modified files

| Path | What changes |
|---|---|
| `src/Logic/Core/GameState.cs` | Add `ControlledEntity` and `ControlledFighter` properties. Possibly cache. |
| `src/Logic/Core/PlayerAction.cs` | Add `ActionKind.EnterPossessionTargeting`, `Possess`, `ExitPossession`. Static factories. |
| `src/Logic/Core/TurnController.cs` | `ResolvePlayerAction` switch: route Move/Attack/UseItem/ThrowItem/CastSpell to `state.ControlledEntity`. Block Equip/Unequip/Descend during Active. Handle the three new ActionKinds. End-of-turn hook for `PossessionSystem.CheckVisibilityConstraint`. End-of-host-turn hook for `PossessionSystem.ApplyDrainTick`. **Death router**: at the entry of the death-handling code path (wherever a monster's HP hitting 0 currently triggers `OnDeath`), check `entity.Has<PossessionEffect>()` first — if true, dispatch to `PossessionSystem.OnPossessionInducedHostDeath` and skip the standard pipeline. Same router branch handles the home-body case (`Player.Has<UnattendedBodyTag>()` → fire `OnHomeBodyKilled`). |
| `src/Logic/Combat/SpellResolver.cs` | Add `dispel` spell handler. Remove one `IStatusEffect` from target within range, fire system-specific callbacks for `PossessionEffect`. |
| `src/Logic/Combat/StatusEffects/StatusEffectProcessor.cs` | Add `"possessed"` → `PossessionEffect` to `EffectImmunityKeys`. |
| `src/Logic/AI/BasicMonsterAI.cs` | Add kick-the-wand behavior when adjacent to `UnattendedBodyTag`'d entity (per §5 / OQ-2). Skip targeting an `UnattendedBodyTag`'d entity if the monster's preferred-target priority is satisfied by another nearby foe (this prevents the catatonic body from being a free kill — the monster *will* prefer hitting the host or a faction enemy if available). |
| `src/Presentation/UI/HUD.cs` | Read `state.ControlledEntity` for camera/FOV center. Render dual HP bar via `PossessionOverlay` when `Player != ControlledEntity`. |
| `src/Presentation/UI/QuickSlotBar.cs`, `MenuButtonBar.cs` | Possess / Cancel / Exit Possession action buttons per state. |
| `config/entities.yaml` (monsters section) | Add `"possessed"` to default `status_immunities` list for `wraith` and `lich`. |

### New events

| Event | Fields |
|---|---|
| `PossessionEnteredEvent` | HostEntityId, HostSpecies, OriginatorBodyId |
| `PossessionExitedEvent` | Reason, HostEntityId, HostSpecies |
| `PossessionDrainEvent` | TargetEntityId, Damage |
| `PossessionTargetingEnteredEvent` / `Cancelled` | (free actions, optional — used for SFX/VFX cues) |
| `WandKickedEvent` | NewWandPositionX, NewWandPositionY, KickerEntityId (per OQ-2) |

---

## §15. Implementation phases (sessions estimate)

Per the calibrated estimation note (sessions, not solo-dev weeks):

| Phase | Sessions | Description |
|---|---|---|
| **Phase 0: Spec gate** | 1 | Resolve open questions (§16) with Rafe before any code. |
| **Phase 1: Primitive + state machine** | 1–2 | `PossessionEffect`, `UnattendedBodyTag`, `PossessionSystem` skeleton with Enter/ExitVoluntary, `state.ControlledEntity`. No UI, no targeting. Test from harness. |
| **Phase 2: Targeting + input re-routing** | 1 | New action kinds, targeting overlay reuse, `TurnController` dispatch updates. Mobile UI gates. |
| **Phase 3: Visibility + drain + safety rails** | 1 | `CheckVisibilityConstraint`, `ApplyDrainTick`, near-death safety rail. Harness validation scenario. |
| **Phase 4: HUD + dual HP bar + active indicator** | 1 | `PossessionOverlay`, HUD camera-follow update, action-bar state. The mobile-UX gate session. |
| **Phase 5: Dispel spell + Variant 3 wiring** | 1 | New `dispel` spell in `SpellResolver`. Hook `OnPossessionDispelled` for both source branches. Variant 3 spawn rule (depends on past-Sasha plan). |
| **Phase 6: Knowledge integration + voice triggers + balance pass** | 1 | `RecordTrait` hooks, voice-line trigger emission (no content yet), harness sweeps for drain & visibility tuning. |
| **Phase 7: Wand-kick mechanic + species ability buttons** | 1 | Phantom wand position (per OQ-2 resolution: Option A, no transient entity), monster kick AI behavior. Host-species ability routing through action bar (Hall Warden grapple, etc.). |

**Total: ~7–9 sessions** to feature-complete. Plus author content (Hollowmark trigger lines per species — content workstream, separate).

Phase 0 closed (2026-04-26 — all OQs resolved). Phases 1–4 are unblocked. Phase 5 (Variant 3 wiring) requires the cross-run persistence schema landing in parallel — sequence accordingly.

---

## §16. Decision log (formerly: open questions)

**Status:** All resolved 2026-04-26. Section retained as decision log so future-us can see the framing each call was made on.

**OQ-1: HP threshold for possession targeting (§3).** v2 implies "low HP target." v3 doesn't restate. Pick a value:
- **0% (no threshold)** → possession is a feature; reach for it any time.
- **50%** → possession is a finisher; bring them low first.
- **25%** → possession is a clutch finisher; high commitment.
- *Recommendation was:* 50% (finisher framing).
- **Resolution:** **0% — no HP threshold.** The drain clock and visibility rule already supply tactical commitment; an HP gate does redundant work and conflicts with Signature Moment #2 (a healthy Hall Warden walked to the altar wants the body to be healthy, not half-dead and already suspicious to the altar guards). The verb stays heavy because Sasha is doing the worst thing he's done; reserving it for finishers makes that line lighter, not heavier. §3 updated.

**OQ-2: Hollowmark kickable-positioning model (§5).** v2 says she's kickable; v3 doesn't change this. Pick a model:
- **A.** No transient wand entity. Phantom `(X, Y)` field on `PossessionEffect`.
- **B.** Transient `WandSpilledEntity`.
- **Resolution: A.** Phantom field on the effect. Monster kick adjusts the field by 1–3 tiles in a random direction; if it drifts past `MAX_POSSESSION_DISTANCE` from the host, Hollowmark abilities suppress until possession ends. Voice trigger `wand_kicked_event` fires on every kick.

**OQ-3: Pickup during possession (§6).**
- **Resolution:** Picks up freely; items go to Sasha's inventory; keeps on exit. Diegetically: the host's hand stuffs it in the host's belt; when Sasha steps out he takes it.

**OQ-4: Elite-host immunity (§6).**
- **Resolution:** Wraith and lich keep `"possessed"` in their `status_immunities` (incorporeal, sealed). **Hall Wardens, Oathbreakers, and Honored Dead do not.** YAML edit must make this explicit when those monsters are added — they get `status_immunities: [confusion, slow, fear, poison, bleed]` (their bureaucratic-undead toughness) but **not** `"possessed"`.

**OQ-5: Auto-explore during possession (§9).**
- **Resolution:** Disabled during Active. Click-to-move stays available.

**OQ-6: Drain safety rail (§7).**
- *Recommendation was:* Ship with safety-on (1-HP pull-out rail).
- **Resolution: Modified safety rail.** Drain alone cannot reduce the home body to ≤0 — when it would, suppress the tick (clamp HP to 1) and force voluntary exit. **Monster damage / status DOT / trap damage** taking the home body to ≤0 is a real death and resolves per §8.4. The previous 1-HP rail wording made possession feel reversible in a way that undercut the verb's weight; the modified rail preserves stakes (die to a real threat, not your own clock) without becoming a kamikaze trap. Hardmode toggle disables the rail entirely. §7 updated.

**OQ-7: Variant 3 kill credit.**
- **Resolution: No Hall Warden credit.** `RecordTrait("past_self", "freed")` on a hidden `"past_self"` pseudo-species. Sets up a future "Freed Past-Selves" catalog page (one entry per dispelled past-Sasha) — long-tail content for engaged players, no authoring cost now. §8.5 and §11 updated.

**OQ-8: Possession on a host that becomes hostile mid-possession.**
- **Resolution:** Document and let emerge. `AggravatedEffect` on the host persists through the possession lifecycle. On exit, the host AI takes over with the aggro applied. Correct emergent behavior, no special handling.

---

**Concerns surfaced in v1.1 review (Rafe, 2026-04-26):**

**OQ-9: §11 host-died knowledge unlock is too generous.** The original spec gave host-died a Tier 3 trait unlock plus kill credit, which made the deepest knowledge path the worst possession outcome — perverse incentive for catalog-completion players to rush in and let the host die.
- **Resolution:** Host-died drops to `RecordEngaged` only. **No trait, no kill credit.** Voluntary exit after ≥5 turns is the unique deepest-knowledge path. The framing: voluntary exit rewards careful play; host-died acknowledges you held the body without rewarding losing it. §8.2 and §11 updated.

**OQ-10: Camera behavior on forced exits (§10).** Tween-back-to-home-body works for voluntary exit but a phone-screen camera lurch on forced exits (no react time before next tap) risks mistaps.
- **Resolution:** Voluntary exit tweens; forced exits (host-died, visibility, dispelled) snap. §10 and §8.2/§8.3 updated.

---

## §17. Test plan

Unit tests (logic layer, harness-runnable):

| Test | Verifies |
|---|---|
| Apply `PossessionEffect` to a target. Confirm `state.ControlledEntity` switches. | Primitive contract. |
| `ExitVoluntary`. Confirm `ControlledEntity` reverts. Confirm `UnattendedBodyTag` removed. | §8.1. |
| Move host outside `MAX_POSSESSION_DISTANCE`. End-of-turn check forces exit. | §4 / §8.3. |
| Block LOS with a wall between host and home body. Forced exit. | §4. |
| Drain ticks deduct HP from home body each player turn. | §7. |
| Drain to 1 HP fires `home_body_near_death` and the next turn forces exit at 1 HP (not 0). | §7 safety rail. |
| Home body killed by monster mid-possession → game over. | §8.4. |
| Host killed mid-possession → exit, knowledge-unlock fires, player resumes home body control. | §8.2. |
| Apply `PossessionEffect` to wraith → blocked by status immunity. | §1. |
| Apply Dispel to a `WardenInitiated` possessed corpse → corpse collapses, gear drops, no Hall Warden kill credit. | §8.5 / Variant 3. |
| Apply Dispel to a `PlayerInitiated` possession → player exits, `DisorientationEffect` applied. | §8.5. |
| Possess an orc. Other orcs do not target the host. The home body remains hostile to all orcs. | §6 faction adoption. |
| Equip during possession → blocked. Drop during possession → allowed. | §6 host-action restrictions. |
| Voluntary exit after 5+ turns → species knowledge unlock to Tier 3. | §11. |
| Voluntary exit after 1 turn → no Tier 3 unlock; counts as engagement. | §11. |

Integration / harness:

| Scenario | Validates |
|---|---|
| Possession-soak: vary `MAX_POSSESSION_DISTANCE` ∈ {3, 4, 5, 6}. Measure mean turns-to-forced-exit and home-body-death rate at depths 1/8/16/25. | Tunes §4. |
| Drain-soak: vary `DrainPerTurn` per depth band. Measure home body deaths-per-N-possessions. | Tunes §7. |
| Past-Sasha Variant 3 round-trip: simulate a death-by-Under-Warden, descend, encounter possessed corpse, dispel, loot. Verify gear matches the persistence record. | §12 + cross-run persistence integration. |

---

## Files for reference

| File | What it tells us |
|---|---|
| `src/Logic/ECS/IStatusEffect.cs` | The effect interface `PossessionEffect` implements |
| `src/Logic/Combat/StatusEffects/StatusEffectProcessor.cs` | Where the `"possessed"` immunity key is registered, where duration ticks happen |
| `src/Logic/ECS/StatusImmunityComponent.cs` | How wraith/lich immunity to possession is wired |
| `src/Logic/Core/PortalSystem.cs` | Reference shape for `PossessionSystem.cs` (sibling pattern, static class, state machine) |
| `src/Logic/Combat/SpellResolver.cs` | Where the new `dispel` spell handler lands; pattern for `ResolveStatusEffect<T>` |
| `src/Logic/Core/TurnController.cs` (line 203) | `ResolvePlayerAction` switch — the input-routing seam |
| `src/Logic/Core/PlayerAction.cs` | Where the new ActionKinds and factory methods land |
| `src/Logic/AI/BasicMonsterAI.cs` (`ChooseTarget`) | Faction-aware target selection — how host's adopted faction routes targeting naturally |
| `src/Logic/Knowledge/MonsterKnowledgeSystem.cs` | `RecordTrait` integration for §11 |
| `src/Logic/ECS/CorpseComponent.cs` | Past-Sasha Variant 3 spawn substrate |
| `src/Presentation/UI/HUD.cs` | Where dual-HP-bar rendering hooks |
| `docs/story/the_under_warden_v3.md` §H/I, §E-prime, §M.6 | Source design for the 4-tile rule, past-Sashas, and the Signature Moment |
| `docs/story/the_under_warden_v2.md` §I | More mechanically detailed possession spec — drain, exit triggers, Hollowmark kickability |
| `docs/story/the_under_warden_design_notes.md` (Net-new systems row + §"Still live in v3" #7) | Why this spec exists — possession-as-status-effect was flagged as the cross-system contract that needed resolving before build |
