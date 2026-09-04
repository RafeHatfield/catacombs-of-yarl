# Yarl Art Loop — PROCESS LAW v0

**Status: v0.8 — DRAFT.** Adapted from Gemfall's `docs/LOOP-PROCESS.md`, re-pointed at
`ART-BIBLE-v0.md`. Structure transfers wholesale; every number is re-derived.

*(The banner read v0.4 while the revision log below already carried v0.5 — corrected here rather
than left, since the banner is what a reader checks first.)*

This document governs *how work is done and certified*. `ART-BIBLE-v0.md` governs *what is
correct*. A session that has read only one of them is not equipped.

---

## 0. Step zero — before any session

1. **Tag and push.** No loop session starts on an unpushed lane. This project has lost work to
   a ceiling before.
2. **Worktree isolation.** One worktree per CC session. Never a shared working copy.
3. **The session states its Task, its Method, and its Bar** before it starts. A session missing
   any of the three is malformed and is stopped, not corrected mid-flight.

---

## 1. The two gates — LOCKED

This is the structural spine and it differs from a one-gate loop in a way that matters.

| Gate             | Who                       | What it decides          | Basis                      |
| ---------------- | ------------------------- | ------------------------ | -------------------------- |
| **Loop gate**    | Blind LLM critic          | Whether to iterate again | Prose verdict, adversarial |
| **Landing gate** | Rafe, in-scene, on device | Whether an asset ships   | The eye. Final.            |

**A critic PASS does not land an asset. It ends a round.** Only the landing gate lands.

**No script ever scores register conformance** (bible §13.4). A script emitting a number is an
instrument and enters the optimisation, where it will silently outcompete every clause that has
no number. A blind critic rendering a prose verdict is not an instrument in that sense and may
hold register questions — but its findings flow to the landing gate as prose, never as
arithmetic that trades against palette compliance.

**There will be no dread score and no staging detector.** A weak proxy is worse than an
acknowledged absence.

### 1.1 The gauntlet clause — LAW

**The two gates are correct and unchanged. This clause governs what happens between them:
long, autonomous, critic-held runs — not checkpointed relay.**

1. **Nothing reaches the human gate that the blind critic would kill.** Any session producing
   visual candidates runs a critic seat over them BEFORE anything is presented to Rafe.
   Mechanical disqualifiers (wrong projection, baked outline, baked shadow,
   object-where-surface-asked, off-canvas) are culled without ceremony; register reaction culls
   the rest to survivors. Rafe sees survivors and counts — never the morgue. The morgue goes to
   the ledger.
2. **The critic's FAIL is not a stop. It is a reprompt.** On FAIL with flip list, the builder
   applies the flip list and runs again, automatically, without returning to any human. This
   continues until the critic passes, the declared batch budget is spent, or a genuine
   ruling-trigger fires (below). "Tried once or twice, then asked" is a malformed session.
3. **Sessions are bounded by budget and width, never by rounds and never by check-ins**
   (§6 already says this about rounds; it now explicitly covers check-ins).
4. **Ruling triggers — the ONLY reasons to return to a human mid-run:** (a) a landing decision
   (Rafe's gate, §1); (b) an amendment to anything frozen (kill criteria, declared canvas,
   surface, bar); (c) an instrument shown unable to fail (§4); (d) a precondition fail;
   (e) budget exhausted below bar. Each return names its trigger. **A return that names no
   trigger is checkpoint creep and is a process defect.**
5. **Evidence-required is not approval-required.** Every round logs its evidence (diffs, counts,
   ledger, verbatim critic verdicts) exactly as before — in the report, read after the run, not
   as a toll-gate during it. Vetting by the design thread applies to landings and rulings, not
   to rounds.
