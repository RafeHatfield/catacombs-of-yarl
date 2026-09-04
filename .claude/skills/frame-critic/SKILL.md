---
name: frame-critic
description: Judge an art round the only way art rounds are judged in this project — a fresh blind critic's eyes on the delivered frames. Use when an art build is ready to be assessed, before any build goes to the device, and whenever an install is refused for want of a verdict. Also covers the loop guards that stop a round grinding.
---

# The frame critic

**An art round is judged by eyes on delivered frames. Nothing else judges it.**

A fresh blind `claude -p` seat is shown a small deck of finished pictures — this build's capture,
the asset bar, the last frame Rafe approved, and one **picture-plant** he personally culled —
shuffled and unlabelled. It ranks them, says which it would ship, and flags anything with an
obvious defect. That is the verdict.

```
.claude/skills/frame-critic/run_frame_critic.sh
```

```
exit 0  PASS   the seat would ship this frame, flagged nothing in it, and ranked it at or
               above the last Rafe-approved frame and near the asset bar. Any round.
exit 1  FAIL   any of those missing; the flip list is in CRITIC-VERDICT.json, verbatim
exit 2  VOID   it did not catch the plant. Findings are NOT READ. Stop and fix the judge.
exit 3  STOP   a loop guard fired. Read STALL-REPORT.md, end the turn, hand it to Rafe.
exit 4  refused — a precondition failed and it says which
```

**PASS is reachable at any round and the guards never gate it** — they decide when to stop and
ask, never what may ship.

---

## 1. Why it is shaped like this

Two collapses, measured, both of the review layer, both the same shape: **the apparatus became
the judge, and then the apparatus broke.**

**One — the instruments became the judge.** At the wall device gate of 2026-08-27 every
instrument in the repo was green and the phone still said no. A gate FAIL against a fully green
instrument set is not a tuning miss. It says the thing being measured and the thing being judged
had come apart, and the numbers had been holding the gate for some time before anyone noticed.

**Two — the plant stopped being in the picture.** Wall rounds 9 and 10 both went VOID because the
generated plant differed from the family in **0.54% of pixels, in 21 cells**: since the cap pass
the cell's base is a cap window and the wall family's top tiles are never drawn, so ruining the
wall tiles ruined almost nothing. The control was *downstream of the engine*, so an engine change
neutralised it silently. Rounds 3 and 6 died the same way for a different reason.

The answers follow directly:

| the failure | the answer |
|---|---|
| a number held the gate and drifted from the eye | **the judge is eyes on pictures.** No threshold in it to drift |
| the control was generated, so the engine could disarm it | **the plant is a picture.** Bytes in `morgue/`. An engine change cannot touch a picture |
| a documented rule was not remembered | **the install script is the choke point.** The gate is the thing that installs |
| a round can iterate forever | **loop guards stop the line** and escalate, rather than grinding |

---

## 2. Instruments gate nothing

Every `measure_*.py`, every census, every screen in this repo **stays exactly where it is and
keeps running.** They are builder's tools: they tell you where to aim between rounds, they are
cheap, and they are often the only way to find out *why* a frame failed.

They do not gate. Not the round, not the install, not a landing. A number that can hold a gate
will eventually be optimised against, and it will silently outcompete every clause that has no
number — which is most of the register (bible §13.4).

An instrument result belongs in a round report and in the aiming. It never appears in a
CRITIC-VERDICT.

---

## 3. The deck

Four frames, shuffled, unlabelled, named `1.png`–`4.png` in a working directory **outside the
repo**:

1. **the build** — captured fresh by the command in `docs/FRAME-CRITIC.json`
2. **the asset bar** — the commercial bar (§13.3: measurements leave, pixels never do; the crop
   is written outside the repo and nowhere else)
3. **the last Rafe-approved capture of the same surface**
4. **the picture-plant** — one frame from `morgue/`, matching this round's surface

The same crop is applied to every Yarl frame so the crop can never become the tell. The shuffle
is seeded from the build id and the round number, so the deck is reproducible from the verdict
file alone — a deck nobody can reconstruct is a verdict nobody can check.

