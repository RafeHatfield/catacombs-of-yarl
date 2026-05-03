# The Under-Warden — third pass

*Edited for medium, grounded for longevity, and a few things we didn't know we needed.*

---

## What changed and why

Three categories of update from v2, all in service of fitting the game into what a 2D top-down mobile-first roguelike can actually deliver, and of giving the story beats mechanical teeth that the doc previously only implied.

**Editorial pass for the medium.** Several v2 specifications assumed desktop-style UI affordances (separate minimap screens, off-screen possession management, hidden-floor ending chains that require the player to reconstruct hints across runs). These are fine in a turn-based dungeon crawler on PC and rough on a phone. The story beats survive; the delivery mechanisms have been reshaped to be legible on a portrait viewport with thumbs and a small screen.

**The respawn question, finally answered.** The v2 doc was silent on why Sasha wakes up above the vineyard with the debt still open. The answer is Hollowmark, and it is load-bearing enough that multiple later beats lean on it.

**Past-Sashas as cross-run encounters.** The Paths are where dead people go. Of course the previous Sasha's corpse is still down there. This was a miss in v2. It's now a system.

Other smaller changes flagged inline, including a refinement to the Unshriven geas that gives their politics real tension, and a spell-break-your-former-self beat that ties the possession system to the Under-Warden's bureaucratic reach.

---

## A) One-breath pitch

Unchanged from v2. Retained for reference.

**You're a retired killer who descended into the Paths of the Dead to buy back a soul you owe a debt to, carrying a brass wand that talks in your head and opens portals through your hand — and the dungeon wants to weigh you.** Twenty-five floors of mobile turn-based roguelike that plays exactly like Shattered Pixel Dungeon for the first ninety seconds so your muscle memory works, then quietly becomes smarter. Every monster from the tileset is present and recognizable — orcs, undead, clerics, monsters, all four factions — but each has one specific tactical interaction the game never tells you about, and the person telling you about it is the wand. You can wear an enemy's body if you're willing to leave yours bleeding on the floor. The signature item is a single conscious wand named **Hollowmark** — she does portals, she breaks spells, and she will not shut up. **The Under-Warden** is the title because the thing in charge of the Paths has a job title, and by the end of the run you will have opinions about him.

---

## B) The PC — Sasha of Reven, retired, owes the Lady One

Unchanged from v2 in all substantive detail — culture, profession, patron, voice register, diary samples. The canonical voice rule still stands:

> **He uses the word "work" where another PC would say "combat." He never glorifies a fight. He calls Hollowmark "the wand" in public, by name in private, and "Holl" only when stressed.**

This is the style bible in three sentences. It is protected.

---

## C) Hollowmark — the wand who is the familiar

Unchanged from v2 in mechanical specification: portals, spell-breaking (once per floor, 5-tile range, dispel one active magical effect), overnight identification (one item per three floors), full 17-trigger voice taxonomy, silence rules, verbosity toggles, Marya-memory fragments surfacing across runs.

**Two additions in this pass**, both small, both load-bearing.

**Hollowmark falls silent for the rest of a floor after a Marya memory surfaces.** No banter, no spell-break commentary, nothing. The player pushes through alone, and it lands. One flag, one floor-descent reset. The medium can enforce silence through a mechanic in a way prose cannot.

**Hollowmark is the reason Sasha respawns.** This is covered in its own section below because it affects several other beats, but the one-line version is: wands of conscience are bound to a further span of service, and Hollowmark's binding pulls Sasha back to his body when he dies, at the cost of some of her own remaining span. She doesn't tell him. She can't. Marya knew when she agreed.

---

## C-prime) Why Sasha wakes up again — the Hollowmark binding

**New section in v3.** The v2 doc never gave a diegetic reason for permadeath-with-repeat-runs, and the answer turns out to be the most narratively generative detail in the game.

**The binding.** A wand of conscience is bound by an agreement made at the prior wielder's death. Marya Hollowmark's agreement, seventy years ago, was the usual one: *one further span of service*. What the formal rite didn't spell out, and what most wand-of-conscience traditions have quietly enforced for centuries, is that *a further span of service* means the wielder gets back to the work when the work isn't done. When Sasha dies in the Paths, Hollowmark pulls him out — back to the vineyard, back to his own bed, back to the debt still open — at the cost of some of her own remaining span.

