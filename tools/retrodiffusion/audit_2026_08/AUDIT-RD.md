# RETRO DIFFUSION — connection audit

> **THE AMENDED RUN'S INTENT, VERBATIM, AT THE TOP WHERE IT CANNOT BE SKIPPED:**
>
> **"This run measures RD's best-known configuration against the bar. It is NOT a controlled
> like-for-like against the baseline — style arm, prompt, and cell design all changed
> simultaneously."**
>
> A **fourth** thing changed too and is named rather than folded in: `input_palette` is applied,
> without which amendment item 9's ramp-coverage measurement has nothing to measure. So the
> honest count is four simultaneous changes, not three. **Every comparison in §6.4 against the
> 5/20 and 9/20 baseline inherits this caveat and none of them is a controlled result.**

**CONNECTED. Eight columns measured, then a 20-tile amended cell. 26 paid generations,
$0.650 spent, 42 free dry runs.**
Nothing landed, nothing was promoted, no corpus file changed, no constant in any pre-existing
instrument was altered, and **tier one is untouched and stays frozen on BitForge to completion
regardless of anything in this document.**

**Both ruling triggers from the pre-run draft are now RESOLVED** — §1.1.4(e) by a top-up
(balance re-read at **$10.26 settled**, gate $0.55 passed) and §1.1.4(b) by the design thread's
amendment. The amended cell has been run in full: **§6**. **No adoption language appears
anywhere in this document; adoption is ruled in the design thread after the tier-one floor
gate.**

---

## 0. THE ANSWER SO FAR, STATED FIRST

**RD connects, prices honestly, and does two things BitForge measurably cannot. It also framed
every tile it produced until the style was changed — and the style the retired track ruled
"primary" is the one doing the framing.**

Three results that would change how a pipeline is built, all measured today:

1. **RD is seed-reproducible. BitForge is not.** Two identical calls, same seed, returned
   **byte-identical PNGs** — sha256 `791d8ad94cc34e25…` twice. Bible §13.7 records *"nothing on
   this platform is seed-reproducible — measured on every surface tried"*, and that fact is
   about PixelLab. It does not generalise. On RD, an image **is** re-derivable from
   (prompt, seed), which is the precondition for a ledger that stores parameters instead of
   megabytes.
2. **RD hard-locks to a palette image. BitForge has no equivalent.** An 8-colour ramp in
   `input_palette` returned a tile with **5 distinct colours**. §5.1's *"one palette governs the
   whole game, every opaque pixel is an exact bible hex or the asset is rejected outright"* is a
   zero-mercy gate this surface can satisfy **at generation time** rather than by post-hoc
   rejection.
3. **32×32 is native and cheap.** `rd_plus__low_res` accepts 16–128, returned exactly 32×32, at
   **$0.025**. No downscale, no upscale.

And the finding that stopped the first batch, then the amended cell that followed it:

4. **The ring was the STYLE, not the surface.** Every tile from `rd_plus__low_res` came back
   with a dark frame around the canvas and a regular 3×3 lattice inside it — §12.1's keyline and
   §8.3.1's lattice, together, in one image. Switching to `rd_tile__single_tile` at the **same
   price** produced a full-bleed, unframed, instrument-CLEAN field on the first call.
5. **The amended 20-tile cell returned RING 0/20 — and tiles that are still not good.** The ring
   axis is clean and the §8.3.1 axis is not: by eye, roughly half are running-bond **lattices**
   and roughly half are featureless **gravel**, and they read as *wall* rather than *floor*.
   **No instrument sees either failure, and none was built for it** (§13.4). §6.5 states this as
   an unblinded eye read, not a seat.
6. **Palette membership passed 20/20 at 100% of pixels while the value structure collapsed** —
   mean 4.75 of 8 ramp steps, **the darkest step absent from every tile**, three middle steps
   carrying 82%. That is amendment item 9's question answered on the first twenty tiles (§6.6).

**Limb 3 of the bar is now decided against RD, conditionally** (§0.2). **This document contains
no adoption recommendation in either direction** — that ruling is the design thread's, after the
tier-one floor gate.

### 0.1 The bar, declared before any generation

Recorded before a single image existed — bible §13.6, a candidate never contributes to its own
acceptance bar.

> **RD becomes a candidate materials supplier only if it wins or ties the blind A/B AND at
> least one of:** (1) ring rate materially below the 25–45% baseline; (2) seamless census pass
> where BitForge fails it; (3) cost-per-accepted-tile materially lower.
> **Otherwise: finding recorded, no second surface, complexity declined.**

