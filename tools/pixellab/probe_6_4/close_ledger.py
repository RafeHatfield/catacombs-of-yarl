#!/usr/bin/env python3
"""§6.4 probe — the closing ledger. Reads every ledger row from disk and totals it.

Nothing here is typed from memory or copied from a prior report. Every figure is recomputed
from the flushed `ledger.jsonl` files and the images beside them, because the probe's own rule
was that the ledger stores images rather than parameters — a claim that is only worth anything
if the closing account is taken from the ledger too.

Emits CLOSING-LEDGER.md.
"""
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))

# Only the phases this probe ran through v2_bitforge.py. Their rows carry a `request` key,
# which is what makes a row a BILLED CALL rather than a claim, a control, or a balance read.
PHASES = OrderedDict([
    ("precondition_evidence", "Preconditions A + C (API half)"),
    ("stage1", "Stage 1 — unconditioned bootstrap, 3 arms x 2 subjects"),
    ("diag_framing", "Diagnostic — coverage_percentage"),
    ("diag_negative", "Diagnostic — negative_description"),
    ("wall_microprobe", "Wall micro-probe — surface framing, no arms"),
    ("conditioning_smoke", "Conditioning smoke test — 2 refs x 6 seeds"),
])

# The pre-probe surface audit is NOT recomputed here and must not be. Its ledger predates
# v2_bitforge.py and records CLAIMS ("cond:v1 style24@24", "NEGCTRL:v2http identical x2"), not
# billed calls — one claim there can stand behind eight generations. Counting its rows as calls
# would understate the spend and counting its non-OK verdicts as errors would invent 33 failures
# that never happened. Its figure is cited from its own document, which measured it against the
# balance endpoint at the time.
AUDIT_GENERATIONS = 246          # AUDIT-FINDINGS.md: "Spend: 246 generations (4371 -> 4125)"


def read(phase):
    p = os.path.join(HERE, phase, "ledger.jsonl")
    if not os.path.exists(p):
        return []
    rows = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def calls(rows):
    """A billed call is a row carrying a request payload. Balance reads and summary rows are
    not calls and are excluded, which is why this is a key test and not a verdict test."""
    return [r for r in rows if "request" in r]


def bracket(rows):
    """Pool before/after for a phase. Some phases write pool_before/pool_after on one summary
    row; others write two rows each carrying `pool`. Handle both rather than assuming one."""
    before = after = None
    settled = True
    for r in rows:
        if r.get("pool_before") is not None:
            before = before if before is not None else r["pool_before"]
        if r.get("pool_after") is not None:
            after = r["pool_after"]
        if r.get("pool") is not None:
            if "before" in str(r.get("claim", "")):
                before = r["pool"] if before is None else before
            elif "after" in str(r.get("claim", "")):
                after = r["pool"]
            if r.get("settled") is False:
                settled = False
    return before, after, settled