6. **Before an asset class burns a second blind budget, measure how the bar builds it.** The wall
   campaign ran ~250 generations of first-principles derivation while the solved construction sat
   in the owned bars, measurable. **When any asset class stalls** — the critic converging on the
   same missing property round after round — **the next session is a measurement pass, not
   another blind batch** (bible §13.3: lessons cross, pixels don't). Builders get recipes with
   numbers; seats get the comparative frame. **Absolute verdicts in a vacuum are how ten
   independent judges ask for the same wrong thing.**

**Named failure this clause exists to prevent: CHECKPOINT CREEP** — the entropic drift of an
autonomous loop toward human relay, observed independently on both projects. Standing test:
**every human touchpoint in a session prompt must cite the law that requires it.** No citation,
no touchpoint.

### 1.2 The eyes-only rule — LAW

**Anything that gates an art round must be a picture judged by eyes.**

Not a threshold, not a census, not a manifest predicate, not a screen. A picture, delivered by
the production renderer, looked at by something with eyes — the blind critic at the loop gate,
Rafe at the landing gate.

**Instruments gate nothing.** They are builder's tools. Every `measure_*.py`, every control, every
census in this repo stays exactly where it is, keeps running, and keeps informing where the next
round aims. They report; they do not decide. An instrument result belongs in a round report and
never in a verdict.

**One paragraph of history, because this clause was bought twice.** Both collapses were of the
review layer, and both are the same shape: *the apparatus became the judge, and then the apparatus
broke.* At the wall device gate of 2026-08-27 **every instrument was green and the phone still
said no** — which is what it looks like when the thing measured and the thing judged have come
apart, and the numbers had been quietly holding the gate for some rounds before anyone checked.
Then the control itself went: wall rounds 9 and 10 both voided because the **generated** plant
differed from the family in **0.54% of pixels, in 21 cells** — since the cap pass the cell's base
is a cap window and the wall family's top tiles are never drawn, so ruining the wall tiles ruined
almost nothing. The plant was downstream of the engine, so an engine change disarmed it in
silence. Rounds 3 and 6 died the same way for a different reason. §13.4 already held that a script
must never score register conformance; these two say the same thing about *every* apparatus that
can drift, and the remedy is to gate on the one artefact that cannot: the picture.

#### 1.2.1 The mechanism — `.claude/skills/frame-critic`

A fresh blind `claude -p` seat is shown the build's capture, the asset bar, the last
Rafe-approved capture of the same surface, and **one picture-plant**, shuffled and unlabelled. It
ranks them for craft, says which it would ship, and flags obvious defects. That is the verdict:
**PASS**, **FAIL** with a verbatim flip list, or **VOID**.

**The plant is a picture, not a build.** A frame Rafe personally culled at the device gate, kept
as bytes in `morgue/` with his words and the commit that produced it, hash-checked before every
round. **An engine change can never neutralise a picture.** The plant must land worst-or-flagged
and must not be shipped; a passed plant voids the round under §4, unchanged.

The plant rule needs no vocabulary list, and that is the gain. The generated plant it replaces
needed one — a hand-maintained list of ruin words that carried `lichen`, which no plant ever
contained, and lacked `hole`, the plainest word for its most prominent feature, for three rounds.
A list widened by reading transcripts is a test derived from its own outcome. **A rank has no
vocabulary.**

**And its limit, measured four times on the day it was built rather than found later. A BLIND
SEAT'S RANKING DOES NOT REPRODUCE RAFE'S CULLS.** In the first live wall round the seat flagged
all three frames, shipped none, and **ranked the plant first** — a frame culled for grey walls,
placed above the current build. In the plant self-test, the build slot deliberately held
`keyline-floor.png`, a frame culled outright, and the seat **ranked it best of three and did not
flag it** (it listed that frame's magenta placeholder walls in its own flip list, so it had seen
them; it simply did not call it a flagged defect). Two further rounds on the same wall build,
different seats and different shuffles, **put the plant above it again, both times**.

Every round came out FAIL and no gate opened, which is the protective claim — and it is narrower
than it sounds: **the gate rests on SHIP, not on RANK.** What is guaranteed is that a build
reaching the phone is one a blind seat said it would ship. What is **not** guaranteed is that the
seat's ordering agrees with the human gate's; the evidence is that it does not. This is the
measured shape of §1.1.1's *"nothing reaches the human gate that the blind critic would kill"* —
it culls what a seat would refuse to ship, not everything Rafe would.

So the plant tests for **softness, not ordering**, and the ordering facts are recorded and
reported rather than scored: `outranked_build`, and `every_frame_flagged` for a seat that flags
everything including the commercial bar. Folding either into the verdict would say the wrong
thing — VOID means *stop and fix the judge*, and the judge was not what failed. A seat too harsh
ever to pass belongs to the five-round park, not to the plant. §8: the rule was declared before
the round, held frozen, cleared honestly, and impeached in the same report.

#### 1.2.2 The install gate

**No build reaches the device without a critic verdict for that exact build.**
`build_review_app.sh` and a PreToolUse hook both call one implementation, `critic_gate.py`, which
requires `CRITIC-VERDICT.json` to exist, to match this working tree's build id (commit + tracked
changes + untracked files), and to read PASS. Two callers, one implementation: a gate reimplemented
in a second place has two behaviours and the second is always the lenient one.