### 0.2 Limb 3 is settled, and it is settled against RD

Rafe supplied the number that was a PLACEHOLDER in the pre-key draft: **PixelLab Tier 2 Pixel
Artisan, ~$25/month, 5000-generation pool.**

| | BitForge | Retro Diffusion |
|---|---|---|
| regime | subscription pool | prepaid, pay-per-image |
| **amortised** per generation | **$25 / 5000 = $0.005** | **$0.025** (measured, `rd_plus__low_res` / `rd_tile__single_tile` @32×32) |
| **marginal**, inside an unspent pool | **≈ $0.000** | **$0.025** |
| cheapest 32×32 anywhere on the surface | — | $0.017 (`rd_fast__low_res`) |

**RD is 5× BitForge amortised and unboundedly more expensive marginally.** For RD to win limb 3
on amortised cost its acceptance rate would have to be **5× BitForge's just to break even** —
and since a whole tier-one session spent 1.8% of the monthly pool, the marginal comparison is
the operative one, and RD cannot win it at any acceptance rate.

**Limb 3 is dead. The verdict rests on limbs 1 and 2** — ring rate and the seamless census —
which is where it should have rested anyway.

> **⚠ LIMB 3 IS DEAD *CONDITIONALLY*, AND THE CONDITION IS NOT A TECHNICAL ONE.**
>
> **It rests entirely on the BitForge subscription being retained for hero work.** The $0.005
> figure is a plan price divided by a pool, and the ~$0.000 marginal figure exists only because
> the pool is already paid for and 98% unspent. **Both numbers are properties of a billing
> arrangement, not of the surface.**
>
> **If that subscription ever ends, the marginal comparison inverts and limb 3 REVIVES** —
> BitForge would go to its own per-image rate or to nothing at all, and RD's $0.025 would be
> competing against a real number instead of against a sunk one. This is recorded so that a
> future session reading *"limb 3 is dead"* does not treat it as a settled property of RD.
>
> **The trigger to re-open: any change to the PixelLab subscription.** Nothing else about this
> comparison needs to move.

---

## 1. THE COLUMNS — measured

One real call per claim. **42 of the 68 calls were free**: `check_cost: true` prices a payload
without generating, and the `/styles/selector` endpoint returns per-style canvas limits, so
column 1 and most of column 2 cost nothing at all. Figures below are the column-audit values;
the amended cell's own totals are in §6.2.

| # | column | verdict |
|---|---|---|
| 1 | **exact canvas at 32×32** | ✅ **NATIVE.** Requested 32×32 → returned 32×32, `upscale_output_factor: 1`. `rd_plus__low_res`, `rd_fast__low_res`, `rd_mini__low_res` all accept **16–128**; `rd_tile__single_tile` 16–64; `rd_tile__tileset` 16–32; every `rd_pro__*` 12–256. **32×32 is comfortably inside the cheap tier.** |
| 2 | **reference / palette** | ✅ **PALETTE LOCK IS REAL — 8-colour ramp in, 5 distinct colours out.** Not accepted-and-ignored; measured on the returned pixels. `reference_images` (style conditioning) is **RD Pro only** per the selector's `supports_reference_images` flag, i.e. **$0.18/image**. |
| 3 | **seed determinism** | ✅ **REPRODUCIBLE.** Assume-none, confirmed otherwise: 2 calls, identical seed, **1 distinct sha256 of 2**, byte-identical. Two calls can disprove and cannot prove in general, so this is evidence, not a guarantee — and the ledger keeps storing images regardless. |
| 4 | **latency & cost** | ✅ **11.4 s mean** (9.2–15.6 s) on the columns, **13.5 s mean** across the 20-cell. One image per call, $0.025 at 32×32. `num_images: 4` prices at $0.098 — a batch discount of 2%, i.e. none. |
| 5 | **estimated vs actual** | ✅ **26 of 26 EXACT** across the whole session (6 columns + 20 cell). `estimate_divergence` 0.0 on every billed call. **No divergence finding, on the largest sample available.** |
| 6 | **the balance ledger** | ✅ **`balance` is the spendable field; `credits` is inert.** `{"balance": 0.412, "credits": 50}` → six generations moved `balance` to `0.262` (exactly 6 × $0.025) and left `credits` pinned at 50.0. **It settles instantly** — no lag, unlike PixelLab's, which settled late enough that two reads 15 s apart agreed on a figure 32% low. |
| 7 | **the seamless flag** | ⚠️ **EXISTS, UNUSABLE WHERE IT IS WANTED.** `tile_x`/`tile_y` work on `rd_plus__low_res` and fail with **HTTP 400 `inference_failed`** across the **whole `RD Tileset` family** — isolated by amendment item 10, Finding 7. |
| 8 | **`bypass_prompt_expansion`** | ✅ accepted at no price difference. Efficacy still unverified — accepted is not honoured (§4.1), and it is held ON so the prompt sent is the prompt in the file. |

