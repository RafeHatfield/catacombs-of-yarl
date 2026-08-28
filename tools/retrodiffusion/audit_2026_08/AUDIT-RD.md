# RETRO DIFFUSION — connection and adoption audit

**Ruling trigger: §1.1.4(d), PRECONDITION FAIL.** The credential is not present in the
environment, so no call — free or paid — has been made to Retro Diffusion. Nothing here claims a
measurement that was not taken. Nothing landed, nothing was promoted, no corpus file changed, no
constant in any existing instrument was altered, and **tier one is untouched and stays frozen on
BitForge to completion regardless of anything in this document.**

> **THE STOP, STATED FIRST.** `RD_API_KEY` is unset in this session's environment, and no login
> profile on this machine defines it (`~/.bashrc`, `~/.zshrc`, `~/.zprofile`, `~/.profile`,
> `~/.bash_profile` — grepped by name; none matched). `PIXELLAB_API_TOKEN` **is** set, so the
> environment carries credentials in general; this one specifically is absent.
>
> **What Rafe needs to do:** `export RD_API_KEY="rdpk-..."` in this shell, then the run order in
> [`README.md`](README.md). Everything downstream of the key is built, compiled, and
> control-certified; the audit executes without further design work.

**Everything that does not depend on the credential was done rather than deferred**, and it is
more than the brief expected — the entire instrument layer is built and *certified against
planted defects*, the bar is declared, and four findings are already banked, one of which
materially changes how the adoption bar's third limb must be read.

---

## 0. THE BAR, DECLARED BEFORE ANY GENERATION

Copied from the session brief, unaltered, and recorded here so that it is on disk *before* a
single image exists — bible §13.6, a candidate never contributes to its own acceptance bar.

> **RD becomes a candidate materials supplier only if it wins or ties the blind A/B AND at
> least one of:**
> 1. ring rate materially below the 25–45% baseline;
> 2. seamless census pass where BitForge fails it;
> 3. cost-per-accepted-tile materially lower.
>
> **Otherwise: finding recorded, no second surface, complexity declined.**

Adoption is Rafe's ruling and is taken **after** the tier-one floor gate, never before.

### 0.1 One limb of that bar is already in trouble, and it is worth knowing before spending

**Limb 3 — cost per accepted tile — is close to unwinnable, for a structural reason that has
nothing to do with image quality.** The two surfaces are on different billing regimes:

| | BitForge (PixelLab) | Retro Diffusion |
|---|---|---|
| regime | **subscription pool** — `Tier 2: Pixel Artisan`, 5000 generations/month | **prepaid, pay-per-image** |
| marginal cost of generation N+1 inside the pool | **≈ $0** | $0.03–$0.18 depending on model |
| evidence | `PIXELLAB-INTEGRATION-AUDIT-2026-08-25.md` §8.1 — the `/balance` object, verbatim | vendor API docs |

Inside an active pool that a whole session spends 1.8% of, RD does not beat BitForge on marginal
cost at any acceptance rate. It can only win limb 3 on **amortised** cost — plan price divided by
pool — and **the plan price is not recorded anywhere in this repo.**

> Per the bible's own clause-marker discipline: *a PLACEHOLDER is not law and is not usable as a
> gate — if a number you need is marked PLACEHOLDER, that is a finding to report, not a gap to
> fill with a guess.* The amortised BitForge per-generation cost is that number. **It is
> reported, not guessed.** Rafe knows the plan price; one line from him closes it.

This does not weaken the audit — limbs 1 and 2 are unaffected and are the interesting ones
anyway — but it does mean **the yield run should not be spent expecting limb 3 to carry the
verdict.**

---

## 1. WHAT WAS BUILT, AND WHAT IT IS CERTIFIED TO DO

`tools/retrodiffusion/audit_2026_08/` — 2,482 lines, all on disk, all compiling.

