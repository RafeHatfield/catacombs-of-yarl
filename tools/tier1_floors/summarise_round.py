#!/usr/bin/env python3
"""Write a round's SEATS-r<N>.json from the transcripts on disk.

Needed because a round can end without its runner finishing: round 2 was stopped after its
verdict and its plant control were both in, so that the remaining two seats did not spend their
wall-clock judging a family the flip list had already superseded (LOOP-PROCESS §1.1.2 — a critic
FAIL is a reprompt, not a stop). The transcripts are the evidence; this reconstructs the summary
from them rather than leaving the round without one.

Every seat that RAN is recorded, and the seats that did not are named as not-run rather than
omitted — a round whose summary quietly lists two seats when four were declared is a round
reporting its own convenience.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import run_seats as RS      # noqa: E402

OUT = os.path.join(HERE, "evidence", "seats")


def main():
    rnd = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    declared = ["F1", "F2", "F3", "F4"]
    seats, void, ran = {}, False, []
    for seat in declared:
        tp = os.path.join(OUT, "r%d_%s_transcript.txt" % (rnd, seat))
        if not os.path.exists(tp):
            seats[seat] = dict(status="NOT RUN — round stopped after the verdict and the plant "
                                      "control were both in; the flip list had already "
                                      "superseded the arm these would have judged")
            continue
        ran.append(seat)
        text = open(tp).read()
        r = RS.parse(text)
        r["transcript"] = os.path.relpath(tp, REPO)
        if seat == RS.PLANT_SEAT:
            caught, hit, culled = RS.plant_caught(r, text)
            r["plant_caught"] = caught
            r["plant_words_hit"] = hit
            r["culled"] = culled
            if not caught:
                void = True
        r.pop("flips", None) or None
        r["flips"] = RS.parse(text)["flips"]
        seats[seat] = r

    res = dict(round=rnd, commit=RS.git_commit(), seats=seats, seats_run=ran,
               seats_declared=declared, plant_seat=RS.PLANT_SEAT, round_void=void,
               plant_words_declared=list(RS.PLANT_WORDS),
               law=("LOOP-PROCESS §4: if the critic does not catch the plant, the round is VOID "
                    "and its findings are not read."))
    p = os.path.join(OUT, "SEATS-r%d.json" % rnd)
    with open(p, "w") as f:
        json.dump(res, f, indent=1)
    print("round %d: seats run %s   VOID=%s" % (rnd, ", ".join(ran), void))
    for seat in ran:
        r = seats[seat]
        tag = "  <- PLANT" if seat == RS.PLANT_SEAT else ""
        print("  %s%s" % (seat, tag))
        print("     CULL: %s" % (r.get("CULL") or "(none)")[:110])
        if seat == RS.PLANT_SEAT:
            print("     plant_caught=%s  hits=%s" % (r.get("plant_caught"), r.get("plant_words_hit")))
        for fx in r.get("flips", [])[:6]:
            print("     flip: %s" % fx[:106])
    print("\nwritten: %s" % os.path.relpath(p, REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