**Corrects the pre-key draft.** That draft flagged a conflict between the archived compass
research (*"rd_plus low_res supports 16–128 arbitrary width/height"*) and the vendor's own
README summary (RD Plus 64–384, only RD Pro reaching 12–256), and named column 1 as the audit's
first question. **The compass doc was right and the README summary was wrong** — the README
gives model-family ranges that do not reflect per-style ranges, and `/styles/selector` settles it
for free. The economics conclusion moves in RD's favour: 32×32 costs $0.025, not $0.18.

---

## 2. WHAT THE TILES ACTUALLY LOOK LIKE

Six generations, all at 32×32. Shown at 8×.

`audit_out/col_sheet.png` — the four audit tiles, all `rd_plus__low_res`:

| tile | ring instrument | what it is |
|---|---|---|
| `col1_native` | CLEAN | 3×3 regular grid of flagstones, **dark frame around the canvas** |
| `col2_palette` | CLEAN | irregular bond — the best material of the six — **dark frame around the canvas** |
| `col3_seed` ×2 | **RING** | speckle field, 1 px constant-width dark border, bbox `[0,0,31,31]` |

`audit_out/probe_sheet.png` — the style probe:

| tile | ring instrument | what it is |
|---|---|---|
| `plus_tiled` (`rd_plus__low_res` + `tile_x`/`tile_y`) | **RING** | 3×3 lattice of framed cells. §8.3.1 and §12.1 in one image. |
| `tilestyle_plain` (`rd_tile__single_tile`) | **CLEAN** | **full-bleed, unframed, edge-to-edge.** Composition correct. |

The instrument's 2-of-4 on the audit tiles is not a rate (n=4) and is not reported as one. What
it does show is the instrument behaving as characterised: on `col1`/`col2` the canvas-edge dark
run is the same value as the interior joints, so it reads as a **mortar joint network** rather
than a drawn ring — the exact C-GAB case `REPORT.md` reasons about — while on the speckle tiles
the border is a distinct constant-width line against noise and fires immediately.

**`tilestyle_plain` gets the composition right and the material wrong.** It is gravel: no bond,
no joints, no stone-to-stone value break. That is §8.3.1's **mirror** — *incident-free is not
featureless* — and it is a prompt problem, not a surface problem, which is what the remaining
budget exists to work on.

---

## 3. FINDINGS

### FINDING 1 — the ring was the STYLE, and the retired track's ruled style is the culprit

`RD_CONVENTIONS.md` ruled `rd_plus__low_res` the **primary production style**, on the criterion
*"produces the closest match to Oryx library aesthetics"*. Measured today against a floor
subject, it frames the canvas on **every** generation and lays a regular grid inside it.
`rd_tile__single_tile`, at the **identical price**, produced a full-bleed unframed field on the
first call.

Two generations, $0.05, and it moved the yield run off a known-bad arm before 24 were spent on
it. **The retired ruling was not merely stale in its criterion — it points at the wrong style
for tiles**, which is the sort of thing a retirement banner does not catch on its own.
`../NOTICE.md` is updated.

### FINDING 2 — `check_cost` is a price oracle, NOT a validator

This audit's design asserted that the free dry run *validates* a payload as well as pricing it,
and used that to justify answering column 1 for free. **It is not true, and the measurement is
unambiguous:** `check_cost` priced `rd_tile__single_tile` + `tile_x`/`tile_y` at $0.025 and the
inference endpoint then refused the identical payload with HTTP 400.

```
tilestyle_tiled  rd_tile__single_tile  REFUSED:invalid_input  est=0.025 act=None
{"detail":{"code":"inference_failed","message":"Unable to run inference.",
 "request_id":"054a972b-b253-41d5-9c68-468fec935f5a"}}
```

