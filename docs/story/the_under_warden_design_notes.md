# The Under-Warden — Design Notes & Viability Study

*Companion to `the_under_warden_v3.md`. Captures the viability study, engine-fit analysis, and gap inventory from the April 2026 investigation session. Written so that returning to this project requires no reconstruction of prior thinking.*

**Last revision:** v3 of the proposal. Supersedes the v2 review.

---

## Status

**Viable. The v3 proposal is genuinely ready to build.** Scope has grown narratively (Hollowmark binding, past-Sashas, Unshriven geas tension, six signature moments) but the delivery reshapes have *reduced* engineering surface, net. The biggest design-to-engine fit issues from v2 are resolved. The one remaining large engineering unknown — possession — has been meaningfully simplified by the 4-tile visibility rule.

When we return to this: read the proposal first, then this document. v3's reshapes are the operative spec; the v2 document is superseded.

---

## Viability verdict

**v3 is materially easier to build than v2**, despite adding content surface. The story is bigger; the engineering is smaller. That is unusual, and it reflects careful editorial work on the proposal side.

What v3 made cheaper:

- **Under-Warden's grief as a floor-24 mural, not a side area.** The mural system is fully built. Engineering drops from a bespoke side room to a single content entry.
- **Don't-Look-Back Room uses portal archways, not minimap toggle.** Portals are fully built. The minimap-trigger-breaks-reward rule is gone.
- **Stele of Lost Word reveals next 3 floors, not all remaining.** Same implementation as a magic-mapping-style boon with a small counter.
- **Swap ending gated on the Things Hael Mentioned catalog, not hint reconstruction.** Catalog UI is one new screen pattern; the hint-chain fragility is gone.
- **Three-state reputation enum (Hostile/Neutral/Allied), not +/-10 numeric score.** Less tuning burden, cleaner HUD, simpler persistence.
- **Three-state Borrek arc reachable in 2–4 runs, not 15.** Content authoring burden for named-NPC variants drops substantially; 3 states × arc length beats 15 run-indexed variants.
- **Vesh's Revenese spirit sold by Hael, not lottery drop.** Deterministic transaction replaces luck-gated moment. Same emotional beat, zero balance tuning.
- **Five bosses → three bespoke + two template.** Warden of Reven and Tide-Hunger share a template; only Hollow King, Weigher, Under-Warden are bespoke. Substantial engineering reduction.

What v3 added:

- **Past-Sashas system (three variants, one per qualifying death cause).** Net-new, but small: variants 1 and 2 reuse existing loot/dialogue primitives, variant 3 reuses the Hall Warden AI with a possession-tag + spell-break-dispels-me flag. Cross-run persistence schema grows by a handful of fields. The beat it buys — spell-breaking the Under-Warden's grip on a former you — is one of the strongest design-mechanic integrations in the whole proposal.
- **Hollowmark binding (respawn lore).** Zero engineering. Pure narrative texture surfaced through existing dialogue channels. One Marya-memory fragment plus a handful of hinting lines.
- **Unshriven geas tension (can't advance the line).** One persistence flag that tweaks floor 4–8 encounter composition after the push-the-marker service is rendered. Trivial engineering; meaningful narrative weight.
- **Hollowmark silence after a Marya memory.** One boolean flag, floor-descent reset. Trivial.

**Net engineering effect: v3 is probably ~15–20% less engineering than v2**, while carrying more narrative surface area. That is a strong result.

**Realistic calendar time at your background-tinkering cadence: 3–6 months door-to-door** with content writing (Claude Chat / ChatGPT-assisted authoring at your voice bar) being the likely long pole, not engineering. iOS submission adds 1–2 weeks at the end. If we hit the average pace we usually do, this probably lands closer to 3–4 months; 5–6 is the honest upper bound that includes genuine playtest iteration, content revision cycles, and a polish month.

---

## Systems breakdown

### Fully built — use as-is or trivial rename

| What the proposal calls for | Engine status | Reference |
|---|---|---|
| Turn-based tactical combat (d20, speed/momentum, crits) | Fully built. | `CombatResolver.cs`, `docs/systems/COMBAT.md` |
| **Wand of Portals** as Hollowmark's core verb | **Fully built.** The cleanest design-to-engine match in the proposal. 3-step state machine, infinite charges, collision displacement all live. | `PortalSystem.cs` |
| Portal archway entry/exit for the Don't-Look-Back Room | Fully built via the existing portal mechanic. No new primitive needed. | `PortalSystem.cs` |
| Player starts with wand-of-portals in backpack | Fully built. | `DungeonFloorBuilder.CreateDefaultPlayer` |
| Four faction buckets (orc/undead/cultist/beast) + hostility matrix + orc-vs-undead emergent combat | Fully built. | `FactionRegistry.cs` |
| Orc roster diversity for Bone/Iron/Hollow castes (7 orc entries) | Fully built. Reskin only. | `docs/systems/MONSTERS.md` |
| Deep-undead roster (zombie, plague_zombie, skeleton, wraith, lich, necromancer, plague_necromancer) | Fully built, 7 entries + casters. | `docs/systems/MONSTERS.md` |
| Trolls (upper + ancient) for Dimhalls | Fully built. | `docs/systems/MONSTERS.md` |
| Ground hazards + traps (acid, bleed, fire, poison gas) for tactical interactions + Contrapasso rooms | Fully built, recently extended. Covers acid-trap-troll beat (Moment #1) directly. | `docs/systems/GROUND_HAZARDS.md`, `config/floor_traps.yaml` |
| Chests (normal/locked/trapped), key items, lockable doors, Branch of Passage equivalent | Fully built. | `ChestComponent.cs`, `LockableComponent.cs`, `KeyItemComponent.cs` |
| **Signposts** (tap-to-read, type-filtered pool, depth-gated) — the Under-Warden memo delivery primitive | Fully built. | `SignpostComponent.cs`, `config/signpost_messages.yaml` |
| **Murals** (discoverable wall lore, once-per-floor uniqueness) — the Under-Warden grief beat, the Marya-memory fragments | Fully built. | `MuralComponent.cs`, `config/murals_inscriptions.yaml`, `MuralTracker.cs` |
| Identification system (per-run shuffled appearances, Scroll of Identify) + piggyback for Hollowmark's overnight ID | Fully built. Hollowmark overnight ID = hook into `IdentifyItem()` on every 3rd floor descent with a player-chosen item. | `IdentificationRegistry.cs` |
| Room archetypes (15 types, constraint-based placement) | Fully built. Reskin for region-specific archetypes. | `PLAN_room_props_archetypes.md` |
| Procedural 25-floor dungeon with depth-keyed ETP budget | Fully built at 25 floors. | `config/level_templates.yaml` |
| Guaranteed item spawns per floor — Stones of Intuition | Fully built for items. | `config/level_templates.yaml` |
| Depth boon system | Fully built. Stele of Lost Word = new boon type. | `BoonTracker.cs` |
| 30+ status effects (Confusion, Slow, Fear, Bleed, Acid, Plague, Entangle, etc.) | Fully built. Covers Iron-Orc-squad-blind and similar tactical interactions. | `docs/systems/STATUS_EFFECTS.md` |
| Status immunities per species | Fully built. Covers wraith/lich immunity spec directly. | `StatusImmunityComponent.cs` |
| Portrait mobile layout, touch input, quick-slot bar, message log | Fully built (7 phases complete). | `PLAN_mobile_layout.md` |
| Scenario harness for balance validation | Fully built. All 23 tactical interactions can be validated before ship. | `DungeonRunHarness.cs` |
| Monster knowledge system (progressive 3-tier species info) — possession's "permanent species knowledge" reward | Fully built. | `MonsterKnowledgeSystem.cs` |

### Partially built or needs reskinning

| Need | What exists | Gap | Complexity (sessions) |
|---|---|---|---|
| Under-Warden memos as a between-floor channel (not environment-placed) | Signpost pool is environment-triggered. Memos are delivered on triggers (run state, specific floors). | New `MemoDeliverySystem` that reads a YAML pool and fires on floor-enter with trigger conditions (floor number, run count, reputation state). Reuses signpost schema. | 1 |
| Hollowmark overnight identification (1 item per 3 floors, player choice) | `IdentifyItem()` exists | Floor-transition hook + mobile prompt UI for item selection. | 1 |
| Hall Wardens, Oathbreakers, Honored Dead, King Bats, ghost, rat, Servants of Old Authority | 28 monsters in roster, none of these specifically | YAML entries + one new Hall Warden AI variant (heavy armor, low speed, grapple-patrol). Rest reuse existing AI types. | 2–3 |
| Boss templates (Warden of Reven, Tide-Hunger) | 28 monsters, no boss-encounter abstraction | Shared template — reskinned stats, one signature mechanic each. Single reusable scaffolding. | 2 |
| Bespoke boss: Hollow King (dialogue-gated oath resolution, combat optional) | No dialogue system yet (see net-new below) | Hollow King encounter reads dialogue state + inventory + oath flags, branches to combat or resolution. | 1–2 (after dialogue system lands) |
| Bespoke boss: Weigher of Hearts (scales-mechanic combat) | Nothing comparable | New encounter type: room-placed scales entity, player places tokens, boss attack pattern reads scale state. | 2 |
| Bespoke boss: Under-Warden (audit, not combat) | No dialogue system yet | Dialogue-gated resolution reading Stones of Intuition inventory + run approach flags + reputation state. | 1–2 (after dialogue system lands) |
| Contrapasso Rooms (Wind/Sludge/Boiling-Floor vaults) | Room archetypes + ground hazards exist | Extend room archetype with a room-effect field (per-turn hazard tick). Wind = directional shove rule (new primitive). | 1–2 |
| Don't-Look-Back Room | Portals exist (see above) | New room archetype + two-archway entry/exit rule + exit-detection flag. | 1 |
| Stele of Lost Word (3-floor stair reveal) | Magic mapping scroll exists | New boon type that pre-reveals stair position on the next N floor generations. | 1 |
| Branch of Passage (consumable key) | `KeyItemComponent` exists | New consumable with "skip-one-lock" flag. | 0.5 |
| Friendly-by-default orcs (Borrek, Vesh, Hael in orc-faction territory) | Faction system has no per-entity override | `NonHostileTag` or per-entity faction override + peaceful-AI branch. Orc patrols ignore tagged NPCs. | 1 |
| Tribute mechanic (drop gold → 4-turn patrol pause) | Gold-as-counter not in engine | Decide gold model (counter vs. inventory). Counter is cheaper. Plus patrol-state timer. | 1 |
| Alarm-bell prop spawning Iron-Orc squad in 8 turns | Interactive props + trap payload timing primitives exist | New interactive prop type + delayed-spawn action. Borrows from `TrapPayloadComponent` timing. | 1 |
| Boundary markers (AI stops pursuit at tile) | No pursue-across-tile rule | Tile-tag or entity-tag + AI pathing check on pursuit. | 1 |
| Diary entries (1 per floor, ~25–30 per run from pool of ~150) | No diary system; signpost pool is similar structurally | New `DiaryEntrySystem` invoked on floor descent, context-aware pool selection. Modal UI card. | 1 |
| Region tile themes (5 regions × distinct aesthetic) | Tileset-switching plan exists (not started); wall autotile + floor composition live | Engineering to wire themes is modest; art authoring is Oryx-asset selection and mapping — your time, not session time. Full Oryx library helps substantially. | 2–3 (engineering) + separate Rafe-hours for art |
| Cross-run persistence (run counter, heirlooms, Marya fragments, Hael catalog, reputation state, past-Sashas, Borrek-arc state, Vesh-arc state) | Nothing persistent | JSON save under user dir. Schema covers: run count, state enums per NPC, action counters, fragment catalog, Hael-hint catalog, past-Sasha records (floor/cause/gear per qualifying run), Borrek-arc state, reputation enum. | 2–3 |
| Death screen with reactive-by-cause epilogues + Hollowmark final line slot | `GameOverScreen.cs` exists, 96 lines | Reskin for death-cause-aware text + Hollowmark voice-line slot + 3 loss epilogues. | 1 |

### Net-new systems

| System | Complexity (sessions) | Notes |
|---|---|---|
| **Possession system** (with v3's 4-tile visibility rule) | **4–6** | Biggest single engineering unknown in the proposal. v3's reshape substantially simplifies the UX: host must stay within 4 tiles of home body, out-of-sight breaks possession automatically. This resolves the worst v2 concern (arbitrary-positioning possession is a mobile-UX problem). Still need: (1) possession targeting mode with range + valid-target rules; (2) `UnattendedBodyState` for the catatonic home body (AI for enemies targeting it, Hollowmark kickable-positioning); (3) host-body state that assumes host stats/abilities; (4) drain clock on home body; (5) exit triggers (voluntary, host death, out-of-sight, home-body death); (6) input re-routing so all player actions target the current controlled entity; (7) HUD showing both bodies and home-body HP; (8) species-knowledge permanent unlock on successful possession. Should be specced as its own plan file before implementation. |
| **Hollowmark familiar ribbon + scheduler** | **3–4** | Italic-purple ribbon (4s persistence, one line at a time), trigger bus (HP thresholds, species-first-sight, traps, idle timers, etc.), line-pool scheduler with once-per-run-per-line guarantee, silence rules (combat gate, shut-up button, Verbose/Tactical/Silent toggle, post-Marya floor-silence flag), mute-between-runs persistence. `ToastLog` and `MessageLogPanel` are not the right surface — this is its own widget. The trigger taxonomy (17 triggers from the v2/v3 spec) is YAML-driven. |
| **NPC dialogue system** | **3–4** | No C# dialogue system today. PoC data model (~80 LOC) is portable. Mobile UI is a fresh design problem: full-screen modal, portrait-oriented, thumb-reachable response buttons, clean dismiss. Schema supports branches, cross-run state conditionals, inventory-gated options. Three NPC arcs wired in (Borrek, Vesh, Hael) use the three-state enum from v3's reshape, which substantially reduces the arc-authoring complexity vs v2's run-indexed variants. |
| **Past-Sashas system** | **2–3** | Three variants. Variant 1 (Looted Body) = new loot-interaction scene reading gear-carried persistence field. Variant 2 (Quipping Shade) = new dialogue-only ambient entity reading cause-of-death field. Variant 3 (Possessed Corpse) = reuses Hall Warden AI + adds `PossessionEffect` status (dispellable by spell-break) + adds possession-tag. Integration with cross-run persistence is a few additional fields (floor, cause, gear, encountered-this-run flag). The spell-break-variant-3 interaction is the payoff — no new systems required, pure composition of existing ones. |
| **Spell-break (generic dispel primitive)** | **1** | `SpellResolver.cs` has `drink_antidote` (specific). Need generic `DispelEffect` spell: single-target within 5 tiles, removes one `IStatusEffect` from target, plus a subset of ground hazards (poison cloud sustained by a caster is a new concept — currently hazards decay on their own clock). Per-floor cooldown tracked on Hollowmark entity state, separate from portal clock. Integrates cleanly with v3's past-Sasha Variant 3 (dispels `PossessionEffect`) and with the Hollow King oath-resolution if that boss uses a dispellable magical binding. **Cursed items dimension still deferred** — blessed/cursed system is out of scope (listed as "Not Yet Built" in `docs/systems/INDEX.md`). Spell-break use cases for v1 are: dispel Iron-Orc shaman rally, dispel lich charging state, dispel Hall Warden grapple, dispel past-Sasha Variant 3 possession, dispel poison-cloud caster. That's enough for the mechanic to feel justified. |
| **Catalog / album UI** | **2** | Three pages: Marya Memory Fragments, Things Hael Mentioned, Past-Sashas Log. Single screen pattern, repeatable. Each entry has metadata (date, place, fragment/hint, cause-of-death). Accessible from main menu between runs. |
| **Faction reputation (three-state enum, orcs only)** | **1** | Hostile / Neutral / Allied. Triggers: 3 killed Iron-Orcs unprovoked (window-based) → Hostile; 1 completed Borrek or Vesh favor → Allied; defaults to Neutral. Persists across runs (or resets per-run — design decision; the proposal is ambiguous, suggest per-run reset unless reputation is meant to stick, in which case persist via cross-run system). Gameplay outcomes: war-tunnel shortcut at Allied, orc hunt at Hostile. |
| **Unshriven geas push-the-marker flag** | **1** | One persistence flag. When set, floor 4–8 encounter composition tweaks (slightly more orc, slightly less undead). Hooked into `DungeonFloorBuilder` encounter-selection step. |
| **Three endings + reactive death epilogues** | **2** | Ending selector reads Stones of Intuition inventory + catalog unlock state + run approach flags. Three win paths (Clean Audit / Theft / Swap) + three loss paths (Kill / Self-Kill / Ledger). Writing is a separate bill. |
| **Crypt of Wend hidden floor + Swap ending unlock path** | **2** | Hidden level template. Unlock gated on Things Hael Mentioned catalog completion (per v3's reshape — much simpler than v2's hint reconstruction). Bespoke funeral-rites scene reusing dialogue system. Swap ending branch wired into endgame. |

**Engineering total: ~40–55 sessions** to feature-complete. At 1–3 hours per session, that's roughly 60–150 hours of us-together focused work.

---

## Content / writing reality check

v3 explicitly accepts the ~22–28K word estimate across five voices (Sasha, Hollowmark, Under-Warden, Borrek, Vesh/Hael). That's the honest number.

With Claude Chat / ChatGPT handling drafting and you as the quality gate at voice, the authoring workflow compresses meaningfully vs. solo writing — but it doesn't collapse. Five voices, with the canonical Sasha rule ("work" not "combat", "the wand" / "Hollowmark" / "Holl" by stress level), plus a dry-Brust-adjacent bureaucratic Under-Warden register, plus three distinct orc voices — the style bible gate in week 1 matters.

**v3 reduces content surface in two places:**

- **Borrek's arc drops from 15 run-indexed variants to 3 state-gated variants.** Meaningful win. An 8-state "progression arc" becomes a 3-state dialogue tree. Possibly 40–50% of the Borrek-specific authoring burden disappears.
- **Vesh's Revenese-spirit arc becomes deterministic (Hael transaction, not lottery drop).** No writing reduction, but the scene is now guaranteed-reachable, so the writing effort isn't wasted on players who never stumble on the item.

**v3 adds content surface in three places:**

- **Past-Sashas:** three variants × ~5–10 lines each = ~500 words, plus the Past-Sashas Log in the catalog (one entry per qualifying death, Hollowmark-voiced = pool of ~50 lines for different death causes). Call it ~1,500 words additional.
- **Hollowmark binding:** one late-game Marya fragment revealing the mechanism + handful of hint lines across Hollowmark's regular pool. ~500 words additional.
- **Unshriven geas tension:** Vesh's drunken regret lines, Borrek's geas-strained dialogue, push-the-marker job script. ~1,000 words additional.

Net content change vs. v2: possibly neutral to slightly up. Call it ~24–30K words for v3.

**Rafe-hours for content:** at Chat-assisted pace with you as editor and voice gate, plausibly 40–80 hours of focused writing/revision across the project. This is the real long pole and scales with your available tinkering cadence.

---

## Timeline assessment

In the units that actually apply to us:

| Workstream | Sessions (us-together) | Rafe-hours (not session-based) |
|---|---|---|
| **Cross-run persistence system** (build first, per v3's sequencing principle) | 2–3 | — |
| **Hollowmark ribbon + scheduler + silence rules** (build second) | 3–4 | — |
| **Possession system** (build third) | 4–6 | — |
| **NPC dialogue system + 3 NPC arcs wired** | 3–4 | content in parallel |
| Spell-break | 1 | — |
| Three-state reputation + hooks | 1 | — |
| Past-Sashas (3 variants) | 2–3 | — |
| Catalog UI (3 pages) | 2 | — |
| Memo delivery channel | 1 | — |
| Diary entry system | 1 | — |
| Don't-Look-Back, Stele, Branch, Contrapasso rooms | 3–4 | — |
| Template bosses (Warden of Reven, Tide-Hunger) | 2 | — |
| Bespoke bosses (Hollow King, Weigher, Under-Warden) | 4–6 | — |
| New monsters + Hall Warden AI variant | 2–3 | — |
| Unshriven geas flag + encounter-composition hook | 1 | — |
| Three endings + death epilogues | 2 | content in parallel |
| Crypt of Wend + Swap unlock path | 2 | content in parallel |
| Region tile themes (5 regions) engineering | 2–3 | 10–20 hours Oryx selection / mapping |
| Balance pass + 23-interaction harness coverage | 3–5 | 5–10 hours playtest judgment |
| Death screen + voice-line integration | 1 | — |
| **Engineering subtotal** | **~40–55 sessions** | — |
| **Content authoring** (24–30K words, 5 voices, Chat/GPT-assisted, Rafe as voice gate) | — | 40–80 hours |
| **Style bible week 1** | — | 4–6 hours |
| **Playtest + feel iteration** | — | 10–20 hours |
| **App Store submission + trailer + store page** | — | 10–15 hours |

**Engineering: ~40–55 sessions.** At your 2–3 sessions/week background-tinkering cadence, that's **13–27 weeks calendar** on the engineering side.

**Rafe-hours total: ~65–120 hours** of non-session work, running in parallel. At whatever pace your day-job leaves room for.

**Wall-clock: iOS review (1–2 weeks) + occasional playtest cycle buffers.**

**Realistic door-to-door: 3–6 months calendar time.** Lower bound if engineering stays ahead of content and we get clean runs of sessions without long gaps. Upper bound if content authoring or art selection slows (both are your-time-dependent) or if possession reveals unknowns that need more iteration.

Where are the risks, in priority order:

1. **Possession is still the biggest engineering unknown.** v3's 4-tile visibility rule is a clean simplification and substantially de-risks the UX, but the input-routing + home-body-AI + drain-clock + HUD surface area is real. Spec it as a dedicated plan file (`plan_possession_system.md`) before starting. Budget: 4–6 sessions plus 1 session of spec work.
2. **Content authoring at voice quality.** The real long-pole. Chat/GPT assistance compresses this, but five voices with the Sasha canonical rule still demands your editorial time. Plan the style bible week 1, gate content against it.
3. **Art/tile authoring across 5 regions.** Your Oryx library coverage helps substantially. The engineering to wire themes is modest; the art decisions are your hours. Budget the tile selection separately from engineering sessions.
4. **NPC dialogue system is a blocker for three downstream systems** (Hollow King, Under-Warden, NPC arcs). Sequence it early so those aren't waiting.
5. **Hollow King's dialogue-gated oath resolution + Weigher's scales mechanic are bespoke.** The scaffolding reduces the surface (three bespoke instead of five), but these two are genuine new encounter types that need more than YAML.

---

## Red flags

Most of the v2 red flags are resolved by v3. Listing the remaining ones and flagging which v2 concerns v3 addressed.

**Resolved by v3:**

- v2's scope-neutrality claim was wrong. v3 explicitly acknowledges it and provides a more honest accounting. ✓
- v2 treated possession as "unchanged from v1" without spec. v3 adds the 4-tile visibility rule, which is the load-bearing mobile-UX fix. Still needs a plan file, but the ambiguity is gone. ✓
- v2's fifteen-run Borrek arc lost most of the audience. v3's three-state enum lands in 2–4 runs. ✓
- v2's "reconstruct hints across runs" Swap ending was fragile. v3's catalog-driven unlock is robust. ✓
- v2's Don't-Look-Back minimap-break was ambiguous on mobile. v3's portal-archway entry/exit is legible. ✓
- v2's numeric +/- faction reputation needed extensive tuning. v3's three-state enum is glanceable. ✓
- v2's bespoke side area for Under-Warden grief. v3's mural replacement uses an already-built system. ✓
- v2's five-bespoke-boss count. v3's three-bespoke + two-template reshape cuts the boss engineering meaningfully. ✓
- v2's assumption that cross-run state was lightweight. v3 explicitly flags it as the first-build system, which is the right sequencing call. ✓
- v2's content estimate of 14K words. v3 accepts the 22–28K reality (24–30K with the v3 additions). ✓

**Still live in v3:**

1. **Possession still needs a dedicated spec.** v3 resolved the UX question (4-tile visibility) but the input-routing / home-body-AI / drain-clock engineering surface is still the largest net-new system in the proposal. Before starting possession, write `plan_possession_system.md` with: targeting rules, state machine, AI for catatonic body, drain formula, exit conditions, HUD layout, Hollowmark kickable-positioning rules, species-knowledge integration.
2. **Hollowmark ribbon UI is still net-new.** v3 doesn't reshape this; the v2 assumption that a delivery mechanism exists is still wrong (`ToastLog` is not the right surface). 3–4 sessions.
3. **Cursed items still deferred, narrowing spell-break's use case list.** v3's past-Sasha Variant 3 integration gives spell-break a strong standalone justification, so this is less of a concern — the mechanic doesn't need the cursed-item dimension to feel meaningful. But the v2/v3 spec lists "dispel a curse from one of your own equipped items" as a spell-break use case, and that one specific use case doesn't work without the cursed-item system.
4. **SPD 90-second onboarding feel is still a polish claim.** Without audio (not in scope), matching SPD's specific game feel is partly impossible. The tap-targets, animation timing, and UI density are reachable; the audio feedback layer is not. Worth either expanding scope to include SFX (~3–5 sessions + sound-asset curation) or softening the claim.
5. **"Audit the Under-Warden" dialogue-driven endgame depends on NPC dialogue landing first.** Not a concern per se — the sequencing is straightforward — just worth noting that the most important story beat in the game is downstream of a system that isn't yet built.
6. **Three NPC arcs + past-Sashas + reputation + Borrek/Vesh/Hael state all write into the same persistence system.** Schema design on day 1 matters. The cross-run persistence schema should be specced with all consumers in mind, not grown field-by-field. One dedicated session to design the schema before implementation pays for itself.
7. **Possession targeting + spell-break + past-Sasha Variant 3 all need to reference possession-as-a-dispellable-status-effect.** Design decision: add a new `PossessionEffect` to the status effect system, applied to host bodies (whether by player or by Under-Warden). Spell-break becomes a generic dispel that removes any `IStatusEffect`, and the past-Sasha Variant 3 beat falls out naturally. Worth making this explicit before implementing any of the three.
8. **Tile theme art is still your-time-bottlenecked.** v3 doesn't change this. Oryx library coverage helps substantially, but five distinct region aesthetics still require selection, mapping, and placement decisions. Plan the tile selection workflow separately from engineering sessions.

---

## Overall verdict

**Build it.** v3 is a build-ready proposal.

The v2 review concluded "viable as the portfolio-anchor slot, but misscoped." v3 resolved nearly every scope concern through editorial work on the proposal itself — not by cutting content, but by reshaping delivery. That is the harder and better version of the fix. The story is intact. The engineering surface is smaller. The content bill is honest.

What's strong about v3:

- **The Hollowmark binding is load-bearing narrative that costs zero engineering.** This is the kind of writing that earns its place — it makes three other beats hit harder (Swap ending, Under-Warden memo escalation, Marya-memory surfacing).
- **Past-Sashas, and specifically Variant 3, is one of the best design-mechanic integrations in the proposal.** The player spell-breaking the Under-Warden's possession of a former-self body is the game's philosophical premise grounded in a mechanical interaction. That's hard to author intentionally and v3 landed it.
- **The Unshriven geas tension** gives Borrek's eventual trust a specific thing to reward, instead of raw run-count. Replaces a lottery with a service rendered. Better for the player, better for the writing.
- **Sequencing principle (persistence → Hollowmark ribbon → possession, then everything else).** This is the right build order. Each system unblocks multiple downstream consumers.

Recommendations, in order of priority:

1. **Spec possession as its own plan file** (`plan_possession_system.md`) before any other system. It's the largest net-new engineering unknown and deserves a dedicated design pass.
2. **Spec the cross-run persistence schema on day 1** with all consumers in view: reputation, Borrek/Vesh/Hael state, Marya fragments, Hael catalog, past-Sashas records, run counter, Unshriven geas flag, heirloom flags, catalog unlock markers, mute-between-runs state. Design once, grow never.
3. **Lock the style bible in week 1 on a phone screen.** Five voices. One sample scene per voice, reviewed on device, before content writing accelerates.
4. **Treat the possession-as-status-effect design decision as a cross-system contract.** Possession, spell-break, and past-Sasha Variant 3 all reference it. Get the contract right before any of the three lands.
5. **Keep cursed items out of v1.** Spell-break doesn't need them to be meaningful, and the design surface of curses is its own system.
6. **Consider whether minimal SFX enters v1 scope.** If it does, budget 3–5 sessions + your time for asset curation from existing free/paid libraries. If it doesn't, soften the SPD-feel claim in marketing copy.

This is the right project. v3 is a build-ready proposal. At your tinkering cadence, we're looking at **3–6 months door-to-door**, with content authoring at voice quality and tile selection being the likely long poles, not engineering.

---

## Files for reference

| File | What it contains |
|---|---|
| `docs/story/the_under_warden_v3.md` | The full proposal (this document's companion) — operative spec |
| `docs/story/the_under_warden_v2.md` | v2 proposal — superseded by v3 |
| `docs/systems/INDEX.md` | Engine implementation-status summary |
| `src/Logic/Core/PortalSystem.cs` | Full 3-step Wand of Portals state machine — Hollowmark's core verb + Don't-Look-Back archway mechanism |
| `src/Logic/AI/FactionRegistry.cs` | Static faction hostility matrix — orc/undead/cultist/beast |
| `src/Logic/ECS/SignpostComponent.cs`, `MuralComponent.cs` | Text delivery surfaces (signposts for memos; murals for Under-Warden grief + Marya fragments) |
| `src/Logic/ECS/ChestComponent.cs`, `LockableComponent.cs`, `KeyItemComponent.cs` | Locked-door + key + chest primitives |
| `src/Logic/Content/IdentificationRegistry.cs` | Identification — Hollowmark overnight ID hook |
| `src/Logic/Combat/SpellResolver.cs` | Spell dispatch — home for the new Dispel spell |
| `src/Presentation/UI/MainMenuPanel.cs`, `GameOverScreen.cs` | Starting points for catalog UI + death epilogues |
| `src/Presentation/UI/ToastLog.cs`, `MessageLogPanel.cs` | Existing text surfaces — *not* the right target for Hollowmark; reference only |
| `config/level_templates.yaml` | Guaranteed-spawn schema for Stones of Intuition |
| `config/signpost_messages.yaml`, `murals_inscriptions.yaml` | Authoring pool formats to mirror for memos/diary/mural fragments |
| `tasks/plans/INDEX.md` | Master plan index — confirms cross-run persistence, NPC dialogue, possession, familiar UI, reputation, spell-break are all un-planned |
