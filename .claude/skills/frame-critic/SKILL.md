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
exit 0  PASS   the seat would ship this frame
exit 1  FAIL   it would not; the flip list is in CRITIC-VERDICT.json, verbatim
exit 2  VOID   it did not catch the plant. Findings are NOT READ. Stop and fix the judge.
exit 3  STOP   a loop guard fired. Read STALL-REPORT.md, end the turn, hand it to Rafe.
exit 4  refused — a precondition failed and it says which
```

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

Every one of them still came out **FAIL** with `SHIP: NONE`, and no gate opened. That is the whole
protective claim and it is narrower than it sounds:

> **The gate rests on SHIP, not on RANK.** Only a PASS opens it, and PASS requires the seat to
> put this frame in SHIP unflagged. What the mechanism guarantees is that a build reaching the
> phone is one a blind seat said it would ship. It does **not** guarantee the seat's ordering
> agrees with the human gate's — the evidence is that it does not.

So the ordering facts are **recorded and reported, never scored**: `outranked_build` when the
plant sits above the build, and `every_frame_flagged` when a seat flags everything including the
commercial bar and its flag therefore carries no discrimination. Folding either into the verdict
would say the wrong thing — VOID means *stop and fix the judge*, and there is nothing wrong with
the judge in either case.

A seat too harsh ever to PASS is a real failure too, and it belongs to the **five-round park**
guard, not to the plant.

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

## 5. The loop guards

The line stops rather than grinding. Every stop writes `STALL-REPORT.md` and is a **LOOP-PROCESS
§1.1.4 ruling trigger** with that report as its evidence.

| guard | fires when | why |
|---|---|---|
| **two strikes** | the same flip item survives two consecutive FAIL rounds | the fix is not landing; a third attempt is a guess |
| **five-round park** | five rounds on this lane with no PASS | the lane needs a ruling, not another round |
| **broken judge** | the plant is missed twice running | nothing past a broken judge is readable, and nothing ships past one |

**Counters are derived from the verdict files in `history/`, on disk, per lane** (the lane is the
git branch). A counter held in memory resets when a session restarts, and a guard a restart
clears is a suggestion with a number in it. Clearing one means deleting committed files, which
shows up in a diff.

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
   (§1.1.2). This is the loop.
5. **VOID** — stop. The judge is what failed, not the art. Nothing from that round is evidence.
   Check whether the plant is actually in the picture the seat saw.
6. **STOP** — end the turn and hand `STALL-REPORT.md` to Rafe.

`--no-capture` replays the round on the frame already on disk. `--build-frame <path>` puts a
chosen frame in the build's slot — that is the judge's own self-test, and its verdict is marked
`self_test` and can never open the install gate.

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