The seat gets the fiction, the tone, and the questions. **It never gets the bible**
(LOOP-PROCESS §3.2), never gets code, coordinates, thresholds, or any hint of which frame is
which.

The questions are fixed:

> Rank these for craft. Which would you ship? For the best and worst, say concretely why.
> Flag any image with an obvious defect.

---

## 4. The plant — the self-test that runs every round

**Declared before the first round, not negotiable afterwards:**

> The plant must land **worst or flagged**, and must not appear in SHIP.

Miss it and the round is **VOID**: its findings are not read, not discounted — void. A soft
critic's findings are worse than no findings because they will be acted on.

This needs **no vocabulary list**, and that is the point of moving to a picture. The generated
plant it replaces needed one — a hand-maintained list of ruin words — and that list went wrong in
every direction a list can. It carried `lichen`, which no plant ever contained. It lacked `hole`,
the plainest word for the plant's most prominent feature, for three rounds. A list widened by
reading transcripts is a test derived from its own outcome. **A rank has no vocabulary.**

### What the plant does NOT test — write this down, it matters

**The plant tests for softness, not for ordering.** It answers one question: would this seat ship
a frame the human gate already rejected? A seat that would is soft, and a soft critic's findings
are worse than none.

It does **not** answer whether the build is better than the plant, and **a blind seat's RANKING
does not reproduce Rafe's culls.** Three rounds, three different seats, three different shuffles,
same result. It is the most important thing in this file:

| run | what happened |
| --- | --- |
| **first live wall round** | the seat flagged all three frames, shipped none, and **ranked the plant first** — a frame Rafe culled for grey walls, put above the current build |
| **the plant self-test** | the build slot deliberately held `keyline-floor.png`, a frame Rafe culled outright. The seat **ranked it best of three and did not flag it.** It listed that frame's magenta placeholder walls in its flip list, so it had seen them — it simply did not call it a flagged defect |
| **the round that found the padded bar** | a different seat on the same wall build **ranked the plant above it again**, and ranked the commercial asset bar last — for a black band the crop box had put there |
| **the round that found the white margin** | a third seat, a third shuffle, **the plant above the build again** — and the bar last again, this time for the example sheet's own white paper margin |
| **the first round under the progress guards** | a fourth seat put the plant **first in the deck and flagged nothing in it.** The round went **VOID** — the first time the control actually fired, and the strongest form of the same finding |

Every one of them still came out **FAIL** with `SHIP: NONE`, and no gate opened. That is the whole
protective claim and it is narrower than it sounds:

> **Rank is never sufficient on its own.** PASS requires the seat to put this frame in SHIP,
> unflagged — and, since the progress amendment, *also* to have ranked it at or above the last
> approved frame and near the bar. Rank is a **necessary** condition added on top, never a
> substitute: a build that outranks everything and is not in SHIP still fails. What the mechanism
> guarantees is that a build reaching the phone is one a blind seat said it would ship. It does
> **not** guarantee the seat's ordering agrees with the human gate's — the evidence above is that
> it does not, which is exactly why rank was added as a filter and not as a verdict.

Two ordering facts remain **recorded and reported, never scored**: `outranked_build` when the
plant sits above the build, and `every_frame_flagged` when a seat flags everything including the
commercial bar and its flag therefore carries no discrimination. Folding either into the verdict
would say the wrong thing — VOID means *stop and fix the judge*, and there is nothing wrong with
the judge in either case.

Rank does one more job, and only one: it is **the progress signal the loop guards read** (§5).
Deciding when to stop and ask a human is a much weaker use than deciding what ships, and it is
the use the evidence supports.

A seat too harsh ever to PASS is a real failure too, and it belongs to the **stall** guard, not to
the plant.

### ⚠ One assumption, stated rather than buried

The amendment that introduced these guards described PASS as *"still = ranks at/above the
last-approved frame and near the bar."* On main, PASS was SHIP-based and said nothing about rank,
so *"still"* cannot mean *unchanged*. It is read here as **not loosened**: PASS is the conjunction
of the rule that shipped and the comparative rule. That can only refuse more builds than either
reading alone, which is the safe direction for an install gate to be wrong in.

