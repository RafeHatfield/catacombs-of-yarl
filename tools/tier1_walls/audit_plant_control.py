#!/usr/bin/env python3
"""IS THE PLANT CONTROL A CONTROL? — and the answer is no, in both directions at once.

    python3 tools/tier1_walls/audit_plant_control.py

LOOP-PROCESS §4 makes the plant seat the thing that decides whether a round's findings are read
at all. Nine rounds have been ruled by it. This asks the question §13.5 asks of every other
instrument in this directory — *has it demonstrated it can fail, and can it also pass?* — of the
one instrument nobody pointed it at.

`plant_caught()` greps the plant seat's answers for a fixed vocabulary. That is a substring match
standing in for a judgement about REGISTER: bible §8.1 holds that nothing in the Paths is ruined
and everything is used up, and the plant is the drama — collapse, cobweb, moss and a forked crack.
Whether a seat NAMED that is a semantic question.

TWO FAILURES, and they point opposite ways:

  IT CERTIFIES ON TERMS THE FAMILY SHARES. §4.1 is already written into `plant_caught`'s own
  docstring — *a cull whose reason the family shares has not discriminated between the arm and the
  plant.* The same is true of the naming terms, and nine of them appear in FAMILY transcripts.

  IT SCORES MISSED ON SEATS THAT NAMED THE RUIN. `plant_walls.ruin()` has drawn A FORKED CRACK
  since it was written; the vocabulary has no crack term of any kind.

AND THERE IS NO VOCABULARY THAT FIXES IT. Add the crack terms and every previously-void round
"catches", mostly on `crack` — which the family authors too (`compose_cap.field_cracks`). Remove
every family-shared term and what is left is arbitrary: `fracture` survives and `crack` does not,
on a ten-transcript sample, though they mean the same thing.

THIS SCRIPT CHANGES NOTHING AND RE-SCORES NOTHING. `run_seats.py` still carries the vocabulary
that ruled rounds 1-9, because re-scoring them with a list chosen after reading their transcripts
is the laundering §4 exists to prevent. The output below is a finding for the design thread.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import run_seats as RS          # noqa: E402

SEATS = os.path.join(HERE, "evidence", "seats")
FIELDS = ("Q11", "Q8", "Q5", "Q3", "Q1", "CULL")

# What `plant_walls.ruin()` actually draws, read off its own section headings.
DRAWN = ("A COLLAPSED COURSE", "COBWEB in the corners", "MOSS:", "A FORKED CRACK")
# Terms that would cover the crack, if a vocabulary could.
CRACK_TERMS = ("crack", "cracked", "fracture", "fissure", "split")


def blob(rec):
    return " ".join(rec["fields"].get(k, "") for k in FIELDS).lower()


def load(pattern):
    out = []
    for p in sorted(glob.glob(os.path.join(SEATS, pattern))):
        try:
            out.append((os.path.basename(p), json.load(open(p))))
        except Exception:
            continue
    return out


def main():
    plants = load("r*_W2.json")
    family = load("r*_W[134].json")
    if not plants:
        raise SystemExit("no plant seats on disk")

    print("THE PLANT CONTROL, AUDITED — %d plant seats, %d family seats\n"
          % (len(plants), len(family)))

    print("1. COVERAGE — does the vocabulary name what the plant DRAWS?")
    src = open(os.path.join(HERE, "plant_walls.py")).read()
    for marker in DRAWN:
        present = marker in src
        covered = marker != "A FORKED CRACK" or any(t in RS.RUIN_WORDS for t in CRACK_TERMS)
        print("   %-24s drawn=%-5s  vocabulary covers it=%s%s"
              % (marker, present, covered, "" if covered else "   <-- NO TERM AT ALL"))

    print("\n2. DISCRIMINATION — do its terms appear in FAMILY transcripts?")
    fb = [blob(r) for _, r in family]
    shared = []
    for t in RS.RUIN_WORDS:
        n = sum(1 for b in fb if t in b)
        if n:
            shared.append((t, n))
    for t, n in sorted(shared, key=lambda x: -x[1]):
        print("   %-24s fires on %d of %d family transcripts" % (t, n, len(fb)))
    print("   -> %d of %d terms do not discriminate plant from family."
          % (len(shared), len(RS.RUIN_WORDS)))

    print("\n3. WHAT EACH ROUND'S VERDICT ACTUALLY RESTED ON")
    print("   round  verdict   terms matched            of those, family-shared")
    sharedset = {t for t, _ in shared}
    for name, rec in plants:
        r = rec.get("round")
        b = blob(rec)
        hit = [t for t in RS.RUIN_WORDS if t in b]
        sh = [t for t in hit if t in sharedset]
        print("   %5s  %-8s  %-24s %s"
              % (r, "CAUGHT" if rec.get("caught") else "MISSED",
                 ",".join(hit)[:24] or "-", ",".join(sh) or "-"))

    print("\n4. THE TWO REPAIRS THAT DO NOT WORK")
    wide = tuple(RS.RUIN_WORDS) + CRACK_TERMS
    narrow = tuple(t for t in RS.RUIN_WORDS if t not in sharedset)
    print("   round  as ruled   +crack terms   family-shared removed")
    for name, rec in plants:
        b = blob(rec)
        print("   %5s  %-9s  %-13s  %s"
              % (rec.get("round"), "CAUGHT" if rec.get("caught") else "MISSED",
                 "CAUGHT" if any(t in b for t in wide) else "MISSED",
                 "CAUGHT" if any(t in b for t in narrow) else "MISSED"))
    print("\n   Widening greens rounds that were ruled VOID. Narrowing flips a round that was")
    print("   ruled VALID. Neither is a control; both are a vocabulary chosen after the fact.")

    print("\nVERDICT: the plant control is NOT an instrument under §13.5. It has never been shown")
    print("         to fail on a seat that missed the ruin, or to pass only on one that caught it.")
    print("         Replacing it is a change to the loop's structure — a judgement, not a grep.")


if __name__ == "__main__":
    main()
