# The mechanism gets the same discipline as everything it gates

`ART-LOOP-PROCESS-v0.md` §4 and `ART-BIBLE-v0.md` §13.5: **no instrument's pass counts until it
has demonstrated it can fail.** That applies to the thing doing the gating exactly as it applies
to the things being gated, and this directory is the demonstration.

Every proof drives **the real code** — the same `critic_gate.py`, `guards()`, `write_stall()`,
`build_review_app.sh` and PreToolUse hook the live path runs. None of them reimplements what it
tests. `verify_on_device.sh --check-log` is the precedent and states the reason: *a test that
reimplements the thing it tests proves the reimplementation.*

---

## 0. What the rounds found — read this first

Three complete rounds ran while this was built, and between them they turned up two things the
design had to absorb:

**The bar crop was wrong, twice, and both halves were found by seats culling the bar.**
`round-that-found-the-padded-bar/` — the box inherited from `tools/tier1_floors/run_seats.py` is
`(336, 240, 720, 528)` against a **720×504** source, so PIL padded the comparative frame with 24
black rows and said nothing. Then `round-that-found-the-white-margin/` — moving it inside the
*file* left it outside the *picture*, since the example sheet's artwork occupies x 24–695,
y 24–479 and the rest is white paper. `crop_to()` now refuses an out-of-bounds box; the second
half is a standing instruction to look at the crop, because a weak detector for *inside the image
but outside the picture* would be worse than reading the verdict. **The first half reaches
backwards into every comparative seat the floor session has run.**

**A blind seat's ranking does not reproduce Rafe's culls — four rounds, four seats, four
shuffles.** Three live wall rounds each **ranked the plant above the build**; the self-test
**ranked a culled frame best of three and did not flag it.** Every one still came out FAIL with
`SHIP: NONE`, which is the protective claim and is narrower than it sounds: **the gate rests on
SHIP, not on RANK.**

## 1. A real round on a real build — `rounds-during-construction/`

The skill was run end to end on main's wall build (`tools/tier1_walls/capture.sh material`,
`tier1_wall_standing`, the ratified rig). **FAIL, plant caught**, seven flip items, all specific.

It also found something in the mechanism's own control, and that is written up in that directory's
README and in the law: **a blind seat's ranking does not reproduce Rafe's culls.** Measured twice
in one day.

## 2. The gate — `proofs/GATE-PROOF.txt`

Twelve cases, all as declared.

| case | | |
| --- | --- | --- |
| A | no verdict at all | REFUSE |
| B | a verdict for a different build **at the same commit** | REFUSE |
| C | a FAIL verdict for this build | REFUSE |
| D | the same, with `YARL_SKIP_CRITIC=1` | ALLOW, exit 10 |
| D2 | the marker written under D | carries `"reviewStatus": "SKIPPED-REVIEW"` |
| E | a PASS verdict for this build | ALLOW |
| E2 | the marker written under E | carries `"reviewStatus": null` |
| E3 | a self-test PASS | REFUSE — it judges the judge, not a build |
| F1 | the hook, on `xcrun devicectl device install` | DENY, with the gate's own words |
| F2 | the hook, on `dotnet test` | silent |
| F3 | the hook, on `build_review_app.sh --no-install` | silent |
| F4 | the hook, on a command carrying the visible override | silent |

**Case B is the one that matters.** The commit is identical and the build is not — which is the
ordinary state of an art session, where a family is recomposed and `git rev-parse HEAD` says
nothing has happened. A gate comparing commits would have installed it.

**F2–F4 are the other half of the test.** A guard that fires on the wrong thing gets disabled, so
the proof checks that the hook is *silent* on work that installs nothing — silence checked, not
assumed.

### What this proof found in its own subject

The first run went red on C, E, E2 and E3, all with one signature: the verdict's `build_id` fixed,
the working tree's different on every call. **`CRITIC-VERDICT.json` is untracked when it is first
written, so writing the verdict changed the build id the verdict had just recorded.** The gate
could never have opened. `build_id.py` now excludes the review layer's own artefacts by name — a
short, closed list containing nothing that reaches the app — and `frame_critic.py` takes the id
*after* the capture, since the capture writes into the tree too.

