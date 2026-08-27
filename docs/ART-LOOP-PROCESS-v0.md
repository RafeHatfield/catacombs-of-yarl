# Yarl Art Loop — PROCESS LAW v0

**Status: v0.4 — DRAFT.** Adapted from Gemfall's `docs/LOOP-PROCESS.md`, re-pointed at
`ART-BIBLE-v0.md`. Structure transfers wholesale; every number is re-derived.

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
