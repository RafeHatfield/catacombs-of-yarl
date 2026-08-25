# PIXELLAB — YARL USAGE AUDIT

**Read-only audit, 2026-08-25.** No call was made to the PixelLab API and nothing in
`tools/pixellab/` was changed. Findings only; the remediation list at §17 is
unactioned.

Audited against `docs/PIXELLAB-VERIFIED.md` (Gemfall, commit `874b5459`).
Confidence tags follow that document's scheme. **[API]** appears nowhere below — I made
no calls. Everything here is **[TREE]** (our own evidence, cited to file and line),
**[SCHEMA]**, or **[INFER]**, and is tagged accordingly.

---

## 0 — THE HEADLINE

**YARL and Gemfall are not on the same PixelLab surface.** Four of the seven "facts that
bite" describe machinery YARL has never touched. Three transfer intact, and two of those
three are already realised as live defects: a refusal reason is permanently lost, and
2,300+ generations were spent against a shared subscription with **zero** balance
checkpoints.

The architecture decision in §2.4 — the one the transfer brief calls most important — is
the real finding. **YARL needs identity-preserving variants, has already hand-rolled them
twice on the wrong surface, and never recorded whether either attempt worked.**

---

## 1 — [TREE] SURFACE MISMATCH — the finding that reframes the other six

YARL is on the PixelLab **v1 REST surface** only:

| YARL calls | via |
|---|---|
| `/generate-image-bitforge` | `client_compat.py:47`, and `pixellab` SDK at 8 sites |
| `/inpaint` | `client_compat.py:67`, `regen_chests_variants.py:65,85` |
| `/animate-with-text` | `regen_chests_variants.py:114` |
| `/balance` | `client_compat.py:75` (one call site — see §7) |

`PIXELLAB-VERIFIED.md` describes the **MCP / object surface**: `create_1_direction_object`,
`create_object_state`, `create_character`, `select_object_frames`, review objects,
promotion, `get_object` download URLs.

**Evidence.** A grep for every MCP tool name across `tools/pixellab/*.py` returns exactly
two hits, both for `get_balance` — no hit for any object, character, or selection endpoint.
`~/.claude.json` registers the `pixellab` MCP server under
`/Users/rafehatfield/development/deathmatch` **only**; the `c-yarl` project entry has
`mcpServers: []`. A YARL session cannot reach the MCP surface today.

**This was already known and consciously deferred.**
`tools/pixellab/PIXELLAB_V2_MCP_FINDINGS.md` (2026-07-24) found the v2 surface, listed
`/objects/{id}/select-frames`, `/create-1-direction-object` and
`CreateCharacterStateRequest.use_color_palette_from_reference`, noted the MCP server was
registered to the other project, and closed with *"Not acted on … a discovery note, not a
recommendation to migrate."* Gemfall then went and paid the tuition on that surface.

**Consequence for the transfer brief:**

| brief fact | status in YARL |
|---|---|
| 1 — `create_character` entry decision | **Not yet made on the right surface** — see §10. Live and load-bearing. |
| 2 — 2000-char cap on `create_1_direction_object` | N/A to v1. Analogue measured at §9. |
| 3 — per-endpoint floors | N/A as stated. YARL has its own unmeasured floor claim — §11. |
| 4 — `select_object_frames` hygiene | N/A. YARL contributes zero review objects — §2. |
| 5 — budget at the ceiling, `get_balance` ground truth | **Transfers. Violated** — §7, §8. |
| 6 — classify refusals at the moment they happen | **Transfers. Violated, and already cost one** — §6. |
| 7 — record IDs at queue time | Transfers in v1 shape. Partially violated — §5. |

---

## 2 — [TREE] Stuck review objects: YARL contributes zero

No object-surface call site exists and no MCP access exists (§1). YARL cannot have created
a review object. The 87 review / 12 completed on the shared account are Gemfall's.

⚠ **This is [TREE], not [API].** I did not call `list_objects` to confirm from the account
side. That call needs your go-ahead; it is read-only and, on the MCP surface, would need
the server registered here first.

---

## 3 — [TREE] Cached CDN URLs: zero exposure

