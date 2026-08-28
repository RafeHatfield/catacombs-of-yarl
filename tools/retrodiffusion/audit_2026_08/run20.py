#!/usr/bin/env python3
"""THE AMENDED CELL — n=20, `rd_tile__single_tile`, no tiling flags.

REPLACES the declared N/T two-cell design, per the design thread's amendment (items 3-5).
The amendment and its reason:

    Cells N and T differed ONLY in `tile_x`/`tile_y`. Those flags return HTTP 400
    `inference_failed` on `rd_tile__single_tile` — the only style measured to return a
    full-bleed unframed tile (AUDIT-RD.md Findings 1 and 3). There is no longer a single style
    on which both cells can run, so the flag is DROPPED FROM THE DESIGN and reported as a
    finding, and the seam question is answered POST HOC by an opposite-edge continuity census
    on every returned tile.

WHAT THIS RUN IS, STATED SO IT CANNOT BE MISREAD LATER
------------------------------------------------------
    This run measures RD's best-known configuration against the bar. It is NOT a controlled
    like-for-like against the baseline — style arm, prompt, and cell design all changed
    simultaneously.

    (And a FOURTH: `input_palette` is applied, without which amendment item 9's ramp-coverage
    measurement has nothing to measure. Named here rather than folded in quietly.)

DECLARED BEFORE THE FIRST CALL
------------------------------
    n         20, matching the baseline's n exactly. Spent in full.
    BUDGET    $0.500 at the measured $0.025. Declared spend is compared against actual and any
              discrepancy is FLAGGED, not reconciled away.
    STYLE     rd_tile__single_tile, 32x32, no tiling flags.
    PROMPT    prompts/floor_material_rd_v2.json — reworked toward §8.3.1's MIRROR.
    PALETTE   the 8-step neutral grey ramp, built in code.
    SCREEN    ring_instrument.py (constants untouched, shelled out to) AND census.py, and per
              amendment item 5 THE TWO ARE ONLY EVER REPORTED IN THE SAME TABLE ROW.
    MANIFEST  per amendment item 7: (prompt, seed, model, full params) AND the returned bytes.
              Reproducibility is PROVENANCE, not a storage substitute.
    REFUSALS  Promotes nothing. Touches no tier-one file. Alters no instrument constant.
              No adoption language anywhere in the output.
"""
import argparse
import hashlib
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "cell20_out")
PROMPTS = os.path.join(HERE, "prompts")

N = 20
SEED0 = 30000
DECLARED_BUDGET_USD = 0.500

# Cumulative across the whole session, tracked here because Budget objects are per-run.
# 10 reserved: 4 column audit + 3 style probe + 3 item-10 isolation. 6 billed; 4 refused and
# NOT billed (balance unmoved across all four, measured).
SESSION_SPENT_BEFORE = 10

# The 8-step neutral ramp. Built in code, NOT taken from the retired Oryx palette: §5.1's
# values are PLACEHOLDER and locking to a closed track's palette is working to a retired bar.
RAMP = [(18, 18, 22), (34, 34, 38), (52, 52, 56), (74, 74, 78),
        (96, 96, 100), (122, 122, 126), (150, 150, 154), (182, 182, 186)]


def ramp_image():
    im = Image.new("RGB", (len(RAMP), 1))
    im.putdata(RAMP)
    return im


