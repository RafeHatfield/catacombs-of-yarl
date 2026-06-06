# Audit Dialogue Handoff: Opening + Warden-of-Wardens Beat (Calibration)

The first vertebra of the audit. This calibrates the Under-Warden's spoken-audit voice and the four-tier scaling; the other four Guardian beats will be written against this locked register and delivered as subsequent handoffs.

**Length caveat, flagged up front:** this text is first-pass and deliberately on the longer side. These are paged dialogue screens; the audit opening especially is a wall the player taps through before the first Guardian rises. We expect a trim pass once it renders and pages in-game and we can see how it feels to advance through. The opening's paragraph 4 (the order-of-reading paragraph) is the first trim target if it overstays. Build it as-is; we iterate against real screens. Do not pre-trim; we want to see the full version page first.

---

## Voice notes (for wiring and for the subsequent beat handoffs)

The audit is the first and only time the player HEARS the Under-Warden speak, vs. reading his memos. The register does not soften, but the apparatus of correspondence (headers, To/From) falls away. Tells that he is speaking rather than writing:

- He addresses the hall and marks the proceeding's stages aloud.
- He refers to Sasha in the third person ("the visiting party") where a person would say "you" -- because to him this is a reading of records, not a conversation. He drifts to "you" only when the accusation is direct; the third-person is the cold default.
- He is reading minutes that happen to be about the man standing in front of him.

The audit is cold throughout -- memo-read-aloud, the climax processed as routine. ONE grief crack is reserved for the Assembly-of-the-Lost beat (written in a later handoff), where reading Sasha's grief for his own dead selves brushes against the Under-Warden's own loss (the floor-19 mural). That crack lands BECAUSE everything around it is cold. The opening and the Warden beat below carry NO crack; they establish the relentless procedural baseline.

The two-part beat structure: the Under-Warden reads the cold audit of a category, THEN the Guardian itself speaks in a blunter register as it takes form. He warns the player of this in the opening ("their manner of speaking more direct than mine"). The contrast -- his bureaucratic framing vs. the Guardian's directness -- is the point. Each Guardian has its own voice, rougher than his.

---

## Wiring

- **The opening** fires when the player arrives in the well, BEFORE Guardian 0 (Warden) rises. This is the audit-narration gate you flagged (insert before Guardian 0). Shared across all playthroughs; not tier-scaled.
- **The Warden-of-Wardens beat** fires on GuardianRoseEvent where GuardianId = Warden. The GuardianTier on the event (Allied / Diminished / Neutral / Savage) selects which of the four versions plays. Each version has two parts: the Under-Warden's reading (fires first), then the Guardian's own line (fires as it takes form / takes its place).
- For the ALLIED tier specifically, the Guardian joins Sasha's side -- its line is spoken as it moves to the player_ally position, not as a hostile rise.

---

## THE AUDIT -- Opening (shared, all playthroughs, fires before Guardian 0)

```
The visiting party has arrived. Noted, and entered.

You may stand where you are. The proceeding does not require you to approach; the proceeding comes to you, in order, as it always has. I have your file. I have had your file for some time. It is not a short file.

Understand what this is. This is not a punishment. This office does not punish; it reconciles. Every descent generates a record, and every record, in the fullness of time, is read back to the party who generated it, so that the account may be closed. You have generated a great deal of record. We are going to read it.

It will be read in the order it accrued in significance, which is the order this office has determined, not the order you would choose. You do not get to choose the order. Few things about this proceeding are yours to choose, though I will tell you, when we reach them, which ones are.

The Wardens of this hall will assist in the reading. Each will speak to the part of the account that concerns it. You may find their manner of speaking more direct than mine. They have not had the benefit of the correspondence; I have been writing to you for some time, and they have only been waiting.

We will begin with the matter this office has documented most thoroughly.

Let the first account rise.
```

Note: "I will tell you, when we reach them, which ones are [yours to choose]" pre-loads the Refuse and Swap choices. When those choices surface later in the proceeding, this line has already established that moments of choice exist. Worth keeping the Refuse/Swap UI copy consistent with this framing (the Under-Warden offering a choice he told the player to expect).

---

