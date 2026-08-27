#!/usr/bin/env python3
"""THE FINAL TABLE for the parent ring-rate run — derived, never hand-copied.

Every number in REPORT-PARENT-RATE.md comes out of this file. The rule it exists to enforce is
the one the remediation session already learned twice: a figure typed into prose by hand has
lost its link to the evidence, and a rescored bar is the moment that link matters most.

THREE RATES, REPORTED SEPARATELY AND NEVER MERGED
-------------------------------------------------
  instrument   `ring_instrument.py`'s mechanical verdict over all 20. This is the headline and
               it is A FLOOR: REPORT §6 measured that the instrument does not catch every
               construction a human calls a keyline, so this number can only be too LOW.
  seat-adjusted a child is counted ringed if the instrument called it RING **or** the blind seat
               culled it `keyline`. Only the borderline children went to a seat, and the triage
               cut sits below the published overlap band, so this is the honest UPPER bound on
               what the instrument missed - not a revision of the instrument's number.
  B-KAB        the published comparison, quoted from REPORT §4 and regen_bkab/RESULT.json.

The exact one-sided Fisher test is computed here rather than asserted, because REPORT §4's own
reasoning turned on whether a difference was real at n=8 ("one in eight is not a difference").
"""
import json
import os
import sys
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RUN = os.path.join(HERE, "parent_rate_cgab", "RESULT.json")
SEAT = os.path.join(HERE, "evidence", "child_seat")
CELL_ROUND = {"P": "CP", "S": "CS"}


def fisher_less(a, n1, b, n2):
    """One-sided P(X <= a) for group 1's ringed count, hypergeometric. No scipy."""
    N, K = n1 + n2, a + b
    return sum(comb(K, x) * comb(N - K, n1 - x) / comb(N, n1)
               for x in range(0, a + 1) if 0 <= n1 - x <= N - K)


def load_seat(cell):
    p = os.path.join(SEAT, "round%s_result.json" % CELL_ROUND[cell])
    return json.load(open(p)) if os.path.exists(p) else None


def main():
    res = json.load(open(RUN))
    rs = [r for r in res["results"] if r.get("verdict") in ("RING", "CLEAN")]
    b = res["compare_against"]

    print("PARENT RING-RATE — C-GAB (RULED primary style parent) — FINAL TABLE")
    print("  parent sha %s   instrument %s   near-ring %.3f"
          % (res["parent_sha256"][:16], res["parent_verdict"], res["parent_near_ring"]))
    print("  spent %d of %d   pool %s -> %s   levers: style_strength=%d, ring refusal %s"
          % (res["spent"], res["budget"], res["pool_before"], res["pool_after"],
             res["style_strength"], "ADDED" if res["ring_refusal_added"] else "NOT added"))

    print("\n  THE PAYLOAD DIFF vs the B-KAB run — the caveat, exact")
    for cell, d in res["payload_diff_vs_bkab"].items():
        print("    cell %s (%s): %s" % (cell, d["arm"],
                                        d["differing_keys"] or "NOTHING but the reference image"))

    seats, adj_total, adj_n = {}, 0, 0
    print("\n  PER CELL")
    for cell in ("P", "S"):
        cs = [r for r in rs if r["cell"] == cell]
        if not cs:
            continue
        ring = [r for r in cs if r["verdict"] == "RING"]
        s = load_seat(cell)
        seats[cell] = s
        extra, void, seen = [], None, 0
        if s:
            void = s["round_void"]
            keyl = set(s["children_keylined"])
            seen = len(s["children"])
            extra = [r for r in cs if r["verdict"] == "CLEAN"
                     and "%s_%s" % (cell, os.path.basename(r["file"])[:-4]) in keyl]
        adj = len(ring) + len(extra)
        adj_total += adj
        adj_n += len(cs)
        print("    cell %s (%s)" % (cell, res["payload_diff_vs_bkab"][cell]["arm"]))
        print("      instrument      %d of %d ringed" % (len(ring), len(cs)))
        if s is None:
            print("      seat            NOT RUN")
        elif void:
            print("      seat            ROUND VOID — the plant was not culled; no seat number")
        else:
            print("      seat            %d of %d borderline culled `keyline` "
                  "(of %d shown, incl. controls)"
                  % (len(extra), sum(1 for r in cs if r["verdict"] == "CLEAN"
                                     and r["near_ring"] >= res["seat_triage_at"]), seen))
            print("      seat-adjusted   %d of %d ringed" % (adj, len(cs)))
            print("      controls        plant %s   parent cull=%s"
                  % ("CAUGHT" if s["plant_caught"] else "MISSED", s["parent_cull"] or "none"))

    ring_all = sum(1 for r in rs if r["verdict"] == "RING")
    print("\n  POOLED")
    print("    instrument      %d of %d ringed" % (ring_all, len(rs)))
    valid = all(s and not s["round_void"] for s in seats.values()) and len(seats) == 2
    if valid:
        print("    seat-adjusted   %d of %d ringed" % (adj_total, adj_n))

    print("\n  AGAINST THE B-KAB RUN (%s)" % b["source"])
    rows = [("B-KAB pooled, mixed levers", b["pooled_ringed"], b["pooled_n"], None),
            ("B-KAB wave 1, THESE levers", b["wave1_ringed"], b["wave1_n"], None),
            ("C-GAB cell P, instrument", sum(1 for r in rs if r["cell"] == "P"
                                             and r["verdict"] == "RING"),
             sum(1 for r in rs if r["cell"] == "P"), "wave1"),
            ("C-GAB pooled, instrument", ring_all, len(rs), "wave1")]
    if valid:
        rows.append(("C-GAB pooled, seat-adjusted", adj_total, adj_n, "wave1"))
    for label, a, n, cmp in rows:
        p = ""
        if cmp == "wave1":
            p = "   vs wave 1: p = %.5g   vs pooled: p = %.5g" % (
                fisher_less(a, n, b["wave1_ringed"], b["wave1_n"]),
                fisher_less(a, n, b["pooled_ringed"], b["pooled_n"]))
        print("    %-30s %2d of %2d%s" % (label, a, n, p))

    pc = sum(1 for r in rs if r["cell"] == "P" and r["verdict"] == "RING")
    sc = sum(1 for r in rs if r["cell"] == "S" and r["verdict"] == "RING")
    lo, hi = sorted((pc, sc))
    print("\n  THE ARM-BLOCK CONFOUND, TESTED WITHIN THIS RUN")
    print("    cell P %d/10 vs cell S %d/10   p = %.4g" % (pc, sc, fisher_less(lo, 10, hi, 10)))
    print("    The cells differ only in the arm block. A p at or near 0.5 means the arm block")
    print("    is not doing the work, and cell S's structure-match corroborates cell P rather")
    print("    than competing with it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