def ramp_coverage(img):
    """AMENDMENT ITEM 9. Which of the 8 ramp steps actually appear, and in what proportion.

    MEASURED, NOT GATED. The reason it is worth measuring at all: palette MEMBERSHIP can pass
    while the VALUE STRUCTURE collapses. A tile using two of eight steps is 100% on-palette and
    is a flat clone field; a tile using all eight across a sane distribution is on-palette and
    has a value break. §5.1 gates the first and the wall recipe depends on the second, and one
    number cannot carry both.

    Nearest-step assignment, so a colour the generator moved slightly off-ramp still counts
    toward the step it is nearest rather than vanishing from the census.
    """
    px = list(img.convert("RGB").getdata())
    counts = [0] * len(RAMP)
    exact = 0
    for p in px:
        if p in RAMP:
            exact += 1
        best, bd = 0, None
        for i, r in enumerate(RAMP):
            d = (p[0] - r[0]) ** 2 + (p[1] - r[1]) ** 2 + (p[2] - r[2]) ** 2
            if bd is None or d < bd:
                best, bd = i, d
        counts[best] += 1
    n = len(px)
    used = sum(1 for c in counts if c)
    return {"steps_used": used, "steps_total": len(RAMP),
            "distribution": counts,
            "fraction": [round(c / n, 4) for c in counts],
            "exact_on_ramp_px": exact, "exact_fraction": round(exact / n, 4),
            "distinct_colours": len({p for p in px})}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=N)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    spec = json.load(open(os.path.join(PROMPTS, "floor_material_rd_v2.json")))
    rd.preflight()
    os.makedirs(OUT, exist_ok=True)
    led = rd.Ledger(OUT, "cell20_ledger.jsonl")

    pal = ramp_image()
    pal_b64 = rd.enc(pal)
    pal_sha = hashlib.sha256(json.dumps(RAMP).encode()).hexdigest()[:16]

    base = dict(spec["parameters"])
    base["prompt"] = spec["prompt"]
    base["input_palette"] = pal_b64

    if a.dry_run:
        print("-- DRY RUN, nothing spent --")
        show = {k: v for k, v in base.items() if k != "input_palette"}
        print(json.dumps({"n": a.n, "seed0": SEED0, "declared_usd": DECLARED_BUDGET_USD,
                          "payload": show, "ramp_sha": pal_sha}, indent=1))
        return 0

    budget = rd.Budget(ceiling=min(a.n, rd.SESSION_CEILING - SESSION_SPENT_BEFORE))
    sess = rd.Session(OUT, "rd_cell20", budget=budget, ledger=led, declaration={
        "amendment": "replaces declared N/T cells; items 3-5",
        "intent": "This run measures RD's best-known configuration against the bar. It is NOT "
                  "a controlled like-for-like against the baseline — style arm, prompt, and "
                  "cell design all changed simultaneously.",
        "fourth_change": "input_palette applied, without which item 9 has nothing to measure",
        "n": a.n, "seed0": SEED0, "declared_budget_usd": DECLARED_BUDGET_USD,
        "style": base["prompt_style"], "tiling_flags": False,
        "prompt_file": "prompts/floor_material_rd_v2.json",
        "ramp": RAMP, "ramp_sha": pal_sha,
        "session_spent_before": SESSION_SPENT_BEFORE,
        "refusals": ["promotes nothing in any state",
                     "touches no tier-one file, corpus file, or survivor",
                     "alters no constant in any instrument",
                     "no adoption language in any output"]}).open()

    manifest = []
    for i in range(a.n):
        seed = SEED0 + i
        p = dict(base)
        p["seed"] = seed
        imgs, row = rd.generate(p, led, "cell20_%05d" % seed, budget, image_subdir="tiles",
                                claim="rd_cell20:%d" % seed,
                                extra={"cell": "AMENDED20", "seed_used": seed,
                                       "tiling": False, "conditioned": False,
                                       "ramp_sha": pal_sha})
        entry = {"seed": seed, "verdict": row["verdict"], "model": row.get("model"),
                 "actual_cost": row.get("actual_cost"),
                 "estimated_cost": row.get("estimated_cost"),
                 "estimate_matched": row.get("estimate_matched"),
                 "seconds": row.get("seconds"),
                 "image": (row.get("images") or [None])[0],
                 "image_sha256": (row.get("image_sha256") or [None])[0],
                 # ITEM 7: full params stored alongside the bytes. Provenance, not a substitute.
                 "params": {k: v for k, v in p.items() if k != "input_palette"},
                 "input_palette_ramp": RAMP}
        if imgs:
            entry["ramp_coverage"] = ramp_coverage(imgs[0])
        manifest.append(entry)
        print("  seed %d  %s  act=%s  %ss  steps_used=%s"
              % (seed, row["verdict"], row.get("actual_cost"), row.get("seconds"),
                 entry.get("ramp_coverage", {}).get("steps_used")))

    close = sess.close()
    actual = close.get("billed_sum")
    disc = None
    if isinstance(actual, (int, float)):
        disc = round(actual - DECLARED_BUDGET_USD, 6)
    led.write({"claim": "rd_cell20:budget_check", "kind": "budget_check",
               "verdict": "INFO" if disc == 0 else "DISCREPANCY_FLAGGED",
               "declared_usd": DECLARED_BUDGET_USD, "actual_usd": actual,
               "difference": disc,
               "note": "FLAGGED, not reconciled — the declared figure is left as declared."})

    json.dump({"n": a.n, "seed0": SEED0, "ramp": RAMP, "ramp_sha": pal_sha,
               "declared_budget_usd": DECLARED_BUDGET_USD, "actual_usd": actual,
               "difference": disc, "entries": manifest},
              open(os.path.join(OUT, "MANIFEST.json"), "w"), indent=1, sort_keys=True)

    print("\ndeclared $%.3f   actual $%s   difference $%s   %s"
          % (DECLARED_BUDGET_USD, actual, disc,
             "as declared" if disc == 0 else "DISCREPANCY FLAGGED"))
    print("-> %s" % os.path.relpath(OUT, rd.REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