## THE WARDEN-OF-WARDENS BEAT -- four tiers (fires on Warden rise)

### Tier: ALLIED (rarely/never possessed Hall Wardens)

Under-Warden:
```
The first account concerns the Wardens of this hall, and the use to which you put them. The account is short. You wore the office of the Warden rarely, or not at all. Where you passed our officers, you passed them as they were, and left them as you found them. This office notes the restraint. It is not obligated to note it; it chooses to. The Warden that rises for you rises in good order, and will stand at your side, because you gave it no cause to stand otherwise.
```
The Warden-of-Wardens (joins Sasha's side):
```
You never wore me. I remember that. Stand, and I stand with you.
```

### Tier: DIMINISHED (1-2 possessions, polite tone)

Under-Warden:
```
The first account concerns the Wardens of this hall. You wore the office on occasion -- twice by this office's count, early, before the correspondence grew firm. The intervals were brief. The officers concerned recovered their time and filed no lasting grievance. This office considers the matter substantially reconciled, and the Warden that rises rises weakened, carrying only what little you took. It will not trouble you long.
```
The Warden-of-Wardens (rises weakened):
```
You wore me once. Briefly. I have mostly forgiven the hour you took. Mostly.
```

### Tier: NEUTRAL (3-5 possessions, procedural_notice tone)

Under-Warden:
```
The first account concerns the Wardens of this hall, and it is not a short account. You wore the office repeatedly -- often enough that the order took notice, often enough that this office moved the matter from routine to review. The officers concerned have reconstructed what time they could. Some of it did not come back. The Warden that rises carries the hours you spent inside it, and it carries them as weight, and it will set that weight against you now.
```
The Warden-of-Wardens (rises hostile):
```
You made my body walk where I did not send it. You will not do it here. Here, the body is mine.
```

### Tier: SAVAGE (6+ possessions, or formal_complaint/final_audit tone)

Under-Warden:
```
The first account is the one this office has documented most thoroughly, because you gave it the most to document. You wore the Wardens of this hall as a man wears coats. You took their hours, their posts, their hands, and you returned what was left of them to duties they could no longer fully perform. I wrote to you about this. I wrote to you a great many times. You will find that what rises now has read every letter, and agreed with all of them.
```
The Warden-of-Wardens (rises savage; this is the form that possesses Sasha's allies via enrage):
```
We are the hours you stole. All of them. Every interval, every post left empty, every officer who woke not knowing where the time had gone. We have been assembled for you. Now wear this.
```

---

## What this calibration establishes (for the subsequent beat handoffs)

- The Under-Warden's spoken-audit voice: cold, third-person-default, reconciliation-not-punishment, memo-read-aloud.
- The four-tier scaling: same voice getting less forgiving without getting louder. Allied = chooses to note restraint. Diminished = substantially reconciled. Neutral = weight set against you. Savage = the gloves-metaphor register + the full memo history pulled into the audit.
- The two-part beat: Under-Warden reads (cold), then Guardian speaks (blunt). Each Guardian's own voice is rougher than his.
- The savage Guardian line references its own mechanic where applicable (Warden's "Now wear this" = the ally-possession/enrage beat).

The remaining four beats (Oathkeeper, Auditor's Own, Assembly, Debt) will be written against this register and delivered as handoffs. The Assembly beat carries the one grief crack. The Debt is unscaled (no tiers -- always full, faced alone) and is the climax, so its text is structured differently (it follows the allies-fall-back, the lonely approach).

---

## Still outstanding in audit/endgame content

- Oathkeeper beat (4 tiers)
- Auditor's Own beat (4 tiers)
- Assembly of the Lost beat (4 tiers, carries the grief crack)
- The Debt sequence (unscaled, post-fall-back, the climax)
- Ally-fallback lines (the AlliesFellBackEvent -- the Guardians who allied withdrawing before the Debt; the "we would if we could" beat)
- Six ending texts (Clean Audit, Theft, Swap, LossGuardians, LossDebt, LossRefused) on WeighingResolvedEvent
- Refuse/Swap choice UI copy (consistent with the opening's "which ones are yours to choose")
- Hollowmark through the Weighing (especially the Assembly beat -- the binding-cost detonation)