She cannot tell him. The binding prevents it. She knows. Marya knew when she agreed. This is part of why Hollowmark is quieter than usual at the start of a new run, and part of why her between-runs lines have the particular dry weariness they do.

**What this buys the game, in rough order of importance:**

1. **The Swap ending hits differently.** The existing line — *"I always knew, Boss. I never minded."* — now has teeth it didn't in v2. She's been giving up her span for him, run after run, for however many it took. The ending was already devastating. Now it's earned.

2. **The Under-Warden's escalating memos make diegetic sense.** He knows Sasha keeps coming back. He knows something is pulling him back. He has a professional opinion about wands of conscience operating outside their original charter. The memos' formal-complaint escalation is now grounded — he's not just annoyed, he's building a procedural case.

3. **Marya-memory surfacing has a new dimension.** One of the rare late-game Marya fragments drops the fact that this is what Hollowmark has been doing. A player who plays a lot of runs eventually learns, through Hollowmark's own slowly-surfacing memory, that her wielder's life has been costing her. The player knows before Sasha does. This is exactly the kind of long-tail content the fragment catalog is built for.

4. **A mechanical hook if we ever want it.** Hollowmark's span depletes across runs. At some threshold she could start saying less, or spell-break less often, or... *don't build this in v1.* It turns her into a resource bar. Leave it as texture. But know it's there for a future update if the game wants it.

**What this does NOT require engineering-wise.** No visible span meter. No countdown. The binding is pure narrative texture surfaced through dialogue. The cost to engineering is zero. The cost to writing is one more Marya-memory fragment and a handful of Hollowmark lines that hint without stating.

---

## D) The antagonist — the Under-Warden, who is still a clerk

Unchanged from v2 in all substantive detail, with one delivery reshape.

**The floor-24 grief side area is now a mural.** The v2 doc had the Under-Warden's grief — the woman he loved who passed through the Hall eighty years ago and whom he hasn't asked about — discoverable in a side area on floor 24. A side area implies a room with its own small arc. The beat lands just as hard as **a mural in the Weighing**, read by Hollowmark, to which Sasha says nothing. The mural system is already built. The engineering cost drops to zero. The emotional beat is unchanged.

Sample mural text, for voice calibration:

> *A woman's name, in a careful hand, carved between the standard Warden inscriptions. Below it, a date eighty years past. Below that, in smaller script, in the same hand: "I did not ask. I am not asking."*

Hollowmark: *"Boss. Don't read it aloud. He doesn't know we saw."*

Sasha says nothing. The player understands.

---

## D-prime) The orcs — the Unshriven, with the geas properly tensioned

Unchanged from v2 in origin lore, castes, named characters, economy, and diplomatic framing. **One addition to the geas that makes the society dynamic rather than static**, and that gives Sasha a specific reason the orcs want him around.

**The Reincorporation Rite did two things, not one.** First-Warden Mathuren bound the Unshriven into orc-bodies and gave them a duty: hold the Boundary against the deeper undead. She also, quietly, built a second clause into the rite: they could not advance the line. They could hold. They could not push. Four hundred years of holding without gaining is a particular kind of tired, and the Unshriven know it — they don't admit it, because admitting it would mean admitting the duty was a punishment, but every Bone-Orc captain has privately wondered whether the line is as permanent as the charter claims.

**This is why Sasha is interesting to them.** He is Revenese. He is not bound by their geas. He can do the one thing four hundred years of Unshriven soldiers have been forbidden to do: he can push a boundary marker deeper into the Dimhalls. Borrek cannot ask him to do this openly — the geas constrains even what he can request aloud — but a Bone-Orc captain who lets a marker's placement slip in conversation, or who hires Sasha for a job that conveniently takes him past a marker that needs moving, is making a calculation he cannot make himself.

