# plan_end_game.md - The Weighing

*Replaces the retired Zhyraxion endgame (dragon boss / Ruby Heart / lore-gated endings). That design is fully retired; none of it is this game. This is the Under-Warden endgame.*

---

## The problem this solves

The game currently has no victory state. A player who descends deep enough keeps descending indefinitely. This document defines what winning is, what the final encounter is, and how it resolves into the three endings v3 already specifies (Clean Audit, Theft, Swap).

The design also solves a roguelike-genre requirement: there must be a wall. A hard final test that most runs fail, that experienced/lucky/well-geared players overcome, that players chase across many failed attempts. The Zhyraxion dragon was the wrong wall (generic, disconnected from the premise). This design makes the wall *express* the premise instead of betraying it.

---

## Core concept: the Weighing

The Paths of the Dead are a literal afterlife. At the bottom, the dead are weighed. The endgame makes this literal: Sasha reaches the Inner Court, the Under-Warden conducts an audit of his entire descent, and the audit becomes a combat encounter in which the things Sasha did wrong rise up as Guardians and test him.

This is the psychostasia - the weighing of the heart - rendered as a roguelike boss gauntlet. The lodestar is Planescape: Torment's endgame, where the final confrontation is the protagonist's accumulated self made manifest. Sasha's enemy at the end is his record.

**The Under-Warden does not fight.** He conducts the weighing. He reads each audit category in bureaucratic register, and as each Guardian rises, he annotates the proceedings. He is the clerk of Sasha's judgment, unfailingly polite, narrating the sins while their manifestations try to kill the man who committed them. This keeps the character intact: a bureaucrat who watches the institution's enforcement tear you apart and files the paperwork either way is more menacing than one who throws a punch.

---

## The five Guardians

Five Guardians, fought every run in a fixed gauntlet. Every player faces the complete judgment; the audit determines each Guardian's power and disposition independently.

Each faction-themed Guardian (the first four) scales on a record metric and can become an **ally** if the player's record in that category is strong. A good record turns the Guardian into a combatant who fights *beside* Sasha against the others. A bad record turns it savage. This makes the Weighing a referendum on the whole playthrough at once: the factions you honored stand with you, the ones you wronged stand against you, and the fight's shape is the sum of your life.

The fifth Guardian (the Debt) does not scale and cannot be allied. It is the constant.

### 1. The Warden-of-Wardens (possession / Hall Wardens)

- **Scales on:** `hall_warden_possessions_total` and the possession-tone track (polite/procedural_notice/formal_complaint).
- **Ally form** (rare/no possessions): a single Hall Warden in good order stands with Sasha, lending institutional authority.
- **Savage form** (many possessions, formal_complaint tone): a fused mass of every Warden Sasha wore, fast and relentless. Signature mechanic: it possesses *Sasha's allies* mid-fight to turn them against him - the possession mechanic turned back on the player. Thematically exact: you wore them, now the consequence wears yours.

### 2. The Oathkeeper (bonding / the Unshriven)

- **Scales on:** orc faction reputation (Hostile/Neutral/Allied) and the geas-betrayal record (unprovoked Unshriven kills, marker-faith).
- **Ally form** (Allied): an orc champion fights beside Sasha. Borrek's people remember the marker he moved and the faith he kept. Possible Borrek/Vesh voice line on the champion's arrival.
- **Savage form** (Hostile): a manifestation of broken oaths, brutal, hitting harder the more orc blood Sasha spilled unprovoked.

### 3. The Assembly of the Lost (death / the past-selves)

- **Scales on:** `CumulativeDeaths` and the past-Sashas catalog size.
- **Ally form** (few deaths): a single past-self stands with Sasha - the one good Sasha, fighting for his successor.
- **Savage form** (many deaths): a horde of every Sasha who fell, the Under-Warden's filed corpses turned against the living one. The binding-cost subtext detonates here - these are the lives Hollowmark spent her span recovering. Possible Hollowmark voice line, heavy, on the Assembly's rise.