`YARL_SKIP_CRITIC=1` installs anyway and stamps **SKIPPED-REVIEW** into the review marker, which
the app draws on screen and reports in its `BUILD IDENTITY` line. It exists for producing a build
to *measure*. **Nothing walked on a SKIPPED-REVIEW build is a gate verdict**, and an override
nobody can see from the phone is the same as no gate.

#### 1.2.3 The loop guards — the line stops, it never grinds

§1.1 makes a FAIL a reprompt rather than a stop, and it is right. These are the bounds on that.

| guard | fires when | why |
| --- | --- | --- |
| **two strikes** | the same flip item survives two consecutive FAIL rounds | the fix is not landing; a third attempt is a guess |
| **five-round park** | five rounds on a lane with no PASS | the lane needs a ruling, not another round |
| **broken judge** | the picture-plant is missed twice running | nothing past a broken judge is readable, and nothing ships past one |

Each writes `STALL-REPORT.md` in plain language — what was tried, the critic's own words, the
capture paths — and **each is a §1.1.4 ruling trigger with that report as its evidence**, which is
the citation §1.1's standing test demands. **Never run a further round past a STOP.**

**The counters are derived from the verdict files on disk, per lane, not held in a session.** A
counter that a restart clears is a suggestion with a number in it; clearing these means deleting
committed files, which shows up in a diff.

---

## 2. The round

**build → capture → blind critique → fix → re-verify**

Never build alone. Never fix without re-verifying — **fix rounds regress**, and that is measured
fact from the predecessor project, not a caution.

### 2.1 Capture is in-scene, lit, and on device — LOCKED

No candidate is captured on a contact sheet or against a void. Capture is the production
renderer, lit per bible §6, rendering the real scene at true display size.

This is not only discipline. Bible §6.3 authors assets to *receive* light, so **a receive-light
asset captured unlit is being judged by the wrong instrument** and its rejection is
uninterpretable.

### 2.2 Every capture declares its own scope

A capture states the contexts it contains and flags any context the shipping game does not
contain. A creature shown standing somewhere it never stands is evidence about the instrument,
not about the creature.

### 2.3 Evidence carries its producer's hash

Every evidence file records the commit hash of the code that produced it. **A hash mismatch at
a ruling invalidates the evidence and forces a re-run.** No exceptions, no "it's probably fine."

---

## 3. Critic law

1. **The critic is a fresh `claude -p` process with cwd outside the repo.** Not a subagent.
   This is both stronger blindness — no shared context, no CLAUDE.md, no memory, no repo
   access — and cheaper on the agent pool.
2. **The critic never receives the bible.** It receives the fiction, the tone, and the
   questions. Handing a critic the rule list converts it into a compliance checker, which is
   what scripts are for. What is wanted from an LLM critic is a *reaction*.
3. **Questions ask what the rule exists to make answerable, never whether the rule was
   followed.** Bible §8.2 holds that polish means on-path and decay means off-path. Do not ask
   "is the wear legible." Ask **"which way would you walk, and why."** If it picks the trodden
   route unprompted, the rule reached the screen. If it picks at random, the rule is an
   intention that never arrived.
4. **The critic must demonstrate it can fail before its pass counts** (§4).
5. **A critic that finds no defect should suspect its own rigour** before crediting the work.
6. **The critic runs every round, not at the end.** A session that batches N candidates and
   presents them uncritiqued has not run the loop; it has run a generator with a delivery step.
   Critic seats are cheap (§3.1) — spend them.

---

## 4. Positive control — no instrument's pass counts until it has demonstrated it can fail

Adopted in full force from Gemfall's Ruling 47. Applies to every critic, census, measure,
harness, and screen.

**For scripts:** stub the metric to a constant, plant the defect it exists to catch, mutate the
thing it guards. Show it goes red. Record the verbatim failure.

