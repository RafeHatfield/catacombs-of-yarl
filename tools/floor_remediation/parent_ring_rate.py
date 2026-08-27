#!/usr/bin/env python3
"""PARENT RING-RATE — is the ring the PARENT's, or is it the SURFACE's?

THE QUESTION
------------
REPORT.md §4 measured 24 generations conditioned on B-KAB: **22 came back ringed.** Two levers
were tried — an explicit refusal of the construction, and `style_strength` 50 -> 80 — and
neither moved it. The conclusion recorded was that the ring cannot be prompted away and that
screening is what catches it.

That conclusion has an untested alternative, and it is the whole reason this file exists.
**B-KAB is itself a ringed tile.** A ring rate of 22/24 from a ringed parent is equally
consistent with two very different worlds:

    the ring is the PARENT's    conditioning faithfully carried down a keyline that was in the
                                reference. A ring-free parent would not produce it. Screening is
                                then a B-KAB-shaped problem that retired with B-KAB.

    the ring is the SURFACE's   this generator draws keylines on 32px floor tiles whatever it is
                                shown. A ring-free parent produces them too. Screening is then
                                permanent infrastructure that every floor generation must pass
                                through, forever.

Those two worlds are told apart by conditioning on a parent the instrument calls CLEAN, holding
everything else still. C-GAB is that parent: RULED primary style parent (bible §5.5, 2026-08-27),
`may_condition: true`, instrument CLEAN at every value, near-ring score 0.791.

DECLARED BEFORE THE FIRST CALL — gauntlet clause §1.1.3, bounded by budget and width, never by
rounds and never by check-ins:

    BUDGET   20 generations, two cells of 10. BOTH CELLS ARE SPENT IN FULL whatever cell P
             shows. This is the B-KAB run's own recorded run-order lesson applied in advance:
             its first draft stopped after any wave that cleared the bar, and stopping early is
             what turns a measurement into an anecdote.
    LEVERS   HELD CONSTANT, at wave 1's setting: `style_strength` 50, and NO ring refusal in the
             negative description. Neither of the two levers the B-KAB run moved is touched
             here. This is a measurement, not a search.
    SCREEN   `ring_instrument.py`, mechanically, every child. It is a FLOOR, NOT A VERDICT
             (bible §13.2, REPORT §6) and its known limit stands unchanged and untuned.
    SEAT     a blind spot-check on the BORDERLINE ones only - see THE SEAT TRIAGE below.
    REPORT   ring rate against the B-KAB run's 22/24. Ruling trigger: report only.

    REFUSALS  no promotion of any child, in any state. Nothing is written to `remediated/`.
              Nothing touches the corpus, the survivors, or `MANIFEST.json`. No constant in
              `ring_instrument.py` is altered. No lever is tuned toward a nicer number.

THE TWO CELLS — AND WHY THERE ARE TWO
-------------------------------------
"Same prompt shape as the B-KAB run" has two faithful readings and they are not the same
experiment. The B-KAB run was `subject_floor + arm_B`, conditioned on B-KAB — and B-KAB is an
arm-B tile, so that run was simultaneously *the parent's own prompt* and *arm B's text*. Swap in
C-GAB, an arm-C tile, and those two readings come apart:

  cell P   PROMPT-MATCHED     `subject_floor + arm_B`, byte-identical to the B-KAB run's prompt.
  (n=10)                      The ONLY thing that differs from that run is the reference image.
                              This is the single-variable comparison and it is the one that
                              answers the question. Its cost: C-GAB is a flat arm-C tile being
                              shown under an arm-B prompt that asks for darker joints, so parent
                              and prompt are no longer coherent the way B-KAB's were.

  cell S   STRUCTURE-MATCHED  `subject_floor + arm_C`, C-GAB's own arm. Replicates the
  (n=10)                      RELATIONSHIP the B-KAB run had - a parent conditioned under its own
                              arm - rather than the text. Its cost: two things now differ from
                              the B-KAB run at once (the reference AND the arm block), so a
                              difference here cannot be attributed to the parent alone.

Each cell's weakness is the other cell's control, which is why 20 buys two tens rather than one
twenty. **If the two cells agree, the arm block is not the explanation and both comparisons say
the same thing.** If they disagree, that disagreement is itself the finding and is reported as
one rather than resolved by picking the more convenient cell.

WHAT DIFFERS FROM THE B-KAB RUN, RECORDED EXHAUSTIVELY SO THE CAVEAT IS EXACT
-----------------------------------------------------------------------------
`subject_floor.json` is used unchanged and is IDENTICAL across every arm. It is the file that
carries `outline: lineless` and the negatives `border, frame, outline` — so the ring refusals
that were already in play for B-KAB are still in play here, in both cells, unchanged.

  cell P vs B-KAB wave 1:  the `style_image` bytes. NOTHING ELSE. The description, the negative
                           description, every parameter and `style_strength` are the same values.
  cell S vs B-KAB wave 1:  the `style_image` bytes, PLUS the arm block - `arm_C.lighting`
                           replaces `arm_B.lighting` in the description, and `shading` goes from
                           "basic shading" to "flat shading". Those two fields and no others.

The diff is asserted at runtime, not claimed in this docstring: `_declare_diff` computes the
exact set of differing payload keys against a reconstruction of the B-KAB wave-1 payload and
writes it into the ledger before anything is spent.

THE SEAT TRIAGE — DECLARED, AND NOT A SECOND THRESHOLD
------------------------------------------------------
REPORT §6 is unambiguous that the instrument does not catch every construction a human calls a
keyline, and that no threshold separates the classes: the seat called 0.654 a keyline and 0.791
clean. So a purely mechanical rate would over-report CLEAN, in a known direction, by a known
mechanism. The spot-check exists to bound that.

    every child the instrument calls CLEAN whose near-ring score is >= 0.60 goes to the seat.

0.60 sits BELOW the floor of REPORT §6's measured overlap band (0.654-0.791), so the triage
cannot miss a child inside the zone where the instrument and the seat are known to disagree.
It is a triage cut and NOT a verdict threshold — `near_ring.py`'s docstring carries that
distinction and ruling 3 forbids the other reading. The seat's culls are reported as a SECOND,
separately-labelled rate; the instrument's rate is never quietly revised by them.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PROBE = os.path.join(REPO, "tools/pixellab/probe_6_4")
sys.path.insert(0, HERE)
sys.path.insert(0, PROBE)
import ring_instrument as RI      # noqa: E402
import near_ring as NR            # noqa: E402
import v2_bitforge as v2          # noqa: E402

SURVIVORS = os.path.join(PROBE, "survivors")
PROMPTS = os.path.join(PROBE, "prompts")
OUT = os.path.join(HERE, "parent_rate_cgab")

CODE = "C-GAB"
PARENT_SHA = "1a24a59aa5607c3beebd8d1cf728acc0f43d6fc0bace6015025a7595c3f6db4f"
CELL_SIZE = 10
BUDGET = 20
STYLE_STRENGTH = 50           # wave 1's value. HELD. Not a lever in this run.
SEAT_TRIAGE = 0.60            # see THE SEAT TRIAGE in the module docstring

# The B-KAB run's headline, quoted so the comparison basis is in the file rather than in memory.
BKAB = dict(pooled_ringed=22, pooled_n=24, wave1_ringed=8, wave1_n=8,
            source="tools/floor_remediation/REPORT.md §4; regen_bkab/RESULT.json")

CELLS = [
    dict(name="P", arm="arm_B", n=CELL_SIZE, seed0=9700,
         label="PROMPT-MATCHED - byte-identical to the B-KAB run's prompt; only the reference "
               "image differs"),
    dict(name="S", arm="arm_C", n=CELL_SIZE, seed0=9800,
         label="STRUCTURE-MATCHED - C-GAB's own arm; replicates a parent conditioned under its "
               "own arm"),
]


def build(arm_file):
    """subject_floor + one arm, exactly as regenerate.py assembles it. No local edits."""
    subj = json.load(open(os.path.join(PROMPTS, "subject_floor.json")))
    arm = json.load(open(os.path.join(PROMPTS, arm_file + ".json")))
    base = dict(subj["parameters"])
    base.update(arm["parameters"])
    base["description"] = subj["description"] + " " + arm["lighting"]
    base["negative_description"] = subj["negative_description"]
    return base


def _declare_diff():
    """Compute the exact payload diff against the B-KAB wave-1 shape. Asserted, not claimed.

    The caveat this run has to carry is 'the prompts differ only where recorded'. A docstring
    saying so is a claim; this is the recording. Any key that differs and is not in the expected
    set is a HARD STOP - it would mean the comparison is not the one described.
    """
    bkab = build("arm_B")          # what the 24-generation run sent, minus its style_image
    out = {}
    for cell in CELLS:
        mine = build(cell["arm"])
        keys = sorted(set(bkab) | set(mine))
        differ = [k for k in keys if json.dumps(bkab.get(k), sort_keys=True)
                  != json.dumps(mine.get(k), sort_keys=True)]
        expected = [] if cell["arm"] == "arm_B" else ["description", "shading"]
        out[cell["name"]] = dict(
            arm=cell["arm"], differing_keys=differ, expected=expected,
            unexpected=[k for k in differ if k not in expected],
            style_strength=STYLE_STRENGTH, ring_refusal_added=False,
            style_image="the reference differs in every cell - that is the variable under test")
        if out[cell["name"]]["unexpected"]:
            raise SystemExit("HARD STOP: cell %s differs from the B-KAB payload in unexpected "
                             "keys %s. The comparison is not the one this module describes."
                             % (cell["name"], out[cell["name"]]["unexpected"]))
    return out


def screen(path):
    """The mechanical screen. Instrument verdict + the triage score, both recorded."""
    a = np.array(Image.open(path).convert("RGB")).astype(int)
    v, rings = RI.verdict(a)
    score, detail = NR.near_ring_score(a)
    return dict(verdict=v, rings=RI.public(rings), near_ring=score, near_ring_detail=detail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print the declaration and the exact payload diff; spend nothing")
    ap.add_argument("--rescreen", action="store_true",
                    help="re-screen the children already on disk and rewrite RESULT.json; "
                         "spends nothing")
    ap.add_argument("--seat-tiles", metavar="DIR",
                    help="write the blind seat's tile lists into DIR, one per cell, by the "
                         "declared triage rule. Spends nothing and picks nothing by hand.")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    parent_path = os.path.join(SURVIVORS, CODE + ".png")
    ref = Image.open(parent_path).convert("RGB")
    parent = np.array(ref).astype(int)

    import hashlib
    sha = hashlib.sha256(open(parent_path, "rb").read()).hexdigest()
    if sha != PARENT_SHA:
        raise SystemExit("HARD STOP: %s.png is not the ruled survivor (sha %s)" % (CODE, sha))
    v_parent, rings_parent = RI.verdict(parent)
    if v_parent != "CLEAN":
        raise SystemExit("HARD STOP: the parent must be ring-CLEAN for this question to mean "
                         "anything; the instrument says %s" % v_parent)
    score_parent, _ = NR.near_ring_score(parent)

    diff = _declare_diff()

    print("PARENT RING-RATE - C-GAB as primary style parent")
    print("  parent      %s  sha %s..." % (os.path.relpath(parent_path, REPO), sha[:16]))
    print("  role        RULED primary style parent (bible §5.5, 2026-08-27), may_condition=true")
    print("  instrument  %s on the parent, near-ring %.3f" % (v_parent, score_parent))
    print("  budget      %d generations, two cells of %d, BOTH SPENT IN FULL" % (BUDGET, CELL_SIZE))
    print("  levers      style_strength=%d, ring refusal NOT added. Held, both cells."
          % STYLE_STRENGTH)
    print("  against     B-KAB %d of %d pooled; %d of %d at wave 1's identical levers"
          % (BKAB["pooled_ringed"], BKAB["pooled_n"], BKAB["wave1_ringed"], BKAB["wave1_n"]))
    print("\n  THE PAYLOAD DIFF vs the B-KAB run - the caveat, recorded rather than claimed:")
    for cell in CELLS:
        d = diff[cell["name"]]
        print("    cell %s (%s): differs in %s"
              % (cell["name"], d["arm"], d["differing_keys"] or "NOTHING - only the reference"))
    print()

    if args.dry_run:
        p = dict(build("arm_B"))
        print("  payload keys: %s" % sorted(list(p) + ["style_image", "style_strength", "seed"]))
        print("  shading P=%s  S=%s" % (build("arm_B")["shading"], build("arm_C")["shading"]))
        print("\n  --dry-run: nothing spent.")
        return 0

    rp = os.path.join(OUT, "RESULT.json")
    if args.seat_tiles:
        return write_seat_tiles(json.load(open(rp)), args.seat_tiles)
    if args.rescreen:
        res = json.load(open(rp))
        for r in res["results"]:
            if r.get("file"):
                r.update(screen(os.path.join(OUT, r["file"])))
        summarise(res, diff, score_parent)
        json.dump(res, open(rp, "w"), indent=1)
        return 0

    if os.path.exists(rp):
        raise SystemExit("HARD STOP: %s exists. This run is a single declared measurement, not "
                         "a loop; re-running would spend a second budget on the same question. "
                         "Use --rescreen." % os.path.relpath(rp, REPO))

    led = v2.Ledger(OUT)
    before, stable_b = v2.settled_pool()
    led.write({"claim": "parent_rate:declaration", "verdict": "INFO", "pool": before,
               "settled": stable_b, "budget": BUDGET, "parent": CODE, "parent_sha256": sha,
               "parent_verdict": v_parent, "parent_near_ring": score_parent,
               "style_strength": STYLE_STRENGTH, "ring_refusal_added": False,
               "cells": {c["name"]: dict(arm=c["arm"], n=c["n"]) for c in CELLS},
               "payload_diff_vs_bkab": diff, "compare_against": BKAB,
               "seat_triage_at": SEAT_TRIAGE})
    print("pool before: %s (settled=%s)\n" % (before, stable_b))

    ref_b64 = v2.enc(ref)
    results = []
    spent = 0
    for cell in CELLS:
        print("== CELL %s ==  %s" % (cell["name"], cell["label"]))
        base = build(cell["arm"])
        if ref.size != (base["image_size"]["width"], base["image_size"]["height"]):
            raise SystemExit("REFUSING: reference %s vs generation %s; the server 500s on a "
                             "mismatch and nothing here resizes a reference"
                             % (ref.size, base["image_size"]))
        for i in range(cell["n"]):
            if spent >= BUDGET:
                break
            seed = cell["seed0"] + i
            p = dict(base)
            p["style_image"] = ref_b64
            p["style_strength"] = STYLE_STRENGTH
            p["seed"] = seed
            name = "%s_seed%d" % (cell["name"], seed)
            img, row = v2.generate(
                p, led, name, image_subdir=cell["name"],
                claim="parent_rate:%s:%s:%d" % (CODE, cell["name"], seed),
                extra={"parent": CODE, "cell": cell["name"], "arm": cell["arm"],
                       "seed_used": seed, "style_strength": STYLE_STRENGTH,
                       "reference": CODE})
            spent += 1
            rec = dict(cell=cell["name"], arm=cell["arm"], seed=seed, file=row["image"],
                       sha256=row.get("image_sha256"), call_verdict=row["verdict"])
            if img is None:
                print("   seed %d  %s" % (seed, row["verdict"]))
                results.append(rec)
                continue
            rec.update(screen(os.path.join(OUT, row["image"])))
            print("   seed %d  %-5s  near-ring %.3f%s"
                  % (seed, rec["verdict"], rec["near_ring"],
                     "   <- carries a ring" if rec["verdict"] == "RING" else
                     ("   <- borderline, goes to the seat"
                      if rec["near_ring"] >= SEAT_TRIAGE else "")))
            for r in rec["rings"][:1]:
                print("        %s %s  wall=%dpx interior=%dpx sides=%.2f width=%.2f+-%.2f"
                      % (r["kind"], r["level"], r["contour_px"], r["interior_px"],
                         r["side_coverage"], r["wall_thickness"], r["wall_thickness_spread"]))
            results.append(rec)
        n_ring = sum(1 for r in results if r["cell"] == cell["name"]
                     and r.get("verdict") == "RING")
        n_ok = sum(1 for r in results if r["cell"] == cell["name"]
                   and r.get("verdict") in ("RING", "CLEAN"))
        print("   cell %s: %d of %d ringed\n" % (cell["name"], n_ring, n_ok))

    after, stable_a = v2.settled_pool()
    led.write({"claim": "parent_rate:pool_after", "verdict": "INFO", "pool": after,
               "settled": stable_a, "generations": spent})

    res = dict(parent=CODE, parent_sha256=sha, parent_verdict=v_parent,
               parent_near_ring=score_parent, budget=BUDGET, spent=spent,
               style_strength=STYLE_STRENGTH, ring_refusal_added=False,
               pool_before=before, pool_after=after, seat_triage_at=SEAT_TRIAGE,
               payload_diff_vs_bkab=diff, compare_against=BKAB, results=results)
    summarise(res, diff, score_parent)
    json.dump(res, open(rp, "w"), indent=1)
    print("\nwritten: %s" % os.path.relpath(rp, REPO))
    return 0


def write_seat_tiles(res, out_dir):
    """The seat's tile lists, derived from RESULT.json by the DECLARED rule. Nothing hand-picked.

    ONE ROUND PER CELL, because the two cells are two different comparisons and a seat should
    not be asked to hold nine unfamiliar floors in mind at once. Every round carries both
    published-prior controls (§13.5) plus one of this run's OWN ringed children:

      the borderline    every instrument-CLEAN child at or above the declared triage cut. This is
                        the measurement the seat is here to make - the instrument's known
                        under-count, bounded.
      CONTROL_ring      the highest-scoring child the instrument called RING, in that cell. The
                        plant proves the seat can cull B-KAB's keyline; this asks whether it
                        culls THIS run's keylines, on this run's material. It is the reverse
                        direction - if the seat clears it, the instrument OVER-counts and the
                        headline rate is biased upward, which must be reported too.
      CONTROL_plant     the raw B-KAB. Not culled => the round is VOID.
      CONTROL_parent    the raw C-GAB. The green half; a seat that culls everything is caught here.

    A cell with no borderline children still gets a round if it has any child at all, because
    "the seat had nothing to look at" and "the seat found nothing" are different results.
    """
    os.makedirs(out_dir, exist_ok=True)
    base = "tools/floor_remediation/parent_rate_cgab"
    surv = "tools/pixellab/probe_6_4/survivors"
    written = []
    for c in CELLS:
        rs = [r for r in res["results"] if r["cell"] == c["name"]
              and r.get("verdict") in ("RING", "CLEAN")]
        if not rs:
            continue
        border = sorted([r for r in rs if r["verdict"] == "CLEAN"
                         and r["near_ring"] >= res["seat_triage_at"]],
                        key=lambda r: -r["near_ring"])
        ringed = sorted([r for r in rs if r["verdict"] == "RING"],
                        key=lambda r: -r["near_ring"])
        tiles = [["%s_%s" % (c["name"], os.path.basename(r["file"])[:-4]),
                  os.path.join(base, r["file"])] for r in border]
        if ringed:
            tiles.append(["CONTROL_ring_%s" % os.path.basename(ringed[0]["file"])[:-4],
                          os.path.join(base, ringed[0]["file"])])
        tiles.append(["CONTROL_plant_BKAB", os.path.join(surv, "B-KAB.png")])
        tiles.append(["CONTROL_parent_CGAB", os.path.join(surv, "C-GAB.png")])
        path = os.path.join(out_dir, "seat_tiles_%s.json" % c["name"])
        with open(path, "w") as f:
            json.dump(tiles, f, indent=1)
        written.append((c["name"], path, len(border), 1 if ringed else 0))
        print("  cell %s: %d borderline (>= %.2f) + %d ring-control + 2 published controls -> %s"
              % (c["name"], len(border), res["seat_triage_at"], 1 if ringed else 0,
                 os.path.relpath(path, REPO)))
    if not written:
        print("  no cell produced a child; nothing to seat.")
    return 0


def summarise(res, diff, score_parent):
    rs = [r for r in res["results"] if r.get("verdict") in ("RING", "CLEAN")]
    ring = [r for r in rs if r["verdict"] == "RING"]
    clean = [r for r in rs if r["verdict"] == "CLEAN"]
    borderline = sorted([r for r in clean if r["near_ring"] >= res["seat_triage_at"]],
                        key=lambda r: -r["near_ring"])
    print("\nRESULT - THE RING RATE FROM A RING-CLEAN PARENT")
    print("  generations: %d of %d   pool %s -> %s"
          % (res["spent"], res["budget"], res["pool_before"], res["pool_after"]))
    for c in CELLS:
        cs = [r for r in rs if r["cell"] == c["name"]]
        if cs:
            print("  cell %s (%-4s): %d of %d ringed   near-ring median %.3f"
                  % (c["name"], c["arm"], sum(1 for r in cs if r["verdict"] == "RING"), len(cs),
                     float(np.median([r["near_ring"] for r in cs]))))
    print("  POOLED       : %d of %d ringed" % (len(ring), len(rs)))
    b = res["compare_against"]
    print("\n  AGAINST THE B-KAB RUN")
    print("    B-KAB pooled, mixed levers        %d of %d" % (b["pooled_ringed"], b["pooled_n"]))
    print("    B-KAB wave 1, THESE levers        %d of %d" % (b["wave1_ringed"], b["wave1_n"]))
    print("    C-GAB pooled, THESE levers        %d of %d" % (len(ring), len(rs)))
    print("\n  BORDERLINE - instrument CLEAN, near-ring >= %.2f, goes to the blind seat: %d"
          % (res["seat_triage_at"], len(borderline)))
    for r in borderline:
        print("    %-16s near-ring %.3f" % (r["file"], r["near_ring"]))
    res["summary"] = dict(pooled_ringed=len(ring), pooled_n=len(rs),
                          per_cell={c["name"]: dict(
                              ringed=sum(1 for r in rs if r["cell"] == c["name"]
                                         and r["verdict"] == "RING"),
                              n=sum(1 for r in rs if r["cell"] == c["name"]))
                              for c in CELLS},
                          borderline=[r["file"] for r in borderline])
    return res


if __name__ == "__main__":
    sys.exit(main())
