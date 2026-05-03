# The Tax Collector of Drown's Gate — Design Notes & Analysis

*Companion to `the_tax_collector_proposal.md`. Captures the viability study, design decisions, and technical findings from the April 2026 investigation session. Written so that returning to this project requires no reconstruction of prior thinking.*

---

## Status

**Viable. Not yet committed.** This is the first storyline investigated for the engine-shakedown release. At least one alternative storyline is under active consideration. The decision about which storyline to build first has not been made.

When we return to this: read the proposal first, then this document. Everything worth knowing about the gap between "what the proposal says" and "what's actually true of the engine" lives here.

---

## Viability verdict

The proposal's "90% engine reuse" claim holds up at the system level. Combat, factions, signpost/memo system, consumables, procgen, chests, inventory, identification, FOV — all directly applicable. The 10% that's genuinely new is well-scoped and mostly concentrated in two areas: currency/revenue tracking and the NPC dialogue system (not yet ported from the Python PoC).

**Estimated timeline: 3.5–4.5 months to feature-complete. 5 months door-to-door including App Store submission/review slack.** The proposal's 3–4 month estimate is honest for the systems work; content quality and one new economy balance loop absorb the slack.

The writing is the real constraint. Voice quality is the bar, not engineering complexity.

---

## Systems breakdown

### Fully built — use as-is or trivial rename

| What the proposal calls for | Engine status |
|---|---|
| Combat system | Fully built. D&D-style D20, speed/momentum, crits. Unchanged. |
| Faction hostility (Residents/Preserved/Crown/Unpreserved) | Fully built. Orc, undead, cleric, beast factions + hostility matrix live. |
| Signpost/memo tap-to-read → "salt-paper memos" | Fully built. `SignpostComponent`, `MuralComponent`, message registries, tap-to-read UX. This IS the memo system, renamed. |
| Named rooms (Morrag's tea shop, Hennick's office) | Room archetype system + `RoomPropPlacer` covers this. New archetypes = new YAML entries. |
| Consumables reskin (potions → tonics, scrolls → forms) | Fully built. 14 potions, 30+ scrolls/wands, identification system. Rename only. |
| Procedural dungeon, 10 floors | Fully built for 25 floors. 10-floor subset = new `level_templates` entries + custom difficulty curve (see below). |
| Monster roster (orcs, undead, ghouls, skeletons, zombies) | Fully built. 28 monsters covering all faction types the proposal names. |
| Chests and locked variants | Fully built. `ChestComponent`, `LockableComponent`, `KeyItemComponent`. |
| Death screen (basis of Second Attempt Clause reskin) | Exists. `GameOverScreen.cs` (~97 lines). Reskin only. |
| Guaranteed item spawns at specific depths | Works today for items via `guaranteed_spawns:` in `level_templates.yaml`. |

### Partially built or needs reskinning

| Need | What exists | Gap | Complexity |
|---|---|---|---|
| Salt-paper glow visual | Signpost/mural sprites exist | Shader or modulate tint on unread items | S |
| Readable items in inventory (counter-forms, expense reports) | Inventory + identification live; no "read text" action | Add `ReadableComponent` + "Read" action to long-press action sheet | S–M |
| Guaranteed NPC spawns at specific depths | Works for items; schema doesn't support named monsters | Extend guaranteed_spawns schema + loader + floor placement | M |
| Friendly-by-default orcs (Morrag, Gurm) | Faction system sets hostility; no per-entity override | `NonHostileTag` or per-entity faction override + peaceful AI branch | M |
| Between-run hub (Ministry office) | Main menu exists; no persistent meta-state between runs | New scene + run-counter + one NPC stub + persistent save | M |
| Heirlooms across runs | No cross-run progression | Persistent unlock flags file; starting inventory selection | S–M |
| Ending selector on revenue total | Basic single-outcome game-over screen | Epilogue text chooser based on revenue value; four epilogues | S |
| Named monster variants (Gurm, Petra, Hennick, etc.) | Monster definitions are YAML; named variants are new entries | One YAML entry + unique spawn wiring + dialogue hookup per NPC (×7) | S per NPC |

### Net-new systems needed