Consequences, both already handled: a free acceptance is evidence about **price**, not about
whether a call will succeed; and the refused call was **not billed**, which the balance
confirms. The `_classify` split that keeps `insufficient_balance` out of the same bucket as
`invalid_input` earned itself here — the body says neither, and the row records the server's own
words verbatim rather than a status line.

### FINDING 3 — the seamless flag and the only unframed style are mutually exclusive

`tile_x`/`tile_y` work on `rd_plus__low_res` (which frames every tile) and fail with
`inference_failed` on `rd_tile__single_tile` (which does not). **The one style that gets the
composition right cannot be asked for seamlessness.**

This kills the declared two-cell design — cells N and T differed only in those flags, and there
is no longer a single style on which both cells can run. See §6, decision 2.

### FINDING 4 — a framed tile PASSES the seamless census, and that is not a bug

All four audit tiles passed both census measures — **including the two the ring instrument
called RING.** The census is not broken; the two instruments are catching opposite things, and
the interaction is worth stating as a general fact:

> **A keyline around the canvas guarantees a seamless verdict.** A border makes every edge of
> the tile identical to every other edge, so the wrap join is perfectly value-continuous. The
> tile lays without a seam *because* it is framed.

Which means **any vendor "seamless tiling" claim can be satisfied by framing the tile** — by
drawing the one construction §12.1 forbids outright. The research doc's warning (*vendor
"seamless" is marketing until baked off*) is right for a sharper reason than it knew. **The
seamless census may never be read without the ring screen beside it**, and `screen.py` runs both
for that reason.

### FINDING 5 — my own reconciliation guard fired on its first live contact, on two real bugs

`Session.close()` returned **RECONCILE_RED** on the audit run: pool delta 0.0 against $0.025
billed. Both causes were defects in this session's code, and both are the shape LOOP-PROCESS
§4.2 exists to catch:

1. **The bracket read a field that never moves.** `_pool()` preferred `credits` (pinned at 50)
   over `balance` (the spendable dollars). Without the reconciliation step it would have printed
   `50.0 -> 50.0` and looked perfectly fine — *a step that runs, changes nothing, and says so
   quietly.*
2. **The billed sum depended on the caller remembering to report it.** `audit.py` called
   `note_billed()` for column 1 and not for columns 2 and 3, so $0.025 was reconciled against
   $0.100 actually spent. A reconciliation a caller can defeat by forgetting a call is Ruling
   104's wish, not a step.

Fixed: `_pool()` prefers `balance`, with the measurement cited in its docstring; and
`Session.close()` now sums `actual_cost` **from the ledger it wrote**, not from an attribute
anyone has to maintain. The real numbers reconcile exactly — **$0.412 → $0.262, delta $0.150,
billed $0.150.**

The control suite needed fixing too, and that half matters: `reconcile/agree` had been planting
its spend by setting `s.billed` directly, which made it a control over a path the live run does
not use. It now plants **through the ledger**. §4.1 again — *the plant must sit on the axis the
guard measures.*

### FINDING 6 — `tools/retrodiffusion/` is not a stub (carried forward, unchanged)

38 entries, 10 working clients, an Oryx palette, and a conventions file — a complete integration
from the **retired Oryx track**, with no ledger, no dry run, no bracket, no ceiling.
`../NOTICE.md` separates the retired bar from the surface facts still worth reading, and now
also carries Finding 1's correction to the style ruling.

---

### FINDING 7 — amendment item 10, answered: it is the whole `RD Tileset` FAMILY, not one style

The brief asked for **one free dry-run probe**. **A free probe cannot answer this question**, and
that is itself the answer to half of it: `check_cost` accepted **all eight** combinations tried,
including the one already measured to fail. Finding 2 reconfirmed on a wider sample — it is a
price oracle, not a validator.

So the isolation was done with the **cheapest real calls**, and all three were **refused and not
billed** (balance unmoved at $10.26 across all three):

| probe | style | size | flags | result |
|---|---|---|---|---|
| `tile_x` alone | `rd_tile__single_tile` | 32 | `tile_x` | **REFUSED** `inference_failed` |
| both flags, larger canvas | `rd_tile__single_tile` | 64 | `tile_x`+`tile_y` | **REFUSED** `inference_failed` |
| a **sibling** tileset style | `rd_tile__tile_object` | 32 | `tile_x`+`tile_y` | **REFUSED** `inference_failed` |

Against the already-measured control that `rd_plus__low_res` + both flags **succeeds**, this
rules out every alternative explanation:

- **Not a request-shape bug** — the identical flags succeed on another style.
- **Not a single-flag issue** — `tile_x` alone fails too.
- **Not size-dependent** — fails at 64 as well as 32.
- **Not specific to `rd_tile__single_tile`** — a sibling in the same group fails identically.

> **The `RD Tileset` style family and the `tile_x`/`tile_y` seamless flags are mutually
> exclusive.** The most likely reading is that the tileset styles carry their own internal
> tiling handling and the flags collide with it, but **that is inference, not measurement**, and
> the server's message (`"Unable to run inference."`) says nothing either way.

The practical consequence is the one the amendment already absorbed: the seam question on the
only usable style is answered **post hoc**, never by the flag.

### FINDING 8 — the reconciliation guard fired a THIRD time, on a third distinct bug

Three instances this session, all the same family (LOOP-PROCESS §4.2), none of which would have
gone red without the reconciliation step:

| # | bug | what it would have printed instead |
|---|---|---|
| 1 | the bracket read `credits` (pinned at 50) instead of `balance` | `50.0 -> 50.0`, looking perfect |
| 2 | `billed_sum` depended on callers remembering `note_billed()` | $0.025 against $0.100 spent |
| 3 | **`Session` built its own ledger while the run wrote another** | `billed 0.0`, and a **false** $-0.5 discrepancy on a run that was exactly on budget |

The third is the sharpest, because **it fired loudly on a run where nothing was wrong with the
money.** A guard that only ever fires on real problems is not being tested; this one produced a
false positive, the false positive was traced to the instrument rather than to the spend, and
the correction is **appended** to the ledger rather than replacing the original row. Both
figures survive in `MANIFEST.json`.

`Session` now takes `ledger=`. The control suite needed its own fix earlier for the same class
of reason — `reconcile/agree` had planted spend by setting an attribute the live path does not
use — and it now plants **through the ledger** (§4.1: the plant must sit on the axis the guard
measures).

### FINDING 9 — `rd_tile__single_tile` is served by `rd_fast`, and priced above `rd_fast__low_res`

Every one of the 20 cell responses reports `"model": "rd_fast"`. But `rd_fast__low_res` prices at
**$0.017** and `rd_tile__single_tile` at **$0.025** — a 47% premium for what the response says is
the same underlying model.

**Reported, not explained.** The premium may buy tileset-specific conditioning that does not show
up in the model field, and the response's `model` may be a family label rather than a weights
identifier. What it does mean concretely: **`model` is not a sufficient provenance key on this
surface**, which is a second reason — beyond the vendor-reweighting risk in RD_CONVENTIONS.md
LAW 2 — that the manifest stores the returned bytes and not merely the parameters.

## 4. THE INSTRUMENTS

`controls.py` → **23 checks, 17 RED halves, 6 GREEN halves, 0 failed.** Every guard in `rd.py`
has demonstrated it can fail, with no network and no credential.

`census.py --controls` → **5 cases, PASS.** Its first draw cut at the 90th percentile of interior
value-steps and its own controls failed it immediately: a 32 px tile has 31 interior steps, so a
clean wrap sits above P90 ~10% of the time per axis, ORed over two axes — **a ~19% false-seam
rate baked into the constant.** Redrawn to a 3σ outlier test with **zero real data on disk**, so
nothing was cut to fit (§8). The subtle-seam plant needed fixing too: written as a flat `+= 12`
it made the tile *more* seamless by cancelling the field's own −10 wrap step, so the instrument
was right and the control was wrong. §4.1 in miniature.

`ring_instrument.py` — constants untouched, **shelled out to as a subprocess rather than
imported**, so a monkeypatch is not possible even by accident. Its own `--controls` suite ran and
passed in the same invocation as every screening call.

---

## 5. WHAT I AM NOT CLAIMING

- **Not that 0/20 is a controlled ring rate.** Four things changed at once. It is RD's
  best-known configuration measured against the bar, not a like-for-like against the baseline,
  and §6.4's p-values inherit that in full.
- **Not that the tiles are good.** RING 0/20 is a true result **on the ring axis only**. By eye,
  roughly half are §8.3.1 lattices and roughly half are §8.3.1-mirror gravel, and they read as
  wall rather than floor. No instrument saw any of that and none was built for it (§13.4).
- **Not a seat verdict.** §6.5 is my own unblinded read. **No blind seat has seen these tiles and
  no human gate has been near them.** The blind A/B was not run.
