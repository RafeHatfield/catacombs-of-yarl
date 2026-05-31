# Possession Voice Surface Handoff

The full Hollowmark possession commentary surface, per section 13 of plan_possession_system.md. Roughly 60 lines across enter pools (tiered) and event-trigger pools.

Design decisions baked in:
- **Occasional fire, mostly silent.** possession_enter should fire on a random chance per possession, not every time. Hollowmark is mostly quiet during possession; when she speaks it's a small gift, not constant chatter. The roll rate is yours to tune; mostly-silent is the intent.
- **Tiered species.** Common creatures share pools (generic, generic orc, generic undead). Six bespoke hosts get their own pools. This collapses the redundant per-species work the spec ballparked at 50-80 lines down to ~60 total including all event triggers.
- **Compound-key fallback** (same as the catalog/hollowmark YAML pattern): possession_enter.hall_warden falls back to possession_enter.orc / possession_enter.undead category pools, falling back to the bare possession_enter generic pool.

Trigger key names below are my reconstruction from the spec and your VoiceLineRegistry wiring. If the canonical keys differ, the content maps by function regardless; rename keys to match what you built. Flag any mismatch.

---

## File: `config/voice_lines/possession.yaml`

```yaml
# ENTER POOLS (occasional fire, compound-key fallback)

possession_enter:
  - "Cold light through your fingers. There it is."
  - "You're in. Body's yours. Clock's running, Boss."
  - "Someone's home in there. Was. Now it's you."
  - "Fits like a borrowed coat. Doesn't it always."
  - "The drain's started. You can't feel it yet. You will."
  - "Boss. Don't get comfortable. We never get comfortable."
  - "In. Good. Make it quick and make it count."

possession_enter.orc:
  - "An orc. Big hands, small patience. Use the hands."
  - "They sing while they work, this lot. You won't. Try not to give yourself away."
  - "Orc body. It'll hold more punishment than yours. Spend it, don't save it."
  - "You're wearing one of theirs, Boss. The others won't look twice. That's the whole trick."
  - "Heavier than you're used to. Lead with the shoulder. The shoulder knows."

possession_enter.undead:
  - "This one was already dead. You're the second tenant. Mind the wiring."
  - "Cold in here, Boss. Colder than the orcs. The dead don't keep the fire going."
  - "It doesn't bleed. That's an advantage until it isn't."
  - "Something's still in here with you. Old. Quiet. Don't wake it."
  - "Wearing the dead. Marya had opinions about this. I'll spare you. Mostly."

possession_enter.hall_warden:
  - "A Hall Warden. Boss. You understand what you're doing. The altar guards will wave you right through, and the Under-Warden will write it down."
  - "You're wearing the law now. Walk like you belong. The other Wardens won't question one of their own."
  - "Careful with this one. Kessen, or one like him. They're attentive, the order. He'll know the time went missing."
  - "Institutional authority, Boss, draped over a Revenese killer. The audacity is almost artistic. Don't waste it."

possession_enter.orc_shaman:
  - "A shaman. There's still ritual in the hands, Boss. You won't know how to use it. Pity."
  - "This one was working on something before you arrived. The others will expect it finished. They'll be watching."
  - "Careful. The shamans are not rank-and-file. Wearing one draws the kind of attention the brutes never would."

possession_enter.king_bat:
  - "Boss. You're a bat. An enormous, ridiculous bat. I want it noted that this was your idea."
  - "The wings work. The poison works. You work, technically. Go be terrible at altitude."
  - "I have followed you into many bad decisions. This is the one with wings. Fly carefully."

possession_enter.troll:
  - "A troll. It heals faster than it thinks, which is to say at all. Let the body soak; it'll mend."
  - "Enormous and slow, Boss. Everything you hit stays hit. Everything that hits you, the body forgives. Within reason."
  - "Don't let the regeneration make you stupid. The body comes back. You don't. Remember which one of you matters."

possession_enter.bone_orc:
  - "One of Borrek's own. Boss. If he knew, I don't think he'd forgive it. Wear it lightly and put it back."
  - "A Bone-Orc. The king's guard. This is the body that holds the line, and you're walking it out of position. Mind what that costs."
  - "Elite. Old. Proud. The body remembers being trusted. Try to deserve it for the minute you're inside."

possession_enter.hollow_orc:
  - "This one went wrong before it died, Boss. The cult does that. It feels... thin. Get out before you learn why."
  - "A Hollow-Orc. There's a hole where the rest of it should be. Don't go looking in the hole."
  - "The orcs won't claim this one and neither should you, longer than you have to. Wear it, use it, leave it."

# EVENT TRIGGER POOLS

possession_drain_warning_25:
  - "Drain's at a quarter, Boss. Still fine. Still watching."
  - "You're thinning. Slowly. I'll tell you when slowly becomes quickly."
  - "A quarter gone from the home body. Noted. Keep working."

possession_drain_warning_50:
  - "Half, Boss. Half. Start thinking about the door."
  - "Home body's at half. This is the part where clever people leave. Are we clever today?"
  - "Halfway thinned. I'd like you back in your own skin before the math turns on us."

possession_drain_warning_75:
  - "Boss. Three-quarters. Out. Now. I'm not asking."
  - "You're almost gone. Get back. Get back. I can't pull you out of this one, I can only pull you out of the other kind."
  - "Too far, Boss. The body's nearly empty. Leave the host. Leave it."

possession_exit_voluntary:
  - "And we're back. Good. Shake it off."
  - "Out clean. Own skin. Don't make a habit of how long that took."
  - "There you are. The real one. I prefer this one, for the record."

possession_exit_host_death:
  - "The host's gone. You're out. That was closer than the clock made it look."
  - "Body died around you, Boss. You came back. The body didn't. That's the right order, at least."
  - "Out, and not a moment to spare. You felt that one. I felt it too."

possession_exit_out_of_range:
  - "Too far, Boss. Coming out. You know the rule."
  - "Lost the thread. Snapping you back. Keep the body close next time or don't bother."
  - "That's the edge. I won't hold it past the edge. Back you come."

possession_home_body_threatened:
  - "Boss. Your body. Something's found it. Get back or get over there."
  - "They're on your home skin, Boss. The real one. It can't defend itself and neither can I."
  - "Your body's being hit while you're out wearing someone else's. This is the nightmare. Move."

possession_wand_kicked:
  - "Kicked me. Boss, your hands are elsewhere and someone kicked me."
  - "I'm on the floor. Again. The indignity of this work."
  - "Get me back, Boss. I'm no use to you under a table."
```