**For the blind critic, tier one has no shipping corpus to mix in**, so "name them cold" cannot
run as designed. The substitute is a **plant**: one deliberately wrong candidate seeded into the
set — for tier one, a picturesquely *ruined* floor, cobwebbed and collapsed, among the *used-up*
ones (bible §8.1).

**If the critic does not catch the plant, the round is void and its findings are not read.**
Not discounted — void. A soft critic's findings are worse than no findings, because they will
be acted on.

**An instrument that cannot be made to fail is decorative and must be labelled so or deleted.**

### 4.1 A lever is proven on its axis, not on the diff — LAW

**Moving pixels above the noise floor proves a lever is connected. It does not prove the lever
does its job.**

The worked case, twice-earned: the integration audit measured the shading parameter **HONOURED**
— pixdiff 1.0 against a 0.354 noise floor — and Stage 1 of bible §6.4 then showed it had never
moved the *lighting* at all. The same gap reproduced on a second surface, through a parameter
rather than a prompt, in the tiles-pro audit.

**Consequence for every positive control:** the plant must carry the defect **on the axis the
lever claims**, and the lever must move *that*. A control that only asks "did anything change?"
certifies connectivity and reports it as efficacy.

### 4.2 A remediation must prove it removed something — LAW

**§4.1's twin, from the other side. §4.1 is a diff that proves less than it claims. This is NO
DIFF AT ALL, reported as success.**

Ruling 104 (`PIXELLAB-VERIFIED.md`): *a documented step with no enforcement is not a step, it is
a wish*, and its named failure mode is a step whose absence has no observable consequence at the
time — only later, and somewhere else. **A fix that runs, changes nothing, and says so quietly
is the same failure wearing the opposite clothes: the step did run, and it was still a wish.**

**LOGGED INSTANCE — `dering_floors.py` on A-VAB, 2026-08-26 to 2026-08-27.**

The composition spike's de-ring step ran on all four §6.4 survivors and removed **zero pixels
from A-VAB**, because it thresholds luminance at 0.30× the tile median and A-VAB's two rings sit
at 0.48×. It printed `0 ring pixels removed of 1024` and exited 0. Nothing went red. The
"de-ringed" A-VAB it wrote is **byte-identical to the raw survivor**, and so is its lit in-scene
capture — `sha256 9e9890c0fa4db115` either way. Round 8's captures were taken through it and
carried a fully ringed floor on every tile while being labelled de-ringed; A-VAB is the tile the
survivor manifest marks `strongest` and the one the spike's own solo-floor arm used as its
single floor. The defect surfaced a round later, somewhere else, exactly as Ruling 104 predicts.

**The check that closes it, and it is one line of state, not a new instrument:** a remediation
records **what its own target measured before and after**, and reds when a tile it was pointed
at is unchanged *and* still fails. `remediate.py` carries `verdict_before`, `verdict_after` and
`pixels_changed` per tile in its manifest for this reason.

**LOGGED INSTANCE 2 — `capture_children.py`'s id block, 2026-08-27. The week's second, and it
generalises the clause.**

The parent-rate run's capture module staged candidate floor tiles from `ID_BASE = 9200`. **Tile
9200 is `wall_autotile: 0`** in the composition spike's theme, whose wall ids are sparse and
reach 9343. Every capture therefore quietly made the candidate floor tile double as a wall tile
— **in a rig whose entire stated claim is that the walls are held constant and the floor is the
only variable.** The captures rendered, the manifests recorded success, and nothing went red.

**It did no damage, and that was measured rather than argued.** Three runs staged three
*different* tiles into `fr_9200` and the plant and parent captures came out byte-identical every
time, and identical to survivor captures taken before the module existed — autotile mask 0 never
fires in a one-wide corridor. The id block was corrected to 9400 and **all sixteen captures
re-taken under it reproduce byte-for-byte**, which is what allowed the seat rounds to stand
rather than be re-run.

**What the second instance adds.** §4.2 was written about a *remediation* that removed nothing.
This one removed nothing either — but it was not a remediation, it was a **rig invariant**. The
clause generalises accordingly:

> **Any step that asserts something is HELD CONSTANT must be able to go red when it is not.**
> A no-op fix and a violated invariant are the same failure: a claim in a docstring with no
> enforcement behind it, discovered later and somewhere else.