v1 returns the image **inline as base64** — `client_compat._decode()` reads
`resp_json["image"]["base64"]`. YARL never receives a download URL, so it cannot cache one.
A repo-wide grep for `pixellab.ai`, `cdn`, `storage.googleapis`, `amazonaws` across
`*.py *.md *.json *.yaml *.cs` returns **9 hits, all documentation references to
`openapi.json` or the sign-up page — zero asset URLs**.

§2.7's browser-User-Agent CDN dependency does not apply to YARL either.

---

## 4 — [TREE] Seed posture: YARL is in better shape than Gemfall

Every v1 endpoint YARL uses carries `seed`, and **every call site passes one**. Measured
across the tracked ledgers:

| ledger | rows | seedless |
|---|---|---|
| `candidates/bank/*/index.csv` | 1174 | **0** |
| `candidates/bank_palette_locked/*/index.csv` | 854 | **0** |
| `reports/burndown2b_generation_log.csv` | 211 | 1 — *and it is the error row*, §6 |
| `reports/burndown3_generation_log.csv` | 44 | 0 |
| `reports/remediation_generation_log.csv` | 12 | 0 |

Filenames encode the seed (`<concept>_s<N>.png`) on **100%** of burndown2b (644 files) and
gauntlet (214 files) candidates.

Brief fact 2's second clause — *"the ONLY generation endpoint with no seed; arms on it are
irreproducible by construction"* — is a Gemfall problem, not a YARL one.

⚠ **Seed is necessary, not sufficient.** `gauntlet.py:70` composes the prompt at runtime
(`prompt` + `REGISTER` + a front-facing suffix + `", small sprite, pixel art"`) and its
`_critic_log.csv` has **no prompt column**. Those 68 generations are reproducible only by
re-reading the script at the right commit. Same for `chair_reroll` (§5).

---

## 5 — [TREE] LEDGER GAPS: 8 generations recorded nowhere, 68 with no prompt

Reconciliation, disk against ledger. One `*_raw32.png` = one generation.

| lane | generations on disk | ledgered | verdict |
|---|---|---|---|
| `bank` | 1174 | 1174 | ✅ exact |
| `bank_palette_locked` | 854 | 854 | ✅ exact |
| `burndown2b` | 210 | 210 ok + 1 error | ✅ exact |
| `burndown3` | 64 | 44 here + 12 in `remediation_generation_log.csv` | ⚠ **8 short** |
| `gauntlet` | 68 | 68 | ✅ count exact, **no prompt column** |
| `remediation_review` | 4 | — | composite sheets, not generations |
| `worn_variants` | 2 | 0 | ⚠ **no seed in filename, no ledger, provenance unknown** |

**The 8:** `chair_route_b`. `chair_reroll.route_b()` calls
`generate_candidates_locked.generate_concept_locked`, which writes only
`_swatch_colors.txt` — no CSV row, in any file. Eight generations exist on disk with no
prompt, no status and no lint verdict recorded anywhere.

The two bank ledgers reconcile perfectly and are the model to copy: `bank_generate.py:435`
writes and `f.flush()`es **one row per candidate, immediately**.

---

## 6 — [TREE] ⚠ REFUSAL REASONS ARE DISCARDED TWICE — and one is already gone

Brief fact 6, reproduced in YARL. Three independent losses on one path:

1. **`client_compat.py:49, 68, 76` — `r.raise_for_status()`.** `requests` raises
   `HTTPError` reading
   `"400 Client Error: Bad Request for url: https://api.pixellab.ai/v1/generate-image-bitforge"`.
   **`r.text` — where the server's reason lives — is never read.** Every refusal,
   over-length and content-policy rejection reaches YARL as a status line with the reason
   already stripped.
2. **`gauntlet.py:88` — `str(e)[:80]`.** Even the status line does not survive: the URL
   alone is 55 characters.
3. **`bank_generate.py:413`** prints the exception to stderr and `continue`s — **no ledger
   row is written for a failure at all.** The CSV cannot represent a failed generation.

**Already realised.** `burndown2b_generation_log.csv` contains exactly one non-ok row:

```
concept=shelf_bottles  tag=shelf_bottles_s3  status=error
```