| file | what it is |
|---|---|
| `rd.py` | the v1 REST client: preflight, `check_cost` dry run, reconciled balance bracket, ledger, hard ceiling, refusal capture |
| `controls.py` | **positive controls for every guard in `rd.py`** |
| `census.py` | the seamless census — wrap seam + centre-to-edge vignette — with its own controls |
| `screen.py` | ring + census over every child; exact one-sided Fisher against the baseline |
| `audit.py` | the columns; free and paid halves separated |
| `yield_run.py` | 24 generations, two cells of twelve |
| `prompts/floor_material_rd.json` | the subject, with clause provenance **and its translation losses** |

### 1.1 Every guard has demonstrated it can fail — §13.5 satisfied before any pass is counted

`python3 controls.py` → **23 checks, 17 RED halves, 6 GREEN halves, 0 failed.**
`CONTROLS-RESULT.json` on disk. Verbatim failures, as recorded:

```
[PASS] RED   preflight/absent
       STOP — no Retro Diffusion credential.
         Set RD_API_KEY in the environment before running anything in this directory.

[PASS] RED   preflight/wrong_shape
       STOP — RD_API_KEY is set but is not a Retro Diffusion key (len=34 prefix_ok=False).
         Vendor keys begin 'rdpk-'. Refusing to send a credential to an endpoint it does not
         belong to.

[PASS] RED   budget/over
       REFUSING: 1 generation(s) would take this session to 4 of a hard ceiling of 3.
       Nothing was called and nothing was billed.

[PASS] RED   budget/session_ceiling
       REFUSING: ceiling 41 exceeds the session ceiling 40 declared in the brief.

[PASS] RED   budget/no_network        BudgetExceeded, 0 HTTP calls
[PASS] RED   divergence/diverge       matched=False divergence=0.12
[PASS] RED   ledger/no_key_on_disk    key_present=False redacted_present=True
[PASS] RED   partial/short            requested 4 images, received 3
[PASS] RED   reconcile/disagree
       pool moved 0.5 but calls billed 0.12 — the bracket and the per-call costs disagree
[PASS] RED   reconcile/unreadable
       balance unreadable at one or both ends of the bracket
[PASS] RED   refusal/400_insufficient_balance … /400_invalid_input … /422_validation …
             /429_rate_limit … /401_auth … /500_server_error
```

Three of these are worth naming because they are the brief's own named defects, closed in code
rather than in prose:

- **`budget/no_network`** — the ceiling refuses *before the socket opens*, proven by arming a
  tripwire transport that raises if touched. A ceiling enforced after the POST is a ceiling that
  bills.
- **`reconcile/disagree`** — *the gauntlet's unbracketed-balance defect does not get a third
  life.* A bracket that is only printed is not a bracket. `Session.close()` compares the pool
  delta against the sum of billed costs and writes `RECONCILE_RED` when they disagree. This is
  LOOP-PROCESS §4.2's cheap move — **compare numbers you already have** — not a new instrument.
- **`ledger/no_key_on_disk`** — the plant is the only realistic leak path, a **server error body
  that quotes the token back**, since the payload never carries it. The row lands with
  `<redacted>` and the credential is absent from the file.

### 1.2 The census caught its own first draw, before any real tile existed

This is the finding I would most want on the record, because it is the process working rather
than the process being described.

The seamless measure's first draw cut at the **90th percentile** of the tile's interior
value-steps. Its own control suite failed it on the first run:

```
[FAIL] control_seamless   expected SEAM=False  got SEAM=True   (wrap_x 8.72 vs cut 10.59)
[FAIL] control_flat       expected SEAM=False  got SEAM=True   (wrap_x 5.66 vs cut  5.47)
```

Both are tiles that **wrap exactly, by construction**. The reason is arithmetic, not taste: a
32px tile has 31 interior steps, so a wrap step drawn from the *same* distribution as the
interior sits above P90 about 10% of the time per axis, and the measure ORs two axes. **A ~19%
false-seam rate on seamless material was baked into the constant.**