Both instances this week were caught by the same move, and it is the cheap one: **compare bytes
you already have.** The MOCK was caught because its output was byte-identical to its input when
it should have differed; the rig was cleared because its output was byte-identical across three
runs when it should not have mattered. Neither needed a new instrument. Where a rig holds
something constant, capture the constant part twice under deliberately different conditions and
diff it — that is the closing check, and it is one comparison, not a system.

**Ask of any fix: what goes red if it silently does nothing?** "The output looks fine" cannot
answer it — in the first instance the output *was* the input, and it looked exactly as fine as
the thing it was supposed to have repaired. **And ask of any invariant: what goes red if it
silently stops holding?**

---

### 4.3 The gate verdict outranks the instrument bar — LAW (Rafe, 2026-09-03)

**A lever proven on a number is not licensed back when its picture was culled.**

The occasion: the floor's `no_erosion` positive control demands that nulling form-as-erosion cost
the floor 20% of its face-value spread. It reads 1.14x against that 1.20x bar — and it read 1.162x
before the change that exposed it, so the bar was already unmet. Exactly one lever clears it:
restoring `DEFORM_FLATTEN` to the strength a frame critic culled as *"large soft value-blobs ...
they read as airbrush, not as light or as material."*

That is measurable-versus-effective in its sharpest form. The number and the eye disagree, and
**the eye wins** — §1.2 and bible §13.2 already say so for acceptance, and it holds for controls
too. The instrument does not get to re-admit a defect the gate removed.

**What happens instead**, and this is the whole of the procedure:

1. **The bar is not moved.** Ever, and least of all by the session whose change exposed it.
   Moving a threshold to clear one's own work is the failure §4 exists to catch.
2. **The lever is not restored.** The culled picture stands.
3. **The check is annotated `SUPERSEDED-BY-GATE`, with the verdict that superseded it and the
   date**, and demoted to a **builder's tool**: it still runs, it still prints its number every
   round, and it **no longer votes**. A superseded check is not a deleted one — if a later round
   changes what it measures, the reading moves and is visible.
4. **Only the superseded axis is demoted.** Where a control guards two things, the half that
   still discriminates keeps its vote. Here the *directional* half is untouched and total —
   grain 1.17 live against -0.01 nulled — and `isotropic_erosion` continues to guard it.
5. **The supersession is recorded where the check lives**, not only in a round doc, so the next
   reader of a non-firing control finds the ruling beside it rather than a mystery.

**The standing hazard this closes:** a bar written for one version of a surface silently becomes
wrong as the surface gains layers. Here the crown gained the lane dish, the margin grit and the
tool marks — three erosion-independent value layers, each with its own control — and every one of
them dilutes a ratio written before they existed. That is a bar going stale, not a floor going
wrong, and the honest response is to say so rather than to chase the number.

---

## 5. The bar

**PASS means genuinely wowed.**

The following are **failing** verdicts: *fine, acceptable, good enough for now, improved,
better than last round, solid, promising, close, nearly there.* Hedging is failing. A verdict
that requires a qualifier is a FAIL.

On FAIL the critic emits a **mandatory executable flip list**: the specific, concrete changes
that would flip the verdict. "Needs more atmosphere" is not a flip list item. "The floor's
value sits too close to the wall base; separate them" is.

**Visual bar** (bible §13.3): blind side-by-side against shipped commercial games, asking
*which of these looks like the shipped game.* The answer must be Yarl or a tie.

- **Shattered Pixel Dungeon** — the bar for structure. Gameplay bar; **the look must exceed it.**
- **Rogue Wizards** — the bar for finish and cohesion. Its projection is explicitly not a target.

This is a **quality** comparison, not a style target. *"Doesn't match SPD"* is not a defect.
*"Looks like the free one next to the paid one"* is.

---

## 6. Certification

**No convergence calls, ever.** "Each round finds finer issues" is a reason to run the next
round, not a reason to stop.

**There is no round cap.** What is capped is width and debt:

| Limit              | Value                                        | Note                              |
| ------------------ | -------------------------------------------- | --------------------------------- |
| Wave width         | 3–4 parallel tracks                          |                                   |
| Certification debt | No new track while >2 sit built-but-unjudged | Self-verification retires nothing |
| Agent budget       | ~7 child agents per parent, working average  | **Count agents, not tracks**      |