Every other field — prompt, seed, overall, colors, A5, A6, final_path — is **empty**. There
is no message. The classification (`content_policy` / `over_length` / `invalid_input`) is
permanently unrecoverable, exactly as §1.7 predicts. We do not know why that call failed
and we cannot find out.

---

## 7 — [TREE] ⚠ NO BALANCE BRACKETING. 2,300+ generations, zero ground-truth checkpoints

`get_balance()` is defined at `client_compat.py:73` and has **one** call site in the entire
repo: `sweep.py:28`, an April-era exploratory script. **No generation tool calls it.**

- No balance value is recorded in any file in the repo.
- No record exists of which billing regime any YARL batch ran under (§5 of the brief:
  pool-metered vs dollar-metered).
- The subscription is **shared with Gemfall**. YARL's spend is unattributable after the
  fact, in both directions.

⚠ **The hazard was noticed at the time and not instrumented.**
`reports/burndown2b_summary.md:58` records a concurrent batch in `yarl-bank` on the *same*
`PIXELLAB_API_TOKEN`; `bank_generate.py:442` carries a `time.sleep(0.4)` *"courtesy delay —
burn-down 2b shares this API token/machine and has priority."* Sharing was understood well
enough to yield politely to it, and never well enough to measure it.

---

## 8 — [TREE/INFER] Budget planning counts files, not charges

`bank_generate.py` decrements `max_remaining` **only after a successful save** (l.439), and
seeds the run's budget as `args.max_total - <PNGs already on disk>` (l.480). It budgets
artefacts, not charges.

That is compatible with §1.4 (a rejected call is free) for the rejection case. It is wrong
for a call that is **charged and then fails downstream** — in `run_pipeline`'s clean, snap
or save steps — which spends quota invisibly.

⚠ **Brief fact 5's ceiling-vs-floor rule has no measured v1 analogue.** Nobody has measured
whether v1 BitForge charges per call, per image, or by canvas tier. Treating v1 as "one
call, one generation" is **[INFER]** and is load-bearing for every `--max-total` we have
ever passed.

---

## 9 — [TREE] Prompt-cap exposure: measured at ~6% of the cap, and unguarded

Longest prompt actually sent, across all 2,251 ledgered rows:

| ledger | max prompt chars |
|---|---|
| `remediation_generation_log.csv` | **117** |
| `bank/*` and `bank_palette_locked/*` | 89 |
| `burndown3_generation_log.csv` | 85 |
| `burndown2b_generation_log.csv` | 58 |

Against a 2000-char cap that is **no exposure whatsoever**. The template is deliberately
short — `PIXELLAB_CONVENTIONS.md`: *"`{object}, small sprite, pixel art`. That's the full
template. Keep it short."*

Two caveats worth carrying anyway:

- **No boundary check exists** at any call site. Gemfall's `pixellab_pack.py check` refuses
  and never trims; YARL has no equivalent.
- The register ruling now mandates appending ~120 chars (`"chunky, minimal detail, bold
  shapes, thick outline"` + the two-plane rule) to every register-critical prompt. Headroom
  is still enormous — this is a watch item, not a risk.
- ⚠ **v1 BitForge's own cap is unmeasured. [INFER]** that it is 2000. §2.1's whole lesson is
  that the cap is undeclared precisely where it is enforced.

---

## 10 — [TREE] ⚠ THE ARCHITECTURE DECISION — YARL made it by accident and hand-rolled around it

The brief's most-important transfer: *"if you want identity-preserving variants later,
enter through `create_character`, not `create_*_object`. That decision is made at your first
call and is expensive to reverse."*

**YARL's first call was v1 BitForge, in April. YARL does want identity-preserving variants,
and has already built two approximations of them by hand.**

`regen_chests_variants.py`, verbatim from its own docstring:

> **STRATEGY 1: Inpaint with surgical mask (lid area only)** — *"Pixels outside mask are
> preserved exactly → structurally identical chest body"*
> **STRATEGY 2: `animate_with_text` with `reference_image`** — *"Uses the proper
> identity-anchor mechanism designed for consistent frames"*

That is chest closed / open / empty / trapped: one object, four states, identity preserved.
It is §2.4's problem, solved by hand on a surface that offers no identity contract.

Corroborating pressure, all already in the repo:

