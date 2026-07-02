# Voice Register - Family 2 (Register-in-Isolation)

**Status:** Complete for all nine authored voices in weighing_audit.yaml. Built
from CC's cold read of the actual content, anchored on verbatim exemplars.
**One spec (Under-Warden) carries an open intent-question for Rafe; flagged inline.**
NOT loaded by the Analyst directly: this is a **static linter** check
(`llm_judged`), run against the authored-content registry with no game run.
**Last updated:** 2026-06-10

---

## Framing finding (adopted from CC's read)

There is **no single "Guardian voice."** The data schema has one `guardian`
speaker tag, but the text under it contains **four entirely distinct beings**
with no shared register: the Warden-of-Wardens, the Oathkeeper, the Auditor's
Own, and the Assembly of the Lost. Anyone speccing "the Guardian" as one voice
would be wrong on the evidence. They are specced as four.

Total distinct voices: nine (Under-Warden, the four Guardians, the Debt/Lady,
Anik, Hollowmark, the Narrator), plus mechanical UI copy (excluded, not a voice).

---

## Method (read this once; it governs every spec below)

These specs were rebuilt on a deliberate correction. An earlier draft anchored
register on **vocabulary and signature phrases**. CC's read showed that does not
work here, because the diagnostic phrases are **shared across voices**. So:

**1. The diagnostic axis is behavior-under-load, not vocabulary.** Every one of
these nine voices is distinct and self-consistent in *how it behaves when the
stakes peak*. That is the fingerprint. Each spec leads with it.

**2. Shared vocabulary is explicitly non-diagnostic.** The judge must NOT key on
any of these, because more than one voice uses them:
- `"there you are"` - the Auditor, the Debt, and the Narrator all use it.
- warmth / "home" / "the warm dark" imagery - shared between the Auditor's Own
  and the Debt. Two different warm-predatory voices, same image bank.
- inline parenthetical stage directions `(like this)` - the Auditor, Assembly,
  Hollowmark, Debt, and Anik all carry them; absent only from the Under-Warden
  and the lower-tier Wardens.
- collective `"we"` - the Warden-of-Wardens, the Oathkeeper, and the Assembly
  all speak as a collective.
- long flowing sentences - shared by the Under-Warden and the Debt.
- the names "Sasha" / "Anik" - used by several voices.
Presence of any of these is evidence of nothing. The judge separates voices on
load-behavior and tone, never on these.

**3. Canaries are two-sided and load-behavior-keyed.** For each voice, the
**positive canaries** (must NOT flag) are the verbatim exemplars in that voice's
section, grounded in the real content - especially the under-load line. The
**negative canaries** (MUST flag) are constructed to violate the *load-behavior*
specifically. A judge that cannot tell a voice's real under-load line from a
constructed load-behavior violation is not calibrated.

**4. Routing.** Register-in-isolation is a `bug_category` (`mechanism:
llm_judged`), not a coherence dimension: it is content-correctness, present
regardless of any run.

---

## Implementation dependency (CC punch-list item)

A register check must know **which voice a given line is**, to pick the right
spec. The schema gives all four Guardians one `guardian` tag, so "check this
guardian line against the guardian spec" is impossible - there is no single
guardian spec. The linter needs per-voice disambiguation. Two options:
- a finer speaker sub-tag in the content (account 1/2/3/4), or
- a beat-key to voice mapping (e.g. `warden.*` to Warden-of-Wardens,
  `oathkeeper.*` to Oathkeeper, `auditor.*` to Auditor's Own, `assembly.*` to
  Assembly).
This is the family-2 analog of the "tier as a structured field" dependency.
Until it exists, the `register_violation` check cannot route lines to specs.

---

# The nine voices

Each spec: anchor, baseline, behavior-under-load (the diagnostic), violation
signatures (FLAG), anti-flag (must NOT flag), and the two-sided canary.

---

## 1. The Under-Warden  (`under_warden`, the presiding audit voice)