**Self-verification retires no debt.** A track is judged by something that did not build it.

---

## 7. Park states

A track that stops writes down which state it stopped in. There are two, and they are not the
same:

- **Finalised, not iterated** — this is done. It does not reopen because a later tier raised
  the standard.
- **Prepared, not generated** — staged, deliberately not spent on.

**Refusals are declared before the run, not after.** Each seat writes *what this seat refuses,
written before it could be tempted*, and the promotion rule is declared before ranking.

**A failed arm ships to the device as evidence, not as a candidate.** Evidence on the phone
beats evidence in a paragraph.

---

## 8. Nothing is cut to fit

A clause, a criterion, or a prompt fragment is removable **only if a probe declares its bar
first and the measurement clears it.** The bar is never re-tuned after the answer is seen.

The worked precedent: bible §6.4's receive-light probe declares its kill criterion before any
arm runs.

**A bar's clauses must name the destination, not just the road — LAW.** The wall micro-probe's
bar was drawn from framing clauses only (*"surface, not object"*) and was cleared **20/20 by
undifferentiated wallpaper**. Framing was the easy half; the clause left out — *"reads as a
wall"* — was the destination. **A bar that can be cleared without reaching the thing the probe
exists to reach is a mis-drawn bar.**

The remedy is not to re-tune it, because that is what the rule above forbids. When a mis-drawn
bar is discovered mid-probe it is **held as frozen, cleared honestly, and impeached in the same
report** — the reader sees both the pass and why the pass is worthless. The micro-probe is the
worked example.

---

## 9. Anything awaiting a ruling is printed in full

A repo path is not a substitute for content. A count is not a substitute for a list. A message
asking for a decision contains the thing being decided on.

*(Violated once already in this project's own handover: a bible was passed by path and turned
out to be a stale revision. The rule is cheap and the failure is not.)*

---

## 10. Sequencing — the demo track

Strict order. Each step gates the next.

| #     | Step                                                         | Gate to proceed                                              |
| ----- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **0** | **Harness.** `ArtAcceptanceSceneBuilder` re-aimed + lighting + device capture. **Track work with its own critic loop** — an orchestrator that writes its own harness and then describes it has no independent check. | Determinism verified; capture reproducible from hash         |
| **1** | **Receive-light probe** (bible §6.4). Three arms, positive control, kill criterion pre-declared. | §6.3 ratified or RETIRED, evidence recorded                  |
| **2** | **Palette derivation.** Shared spine + Boundary reserved slots. | Palette locked in bible; `palette_check` built and shown to fail |
| **3** | **Two-region swatch check.** Mock a deep-region allocation against the spine, both on device. Detects §5.2's flattening risk without building a second region. | Two places, or spine widened                                 |
| **4** | **Tier one — floors and walls.** The first approved assets ARE the scene. | Landing gate                                                 |
| **5** | **Tier two — 2–3 signature props.** Judged in the scene tier one built. | Landing gate                                                 |
| **6** | **Tier three — one creature.** Tests bible §7.4's second seam: creatures inherit binding through gear, not anatomy. | Landing gate                                                 |
| **7** | **Tier four — Sasha.** Last, per bible §10.5. Rigged from frame one; attachment tolerance instrumented. | Landing gate                                                 |

---

## 11. Re-aim inventory — audited against the repo, 2026-08-24

**Survives, corpus-agnostic:**
`capture_scene.py` · `review_capture.py` · `crop_captures.py` · `scene_capture_config.yaml` ·
`review_scenes/` · `verify_capture_determinism.py` · `build_generated_manifest.py` ·
`snap_to_palette.py` · `verify_snap.py`

`verify_snap.py` is already the **compliance-is-not-rescue** audit: the snap makes the palette
check pass *by construction*, so passing it is not evidence of good art. **Any generation
needing heavy snapping is regenerated, never shipped**, and mean snap distance is recorded per
asset as an audit trail of how far the art was reinterpreted.