- `PIXELLAB_CONVENTIONS.md` reserves the `creatures_24x24` namespace at **6001+**,
  *"untested, not yet in use."*
- `PIXELLAB_V2_MCP_FINDINGS.md` flagged `use_color_palette_from_reference` as *"relevant if
  we ever do player-class or creature variant work through PixelLab rather than by hand."*
- Visible corpses shipped (PR #110). A corpse is a wounded/dead **state of a creature** —
  the exact case `create_character_state` names.

⚠ **And neither hand-rolled strategy has a recorded verdict.** `regen_chests_variants.py`
writes PNGs to `batch_new_sprites_results/` — which `tools/pixellab/.gitignore` excludes
(`*_results/`). No ledger row, no lint result, no gate outcome for either strategy exists in
the repo. **We do not know whether masked-inpaint or `animate_with_text` preserved identity
well enough**, and the outputs are not in version control.

**This is the decision to take before any further generation work**, and it is genuinely
expensive to reverse. It is not urgent for props — props have no identity to preserve. It is
urgent the moment creature, corpse, or state art starts.

---

## 11 — [TREE→INFER] A floor claim nobody measured

`regen_chests_variants.py:29`:

```python
hero_64 = hero_32.resize((64, 64), Image.NEAREST)
# Upscale to 64x64 for inpaint (clean ratio, avoids min-area issues)
```

**"avoids min-area issues" is untagged folklore.** Nobody measured v1 `/inpaint`'s floor.
Gemfall measured that the MCP editing family is *not* uniformly floored (§1.2 vs §1.1) —
generalising a floor across a family is precisely what the brief warns against.

Everything else in YARL generates at 32×32 and downscales locally with PIL, so no other call
approaches a floor. This one working assumption is the only exposure — and the probe is
**refusal-shaped, therefore free** under §1.4 / Law 4. It should be measured, not reasoned
about.

---

## 12 — [TREE] Ledger durability is inconsistent across three tools

| tool | write pattern | failure mode |
|---|---|---|
| `bank_generate.py:435` | one row per candidate, `f.flush()` immediately | ✅ crash-safe |
| `run_batch.py:59` / `run_locked.py:49` / `remediation_round.py:50` | `append_log(...)` called **once, after the whole concept run returns** | a kill mid-concept loses **every** row for that concept |
| `gauntlet.py:94` | written after the loop, **mode `"w"`** | a kill loses everything; a re-run **overwrites** the prior record |

`bank_generate.py`'s docstring advertises *"Safe to interrupt (Ctrl-C or backgrounded
process kill) and re-run"* — true for that tool, and not true for the other four, which make
the same class of run.

---

## 13 — [TREE] Latent defect: the API key env var is split two ways

- `client_compat.py:18` — `os.environ["PIXELLAB_API_TOKEN"]`
- Seven scripts (`table_test`, `batch_replace`, `regen_chests_variants`, `consistency_test`,
  `regen_puddle`, `regen_chests`, `sweep`) — `os.environ["PIXELLAB_API_KEY"]`
- `PIXELLAB_CONVENTIONS.md:15` and the entire `PIXELLAB_SETUP_WALKTHROUGH.md` document
  **KEY**.
- `bank_generate.check_api_key()` (l.326) passes if **either** is set — then calls
  `client_compat`.

So a shell configured exactly as our own docs instruct clears `bank_generate`'s guard and
dies on the first generation with `KeyError: 'PIXELLAB_API_TOKEN'`. Noisy, not silent, so
it costs minutes rather than money — but the documented setup is insufficient for the
primary tool.

---

## 14 — [TREE] SILENT-STEP AUDIT (Ruling 104) applied to YARL

*A documented step with no enforcement is not a step. It is a wish.* Three wishes in
`PIXELLAB_CONVENTIONS.md`:

1. **"Register all keepers in sprite browser and props.yaml."** Nothing goes red if a landed
   sprite is absent from `config/props.yaml` or `tools/sprite_browser_ai.html`.
