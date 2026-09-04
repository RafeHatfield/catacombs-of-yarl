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

**A blind seat's ranking does not reproduce Rafe's culls — now five rounds, five seats, five
shuffles, and the fifth voided a round.** Three live wall rounds each **ranked the plant above the
build**; the self-test **ranked a culled frame best of three and did not flag it**; and the first
round under the progress guards put the plant **first in the deck and flagged nothing in it** —
`void-round-2026-09-03/`. Every one still came out with `SHIP: NONE`, which is the protective
claim and is narrower than it sounds: **PASS needs SHIP; rank is only ever a filter on top.**

That fifth round points at the **plant**, not the seat. `grey-walls.png` was culled for *chroma*
and the seat is asked to rank *craft* — a plant whose defect is orthogonal to the question can be
ranked first by a perfectly competent seat. `morgue/README.md` carried this as a stated risk (*the
wall lane holds one entry*); the round turns it into a measurement. **The wall lane needs a plant
culled on construction, and morgue entries are Rafe's culls.**

**A VOID round's findings were being printed on the most-read surface there is.**
`critic_gate.py` printed the flip list for every non-PASS verdict, void included — exactly the
reading §4 forbids, found the first time a round actually voided. A void verdict now carries no
readable `flip_list` at all (the findings are kept under `flip_list_withheld`, because deleting
evidence is a different sin), so the gate, the stall report and the guards are correct **by
construction** rather than by each reader's manners.

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

⚠ **Property 3 used to skip itself** whenever a real `CRITIC-VERDICT.json` was on disk — which,
once the mechanism had shipped, was always. The most important of the three stopped being checked
at the exact moment it started mattering, and the transcript said `3 skipped` quietly enough that
it read as fine. It moves the real verdict aside and puts it back now, the way `prove_gate.py`
already did.

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

**These measure progress, not rounds.** The signal is where the build ranked in that round's blind
shuffled deck, normalised across deck sizes. Driven against fixture histories (`guard-fixtures/`,
built by `make_guard_fixtures.py`) through `--check-guards`, which runs the real `guards()` and
writes a real stall report.

| fixture | what it presents | exit |
| --- | --- | --- |
| `broken-judge/` | two consecutive VOIDs | **3 — STOP broken-judge** |
| `no-change/` | two consecutive FAILs on literally the same picture, rank improving between them | **3 — STOP no-change** |
| `thrash/` | the same request twice, differently worded, rank going backwards | **3 — STOP thrash** |
| `stall/` | a new best at round 1, then three readable rounds that never beat it | **3 — STOP stall** |
| `ceiling/` | fifteen rounds that improve every single round | **3 — STOP ceiling** |
| `no-stop/` | a lane doing well enough that nothing may fire | **0 — no stop** |

**Each fixture fires its own guard and no other**, and the check order proves it: the guards are
evaluated broken-judge → no-change → thrash → stall → ceiling, so a fixture reporting `stall` has
demonstrated that the three before it stayed quiet. A history that fired two guards would prove
nothing about either.

**The negative control is the half usually skipped.** A guard that always fires is exactly as
useless as one that never does, and much harder to notice: every round STOPs, everyone stops
reading the reason, and the mechanism is gone. `no-stop/` puts four temptations in front of the
guards — a repeated flip item, a run of FAILs, a lane several rounds deep, and two consecutive
FAILs sharing a flip item — and requires silence. **The last of those is the case the old
two-strikes guard got wrong**: rounds 3 and 4 are consecutive FAILs sharing a flip item, but round
4 sets a new best rank, so `thrash` must hold its fire. The advisory speaks; the line continues.

The `thrash` fixture's wording is the point of it. Its two flip items overlap at **Jaccard 0.692**
on content words, against a threshold of **0.60 declared in `frame_critic.py` before any round
ran**. Exact string equality would have matched neither, and a guard that silently never fires is
the failure a guard cannot have.

The `ceiling` fixture is deliberately awkward: fifteen rounds that improve *every* round, because
that is the only lane for which the ceiling is the correct guard. It uses an unrealistically wide
deck to buy fifteen strictly increasing ranks, and says so in its own docstring rather than
leaving a reader to notice.

### What this proof found in its own subject — the hash could not see the thing it was for

The no-change guard first measured a **256-bit perceptual (difference) hash** of the delivered
frame, with a declared floor of 2 bits. Calibrating it against real data before it shipped:

| pair | dHash distance | signature Δ (mean / worst cell) |
| --- | ---: | ---: |
| a frame against itself | 0 bits | 0.000 / 0 |
| `washed-slab-lane` → `tile-quantized-wear` | **2 bits — the entire floor** | 1.942 / 36 |
| `tile-quantized-wear` → `keyline-floor` | 8 bits | 1.200 / 38 |

Those first two are **consecutive real builds that Rafe culled for two different defects.** The
guard would have stopped that lane on a round where the art genuinely moved. Raising the hash
resolution did not help — the gap held at 0.4–0.9% of bits from 256 up to 4096 — because a
gradient-sign hash asks *is this the same scene* and the honest answer was yes. Wrong question.

The distance is a magnitude now: mean and worst-cell luminance difference over a 32×32 grid of the
delivered frame, with **both** required to be small. Mean alone would miss a change confined to a
corner — one tile of ninety moving twenty levels contributes about 0.2 to the mean — and a corner
is exactly where a seat looks. The floors are 0.25 and 4 levels, five and nine times below the
smallest real change measured.

**That calibration is now a fixture, not a comment.** The `thrash` lane's two pictures *are* that
pair, so if the measure ever stops telling them apart, `no-change` fires first and the fixture goes
red.

## 5. What was NOT verified, and will not be claimed

- **Nothing was walked on the device.** `SKIPPED-REVIEW` is shown reaching the *marker*, and the
  code that draws it on screen compiles and boots headless — the phone has not been asked. That is
  a device walk, and device walks are Rafe's.
- **No art was judged for landing.** A critic PASS ends a round; only the landing gate lands
  (§1).
- **The wall lane's morgue holds one entry**, so wall rounds draw the same plant every round. Safe
  against a fresh seat, not against a builder who learns to compose around one picture. Stated in
  `morgue/README.md` rather than discovered later.