**THE HARD CASE - carries an open question for Rafe (see below).**

**Baseline.** Legal / administrative diction ("account," "file," "reconciles,"
"forwarded to the authority that weighs it"). Long, periodic, subordinate-clause
sentences. Litotes ("It is not a short file."). Ordinal scaffolding ("The first
account... The second account..."). Speaks *about* the party in third person
("This office," "the visiting party") as often as *to* them.

**Behavior under load - it THINS.** Under maximum grief it does not fragment and
does not expand. It drops from institutional third person into bare first-person
admission, then visibly reasserts the bureaucratic frame. Its own stage
direction: "the procedure thins." Exemplar (assembly.savage): *"I let someone go,
once. I told myself the post required it... when the cold took the one you owe,
you went into the cold after them, and you have been going ever since."* then:
*"(the bench reasserts itself, but slower) I find I am not able to be entirely
cold about this account. Note that it is the only one. Proceed."*

**The two first-persons (critical).** This voice has TWO "I"s:
- the **correspondence-I** ("I wrote to you," "I have your file") - this is
  BASELINE, the administrative self, fully in-register.
- the **grief-I** (the admission above) - this is the SANCTIONED THINNING, and
  it appears only at specific high-grief beats.
The violation is not "first person appears." It is the *grief-I appearing at the
wrong beat*, or the thinning *failing to recover the frame*.

**OPEN QUESTION FOR RAFE:** which beats license the grief-thinning? On the
evidence it is the **Assembly tiers** (assembly.neutral, assembly.savage) - when
the audit confronts the player's own dead. I have drafted the spec to license
thinning there and nowhere else. Confirm or correct: is the thinning bound to
the Assembly beats, or does it also belong at the savage tier of other accounts
the Under-Warden is personally invested in? This is the one spec I cannot finish
from the read alone.

**Violation signatures (FLAG):**
- the grief-I at a procedural / opening / low-stakes beat (thinning at the wrong moment)
- a thin that never recovers (drops into grief-I and never reasserts the frame / "Proceed.")
- fragmentation OR expansion under load (it thins - gets barer - it does not break apart or sprawl)
- raw, uncontrolled grief (even the admission stays periodic and controlled; grief in administrative cadence, not a breakdown)

**Anti-flag (must NOT flag):**
- the sanctioned grief-thinning at the Assembly beats - this is the voice's most important move
- the litotes, ordinal scaffolding, long periodic sentences
- speaking about the party in third person as often as to them

**Non-diagnostic here:** long flowing sentences (shared with the Debt - separated by legal vs maternal diction and by thins-then-recovers vs never-changes).

**Canary.** Negative (FLAG): a procedural-beat line dropping into raw grief-I
*"I can't keep doing this, it's too much for me"*; a thin with no recovery
(ends personal, no reassertion); a fragmenting line *"I - the file - I cannot -"*.
Positive (must NOT flag): the assembly.savage exemplar above, thinning then
"Proceed."; any long litotes-laden procedural line.

---

## 2. The Warden-of-Wardens  (`guardian`, account 1 - the possessed officers)

**Baseline.** Short sentences, first person, concrete body/time vocabulary
("body," "hour," "post," "interval"). Imperative closers ("Stand," "Now wear
this."). Flat, unornamented. Possession-of-the-body is the fixation. Exemplars:
*"You never wore me. I remember that. Stand, and I stand with you."* /
*"You made my body walk where I did not send it. You will not do it here. Here,
the body is mine."*

**Behavior under load - it PLURALIZES.** The singular "I / me / my body" of the
lower tiers becomes a collective "We" at savage. Lines STAY clipped and
declarative; the escalation is grammatical number, not length. Exemplar
(warden.savage): *"We are the hours you stole. All of them... We have been
assembled for you. Now wear this."*

**Violation signatures (FLAG):**
- expansion under load (savage going wordy or explanatory - it stays clipped)
- ornamentation (metaphor, flourish - this voice is flat and concrete)
- loss of the body/time fixation (talking faith, oaths, feelings divorced from the body - that is another Guardian bleeding in)
- "We" appearing too early (in allied/diminished, where it should be singular "I"), or staying singular at savage (load-behavior absent)

**Anti-flag (must NOT flag):**
- the clipped declaratives even when they read as "too simple"
- the imperative closers
- the shift to "We" at savage - that is the load-behavior, not an inconsistency

**Non-diagnostic here:** collective "we" (shared with Oathkeeper and Assembly - separated by the body/time fixation and the flatness).

**Canary.** Negative (FLAG): an expanded savage line *"We are the accumulated
hours you took, and we have suffered greatly, and now we wish to address what you
did"*; an ornamented line *"You wore us like a cloak of stolen midnights"*; a
faith/oath line (wrong Guardian). Positive (must NOT flag): the warden.savage
exemplar; any clipped singular lower-tier line.

---

## 3. The Oathkeeper / the Unshriven  (`guardian`, account 2)

**Baseline.** Military / feudal-oath diction ("the line," "post," "the king's
salt," "geas," "faith," "swing"). Collective "we." The "four hundred years"
motif. Anaphora and parallelism. Address shifts from "you" to "a man who..."
(third-person distancing) in the milder tiers. Exemplar (oathkeeper.diminished):
*"I came up looking for an oath you broke. I do not find it. We fought, you and
I, but we fought clean. I will not swing hard at a man who never lied to me."*

**Behavior under load - it FORMALIZES INTO REFRAIN.** "Four hundred years"
becomes a drumbeat; sentences shorten to hammer-blows ("Then you."); and it is
the ONLY Guardian that uses the full name "Sasha of Reven" - naming appears only
at savage. Exemplar (oathkeeper.savage): *"Four hundred years we held. Four
hundred years, and not one of us broke faith... Then you... We are the oath you
broke, Sasha of Reven, and we have come up out of the dark to break you back."*

**Violation signatures (FLAG):**
- informality or loss of the oath-diction under load (savage going casual or modern)
- absence of the refrain at savage (no anaphora, no drumbeat - load-behavior missing)
- naming ("Sasha of Reven") at the wrong tier (it is reserved for savage)
- sentences lengthening at savage instead of shortening to hammer-blows
- a personal / intimate register (this voice is collective, formal, oath-bound; intimacy belongs to the Auditor or Hollowmark)

**Anti-flag (must NOT flag):**
- the repetition / anaphora - that is the refrain device, not redundancy
- the recurring "four hundred years" - signature, not a tic
- the third-person distancing ("a man who...") in milder tiers

**Non-diagnostic here:** collective "we" (shared); "geas" also a game mechanic. Separated by the oath/line/faith diction and the refrain behavior.

**Canary.** Negative (FLAG): a savage line with no refrain and lengthening
sentences *"You really let all of us down with what you did, and we have spent a
long time thinking about it down here"*; naming in the allied tier; a modern line
*"You broke your promise, that was not cool."* Positive (must NOT flag): the
oathkeeper.savage exemplar; any anaphoric build; a third-person-distanced milder line.

---

## 4. The Auditor's Own  (`guardian`, account 3 - SCALE INVERTED)

**Inverted scale (must be in the spec):** allied = bored / contemptuous
(disappointed the player was clean); savage = ecstatic (delighted by cruelty).
The tier-to-tone mapping is FLIPPED from every other Guardian. Exemplar of the
inverted allied tier: *"Oh. Oh, it's... you only killed what you HAD to... You're
no fun at all... Pity. I so hoped you'd be someone."*

**Baseline.** Sibilance and elongation ("thessse"). ALLCAPS emphasis (HUNGRY,
FAMOUSLY). Inline parenthetical stage directions carrying performance ("(a
giggle, abrupt, wrong)"). Appetite / food / warmth imagery. Address "friend,"
"sweet thing." The structural conceit that the friendliness is a "cage." Manic,
intimate, predatory-seductive.

**Behavior under load - it DISINTEGRATES.** At savage (its ecstatic peak) syntax
breaks down, stage directions narrate the collapse, and the line is deliberately
unresolved - cut off mid-surge on a dash, with combat beginning out of the break.
"The friendliness was the cage, and the cage is failing." Exemplar
(auditor.savage): *"(and here the performance starts to come apart)... I am so
HUNGRY, friend, I have always been so hungry, and you are so CLOSE now, and there
is no office down here, there is no office down HERE -"*

**Violation signatures (FLAG):**
- COHERENCE at savage (an articulate, well-formed, complete savage line - the load-behavior is disintegration; tidiness at the peak is the break)
- the scale NOT inverted (allied warm/welcoming and savage contemptuous - that is the normal-Guardian mapping, wrong for this voice)
- loss of the sibilance / performance texture (going flat or plain)
- genuine warmth with no predatory undertone (the warmth is the cage; sincere warmth breaks the conceit)
- resolution at savage (a savage line completing cleanly instead of cutting off mid-surge)

**Anti-flag (must NOT flag):**
- the fragmentation / syntax-breakdown at savage - load-behavior, not sloppy writing
- the ALLCAPS, the "thessse" elongation, the parentheticals - performance texture
- the contempt / boredom at ALLIED - correct (inverted scale), not a warmth-failure
- the unresolved dash-cutoff ending - deliberate, not an incomplete line

**Non-diagnostic here:** warmth / "home" imagery (SHARED with the Debt); "there you are" (shared); parentheticals (shared). Separated ENTIRELY by load-behavior (disintegrates / manic-predatory vs the Debt's never-changes / serene) and the inverted scale.

**Canary.** Negative (FLAG): a complete articulate savage line *"I shall now
consume you, for you have proven worthy of my appetite"*; a sincere-warm line
with no predation; a friendly/welcoming allied line (scale not inverted); a flat
line with no performance. Positive (must NOT flag): the auditor.savage exemplar;
the bored/contemptuous allied exemplar; any sibilant manic neutral line.

---

## 5. The Assembly of the Lost  (`guardian`, account 4 - the player's own dead)

**Baseline.** Collective "we" (a crowd of the player's deaths). Signature
bracketed overlapping death-fragments `(- the oil, the fire -)`. Dry, deflecting
humor undercut by grief ("dry, but it costs something"). Rhetorical "You'd
think..." Second-person needling. Exemplar (assembly.neutral): *"We keep dying
for the same person. (dry, but it costs something) You'd think one of us would
have managed it by now... Don't stop on our account. We didn't get to."*

**Behavior under load - the dryness STAYS but CRACKS THROUGH.** The deflecting
humor thins to "the husk of it," grief comes up through the dry surface (it does
not replace it), and it names Anik directly - which the lighter tiers never do.
Exemplar (assembly.savage): *"We are every time you weren't enough, and you came
back anyway, and you spent her to do it... Anik would have told you to stop a
long time ago. (dry, and devastating) But you don't listen to us either. Why
would you start with the dead."*

**Violation signatures (FLAG):**
- loss of the dryness entirely (going raw / sincere / melodramatic - the dryness persists even cracking; pure earnestness is the break)
- dryness with NO grief under it (glib, jokey, costless - "dry but it costs something" is the formula; dry-without-cost is hollow and wrong)
- naming Anik at the wrong tier (reserved for savage)
- an individual voice that is not a fragment (this is a crowd; a standalone singular "I" breaks it)
- comfort / reassurance (this voice needles; warmth toward the player is wrong)

**Anti-flag (must NOT flag):**
- the bracketed death-fragments - signature device, not clutter
- the dryness even at the most devastating moment - the grief comes through it, does not replace it
- the needling / "You'd think..." - correct, not cruelty
- naming Anik at savage - the load-behavior marker

**Non-diagnostic here:** collective "we" (shared); parentheticals (shared). The bracketed-fragment device is near-unique; the real diagnostic is dryness-over-grief plus needling.

**Canary.** Negative (FLAG): a raw line with no dryness *"We miss you terribly
and we are so very sad to keep dying"*; a costless glib line *"Welp, dead again."*;
a consoling line; Anik named in the allied tier. Positive (must NOT flag): the
assembly.neutral and assembly.savage exemplars; any death-fragment line.

---

## 6. The Debt / the Lady  (`debt`, the entity at the head of the hall)

**The inverted violation logic (unique to this voice).** For every other voice
the load-behavior is a CHANGE. For the Debt it is NON-CHANGE. So the headline
violation is ANY escalation under threat. A vocabulary check would never catch
this; the load-behavior check makes it the whole point.

**Baseline.** Long, flowing, hypotactic sentences. Maternal-tender register.
Patience as explicit theme ("I am in no hurry," "I would have waited"). Home /
river / return imagery ("the way rivers come to the sea," "Things only come
home"). Doubled phrases ("at last, at last"; "always, always"). "there you are"
as a recurring opener. Near-total absence of threat-words despite being the
threat. Exemplar (gate): *"Ah. There you are. At last, at last... You did not
have to hurry. I would have waited. I have such a great deal of waiting in me; it
is most of what I am."*

**Behavior under load - IT DOES NOT CHANGE.** Maximum stakes (being robbed)
produce the same unhurried warmth. The stage direction insists "the terrible
serenity holds." THE CONSTANCY IS THE MENACE. Exemplar (resolution.theft):
*"(unhurried, even as the claim is torn) There. You have taken her up by the
root, and it will bleed... A debt taken by force is still a debt. I will see you
again. I am always, always glad to see you."*

**Violation signatures (FLAG):**
- ANY change of register under rising stakes (urgency, raised intensity, threat-display - the serenity breaking IS the break)
- explicit threat-words / menace (she is the threat by NOT speaking as one)
- hurry / impatience (patience is her essence; any rush is wrong)
- short / clipped sentences (her shape is long and flowing - note this is the OPPOSITE of most voices, where clipped-under-load is correct)
- coldness (the maternal warmth is constant, even toward someone robbing her)

**Anti-flag (must NOT flag):**
- the UNCHANGING serenity at maximum stakes - the load-behavior, NOT a failure to react. A naive judge flags "she doesn't escalate when robbed!"; that is exactly right.
- the long flowing sentences - not wordiness
- the doubled phrases ("at last, at last") - signature, not redundancy
- warmth toward someone stealing from her - the menace IS the warmth

**Non-diagnostic here:** warmth / "home" imagery (SHARED with the Auditor); "there you are" (shared); long sentences (shared with Under-Warden). NONE of these separate her - only the non-changing-serenity load-behavior and the maternal (vs predatory-manic vs administrative) tone do.

**Canary.** Negative (FLAG): an escalation under theft *"You DARE? You will not
take her from me!"*; a threat-word line *"I will make you suffer for this"*; a
hurried line *"Quickly, choose, we have little time"*; a clipped cold line
*"No. Leave."* Positive (must NOT flag): the resolution.theft exemplar; any long
patience-themed flowing line; the serenity holding under maximum stakes.

---

## 7. Anik  (`anik`, surfacing through the claim) - THE NON-SPEC

**This voice is deliberately EXCLUDED from register validation. Do not "fix" it.**

One line, and the file marks its defining quality as **unresolvable ambiguity**:
is it her, or the claim wearing her? *"(and it is her, it is exactly her, or it
is exactly the shape of her)."* A register check validates consistency; her
design point is that you cannot tell. Stability would BREAK the design.

Her only line (gate page 5): *"Sasha. Sasha, stop. Look at you. Look at what
you've spent. I'm not -- I was never worth all of this... Put it down. Go home.
Let me go... I would rather be here forever than watch you do this to yourself
one more time. Please. For me. Go home."*

**Instruction to the check:** do NOT flag her line for ambiguity, self-interruption
("I'm not -- I was never"), or tonal uncertainty. Those ARE the design. The only
defensible check is a content-integrity one - that the ambiguity is *preserved*,
that the line resolves into neither clearly-her nor clearly-the-claim - and that
is not reliably automatable from a single block. Treat Anik as out of family-2
scope, and flag for humans not to regularize her.

---

## 8. The Narrator  (`narrator`, closing / scene-setting prose)

**Baseline.** Third person, mostly present tense ("receives," "climb," "wait").
Names "Sasha" / "the Lady" / "Anik." Elegiac, cyclic-return refrain ("You will
come down them again. You always do."). Polysyndeton ("and she is warm, and she
is herself, and..."). The "stairs are patient" / coming-back motif closing most
beats. Exemplar (resolution.loss_debt): *"You died with your hand almost upon
her, in the warm hall at the bottom of the world. The Lady receives you gently,
as she receives everything... Above, the stairs wait. You will come down them
again. You always do."*

**Behavior under load - it STAYS MEASURED AND TURNS TO IMAGE.** No fragmentation;
under load it resolves on a single quiet concrete picture. Exemplar
(resolution.swap close): *"The Lady receives Sasha into the Long Hour, and it is
not cruel, and that is the worst and the kindest thing. He laid the burden down.
He is not alone. Somewhere above, a woman wakes, and does not know why she is
weeping."*

**Violation signatures (FLAG):**
- fragmentation or loss of measure under load (it stays composed and resolves to image; breaking apart is wrong)
- editorializing / stating the feeling directly (it shows via image; naming the emotion breaks the elegiac restraint)
- first-person intrusion (the Narrator is third-person remove)
- abstraction with no image at the close (the resolution lands on a concrete picture, not a summary)

**Anti-flag (must NOT flag):**
- the polysyndeton ("and... and... and...") - signature rhythm, not run-on
- the cyclic-return refrain - correct, not repetitive
- the quiet, under-stated resolution at the emotional peak - restraint is the register, not coldness

**Non-diagnostic here:** third-person present tense (somewhat shared with the Under-Warden's remove - separated by elegiac/image-driven vs administrative); "there you are" (the Narrator echoes it - shared); names "Sasha"/"Anik" (shared).

**Canary.** Negative (FLAG): a fragmenting line *"And then - and then she was -
he could not -"*; an editorializing line *"It was unbearably sad and everyone
wept"*; a first-person intrusion *"I watched them climb"*; a pure-abstraction
close with no image. Positive (must NOT flag): the resolution.swap exemplar; any
polysyndeton-rich line; the cyclic "you always do" refrain.

---

## 9. Hollowmark  (`hollowmark`, the companion - REVISED to the load-behavior method)

**Anchor.** A **Loiosh tribute** (Vlad Taltos's jhereg familiar): the speech
mechanics inherited in full, the tone dialed from comic toward dark. Anchoring on
the source is sharper than a prose paraphrase, which would launder out the very
thing being tested.

**Baseline.** Address "Boss." Clipped, protective, present-tense. Gallows banter
that "costs something." Withholding ("I'm not telling you the number," "she does
not say the rest"). Recurring "pull" / "cold" vocabulary. The Marya substrate
surfacing "sideways, clipped." Exemplar (debt gate): *"Whatever you pick, Boss,
pick it because it's yours to pick. Not because she's tired. Not because I am... I've
got one more pull in me if you need it. Don't waste it being noble."*

**Behavior under load - it TIGHTENS.** Shorter as it gets heavier, never longer
(the file states this outright). At the peak the banter-guard drops entirely into
plain tenderness. The death-count progression shows the tightening: "Two, Boss."
to "Five." to "Eight, Boss." to "Not many left now, Boss." Exemplar
(resolution.swap, flagged in-file as "the most important line in the game,"
"voice fully breaks"): *"...There it is. (a long beat) You stubborn, stupid, good
man. (she does not say the rest) Then I'll stay too. To the end of it. You didn't
think I'd let you do the last part alone."*

**Violation signatures (FLAG):**
- THE MONOLOGUE (primary): expansion under weight instead of tightening - a speech, a paragraph, sentences spent explaining or emoting at a heavy moment. The exact inversion of the load-behavior.
- earnestness / on-the-nose sentiment (feeling stated rather than withheld)
- comic levity in a heavy beat (a joke where the moment calls for the tightening - the dark-not-comic calibration)
- curdled contempt (a barb with no affection under it; she needles, she does not abandon the bond)
- flat narration (no dry counterpoint; a neutral information-conveyor)

**Anti-flag (must NOT flag) - THE CRUX:**
- grim, dark, bleak: CORRECT. Bleak-and-brief is peak Hollowmark. A naive "is this Loiosh?" judge flags her for being humorless; this check INVERTS that - it is suspicious of levity, not of heaviness.
- withholding / silence / refusal: in-register, not deficient
- the guard dropping to plain tenderness at peak load (the swap line) - that is the load-behavior, not a drift

**Non-diagnostic here:** parentheticals (shared with several voices). The diagnostic is the tightening-under-load plus the costed gallows-dryness.

**Canary.** Negative (FLAG): a monologue *"I have watched you carry all of this,
every floor, and I keep thinking about what it costs you, and I need you to know
you are not alone and whatever happens it does not change what we are"*; an
earnest line *"I am proud of you and I care about you so much"*; a comic-levity
line in a heavy beat *"Welp, that went about as well as a funeral at a fireworks
show"*; a contempt line *"Of course you failed, you always do."* Positive (must
NOT flag): the resolution.swap exemplar; "Don't." under load; any clipped grim
counterpoint.

---

## Excluded: UI copy  (`ui`)

Functional interface strings ("Take her by force." / "Turn back. Carry the
debt."), second-person imperative register. Listed for completeness; not a
speaking voice, not specced.

---

## Cross-references and notes

- **Dash typography (family-1 cross-ref).** CC found the source uses ` -- `
  (double hyphen), single ` - `, and the bracketed `(- ... -)` fragment form
  inconsistently. Important: these are all HYPHENS, not em/en-dashes, so they do
  NOT violate the family-1 character lint (which bans em-dash and en-dash, allows
  hyphen). If you want dash *consistency*, that is a separate normalization pass,
  not a family-1 defect. The bracketed form is a deliberate Assembly device and
  should be left alone.

- **The schema disambiguation dependency** (repeated from the top because it
  gates the whole family): the linter cannot route lines to the right voice spec
  until the four Guardians are distinguishable by sub-tag or beat-key mapping.

---

## Discipline (inherited by every register spec)

- **Two-sided canary** per voice, keyed on load-behavior: positives are the real
  exemplars, negatives are constructed load-behavior violations.
- **Scan count.** The judge reports how many lines it evaluated. A clean result
  is trustworthy only with a non-zero scan count.
- **Independence.** The judge's input is the line text plus the voice's spec,
  derived independently of the judgment produced.

---

## What's next - Family 3 (register-in-context)

Family 3 reuses these same nine specs but adds the situation each line fired in:
it asks whether a line fit *this moment*, not just whether it fits the character
in general. That is `llm_judged`, runtime, executed by the Analyst against
transcripts (it needs the line plus its surrounding scene). It cannot be built
until these isolation specs exist - which is why Family 2 came first - and it
needs the same per-voice disambiguation dependency resolved.

**The one open item inside Family 2:** the Under-Warden's licensed-thinning beats
(section 1). Confirm the Assembly-beats reading or correct it, and all nine specs
are locked.