**Mechanical payoff:** the orc-alliance track now has a specific Sasha-can-do-this-they-can't service rendered, which is a stronger motivation for Borrek's eventual knife-gift than "he's friendly after multiple visits." It replaces one of Vesh's generic run-jobs with a push-the-marker job that visibly advances the Unshriven's territorial reach, shifts floor 4-8 encounter composition on subsequent runs in small ways (slightly more orc territory, slightly less undead), and gives Captain Vesh a specific drunken regret to voice when he's too far into the borr-lath: *"We're not supposed to want it. That's the worst part. They built the wanting into us and then told us we couldn't have it."*

**What this does NOT require engineering-wise.** The "territory shift" is purely a YAML tweak to floor-4-8 encounter budgets when a flag is set. One persistence flag. Everything else is dialogue and mural content.

---

## E) The world — the Paths of the Dead, lightly redrawn

Unchanged from v2 in all substantive detail — five regions, aesthetics, resident factions, bosses, signature setting details (House Shrine, Branch of Passage, Contrapasso Rooms).

**Three delivery reshapes in this pass.** Each preserves the story beat; each adjusts how it lands on a phone.

**The Stele of the Lost Word now reveals stairs on the next three floors, not all remaining floors.** Permanent future-stair revelation collapses exploration on floors 18-25, which is where the Weighing and Inner Court are meant to feel oppressive. Three floors is a meaningful boon — one full region's worth of navigational easement — without trivializing the endgame. Hollowmark's line is unchanged and still pays off the Marya-knew-the-language beat: *"It says 'turn left.' Across all of these floors. I think it's a very old joke. The down-stair is always northwest if you turn left first. I don't know why. Marya thought it was funny. I think she was wrong, but she's dead, so I let her have it."*

**The Don't-Look-Back Room now uses portal archways, not the minimap.** On mobile the minimap is a persistent HUD element, not a separate screen the player opens — the v2 "peek breaks reward" trigger is ambiguous. Reshaped: the room is entered through a portal archway, the minimap is force-hidden while inside, and the room has two exits. The far archway gives the blessed item. Re-entering through the entrance archway (literally turning back) gives the cursed one. Same Orpheus gag, a physical gesture the player makes, legible on any screen.

**The Swap ending is now gated through the Things Hael Mentioned catalog, not through hint reconstruction across runs.** The v2 specification — Hael drops hints across multiple runs, player pieces them together — is the most fragile delivery in the whole doc. Players miss hints. Players don't connect them. Reshaped: each Hael conversation that includes a Crypt-of-Wend hint adds an entry to a dedicated catalog page, viewable between runs. When enough entries are collected, an unlock marker appears on the catalog page itself, indicating that Hael will now give the player the Branch-of-Passage instructions on their next encounter. Same mystery, same reward cadence, no chance the thread is lost. This also lets the player see how close they are to the hidden ending, which is the kind of legibility mobile rewards.

---

## E-prime) Past-Sashas — the bodies we left down there

**New system in v3.** The Paths are the afterlife. Every Sasha who has died here is, in some form, still here. The v2 doc did not acknowledge this. It should have.

**Rarity cap:** one prior-Sasha encounter per run, drawn from the most recent qualifying death. Gated on "at least your second run, and your first run ended in one of the qualifying ways." No first-run encounters with your own corpse — that's nonsense to a fresh player.

**Three variants, keyed to how the previous Sasha died:**

**1. The Looted Body (previous death: monster).** Sasha's corpse is where it fell, already picked over by the dungeon. Approaching triggers a loot interaction — the player recovers a random subset of the gear that last-run Sasha was carrying, not all of it. The dungeon took its cut. Hollowmark is dry: *"Tuesday's Sasha. He was overconfident about the acid. You won't be."* No combat. No mystery. Just a ghost-story detail that also happens to be useful.

**2. The Quipping Shade (previous death: self-inflicted tactic — oil-slick fire, possession-neglect, a poison you set yourself).** Translucent, sitting against a wall, not hostile. One line of dialogue, in Sasha's own voice, about how he died. The player hears their own voice speaking back to them — the first time the game uses that trick. *"You'll notice the oil slick. I didn't. Don't be me."* Cannot be looted. Cannot be interacted with further. He's there to make the player laugh ruefully and to remind them the game remembers.