2. **The register prompt fragment is MUST-carry** for register-critical props — *"Every
   generation prompt … MUST carry `chunky, minimal detail, bold shapes, thick outline`"* plus
   the two-plane rule. **Nothing checks that a prompt carried it.** `gauntlet.py:69` appends
   `REGISTER` in code; `run_batch.py`'s `CONCEPTS` prompts (`"ornate iron candelabra with lit
   candles"`, `"large loose boulder rock"`, …) do **not** — and the ledger stores the prompt,
   so this one is checkable from data we already have.
3. **"Keep a record of which seeds are in use per object."** §5 shows the record is partial —
   8 generations have no row and 68 have no prompt.

Each fails Ruling 104's test: nothing reds when the step is skipped.

---

## 15 — [TREE] On porting `tools/pixellab_pack.py`

Gemfall's `pixellab_pack.py` is the right *shape* and the wrong *surface*. Its substance —
packs, frame selection, promotion, the host-independent
`/mcp/objects/{id}/download` endpoint, the browser-UA CDN workaround — is MCP-specific and
has no v1 counterpart. A literal port would import machinery YARL cannot call.

What transfers is the pattern, and YARL needs it: **one integration surface**. Today there
are three client constructions — the SDK directly (7 scripts), `client_compat`'s raw HTTP
(`bank_generate`, and 2 of the 3 endpoints), and `sweep.py`'s own — plus five ledger
formats. Rafe's standing preference for one implementation pattern across both games is
served by a v1-shaped `pixellab_pack.py` with the same *contract*: refuse-don't-trim at the
boundary, verbatim error capture, `get_balance` brackets, queue-time ledger rows, and an
`audit` subcommand that reds on a lane with no record.

---

## 16 — WHAT THE BRIEF GOT RIGHT ABOUT YARL, AND WHAT IT DIDN'T

**Right, and confirmed live:** refusal reasons discarded (§6, already cost one); no balance
ground truth against a shared pool (§7); the identity-variant architecture decision is real,
unmade, and load-bearing (§10).

**Doesn't apply as stated:** stuck review objects (§2 — zero), cached CDN URLs (§3 — zero),
the 2000-char cap (§9 — measured at 117 max), seed irreproducibility (§4 — YARL is clean),
per-endpoint floors as described (§11 — one unmeasured claim, different endpoint).

**The brief's own Law 2 applies to the brief.** *Cite the endpoint's own live schema — never
a neighbour's, never a prior report.* `PIXELLAB-VERIFIED.md` is a prior report about a
neighbouring surface. Nothing in it should be treated as settled for v1 without measuring
v1.

---

## 17 — REMEDIATION LIST

> **STATUS 2026-08-25, after the platform audit.** Items 2, 3 and 7 are **done** on this
> branch — see `docs/PIXELLAB-INTEGRATION-AUDIT-2026-08-25.md` §6. Items 5 and 8 are
> **superseded**: they repair the v1 script fleet, which the platform audit recommends
> retiring rather than fixing. Items 1, 4 and 6 remain open, and item 1's framing is
> corrected there — the identity guarantee it rests on is not in the REST spec.

Ordered by cost of *not* doing it.

1. **§10 — take the architecture decision.** Does YARL need identity-preserving creature /
   state variants? If yes, the entry point is `create_character` on the MCP surface, and the
   MCP server needs registering here. Everything else on this list is cheaper afterwards.
2. **§6 — capture `r.text` before `raise_for_status()`**, classify, and write a ledger row on
   failure. Three-line change in `client_compat.py`; removes a permanent-loss class.
3. **§7 — bracket every batch with `get_balance` and record both readings and the regime.**
   Cheap, and the only thing that makes shared-pool spend attributable.
4. **§11 — measure the v1 `/inpaint` floor.** Refusal-shaped, therefore free.
5. **§5, §12 — one flush-per-row ledger format**, and rows for `chair_route_b` and
   `worn_variants` reconstructed where possible.
6. **§14.2 — a check that reds when a register-critical prompt lacks the mandated fragment.**
   The ledger already stores prompts; this is a script over existing data.
7. **§13 — settle on one env var name** and fix the docs.
8. **§15 — one integration surface**, once 2–5 have decided what it must carry.

⚠ **Per `ART-LOOP-PROCESS-v0.md` §4 and bible §13.5, any check built for items 6 or 8 must
demonstrate it can fail before its passes count.**