**Retired with the Oryx track** — these are the Oryx-*derived data and strategies*, and under
Ruling 56 their verdicts over a Yarl corpus would be findings about the instrument:
`fineness_thresholds.json` · `fineness_canon_baseline.csv` · `speckle_canon_baseline.*` ·
`f4_recalibration.py` · `extract_master_palette.py` · `derive_armor_stand.py` ·
`derive_bottle_shelf.py` · `derive_tool_rack.py` · `derive_workbench_barrel.py` ·
`outline_repair.py` (bible §12.1)

> **CORRECTION (v0.2, 2026-08-24).** v0.1 of this document retired the entire fineness family,
> including its metric code. That was wrong and would have deleted working infrastructure.
> `docs/archive/oryx-track/README.md` records the roadmap ruling that closed the track, and it
> draws the line explicitly: **the Part A checks and the F1–F3 structural-fineness family are
> retained; only the Oryx-derived thresholds and baselines are struck.** The metric code is
> corpus-agnostic — what dies is the calibration, not the measurement.
>
> **Retained, pending re-derivation against the Yarl corpus:** `fineness_metrics.py` ·
> `fineness_strips.py` · `fineness_sweep.py`. Their thresholds are **PLACEHOLDER** until a Yarl
> corpus exists to derive them from, and **a retained metric with a struck threshold is not a
> gate.** F4 was already demoted to advisory on the old track and does not return without a
> derivation of its own.
>
> *Recorded rather than silently edited. The error was mine, caught by the repo.*

**Also retained, and not archived** — noted here because a session reading only the retirement
list would assume otherwise: `ReviewSceneBuilder`, the in-scene review protocol, the
acceptance/capture harness, the generated-assets manifest, and `tools/pixellab/` (docs carry an
in-place notice; the tool is live). `docs/2d-vs-iso.md` also stands — its top-down-over-isometric
conclusion is independent of the Oryx question and corroborates bible §3.

**Owed a clause-by-clause audit before any verdict:**
`art_lint.py` — A1–A7. Some checks are plausibly corpus-independent; some encode Oryx
construction. **This is a CC task with evidence, not a judgement call from memory.**

---

## 12. PixelLab facts — banked, do not rediscover

- `size` and `style_images` are **mutually exclusive**. The largest reference dictates output
  dimensions, so **author references at target canvas.**
- **Single-reference conditioning fails.** Never fewer than two. Maximum eight.
- Generation prompts live as **auditable files with clause provenance and a self-check that
  asserts load-bearing clauses survived** — never as a string typed into a chat.

**The measured surface facts live in bible §13.7 and are not repeated here** — which surface
conditions, which supplies parts, which camera parameters are spent, and why the ledger stores
images rather than parameters. One home, cited from both documents.

---

*v0.8 — 2026-09-03. **New §4.3: the gate verdict outranks the instrument bar.** Ruled at the
floor's close. A positive control that can only be cleared by restoring a lever the eye culled is
superseded, not satisfied: the bar is not moved, the lever is not restored, and the check is
annotated `SUPERSEDED-BY-GATE` and demoted to a builder's tool — it prints its number every round
and no longer votes. Only the superseded axis is demoted; where a control guards two things, the
half that still discriminates keeps its vote. First instance: the floor's `no_erosion` spread bar,
already unmet at 1.162x before the change that exposed it, clearable only by re-admitting the
value-blob defect a frame critic culled. The hazard it closes is a bar going stale as a surface
gains layers — that is the bar going wrong, not the surface.*