**3. The Possessed Corpse (previous death: the Under-Warden).** This one is different, and it's the beat that ties past-Sashas into the spell-break system in a way that pays for itself several times over.

A Sasha killed by the Under-Warden was *filed*. His corpse was possessed by the Under-Warden's bureaucratic authority — the same mechanic, in a theological sense, as Sasha's own possession ability, exercised in the opposite direction. The body patrols as a Hall Warden-class enforcer, hostile, carrying its old gear.

**Hollowmark's spell-break breaks the possession.** This is a 5-tile-range dispel of an active magical effect — exactly the existing spell-break mechanic, applied to a specific target. When she dispels the possession, the corpse collapses inert, and the player can loot it normally. Hollowmark's line: *"That wasn't you anymore, Boss. You can have the gear back now."*

**Why this is the best beat we've added.** The game has just confirmed, mechanically, that the possessed body was not Sasha. That line and that moment have weight for the Swap ending later — when Sasha contemplates trading his own continued existence for Anik's, the player has already internalized, through a spell the player cast, that a Sasha-body isn't the same as Sasha-the-person. The ending's philosophical premise is grounded in a mechanical interaction the player did themselves.

It's also the only place in the game where the player uses spell-break on a former self. Reviewers notice that kind of thing.

**Engineering cost:** the past-Sasha schema adds a few fields to the cross-run persistence system (floor where last qualifying death occurred, cause of death, gear carried, flag for encountered-this-run). One new encounter type per variant; variants 1 and 2 reuse existing loot/dialogue primitives; variant 3 reuses existing Hall Warden AI with a possession-tag and a spell-break-dispels-me flag. The whole system is hours, not days, according to Claude Code's revised estimates.

---

## F-G) The tactical interactions — twenty-two, lightly retuned

Unchanged from v2 in composition — the master list stands at twenty-two with the orc-specific additions (Iron-Orc patrol diversion, Hollow-Orc Holy vulnerability). Spell-break remains interaction #6(g), one use per floor, separate clock from portals.

**One small addition to the master list from the past-Sashas system:**

**Interaction #23: Dispel a possessed former self.** Spell-break at 5-tile range, applied to a Possessed Corpse encounter (see past-Sashas). Dispels the Under-Warden's possession, collapses the body, permits normal loot. Diegetically one of the most specific uses of spell-break in the game. Discovery-cap neutral — this interaction is only reachable by players who have already died to the Under-Warden at least once, which is self-selecting.

---

## H-I) Possession and Hollowmark's voice

Hollowmark's voice surface is unchanged from v2. Possession gets one delivery reshape.

**Possession now enforces a visible-home-body rule.** The v2 specification had Sasha possessing a host while his home body could be arbitrarily far away on the floor, which is a desktop-tactical-puzzle problem and a mobile-legibility problem. Reshape: possession targets must be within a fixed radius of Sasha's home body (4 tiles is the current proposal, tunable in balance), and if the host moves beyond sight of the home body during possession, possession ends — Hollowmark says so, Sasha snaps back. *"Boss. Too far. Coming out."*

This preserves the positional-tension the v2 doc wanted (leave your body where enemies can reach it, keep Hollowmark kickable) while making the whole interaction readable on a phone screen. The player can always see both bodies. The decisions stay tactical. The UI stays sane.

All other possession mechanics are unchanged: catatonic home body, drain clock, species-knowledge permanent unlock, Hollowmark kickable-positioning, exit triggers on combat/voluntary/host-death.

---

## J-K) Delivery architecture and replay

Unchanged from v2 in all substantive detail. Six text channels, no voice acting, daily seeds, challenge modes, badges, catalog, Hollowmark meta-unlock growing chattier across runs.

**Content bill reality-check:** the v2 claim of ~14,000 words is optimistic; realistic is ~22-28K words across five voices. This is not a scope cut — it is an honest re-estimate of the authoring work, which runs in parallel with engineering and is the real long-pole, not the code. Style bible lands in week 1 across five voices (Sasha, Hollowmark, Under-Warden, Borrek, Vesh/Hael), not two.

