#!/usr/bin/env python3
"""THE PLANT CONTROL, REBUILT AS A JUDGEMENT — LOOP-PROCESS §1.1's STOP, discharged.

    python3 tools/tier1_walls/plant_adjudicator.py --controls     # run this FIRST
    python3 tools/tier1_walls/plant_adjudicator.py --round 10

RULED (Rafe, 2026-09-02): *"replace the plant control under the §1.1 STOP first — round 10's seat
is untrusted in either direction until the control can catch its own plant."*

`audit_plant_control.py` established that the grep is not an instrument: four of its 26 terms fire
on FAMILY transcripts (`nothing has happened` 7/10, `stamped` 6/10), rounds 4 and 8 rest entirely
on those, and it has no term at all for the forked crack the plant draws — which is what killed
round 9. Widening greens the void rounds; narrowing flips the valid ones. **The defect it guards
is a register judgement and a substring match cannot make one.**

So the control is a judgement now. A fresh `claude -p`, given the plant seat's TRANSCRIPT and
nothing else, asked one question: *did this reviewer report the structure as ruined — damaged and
never answered — as a DEFECT?*

WHAT IT IS AND IS NOT GIVEN, because §3's law is about seats and this is not a seat. The blind
SEAT is never given the bible: it must arrive at the register on its own or fail to. The
ADJUDICATOR is not reviewing an image — it is scoring an answer — so it is given the criterion it
scores against, in plain language, and never the bible, never the round, never which build, never
the family's name, and never the image. A scorer without a criterion is a coin.

⚠ IT DECIDES ROUND 10 ONWARD AND RE-SCORES NOTHING. Rounds 1-9 stand on the control that was in
force when they ran — including round 9, which is VOID by ruling and is not re-rolled. Running
this over past transcripts below is VALIDATION DATA, clearly labelled, and changes no verdict.

THE CONTROL'S OWN CONTROL (§13.5, and Rafe's *"until the control can catch its own plant"*):
the ten FAMILY transcripts on disk are the negative set. They were written about builds with no
collapse, no cobweb, no moss and no unanswered damage in them, so an adjudicator that reports
CAUGHT on a family transcript is reporting a ruin that is not there. It must return NOT CAUGHT on
all ten, and must be able to return CAUGHT at all. Both halves, or it is a coin again.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SEATS = os.path.join(HERE, "evidence", "seats")
WORK = ("/private/tmp/claude-501/-Users-rafehatfield-development-c-yarl/"
        "8ce8033c-4b4a-4de0-8e48-d9cfede08b85/scratchpad/adjudicator")

CRITERION = """You are scoring one reviewer's written report of a picture. You cannot see the
picture and you must not guess at it. Judge only what the reviewer WROTE.

THE PLACE the picture is from: an underworld that has been in continuous heavy use for longer than
anyone's records go back, held for four hundred years by a company of soldiers who repair things
endlessly and do not care how the repairs look. Its governing rule is this:

    NOTHING THERE IS RUINED. THINGS ARE USED UP.

Wear, scuffing, patina, things worn smooth or worn thin, repairs made badly and left — all of that
is correct and expected. What would be WRONG is the picturesque ruin: collapse, rubble spilling
out, cobwebs, moss or damp bloom, and above all DAMAGE THAT NOBODY ANSWERED — breakage sitting
un-repaired in a place whose garrison repairs everything.

YOUR QUESTION, and it is the only one:

    Did this reviewer report the standing structure as RUINED — broken, collapsed, cobwebbed,
    mossy, or damaged-and-never-repaired — and treat that as something WRONG with it?

It counts whatever words they used. It counts if they described the damage plainly and said it was
the wrong story for the place, or that nobody had repaired it. It does NOT count if they only
described wear, age, dirt, or being worn out; those are correct for this place. It does NOT count
if they merely disliked the picture, said it was too dark, said it was flat, said it was hard to
see, or complained about anything other than the structure being ruined.

Answer in exactly this form and nothing else:

VERDICT: CAUGHT
or
VERDICT: NOT CAUGHT

QUOTE: one sentence copied exactly from the report that decides it, or NONE.
WHY: one sentence in your own words.
"""

FIELDS = ("Q11", "Q8", "Q5", "Q3", "Q1", "CULL", "FLIP LIST")


def transcript_of(rec):
    """The reviewer's own words, with nothing that identifies the build or the round."""
    parts = []
    for k in FIELDS:
        v = rec["fields"].get(k)
        if v:
            parts.append("%s: %s" % (k, v.strip()))
    return "\n\n".join(parts) if parts else rec.get("transcript", "")


