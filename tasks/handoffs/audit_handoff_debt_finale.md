# Audit Dialogue Handoff: The Debt (the finale)

The last piece of the audit, and the climax of the game. This is NOT a tiered Guardian beat -- the Debt is unscaled. It fires via GetDebt / EmitDialogue before the choice gate (or auto-resolve), per the structure you built. Drops into the "debt" YAML key.

**TRIM PRIORITY -- read this first.** This is the highest-priority trim candidate of all the audit content, and we know it going in. It is the densest text in the game arriving at the player's peak fatigue point (after the lonely 11-tile walk, at the end of a long encounter, competing with their desire to REACH THE CHOICE). When this pages in-game, the Debt is the FIRST place to trim, not the last. The caveat that complicates it: the Lady's unhurried length is arguably load-bearing characterization (she has all the time there is; a terse Lady of the Long Hour is a contradiction). So the trim will be delicate -- cut for pacing without cutting the unhurriedness that IS her. That's a real in-game judgment once it's rendered. Build it as-is, see it page, then we trim it together against the screens. Do not pre-trim.

## The Lady's register (last new voice in the game)

NOT a cold creditor. WARM. The reference is Deionarra from Planescape: Torment -- ethereal, yearning, serene, unmoored. The Lady of the Long Hour does not TAKE; things COME to her, the way rivers come to the sea, and she receives them with calm longing, like a lover welcoming a partner back into her arms -- not possessively, but as inevitability. The horror is that you cannot fight love, and she is not fighting; she is embracing. She finds it incomprehensible that things would go any other way. She is in no hurry because she cannot lose: in a Swap she loses nothing (she simply receives Sasha instead of Anik); in a Theft she only has to wait longer; in a Refuse she waits longer still. Her serenity is the serenity of the inevitable.

## Anik within the claim -- the unbearable ambiguity (by design, unresolvable)