Redrawn to an outlier test — `wrap > median(inner) + 3σ_robust(inner)` — and given a **subtle**
seam control so the stricter cut owed proof it had not bought its false-positive rate down by
going blind. Final suite:

```
[PASS] control_seamless     want SEAM=False  got SEAM=False | wrap_x  8.72 vs cut 14.89
[PASS] control_seam         want SEAM=True   got SEAM=True  | wrap_x 61.59 vs cut 15.38
[PASS] control_seam_subtle  want SEAM=True   got SEAM=True  | wrap_x 20.41 vs cut 14.54
[PASS] control_vignette     want SEAM=False  got VIG=True   | ratio 1.316
[PASS] control_flat         want SEAM=False  got SEAM=False | wrap_x  5.66 vs cut  5.94
```

**The subtle plant had to be fixed too, and it is the more interesting half.** Written as a flat
`+= 12` it made the tile *more* seamless — the periodic control field's own wrap step is about
−10 levels, so +12 nearly cancelled it and the wrap *fell* from 8.7 to 5.3. The instrument
correctly reported no seam; the control read as an instrument failure. That is **§4.1 LAW in
miniature** — *the plant must carry the defect on the axis the lever claims* — and a plant whose
sign is left to chance does not. The sign is now computed from the field.

**Nothing was cut to fit (§8): there is zero real data on disk.** The correction happened before
the first generation, which is the only time a constant may move.

The census is relabelled in its own docstring with the wording Rafe applied to the ring
instrument, because it has the same shape of limit: it measures **value** continuity and cannot
see a structural discontinuity that is value-matched. **Measured error in both directions;
orders attention, rules nothing.**

---

## 2. THE COLUMNS — measured, pending, and why

One real call per claim. **Free calls answer more of this than expected**, and that is
load-bearing: `check_cost: true` *validates* a payload as well as pricing it, so every question
of the form *"will this surface accept this?"* costs nothing. Columns 1, 6, 7 and the discovery
half of 2 and 8 are free.

| # | column | status | what is already known, and from where |
|---|---|---|---|
| 1 | **exact canvas at 32×32** | ⏸ pending key — **free** | **The live question of this audit.** Vendor docs give RD Pro 12–256, RD Plus 64–384, RD Fast 64–384 — which would put **32×32 out of reach of both cheap models** and reachable only at $0.18. The repo's own retired research doc contradicts that: *"rd_plus low_res supports 16–128 arbitrary width/height."* `audit.py --free` sweeps 7 sizes × up to 6 styles by `check_cost` and settles it for **$0**. |
| 2 | **reference / palette support** | ⏸ pending key — free probe + 1 paid | Documented: `input_palette` (all models), `reference_images` (RD Pro only, ≤9). Free probes test acceptance and limits; one paid call measures whether an 8-colour palette is actually *respected* rather than accepted-and-ignored (§4.1 — a parameter that validates is not a parameter that works). |
| 3 | **seed determinism** | ⏸ pending key — 2 paid | **Assume none, confirm.** Bible §13.7 records *"nothing on this platform is seed-reproducible"* — measured, about PixelLab. **RD documents a reproducible seed.** If it holds, this is a genuine structural difference: a reproducible surface is one where a ledger could store parameters instead of images. Two calls can *disprove* it and cannot prove it in general; that asymmetry is stated in the script and the ledger keeps storing images either way. |
| 4 | **latency and cost per call** | ⏸ pending key — no dedicated spend | `seconds`, `estimated_cost`, `actual_cost` on every ledger row. |
| 5 | **estimated vs actual** | ⏸ pending key — no dedicated spend | Every paid call is preceded by its own free `check_cost`. `estimate_divergence` and `estimate_matched` per row; a divergence is a finding. Guard certified (`divergence/diverge`). |
| 6 | **the balance ledger** | ⏸ pending key — **free** | `GET /v1/inferences/credits`. Two open questions the reads settle for $0: which field moves when billed (`credits` or `balance`), and **whether it settles** — PixelLab's settled *late and slowly*, two reads 15s apart agreeing on a figure that was 32% low. The same consecutive-reads discipline is applied until measured otherwise, and `stable=False` is written honestly when it never settles. |
| 7 | **the seamless flag** | ⏸ pending key — **free** existence, measured in the yield run | `tile_x` / `tile_y`, per-axis. **BitForge has no equivalent at all.** Semantics measured on the flag's own axis by cells N and T (below), not asserted from the docs. |
| 8 | **`bypass_prompt_expansion`** | ⏸ pending key — free probe | **Added by this audit, not in the brief.** RD documents an automatic LLM prompt-enrichment step. Left on, *the prompt actually sent is not the prompt in the file* — every clause-provenance line would be a claim about a string the model never saw, and LOOP-PROCESS §12 requires a generation prompt to be an auditable file. It is bypassed. ⚠ Its efficacy is **unverified**, and a parameter silently ignored and fully charged is a measured failure mode on the neighbouring platform (PixelLab AUDIT 9.3). |

