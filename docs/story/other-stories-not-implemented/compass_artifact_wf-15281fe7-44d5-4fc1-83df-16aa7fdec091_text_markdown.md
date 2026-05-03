# The Under-Warden: a love letter to roguelikes, written in Vlad's voice

## A) One-breath pitch

**You're a retired Eastern assassin who descended into the Paths of the Dead to buy back a soul you owe a debt to, carrying a jhereg-egg charm that talks in your head and a wand of portals with three charges — and the dungeon wants to weigh you.** It's a twenty-five-floor mobile roguelike that plays exactly like Shattered Pixel Dungeon for the first ninety seconds so your muscle memory works, and then quietly becomes smarter. Every monster in the Oryx tileset is present and recognizable — orcs, zombies, skeletons, trolls, bats, clerics — but each one has one specific interaction the game never tells you about, and the person telling you about it is the lizard in your amulet. You can possess an enemy's body if you're willing to leave yours bleeding out on the floor. There is no pet that follows you. There is, instead, a voice. The title is **The Under-Warden**, because the thing in charge of the Paths has a job title, and by the end of the run you will have opinions about him.

---

## B) The PC — Sasha of Reven, retired, owes Verra one

**Name:** Sasha of Reven. Human, Eastern, forty-two, small, dark-haired, walks with a favored right knee. Retired four years. Retirement did not take.

**Profession:** Assassin, though he prefers *specialist* on the rare occasions he prefers anything. He does not describe himself as an adventurer. Adventurers are the people he used to be hired to clean up after.

**The reason he descended:** He owes his patron goddess — call her **Verra** — a soul. Specifically, he owes her *Anik's* soul, a woman who died because Sasha took a contract he should have turned down. Verra offered him a trade: descend the Paths, find Anik before she reaches the **Hall of Judgment**, bring her back. In exchange, Sasha's ledger with her closes. He knows she's lying about half of it. He went anyway.

**Voice register:** Vlad Taltos at ~70% — short declaratives, dry kickers, fear acknowledged sideways, gear treated affectionately, debts tracked. Rucks at ~15% — cadence. Lilarcor at ~10% — self-aware about being the sort of person who narrates his own dungeon crawl into a logbook. Morte at ~5% — gallows humor on death, only on death. **He never flirts with NPCs. He never glorifies a fight. He uses the word "work" where another PC would say "combat."**

**Five diary samples** (reach for these; they set the tone for every piece of text in the game):

> **Entry 1, Floor 1.** *The stairs don't end; they just stop pretending to. Loiosh says this is a bad idea. Noted. Took the first step anyway. The air smells like old coins. Down we go.*

> **Entry 4, Floor 3, after a near miss.** *It was closer than I like. Bigger than I like, too. The thing swung, I wasn't there, I was, I wasn't, and then it was on the floor and I was mostly upright. Had to be done. Need new boots. These ones have troll on them.*

> **Entry 7, Floor 6, after a bargain.** *She wanted her bones carried one floor up and set in the right alcove. I said yes. She said her name in a language I didn't know and gave me a key. One debt paid, one owed, call it even. I hate this place a little less.*

> **Entry 11, Floor 10, after finding the ring.** *Picked up a ring. Shouldn't have. The finger went cold, then the hand, then something in my chest took an interest. Spellbreaker buzzed, which was comforting; Loiosh swore, which was less so. Kept the ring. Going to regret it. Aware of this.*

> **Entry 19, Floor 17, after possession.** *Wore an orc for four turns. Worst thing I've ever done, by which I mean the fourth or fifth. You forget your own arms have the reach you're used to. When I climbed out he looked at me like he knew. Then I stabbed him with his own cleaver. Fair's fair.*

Sasha's diary is the only narrative delivery vehicle in the game outside of item flavor. One entry per floor entered, auto-composed from a pool that reacts to what just happened on the previous floor. Most entries are eight to forty words. He is telling you this story afterward, which is why he gets to foreshadow and undercut himself.

---

## C) The antagonist — the Under-Warden, who is a clerk

**The Under-Warden** is not a dark lord. He is a **bureaucrat of the dead**, the subordinate-of-subordinates who has been running the Paths since the god who runs them lost interest. Think Anubis if Anubis had been promoted into middle management and never promoted out. He wears the robes of a senior cleric, carries a ledger, and speaks like someone counting inventory.

His problem with you is *procedural*. You are an **Easterner**, the law of the Paths does not technically cover you, and he hates technicalities because technicalities make paperwork. He does not try to kill you in the early floors. He sends memos. You find the memos. They are very polite. They grow less polite.

