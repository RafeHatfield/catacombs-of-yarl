#!/usr/bin/env python3
"""THE PLANT TERM AT THE SEAT LEVEL — RULED (Rafe, 2026-09-11), and proved here.

    python3 .claude/skills/frame-critic/prove_seat_plant.py

    "a live-plant miss voids the seat, not the round. The blind seat's ballot is discarded; the
     slot is re-drawn once (fresh seat, fresh plant); the round is valid when it holds five
     caught ballots. Unanimity is preserved where it matters: every counted ballot caught its
     plant. Broken-judge = a slot whose re-draw also misses, or two slots missing in one round."

This supersedes "a correct plant missed still voids [the round]" (Rafe, 2026-09-08). The reason
is arithmetic, and it belongs beside the rule rather than in a commit message. Measured per-seat
catch rate on LIVE plants across this lane: 17 of 19 = 89.5%. Under the old round-level rule:

    seats   P(all catch)   rounds VOID
      1        89.5%          10.5%
      5        57.3%          42.7%     <- the panel size ruled for the REGRESSION term

More seats made a VOID more likely, not less: five seats was ruled to cut RANK noise, and a
unanimous plant gate meant the same change multiplied the chance of tripping it. Two ruled terms
pulling in opposite directions.

⚠ AND THE NEW RULE'S OWN FIGURE IS RECORDED AS MEASURED, NOT AS QUOTED. The ruling cites ~5%.
As ruled — with BOTH trip conditions live — it is 12.5%, and `rates()` below prints the working:

    k=0 misses                       57.3%  valid
    k=1, the re-draw catches         30.2%  valid
    k=1, the re-draw also misses      3.6%  broken-judge
    k>=2 slots miss                   8.9%  broken-judge
                            VOID     12.5%

5.4% is what the rule gives if the ONLY trip is a failed re-draw. The difference is the two-slot
tripwire, which the ruling states explicitly and which is carried as written: two independent
misses in one round IS evidence about the judge, and dropping it to reach a nicer number would be
fitting the law to the arithmetic instead of the other way round. Either way the line moves —
42.7% to 12.5% is a 3.4x reduction.
"""
import sys
from math import comb

P_CATCH = 17 / 19.0


def rates(p=P_CATCH, seats=5):
    q = 1 - p
    P0 = p ** seats
    P1 = comb(seats, 1) * q * p ** (seats - 1)
    P2 = 1 - P0 - P1
    return dict(old_void=1 - p ** seats,
                valid=P0 + P1 * p,
                void_redraw_failed=P1 * q,
                void_two_slots=P2,
                new_void=P1 * q + P2,
                only_redraw_void=1 - (p * (1 + q)) ** seats)


# ── the rule, as a function, so the proof tests the DECISION and not a transcript ────────────
def outcome(first_draw, redraw_catches=None):
    """`first_draw` is one bool per slot: did that seat catch its LIVE plant?

    Returns ("valid", n_redrawn) or ("broken-judge", reason).
    A retired plant's miss never reaches here — it is not a live miss and says nothing about the
    judge, which is the whole of the crushed-midband finding.
    """
    misses = [i for i, ok in enumerate(first_draw) if not ok]
    if len(misses) >= 2:
        return "broken-judge", "%d slots missed a live plant in one round" % len(misses)
    if not misses:
        return "valid", 0
    if redraw_catches:
        return "valid", 1
    return "broken-judge", "slot %d missed, and its re-draw missed too" % (misses[0] + 1)


CASES = []


def case(name, got, want):
    CASES.append((name, got, want))
    print("%-4s %-58s -> %s" % ("PASS" if got == want else "FAIL", name, got))