**One addition to the catalog system:** the Things Hael Mentioned page (see Endings reshape above), which is the gating mechanism for the Swap ending and which is also a pleasant long-tail object in its own right — the catalog entries are Hael's voice, which is its own register, and players who never pursue the Swap will still enjoy the catalog as Hael-lore.

**One addition to between-runs content:** a small Past-Sashas log, tracking every prior Sasha and how he died, viewable from the main menu. Pure fanservice. Costs two days of writing and a single scene.

---

## L) Endings — three flavors, one structure

Unchanged from v2 in all substantive detail. The Swap ending's hint-delivery is reshaped to use the Things Hael Mentioned catalog (see above); the emotional beats of all six endings (three wins, three losses) are unchanged.

**One line strengthened by the Hollowmark-binding reveal:** the Swap ending's *"I always knew, Boss. I never minded."* now lands on a player who (if they've played enough runs) has already learned that Hollowmark has been giving up her span to bring Sasha back. The line was already devastating. Now it's earned.

---

## M) Five signature moments

Unchanged from v2. Retained for reference.

1. **"The time I beat the troll with an acid trap."** Around floor 7.
2. **"The time I wore a Hall Warden to the altar."** Around floor 13.
3. **"The time Hollowmark told me the orc on the other side of the portal had a cursed axe."** The wand-as-familiar plus signature-item integration.
4. **"The time I drank borr-lath with King Borrek and he gave me his daughter's bloodline news."** The moment that sells the orc society. Now gated on cumulative-meaningful-interactions rather than raw run count (see next section), and specifically reachable through the push-the-marker service (see Unshriven geas above).
5. **"The time I fled from a troll by jumping down a chasm, and Hollowmark screamed the whole way."** Brogue's chasm-dive, flavored by the wand's reaction.

**Candidate sixth moment added by this pass:**

6. **"The time I broke the Under-Warden's grip on my own corpse, and Holl told me it hadn't been me anymore."** The past-Sashas spell-break beat. Not required to hit as a Moment for most players, but reachable by any player who dies to the Under-Warden once and then returns. The game's quietest philosophical beat and one of its best.

---

## M-prime) Named NPC arc reshape — Borrek, Vesh, Hael

**New framing in v3.** The v2 doc gated Borrek's full arc on run count (first wary, third curious, eighth friendly, fifteenth daughter's-bloodline payoff). Fifteen runs is longer than most mobile roguelike players retain. The median Shattered Pixel Dungeon player does not hit fifteen runs. Gating the emotional climax of the orc faction on that threshold loses it for most of the audience.

**Revised gating: cumulative meaningful interactions, not raw run count.**

- **Wary** (default): Borrek is polite but guarded on first audience.
- **Curious** (unlocked by one orc-positive action across any run — tribute paid, Vesh job completed, orc-undead fight sided with orcs, boundary-push service rendered): Borrek is openly interested, shares stories.
- **Allied** (unlocked by three orc-positive actions across any run): Borrek trusts Sasha enough to share the daughter's-bloodline concern. The knife moment becomes reachable.

This is a three-state arc reachable in 2-4 runs for an engaged player, not 15. Same emotional beats, front-loaded so more of the audience actually sees them. Persistence schema drops from "per-run Borrek dialogue variants × 15" to "three state flags plus action-counter."

**Captain Vesh's Revenese-spirit arc reshape:** the v2 specification required a rare drop on floor 8, unclear to the player, found through luck across multiple runs. Reshape: the spirit becomes an item **Hael sells once the player has met Vesh and Hael has an Allied-or-better relationship** with Sasha. Transforms a lottery into a transaction. Preserves the emotional moment entirely — Sasha brings the specific Revenese spirit to Vesh, Vesh pours them each one, Vesh tells his story, Sasha gets his +1 for the run. The *finding* is now deterministic; the *meaning* is still earned.