Then it went red a second time, on the same three cases, because the proof's own output was being
redirected into `evidence/proofs/`. Same lesson from the other side, and the correct behaviour of
the mechanism rather than a bug in it: **any untracked file written into the tree while a check is
live moves the build id.** A build id that ignored new files could not see a new tile.

## 2b. The build id — `proofs/BUILD-ID-PROOF.txt`

The gate's claim is *this verdict is about THIS build*, and it is only as good as the identifier
behind it. Three properties, all of which must hold together:

| | |
| --- | --- |
| **1** | a new file in the tree **moves** the id — and removing it puts the id back. An identifier that never changes is not one |
| **2** | **staging the same bytes does not move it** (checked against a scratch `GIT_INDEX_FILE`, so the real staging area is never touched) |
| **3** | writing `CRITIC-VERDICT.json` does not move it |

Property 2 is why the id is content-addressed — a sha256 over `(path, git blob sha)` for the
effective working tree — rather than a hash of `git diff HEAD`. Under the diff scheme, **committing
the exact pixels that had just passed produced a different id**, and the gate refused a build it
had approved seconds earlier. The verdict would have had to be re-run to land the PR containing it.

It costs 0.34s over 28,171 files: `git ls-files -s` supplies the blob shas without reading
anything, and only the handful of paths that actually differ go through one batched
`git hash-object`.

The check also caught its own bug, which is worth recording because it is a worktree-specific
trap: it copied `.git/index` by hardcoded path, and **in a git worktree `.git` is a file**, not a
directory. Nothing was copied, `git add -A` ran against an empty scratch index, and the id came
back as the sha256 of the empty string — a confident wrong answer that made a holding property
look violated. It asks `git rev-parse --git-path index` now.

## 3. The plant self-test — `rounds-during-construction/`

A deck whose **build slot held a morgue frame** — `keyline-floor.png`, culled by Rafe as *"outlined
chips"*. Declared expectation: the seat flags it.

**It did not.** It ranked that frame best of three and left it out of `FLAGGED`, while listing the
same frame's magenta placeholder walls in its own flip list. The round came out **FAIL**,
`SHIP: NONE`, so no gate would have opened, and that deck's plant was caught.

Reported as it happened rather than re-run until it agreed. It is the sharpest statement of what
the mechanism promises: **the gate rests on SHIP, not on RANK.**

## 4. The loop guards — `proofs/GUARD-*.txt`, `proofs/STALL-*.md`

Driven against fixture histories (`guard-fixtures/`, built by `make_guard_fixtures.py`) through
`--check-guards`, which runs the real `guards()` and writes a real stall report.

| fixture | guard | exit |
| --- | --- | --- |
| `two-strikes/` | two consecutive FAILs whose flip lists carry **the same request, differently worded** | **3 — STOP** |
| `five-round-park/` | five FAILs, unrelated flips, no PASS | **3 — STOP** |
| `broken-judge/` | two consecutive VOIDs | **3 — STOP** |
| `no-stop/` | FAIL, PASS, FAIL(same flip as round 1), FAIL(unrelated) | **0 — no stop** |

**The negative control is the half usually skipped.** A guard that always fires is exactly as
useless as one that never does, and much harder to notice: every round STOPs, everyone stops
reading the reason, and the mechanism is gone. `no-stop/` puts three separate temptations in front
of the guards — a repeated flip item, a run of FAILs, and a lane four rounds deep — and requires
silence. The intervening PASS is what makes the repeated item legal: two FAILs with a PASS between
them are not consecutive.

The two-strikes fixture's wording is the point of it. Its two flip items overlap at **Jaccard
0.692** on content words, against a threshold of **0.60 declared in `frame_critic.py` before any
round ran**. Exact string equality would have matched neither, and a guard that silently never
fires is the failure a guard cannot have.

## 5. What was NOT verified, and will not be claimed

- **Nothing was walked on the device.** `SKIPPED-REVIEW` is shown reaching the *marker*, and the
  code that draws it on screen compiles and boots headless — the phone has not been asked. That is
  a device walk, and device walks are Rafe's.
- **No art was judged for landing.** A critic PASS ends a round; only the landing gate lands
  (§1).
- **The wall lane's morgue holds one entry**, so wall rounds draw the same plant every round. Safe
  against a fresh seat, not against a builder who learns to compose around one picture. Stated in
  `morgue/README.md` rather than discovered later.