### 4. The Auditor's Own (purity / restraint / chthonic Old Authority)

- **Scales on:** a measure of excess - suffering caused beyond necessity, how much taken versus needed. (Metric needs definition; see open questions.)
- **Ally form** (professional descent): a being of cold order judges Sasha *adequate* and lends its weight.
- **Savage form** (butcher's descent): the full wrath of Old Authority, the oldest and least human of the Guardians.

### 5. The Debt (Anik's soul / why Sasha came)

- **Does not scale.** Always full strength, every run, for every player.
- **Cannot be allied.** It is Anik's soul, the reason for the descent, the one reckoning no one can stand in for.
- **When the Debt rises, the allies fall back.** Not defeated - this part simply isn't theirs. Borrek's champion cannot pay Sasha's debt. The past-selves cannot. The Old Authority cannot. Sasha faces the Debt alone, every run, at full power, regardless of how the rest of the Weighing went.
- **The story this tells:** the Debt is hard because debts are hard, not because Sasha was good or bad. Faction goodwill does not discharge it. It was always his burden to carry, and at the end he carries it alone.
- **On the ally fallback:** allies should get a line as they withdraw. Example (orc champion): *"This one we cannot carry for you, Sasha of Reven. We would if we could."* The virtuous player, who had company a moment ago, feels the weight of facing the Debt alone precisely because of the contrast. The narrative does the emotional work.

---

## Why the Debt is unscaled and unaided (design rationale)

This was a deliberate choice over an alternative (inverse-scaling: Debt gets harder the more allies you have). The inverse-scaling version created a perverse incentive - a player might betray a faction to weaken the Debt - and told a slightly false story (punishing virtue as if kindness were a distraction from the debt).

The unscaled-unaided version is cleaner:

- **The wall is always there, for everyone, and it is the same wall.** The virtuous player coasts through weak/allied Guardians and hits the Debt at full strength with no help. The monstrous player claws through savage Guardians and reaches the Debt half-dead. Both face the identical final test. Both can fail.
- **Virtue is rewarded without trivializing the wall.** Good behavior gives allies and a healthier approach to the Debt; it does not let you skip the Debt.
- **The difficulty curve is correct.** Virtuous run: front-loaded easy, back-loaded to a lonely brutal climax. Monstrous run: uniformly brutal. Both earn the win; neither gets a victory lap.
- **The Debt becomes the community's shared referent.** Every player who wins beat the same Debt. "How did you do against the Debt" has a common meaning, the way "did you beat Olmec" does. The faction Guardians are the personal, variable part of each run; the Debt is the universal constant.

---

## Flow: audit to Weighing to ending

1. **Arrival.** Sasha reaches the Inner Court (floors 20-25 region). The final encounter is at floor 25.

2. **The audit (dialogue).** The Under-Warden conducts the audit. He reads Sasha's record category by category - the memos pay off here; the audit is the sum of every grievance filed. This is where the player learns, in the Under-Warden's voice, what their playthrough amounted to. Each category's standing determines the corresponding Guardian's power/disposition.

3. **The Weighing (combat gauntlet).** The five Guardians, in sequence or in a structured arena. As each category is weighed, its Guardian rises (savage, diminished, or allied). The Under-Warden annotates throughout in bureaucratic register: *"Category seven: bilateral occupancy. Sixteen recorded instances. The Warden-of-Wardens will now assess."* The first four Guardians resolve according to record. Then the allies fall back and the Debt rises alone.

4. **The outcome (ending).** Surviving the Weighing resolves into one of the three v3 endings:

   - **Clean Audit** - survive the Weighing with a clean record (Guardians were light/allied, you passed well). The Under-Warden files a clean audit. Sasha leaves with Anik's soul, debts paid, the lawful exit. Achievable for skilled players who also behaved.

   - **Theft / Defiance** - survive the Weighing with a heavy record (savage Guardians, beaten against the odds). The audit closes adverse. Sasha takes the soul by force and escapes. The hard wall; the defiant ending. Per v3, this is also the meta-hook - the institution's grievance becomes permanent, future descents harder.

   - **Swap** - the hidden ending, available only if the Things Hael Mentioned catalog (Crypt-of-Wend) is complete. At the moment of judgment, instead of being weighed, Sasha offers *himself*. He is not taking anything; he is staying. The Guardians do not fight - there is nothing to judge. The binding-cost payoff: *"I always knew, Boss. I never minded."* The true terminus. (See v3 sections on the Swap and the Hael catalog gating.)

5. **The losses (v3's three losing endings).** v3 specifies six endings: three wins (above) and three losses. The losses are the ways Sasha fails the Weighing - dying to the Guardians, dying to the Debt, or some specific narratively-framed failure. The Under-Warden writes a final memo for each. (The three loss framings need definition; see open questions.)

---

## What happens after winning (replay structure)

- **Clean Audit** loops - you won, it is a milestone, the descent resets and continues. Possibly unlocks a harder mode or a new starting condition.
- **Theft / Defiance** loops but unlocks - the harder ending opens new content or difficulty, and seeds the knowledge toward the Swap (the meta-hook v3 describes).
- **Swap** is the true terminus - the genuine ending for dedicated players who completed the Hael catalog. After the Swap, credits / a real ending state.

This matches standard roguelike structure (most endings loop as milestones; one hidden true ending is the terminus).

---

## The Under-Warden's own unaudited account

The floor-19 grief mural (v3) gains weight from the Weighing. The Under-Warden, who is about to weigh Sasha for everything, is himself a man who never asked about the woman he loved eighty years ago. The judge has his own unaudited account. This should be felt but never stated - the mural surfaces it once; the Weighing never references it directly. The player who saw the mural carries the knowledge into the audit. (No engineering implication beyond the existing mural; flagged for narrative resonance.)

---

## Viability pass (engineering)

Verdict: buildable, no research-risk blockers, premise holds for six of seven hooks. Not a Zhyraxion-class mismatch. Estimate ~8-11 us-together sessions to tuned-and-beatable (framework ~6.5-9, balance pass 1-2). Content runs in parallel and is the real long-pole, not counted in that estimate.

Key finding that reframes the pass: persistence (all 7 phases) and possession (Phases 1-7) are already built and shipped, so the audit's data substrate is already in the ground. Most "does this exist" questions answer against real code, and the answers are better than the plan assumed.

Three things are genuinely net-new; only one was a design unknown (now resolved):

1. The win-condition scaffold does not exist at all. Dungeon mode has no victory state, no depth cap, no special floor-25 behavior. The Weighing is not inserted into the endgame; it is the endgame, built from zero. This is the bulk of the lift, but known-shape work.
2. Player-allied combat AI is net-new and touches core targeting. The faction system supports NPC-vs-NPC, but there is no faction that fights for the player. FactionRegistry.AreHostile hardcodes player-vs-everything, and ChooseTarget hardcodes the player as a priority-10 target. The lift includes the friendly-fire surface (AoE, thrown items, cleave, possession targeting, auto-explore pathing must all learn not to hit or path through allies).
3. The excess metric had no backing data and no definition. RESOLVED below.

The convergence premise ("everything feeds the Weighing") is genuinely true for six of seven hooks: possession, memo tone, faction reputation, the geas marker, deaths + past-Sashas catalog, and the Hael catalog all have clean existing hooks. The memo system in particular is a gift: MemoFormatter, the grievance log, tone progression, and PendingMemos are exactly the substrate the audit dialogue needs. The audit is the memo system's natural terminus, already wired. The seventh hook (excess) was an absence, not a rework, and is resolved below.

---

## Resolved design decisions

All flags from the viability pass are resolved. The plan is build-ready.

**1. Arena structure: SEQUENTIAL, committed knowingly.** Simultaneous is less code (the engine already runs many entities on a floor; five Guardians at once is a spawn list plus the existing turn loop). Sequential requires a new orchestration layer (sub-encounter state machine, spawn-on-cue, narration gates, the allies-fall-back gate). We are paying for sequential anyway, because it is the only structure that delivers the two load-bearing beats: per-category audit narration (each Guardian rises as its category is read) and the allies-fall-back-before-the-Debt moment. That moment is the emotional climax of the ending and cannot be cleanly extracted from a simultaneous melee. The orchestration layer is the keystone framework piece; budget it as the largest single chunk. Waves are rejected (they fight the per-category narration).

**2. Excess metric: UNPROVOKED CROSS-FACTION KILLS, per-faction granularity.** Not a butcher-rate (total kills / floors), because that measures *playing the game* (descending means fighting) rather than cruelty. Unprovoked cross-faction kills captures the distinction the game cares about: killing what attacks you is work; killing what would have let you pass is excess. The faction system already computes the provoked/unprovoked distinction (it feeds the orc-rep Hostile threshold). Track it cross-run with enough granularity to filter by faction, because the orc subset also feeds the Oathkeeper's fine scaling (Guardian 2). One tracked field serves both Guardian 4 (all factions) and Guardian 2 (orc subset). New field, sensible default, no migration needed per the persistence default-value escape hatch. Engineering: an increment site in combat, a run-scoped counter on GameState, a cross-run field flushed at run-end.

**3. Guardian-possesses-allies (Warden-of-Wardens savage form): FACTION-FLIP / ENRAGE, not PossessionEffect.** The possession control primitive never drove NPCs (WardenInitiated only tags a body for spell-break; it does not puppet). What we want -- turn Sasha's ally hostile mid-fight -- is a faction flip, and EnragedEffect with HostileToAll already does exactly this and is honored by ChooseTarget. Apply enrage (or flip the ally's faction string); dispel-to-restore composes through the existing spell-break path. Do NOT budget this as "reuse the possession system." Cheap.

**4. Ally combat AI: new player_ally faction + ChooseTarget gate + friendly-fire surface.** (a) New "player_ally" faction in the matrix: not hostile to player, mutually hostile with Guardian factions. (b) Gate the hardcoded "always target the player" branch in ChooseTarget behind AreHostile(myFaction, "player"); core combat AI change, needs tests. (c) The friendly-fire surface (AoE scrolls, thrown items, cleave/bonus-attack, possession targeting, auto-explore/click pathfinding) must all learn not to hit or path through allies. This (c) surface is where it goes from small to real-lift. Moderate, ripples.

**5. Audit scoring function: deterministic, over existing fields plus the new excess metric.** First-pass tier thresholds below (four tiers per faction Guardian: Allied / Diminished / Neutral / Savage). All numbers are strawman, tuned in the harness balance pass; the structure is what the scoring function is built against.

- *Warden-of-Wardens* (HallWardenPossessionsTotal + LastMemoTone): Allied = 0 possessions; Diminished = 1-2 and polite tone; Neutral = 3-5 and procedural_notice; Savage = 6+ or formal_complaint/final_audit tone.
- *Oathkeeper* (factions["orc"].State + unprovoked orc kills): Allied = orc rep Allied; Diminished = Neutral rep, 0 unprovoked orc kills; Neutral = Neutral rep, some unprovoked orc kills; Savage = orc rep Hostile.
- *Assembly of the Lost* (CumulativeDeaths + past_sashas catalog size): Allied = 0-2 deaths; Diminished = 3-5; Neutral = 6-10; Savage = 11+.
- *Auditor's Own* (unprovoked cross-faction kills, normalized by floors reached): Allied = very low rate; Diminished = low; Neutral = moderate; Savage = high.

**6. Ending determination: switch at the end of the Weighing.** Inputs all queryable. Survival (IsGameOver exists; the win path is new per decision 7). Swap availability (hael.BranchOfPassageUnlocked already exists as a computed property, directly queryable at the encounter). Clean-vs-heavy aggregate (computable from LastRunWasClean, CumulativeDeaths, faction states, the per-Guardian tiers; threshold is a design call, strawman: "heavy" if any Guardian is Savage or CumulativeDeaths high or orc rep Hostile, else "clean"). Cheap.

**7. Floor-25 / win scaffold: built from zero, clean insertion (no conflict, but no scaffolding either).** Floor 25 currently does nothing (indefinite-descent point; "Inner Court" is only a display label for floors >=18). No depth cap, no dungeon-mode victory state (PlayerWon is scenario-only). Build: a depth gate at 25, a special hand-authored arena floor-build (not procedural), a dungeon-mode victory state in GameState, and the win-flush to persistence (audit_completed, ending type). Bundle this as the "win scaffold" chunk (1-2 sessions).

**8. The three losing endings: CLOSED SET of three cause-codes.**

- `weighing_loss_guardians` -- Sasha died during the gauntlet, before reaching the Debt. The judgment killed him; he never faced what he came for. Under-Warden final memo files this as the institution's enforcement succeeding.
- `weighing_loss_debt` -- Sasha survived the Guardians, reached the Debt, and the Debt took him. The closest failure: he beat everything except the one thing he came to settle. The most pointed final memo; the debt remains unpaid, Anik unredeemed.
- `weighing_loss_refused` -- a CHOSEN loss, not a death. At the audit, Sasha can decline to be weighed: turn back, abandon the descent, leave the Paths without Anik's soul, debt open. The Under-Warden files this almost with respect -- the visiting party assessed the cost and declined. The case remains open. This is the only non-death loss; it gives the roguelike loop a dignified non-death failure state and a meta-hook (a Sasha who refused once and returns). It is an addition to v3's strict spec, deliberately included.

Death-cause routing: PlayerDeathCause is already a free string consumed by the memo evaluator and recorded into past_sashas. Add the three codes above; wire GameOverScreen (currently a generic "Defeated" that does not even display cause) to route on cause -> the right final memo/epilogue. The `weighing_loss_refused` path routes from a choice at the audit, not from death. Small presentation work plus the three authored memos (content, ours).

---

## Content surfaces this creates (ours, not engineering)

For planning the content sessions that accompany this build:

- **The audit dialogue** - the Under-Warden reading each category. Substantial; this is the climactic Under-Warden voice work. Needs to scale its text to the player's record (a clean category reads differently from a savage one).
- **Per-Guardian rise text** - the Under-Warden's annotation as each Guardian appears, plus any Guardian voice (the Oathkeeper's orc champion, the Assembly's past-self, etc.).
- **Ally-fallback lines** - the Guardians withdrawing before the Debt. The orc champion's line is sketched above; each ally needs one.
- **The three winning ending texts** - Clean Audit final memo, Theft/Defiance final memo, Swap sequence (the heaviest, with the Hollowmark payoff).
- **The three losing ending texts** - distinct final memos for the loss states.
- **Hollowmark voice through the Weighing** - she is present; the Assembly of the Lost especially needs her, given the binding-cost detonation.

This is a large content surface and the most important in the game - it is the ending. It should be drafted with the same care as the memo tones, probably across two or three focused sessions, after the engineering shape is confirmed.

---

## Sequencing recommendation

1. Resolve the open engineering questions (especially arena structure, ally AI, and the floor-25 insertion point) so the build has a concrete shape.
2. Engineering builds the Weighing framework (arena, audit-to-combat flow, scoring function, ending branch) with placeholder Guardian content.
3. Content authoring (ours) produces the audit dialogue, Guardian text, and ending texts in parallel, drafted against the confirmed structure.
4. Integration and the balance pass - the Guardian power scaling is where the wall's height gets tuned, and it needs the harness (Guardian-soak scenarios at varying record states) to validate that the wall is beatable-but-hard at the intended skill/gear level.

This is the keystone. Everything else in the game now feeds it.