- **Not that the palette lock is register-correct.** 100% membership with a collapsed value
  range is exactly the pair of facts §6.6 exists to separate. §5.1's actual values are still
  PLACEHOLDER, so there is no bible palette to lock to yet.
- **Not that seed reproducibility generalises.** Two calls, one style, one seed. It disproves
  "assume none"; it does not prove determinism across styles, sizes, or time — and per
  RD_CONVENTIONS.md LAW 2 it is provenance, never a storage substitute.
- **Not that limbs 1 or 2 are decided.** Limb 1 has a number but not a controlled one, and limb
  2's flag turned out to be unusable on the only style worth running. Limb 3 is decided, against
  RD, and **conditionally** (§0.2).
- **Not an adoption recommendation, in any direction.** No sentence of this document argues for
  or against taking RD on. That ruling is the design thread's, after the tier-one floor gate.
- **Not that `bypass_prompt_expansion` works.** Accepted is not honoured.
- **Not that Finding 9's price premium is understood.** It is reported, not explained.

## 6. THE AMENDED RUN — n=20, `rd_tile__single_tile`, no tiling flags

Both decisions the pre-run draft left open were resolved by the design thread. Money: the
balance was topped up and the gate re-read **$10.26 settled, from the `balance` field** — the
$0.55 precondition passed with room. Design: the N/T cells were replaced.

### 6.1 Declared before the first call

| | |
|---|---|
| n | **20**, matching the baseline's n exactly. Spent in full. |
| style | `rd_tile__single_tile`, 32x32, **no tiling flags** |
| prompt | `prompts/floor_material_rd_v2.json` — reworked toward §8.3.1's **mirror** |
| palette | the 8-step neutral grey ramp, built in code (not the retired Oryx palette) |
| budget | **$0.500** declared |
| seam | measured **post hoc**, reported only in the same row as the ring result |

### 6.2 The totals

| | declared | actual |
|---|---|---|
| generations | 20 | **20, all OK, 0 refused** |
| spend | $0.500 | **$0.500** |
| balance | — | $10.26 -> $9.76, **delta $0.500** |
| estimate vs actual | — | **20 of 20 exact** |
| distinct images | — | **20 of 20** |
| latency | — | 13.5 s mean |
| model served | — | **`rd_fast`** — see Finding 9 |

**No discrepancy. Declared and actual agree exactly, and the balance bracket reconciles.**

> WARNING — **ONE DISCREPANCY WAS FLAGGED BY THE RUN ITSELF AND IT WAS AN INSTRUMENTATION
> ARTEFACT, NOT A MONEY FACT. Recorded rather than tidied.** `run20.py` printed
> `declared $0.500 actual $0.0 difference $-0.5 DISCREPANCY FLAGGED` and closed
> `RECONCILE_RED`. Cause: `Session` built its **own** `ledger.jsonl` while `generate()` wrote
> `cell20_ledger.jsonl`, so `billed_from_ledger()` summed an empty file. The money was right the
> whole time. Fixed (`Session` now takes `ledger=`); the corrected reconciliation is **appended**
> to the ledger as `close_CORRECTED` with the original row left in place, and `MANIFEST.json`
> carries both figures. See Finding 8 — the **third** instance this session.

### 6.3 Per-tile: ring and seam in the same row, per amendment item 5

Seam is from the post-hoc opposite-edge continuity census. **Neither column is quotable without
the other** (RD_CONVENTIONS.md LAW 1).