---

## Notes for wiring

**Fire rate on possession_enter.** This pool should fire occasionally, not on every possession. Suggest a per-possession random roll (somewhere in the 20-35% range as a starting point, tunable). The other event pools fire on their actual events (drain crossing a threshold, an exit, the home body taking damage, the wand being displaced) and should fire reliably when those events occur, not on a roll. Only the enter commentary is roll-gated; the event triggers are event-gated.

**Compound-key fallback for enter.** possession_enter.{species} looks up the species-specific pool, falls back to a category pool (possession_enter.orc for any orc-family creature, possession_enter.undead for any undead-family creature), falls back to the bare possession_enter generic pool. The six bespoke keys are: hall_warden, orc_shaman, king_bat, troll, bone_orc, hollow_orc. Everything else resolves to a category or generic pool. The species-to-category mapping (which creatures count as "orc" vs "undead" for fallback) is yours to define from the entities data.

**possession_home_body_threatened firing.** This should fire when the catatonic home body takes damage while Sasha is in a host. It's the most alarming of the triggers and probably should not be roll-gated; if the home body is being hit, the player needs to know. Consider a once-per-possession cap so it doesn't fire every turn the body is under attack, but it should fire at least once when the threat begins.

**No species variants on the event pools.** Drain warnings, exits, threatened, and wand-kicked are species-agnostic. Same pools regardless of what Sasha is wearing.

---

## Design intent (context, not implementation)

Hollowmark's possession commentary carries a familiar's worn-in attitude toward a thing her person does that she has complicated feelings about. Possession is Sasha's specialty, it's morally weighty, and she's watched him do it for a long time. The voice across this surface ranges from dry tactical guidance (the generic and orc pools) to comedy (king_bat, wand_kicked) to genuine alarm (home_body_threatened, critical drain) to faction weight (bone_orc).

One line to flag specifically: in possession_drain_warning_75, "I can't pull you out of this one, I can only pull you out of the other kind." This is the binding-cost subtext at its most legible. She distinguishes between pulling Sasha out of a possession (which she can't) and pulling him out of death (which she can, at the cost of her span, per the Hollowmark binding in v3 section C-prime). A first-time player reads it as tactical confusion under pressure. A player who has learned about the binding reads it as her telling him mid-crisis exactly what she does for him. It is intended to recontextualize on replay. It is the closest the possession surface comes to stating the binding, and that placement is deliberate: a crisis moment is where she would let it slip.

The bone_orc pool leans hard on faction weight (wearing Borrek's elite guard as a small betrayal). This is intentional and sets up the Oathkeeper Guardian in the endgame: a player who wore the king's guard has more to answer for when broken faith is weighed.

---

## Still outstanding in content

After this:
- **final_audit memos** (held pending endgame lock, per the catalog_referenced handoff)
- **The endgame content surface** (audit dialogue, Guardian text, ending memos) - the largest remaining content surface, drafted after the endgame engineering shape is confirmed by the viability pass
- Possibly **Hollowmark between-runs commentary**, **NPC dialogue trees** (Borrek/Vesh/Hael), **Marya fragments**, and **mural/signpost content** - the remaining surfaces from the original content map, sequenced as engineering needs them
