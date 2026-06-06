# Endgame Content Handoff: Connective Tissue (final endgame content)

The last endgame content. Two combat-death endings, the ally-fallback lines, and the Refuse/Swap UI copy. With this, the endgame is content-complete and the balance pass can run against fully voiced content.

Register note up front: these are the SEAMS, not the set pieces, and two of the three want BREVITY (the opposite of the Debt). Death screens are short and final; UI copy is terse. Only the ally-fallback lines have any room, and not much.

---

## 1. THE TWO COMBAT-DEATH ENDINGS (fire on WeighingResolvedEvent: LossGuardians, LossDebt)

These return empty from GetResolution currently (you flagged them as the broader ending-texts batch). Here they are. They are DEATHS -- short, final, the opposite of the Lady's length. Do not pad them.

They are tonally distinct: LossGuardians is curt (you died among your sins, never reached the Debt; the Under-Warden files it). LossDebt aches (you reached the Debt, chose Force, lost -- the closest possible failure, and the Lady is present because you died in her hall reaching for Anik). LossDebt should hurt more than LossGuardians.

### LossGuardians (died in the gauntlet, before reaching the Debt)

Under-Warden:
```
The visiting party did not complete the proceeding. The account remains open. The reading will resume when the party returns, as the party will.
```
Closing narration:
```
You fell among your own accounts, with the Debt still unread and Anik still unreached. The Under-Warden files the hour and turns the page. There is always another descent. There is always another reading. The stairs are patient, and so is he.
```

### LossDebt (reached the Debt, chose Force, lost the fight)

The Debt (the Lady, gentle even now -- especially now; her kindness in your defeat is the ache):
```
Oh, so close. So close, and so tired. Come here. You reached so far. Rest now; you have earned the resting, even if you did not earn the having. (softer) She is still here. She is always here. You will reach her next time, or the time after. I am in no hurry, and now, neither are you.
```
Closing narration:
```
You died with your hand almost upon her, in the warm hall at the bottom of the world. The Lady receives you gently, as she receives everything, and holds you a while beside the one you came for, the two of you so near and not yet free. Above, the stairs wait. You will come down them again. You always do.
```

---

## 2. THE ALLY-FALLBACK LINES (fire on AlliesFellBackEvent, before the Debt rises)

These fire for whichever Guardians ALLIED with Sasha, as they withdraw before the Debt. The beat is the choice-not-a-wall payoff: the allies step back by WILL, not because a barrier stops them. "We would if we could." Each allied Guardian withdraws in its own register.

IMPORTANT -- which Guardians can be allies, and the Auditor's Own exception:
- Warden, Oathkeeper, Assembly can ally at their good-record tiers; their fallback is SOLIDARITY (regret, love, letting you go alone).
- The Auditor's Own only "allies" at the clean tier where it is DISAPPOINTED in you and turns away. So its fallback is NOT solidarity -- it is dismissal/boredom. It does not get a tender goodbye; that would betray the character. This is intentional. It only fires for a clean-record player (the player who'd find its dismissal a relief).

Fire only the lines for Guardians that actually allied this run. If none allied, the framing narration still plays (the Debt rises and Sasha is alone); the per-Guardian lines are skipped.

Framing narration (as the allies begin to withdraw -- plays whenever at least one ally is present):
```
The Debt rises at the head of the hall, and one by one, those who stood with you step back. Not driven. Not barred. They step back because this part was never theirs.
```

The Warden-of-Wardens (allied -- institutional, with a heart here):
```
This is past the edge of my post, and past the edge of my charter. I kept the law for you because you kept it for me. But the law does not reach the thing at the head of this hall. You go to it as you came: yourself. Go well.
```

The Oathkeeper (allied -- orcish):
```
This one we cannot carry for you, Sasha of Reven. We would if we could. We have carried much. Not this. (a beat, hammered) Stand. We will be here when you turn back around. If you turn back around.
```

The Assembly of the Lost (allied -- your own dead voice; the one or two good past-selves who stood with you; carries the past-Sashas tragedy in miniature):
```
We'd come with you. We always came with you. (dry, and it costs something) But we already tried this part, every one of us, and we are the proof of how it went. This time you go without us. Maybe that's what changes it. (a beat) Go on. We'll be watching, same as ever.
```

The Auditor's Own (NOT solidarity -- the beast losing interest; only fires for a clean-record player where it allied out of boredom):
```
Mm. No. I don't follow careful little men into rooms like that one. There's nothing in there for me -- she doesn't deal in the kind of thing I eat. (a yawn, almost) Go and be tedious with the tall pale woman. We're done, you and I. You were never going to be any fun.
```

---

## 3. REFUSE / SWAP UI COPY (the Debt choice gate)

Button labels for the three gate options, plus confirmation text. Terse. Consistent with the Lady naming the three options in her terms.

### Button labels

- Force: `Take her by force.`
- Self (Swap): `Give yourself in her place.`
- Refuse: `Turn back. Carry the debt.`

### Confirmation text

Recommendation: confirm ONLY Force and Swap (irreversible, run-ending). Do NOT confirm Refuse (recoverable -- you climb back up and can return). If confirmations feel heavy in-game, they're trivial to cut; start with these two.

Force (confirm):
```
You will tear her free against the Lady's hold. If you fall, you fall here, in the warm hall, with her almost in reach. Reach anyway?
```
[Confirm: reach / Cancel: not yet]

Self / Swap (confirm):
```
You will give yourself into the Long Hour, and she will go up without you, and never know the cost. There is no taking this back. Stay, so that she goes free?
```
[Confirm: stay / Cancel: not yet]

Refuse: no confirmation -- resolves directly to LossRefused.

---

## Notes

- Death-screen brevity is the rule: LossGuardians and LossDebt are short by design. LossDebt is the achier of the two (closest failure, the Lady present). Do not lengthen.
- The Auditor's Own fallback breaks the "we would if we could" pattern on purpose -- it dismisses rather than mourns, consistent with its inverted character, and only fires for the clean-record player who allied it out of boredom.
- The ally-fallback lines fire conditionally per allied Guardian; the framing narration plays if at least one allied; if none allied, Sasha simply faces the Debt alone with no fallback beat (the framing narration could still play, or be skipped if there's no one to step back -- your call on whether "those who stood with you step back" reads wrong when no one stood with you; if so, gate the framing narration on at-least-one-ally too).
- Confirmation dialogs: Force and Swap only. The button labels themselves are the terse-est writing in the endgame and carry the choice; the confirmations exist only because these two are irreversible and run-ending.

## This completes endgame content

With this handoff, the full endgame is content-complete:
- The audit (opening + 5 beats + Debt + 4 resolutions) -- delivered, wired
- The two combat-death endings -- this handoff
- Ally-fallback lines -- this handoff
- Refuse/Swap UI copy -- this handoff

Remaining is the balance pass (Guardian-soak against the now-fully-voiced encounter) and the in-game trim pass once the blocking paged panel lands (the Debt's opening pages are the priority trim target). After balance and trim, the Weighing is done.
