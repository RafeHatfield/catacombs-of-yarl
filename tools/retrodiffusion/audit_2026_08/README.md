# Retro Diffusion — adoption audit, 2026-08

**This is an audit, not an integration.** Nothing here is adopted, nothing is promoted to
reference or corpus, and tier one stays frozen on BitForge to completion regardless of what
these numbers say. Adoption is Rafe's ruling and it is taken *after* the tier-one floor gate,
never before.

The bar RD has to clear was written before the first call and is in
[`AUDIT-RD.md`](AUDIT-RD.md).

---

## The credential

```bash
export RD_API_KEY="rdpk-..."      # the API key, from retrodiffusion.ai
```

| | |
|---|---|
| **Environment variable** | `RD_API_KEY` |
| **Where it must never go** | git, logs, reports, the ledger, a terminal |
| **Preflight** | every script calls `rd.preflight()` before doing anything |

`RD_API_KEY` is the name `../RD_CONVENTIONS.md` established and the name the retired track's
scripts already read. One name for one secret rather than a second one to leak.

**Preflight fails loudly and early**, before any plan is printed and long before any call:

```
STOP — no Retro Diffusion credential.
  Set RD_API_KEY in the environment before running anything in this directory.
  The key is never committed, never printed, and never written to the ledger.
```

It also refuses a credential of the **wrong shape** — RD keys begin `rdpk-`, and a key that
does not is most likely another vendor's, which this code will not send to RD's endpoint:

```
STOP — RD_API_KEY is set but is not a Retro Diffusion key (len=34 prefix_ok=False).
  Vendor keys begin 'rdpk-'. Refusing to send a credential to an endpoint it does not
  belong to.
```

Both messages report the key's **shape**, never its value. `rd._scrub()` walks every ledger row
before it is written and replaces any occurrence of the credential with `<redacted>` — belt and
braces against a server error body that quotes the token back, which is the only realistic path
by which it could reach disk. Control 4 in `controls.py` plants exactly that and proves it.

## The surface

API / website only: **`https://api.retrodiffusion.ai/v1`**, header `X-RD-Token`.

- The **Aseprite extension is a different product with different models** and is out of scope.
  Nothing here buys, installs, or calls it.
- The **MCP server** at `mcp.retrodiffusion.ai` is also not used. It is a second surface with
  its own tool shapes, and an audit that cannot say which surface produced a number has
  measured nothing.

## Money

| guard | where | what it does |
|---|---|---|
| Hard ceiling | `rd.SESSION_CEILING = 40` | **40 paid generations**, in code. `Budget` refuses call N+1 *before the network*, so an over-budget call is never billed. A ceiling above 40 cannot be constructed. |
| Free dry run | `rd.check_cost()` | `check_cost: true` prices the exact payload and generates nothing. Run before **every** paid call. |
| Estimate vs actual | `rd.generate()` | Both recorded per call. A divergence is written to the ledger as a finding, not smoothed over. |
| Balance bracket | `rd.Session` | Credits read before and after, and **reconciled**: the pool delta is compared against the sum of billed costs and goes `RECONCILE_RED` on disagreement. The gauntlet's unbracketed-balance defect does not get a third life. |

Free calls do not count against the ceiling, and that is deliberate — the whole point of a free
dry run is that it is free. Columns 1, 6, 7 and half of 2 and 8 are answerable with `check_cost`
alone, so they cost nothing.

## Layout

```
rd.py            the client: preflight, check_cost, balance bracket, ledger, ceiling
controls.py      POSITIVE CONTROLS for every guard in rd.py — run this first
prompts/
  floor_material_rd.json   the subject, with clause provenance and its translation losses
audit.py         the columns — one real call per claim
yield_run.py     24 generations, two cells of twelve
census.py        the seamless census, with its own control suite
screen.py        ring + census over every child, and the arithmetic vs the baseline
AUDIT-RD.md      the bar, declared first; then the findings
```

## Order of operations

```bash
python3 controls.py                       # free. every guard demonstrates it can fail
python3 census.py --controls              # free. the census demonstrates it can fail
python3 audit.py --free                   # free. style list + canvas sweep + capability probes
python3 audit.py --paid --style <id>      # ~5 generations
python3 yield_run.py --style <id>         # 24 generations
python3 screen.py                         # free. ring + census + Fisher vs baseline
```

`--dry-run` on `yield_run.py` prints the whole plan and spends nothing.

## Refusals

Does not touch tier one's session, corpus, or surface freeze. Does not promote any RD output to
reference or corpus, in any state. Does not spend past the ceiling. Does not print the key
anywhere. Does not buy anything.

## What is *not* here, and why

`tools/retrodiffusion/` — the parent directory — is **not** the empty stub this session's brief
assumed. It is a complete legacy integration from the **retired Oryx-conformance track**. See
[`../NOTICE.md`](../NOTICE.md). It is read as evidence about the surface and is not extended:
its palette, style ruling, sprite-id namespaces and prompt template all answer to a corpus that
is no longer the target, and it has no ledger, no dry run, no bracket and no ceiling.