| System | Complexity | Notes |
|---|---|---|
| **Currency / revenue tracking** | M | Coin sprites exist; a gold-value system does not. Decision needed (see below): counter-only vs. inventory item. Counter-only is the right call for a casual game. |
| **NPC dialogue system** | M–L | Biggest underestimate in the proposal. Nothing is ported from the PoC to C#. No `DialogueComponent`, no dialogue UI, no YAML loader. The PoC data model (~80 LOC) is portable; the UI is a fresh mobile design problem. See dialogue section below. |
| **Second Attempt Clause death flow** | S | Comedy diary entry on death + attempt counter. Reskin of existing GameOverScreen. |
| **Four-ending epilogue selector** | S | Switch on revenue value + epilogue text YAML. |
| **Peaceful NPC interaction (bump → dialogue)** | S (with faction override) / M (without) | Depends on friendly-faction work. |
| **Simple persistent save between runs** | S–M | Run counter, heirloom flags, last revenue total. JSON under user dir. |
| **Named room archetypes** | S–M | Room archetype system exists. 4–6 new named archetypes with fixed props + guaranteed NPC. |
| **Crown Revenue HUD element** | XS | HUD.cs has HP + depth. Add a third label. |
| **RunApproachFlags on GameState** | XS | Three booleans written during run, read only at epilogue. See replayability section. |

---

## Design decisions locked in discussion

### Gold as counter-only (not inventory item)

**Decision:** Coins are a counter-only resource. Pick up = +N to the revenue total, no inventory slot consumed. This matches the casual fantasy and avoids inventory clutter.

### Revenue target: range-based, not exact

**Decision:** The 13,612 "Audit Honorable" secret ending fires on a range (e.g., 13,500–13,999), not on an exact number. The epilogue text reads "within the Ministry's acceptable variance" — the precise number becomes narrative flavor, not a mechanical requirement. Cheaper than a guaranteed topup mechanic and more forgiving to RNG.

### Replayability: the middle path

**Decision:** Cross-run Drown recognition via run counter + three in-run approach flags feeding the modifier paragraph slot + Morr's smuggling arc run-1-only (no cross-run unlock). No persistent meta-progression beyond these.

**Why:** Cheapest option that honestly earns "replayable" on the store page. Anything richer (cross-run Morr unlocks, escalating Drown animosity) is roguelike-scale meta-progression — a different game. Anything thinner is the one-evening game, and the marketing has to match.

### Three approach flags

**Decision:** Three binary flags tracked within a single run, read only at epilogue selection:

1. **Spared friendly residents** — did Wel fight Morrag, Gurm, Petra, or walk past them?
2. **Filed Petra's library book** — small acts of Ministry procedural integrity
3. **Robbed Deacon Morr / took the smuggling cut** — the one real moral compromise available

These map to three distinct modifier paragraphs per revenue tier. They are **writing variance, not systems variance**. The only place they touch systems is epilogue selection at run-end. This boundary is firm — approach flags do not branch combat, routes, or revenue during Month 1.

**Implementation:** A `RunApproachFlags` struct on `GameState` with three booleans, written at the relevant moments (Morrag encounter resolution, Petra library book interaction, Morr smuggling branch), read only at epilogue selection. This is the full systems footprint.

### Epilogue structure: slot model, closing paragraph

**Decision:** 4 base epilogues (one per revenue tier) + 3–5 modifier paragraphs keyed to approach flags = 9 writing units, not 32.

- Base epilogue opens with the Ministry's framing of the revenue tier
- Modifier paragraph is always the **closing paragraph** — position-stable across all epilogues
- Moral weight lands at the close; Wel's diary voice naturally ends on a dry note; Drown's memos end on a quiet one; epilogues should match that cadence

**Gate:** Write one complete example (Honorable + clean-hands) before the spec locks, to confirm the shape feels right before 9 writing units commit to it.

### Deacon Morr as the only quest-giver Assessor

**Decision:** Tallis (Floor 5) and Ennel (Floor 7) are flavor-only — three-exchange dialogue trees with no mechanical consequences. Morr (Floor 9) is the only Assessor whose scene affects revenue or endings. Morr becomes memorable precisely because he's the only one who acts on the world.

