#!/usr/bin/env python3
"""§6.4 probe — CONDITIONING SMOKE TEST. Small, informational, NOT arm-based, NO GATE.

RULED (Rafe, STOP 1): ~6 generations conditioned on each of the two strongest survivors
(A-VAB, C-GAB), same subject prompts.

    Question: does the material DNA propagate, and how sensitive is it to WHICH reference?
    No gate. Evidence for tier 1's bet on single-reference conditioning.

**This is not Stage 2 and must not be read as it.** Stage 2 is two seats per arm, half the
arm's budget each, measuring treatment hold under conditioning. This is twelve generations
asking whether the conditioning channel carries material at all. It has no arms, no treatment
lever, no regeneration rate, and no pass mark. It cannot rule on anything and is not offered
as ruling on anything.

WHY IT IS WORTH TWELVE GENERATIONS ANYWAY
-----------------------------------------
`AUDIT-FINDINGS.md` records that BitForge takes **exactly one** `style_image`, and the probe's
brief handles the fragility that creates with a two-seat design whose whole premise is that
*which* reference you pick matters. Tier 1 bets on that mechanism. Nothing has ever measured
it on this project. Two references x the same six seeds is the cheapest arrangement that can
show a difference between references at all — and if the two seats come back
indistinguishable, that is itself worth knowing before tier 1 spends real budget on seat
diversity.

MECHANICS THAT WILL BITE IF FORGOTTEN
-------------------------------------
* `style_image` must EQUAL the generation size or the server returns a hard HTTP 500
  (`style_image must be size (24, 24), not torch.Size([32, 32])`). Survivors are 32x32 native
  and generation is 32x32, so they match — but nothing here resizes, and nothing should.
* `style_strength` defaults to **0**, at which a reference does nothing at all. It is set
  explicitly. 50 is the schema's own "balanced".
* `client_compat.generate_image_bitforge` cannot carry a style_image (#140). This module
  hand-encodes `Base64Image`, which is the entire reason it exists.
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import v2_bitforge as v2  # noqa: E402

OUT = os.path.join(HERE, "conditioning_smoke")
PROMPTS = os.path.join(HERE, "prompts")
SURV = os.path.join(HERE, "survivors")
SEEDS = [8800 + i for i in range(6)]        # the SAME six seeds for both references
STYLE_STRENGTH = 50
REFS = ("A-VAB", "C-GAB")


def main():
    subj = json.load(open(os.path.join(PROMPTS, "subject_floor.json")))
    arm = json.load(open(os.path.join(PROMPTS, "arm_B.json")))
    led = v2.Ledger(OUT)

    print("CONDITIONING SMOKE TEST — informational, no gate, not Stage 2.")
    print("commit:  %s" % led.commit)
    print("refs:    %s (the two Rafe named strongest)" % ", ".join(REFS))
    print("seeds:   %s — identical across both refs, so the reference is the only variable"
          % SEEDS)
    print("style_strength: %d (the default is 0, at which a reference does nothing)\n"
          % STYLE_STRENGTH)

    before, stable_b = v2.settled_pool()
    led.write({"claim": "smoke:pool_before", "verdict": "INFO", "pool": before,
               "settled": stable_b, "planned_generations": len(REFS) * len(SEEDS)})

    base = dict(subj["parameters"])
    base.update(arm["parameters"])
    base["description"] = subj["description"] + " " + arm["lighting"]
    base["negative_description"] = subj["negative_description"]

    for code in REFS:
        ref_path = os.path.join(SURV, "%s.png" % code)
        ref = Image.open(ref_path).convert("RGB")
        if ref.size != (base["image_size"]["width"], base["image_size"]["height"]):
            print("REFUSING: %s is %s, generation is %s — the server rejects a mismatch with a "
                  "hard 500 and nothing here resizes a reference." %
                  (code, ref.size, base["image_size"]))
            return 2
        print("== reference %s (%s) ==" % (code, ref.size))
        for s in SEEDS:
            p = dict(base)
            p["seed"] = s
            p["style_image"] = v2.enc(ref)
            p["style_strength"] = STYLE_STRENGTH
            img, row = v2.generate(p, led, "%s_seed%d" % (code, s), image_subdir=code,
                                   claim="smoke:cond:%s:%d" % (code, s),
                                   extra={"reference": code, "seed_used": s,
                                          "style_strength": STYLE_STRENGTH,
                                          "informational": True})
            print("   seed %d  %s  %s" % (s, row["verdict"], row.get("out_size") or ""))

    after, stable_a = v2.settled_pool()
    print("\npool after: %s (settled=%s)  spent: %s" %
          (after, stable_a, (before - after) if (before and after) else "UNMEASURED"))
    led.write({"claim": "smoke:pool_after", "verdict": "INFO", "pool": after,
               "settled": stable_a})
    print("\nWhether material DNA propagated is an EYE call from the sheet. No number here\n"
          "answers it, and a pixdiff would not: Stage 1 established on this very surface that\n"
          "a diff above the noise floor says a parameter MOVED the output, not that it moved\n"
          "it in the intended direction.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