**Faction reputation reshape:** the v2 specification had a +/- integer score with thresholds at +10 and -10. Reshape to a **three-state enum** (Hostile / Neutral / Allied) with clear trigger conditions: three killed Iron-Orcs unprovoked within a window → Hostile; one completed Borrek or Vesh favor → Allied; defaults to Neutral. Same gameplay outcomes (war-tunnel shortcut at Allied, orc hunt at Hostile), much less tuning burden, glanceable at a glance on a phone HUD.

---

## M-prime-prime) Boss structure reshape

**New framing in v3.** The v2 doc specified five bespoke bosses (Warden of Reven, Tide-Hunger, Hollow King, Weigher of Hearts, Under-Warden). Reshape to **three true bosses and two bespoke non-combat encounters**, which is a substantially more tractable build:

- **Warden of Reven** (floor 3) and **Tide-Hunger** (floor 8) share a boss template — reskinned stats, one signature mechanic each. Warden of Reven tests the player's use of basic portals and ground hazards. Tide-Hunger tests the player's ability to manage multiple threats (it spawns lesser undead). Both are combat bosses.
- **Hollow King** (floor 13) is bespoke. Dialogue-gated, oath-resolution mechanic. Combat is possible but not the intended path.
- **Weigher of Hearts** (floor 19) is bespoke. Scales-mechanic combat — the player places tokens on a pair of scales in the room, and the boss's attacks change based on which side is heavier.
- **The Under-Warden** (floor 25) is bespoke. Audit-not-kill dialogue resolution. Not a combat encounter at all.

Three bespoke endgame sequences plus two template bosses is a substantially different engineering surface than five bespoke bosses, and it pushes the bespoke effort to where it matters — the back half of the run, where the game's identity lives.

---

## N) Scope and sequencing — revised

The v2 claim of "roughly neutral, maybe slightly faster" vs. v1 was wrong. v3's scope is honestly *larger* than v2, not smaller — the past-Sashas system, the Hollowmark binding, the Unshriven geas tension, the catalog-driven Swap gating, the six-moment list, and the mural-based grief delivery all add surface area.

**What offsets the growth:** the delivery reshapes collectively remove a substantial amount of bespoke engineering. Three-state reputation replaces numeric tuning. The floor-24 grief mural replaces a bespoke side area. The portal-archway Don't-Look-Back Room replaces a novel minimap-trigger system. Three-state Borrek gating replaces fifteen-state persistence. Template bosses reduce the bespoke-boss count from five to three. Net engineering surface is probably similar to v2, possibly smaller — Claude Code should re-run numbers when we're ready.

**What doesn't change:** the real long-pole is content authoring, which is ~22-28K words across five voices. This runs in parallel with engineering and is on us working together, which is the workflow we're committing to. Style bible in week 1 on a phone screen — five voices, not two.

**Sequencing principle:** build the cross-run persistence system first, because Borrek, Vesh, Hael, Marya fragments, past-Sashas, Hollowmark's between-runs lines, and the catalog all depend on it. Build Hollowmark's ribbon second, because her voice gates the content authoring of most other systems. Build possession third, because it's the biggest net-new engineering unknown. Everything else slots around those three.

---

## O) Where this sits in the portfolio — unchanged

The Under-Warden remains the **craftsmanship bet**. What this pass preserves is the holistic version of the story — nothing has been cut for expedience. What it adjusts is the delivery, so the version that ships actually works on the platform it's shipping on.

---

## A note on the future

The v2 doc noted that every piece of this proposal converts cleanly if a licensed Brust version ever becomes possible. That is still true, and the additions in v3 don't change it: the Hollowmark binding converts to Spellbreaker's binding, past-Sashas convert to past-Vlads (a thing the novels gesture at but never mechanize), the Unshriven geas converts to whichever Dragaeran-military-afterlife framing Brust prefers, and the Under-Warden's grief mural converts intact. Every serial number remains filed in a way that allows it to be re-engraved.

The game stands on its own if that day never comes. Hollowmark is her own person, Sasha is his own man, the Under-Warden is his own particular kind of sad, and the Unshriven are their own four-hundred-year-old tired.

Sleep well. The Under-Warden's ledger is, as always, open.