If rank alone was meant, drop the two SHIP terms from the verdict line in `frame_critic.py`. It is
one edit, and it **loosens** the gate, so it is Rafe's to make.

**The rule was declared before the first round and was not touched after it.** LOOP-PROCESS §8: a
bar found wanting mid-run is held frozen, cleared honestly, and impeached in the same report —
never re-tuned once the answer is visible. This section is that impeachment.

### The morgue

`morgue/` holds frames **Rafe personally culled at the device gate**, with his verbatim words and
the commit whose build produced them. `MORGUE.json` records a sha256 per entry and the runner
refuses to start if any file has changed — a plant that can be edited is a plant that can be
softened.

Entries are **tagged by surface** and the deck draws a plant of the round's surface. A floor plant
in a wall round gets caught for its magenta wall mocks: the right image flagged for the wrong
reason, which is not a control at all.

**Adding an entry** is the correct response to any device-gate cull. One file, one block in
`MORGUE.json`, with the quote and the commit.

---

## 5. The loop guards — they measure progress, not rounds

The line stops rather than grinding, **and it does not stop a lane that is working.** Every stop
writes `STALL-REPORT.md` and is a **LOOP-PROCESS §1.1.4 ruling trigger** with that report as its
evidence.

### The signal

**Where the build ranked** in that round's blind shuffled deck, against the asset bar, the last
Rafe-approved frame and the plant. Normalised so decks of different sizes compare:

```
rank_score = (deck_size − rank_position) / (deck_size − 1)      1.00 first, 0.00 last
```

It costs nothing extra — the round already produces it — and it is a judgement about the picture
rather than about the apparatus. **A round count is not.** The five-round park it replaces counted
rounds, which is the wrong quantity in both directions at once: five rounds that are getting
somewhere should keep going, and two that are not should already have stopped.

**The seat is never told the round number, the history, or that anything is being tracked.** Not
in the prompt, not in the deck, and not in the path it sits in — the working directory is named by
a hash, because it used to be named `<lane>-r7` and that is the seat's own cwd.

### The guards, in the order they are checked

| guard | fires when | why the order |
|---|---|---|
| **broken judge** | the plant is missed twice running | nothing past it is readable, so every guard below would be reasoning about rounds §4 forbids reading |
| **no change** | two consecutive FAILs whose delivered frames are within **2 bits of a 256-bit perceptual hash** | the cheapest true statement available: the fix did not reach the picture at all |
| **thrash** | the same flip item across two consecutive FAILs **and no movement in rank** | the same request twice, with nothing to show for it |
| **stall** | **3** readable rounds with no new best rank | matching the best is not progress; the lane is not converging |
| **ceiling** | **15** rounds on the lane | the backstop, and it should never be the one that fires |

**`two strikes` stays, as the builder's judgement overlay — reported, never a stop.** A flip item
can legitimately survive a round the build won on every other axis, and stopping there sends a
ruling to Rafe about a lane that is working. That is what `thrash` adds the rank condition for:
same substance, one more condition, and the condition is exactly what separates a stuck lane from
a busy one. When the advisory speaks and the guard does not, the runner says so and the builder
decides.

A **VOID** round's rank is not evidence — §4 says its findings are not read, and that has to
include its rank — so void rounds are excluded from the progress series. They still count toward
the ceiling: they consumed a round.

### The series is in the verdict files

Every verdict carries `progress`, including the **whole rank series to date** and each round's
perceptual hash. Not merely derivable by walking `history/` — written into the file, so it is in
the diff, in the PR, and in the stall report. **A counter a restart can clear is a suggestion with
a number in it**, and so is one that lives only in a directory listing. Clearing this means
deleting committed files.

**When a guard fires: write nothing else, run no further rounds, end the turn.** Say plainly that
the line stopped, which guard fired, and where the report is. Do not summarise the report away —
Rafe reads it.

---

## 6. The install gate

`critic_gate.py` is the one implementation, with two callers: `build_review_app.sh` runs it before
it exports, and a PreToolUse hook (`.claude/hooks/critic_install_guard.sh`) runs it against any
shell command that would put a build on a device. Two callers, one implementation — a gate
reimplemented in a second place has two behaviours and the second one is always the lenient one.