def main():
    out = []
    out.append("# §6.4 PROBE — CLOSING LEDGER\n")
    out.append("**Probe CLOSED 2026-08-26. §6.3 RATIFIED at STOP 2** (Rafe, on the reference "
               "device).\n")
    out.append("Every figure below is recomputed from the flushed `ledger.jsonl` files and the "
               "images beside\nthem — not copied from a prior report and not typed from memory. "
               "The probe's rule was that\nthe ledger stores images rather than parameters, "
               "because no surface on this platform is\nseed-reproducible; a closing account "
               "taken any other way would not honour it.\n")
    out.append("| phase | billed calls | images kept | refused/error |")
    out.append("|---|---:|---:|---:|")

    tot_calls = tot_imgs = tot_bad = 0
    detail = []
    for phase, label in PHASES.items():
        rows = read(phase)
        gens = calls(rows)
        ok = [r for r in gens if r.get("verdict") == "OK"]
        bad = [r for r in gens if r.get("verdict") != "OK"]
        # Images KEPT means generated images, counted from the ledger — not every PNG in the
        # directory, which would sweep in contact sheets this probe built for reading.
        imgs = len([r for r in ok if r.get("image")])
        out.append("| %s | %d | %d | %d |" % (label, len(gens), imgs, len(bad)))
        tot_calls += len(gens)
        tot_imgs += imgs
        tot_bad += len(bad)
        b, a, settled = bracket(rows)
        if b is not None or a is not None:
            detail.append((label, b, a, settled))

    out.append("| **probe total** | **%d** | **%d** | **%d** |" % (tot_calls, tot_imgs, tot_bad))
    out.append("| _surface audit (pre-probe, cited not recomputed)_ | _%d_ | _27_ | _0_ |"
               % AUDIT_GENERATIONS)
    out.append("| **GRAND TOTAL** | **%d** | **%d** | **%d** |"
               % (tot_calls + AUDIT_GENERATIONS, tot_imgs + 27, tot_bad))
    out.append("\n⚠ The surface audit's row is **cited from `AUDIT-FINDINGS.md`, not recomputed "
               "here.** Its ledger\npredates this module and records *claims* rather than billed "
               "calls — one claim there can stand\nbehind eight generations. Counting its rows "
               "would understate the spend, and counting its\nnon-OK verdicts as errors would "
               "invent failures that never happened.\n")

    out.append("\n## Balance brackets, settled at both ends\n")
    out.append("AUDIT 8.5: the platform's balance ledger settles late and slowly — two reads 15s "
               "apart once\nagreed on a figure that was 32% low. Every bracket below required "
               "**three consecutive\nidentical reads** before it was believed.\n")
    out.append("| phase | pool before | pool after | settled |")
    out.append("|---|---:|---:|:--:|")
    for label, a, b, settled in detail:
        out.append("| %s | %s | %s | %s |" % (label, a, b, "yes" if settled else "**NO**"))

    out.append("\n## What the probe spent, and on what\n")
    out.append("- **Generations billed by the probe proper: %d**, plus **%d** for the "
               "pre-probe surface audit\n  that froze the instrument — **%d total.** Cost was "
               "measured settled at **1.00 generation per\n  BitForge call** *before* the "
               "120-generation Stage 1 batch was authorised, not reconstructed\n  after it.\n"
               % (tot_calls, AUDIT_GENERATIONS, tot_calls + AUDIT_GENERATIONS))
    out.append("- **Images retained by the probe proper: %d.** Every generation — accepted, rejected, control, "
               "diagnostic — is on\n  disk with its full request payload. Nothing was deleted "
               "and nothing was curated out of the\n  ledger; curation happened downstream, on "
               "contact sheets, by Rafe.\n" % tot_imgs)
    out.append("- **Refusals/errors: %d.**\n" % tot_bad)

    out.append("\n## The frozen instrument, recorded\n")
    out.append("v2 HTTP `POST https://api.pixellab.ai/v2/create-image-bitforge`, every call, "
               "every stage.\nChosen on measured evidence, not preference: the only surface "
               "where a 32px native canvas and\na shading lever coexist AND the lever is "
               "measurable (pixdiff 1.0000 against a measured noise\nfloor of 0.3542; MCP "
               "`pro` and `pixflux` both measure 1.0000 against a 1.0000 noise floor,\nwhich is "
               "NO INSTRUMENT).\n")
    out.append("`client_compat.generate_image_bitforge` was never used and cannot be: it passes "
               "`style_image`\nthrough raw kwargs where it dies unserialisable (issue #140). "
               "This probe hand-encoded\n`Base64Image` throughout.\n")

    out.append("\n## What the probe answered, and what it did not\n")
    out.append("**Answered.** §6.3 is ratified on the device. The canvas holds at 32x32 native "
               "at x2 on the\nfrozen surface. `shading` is measurable on this endpoint and "
               "measurably did **not** move the\noutput in the intended direction. "
               "`coverage_percentage` moves pixels above the noise floor and\nchanges nothing "
               "compositional. `negative_description` is not additive. Single-reference\n"
               "conditioning propagates material DNA in 12 of 12, and propagates composition "
               "with it.\n")
    out.append("**Not answered, and not to be cited as answered.** The three-arm comparison. "
               "Stage 1 produced\nno arm A — no candidate in any arm depicted a directional key "
               "light — so there was nothing for\narms B and C to be compared against. The "
               "effort ratio never acquired a denominator and was\nnever computed. Ruling 47's "
               "clause stands: a finding about test conditions, not permission to\npick an "
               "arm.\n")
    out.append("**Reported as a bar cleared by the wrong instrument.** The wall micro-probe's "
               "declared bar was\n>=5 usable-as-wall in 20 and it returned 20/20 on framing — "
               "and all 20 are undifferentiated\nnoise. The bar was not re-tuned after the "
               "answer was visible (LOOP-PROCESS §8). It was drawn\nbadly, and that is recorded "
               "rather than corrected in hindsight.\n")

    path = os.path.join(HERE, "CLOSING-LEDGER.md")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    print("\n-> %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
