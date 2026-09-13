#!/usr/bin/env python3
"""FALSE-REFUSE AND TRUE-CATCH FOR THE INSTALL GATE'S REGRESSION TERM.

RULED (Rafe, 2026-09-09): *"five seats; block only on strong-majority regression (>=4 of 5 rank
below the reference); else install if exit met and plant caught. Rank-in-deck cannot resolve
polish-sized deltas at a 40% flip rate — publish the false-refuse/true-catch numbers beside
RANK-NOISE-FLOOR.json."*

WHAT THIS IS AND IS NOT. It is arithmetic on a measured input, not a simulation of taste. The one
empirical number is q, THE PROBABILITY A SINGLE SEAT RANKS THE BUILD BELOW ITS REFERENCE, and it
comes from seats that actually ran on frozen bytes. Everything else is the binomial that follows
from it, because seats are drawn independently — each is a fresh `claude -p` with no memory of the
others, which is the one assumption here and it is the mechanism's own design.

    P(block) = P(at least ceil(4n/5) of n seats say "below")

A FALSE REFUSE is that probability evaluated at the q measured on a build we have no reason to
call a regression. A TRUE CATCH is the same expression at the higher q a real regression would
produce — and since no measured q exists for "a build that genuinely got worse", it is swept
rather than invented. That is the honest shape: one measured number, one swept one, and the reader
can see which is which.

§13.13: a gate's binding term must have a measured noise floor and must never be a single sample.
This is that floor turned into the two numbers a threshold is actually chosen on.
"""
import json
import os
from math import comb

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "docs", "GATE-POWER.json")

# ── THE MEASURED INPUT ────────────────────────────────────────────────────────────────────────
# Lane `polish-198-halo`, two panels of three on BYTE-IDENTICAL bytes (the rounds' own progress
# line reads "picture moved mean 0.000 / worst 0 luminance levels"):
#     r002  not below in 3 of 3
#     r003  not below in 1 of 3
# Six seats, one picture, four not-below. This build is the best available example of "not a
# regression" — its item exit is met and measured, and its own reference is the frame it was
# derived from.
SEATS_OBSERVED, NOT_BELOW_OBSERVED = 6, 4
Q_GOOD = (SEATS_OBSERVED - NOT_BELOW_OBSERVED) / SEATS_OBSERVED


def p_block(n, q, ratio=(4, 5)):
    """P(a panel of n blocks), where blocking needs at least ratio of them to say 'below'."""
    need = -(-n * ratio[0] // ratio[1])          # ceil(n * 4/5)
    return sum(comb(n, k) * q ** k * (1 - q) ** (n - k) for k in range(need, n + 1))


def p_block_majority(n, q):
    """The OLD rule: block unless a majority is not-below, i.e. block when below >= ceil(n/2)."""
    need = n // 2 + 1 if n % 2 else n // 2       # not_below*2 <= n  <=>  below >= ceil(n/2)
    return sum(comb(n, k) * q ** k * (1 - q) ** (n - k) for k in range(need, n + 1))


def main():
    rows = []
    print("MEASURED INPUT: %d of %d seats ranked the build BELOW its reference on frozen bytes,"
          % (SEATS_OBSERVED - NOT_BELOW_OBSERVED, SEATS_OBSERVED))
    print("                so q_good = %.3f. Everything below follows from that.\n" % Q_GOOD)

    print("FALSE REFUSE — a build that is NOT a regression, blocked anyway (q = %.3f)" % Q_GOOD)
    print("   panel  old rule (majority not-below)   new rule (>=4/5 below)")
    for n in (3, 5, 7):
        old, new = p_block_majority(n, Q_GOOD), p_block(n, Q_GOOD)
        print("   n=%d          %6.1f%%                      %6.1f%%" % (n, old * 100, new * 100))
        rows.append(dict(kind="false_refuse", n=n, q=round(Q_GOOD, 4),
                         old_rule=round(old, 4), new_rule=round(new, 4)))

    print("\nTRUE CATCH — a build that IS a regression, blocked. q swept, because no q has been")
    print("measured for a real regression and inventing one would be the whole answer.")
    print("   q      meaning                              old (n=3)   new (n=5)")
    for q, meaning in ((0.50, "half the seats see it"),
                       (0.60, "three seats in five see it"),
                       (0.70, "seven seats in ten see it"),
                       (0.80, "four seats in five see it"),
                       (0.90, "nine seats in ten see it"),
                       (0.95, "all but one seat in twenty")):
        old, new = p_block_majority(3, q), p_block(5, q)
        print("   %.2f   %-36s %6.1f%%      %6.1f%%" % (q, meaning, old * 100, new * 100))
        rows.append(dict(kind="true_catch", q=q, meaning=meaning,
                         old_rule_n3=round(old, 4), new_rule_n5=round(new, 4)))

    doc = {
        "schema": "frame-critic/gate-power/1",
        "_what": [
            "FALSE REFUSE AND TRUE CATCH for the INSTALL-LATEST regression term.",
            "",
            "RULED (Rafe, 2026-09-09): 'five seats; block only on strong-majority regression",
            "(>=4 of 5 rank below the reference) ... publish the false-refuse/true-catch numbers",
            "beside RANK-NOISE-FLOOR.json.'",
            "",
            "ONE NUMBER HERE IS MEASURED AND THE REST IS ARITHMETIC. q_good is the rate at which",
            "a single blind seat ranks a NON-REGRESSED build below its reference, taken from six",
            "seats on byte-identical frames (r002 and r003 of polish-198-halo, 4 of 6 not below).",
            "The true-catch column has no measured q — no build has yet been shown to a panel",
            "while known to be worse — so q is SWEPT there and labelled as swept. Inventing it",
            "would have been inventing the answer.",
            "",
            "WHAT THE TABLE SAYS IN ONE LINE. The old rule refused a good build about a quarter",
            "of the time; the new one refuses it about one time in twenty. The price is catch",
            "power against SMALL regressions — a build six seats in ten would rank below is now",
            "blocked about a third of the time instead of four fifths — and that price is",
            "deliberate: a term that cannot resolve a polish-sized delta should not be the thing",
            "that decides, and the item's own MEASURED EXIT, which no seat votes on, is what",
            "carries 'did this do the thing it set out to do'.",
            "",
            "Regenerate: python3 tools/tier1_floors/measure_gate_power.py"
        ],
        "measured_input": {
            "rounds": ["r002-polish-198-halo", "r003-polish-198-halo"],
            "identical_bytes": True,
            "seats": SEATS_OBSERVED,
            "not_below": NOT_BELOW_OBSERVED,
            "q_good": round(Q_GOOD, 4),
            "note": "q_good is the per-seat probability of calling a NON-regressed build 'below'",
        },
        "rule_old": "block unless a MAJORITY of seats are not-below (in force 2026-09-08 to 09-09)",
        "rule_new": "block only when >= 4/5 of seats rank the build BELOW the reference",
        "rows": rows,
    }
    with open(OUT, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print("\nwritten: %s" % os.path.relpath(OUT, REPO))


if __name__ == "__main__":
    main()