The Lady holds Anik as collateral, visible within her light. Anik's voice surfaces through the claim, and it is IMPOSSIBLE to tell -- for Sasha or the player -- whether it is the true Anik (telling him the truth: she wasn't worth this cost, go home) or the claim wearing her shape (the creditor's best defense, puppeting the soul to send the thief away). The words are the same either way; the LOVE in them is the same either way; because the Lady speaks in the language of love natively, the manipulation and the truth are indistinguishable in both content and tone. This is the finale's final knife. The handoff text makes the ambiguity explicit in a parenthetical -- that is intentional; we want it to land, not be missed.

## Hollowmark at the Debt -- clipped, the Loiosh principle at peak load

Hollowmark is present (she's bound to Sasha; she doesn't fall back like the ally-Guardians). She speaks once at the threshold and once in the Swap resolution. At the threshold she REFUSES TO ARGUE FOR EITHER CHOICE -- she won't put her thumb on the scale even though the Swap would free her from the binding. That refusal is the most loving thing she can do. In the Swap resolution her voice "fully breaks" for the only time in the game -- but even broken it stays SHORT, and the depth is in what she refuses to say (she does not say the binding can end, that she can rest; she says only "Then I'll stay too"). Do not let her lines grow even here. Shorter is the character, especially here.

---

## THE DEBT -- the claim's terms (fires before the gate / auto-resolve, for all who reach the Debt)

Scene-set (narration, if the panel supports a non-speaker descriptive line; else fold into the Debt's first line):
```
The allies have fallen back. You have walked the length of the hall alone. At the head, where the Under-Warden presided, something rises that he does not announce, because it does not answer to him. It is not cold. That is the first wrong thing.
```

The Debt (the Lady's claim -- ethereal, yearning, a lover receiving the inevitable):
```
Ah. There you are. At last, at last. I felt you on the stairs, all that long way down, hurrying so. You did not have to hurry. I would have waited. I have such a great deal of waiting in me; it is most of what I am.

You have come such a long way, and died so many times to do it, and look at you, still warm, still wanting. I do love the wanting ones. They come to me brightest.

(and within the light, held, there is a shape, and the shape is hers)

Do you see what I keep? I keep her so gently. You needn't have worried, all this time. Nothing is hurt here. Nothing is ever hurt here. Things only come home, in the end, the way rivers come to the sea, the way you have come to me tonight without quite meaning to. She came to me. You will come to me. It was always only a question of the order, and the order does not matter to me as it matters to you.

So. Here is what is yours to choose, the small thing the warden promised you. You may take her, if you can, by force, and carry her back up into the cold and the wanting, for a while, until you both come home again, as you will. Or you may stay, and give yourself into her place, and let her go up without you, and rest -- oh, you are so tired, I can feel how tired you are from here. Or you may turn from this room and keep your debt unpaid a little longer, and we will simply wait for each other, you and I, as we have been waiting all along.

There is no wrong choice. They all end here, with me, eventually. Choose the one that lets you put the burden down.
```

Anik, surfacing through the claim (her voice, or the claim wearing it -- unknowable):
```
Sasha. (and it is her, it is exactly her, or it is exactly the shape of her) Sasha, stop. Look at you. Look at what you've spent. I'm not -- I was never worth all of this. You have to know that by now. Put it down. Go home. Let me go. (softer) I would rather be here forever than watch you do this to yourself one more time. Please. For me. Go home.
```
Ambiguity note (render as a beat/stage line if the panel supports it; otherwise it's authorial intent for tone, not necessarily shown): there is no way to tell whether that is the woman he is dying to save telling him the truth, or the thing that holds her telling him the most useful lie in her gentlest voice. The words are the same either way. So is the love.

Hollowmark, at the threshold (clipped -- refuses to argue for either; the line is not tier-scaled):
```
Whatever you pick, Boss, pick it because it's yours to pick. Not because she's tired. Not because I am. (a beat) I've got one more pull in me if you need it. Don't waste it being noble.
```

After this, the choice gate (Force / Self / Refuse) or the auto-resolve fires, per your structure.

---

## THE FOUR RESOLUTIONS (fire on WeighingResolvedEvent, after the branch completes)

These are the Debt-specific ending texts. (The two pure-combat-death losses -- LossGuardians, and LossDebt from losing the Force fight -- are deaths and come with the broader ending-texts batch; the Force WIN aftermath is below as Theft.)

### CLEAN AUDIT (auto-resolve: clean record, no Swap path -- claim satisfied by conduct)

The Debt:
```
Oh. (a pause, and something like pleasant surprise) You come to me already light. Look -- there is almost nothing owing. You spent so little that was not spent well. You may take her, then; the account closes itself, and there is nothing here to fight, because you have already paid me in the only coin I ever truly keep, which is the manner of a life.

Take her hand. Go up. (the faintest wistfulness) You will come home in your own time, both of you, and I will be glad of you then. I am in no hurry. Go.
```
Closing narration:
```
Sasha takes Anik from the light, and she is warm, and she is herself, and the long hall opens behind them. The debt is paid. They climb.
```

### SWAP (Self chosen -- the heart of the game; the binding payoff)

The Debt:
```
(she is not disappointed; she is tender) Yes. Oh, yes. I thought you might. The tired ones do, sometimes, the ones who have carried someone a long way. You give yourself, and she goes up, and the books are even, and I lose nothing, because it was always going to be one of you, and you are warm, and you are here, and you will do.
```
Hollowmark (the payoff -- the only time her voice fully breaks, and even now it is short):
```
...There it is. (a long beat) You stubborn, stupid, good man. (she does not say the rest) Then I'll stay too. To the end of it. You didn't think I'd let you do the last part alone.
```
Closing narration:
```
The Lady receives Sasha into the Long Hour, and it is not cruel, and that is the worst and the kindest thing. He laid the burden down. He is not alone. Somewhere above, a woman wakes, and does not know why she is weeping.
```

### THEFT (Force chosen and WON -- fires after the combat win; the open wound)

The Debt (she does not rage even now -- she is patient, and that is worse):
```
(unhurried, even as the claim is torn) There. You have taken her up by the root, and it will bleed, the place you tore her from, it will bleed a long time. But take her. Go. (the terrible serenity holds) You have not escaped me, Sasha. You have only made me wait, and made the waiting harder, and I will hold the torn place open until you bring her back down, or come down yourself to mend it. A debt taken by force is still a debt. I will see you again. I am always, always glad to see you.
```
Closing narration:
```
Sasha tears Anik free and runs, and she is warm and she is alive and the claim screams silently behind them, unpaid, unhealed. They climb out of the Paths with the wound open at their backs. It is not over. It will never quite be over. But she is breathing, and so is he, and for tonight that is enough.
```

### REFUSE (turned back at the threshold -- debt open, dignified withdrawal)

The Debt (gentle, unsurprised, certain):
```
(no anger, only patience) Going? Yes. Yes, I thought you might not be ready. It is a great deal to choose, and you have only died a dozen times; some come to me a hundred times before they are ready to choose at all. Go back up, then. Carry it a while longer. (the warmth is unbearable) I will keep her safe for you. I keep everything safe. And when you are ready -- this year, or in a hundred -- you will come down these stairs again, and I will say there you are, as I said tonight, and we will try once more. There is no hurry. There has never, ever been any hurry.
```
Closing narration:
```
Sasha turns from the hall and climbs back up into the world, the debt unpaid, Anik still held, the Lady's patience following him up every stair like warmth from a door left open behind him. He will come back. He knows he will come back. That is the whole of what she has, and it is enough.
```

---

## Wiring notes

- The Debt's terms + Anik + Hollowmark's threshold line all fire via GetDebt before the gate/auto-resolve. They play for everyone who reaches the Debt (all three gate shapes AND the auto-clean path -- though for auto-clean, the terms might be slightly redundant with the Clean resolution; worth checking in-game whether auto-clean should play the full terms or skip to the Clean resolution. Minor; flag if it reads odd).
- The four resolutions fire on WeighingResolvedEvent with the EndingType. CleanAudit / Swap / Theft / LossRefused map to the four above.
- Hollowmark's Swap line fires as part of the Swap resolution (after the Debt's Swap line).
- Closing narration lines: render as non-speaker descriptive text if the panel supports it; these are the final words of a run, so they want to land with weight (slower pacing, hold before the game-over/credits transition if possible).

## This completes the audit

All five beats (opening + Warden + Oathkeeper + Auditor's Own + Assembly + the Debt) are now drafted and delivered. Remaining endgame content:
- The two pure-death ending texts (LossGuardians, LossDebt-in-combat) -- deaths, distinct from the Debt resolutions above
- Ally-fallback lines (AlliesFellBackEvent -- "we would if we could", the allied Guardians withdrawing before the Debt rises)
- Refuse/Swap choice UI button copy (short -- the button labels and any confirmation text)
- Any remaining Hollowmark through the earlier Weighing beats if wanted

Then the endgame is content-complete and the balance pass (Guardian-soak against the real, voiced encounter rhythm) can run against final content.