| seed | RING | seam x | seam y | vignette | ramp steps | on-ramp px | distinct |
|---|---|---|---|---|---|---|---|
| 30000 | CLEAN | SEAM | SEAM | — | 6 / 8 | 100% | 6 |
| 30001 | CLEAN | — | — | — | 4 / 8 | 100% | 4 |
| 30002 | CLEAN | — | — | — | 5 / 8 | 100% | 5 |
| 30003 | CLEAN | — | — | — | 4 / 8 | 100% | 4 |
| 30004 | CLEAN | — | — | — | **7 / 8** | 100% | 7 |
| 30005 | CLEAN | — | SEAM | — | 5 / 8 | 100% | 5 |
| 30006 | CLEAN | — | SEAM | — | 5 / 8 | 100% | 5 |
| 30007 | CLEAN | — | — | — | 5 / 8 | 100% | 5 |
| 30008 | CLEAN | — | — | — | 5 / 8 | 100% | 5 |
| 30009 | CLEAN | SEAM | — | — | 4 / 8 | 100% | 4 |
| 30010 | CLEAN | — | — | — | 4 / 8 | 100% | 4 |
| 30011 | CLEAN | — | — | — | 5 / 8 | 100% | 5 |
| 30012 | CLEAN | — | SEAM | — | 4 / 8 | 100% | 4 |
| 30013 | CLEAN | SEAM | SEAM | — | 5 / 8 | 100% | 5 |
| 30014 | CLEAN | — | — | — | 4 / 8 | 100% | 4 |
| 30015 | CLEAN | — | — | — | 4 / 8 | 100% | 4 |
| 30016 | CLEAN | — | — | — | 4 / 8 | 100% | 4 |
| 30017 | CLEAN | — | — | — | 5 / 8 | 100% | 5 |
| 30018 | CLEAN | — | SEAM | — | 5 / 8 | 100% | 5 |
| 30019 | CLEAN | — | SEAM | — | 5 / 8 | 100% | 5 |
| **totals** | **RING 0 / 20** | **SEAM 8 / 20, either axis** | | **VIGNETTE 0 / 20** | **mean 4.75 / 8** | **100%** | |

### 6.4 Against the baseline — with the header caveat attached to every line

Exact one-sided Fisher, the same `fisher_less` arithmetic that produced the baseline's own
p-values.

| comparison | RD | BitForge | p (RD lower) |
|---|---|---|---|
| instrument rate | **0 / 20** | 5 / 20 | **0.0236** |
| seat-adjusted rate | **0 / 20** | 9 / 20 | **0.00061** |

**These are not controlled results and must never be quoted as if they were.** Four things
changed at once. What they establish is narrow and worth stating precisely: **RD's best-known
configuration produced no mechanical rings in 20 tiles.** Whether that is the surface, the
tile-dedicated style, the reworked prompt, or the palette lock is **not separated by this run
and cannot be separated by it.**

### 6.5 What the tiles are, by eye — NOT INSTRUMENTED, NOT A SEAT

The ring axis came back clean. **The tiles are not clean**, and the difference matters enough to
state plainly with its status labelled.

**The population is bimodal, and both modes fail §8.3.1 — from opposite sides:**

- **Roughly half are running-bond BRICKWORK on a near-fixed pitch.** Laid 2x2 the courses line
  up into ruled horizontal bands across the field. That is §8.3.1 verbatim — *"any treatment
  applied at a constant position within a tile becomes a lattice when tiled"* — and it is the
  same construction the sighted round's wall tops were culled for.
- **Roughly half are fine GRAVEL** — even noise, no bond, no joints, no stone-to-stone value
  break. That is §8.3.1's **mirror**: *"incident-free is not featureless ... stripping that to
  avoid a motif produces the flat clone field the same seats cull on sight."*

**The ring instrument cannot see either failure**, and that is not a defect in it — a running
bond is not a closed contour, so criterion 1 never fires. **RING 0/20 is a true result on the
ring axis and is not a statement that the tiles are good.** There is no lattice instrument and
per §13.4 this audit does not build one.

**A register finding outranks both: they read as WALL, not FLOOR.** Brick coursing and rubble
both present as vertical masonry seen face-on, when the prompt asked for *"seen from directly
above."* §3's projection question, arriving on a new surface.

> **STATUS OF THIS SUBSECTION, SO IT CANNOT BE MISTAKEN FOR A GATE:** it is my own unblinded eye
> read, made while knowing what the prompt asked for. **It is not a blind seat and not a
> verdict.** No seat has seen these tiles; no human gate has been near them. Counts are given as
> "roughly half" rather than as a table, because a precise split is exactly the number that
> would later get quoted as though it had been measured.

### 6.6 Amendment item 9 — ramp coverage. The headline is a collapse.

**Palette membership: 20 of 20 tiles, 100% of pixels EXACTLY on the 8-step ramp.** Not
approximately — every pixel is one of the eight declared colours. §5.1's zero-mercy gate would
pass all twenty without a murmur.

**Ramp coverage: mean 4.75 of 8 steps. Range 4-7.** The distribution is not merely narrow, it is
centred:

| ramp step | 0 darkest | 1 | 2 | 3 | 4 | 5 | 6 | 7 lightest |
|---|---|---|---|---|---|---|---|---|
| mean share of pixels | **0.000** | 0.005 | 0.058 | 0.214 | **0.343** | 0.262 | 0.108 | 0.009 |