def adjudicate(text, timeout=900):
    os.makedirs(WORK, exist_ok=True)
    prompt = CRITERION + "\n\nTHE REPORT:\n\n" + text
    p = subprocess.run(["claude", "-p", prompt], cwd=WORK, capture_output=True,
                       text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    out = (p.stdout or "") + (p.stderr or "")
    m = re.search(r"VERDICT:\s*(NOT\s+CAUGHT|CAUGHT)", out, re.I)
    verdict = m.group(1).upper().replace("  ", " ") if m else None
    q = re.search(r"QUOTE:\s*(.+)", out)
    why = re.search(r"WHY:\s*(.+)", out)
    return dict(caught=(verdict == "CAUGHT") if verdict else None,
                verdict=verdict, quote=q.group(1).strip() if q else None,
                why=why.group(1).strip() if why else None, raw=out)


def load(pattern):
    out = []
    for p in sorted(glob.glob(os.path.join(SEATS, pattern))):
        try:
            out.append((os.path.basename(p), json.load(open(p))))
        except Exception:
            continue
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int)
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--validate-plants", action="store_true",
                    help="also run over past PLANT transcripts. Validation data only — it changes "
                         "no stored verdict, and round 9 stays VOID by ruling.")
    a = ap.parse_args()

    if a.round is not None:
        p = os.path.join(SEATS, "r%d_W2.json" % a.round)
        rec = json.load(open(p))
        r = adjudicate(transcript_of(rec))
        rec["adjudicator"] = {k: v for k, v in r.items() if k != "raw"}
        rec["caught"] = bool(r["caught"])
        rec["round_verdict"] = "VALID" if rec["caught"] else "VOID"
        json.dump(rec, open(p, "w"), indent=2)
        print("round %d plant -> %s\n  quote: %s\n  why:   %s"
              % (a.round, r["verdict"], r["quote"], r["why"]))
        return 0 if r["caught"] else 1

    if not a.controls:
        raise SystemExit("nothing to do: pass --controls or --round N")

    print("THE CONTROL'S OWN CONTROL — the family transcripts are the negative set.")
    print("They were written about builds with no ruin in them. A CAUGHT here is a ruin that is")
    print("not there, and the adjudicator would be as decorative as the grep it replaces.\n")
    fam = load("r*_W[134].json")
    bad = []
    for name, rec in fam:
        r = adjudicate(transcript_of(rec))
        flag = "" if r["caught"] is False else "   <-- FALSE POSITIVE"
        if r["caught"] is not False:
            bad.append(name)
        print("  %-14s %-12s %s%s" % (name, r["verdict"], (r["why"] or "")[:70], flag))

    res = dict(negative_set=len(fam), false_positives=bad)
    if a.validate_plants:
        print("\nVALIDATION DATA ONLY — past plant transcripts. NO STORED VERDICT CHANGES, and")
        print("round 9 is VOID by ruling and is not re-rolled.\n")
        pos = []
        for name, rec in load("r*_W2.json"):
            if "adjudicator" in rec:
                continue
            r = adjudicate(transcript_of(rec))
            pos.append((name, r["verdict"]))
            print("  %-14s ruled=%-7s adjudicator=%-12s %s"
                  % (name, "CAUGHT" if rec.get("caught") else "MISSED",
                     r["verdict"], (r["quote"] or "")[:60]))
        res["plants_validation"] = pos
        res["can_say_caught"] = any(v == "CAUGHT" for _, v in pos)

    ok = not bad and res.get("can_say_caught", None) is not False
    res["proven"] = bool(ok)
    json.dump(res, open(os.path.join(HERE, "evidence", "PLANT-ADJUDICATOR.json"), "w"), indent=2)
    print("\n  negative set: %d family transcripts, %d false positives" % (len(fam), len(bad)))
    if "can_say_caught" in res:
        print("  can it say CAUGHT at all: %s" % res["can_say_caught"])
    print("  VERDICT: %s" % ("the control discriminates — it is an instrument" if ok
                             else "NOT PROVEN — do not run round 10's seats on it"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
