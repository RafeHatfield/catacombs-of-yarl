# Visible Corpses (Presentation)

Ruled Foundation, 2026-08-22. Corpses have mechanical weight — necromancer raise
(`RaiseDeadResolver` / `NecromancerAI` / `LichAI`), possession blocking (`PossessionSystem`),
and the past-Sasha Spell-Break (`wand_of_spell_break` → dispel) — but had never rendered:
live play removed the sprite on death, resume skipped them. This closes the visibility gap.
**Presentation only** — no corpse mechanics, loot, RNG, or `MakeCorpse` changed.

## Ruled treatment
A corpse renders as the **species' own sprite** (via its retained `SpeciesTag`) under a corpse
treatment: **rotated ~90°** (fallen), **darkened + desaturated**, **faded**. No new art assets.

Proposed values (in `CorpseSpriteManager`; device-judged, then lock):

| Lever    | Proposed value                          |
|----------|-----------------------------------------|
| Rotation | 90° (`Mathf.Pi / 2`)                    |
| Modulate | `Color(0.50, 0.45, 0.42, 0.75)` — darken + desaturate + 75% opacity |

Rotation pivots at the sprite `Position` (with the same grounding `Offset` as the live sprite),
so a fallen body may sit slightly toward one side of the tile — acceptable, tune on device.

## Architecture — reconcile against `state.Corpses`
`CorpseSpriteManager` (mirrors `ItemSpriteManager`) owns corpse sprites on the shared
`entityLayer`, keyed by entity id. It is deliberately **separate from `EntitySpriteManager`**
(which renders the living and skips `Has<CorpseComponent>()`), so status-tint / position passes
never touch the dead.

- **`Sync(state)`** is the single source of truth, run once per turn: create a sprite for every
  corpse in `state.Corpses` lacking one, free any sprite whose entity has left `state.Corpses`.
  Every corpse world-exit routes through `state.Corpses`, so one reconcile covers all paths.
- **`Initialize(state)`** = first `Sync` on floor load / **resume** (rebuilds carried corpses).
- **`UpdateVisibility(state)`** = FOV-only, matching the **item convention** (visible only in
  current FOV, never remembered, **not on the minimap**).
- **Z-order**: `GetEntitySortOrder(x,y) - 1` = one below a co-located live entity (odd sort
  order), so a living monster or the player walking onto the tile draws **on top** of the remains.

### Seams
- **Live death**: `GameController` still `RemoveEntity`s the live sprite on `DeathEvent`; the
  next `Sync` creates the corpse sprite (the entity is already in `state.Corpses`).
- **Resume**: `EntitySpriteManager.Initialize` keeps skipping `Has<CorpseComponent>()` (symptom-B
  fix); `CorpseSpriteManager.Initialize` draws the corpses instead. Never re-sprited as live.
- **Raise** (`RaiseDeadEvent`): the corpse entity is transformed in-place into a living monster.
  `Sync` removes its corpse sprite (it left `state.Corpses`); a new handler spawns its **live**
  sprite — the corpse visual becomes the raised monster cleanly. (Previously a raised monster had
  **no** sprite at all: its live sprite was freed on the original death and corpses were never
  drawn. `RaiseDeadEvent` had no handler — now it does.)

### Removal symmetry (item 3 trace)
`state.Corpses` is mutated in exactly three places; `Sync` reconciles all of them:

| Path | Site | Sprite outcome |
|------|------|----------------|
| Raise (necromancer / scroll) | `RaiseDeadResolver.Raise` → `state.Corpses.Remove` | `Sync` frees corpse sprite; raise handler spawns live sprite |
| Floor change | `TurnController` → `state.Corpses.Clear` | managers rebuilt on the new floor; `Initialize` sees no corpses |
| — | — | — |

**`CorpseState.Consumed`/`Spent` is a terminal *state*, not a world-exit** — a consumed corpse
stays in `state.Corpses`, so its visual **correctly persists** (an inert remains is still there).
Nothing removes a consumed corpse from the world today, so there is no fourth removal path to
clear. (If a future consume mechanic removes it from `state.Corpses`, `Sync` clears it for free.)
A distinct Spent/Consumed visual is a possible future refinement, not part of this ruling.

## Interaction
- **Inspect**: long-press a corpse tile → `ShowFeature("Remains of {OriginalName}", …)`. Ranks
  below live monsters (a living monster on the remains inspects as the monster) and above items.
  **Flag — label:** "Remains of {Name}" is a proposal; if a different register is wanted (e.g.
  "{Name}'s corpse", or a `Remains` category on the inspect card), that's a one-line change.
- **Targetable (past-Sasha)**: the dispel/Spell-Break resolver already resolves targets against
  `state.Monsters` (which includes corpses), so a corpse is a valid target in Logic. The
  presentation half: `InputHandler` SingleTarget resolution now falls back to a corpse carrying a
  `PossessionEffect` (exactly a Warden-possessed past-Sasha host) when no living monster is at the
  tap. Ordinary corpses carry no `PossessionEffect` and stay untargetable, so damage spells can't
  hit remains. Range / LOS / effect validity stay enforced by `ResolveDispel`.

## Guards
- `MidRunCorpseResumeTests.LiveDeath_YieldsCorpseClassifiedVisualIntent` — the live-death seam
  yields the render-classification composite (`state.Corpses` + `CorpseComponent` + no `Fighter` +
  kept `SpeciesTag`) that both presentation halves consume. Complements the resume-seam test.
- `PossessionDispelTests.Dispel_TargetingWardenPossessedCorpse_Resolves` — Spell-Break aimed at a
  Warden-possessed corpse entity resolves (the past-Sasha visibility half).
- The manager itself is Godot code (no Presentation reference in the test project, like
  `EntitySpriteManager`/`ItemSpriteManager`); the widget-geometry smoke harness should gain a
  corpse-sprite-presence line item **if/when** it is built.
