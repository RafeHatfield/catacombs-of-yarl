#!/usr/bin/env python3
"""THE PANEL DECIDES BY VOTE, AND THE VOTE MUST BE ABLE TO REFUSE.

RULED (Rafe, 2026-09-08):

    "majority of three independent blind seats rank the build above approved_capture, no unrouted
     flags from any; each seat its own axis-matched plant."

    LAW: "a gate's binding term must have a measured noise floor and must never be a single
     sample."

§13.5 / LOOP-PROCESS §4 — a new gating rule's PASS counts for nothing until it has been shown to
fail. This drives `frame_critic.panel_verdict` itself, never a copy, so what is proved is what
runs.

THE ASYMMETRY IS THE THING BEING PROVED. Rank takes a majority because rank is the noisy term —
it flipped on identical bytes, which is why the panel exists at all. A FLAG does not: one seat
finding a defect is enough, because a flag outvoted 2-1 is still a defect two seats missed.
Cases D and E are that asymmetry, stated as two outcomes that differ only in which term dissents.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frame_critic as FC   # noqa: E402

FAILURES = []


def seat(above, flagged=False, shipped=False, caught=True):
    return dict(above_approved=above, build_flagged=flagged, shipped=shipped, caught=caught)


def case(name, seats, want, approved=True, beats=True, near=True):
    got = FC.panel_verdict(seats, approved, beats, near)
    ok = got == want
    n_above, n_flag, n_ship, all_caught, maj = FC.panel_tally(seats)
    print("\n%s %s" % ("PASS " if ok else "FAIL ", name))
    print("      %d seats | above %d | flagged %d | shipped %d | all caught %s | majority %s"
          % (len(seats), n_above, n_flag, n_ship, all_caught, maj))
    print("      -> %s (wanted %s)" % (got, want))
    if not ok:
        FAILURES.append(name)


def main():
    print("THE THREE-SEAT VOTE — driving frame_critic.panel_verdict\n")

    # ── rank takes a MAJORITY, because rank is the term that flipped ─────────────────────────
    case("A  3 of 3 above the reference, clean          -> PASS-INSTALL",
         [seat(True), seat(True), seat(True)], "PASS-INSTALL")
    case("B  2 of 3 above (one dissent)                 -> PASS-INSTALL",
         [seat(True), seat(True), seat(False)], "PASS-INSTALL")
    case("C  1 of 3 above — NO majority                 -> FAIL",
         [seat(True), seat(False), seat(False)], "FAIL")
    case("C2 0 of 3 above                               -> FAIL",
         [seat(False), seat(False), seat(False)], "FAIL")

    # ── a FLAG from ANY seat is disqualifying — the asymmetry, proved as a pair ──────────────
    case("D  3 of 3 above but ONE seat flags the build  -> FAIL",
         [seat(True), seat(True), seat(True, flagged=True)], "FAIL")
    case("E  the same panel with the flag withdrawn     -> PASS-INSTALL",
         [seat(True), seat(True), seat(True)], "PASS-INSTALL")

    # ── every seat must catch its plant; a panel does not average a soft seat away ───────────
    case("F  one seat MISSES its plant                  -> VOID",
         [seat(True), seat(True), seat(True, caught=False)], "VOID")
    case("G  a missed plant outranks everything else    -> VOID",
         [seat(True, flagged=True, caught=False), seat(True), seat(True)], "VOID")

    # ── the reference must exist, exactly as for one seat (§13.11's saturating comparator) ───
    case("H  no seeded reference in the deck            -> FAIL",
         [seat(True), seat(True), seat(True)], "FAIL", approved=False, beats=False)

    # ── SHIP is the wowed signal and still reaches the stronger state ────────────────────────
    case("I  a majority would SHIP it                   -> PASS",
         [seat(True, shipped=True), seat(True, shipped=True), seat(True)], "PASS")

    # ── and a single seat still behaves exactly as it did before the panel existed ───────────
    case("J  one seat, above, clean                     -> PASS-INSTALL",
         [seat(True)], "PASS-INSTALL")
    case("K  one seat, above, but it flags the build    -> FAIL",
         [seat(True, flagged=True)], "FAIL")

    print("\n%s" % ("=" * 70))
    if FAILURES:
        print("%d CASE(S) FAILED: %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("EVERY CASE BEHAVED AS DECLARED. The vote refuses on a lost majority, on any single")
    print("seat's flag, and on any missed plant — and it opens only when the panel agrees.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