This is deliberately low-key. The brief says the focus is tactical play, not a villain. The Under-Warden is a framing device — he makes the dungeon feel *judged* rather than just dangerous, and he gives the final floor a voice that isn't a snarling demon. Boss fight on floor 25 is the Under-Warden, not because he's the strongest thing down there (he isn't), but because he's the one with the ledger, and he can *close* it on you.

Monster factions mapped to the engine's existing art:

- **Orcs → the Unshriven.** Soldiers who died wrong — face-down in the wrong field on the wrong day. Violent because they were robbed of passage. Tier-1 humanoid threat. They carry their death-wound as flavor text ("*broken greataxe, half his helmet missing*").
- **Undead → the Dead who did not make their House's route.** Three tiers: **Shades** (floors 1–8, the common lost), **Oathbreakers** (floors 9–17, ghosts bound by a promise you can discharge), **Honored Dead** (floors 18–25, nobles in gilded armor, Baldor-style — they sit against unopenable doors until you complete their contract).
- **Clerics → Hall Wardens.** Not priests in the "healer" sense. They are weighers. They do not heal you. They **judge** you — each one carries a small ledger and debuffs you based on how many kills you've taken on that floor. They are the Under-Warden's staff.
- **Monsters → chthonic things older than the Paths.** Trolls (the stone-things), giant rats, king bats (Harpy/Keres analogs), giant centipedes, spiders. The dungeon's oldest residents; predate the judgment system, don't care about it.

---

## D) The world — the Paths of the Dead, which are partway into your floor

**The ONE weird idea:** *You didn't mean to be here.* You descended into **Reven Crypt**, the family tomb of the dead woman you're trying to recover. It turns out Reven Crypt was built on, or into, or *through* a node of the actual Paths of the Dead — the literal afterlife that Brust's Dragaerans and Tolkien's Aragorn and Virgil's Aeneas all travel through. On floor 1 you are in a normal fantasy tomb. On floor 3 you meet your first Oathbreaker, and she asks you for something instead of attacking. On floor 5 the walls start using a different stone. By floor 10 you know.

This gives the game the three-act structure of classical katabasis while letting the player's first impression be *classic fantasy dungeon*, which is exactly the "love letter" feel the brief asked for.

**Five regions of five floors each** (SPD rhythm, because SPD's rhythm is correct):

| Region | Floors | Aesthetic | Monster mix | Boss |
|---|---|---|---|---|
| **The Crypt** | 1–5 | Stone tombs, oil lamps, family sarcophagi | Rats, goblins, Shades (low), one Oathbreaker cameo | **The Warden of Reven** (old family ghost, refuses to let you leave) |
| **The Greymist** | 6–10 | The fog over Brust's Greymist Valley; fog LOS limits | Unshriven orcs, Shades, giant centipedes, first Hall Warden | **The Ferryman** (not hostile until you refuse his toll) |
| **The Dark Door** | 11–15 | Tolkien's Dimholt — black trees now made of stone, the finger-of-doom stele, Baldor's descendants | Oathbreakers, trolls, skeleton archers | **The Dead King** (answers to his oath, freed if you resolve it) |
| **The Halls** | 16–20 | Dante-by-way-of-Brust — contrapasso rooms, weighing-chambers | Honored Dead, Hall Wardens (heavy), king bats, liches | **The Weigher of Hearts** |
| **The Inner Court** | 21–25 | Brust's Halls of Judgment. Pillars, scales, the Orb-echo. | Named elites of every prior type, one Divine Servant (demon analog) | **The Under-Warden**, who has a ledger |

The Amulet — Anik's soul — is on floor 25, pinned to the Under-Warden's ledger. You do not kill him for it. You **audit** him.

Signature setting details, one per region, stolen directly from the sources:

- **The House Shrine** (every region): a small altar where you leave an offering (gold, food, a cursed item) and receive a small boon. Direct steal from Brust's statue at Greymist Valley. Identifies one item of the offered tier.
- **The Finger of Doom** (Region 3): a single stele you can examine that whispers in an unknown language. Examining it costs you one turn and permanently reveals the location of stairs on every remaining floor. Tolkien, direct.
- **The Golden Branch** (Region 2 or 3, one per run, consumable key): a single-use item that lets you bypass one locked gate, one charmed door, or one boss room's entry condition. Virgil, direct.
- **The Don't-Look-Back Room** (Region 4, a machine-room in Brogue's sense): a hall where the minimap goes dark. Reach the far end without opening the minimap and the room rewards you with a blessed item. Peek and the reward is replaced with a cursed one. Orpheus, direct.
- **The Contrapasso Rooms** (Region 4, rare): dungeon rooms themed to one of Dante's sins, with an environmental effect — the Lust room has winds that shove you one tile/turn, the Gluttony room is flooded with stinking sludge, the Violence room has a boiling-blood pool that deals 3/turn. Each is a vault in the Brogue sense — a designed puzzle using general rules.

---

## E) The MacGuffin — the Ledger, not the Amulet

The brief suggested literally the Amulet of Yendor or equivalent. The right call is to keep the *shape* and change the *object*.

**The Ledger.** It sits on the Under-Warden's lectern on floor 25. It contains every unsettled debt in the Paths, including the line that says *Anik of Reven, soul held pending, recovery forbidden*. You don't fight him. You **edit** him.

How you edit him: you have collected, over the run, **three Stones of Intuition** (SPD-style), each earned by completing an Oathbreaker's quest. Each stone represents a paid debt. You press each stone onto the Ledger's relevant line, and the line closes. The Under-Warden cannot prevent this — he can only kill you before you do it. So the *fight* is: reach the lectern, survive long enough to press three stones.

This gives you:
1. **A traditional MacGuffin** (recover the soul) with a twist (you rewrite the record, you don't steal the object).
2. **A built-in reason Oathbreakers exist** — each one you help yields a stone, so doing side-quests on earlier floors is load-bearing for the final boss, which rewards tactical exploration through the full run.
3. **A literal weighing-and-judgment climax** — exactly what Brust's Halls of Judgment is about, exactly what Dante's Inferno is structured around.
4. **Something the Under-Warden can monologue at you about**, in the voice of an offended auditor. "You are aware these entries have not been properly sanctified." "The Eastern clause does not apply to paragraph twelve." Etc.

The Ledger can also be *stolen* as a bad ending — if you grab it and flee without pressing the stones, you escape with Anik's soul but at the cost of *replacing* her debt with yours. The Paths now have a line in the book that says *Sasha of Reven, soul held pending*, and the next run begins with that debt visible. Nice meta-layer hook, no extra mechanics needed.

---

## F) Death and reset — clean, classic, one grace note

**Permadeath, per-run identification, per-run everything.** Don't be cute. This is a love letter.

On death you get a **death screen in Vlad voice**, reactive to cause ("*Killed by a troll. Had to be done, apparently. The troll thought so.*" / "*Poisoned. By a trap I set off on purpose. I meant it to happen to the bat, not me. Should have read the room.*" / "*Starved. In a place where nothing is actually alive. The ironies of down here are cheap.*"), and Loiosh gets the last word ("*Boss. BOSS. ... Well, rats.*").

One grace note: between runs, Loiosh remembers. **Three phrases per floor unlock after you've seen that floor in any prior run**, giving the familiar a growing repertoire of jokes the more the player plays. This is metaprogression of *voice*, not of power. Hades does this with its 20,000-line reactive dialogue system. You only need ~1,200 lines (3 × 25 floors × ~16 trigger types) for the equivalent effect, and Evan Debenham-style content discipline makes that one person's six-month job.

Optional second grace note (ship if budget permits): the **badge system**, SPD-style — ~40 badges on first release, track in-game catalog of what you've identified, what monsters you've possessed, what tactical interactions you've executed. No stat rewards. Just a recognition system.

---

## G) The fifteen-to-twenty tactical interactions — the heart of the thing

These are the specific things the game teaches through play, never through tutorial. Each one is **one classic roguelike technique plus one twist**. Each has specific numbers. Each is tested through an in-world monster, item, or trap that makes the interaction *discoverable* — a monster whose flavor text hints, a trap whose name hints, a Loiosh line that fires the second or third time the player encounters the situation.

**The Brogue principle applies throughout**: the simulation is consistent, the rules are absolute, the combinations emerge. Fire lights gas. Acid prevents regeneration. Water conducts. Confusion causes random walk. The player learns the atoms; the game never states the compounds; every compound works.

### 1. Troll + acid trap prevents regeneration
**Source:** NetHack trolls, Brogue caustic-gas-vs-regen, direct descendant of the dev's own brief.
**The rule:** Trolls regenerate **4 HP/turn**. Acid on a troll cancels regen for **6 turns**. Acid traps exist on most mid-floor levels. The player learns to **step onto an acid trap one turn before the troll closes**, taking 4 acid damage themselves, so that when the troll slashes them next turn it picks up acid and cannot regen. The troll becomes killable.
**The twist:** Acid also dissolves the troll's **2 DR armor plating** (the armor value it's wearing as a monster) for those 6 turns, so melee damage roughly doubles. Reinforces the "acid is an answer to trolls" lesson with a second layer.
**Loiosh's line on first troll kill via acid:** *"Cheaper than a potion. Filthier than a potion. Still cheaper."*

### 2. King Bat poison synergy
**Source:** The dev's own brief — the literal example.
**The rule:** King Bats deal **1d6 damage plus Drain Life**, healing themselves for half of damage dealt. Against a **poisoned** target, Drain Life **fails** — the blood is toxic. So a player who deliberately steps onto a poison trap, taking 1 HP/turn for 10 turns, becomes King-Bat-immune. This is a signature tactical moment.
**The twist:** After you survive a King Bat fight while poisoned, you gain **Tainted Blood** buff for 30 turns — ALL vampiric and lifesteal monsters (six types across the run) fail to heal from you. An investment that pays off for half a floor.
**Discovery mechanism:** A dead Oathbreaker on floor 7 has a note on his corpse: *"The bats don't drink sick blood. Wish I'd been sick."* That's it. That's the tutorial.

### 3. Caustic Gas ignition chain
**Source:** Brogue, direct.
**The rule:** Gas vents release a cloud that persists **8 turns**, deals **1 HP/turn caustic** to anything in it. Any fire source — a torch thrown, a fire trap triggered, a scroll of fire read — ignites the cloud, dealing **8 damage flat** to everything inside plus igniting any grass/furniture. Classic Brogue.
**The twist:** In The Under-Warden, **incense clouds** (thrown from incense burners found on House Shrines) behave like caustic gas but *heal* friendly undead by 2/turn instead of hurting them. So you can bless your own possessed shade-ally by standing him in incense. Doubles the environmental vocabulary without a new system.

### 4. Oathbreakers freed by completing their oath
**Source:** Tolkien's Oathbreakers — direct lift, mechanized.
**The rule:** Oathbreaker ghosts are **immune to all damage**. You can't kill them. Each carries an unfulfilled oath visible via long-press examine ("*I swore to burn my brother's body*" / "*I swore to return the cup to the altar*"). Fulfill the oath — bring the item, perform the action — and the Oathbreaker dissolves, dropping a **Stone of Intuition** (ledger-closer for the final boss) and one random item.
**The twist:** Some oaths are **contradictory** between nearby Oathbreakers. Fulfilling one means failing another, and the failed one becomes a **Wrathful Shade** — a hostile elite. This is a genuine moral choice, not a checklist.
**Loiosh's line on first Oathbreaker release:** *"There. That's one, closed. You look proud. Don't."*

### 5. Cleric judgment debuff, cleansed by possession
**Source:** Combination of NetHack priest mechanics + Dishonored possession.
**The rule:** Hall Wardens carry a **ledger** that applies **Judged** debuff on line-of-sight: **-1 accuracy per kill taken on current floor**. Stack it and your hit rate collapses. You can't dispel it with any scroll.
**The twist:** You can **possess the Hall Warden**. While possessing, you use *his* ledger to write out his own entry on you. Leave the host and the debuff is erased. This teaches possession's core value isn't combat — it's bureaucratic.

### 6. Wand of Portals — six legitimate uses
**Source:** The dev's existing engine's wand. He asked for it as a significant gameplay device. Delivered.
**The rule:** The wand opens a **two-tile portal pair** lasting **4 turns**. Start at 3 charges, recharges 1 per full floor descent, hard cap 5. Anyone (you, enemy, item, projectile, gas) that walks into one side exits the other. This is deep design space.
**The six taught uses**:
- (a) **Emergency retreat** — portal to an explored tile, walk through, gain safety.
- (b) **Projectile redirection** — portal a skeleton archer's arrow back at him. Archer goes down in one shot.
- (c) **Gas cloud relocation** — open a portal at the edge of a caustic cloud; the cloud flows through and engulfs the enemy on the far side.
- (d) **Trap relocation** — a portal opened on a pressure plate moves the "triggered effect" to the other portal's location. Fire trap in your face becomes fire trap behind pursuer.
- (e) **Item retrieval** — grab an item across a chasm or lava you can't cross. Replaces NetHack's Apport-scroll use case.
- (f) **Boss-phase skip** — on floors 10 and 20, the boss has a kill-room. Portal out.
**The twist:** Loiosh can *see through portals*. He'll call out enemy positions on the far side before you step through. This ties the familiar to the signature item.

### 7. Stair-dancing, with an anti-cheese
**Source:** DCSS, direct.
**The rule:** Descending stairs brings only adjacent enemies with you. Classic split.
**The twist:** The Paths penalize cowardice. **If you descend with visible enemies unslain above**, the Under-Warden's **memo** appears on your next floor: "*entry: fled from engagement on floor N*." Accumulate **three memos** and a **Revenant** (fast, durable, tracking elite) spawns two floors down. This preserves stair-dancing as a legitimate panic tool while preventing full-run stair-dance abuse. You get maybe two freebies per run.

### 8. Corridor fighting, with positional punishers
**Source:** DCSS funneling.
**The rule:** Standard corridor-funnel works. 1-tile wide, only one enemy can hit you per turn.
**The twist:** **Giant centipedes** have a **Pierce attack** that hits the adjacent tile behind their target — forcing you *not* to corridor them if there's an ally or NPC at your back. And **casters** (goblin conjurers, liches) won't follow into corridors; you have to come out to them. These two enemies train the player to *read the situation* rather than reflex-corridor every pack.

### 9. Sleeping enemies take triple damage (surprise attack)
**Source:** Brogue backstab + SPD surprise.
**The rule:** Attacks against unaware enemies deal **3x damage** and proc any runic effect with **2x chance**. Full Brogue.
**The twist:** In the Paths, the **Shades** (most floors 1–10) are often *sleeping by default* — they're the dead-who-wandered-off-the-path. This makes stealth/first-hit play dominant early, which is perfect: it teaches the surprise mechanic while letting the game be gentle in the first region.

### 10. Paralysis vent + food ration = pack lock
**Source:** Brogue, direct.
**The rule:** Paralysis vents trigger on weight. Drop a food ration (2 weight) on the tile; the next creature to step on it paralyzes for **15 turns**. Any creature.
**The twist:** The food ration is *consumed* by the triggering. Teaches the resource cost of the trick — you just traded one hunger-refill for one lockdown. You have to *want* the trade.

### 11. Chasm-push via Staff of Beckoning's successor
**Source:** Brogue staves.
**The rule:** The **Rod of Summoning** (level-appropriate wand in the Ledger tier) yanks any enemy 3 tiles toward you. Aim it so the three-tile drag crosses a chasm — the enemy falls to the next floor. One-shot removal of any non-flying threat.
**The twist:** The *dragged* enemy is **friendly** on the floor below for 8 turns — it thinks you rescued it. A possessable ally by accident. Brand-new tactical wrinkle classic Brogue doesn't have.

### 12. Fire propagation through grass and Wand of Regrowth
**Source:** SPD, direct.
**The rule:** Wand of Regrowth grows tall grass in a cone. Tall grass is flammable. Fire traps and fire scrolls ignite grass; fire spreads through contiguous grass at 1 tile/turn, dealing **4 damage/turn** to anything standing in burning grass.
**The twist:** Regrowth's grass also generates **dewdrops** when walked through (SPD-style). Heal on trample. So the player uses the same spell to farm both a defensive resource and an offensive battlefield. One item, two opposed uses — the Brogue criterion for "this is deep."

### 13. Acid trap + troll + Rod of Summoning (the full combo)
**Source:** Emergent; this is a compound tactical interaction, not a single rule.
**The rule:** You yank the troll with the Rod onto an acid trap, then disengage. The troll takes acid damage, can't regen for 6 turns, armor is corroded, and you've spent 0 HP. A four-part play: identify the trap, identify the rod, identify the troll's weakness, execute the sequence.
**The twist:** This is the kind of play the game rewards *without ever instructing the player*. The first time you pull it off, Loiosh has a dedicated reaction line: *"That was competent, Boss. I'm shocked. Don't let it go to your head. You can't afford the rent up there."*

### 14. Reflection-armor heal bounce
**Source:** Brogue, direct.
**The rule:** Runic reflection armor bounces any zap that hits you. Zapping a healing staff at a reflective ally bounces the heal back at you, letting you self-heal from a staff that can't target you.
**The twist:** In The Under-Warden, **Oathbreaker ghosts are naturally reflective** to all staff magic (they're already dead; magic slides off them). A freed Oathbreaker you have as a one-floor ally is a walking reflector. Teaches players to keep the Oathbreaker alive through the floor.

### 15. Identification through possession
**Source:** Possession systems in Dishonored / Oddworld, cross-bred with NetHack price-ID.
**The rule:** Possess a creature → its full monster-card (HP, damage, resistances, attacks) is revealed for the rest of the run for ALL of its species. Free identification of that monster's stats.
**The twist:** Possess a shopkeeper → all of his stock's prices become "true prices," and you can see which of his items is enchanted. Possessing shopkeepers has a **massive retaliation cost**: on release, the shop closes permanently this run, and the Under-Warden's third memo fires. One-time-use per run, maximum.

### 16. Contrapasso-room environmental damage
**Source:** Dante, mechanized.
**The rule:** Contrapasso rooms in region 4 have environmental effects that match their theme — Lust-room wind shoves everyone one tile/turn in a fixed direction, Violence-room boiling-blood pool deals 3/turn, etc. The player can *use the room against its inhabitants* if they know the room's rule.
**The twist:** The Lust-room wind can be used to **push an enemy into your portal**. The Violence-room blood pool can be **channeled** by a cleric's staff to heal a possessed undead. Each contrapasso room has *two* counter-tactical uses, not one.

### 17. Reading a scroll of Fire next to a caustic cloud
**Source:** Brogue chain reactions, but embedded in the scroll/potion vocabulary so players discover it through normal identification.
**The rule:** Scroll of Fire reads as a **3-tile-radius burn centered on you**, dealing 6 damage. Obvious panic button. Painful.
**The twist:** If the burn radius overlaps a gas cloud, it ignites the full cloud simultaneously — turning a 6-damage self-hurt into a 40-damage AoE that bypasses armor. The scroll transforms from "oh no" to "delete this pack" with zero stat change, just terrain awareness.

### 18. Cleric altars via possession
**Source:** Our own signature moment, from the possession research.
**The rule:** On each region's House Shrine there's a cleric altar that only **ordained clerics** may use. You're an Easterner, retired, not ordained. But if you possess the floor's Hall Warden and walk him to the altar, *he* can use it. The altar grants **Judged Exempt** — Hall Wardens on subsequent floors ignore you until you attack them.
**The twist:** The altar effect transfers through your bond to your home body. Leave the host. You're still Exempt. Signature moment. Players tell their friends about this. (This is the #1 reason to ship possession.)

### 19. Cursed-item handling in a host body
**Source:** Possession mechanics + NetHack curses.
**The rule:** You can't normally remove a cursed item you've equipped. Classic.
**The twist:** Cursed items equipped on a **host body** don't bind to your home body. So wielding that cursed sword is now *free*: possess an enemy, equip the cursed sword, use it for one fight, leave the host, the curse stays behind. Teaches possession's *identification* use — you can safely try-before-you-buy cursed gear.

### 20. Oil flasks as a grease layer
**Source:** NetHack oil flasks.
**The rule:** Throwing an oil flask onto a floor tile creates **slick terrain** for 12 turns. Anything stepping on it has a 50% chance to fall prone, losing its next turn.
**The twist:** Slick terrain also **propagates fire at 2 tiles/turn** instead of 1. A lit oil slick is a 4-tile-long fire-line that moves. Combine with paralysis vent (see #10) and you have a room-clearer with no damage to yourself.

### 21 (bonus). Don't-look-back room
The full Orpheus gimmick. Cross the room, don't open the minimap, get the blessed reward. Open the minimap, get the cursed version. Loiosh explicitly says nothing in this room. He's not allowed to. Even he respects the rules.

---

Twenty named interactions. Every single one is the same core shape: *a beloved roguelike technique, plus one twist that makes it specifically this game's*. None of them require new engine features beyond the possession system and the wand of portals the dev already has. Most of them emerge from the existing terrain, trap, and monster vocabulary.

---

## H) The familiar — Szavka the jhereg, in a charm

**Name:** Szavka (Hungarian diminutive, fits the Eastern-adventurer register, not the same as Loiosh so we're inspired-by, not copyright-adjacent).

**Form:** A small flying lizard bonded into an **egg-amulet** you wear. **No overworld sprite. No pathfinding. No follow-AI.** She lives in your head (and, diegetically, in the amulet). Cutting the delivery vehicle from "pet that follows" to "voice that talks" is the single most important design decision in the whole proposal.

**Delivery mechanism:** An **italic-purple text ribbon** at the bottom of the screen, persisting for 4 seconds per line, max one line on screen at a time. A small charm icon in the HUD corner pulses when she speaks. No voice acting. No audio required. Localizable. Minimal UI footprint.

**Voice register:** Loiosh (70%) + Rucks cadence (15%) + Lilarcor self-awareness (10%) + Morte gallows humor only on death (5%). Cynical, loyal, tactically sharp, self-deprecating about being annoying. Calls Sasha **"Boss."** Never flirts with NPCs. Never explains a mechanic Sasha has already used.

**Silence rules** (enforced at engine level, non-negotiable):
- **Every line is authored once per run.** No repetition. If a trigger fires a second time, a different pool-member fires, or nothing.
- **Combat silence by default.** During active combat (any enemy in sight and in 3-tile range), Szavka only speaks if HP crosses 25%, 10%, 1%, or if a new monster species appears.
- **Idle only after 20+ silent turns.** She only volunteers a comment when the player stops engaging, never during flow.
- **Player can tell her to shut up.** A UI button on the charm icon: tap → she's muted for the rest of the run. She has a single acknowledge-line: *"Right. Fine. Call me when something eats you."* Tapping again un-mutes her. **This button is the diegetic, Lilarcor-inspired defusing of the Navi problem.** Players who find her charming will never touch it. Players who don't, will, and will feel respected.
- **Verbose / Tactical-only / Silent** settings toggle in options.

**Trigger taxonomy** (authored content per trigger, pool-based, stale after 3 runs):

| Trigger | Lines per floor | Example |
|---|---|---|
| First sighting of new monster species | ~25 total (1 per monster) | *"That's a Hall Warden. He's going to write you up. Hit fast."* |
| First entry to a new region | 5 | *"This is the Greymist. Whatever Brust wrote about it, he was lying politely. Fog's real."* |
| HP at 25% | 1 per run | *"Boss. You're leaking."* |
| HP at 10% | 1 per run | *"Boss. BOSS. Drink something."* |
| HP at 1% | 1 per run | *"Goodbye."* |
| Trap triggered (first of each type) | ~8 total | *"Acid. On purpose, I hope."* |
| Item identified | pool of ~30 | *"Ah. It's that kind of potion. Good."* |
| Kill streak ≥5 no-damage | 3 per run | *"Showing off, are we."* |
| Long idle | 3 per run | *"Any decade now, Boss."* |
| On death | 1 reactive per cause-of-death | *"Poisoned. By a trap you set off on purpose. Subtle."* |
| On possession enter | 1 per species, ~25 | *"Ugh. This one smells like wet dog."* |
| On home body drain starting | 1 per run | *"They're eyeing your body, Boss."* |
| On possession exit successful | ~6 total | *"See. I knew you'd make it. I lied, but I knew."* |
| Between runs (results screen) | ~50 lines reacting to death cause, best kill, biggest find | *"Twenty-two floors. Not bad. Not good. Somewhere in between, which is where you live, I guess."* |

**Tactical intel delivery:** Szavka sees through the Wand of Portals. When you place a portal, she **scouts the far side**: "*Three shades and a Warden on the other side. Don't walk through.*" This ties the familiar to the dev's signature item and gives her a repeatable gameplay function beyond flavor.

**Why this works where Navi fails:** Szavka's comments are event-triggered and one-shot, never repeated. She never tells the player what to do (no "hey, listen!"). She reacts to what Sasha just did, Rucks-style. She can be told to shut up. She has her own jokes about her own existence. She is a character, not a hint engine.

**Why this works where Morte would fail:** Morte's horny-insult register punches outward at NPCs, which ages poorly across a hundred runs. Szavka's snark is *inward*, at Sasha — the jokes come from affection and friction inside the pair. You can hear this for four hundred runs because the dynamic renews itself with every new crisis.

---

## I) Possession — "wear a body," pay with your own

**Mechanic name in-game:** *Wear a body.* Sasha never uses the word "possess" — it's work, it's something he does, it's not a power he shows off.

**Cost:** **Once per floor**, baseline. Upgradeable to twice per floor via the region 3 altar boon. It is not a mana-spam ability. It is a rare, dramatic move.

**The channel:** Tap an enemy → 1-turn channel animation (Sasha goes still, holds the amulet to his forehead, Szavka visibly glows). Any damage to Sasha during the channel cancels the possession and wastes the use. Turn-based, so the player fully controls the setup.

**Risk model** (the dev's exact instinct, tuned):
- Sasha's body goes **catatonic** at his current tile. Visible on the map. Targetable.
- **Grace window: 2 turns** of zero drain. Short flip-and-exit plays are free.
- After turn 2: **1% of Sasha's max HP per possessed turn** (min 1 HP, rounded up).
- **Doubles (2% max HP) if any enemy has line-of-sight on Sasha's body.** This is the pressure knob. Leave his body in the open and the timer accelerates.
- **Resting heals Sasha's body** at normal rate (1 HP / 10 turns) — but the drain is per *your* action, so this only matters if you're efficient.
- **If the host dies while you're in it** → you have 5 turns to jump to an adjacent possessable or the run ends. (With the *Chain Possession* upgrade, this becomes automatic.)
- **If Sasha's body dies while you're out** → the run ends. You get a 5-turn "final word" in the host to do one last thing (kill a boss, grab a stone, stab a specific enemy), then permadeath.

**Valid targets:**
- **All living humanoids and beasts** — orcs, rats, bats, centipedes, goblins, most monsters.
- **Recent corpses** (within 3 turns of death), for scouting-only use — you can't fight in a corpse but you can see and walk.
- **Vacant vessels** (statues at shrines, empty suits of armor), once per region.
- **NOT possessable:** Bosses, Oathbreakers (already occupied), elementals, slimes, Hall Wardens *on first meeting* (you must see their Judgment once before you can wear them).

**Upgrades**, each costs one skill point from the region 1, 3, 4, and 5 altar boons (four total per run):
1. **Lasting Host** — grace window 2 → 5 turns.
2. **Chain Possession** — host dies, auto-jump to adjacent possessable (Dishonored-style).
3. **Deep Host** — identify all magical items in host's inventory (not just stats).
4. **Willing Vessel** — mark one freed Oathbreaker per run as free possession (no drain). Turns the Oathbreaker-quest loop into a possession enabler.

**Tactical uses** (these are what the player learns the skill is *for*):

1. **Free species identification** (interaction #15 above).
2. **Walk through a species-locked door** — orc-only passages in region 2; cleric-only altars in regions 3–5.
3. **Free cursed-item trial** (interaction #19).
4. **Fooling other enemies** — Oddworld-style. Possessed orcs aren't attacked by other orcs for 4 turns (grace; then their Unshriven fellows notice the wrong-walking).
5. **Cleric altar access** (interaction #18) — the signature moment.
6. **Saving throws in a tight spot** — possess the enemy that's about to hit you, walk him around a corner, leave the host stunned. Emergency ejector seat.
7. **Suicide weapon** — leave the host via *Explode* (2d8 damage to adjacent, host dies, costs nothing extra). The possessed-orc bomb.
8. **Scouting-by-corpse** — possess a fresh corpse for 8 cost-free turns to walk the floor invisibly. The cost: you can't attack, and you can't pick up items (the corpse has no agency). Revelation, not power.

**The integration with the familiar:** Szavka narrates every possession. This is the single best design move in the whole document — the mechanical risk is held in relational tension by the voice. Her dedicated possession lines are the most-polished writing in the game. *"They're eyeing your body, Boss."* / *"Boss. BOSS. Get back in it, now."* Loiosh sitting on Vlad's shoulder commenting while Vlad wears an orc is the reference. Build toward that exact feeling.

---

## J) Delivery architecture — lean, traditional, nothing wasted

No cutscenes. No voice acting. No parallax backgrounds. No illustrated story panels. This is a traditional roguelike; its narrative lives in **six thin channels**:

1. **Sasha's diary** — one short entry per floor entered, auto-composed from trigger pools. Appears on floor-entry screen; can be swiped away; archived in a "journal" menu. The diary is where the full Vlad voice lives.

2. **Item flavor text** — every single item, including every mundane item, gets a 20–60 word Vlad-voice description. The **Potion of Healing** flavor ("*Tastes like a goat died in a church. Works, though.*") is the game's foundational tonal commitment. Target: ~180 items × ~40 words = ~7,200 words of flavor. One writing pass. Cheaper than any cutscene.

3. **Monster descriptions** — every monster gets a Vlad-voice description on first-identify. ~45 monsters × ~50 words = ~2,250 words. Each ends with a *hint* about the tactical interaction: "*Kill the one with the lit candle in its chest first. That one's steering.*" The description is the tutorial.

4. **Szavka's trigger lines** — ~1,200 lines across all triggers and runs. Pooled, reactive, authored-once.

5. **Lore notes / ledger entries / Oathbreaker oaths** — ~50 Oathbreaker oaths, ~25 Under-Warden memos, ~30 ambient environmental notes. ~2,500 words total.

6. **Shopkeeper and Ferryman banter** — the shopkeepers are deliberately *bad* at dungeon etiquette. They sell you things at wrong prices because the dungeon's economy is dead-currency. A Ferryman quotes you tolls in coin you picked up on a previous floor. ~500 words of dialogue.

**Total writing budget: ~14,000 words of game text**, all in Vlad's voice, all in short chunks, all reactive to player state. One writer (me or the dev or a collaborator) can produce this in three focused months with revision passes. This is the Brogue/SPD model: lean text, maximal interaction-density.

**No chapters. No acts. No cutscenes.** The region transitions are marked by environmental shift plus a one-line Szavka comment plus a one-paragraph Sasha entry. That's it.

---

## K) Replay — depth without narrative branches

**No narrative branching.** This is not Vess House; this is not Long Winter. The story is "Sasha went into the Paths, he did or did not come out." Replay value lives in tactical depth.

**Replay surfaces:**

1. **Daily seeded runs** — SPD model. One seed per day, shared globally, leaderboard. Three-hour target. The social layer. Non-negotiable for mobile retention.

2. **Challenge modes** — unlocked after first win. Nine SPD-style challenges, stackable. Proposed set: *No Possession. No Portals. No Familiar (Szavka silent). Shopkeeper-hostile. No House Shrines. Judged Always (permanent Hall Warden debuff). Hungry Paths (double food drain). Silence of the Dead (no monster flavor text on identify — pure play). Iron Sasha (one life, no reset until win).*

3. **Catalog** — every item, monster, and tactical interaction discovered accumulates in an in-game journal. Non-mechanical. SPD-style. **Shows interaction list** (#G above) as each is discovered, so the player can see what they've figured out and what they haven't. A literal checklist of the 20 tricks. Incredible retention hook.

4. **Badges** — ~40 on launch. Some are completion, some are tactical (*"kill a troll with only acid-trap damage"* / *"clear a floor without Szavka speaking"* / *"possess a shopkeeper and escape the floor alive"*). SPD's badge design is the reference; don't reinvent.

5. **Szavka voice-line meta-unlock** — she grows chattier per-floor the more you've played that floor. 3 lines per floor per run, so runs 2, 3, and 4 reveal new Szavka banter on each floor. Capped around run 4 so she's fully voiced for a dedicated player. Pure flavor retention, no power.

No unlockable classes. No stat upgrades between runs. No gold-hoard metagame. The dev wants a traditional roguelike; traditional roguelikes do not have shop upgrades. SPD's model — knowledge metagame, not power metagame — is the correct answer.

---

## L) Endings — three flavors, one structure

**One win condition, one loss condition, three flavored variants of each.**

**Wins:**

- **The Clean Audit.** Press all three Stones of Intuition onto the Ledger, close Anik's line properly. Sasha climbs out of the Paths with Anik's soul. *"Eight floors back up. Then four. Then one. The stairs pretend to end, and this time I let them."* The canonical good ending. Verra is satisfied. Debt closed.

- **The Theft.** Grab the Ledger and flee without pressing stones. Sasha escapes, but his line now sits in the book: *Sasha of Reven, soul held pending.* Next run, a new Under-Warden memo fires on floor 1 — the Paths are looking for you. Meta hook, no mechanical penalty.

- **The Swap.** Press only your own stone (gained by completing Sasha's *own* unfulfilled oath, a hidden quest chain for players who pay attention). Trade yourself for Anik. She walks out, Sasha doesn't. *"I stayed. Someone had to sign the book. Loiosh carried the news up. He'll be insufferable about it. He's earned it."* The secret good ending — hard to find, not signposted, the kind of ending Brogue would respect.

**Losses:**

- **The Kill.** You died to a monster. Szavka gets the last word, snarky.
- **The Self-Kill.** You died to your own tactic (poison trap, oil-slick fire, possession-body neglect). Szavka gets the last word, gentler.
- **The Ledger.** You died to the Under-Warden. He writes your entry personally, one formal paragraph, in a different text register than anything else in the game. It reads like paperwork. It's devastating.

---

## M) Five signature moments the player will share

These are the five specific stories a player tells a friend after a run. If the game delivers these, the game is good. Each should be a clip-worthy, screenshot-worthy, 10-second description worth.

1. **"The time I beat the troll with an acid trap."** Deliberate self-poisoning via acid, trolls suddenly killable. Teaches the entire *environment-as-weapon* vocabulary in one interaction. Should happen naturally around floor 7.

2. **"The time I wore a Hall Warden to the altar."** Full possession-signature moment. The player walks an enemy to an altar the player themselves cannot use, transfers the boon, then decides whether to explode the host or leave him. Should happen around floor 13.

3. **"The time Szavka told me the orc on the other side of the portal had a cursed axe."** The wand-of-portals-plus-familiar-scouting moment. Player places a portal, Szavka calls the far side, player readies, charges through into a prepared fight. Feels like the game is working with you, not at you.

4. **"The time the Oathbreaker asked me to carry her bones two floors up."** The sidequest moment. A non-combat interaction that turns into a three-floor planning problem — do I keep her bones through a second floor's inventory pressure, or do I abandon the quest? Pays off with a Stone of Intuition, which matters at floor 25. Teaches the Ledger-end-game in the middle of the dungeon.

5. **"The time I fled from a troll by jumping down a chasm, and Szavka screamed the whole way."** The panic-tool-that-is-also-a-shortcut moment. Brogue's chasm-dive, flavored by the familiar's reaction, flavored again by the diary entry at the bottom. The kind of roguelike moment that players narrate.

Any one of these five is a Twitter clip. All five together are a review.

---

## N) Scope and sequencing for a solo dev — six to eight months

**Pre-production (Month 1).**
- Lock the 20 tactical interactions (G) as a design spec. No additions during production.
- Lock the 25-floor structure. Lock the five regions. Lock the 45 monsters and 180 items.
- Write the 20 trigger types for Szavka. Lock the voice.
- Build the possession prototype on paper; tune the drain numbers.

**Core build (Months 2–3).**
- Port the existing engine to handle: the possession system, the portals (already done by dev), Stones of Intuition, the Ledger UX, the House Shrine altars.
- Content-build the 25 floors: environment, monster distribution, trap placement, vault placement. This is where **Brogue-style machines** live — aim for ~8 hand-designed vault templates mixed with procedural generation, like SPD.
- Import Oryx assets; reskin minimally (Hall Wardens are priests in red; Oathbreakers are skeletons with small candle-sprite overlay; Honored Dead are skeletons in gilded armor).

**Writing pass (Month 4, can parallel Month 3).**
- ~14,000 words of text: diary, item flavor, monster descriptions, Szavka lines, Oathbreaker oaths, Ledger memos, shopkeeper banter, ending variants.
- One pass, then revision.

**Tactical tuning (Months 5–6).**
- Playtest every one of the 20 interactions. Each must be discoverable within ~6 runs by a non-expert tester. Any interaction that requires wiki-lookup is either re-taught (flavor hint, Szavka line, monster description) or cut.
- Numeric balance: HP, damage, drain rates, regen. SPD-style pass.
- Tune the Under-Warden boss fight. This is the last 40 hours of tuning work.

**Polish and ship (Months 7–8).**
- UI polish. Badge system. Daily-run infrastructure. Cloud save (carefully — SPD has had issues).
- Launch.

**Key scope discipline:**
- **No voice acting.** Text only. Saves 2+ months and $8K+.
- **No hand-drawn art.** Oryx only. Small sprite overlay for Szavka-speaks charm glow; small overlay for possession channel. Nothing else custom.
- **No procedural narrative.** The diary is pool-selected, not LLM-generated, not markov-chained. Authored lines, triggered by event.
- **No multiplayer.** Daily leaderboard only.
- **One class.** Sasha. No subclasses. No alternates. Ship the game before shipping classes.
- **One weapon type baseline (dagger), four weapon-family variants available as drops (sword, mace, bow, staff).** Don't build a weapon RPG. Build a roguelike.

The dev has six months of realistic full-time solo capacity. This is a seven-to-eight-month design as scoped; cutting ~5 tactical interactions and ~5 floors gets it to six. Ship the reduced version. Add via updates.

---

## O) Where this sits in the portfolio

Rafe now has seven proposals. They sort cleanly:

| | Proposal | Genre | Audience | Risk |
|---|---|---|---|---|
| 1 | **Vess House** | Grief-horror | Narrative gamers (Spiritfarer crowd) | Emotionally heavy, small audience |
| 2 | **Long Winter** | Political epic | CRPG adults | Scope risk |
| 3 | **Vale Interior** | Rival-as-architect | Puzzle-narrative | High-concept, niche |
| 4 | **Drown's Gate Tax Collector** | Casual comedy | Broad mobile | Depends on humor writing |
| 5 | **Pip Mail Carrier** | Kids | Family | Low risk, low ceiling |
| 6 | **The Long Rotation** | Cursed-dragon rescue | Rafe's original crowd | Personal project |
| 7 | **The Under-Warden** | Traditional roguelike | Roguelike veterans + curious mainstream | Depends entirely on execution |

**The Under-Warden's position: the craftsmanship bet.** It is the proposal least dependent on premise and most dependent on execution. That's exactly what the brief asked for — "win by nudges and adjustments that all add up." The target audience is the enormous existing roguelike community (Shattered Pixel Dungeon has ~10M installs; the roguelike tag has sustained a top-30 presence on mobile for a decade) plus the mainstream players who would never touch a roguelike but will touch *this one* because the voice makes the friction feel like character.

**Compared to the others:**
- It is Rafe's **safest commercial bet** — the roguelike market is proven, the tactical-depth angle is underserved on mobile, and the familiar+possession signature is a review hook.
- It is his **most defensible portfolio anchor** — the game ages well, supports years of updates, has a clear DLC/expansion path (new regions, new classes, new familiars).
- It is **orthogonal to the other six**. None of them compete for the same shelf space. Players who pick up Pip don't pick up Under-Warden, and vice versa. It does not cannibalize the portfolio.
- **Timeline fit: six to eight months, second-release slot.** Release after whichever simpler proposal he ships first (probably Pip or Tax Collector), so the engine is proven and the possession/portal mechanics have been dev-tested in a lighter context. Under-Warden is the *craft showcase* — the game you point journalists at when you pitch his next three.

---

## Conclusion — the nudges, named

This proposal commits to a small number of specific decisions that are each conservative on their own but compound into a distinctive game.

**The setting is a literal afterlife, not a metaphorical one** — which unlocks every katabasis trope and licenses a dungeon that is *judged* rather than merely dangerous.

**The MacGuffin is a ledger, not an amulet** — which turns the final fight from a kill into an audit, ties the mid-game Oathbreaker quests to the end-game, and gives the Under-Warden a voice that isn't a snarl.

**The familiar lives in an amulet and speaks in italic text** — which solves the Navi problem, costs no sprite budget, and lets Szavka narrate the possession system (the single best interaction in the design).

**Possession costs your body's HP, escalated by line-of-sight** — which makes every possession a mini-puzzle about where you leave yourself, and produces the signature Cleric-Altar moment that reviewers will open with.

**The 20 tactical interactions are each one classic roguelike trick plus one twist** — which is exactly the Brogue grammar the brief asked for, and which means a veteran roguelike player will recognize every mechanic while also discovering something new in every one.

**Sasha's voice carries every piece of text** — which means the game's personality lives in ~14,000 words of authored flavor, producible by one person in three months, with no voice acting or cutscenes.

This is the quiet proposal. It does not have the high concept of Vess House or the scope of Long Winter. What it has is thirty beloved roguelike mechanics, each tuned by one click, connected to a voice that treats the dungeon like a day at work, anchored by a possession system that turns the entire floor into a chessboard. Rafe asked for a game that wins through nuance. The nuance is *every single one of the twenty interactions*, and the character is the way Sasha talks about them. Build this one, ship it, watch it get a cult. The Under-Warden will file your review personally.