It requires **CRITIC-VERDICT.json to exist, to match this working tree's build id exactly, and to
read PASS.** The build id folds in the commit, every tracked change and every untracked file, so
a recomposed family moves it even when the commit does not.

**The override is visible:**

```
YARL_SKIP_CRITIC=1 tools/tier1_walls/device.sh build
```

installs, and stamps `SKIPPED-REVIEW` into the review marker. The app **draws it on screen** and
reports it in its `BUILD IDENTITY` line for as long as that build is on the handset. It exists for
producing a build to *measure*; nothing walked on a SKIPPED-REVIEW build is a gate verdict. An
override nobody can see from the phone is the same as no gate.

---

## 7. Running a round

1. Build the thing. Aim with instruments as much as you like.
2. `run_frame_critic.sh`.
3. **PASS** — the round ends. `CRITIC-VERDICT.json` goes in the PR diff and is named in the PR
   body. The device gate is next, and it is Rafe's.
4. **FAIL** — apply the flip list, run again. Automatically, without returning to a human
   (§1.1.2). This is the loop. Read the `== progress` block: it says where the build ranked,
   whether that is a new best, and how far the picture actually moved. **A round that moved the
   picture very little is a round to look at before spending another seat** — the no-change guard
   will say so eventually, but it needs two rounds to say it and you have the number now.
5. **VOID** — stop. The judge is what failed, not the art. Nothing from that round is evidence,
   including its rank. Check whether the plant is actually in the picture the seat saw.
6. **STOP** — end the turn and hand `STALL-REPORT.md` to Rafe.

If the runner prints the **two-strikes advisory** and does not stop, that is working as intended:
the same request survived, but the build moved in the deck. Decide whether to keep going. That
judgement is yours; `thrash` only takes it out of your hands when the rank has stopped moving too.

`--no-capture` replays the round on the frame already on disk. `--build-frame <path>` puts a
chosen frame in the build's slot — that is the judge's own self-test, it runs on its own
`-selftest` lane so it cannot touch a real lane's progress series, and its verdict is marked
`self_test` and can never open the install gate.

`--check-guards --history <dir> --lane <name>` evaluates the guards against a history without
running a round or spending a seat. It is how the fixtures in `evidence/guard-fixtures/` drive
the real `guards()` rather than a copy of it.

---

## 8. Configuration

`docs/FRAME-CRITIC.json` — surface, capture command, crop, asset bar, approved capture. Editing
it is how a session moves the critic to a new surface. **Nothing content-specific lives in this
skill**, so that a content change has nothing here to break.

`approved_capture` is **read off the record, never chosen.** It is the frame Rafe approved, with
his words and the commit. If the record contains no approval for a surface, it is `null` and the
deck runs three frames — picking one yourself means choosing the baseline your own work is judged
against, which is the conflict the comparative frame exists to remove.

---

## 9. Proving it still works

The mechanism gets the discipline it enforces. Three scripts, none of which reimplements what it
tests — they drive the real gate, the real guards and the real build id:

```
python3 .claude/skills/frame-critic/prove_gate.py       > /tmp/out.txt 2>&1   # 12 cases
python3 .claude/skills/frame-critic/prove_build_id.py                        # 3 properties
python3 .claude/skills/frame-critic/frame_critic.py --check-guards \
        --lane guard-two-strikes \
        --history .claude/skills/frame-critic/evidence/guard-fixtures/two-strikes
```

⚠ **Do not redirect a proof's output into the repo.** Any untracked file written into the tree
while a check is running moves the build id under it, and cases go red — the mechanism working
correctly and the test being wrong. Write outside the tree and copy the transcript in.

Results and what they found are in `evidence/PROOF.md`. Run them after touching anything in this
directory.

## 10. What this does not do

It does not gate non-art work. It does not judge assets on a contact sheet — every frame in the
deck is a delivered frame from the production renderer, lit, at device pixel size (§2.1). It does
not land anything: **a critic PASS ends a round; only Rafe's walk lands an asset** (§1).