### 2.1 The yield run's design, declared

24 generations, **two cells of twelve, both spent in full whatever cell N shows.**

| cell | `tile_x`/`tile_y` | what it is for |
|---|---|---|
| **N** | OFF | the like-for-like ring-rate comparison — BitForge had no such flag, so leaving it on would confound the rate with a lever the baseline never had |
| **T** | ON | the seamless census, **and the flag's own axis** |

Nothing else differs. §4.1: with one variable between two cells of twelve, the difference in
seam rate **is** the flag's effect, and the difference in ring rate says whether the flag costs
anything in the currency the bar is denominated in. `screen.py` computes the exact one-sided
Fisher for both, using the same `fisher_less` arithmetic that produced the baseline's p-values.

---

## 3. FINDINGS — four, banked without a credential

### FINDING 1 — `tools/retrodiffusion/` is not a stub. It is a complete retired integration.

The brief said *"a stub dir already exists — audit it first; repo wins over this prompt."* The
repo wins, and it says something different: **38 entries, 10 working Python clients, 14
candidate output directories, an extracted Oryx palette, an Oryx style reference, and a
conventions file with a documented style ruling.** All of it written for the
**Oryx-conformance track, which closed 2026-08-24**.

Every threshold in it answers to a retired corpus: the palette is the Oryx master palette
(§5.1's successor palette has **PLACEHOLDER** values, so there is currently nothing to lock to);
the style ruling picked `rd_plus__low_res` because it *"produces the closest match to Oryx
library aesthetics"*; the sprite-id namespaces are allocated against the Oryx tilesets; the
prompt template is tuned for 16×16/24×24 against tier one's **32×32**.

And as machinery it is missing every guard this audit is required to have: **no ledger, no cost
dry run, no balance bracket, no budget ceiling.** `batch_generate.py` gates spending on an
interactive `input()` and estimates cost from a hard-coded `$0.18`.

**Handled the way `tools/art_lint/` was handled** — the code was retained, the *bar* was
retired, and a retained tool with no live spec is a trap unless it says so on the tin. Added
[`../NOTICE.md`](../NOTICE.md), which separates what is retired from the handful of facts about
the **surface** that are still true and were read as evidence rather than re-bought:
the endpoint, the `X-RD-Token` header, the `RD_API_KEY` variable name, and that the response
carries `balance_cost` / `remaining_balance` — so the surface supports a balance bracket
natively.

### FINDING 2 — the repo disagrees with itself about the response field names

| source | cost field | remaining field |
|---|---|---|
| `tools/retrodiffusion/batch_generate.py` | `balance_cost` | `remaining_balance` |
| `docs/archive/oryx-track/RETRO_DIFFUSION_WALKTHROUGH.md` | `credit_cost` | `remaining_credits` |

Both are in-repo, both were written against real calls, and they do not agree. The client reads
**both** (`j.get("balance_cost", j.get("credit_cost"))`) and column 6 records which one is live.
A cost read from the wrong key is `None`, and a `None` cost silently disables the
estimate-vs-actual comparison **and** the balance reconciliation — which is exactly the class of
silent no-op LOOP-PROCESS §4.2 exists for. Worth the four characters.

### FINDING 3 — the research doc named in the brief is not on disk

Searched the repo and the home tree for `PixelLab_and_Alternatives_for_AI_Pixel-Art_Tileset_
Generation…`. **No file of that name exists on this machine.**

The closest in-repo research is
`docs/archive/story/other-stories-not-implemented/compass_artifact_wf-37844a6d-…_text_markdown.md`
— *"The right AI pixel art stack for an Oryx-style indie game"* — which is the RD-vs-PixelLab-vs-
Scenario comparison, and it is **misfiled under story archive** rather than with the art track.
It is Oryx-track material and its numbers are secondary-sourced exactly as the brief warns.

**It does not block the audit** — the authoritative v1 REST surface was read from the vendor's
own `api-examples` repository, and every claim taken from it is marked as vendor-documented
rather than measured. But two of its claims are load-bearing and now in direct conflict with the
vendor docs, which makes column 1 the audit's first question rather than a formality:

| claim | compass doc (Apr 2026, secondary) | vendor docs (read 2026-08-27) |
|---|---|---|
| low-res canvas | *"rd_plus low_res supports **16–128** arbitrary width/height"* | RD Plus **64–384**; only RD Pro reaches 12–256 |
| RD Plus price | ~$0.027/image (via `RD_CONVENTIONS.md`) | ~$0.06/image |

**If the vendor docs are right, 32×32 costs $0.18 on RD and the audit's economics change
before a single tile is judged.** One free `check_cost` sweep settles it.

### FINDING 4 — the translation to RD's payload shape is lossy, and it caps what a negative result may claim

RD's v1 REST surface **documents no negative-prompt field.** BitForge's floor prompt carries 31
negative terms, and three of them — `border, frame, outline` — are the **ring refusals that were
in play for every BitForge ring rate this audit compares against** (`REPORT-PARENT-RATE.md` §1:
*"Those ring refusals were in play for B-KAB and are in play here, unchanged, in both cells"*).
Four more BitForge parameters have no equivalent: `outline: lineless`, `detail`, `view`, and
`shading` — the last being the one BitForge lever measured live.

They are restated as positive assertions inside the prompt, which is weaker: **a negative list is
an exclusion and a sentence is a request.** The consequence is asymmetric and is written into the
prompt file so it cannot be forgotten at reporting time:

- **A ring rate WORSE than baseline cannot distinguish** *"the surface rings more"* from *"the
  surface was denied the ring refusals."* That is the honest ceiling on a negative result.
- **A ring rate BETTER than baseline is unaffected** — achieved with *fewer* refusals in hand,
  which is a stronger result, not a weaker one.

A second asymmetry, recorded in the same place: **the 25–45% baseline is a *conditioned* rate**
(C-GAB children at `style_strength` 50) and this run is **unconditioned**. RD's conditioning
mechanism is a different mechanism at a different price and its efficacy is unmeasured;
conditioning would add a second uncontrolled variable to a run whose job is to measure the
surface. So the question the yield run can actually answer is stated narrowly: *does raw RD
floor material ring less than conditioned BitForge floor material?*

---

## 4. WHAT I AM NOT CLAIMING

- **Not that RD works.** No call was made. Every column is pending and marked pending.
- **Not that the live pricing is anything.** It was **not** verified at a first paid call,
  because there was no first paid call. The table in Finding 3 compares two *secondary* sources
  against each other, which is a conflict to resolve, not a resolution.
- **Not that 32×32 is or is not reachable.** That is column 1 and the two sources disagree.
- **Not that the seed is or is not reproducible.** RD documents it; the bible's measured fact is
  about a different platform. Column 3 exists precisely because a vendor claim is not evidence.
- **Not that the census would pass an RD tile.** Its controls prove it can fire and stay quiet on
  *planted* material. It has never seen a real generation from any surface.
- **Not that the client is bug-free.** Its *guards* are certified against planted defects; the
  paths that only run against a live server — image decode, async, the styles selector — have
  been exercised against stubs, not against RD.
- **Not that limb 3 is decided.** It is *disadvantaged*, structurally, and the number that would
  settle it is a PLACEHOLDER reported rather than guessed.

---

## 5. EVIDENCE

```
CONTROLS-RESULT.json              23 checks, 17 RED, 6 GREEN, 0 failed — VERDICT PASS
census_controls/RESULT.json       5 cases, suite_pass true
census_controls/*.png             the five planted control tiles, on disk
```

```
$ git diff --stat
 tools/retrodiffusion/NOTICE.md                                 |  45 ++
 tools/retrodiffusion/audit_2026_08/AUDIT-RD.md                 | this file
 tools/retrodiffusion/audit_2026_08/CONTROLS-RESULT.json        | 193 ++
 tools/retrodiffusion/audit_2026_08/README.md                   | 112 ++
 tools/retrodiffusion/audit_2026_08/audit.py                    | 295 ++
 tools/retrodiffusion/audit_2026_08/census.py                   | 291 ++
 tools/retrodiffusion/audit_2026_08/census_controls/RESULT.json | 190 ++
 tools/retrodiffusion/audit_2026_08/census_controls/*.png       | 5 files
 tools/retrodiffusion/audit_2026_08/controls.py                 | 413 ++
 tools/retrodiffusion/audit_2026_08/prompts/floor_material_rd.json | 116 ++
 tools/retrodiffusion/audit_2026_08/rd.py                       | 512 ++
 tools/retrodiffusion/audit_2026_08/screen.py                   | 160 ++
 tools/retrodiffusion/audit_2026_08/yield_run.py                | 155 ++
 16 files changed, 2482 insertions(+)
```

**Spend to date: $0.00. Generations: 0. Ledger rows from RD: 0.** The ledger files do not exist
yet because nothing has been called, and an empty ledger is not written to pretend otherwise.

## 6. REFUSALS HONOURED

Did not touch tier one's session, corpus, or surface freeze — no file under `tools/tier1_floors/`
or `tools/pixellab/probe_6_4/` is modified, and `ring_instrument.py` is **shelled out to as a
subprocess rather than imported**, so its constants cannot be monkeypatched even by accident.
Promoted nothing. Spent nothing. Printed no key. Bought nothing.

---

## 7. WHAT HAPPENS WHEN THE KEY ARRIVES

No further design work. `README.md` carries the run order; the whole audit is one shell session:

```bash
export RD_API_KEY="rdpk-..."
python3 controls.py && python3 census.py --controls   # free, re-certify
python3 audit.py --free                               # free: styles, canvas sweep, probes
python3 audit.py --paid --style <resolved>            # ~5 generations
python3 yield_run.py --style <resolved>               # 24 generations
python3 screen.py                                     # free: ring + census + Fisher
```

**29 of the 40-generation ceiling**, leaving 11 in reserve for the blind A/B's own needs and for
a cell that comes back short.

**The one piece that still needs Rafe rather than a key:** the blind A/B seats are run against
BitForge GAB-line material from the ledger, shuffled and unlabelled as to source, with a plant
per §4 — *a passed plant voids the seat.* That is built as a plan, not as code, because the
seat harness lives on the tier-one side of the freeze and this session does not touch it.

**Rafe's ruling on adoption is owed only after the tier-one floor gate**, per the bar in §0. If
limbs 1 and 2 both fail, §0's own default applies without a ruling: *finding recorded, no second
surface, complexity declined.*