**The darkest step never appears in any of the twenty tiles. The two ends together carry under
1.5% of all pixels. Three middle steps carry 82%.**

This is exactly what amendment item 9 was written to catch: **membership passes while the value
structure collapses.** A lint checking membership alone gives all twenty a clean bill, and the
tiles have no deep shadow and no highlight — the value range the wall recipe and §6.5's value
stack both depend on.

**Reported, not gated, and no lint change is proposed here** — that is a later ruling. What the
run establishes is that the two properties are **separable in practice, not only in principle**,
and that on this surface they came apart on the first twenty tiles.

## 7. EVIDENCE

```
audit_out/audit_ledger.jsonl    the column audit + style probe + item-10 isolation
audit_out/col1|col2|col3/       the four column tiles
audit_out/probe_style/          the two style-probe tiles
audit_out/item10/               (all three item-10 probes refused; no images written)
audit_out/col_sheet.png         contact sheet, 8x
audit_out/probe_sheet.png       contact sheet, 8x
audit_out/ring_paid.json        ring instrument, controls PASS
audit_out/census_paid.json      census, per-tile verdicts

cell20_out/cell20_ledger.jsonl  the amended cell, one flushed row per call + close_CORRECTED
cell20_out/MANIFEST.json        per generation: prompt, seed, model, FULL params, sha256,
                                ramp coverage — AND the bytes on disk beside it (LAW 2)
cell20_out/tiles/               the 20 tiles
cell20_out/plates/              every tile laid 2x2 at 4x — §8.3's scale rule
cell20_out/ring.json            ring instrument, controls PASS, 0/20 RING
cell20_out/census.json          census, controls PASS, 8/20 SEAM, 0/20 VIGNETTE
cell20_out/cell20_sheet.png     all 20 at 5x
cell20_out/plate_sheet.png      four representative tiles, laid 2x2
cell20_out/half0.png|half1.png  the 20 at 7x, for the eye read in §6.5

CONTROLS-RESULT.json            23 checks, 17 RED halves, 0 failed
census_controls/                5 planted control tiles + RESULT.json
```

### 7.1 Measured totals, whole session

| | |
|---|---|
| paid generations | **26** of a 40 hard ceiling (6 columns + 20 cell) |
| refused, **not billed** | **4** (1 style probe + 3 item-10) — balance unmoved across all four |
| free calls | **42** `check_cost` + selector + balance reads |
| **total spend** | **$0.650** — $0.150 columns, $0.500 cell |
| balance | $0.412 → topped up → $10.26 → **$9.76** |
| estimate vs actual | **26 of 26 exact** |
| declared vs actual, cell | **$0.500 vs $0.500 — no discrepancy** |
| discrepancies flagged | **1, and it was an instrumentation artefact** (Finding 8), flagged not reconciled, original row retained |

### 7.2 `git diff --stat`

```
 RD_CONVENTIONS.md                                        |  46 ++
 tools/retrodiffusion/NOTICE.md                           |   2 +-
 tools/retrodiffusion/audit_2026_08/AUDIT-RD.md           | rewritten
 tools/retrodiffusion/audit_2026_08/rd.py                 |  14 +-
 tools/retrodiffusion/audit_2026_08/controls.py           |  17 +-
 tools/retrodiffusion/audit_2026_08/run20.py              | 213 +++++
 tools/retrodiffusion/audit_2026_08/prompts/floor_material_rd_v2.json | 116 +++
 tools/retrodiffusion/audit_2026_08/cell20_out/           | 20 tiles + plates + manifests
 tools/retrodiffusion/audit_2026_08/audit_out/            | ledger + sheets + screens
```

Exact figures in the commit; the staged stat is reproduced verbatim there rather than
paraphrased here.

## 8. REFUSALS HONOURED

No file under `tools/tier1_floors/` or `tools/pixellab/probe_6_4/` touched — **BitForge stayed
frozen throughout, and tier one is exactly as it was.** Nothing promoted to reference or corpus
in any state. No constant in `ring_instrument.py` altered — it is shelled out to as a
subprocess, not imported, so a monkeypatch is not possible even by accident, and its own
`--controls` suite ran and passed inside every screening invocation. Nothing bought beyond the
declared generations. The key was never printed, and `_scrub()` guards every ledger row against
a server body that quotes it back.

**No adoption language anywhere in this document**, per the amendment's item 13. Every limb of
the bar is reported as measured or as undecided; none is argued for.