*v0.7 — 2026-09-03. **New §1.2: the eyes-only rule.** Anything that gates an art round must be a
picture judged by eyes; instruments are builder's tools and gate nothing. Bought twice, both
times by the review layer rather than the art: at the 2026-08-27 wall gate **every instrument was
green and the phone still said no**, and then the control itself went — wall rounds 9 and 10
voided because the generated plant differed from the family in **0.54% of pixels, in 21 cells**,
the cap pass having quietly stopped the wall family's top tiles from being drawn at all. §1.2.1
puts the plant beyond that reach by making it a **picture** — a frame Rafe personally culled, kept
as hash-checked bytes in a morgue — which no engine change can neutralise, and which needs no
vocabulary list (the generated plant's list carried `lichen`, which no plant ever had, and lacked
`hole` for three rounds). §1.2.2 makes the install script the choke point, with a visible
SKIPPED-REVIEW override. §1.2.3 adds the three loop guards — two strikes, five-round park, broken
judge — each writing `STALL-REPORT.md` as a §1.1.4 ruling trigger, with counters derived from the
verdict files on disk so a session restart cannot clear them. §1.2.1's limit is recorded from the
mechanism's own rounds, held frozen per §8 rather than re-tuned: the plant tests for softness, not
ordering, and a plant that outranks the build is reported rather than scored. Those rounds also
found that **the asset-bar crop was wrong twice over**, each half caught by a seat culling the
bar: `(336, 240, 720, 528)` against a 720×504 source, so PIL padded the comparative frame with 24
black rows and said nothing; and then, moved inside the file, still outside the picture, reaching
the example sheet's own white paper margin. `crop_to()` now refuses an out-of-bounds box and the
second half is a standing instruction to look at the crop — a weak detector for *inside the image
but outside the picture* would be worse than reading the verdict.
`tools/tier1_floors/run_seats.py` still carries the original box, which reaches backwards into
that session's comparative seats.
`gate_precheck.py`'s instrument rows are demoted to advisory in the same commit; no instrument was
deleted. Mechanism: `.claude/skills/frame-critic`.*

*v0.6 — 2026-08-27. **§4.2 gains its second logged instance and generalises.**
`capture_children.py` staged candidate floors from id 9200, which is `wall_autotile: 0` in the
spike's theme — silently making the floor tile double as a wall in a rig whose claim is that the
walls are held constant. Nothing went red. Measured harmless (three runs, three different tiles
at that id, byte-identical controls every time; mask 0 never fires in a one-wide corridor),
corrected to 9400, and all sixteen captures re-taken reproduce byte-for-byte — which is why the
seat rounds stood instead of being re-run. The clause now covers **any step asserting an
invariant**, not only a remediation: a no-op fix and a violated "held constant" are the same
failure. Both of this week's instances were caught by the same cheap move — compare bytes you
already have — so the closing check is one comparison, not a system. The status banner also read
v0.4 against a v0.5 log; corrected.*

*v0.5 — 2026-08-27. **New §4.2: a remediation must prove it removed something** — §4.1's twin
from the other side, and Ruling 104's failure mode wearing the opposite clothes. §4.1 is a diff
that proves less than it claims; §4.2 is no diff at all, reported as success. Logged instance:
`dering_floors.py` removed zero pixels from A-VAB, printed `0 ring pixels removed of 1024`,
exited 0, and nothing went red — its "de-ringed" output is byte-identical to the raw survivor
and so is the lit capture taken through it (sha256 `9e9890c0fa4db115` either way), which is how
a round's captures carried a fully ringed floor while being labelled de-ringed. The check is one
line of state, not a new instrument: record the target's own verdict before and after, and red
when a tile you were pointed at is unchanged and still failing.*

*v0.4 — 2026-08-27. Three clauses, each twice-earned or campaign-earned. **New §4.1:**
measurable is not effective — a lever is proven on the axis it claims, not on the diff; the
shading parameter measured HONOURED and never moved the lighting, on two surfaces. **§8 gains
the destination rule:** a bar drawn from framing clauses alone was cleared 20/20 by
undifferentiated wallpaper, and a mis-drawn bar is held frozen, cleared honestly, and impeached
in the same report. **§1.1 gains item 6, the sighted-round rule:** when an asset class stalls,
the next session measures how the bar builds it instead of burning a second blind budget — ~250
generations of derivation ran against a construction the owned bars already carried. §12 now
points at bible §13.7 for the measured platform facts rather than mirroring them. Sources: PRs
#144–#146.*

*v0.3 — 2026-08-25. **The gauntlet clause** (new §1.1): autonomous critic-held runs restored as
the default execution mode; ruling triggers enumerated; checkpoint creep named with its standing
test; evidence-required distinguished from approval-required. **§3 gains item 6**: the critic
runs every round, not at the end. Prompted by a measured audit — the blind critic had not run
once since the process was adopted, and unculled candidate sheets reached the human gate. The
founding Task/Method/Bar block is the reference for this restoration.*

*v0.1 — 2026-08-24. Adapted from Gemfall LOOP-PROCESS. Two-gate structure and §3.2 (critic
never receives the bible) are Yarl-specific additions. §10 sequencing is new: tier zero is the
harness, not art.*
