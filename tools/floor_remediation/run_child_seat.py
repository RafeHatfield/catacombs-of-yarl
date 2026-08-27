#!/usr/bin/env python3
"""THE BLIND SEAT — SPOT-CHECK ROUND for the parent ring-rate run.

WHY THERE IS A SEAT AT ALL IN A RUN WHOSE SCREEN IS MECHANICAL
--------------------------------------------------------------
REPORT.md §6 measured, and ruling 3 confirmed, that `ring_instrument.py` is A FLOOR AND NOT A
VERDICT: it catches the drawn keyline decisively and it does NOT catch every construction a
human calls one. The overlap is published — the seat called a tile scoring 0.654 a keyline and
tiles scoring 0.688 and 0.791 clean. So a purely mechanical ring rate is biased in a KNOWN
DIRECTION: it under-counts. The seat bounds that bias. It does not replace the instrument's
number and it never silently revises it — the two rates are reported separately and labelled.

WHAT THE SEAT SEES — LOOP-PROCESS §2.1 / §3, unchanged
------------------------------------------------------
A fresh `claude -p`, cwd OUTSIDE the repo, no bible, no memory, no prior round. Blindness is
structural, not promised. What it reads is the LIT IN-SCENE CAPTURE at the reference device's
pixel size, never a contact sheet and never a 32x32 PNG. `seat_prompt.txt` is used VERBATIM —
the same instrument that produced rounds A and B, so its verdicts are comparable to theirs.
Its parser is imported from `run_seat.py` for the same reason, including the LOOP-PROCESS §5
rule that converts a hedged PASS to a FAIL.

THE TWO CONTROLS — bible §13.5
------------------------------
  PLANT (red)    the raw un-remediated B-KAB. Culled `keyline` by this seat in BOTH round A and
                 round B. NOT CULLED HERE => THE ROUND IS VOID, not discounted, void.
  PARENT (green) the raw C-GAB, the tile every child was conditioned on. `cull: none` in round A.
                 A seat that culls everything satisfies the plant and has still discriminated
                 nothing; the parent is what catches that. If the parent is culled `keyline`
                 here, the round is NOT void — it is a finding about the parent and is reported.

Codes are anonymised and ordered by a hash of the label, so the listing order carries no
information about which image is a child, the plant, or the parent. The mapping is written to
the result JSON, which the seat never sees.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import run_seat as RS      # noqa: E402

CAPTURES = os.path.join(HERE, "evidence", "children")
OUT = os.path.join(HERE, "evidence", "child_seat")
WORK_ROOT = ("/private/tmp/claude-501/-Users-rafehatfield-development-c-yarl/"
             "9bc57ff8-426b-4eb1-a110-1b2333ed06d5/scratchpad/child_seat")

# Published prior verdicts, quoted so the controls are controls rather than assertions.
PRIOR = {
    "plant": "round A and round B both culled the raw B-KAB `keyline`",
    "parent": "round A returned `cull: none` on the raw C-GAB",
}


def assign_codes(labels):
    """F1..Fn, ordered by a hash of the label. Deterministic, recorded, and not set order."""
    ordered = sorted(labels, key=lambda s: hashlib.sha256(s.encode()).hexdigest())
    return {"F%d" % (i + 1): lab for i, lab in enumerate(ordered)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="C", help="round id, for the transcript filename")
    ap.add_argument("--captures", default=CAPTURES,
                    help="capture directory written by capture_children.py (one per cell)")
    args = ap.parse_args()

    man = json.load(open(os.path.join(args.captures, "manifest.json")))
    labels = [c["label"] for c in man["captures"]]
    plant = next((l for l in labels if l.startswith("CONTROL_plant")), None)
    parent = next((l for l in labels if l.startswith("CONTROL_parent")), None)
    if not plant or not parent:
        raise SystemExit("HARD STOP: the round needs both controls. plant=%s parent=%s"
                         % (plant, parent))

    mapping = assign_codes(labels)
    work = os.path.join(WORK_ROOT, "round%s" % args.round)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    for code, lab in mapping.items():
        shutil.copy2(os.path.join(args.captures, lab + ".png"), os.path.join(work, code + ".png"))

    inv = {lab: code for code, lab in mapping.items()}
    print("=" * 78)
    print("BLIND FLOOR SEAT - SPOT-CHECK ROUND %s" % args.round)
    print("commit: %s" % RS.git_commit())
    print("cwd:    %s" % work)
    print("        outside the repo; %d captures, codes anonymised, not in set order"
          % len(mapping))
    print("        %d children + plant (%s) + parent (%s)"
          % (len(mapping) - 2, inv[plant], inv[parent]))
    print("=" * 78)

    text = RS.run(work)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "round%s_transcript.txt" % args.round), "w") as f:
        f.write(text)

    verdicts, flips, rank, sep = RS.parse(text)
    near = {c["label"]: c["near_ring"] for c in man["captures"]}
    instr = {c["label"]: c["floor_verdict"] for c in man["captures"]}
    for code in sorted(verdicts, key=lambda c: int(c[1:]) if c[1:].isdigit() else 0):
        lab = mapping.get(code, "?")
        tag = ("  <- PLANT" if lab == plant else "  <- PARENT" if lab == parent else "")
        print("  %-4s = %-26s %-4s cull=%-12s instr=%-5s near=%.3f%s"
              % (code, lab, verdicts[code]["verdict"], verdicts[code]["cull"] or "none",
                 instr.get(lab, "?"), near.get(lab, 0.0), tag))
        print("        %s" % verdicts[code]["why"][:100])
        if verdicts[code]["hedge_converted"]:
            print("        (PASS converted to FAIL: the reason hedged - LOOP-PROCESS §5)")

    pv = verdicts.get(inv[plant], {})
    caught = pv.get("verdict") == "FAIL"
    par = verdicts.get(inv[parent], {})
    children = [c for c, l in mapping.items() if l not in (plant, parent)]
    keylined = [c for c in children if verdicts.get(c, {}).get("cull", "").strip() == "keyline"]

    print("\n  PLANT  : %s (cull=%s)   prior: %s"
          % ("CAUGHT" if caught else "MISSED - ROUND VOID", pv.get("cull"), PRIOR["plant"]))
    print("  PARENT : cull=%s   prior: %s" % (par.get("cull"), PRIOR["parent"]))
    if par.get("cull", "").strip() == "keyline":
        print("           ^ the parent itself is culled keyline. NOT a void round - a FINDING")
        print("             about the ruled primary style parent, and it is reported as one.")
    print("  CHILDREN culled `keyline` by the seat: %d of %d  %s"
          % (len(keylined), len(children), sorted(keylined)))

    rec = dict(round=args.round, commit=RS.git_commit(), mapping=mapping, plant=plant,
               parent=parent, prior=PRIOR, verdicts=verdicts, ranking=rank, separator=sep,
               flip_list=flips, plant_caught=caught, round_void=not caught,
               parent_cull=par.get("cull"), children=children,
               children_keylined=[mapping[c] for c in keylined],
               instrument=instr, near_ring=near)
    with open(os.path.join(OUT, "round%s_result.json" % args.round), "w") as f:
        json.dump(rec, f, indent=1)
    print("\n-> %s" % os.path.relpath(OUT, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
