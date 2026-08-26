# §6.4 probe — prompt files

**These are the prompts. Not a copy of them, not a summary of them.** The runner composes its
request from these files and from nothing else; there are no chat strings anywhere in the
probe. ART-LOOP-PROCESS-v0 §2.3 (evidence carries its producer) and the session brief both
require it, and the reason is the kill criterion: an effort ratio computed against a prompt
nobody can read afterwards is not evidence.

## The composition rule

```
description = subject.description + " " + arm.lighting
parameters  = subject.parameters  +  arm.parameters      (arm wins on conflict)
```

A **subject** file (`subject_floor.json`, `subject_wall.json`) carries everything about *what
the thing is* — construction grammar, wear, projection, register. A **arm** file
(`arm_A.json`, `arm_B.json`, `arm_C.json`) carries everything about *how light is authored into
it* and nothing else.

**This split is the experiment's single-variable discipline made structural.** Across the three
arms of one subject, exactly one sentence and exactly one parameter (`shading`) differ. Anything
else that differed would confound the effort ratio the kill criterion rests on — the probe would
be measuring subject difficulty, not lighting treatment.

## Provenance

Every phrase carries the bible clause that produced it, and every parameter value carries the
clause or ruling that produced it. `provenance` is not commentary: when a candidate is rejected
for a register failure, the phrase that was supposed to prevent it is named in the same file.

`constant_across_arms: true` on a parameter means it is a **confound control**, not a
preference. It is held identical on all three arms so that it cannot explain a difference
between them.

## The one convention this probe knowingly departs from

`tools/pixellab/PIXELLAB_CONVENTIONS.md` — *"the single most important rule: use minimal
params"* — advises against passing `shading`, `detail`, `outline` and `view` at all.

That guidance is retired-track-era: its stated evidence is the Oryx sprite composite as a style
reference, and its authority died with that track. More to the point, **this probe cannot
honour it and still exist.** `shading` IS the arm lever; a probe of authored lighting treatment
with the lighting parameter left at default is not a probe. The lever is also the one the
surface audit measured as live on precisely this endpoint — `pixdiff` 1.0000 against a measured
noise floor of 0.3542 (`AUDIT-FINDINGS.md`, column 2).

The convention's warning is not dismissed, it is **converted into a measurement**: "treatment
miss" (usable art, wrong lighting) is a counted, reported Stage 1 outcome per arm. If the
parameters do degrade character, the counts say so in the arm's own numbers rather than in a
recollection.