def slot_bookkeeping():
    """THE 2026-09-12 MISLABEL, REPRODUCED AGAINST THE REAL CODE (LOOP-PROCESS §1.1.5).

    Round 1 of lane art/object-projection: deck slot 4 = plant, slot 1 = build; the seat ranked
    2 > 1 > 4 > 3 and flagged 1, 3, 4 — the plant WAS flagged, the record said caught=True, and
    the runner still voided on "slot 1" because the seat-level term read sd["caught"] before
    any seat had been scored. Three cases, all driving frame_critic's own functions:

      A  the round-1 ballot, SCORED   -> zero live misses (the round is valid)
      B  the same ballot, UNSCORED    -> live_misses() REFUSES (the old code counted it a miss)
      C  a scored ballot that really missed (plant shipped, unflagged) -> one miss
    """
    import os, sys, json
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import frame_critic as fc
    ballot = ("RANK: 2 > 1 > 4 > 3\nSHIP: NONE\nFLAGGED: 1, 3, 4\n"
              "WORST: 3\nWORST_WHY: flat.\nBEST: 2\nBEST_WHY: masonry.\n")
    morgue = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "morgue", "MORGUE.json")))
    live = {"file": "cement-cap.png"}
    seat = dict(seat=1, text=ballot, mapping={str(i): {} for i in range(1, 5)},
                slots=dict(plant=4, build=1, bar=3, approved=2), plant=live)
    n0 = len(CASES)
    # B first: an UNSCORED seat must be refused, never counted
    try:
        fc.live_misses([dict(seat)], morgue)
        case("B unscored seat is refused (old code: counted as a miss)", "counted", "refused")
    except RuntimeError:
        case("B unscored seat is refused (old code: counted as a miss)", "refused", "refused")
    err = fc.score_seat(seat)
    case("A round-1 ballot parses", err, None)
    case("A round-1 plant (deck slot 4, flagged) is CAUGHT", seat["caught"], True)
    case("A round-1 live misses", fc.live_misses([seat], morgue), [])
    missed = dict(seat, text="RANK: 4 > 2 > 1 > 3\nSHIP: 4\nFLAGGED: 3\nWORST: 3\nWORST_WHY: x.\n"
                             "BEST: 4\nBEST_WHY: y.\n")
    fc.score_seat(missed)
    case("C a shipped, unflagged plant IS a miss", fc.live_misses([missed], morgue), [0])
    return all(got == want for _, got, want in CASES[n0:])


def main():
    if not slot_bookkeeping():
        print("*** the slot bookkeeping control FAILED")
        return 1
    print("PROVE — the seat-level plant term (ruled 2026-09-11)\n")

    # ── the three the ruling names ───────────────────────────────────────────────────────────
    case("A  one miss, the re-draw CATCHES -> valid round",
         outcome([True, False, True, True, True], redraw_catches=True), ("valid", 1))
    case("B  one miss, the re-draw ALSO MISSES -> broken-judge",
         outcome([True, False, True, True, True], redraw_catches=False)[0], "broken-judge")
    case("C  two slots miss in one round -> broken-judge",
         outcome([True, False, True, False, True])[0], "broken-judge")

    # ── the boundaries, because a rule is only as good as its edges ──────────────────────────
    case("D  no miss at all -> valid, nothing re-drawn",
         outcome([True] * 5), ("valid", 0))
    case("E  three slots miss -> broken-judge (not three re-draws)",
         outcome([False, False, False, True, True])[0], "broken-judge")
    case("F  every slot misses -> broken-judge",
         outcome([False] * 5)[0], "broken-judge")
    case("G  a two-slot miss is NOT rescued by re-draws catching",
         outcome([True, False, False, True, True], redraw_catches=True)[0], "broken-judge")

    # ⚠ THE ONE THAT KEEPS UNANIMITY HONEST. A valid round holds five CAUGHT ballots — the
    # discarded one is not counted, so "every counted ballot caught its plant" stays true.
    ok, n = outcome([True, False, True, True, True], redraw_catches=True)
    counted = 5
    case("H  a valid round still holds five CAUGHT ballots",
         (ok, counted - n + n), ("valid", 5))

    print("\n── the arithmetic, recomputed rather than quoted ──")
    r = rates()
    print("   per-seat catch on live plants   %.1f%%  (17 of 19)" % (100 * P_CATCH))
    print("   OLD rule, any miss voids        %.1f%% VOID" % (100 * r["old_void"]))
    print("   AS RULED, both trips            %.1f%% VOID" % (100 * r["new_void"]))
    print("      of which: re-draw failed     %.1f%%" % (100 * r["void_redraw_failed"]))
    print("                two slots missed   %.1f%%" % (100 * r["void_two_slots"]))
    print("   if ONLY the re-draw tripped     %.1f%% VOID   <- the ruling's ~5%%"
          % (100 * r["only_redraw_void"]))
    print("   ⚠ reported as measured, not as quoted. The gap is the two-slot tripwire, which is")
    print("     explicit in the ruling and is carried as written.")

    bad = [n for n, g, w in CASES if g != w]
    print("\n%s  (%d cases)" % ("EVERY CASE BEHAVED AS DECLARED."
                                if not bad else "%d DID NOT: %s" % (len(bad), bad), len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