### Combat difficulty: both axes live

**Decision:** Combat cannot be trivial. Combat lethality is the enforcement mechanism that makes revenue decisions matter. Without real stakes per encounter, routing decisions have nothing to push against.

**Design target for Floor 6:** A greedy player gets killed sometimes (not just gets hurt) while pursuing revenue. A careful player survives but watches their revenue target slip. The interesting decisions happen when both pressures conflict — the optional room has good loot and a hard fight; the safe path gets you to the stairs alive but under-funded.

### 10-floor difficulty curve: full compression, not truncation

**Decision:** B1–B2 truncation is wrong — that's the "combat as flavor" version. The correct approach is the full B1 through B3/B4 difficulty curve compressed into 10 floors. Floor 6 in a 10-floor game is psychologically and mechanically where Floor 15 sits in the 25-floor version, but the player's gear won't match. This requires a custom difficulty curve with new `level_templates.yaml` entries and a balance pass — not a truncation of the existing 25-floor curve.

---

## Technical findings

### Dialogue system: not ported, mobile-native UI required

The PoC has a complete dialogue system (`npc_dialogue.py`, `npc_dialogue_screen.py`, YAML loaders). **None of it is ported to C#.** The C# build has no `DialogueComponent`, no dialogue UI panel, no dialogue YAML loader.

**What to port:** The PoC's data model (dialogue nodes, branch options, per-run flags) — ~80 LOC. Port faithfully.

**What to redesign from scratch:** The UI. The PoC was keyboard-driven. Mobile requires:
- Full-screen or near-full-screen modal (owns the whole screen, dismisses cleanly back to game state)
- Portrait-oriented, thumb-reachable response buttons
- No hover states
- Must coexist cleanly with the existing mobile HUD layout (portrait stack is tight)

**Estimated cost:** 2–3 weeks. Not 1 week. This is the proposal's biggest underestimate.

**Dialogue modal input state test list** (write before implementation, not after):
- Clean dismiss on tap-outside
- Input blocked during open/close animation
- Queued input discarded (not deferred) on close
- No ghost states on mid-animation interrupt
- Full-screen modal doesn't leak into game input layer on dismiss

### Bot persona port: translation work is bounded

The C# `BotBrain` is a static class implementing a hardcoded "balanced" persona (`BotConfig.PanicThreshold`, `BotConfig.HealThreshold` are constants). **There is no persona system in C#.**

The PoC's 6-parameter `BotPersonaConfig` (frozen dataclass) translates cleanly to a C# record. Main work:
1. Parameterize the hardcoded thresholds
2. Add `avoid_combat` decision branch — **not present in C#**, needed for "careful player" test
3. Add `prefer_stairs` decision branch — **not present in C#**, needed for routing tests
4. Add `revenue_priority` parameter — **not in the PoC** (currency didn't exist there). This is the new parameter that makes a greedy-revenue bot chase coin pickups rather than just potions. New design, not port work.

**Estimated cost:** 1–2 days. The data model port is clean; `avoid_combat` and `prefer_stairs` branches are the substantive addition.

### Revenue harness: needs bot personas + new scenario YAMLs

The current harness measures H_PM, H_MP, Death%. It cannot validate the dual-axis design target ("greedy bot gets killed sometimes, careful bot survives but under revenue pressure"). The revenue harness needs:
- Revenue-per-floor, revenue-at-death, revenue-at-Floor-10 exported per run
- Greedy-revenue bot persona (high `revenue_priority`, low `retreat_hp_threshold`)
- Cautious bot persona (`avoid_combat: true`, standard thresholds)
- New 10-floor scenario YAML files for Drown's Gate (the 25-floor scenarios don't transfer)

**Bot persona port and revenue harness are the same workstream, not two independent ones.**

### Schema-first workflow

**Critical sequencing constraint:** The memo/dialogue YAML schema must be specced before any content writing begins. Content written against a schemaless YAML is content that gets touched twice when the schema is added in Month 2.

**Schema needs:**
- Conditional content support: `run_count_gte: 2` for Drown's cross-run recognition variants
- Approach-flag keys: `if_flag: spared_residents` etc. for modifier paragraph selection
- **Provenance metadata per entry:** `author_voice` (Wel diary / Drown memo / Ministry form / NPC dialogue / ambient signpost), `location`, `trigger_conditions`, `word_count`

