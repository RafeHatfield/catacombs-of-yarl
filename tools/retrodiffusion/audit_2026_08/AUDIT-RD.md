# RETRO DIFFUSION — connection and adoption audit

**CONNECTED. Eight columns measured. Six paid generations, $0.150 spent, 34 free dry runs.**
Nothing landed, nothing was promoted, no corpus file changed, no constant in any pre-existing
instrument was altered, and **tier one is untouched and stays frozen on BitForge to completion
regardless of anything in this document.**

**Ruling triggers: §1.1.4(b) — an amendment to a declared design; and §1.1.4(e) — budget
exhausted below bar.** Both are named in §6 with the decision each needs. The yield run has NOT
been spent, for two reasons that both arrived from measurement rather than from caution.

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

And the finding that stopped the batch:

4. **The ring was the STYLE, not the surface.** Every tile from `rd_plus__low_res` came back
   with a dark frame around the canvas and a regular 3×3 lattice inside it — §12.1's keyline and
   §8.3.1's lattice, together, in one image. Switching to `rd_tile__single_tile` at the **same
   price** produced a full-bleed, unframed, instrument-CLEAN field on the first call.

**Limb 3 of the adoption bar is now decided, and it is decided against RD** (§0.2).

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

---

## 1. THE COLUMNS — measured

One real call per claim. **34 of the 41 calls were free**: `check_cost: true` prices a payload
without generating, and the `/styles/selector` endpoint returns per-style canvas limits, so
column 1 and most of column 2 cost nothing at all.

| # | column | verdict |
|---|---|---|
| 1 | **exact canvas at 32×32** | ✅ **NATIVE.** Requested 32×32 → returned 32×32, `upscale_output_factor: 1`. `rd_plus__low_res`, `rd_fast__low_res`, `rd_mini__low_res` all accept **16–128**; `rd_tile__single_tile` 16–64; `rd_tile__tileset` 16–32; every `rd_pro__*` 12–256. **32×32 is comfortably inside the cheap tier.** |
| 2 | **reference / palette** | ✅ **PALETTE LOCK IS REAL — 8-colour ramp in, 5 distinct colours out.** Not accepted-and-ignored; measured on the returned pixels. `reference_images` (style conditioning) is **RD Pro only** per the selector's `supports_reference_images` flag, i.e. **$0.18/image**. |
| 3 | **seed determinism** | ✅ **REPRODUCIBLE.** Assume-none, confirmed otherwise: 2 calls, identical seed, **1 distinct sha256 of 2**, byte-identical. Two calls can disprove and cannot prove in general, so this is evidence, not a guarantee — and the ledger keeps storing images regardless. |
| 4 | **latency & cost** | ✅ **11.4 s mean** (9.2–15.6 s), one image per call, $0.025 at 32×32. `num_images: 4` prices at $0.098 — a batch discount of 2%, i.e. none. |
| 5 | **estimated vs actual** | ✅ **6 of 6 EXACT.** Every paid call was preceded by its own free dry run; `estimate_divergence` 0.0 on all six. **No divergence finding.** |
| 6 | **the balance ledger** | ✅ **`balance` is the spendable field; `credits` is inert.** `{"balance": 0.412, "credits": 50}` → six generations moved `balance` to `0.262` (exactly 6 × $0.025) and left `credits` pinned at 50.0. **It settles instantly** — no lag, unlike PixelLab's, which settled late enough that two reads 15 s apart agreed on a figure 32% low. |
| 7 | **the seamless flag** | ⚠️ **EXISTS, PARTIALLY UNUSABLE.** `tile_x`/`tile_y` are accepted on `rd_plus__low_res`. On `rd_tile__single_tile` — the only style that produced an unframed tile — the same flags return **HTTP 400 `inference_failed`**. See Finding 3. |
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

- **Not a ring rate.** Six generations is not a rate and no percentage is computed from them.
  The 24-generation yield run has not been spent.
- **Not that `rd_tile__single_tile` is good.** One tile, correct composition, **wrong material** —
  gravel, not flagstones. It cleared a mechanical screen; no seat has seen it and no human gate
  has been near it.
- **Not that seed reproducibility generalises.** Two calls, one style, one seed. It disproves
  "assume none"; it does not prove determinism across styles, sizes, or time.
- **Not that the palette lock is register-correct.** 5 colours from an 8-colour ramp proves the
  **mechanism**. §5.1's actual values are PLACEHOLDER, so there is no bible palette to lock to
  yet.
- **Not that limbs 1 or 2 are decided.** Only limb 3 is, and against RD.
- **Not that `bypass_prompt_expansion` works.** Accepted is not honoured.

---

## 6. TWO DECISIONS, AND THEY ARE RAFE'S

### Decision 1 — money. §1.1.4(e), budget exhausted below bar.

**Balance is $0.262. The declared 24-generation yield run costs $0.600.** The 40-generation
ceiling was never the binding constraint; the prepaid balance is.

| option | cost | what it buys |
|---|---|---|
| **A — top up (recommended)** | ~$5 | Runs the declared width many times over. A $1 top-up alone clears it. |
| **B — run 10 now** | $0.250 | One cell of 10 against a baseline of 20. Usable only for a large effect; halves the power on the one number the bar turns on. |
| **C — run 15 at `rd_fast__low_res`** | $0.255 | More width, but a **different and cheaper model** than the one under test. Understates RD. |

### Decision 2 — design. §1.1.4(b), an amendment to a declared design.

Finding 3 killed the declared N/T cells: `tile_x`/`tile_y` refuse on the only style that
produces unframed tiles. The replacement I would run:

> **A single cell of 20 on `rd_tile__single_tile`, no tiling flags — $0.500 — matching the
> baseline's n=20 exactly**, with the prompt reworked toward §8.3.1's mirror (the material needs
> bond and joints; the composition is already right).
>
> The seamless flag is **dropped from the design and reported as a finding instead**: it is
> unusable on the only style worth running, and per Finding 4 a flag that can be satisfied by
> framing the tile was never going to settle limb 2 on its own anyway.

**Limb 2 then rests on the census measuring `rd_tile__single_tile`'s natural wrap**, which is the
honest test — does the material lay seamlessly because it *is* seamless, rather than because it
is fenced.

---

## 7. EVIDENCE

```
audit_out/audit_ledger.jsonl   41 rows: 34 free check_cost, 7 generate (6 OK, 1 refused)
audit_out/col1|col2|col3/      the four audit tiles
audit_out/probe_style/         the two style-probe tiles
audit_out/col_sheet.png        contact sheet, 8x
audit_out/probe_sheet.png      contact sheet, 8x
audit_out/ring_paid.json       ring instrument, controls PASS, per-tile verdicts
audit_out/census_paid.json     census, per-tile verdicts + 2x2 plates
audit_out/plates/              every tile laid 2x2 at 4x
CONTROLS-RESULT.json           23 checks, 0 failed
census_controls/               5 planted control tiles + RESULT.json
```

**Spend: $0.150 of a $0.412 balance. 6 paid generations of a 40 ceiling. 34 free calls.
Estimate matched actual 6/6. Balance reconciles exactly.**

## 8. REFUSALS HONOURED

No file under `tools/tier1_floors/` or `tools/pixellab/probe_6_4/` touched. Nothing promoted to
reference or corpus in any state. No constant in `ring_instrument.py` altered — it is shelled
out to, not imported. Nothing bought. The key was never printed, and `_scrub()` guards every
ledger row against a server body that quotes it back.
