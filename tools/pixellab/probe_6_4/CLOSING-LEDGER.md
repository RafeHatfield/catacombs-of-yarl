# §6.4 PROBE — CLOSING LEDGER

**Probe CLOSED 2026-08-26. §6.3 RATIFIED at STOP 2** (Rafe, on the reference device).

Every figure below is recomputed from the flushed `ledger.jsonl` files and the images beside
them — not copied from a prior report and not typed from memory. The probe's rule was that
the ledger stores images rather than parameters, because no surface on this platform is
seed-reproducible; a closing account taken any other way would not honour it.

| phase | billed calls | images kept | refused/error |
|---|---:|---:|---:|
| Preconditions A + C (API half) | 2 | 2 | 0 |
| Stage 1 — unconditioned bootstrap, 3 arms x 2 subjects | 120 | 120 | 0 |
| Diagnostic — coverage_percentage | 8 | 8 | 0 |
| Diagnostic — negative_description | 12 | 12 | 0 |
| Wall micro-probe — surface framing, no arms | 20 | 20 | 0 |
| Conditioning smoke test — 2 refs x 6 seeds | 12 | 12 | 0 |
| **probe total** | **174** | **174** | **0** |
| _surface audit (pre-probe, cited not recomputed)_ | _246_ | _27_ | _0_ |
| **GRAND TOTAL** | **420** | **201** | **0** |

⚠ The surface audit's row is **cited from `AUDIT-FINDINGS.md`, not recomputed here.** Its ledger
predates this module and records *claims* rather than billed calls — one claim there can stand
behind eight generations. Counting its rows would understate the spend, and counting its
non-OK verdicts as errors would invent failures that never happened.


## Balance brackets, settled at both ends

AUDIT 8.5: the platform's balance ledger settles late and slowly — two reads 15s apart once
agreed on a figure that was 32% low. Every bracket below required **three consecutive
identical reads** before it was believed.

| phase | pool before | pool after | settled |
|---|---:|---:|:--:|
| Preconditions A + C (API half) | 4124.0 | 4122.0 | yes |
| Stage 1 — unconditioned bootstrap, 3 arms x 2 subjects | 4122.0 | 4002.0 | yes |
| Wall micro-probe — surface framing, no arms | 3982.0 | 3962.0 | yes |
| Conditioning smoke test — 2 refs x 6 seeds | 3962.0 | 3950.0 | yes |

## What the probe spent, and on what

- **Generations billed by the probe proper: 174**, plus **246** for the pre-probe surface audit
  that froze the instrument — **420 total.** Cost was measured settled at **1.00 generation per
  BitForge call** *before* the 120-generation Stage 1 batch was authorised, not reconstructed
  after it.

- **Images retained by the probe proper: 174.** Every generation — accepted, rejected, control, diagnostic — is on
  disk with its full request payload. Nothing was deleted and nothing was curated out of the
  ledger; curation happened downstream, on contact sheets, by Rafe.

- **Refusals/errors: 0.**


## The frozen instrument, recorded

v2 HTTP `POST https://api.pixellab.ai/v2/create-image-bitforge`, every call, every stage.
Chosen on measured evidence, not preference: the only surface where a 32px native canvas and
a shading lever coexist AND the lever is measurable (pixdiff 1.0000 against a measured noise
floor of 0.3542; MCP `pro` and `pixflux` both measure 1.0000 against a 1.0000 noise floor,
which is NO INSTRUMENT).

`client_compat.generate_image_bitforge` was never used and cannot be: it passes `style_image`
through raw kwargs where it dies unserialisable (issue #140). This probe hand-encoded
`Base64Image` throughout.


## What the probe answered, and what it did not

**Answered.** §6.3 is ratified on the device. The canvas holds at 32x32 native at x2 on the
frozen surface. `shading` is measurable on this endpoint and measurably did **not** move the
output in the intended direction. `coverage_percentage` moves pixels above the noise floor and
changes nothing compositional. `negative_description` is not additive. Single-reference
conditioning propagates material DNA in 12 of 12, and propagates composition with it.

**Not answered, and not to be cited as answered.** The three-arm comparison. Stage 1 produced
no arm A — no candidate in any arm depicted a directional key light — so there was nothing for
arms B and C to be compared against. The effort ratio never acquired a denominator and was
never computed. Ruling 47's clause stands: a finding about test conditions, not permission to
pick an arm.

**Reported as a bar cleared by the wrong instrument.** The wall micro-probe's declared bar was
>=5 usable-as-wall in 20 and it returned 20/20 on framing — and all 20 are undifferentiated
noise. The bar was not re-tuned after the answer was visible (LOOP-PROCESS §8). It was drawn
badly, and that is recorded rather than corrected in hindsight.

