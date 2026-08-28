# ⚠️ This directory is retired Oryx-track material — 2026-08-27

**Everything in this directory except [`audit_2026_08/`](audit_2026_08/) was written for the
Oryx-conformance art track, which closed on 2026-08-24.** The scripts still run. Nothing they
produce is usable, and no threshold in them is a bar.

Same shape as [`tools/art_lint/NOTICE.md`](../art_lint/NOTICE.md), and for the same reason: the
code was retained, the **bar** it answered to was retired, and a retained tool with no live spec
is a trap for the next session unless it says so on the tin.

## What is retired here

| file / thing | why it is retired |
|---|---|
| `oryx_palette.png`, `oryx_style_reference.png`, `extract_palette.py`, `create_oryx_style.py` | Built from the Oryx master palette. `ART-BIBLE-v0.md` §5.1 specifies a successor palette whose **values are PLACEHOLDER**. There is currently no palette to lock to, and locking to this one is working to a closed track. |
| `../RD_CONVENTIONS.md`'s style ruling | `rd_plus__low_res` was chosen because it "produces the closest match to Oryx library aesthetics". That criterion no longer exists. **AND IT IS THE WRONG STYLE FOR TILES — MEASURED 2026-08-28:** every floor generation from it came back with a dark frame around the canvas and a regular grid inside it (§12.1 keyline + §8.3.1 lattice). `rd_tile__single_tile`, at the identical $0.025, produced a full-bleed unframed field on the first call. See `audit_2026_08/AUDIT-RD.md` Finding 1. |
| The sprite-id namespaces (4001–4999, 5001–5999, 6001+) | Allocated against the Oryx tilesets. |
| The standard prompt template and its notes | Tuned for 16×16/24×24 Oryx-matched props. Tier one authors at **32×32** (RULED, 2026-08-25). |
| `batch_generate.py`, `style_test_prop.py`, `img2img_test_bed*.py`, `oblique_test_bed.py`, `perspective_test_bed.py` | All hard-code the above. None has a ledger, a cost dry run, a balance bracket, or a budget ceiling; `batch_generate.py` gates spending on an interactive `input()` prompt and estimates cost from a hard-coded `$0.18`. |
| Every `batch_*/`, `style_test*/`, `*_test_bed*/` output directory | Candidates generated to the retired bar. Kept as ledger, promoted to nothing. |

## What is still true and worth keeping

These are facts about the **surface**, not about the retired corpus, and the 2026-08 audit reads
them as evidence rather than re-buying them:

- The v1 REST endpoint, `POST https://api.retrodiffusion.ai/v1/inferences`, header `X-RD-Token`.
- The credential lives in **`RD_API_KEY`**. One name for one secret.
- The response carries `balance_cost` and `remaining_balance` — so the surface supports a
  balance bracket natively. *(⚠ `docs/archive/oryx-track/RETRO_DIFFUSION_WALKTHROUGH.md` names
  these `credit_cost` and `remaining_credits` instead. The repo disagrees with itself; the audit
  reads both fields and records which one is live.)*
- `remove_bg`, `input_palette`, `input_image` + `input_image_strength` were all exercised
  against real calls and worked.

## What replaces it

[`audit_2026_08/`](audit_2026_08/) — a fresh client with a hard budget ceiling, a free cost dry
run before every paid call, a bracketed and *reconciled* balance, a ledger that stores images
with full redacted payloads, and a positive-control suite proving every one of those guards can
go red. It is an **audit**, not an adoption: RD is not in the pipeline, and tier one is frozen
on BitForge.

**Do not delete this directory** — it is the ledger of what the retired track spent — and do not
extend it. New RD work goes in `audit_2026_08/`.
