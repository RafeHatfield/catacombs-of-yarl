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


def seat(above, flagged=False, shipped=False, caught=True, not_below=None):
    """A seat's ballot. `not_below` defaults to `above` — a seat that ranks the build above the
    reference is trivially not below it — so the older cases keep meaning what they meant."""
    return dict(above_approved=above, not_below=above if not_below is None else not_below,
                build_flagged=flagged, shipped=shipped, caught=caught)


def case(name, seats, want, approved=True, beats=True, near=True, exit_met=True):
    got = FC.panel_verdict(seats, approved, beats, near, exit_met)
    ok = got == want
    t = FC.panel_tally(seats)
    print("\n%s %s" % ("PASS " if ok else "FAIL ", name))
    print("      %d seats | above %d | not-below %d | flagged %d | shipped %d | caught %s"
          % (t["n"], t["above"], t["not_below"], t["flagged"], t["shipped"], t["all_caught"]))
    print("      -> %s (wanted %s)" % (got, want))
    if not ok:
        FAILURES.append(name)


def main():
    print("THE PANEL VOTE — driving frame_critic.panel_verdict\n")

    # ── THE REGRESSION TERM — RULED (Rafe, 2026-09-09) ───────────────────────────────────────
    #
    #     "five seats; block only on strong-majority regression (>=4 of 5 rank below the
    #      reference); else install if exit met and plant caught. Rank-in-deck cannot resolve
    #      polish-sized deltas at a 40% flip rate."
    #
    # ⚠ THREE CASES BELOW CHANGED THEIR EXPECTED ANSWER, AND THAT IS A RULING RATHER THAN A
    # WEAKENING SLIPPED PAST A PROOF. They are kept and re-stated with the old expectation named,
    # so the diff shows exactly what moved and on whose word. What did NOT move: every plant must
    # be caught, the exit must be met, and a FLAG still blocks the install — that term now lives
    # only at `critic_gate`, where it was always enforced, and `prove_gate` K6/K10 hold it there.
    # A term is not proved by the file that used to hold it.
    case("A  5 of 5 above the reference, clean          -> INSTALL-LATEST",
         [seat(True)] * 5, "INSTALL-LATEST")

    # the ruling's own arithmetic, at the size it was ruled for
    case("B1 4 of 5 BELOW — strong majority            -> FAIL",
         [seat(False, not_below=False)] * 4 + [seat(True)], "FAIL")
    case("B2 3 of 5 below — not strong, it installs    -> INSTALL-LATEST",
         [seat(False, not_below=False)] * 3 + [seat(True), seat(True)], "INSTALL-LATEST")
    case("B3 5 of 5 below — unanimous                  -> FAIL",
         [seat(False, not_below=False)] * 5, "FAIL")

    # the SAME standard at other panel sizes: four FIFTHS, never the number four
    case("C  2 of 3 below (was FAIL until 2026-09-09)  -> INSTALL-LATEST",
         [seat(True), seat(False, not_below=False), seat(False, not_below=False)],
         "INSTALL-LATEST")
    case("C2 3 of 3 below — unanimous at n=3           -> FAIL",
         [seat(False, not_below=False)] * 3, "FAIL")
    case("C3 tied (one place under) is NOT below       -> INSTALL-LATEST",
         [seat(True)] + [seat(False, not_below=True)] * 4, "INSTALL-LATEST")
    case("C4 the same panel with the exit NOT met      -> FAIL",
         [seat(True)] + [seat(False, not_below=True)] * 4, "FAIL", exit_met=False)

    # ── A FLAG NO LONGER FORCES FAIL AT ROUND TIME. It blocks at the gate, and only there ────
    #
    # The pair it would be dangerous to leave unstated. The flag term did not go away; it stopped
    # being evaluated twice. `critic_gate` refuses any install whose flagged build carries no
    # lawful disposition (prove_gate K6) and accepts it when every item does (prove_gate K10).
    # If those two ever go green together, this pair means nothing and the guard is gone.
    case("D  5 of 5 above, ONE seat flags it           -> INSTALL-LATEST (the gate holds it)",
         [seat(True)] * 4 + [seat(True, flagged=True)], "INSTALL-LATEST")
    case("E  the same panel with the flag withdrawn    -> INSTALL-LATEST",
         [seat(True)] * 5, "INSTALL-LATEST")

    # ── every seat must catch its plant; a panel does not average a soft seat away ───────────
    case("F  one seat MISSES its plant                 -> VOID",
         [seat(True)] * 4 + [seat(True, caught=False)], "VOID")
    case("G  a missed plant outranks everything else   -> VOID",
         [seat(False, flagged=True, caught=False)] + [seat(False, not_below=False)] * 4, "VOID")

    # ── the reference must exist (§13.11's saturating comparator) ────────────────────────────
    case("H  no seeded reference in the deck           -> FAIL",
         [seat(True)] * 5, "FAIL", approved=False, beats=False)

    # ── SHIP is the wowed signal and still reaches the stronger state ────────────────────────
    case("I  a majority would SHIP it                  -> PASS",
         [seat(True, shipped=True)] * 3 + [seat(True), seat(True)], "PASS")

    # ── one seat still behaves as one seat: four fifths of 1 is 1 ────────────────────────────
    case("J  one seat, above, clean                    -> INSTALL-LATEST",
         [seat(True)], "INSTALL-LATEST")
    case("K  one seat, and it ranks the build BELOW    -> FAIL",
         [seat(False, not_below=False)], "FAIL")

    print("\n%s" % ("=" * 70))
    if FAILURES:
        print("%d CASE(S) FAILED: %s" % (len(FAILURES), ", ".join(FAILURES)))
        return 1
    print("EVERY CASE BEHAVED AS DECLARED. The vote refuses on a STRONG-MAJORITY regression and")
    print("on any missed plant. The flag term now lives at the gate — prove_gate K6 and K10 are")
    print("the other half of this rule, and neither half proves it alone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