The provenance metadata is what makes the Month 3 voice-consistency pass tractable. Filtering "show me all Drown memos in order" becomes a YAML query with metadata; without it, it's a grep exercise across 60 files.

---

## Sequencing (if/when this moves to build)

**Week 1 gate (non-negotiable):** Voice on a phone screen, not in a markdown file. Comic prose that lands in a 4-inch column of iPhone text is a different craft than comic prose on a laptop — line breaks, pacing, word choice all shift. The engineering to get one memo on device (signpost reskin + YAML entry) is a Day 3 task. The writing to get a *good* memo isn't.

**Actual Week 1 sequence:**
1. Day 1–2: Style bible session (establish Wel's voice register, Drown's voice register, sample item flavor lines)
2. Day 3–4: Spec both YAML schemas (memo schema with provenance metadata + dialogue schema with conditional content support)
3. Day 4–5: First 5 memos drafted and edited against the style bible
4. Day 5: On-device integration (signpost reskin, drop memos into YAML, run on iPhone)
5. Day 6–7: External reader feedback — "is this funny / does the tone hold"

**Milestone 1 passes when:** A stranger reads 5 memos on a phone and laughs.

**Month 1–4 shape:**
- Month 1: Content writing (~10,000 words polished comic prose, not 7,000 — NPC dialogue trees, item flavor, and endings add ~3,000)
- Month 2: Systems (dialogue system is the swing variable — port data model, design mobile UI from scratch)
- Month 3: Balance + polish (revenue economy needs new target bands; add revenue/floor tracking to harness before tuning, not during)
- Month 4: Release prep (store page, trailer, submission — add 2–3 weeks App Store review slack → 5 months door-to-door)

**Parallel workstreams once both schemas are locked:**
- Voice bible + content writing
- Harness scaffold (bot persona port + 10-floor scenario YAMLs + revenue metrics)

These are independent and can run simultaneously.

---

## Open questions (undecided as of session end)

- **Which storyline ships first?** Drown's Gate is viable. At least one alternative is under active investigation. Decision pending.
- **Pricing model:** "Free engine-shakedown" fits a one-evening game well. The middle-path replayability decision moves this closer to "replayable roguelike" territory, which could support a small price point. Decide consciously before store page copy is written.
- **Name for shipping:** Proposal offers four options — "The Tax Collector of Drown's Gate," "Drown's Gate," "Fort Drown," "Arrears." "Arrears" compresses best on store pages. Decide by end of Month 1 since it cascades into store research, trailer script, and splash art.
- **Audio:** No audio system exists in the C# build. If audio is in-scope for this release, it needs a line item in Month 4 or it eats store-page/trailer time.
- **Drown's Floor 10 encounter:** The "reconciliation of ledgers" is a bespoke scene type — not combat. Roughly the effort of one boss fight, implemented in UI/narrative rather than combat mechanics. Budget it explicitly.

---

## Files for reference

| File | What it contains |
|---|---|
| `docs/story/the_tax_collector_proposal.md` | The full proposal (this document's companion) |
| `src/Logic/Balance/BotBrain.cs` | C# bot — single "balanced" persona, hardcoded constants |
| `src/Presentation/UI/GameOverScreen.cs` | Death/victory screen to reskin as Second Attempt Clause |
| `src/Presentation/UI/HUD.cs` | Where the Crown Revenue label goes |
| `config/level_templates.yaml` | Guaranteed spawns schema (items work; monsters need extension) |
| `config/signpost_messages.yaml` | The memo system's direct equivalent in the current engine |
| `~/development/rlike/docs/BOT_PERSONAS.md` | PoC bot persona parameter definitions |
| `~/development/rlike/components/npc_dialogue.py` | PoC dialogue data model to port |
| `~/development/rlike/config/entity_dialogue.yaml` | PoC dialogue content for reference |
| `~/development/rlike/docs/planning/VICTORY_CONDITION_PHASES.md` | PoC victory/ending system (different from this proposal, but useful reference) |
