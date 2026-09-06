# The device gate closed itself for two days, and only the build path noticed

**RECORDED 2026-09-05. Corrected by ruling (Rafe) in the same commit.** Not a round and not a
finding about the art — a note about the apparatus, kept because the failure is repeatable by
construction and the next person to edit a ruled constant will walk into it.

## What happened

`gate_precheck.py` condition 4 asks whether **every currently-ruled fix is present in this build**,
against a list in `docs/GATE-CONDITIONS.json`. It exists for one reason, stated in its own header:
*"A build that quietly lost a ruled fix would look exactly as good as one that kept it."*

| when | commit | what |
|---|---|---|
| 2026-09-02 | `2fe0e938` | the gate is written and hardened into the build path. Its `sheltered-joint-draws` entry asserts `SHELTER_WEIGHTS == (0.06, 0.50, 0.26, 0.18)`. **Correct — that is exactly what the code carried that day.** |
| 2026-09-03 | `c3ff7dc9` | *"three critic rounds — joints raised, hatch cut, value range opened, real walls in frame"* raises the sheltered joints to `(0.04, 0.26, 0.52, 0.18)`. **`GATE-CONDITIONS.json` is not touched.** |
| 2026-09-03 → 2026-09-05 | — | **condition 4 fails on every build.** The review build refuses to install, every time. |

**The registry was stale; the build was right.** The value in the code is the later, ruled one —
the critic-driven raise-back, documented at length in `compose_ashlar.py` beside the constant, and
the behaviour Rafe has been walking since. The entry was a snapshot of the pre-raise state.

## The two-day install blackout, and why nobody saw it

**The review-build path is the only one that consults this file.** It is also the only one that
bakes `REVIEW_BUILD.json`, which is what makes the app boot into the lit review corridor with the
rig panel instead of into the menu.

The ordinary game build calls no precheck and bakes no marker. **So for two days the only
buildable device artefact was one that cannot be walked for a review**, and the gate refusing the
walkable one was refusing it for a fix that was present. The refusal was correct on its own terms
and wrong about the world.

> **It surfaced only because #174's round needed a rig walk.** A gate that fails silently for two
> days because nothing exercises it is a gate whose next true refusal is indistinguishable from
> its background noise.

## What was changed

`docs/GATE-CONDITIONS.json`'s `sheltered-joint-draws` check now reads
`const:SHELTER_WEIGHTS==(0.04, 0.26, 0.52, 0.18)`, with the correction and its provenance recorded
**on the entry itself** rather than only here — the same discipline LOOP-PROCESS §4.3 point 5
applies to a superseded control: *the supersession is recorded where the check lives, so the next
reader finds the ruling beside it rather than a mystery.*

⚠ **Nothing else in the registry was touched.** The other ruled fixes were not re-verified against
their constants in this pass; if one of them has drifted the same way it is still drifted, and it
will announce itself the same way — as a refusal for a fix that is present.

## The structural point, which is not fixed here

**This registry does not follow the code, and nothing makes it.** A ruled constant and its gate
entry are two files that must be edited together by hand, with no test tying them; the gate only
speaks when someone tries to install. Two candidate answers, neither taken here because both are
changes to a ruled mechanism:

- derive the registry from the code at check time, so the two cannot disagree — but then it
  asserts nothing, and a lost fix would pass;
- keep it hand-written and add a **test** that fails in CI the moment a named constant moves,
  which is the same guard arriving days earlier and in a place someone reads.

Filed rather than chosen. **The rule that does apply now:** change a constant named in
`GATE-CONDITIONS.json` and change its entry in the same commit.
