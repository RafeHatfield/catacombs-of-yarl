#!/usr/bin/env python3
"""THE STALL GUARD AT THE CEILING — it must still fire, and it must stop firing on progress.

RULED (Rafe, 2026-09-07), bible §13.11's second instance. `rank_score` is
`(deck_size - position) / (deck_size - 1)`, so first place in a three-frame deck is **1.00 and
there is nothing above it**. The guard demanded a NEW best and counted matching as standing
still, so **any lane that ever ranked first was guaranteed to STOP three readable rounds later,
however good the work was.** The metric saturated. A saturated instrument stops measuring the
thing and starts measuring the ceiling.

Progress is now a tuple — `(rank_score, shipped, -unresolved_flips)` — and this proves the two
directions that matter, because either one alone is worthless:

  a lane at rank 1 with SHRINKING unresolved flips   must NOT stall   (else the fix did nothing)
  a lane at rank 1 with STATIC flips                 must STALL       (else it is not a guard)

The second is the one that keeps this honest. A "fix" that simply stopped the guard firing at the
ceiling would pass the first case and quietly delete the check — which is the same failure shape
as a park marker that silences a guard rather than clearing named history.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frame_critic as FC  # noqa: E402

LANE = "stalllane"


# ⚠ EACH ROUND'S FLIPS MUST SHARE NO CONTENT WORDS WITH ANOTHER ROUND'S. `same_flip` matches on
# word overlap so a rephrased request still counts as a repeat, which is right — and it means a
# lazy fixture ("flip 1-0", "flip 2-0") reduces to the single word "flip" and every round reads as
# a THRASH. The first version of this control did exactly that and returned `thrash` six times.
# Distinct vocabulary per round isolates the guard under test.
VOCAB = {
    1: "masonry joints dissolve into gradient",
    2: "sprite outline saturated cyan repaint",
    3: "void carries flat empty information",
    4: "timber pins repair vocabulary absent",
    5: "crack terminates arbitrary corner midtile",
}


def verdict(rnd, score, flips, ship=None, sig=None):
    return {
        "schema": 1, "lane": LANE, "round": rnd, "verdict": "FAIL",
        "timestamp": "2026-09-07T00:%02d:00" % rnd,
        "build_frame": {"sha256": (sig or chr(97 + rnd)) * 64},
        "plant": {"caught": True},
        "seat": {"ship": ship},
        "progress": {"rank_score": score, "capture_signature": (sig or chr(97 + rnd)) * 64},
        "flip_list": ["%s %s" % (VOCAB[rnd], "abcdefghijklm"[i] * 6) for i in range(flips)],
    }


def run(tmp, verdicts, rulings=None):
    hd = os.path.join(tmp, "h")
    os.makedirs(hd, exist_ok=True)
    for f in os.listdir(hd):
        os.remove(os.path.join(hd, f))
    for v in verdicts:
        json.dump(v, open(os.path.join(hd, "r%03d.json" % v["round"]), "w"))
    gp = os.path.join(tmp, "gate.json")
    json.dump({"rulings": rulings or []}, open(gp, "w"))
    name, _ = FC.guards(FC.history(hd), LANE, os.path.join(tmp, "none.json"), gp)
    return name


def main():
    # Five rounds all at the ceiling. Only the flip counts differ between the two lanes.
    shrinking = [verdict(r, 1.0, 12 - r) for r in range(1, 6)]      # 11,10,9,8,7
    static = [verdict(r, 1.0, 8) for r in range(1, 6)]              # 8,8,8,8,8
    # ship arriving at the ceiling, flips static — SHIP alone must count as progress
    shipped = [verdict(r, 1.0, 8) for r in range(1, 5)] + [verdict(5, 1.0, 8, ship=["combined"])]
    # routed: flips static in the SEAT's list, but a gate ruling resolves them
    routed_v = [verdict(r, 1.0, 8) for r in range(1, 6)]
    routed_r = [{"lane": LANE, "round": r, "unresolved_flips": 10 - r} for r in range(1, 6)]
    # a round excluded from THIS guard cannot set its best: round 1 sets an unbeatable 1.00/0
    # unresolved, the rest are worse; cleared, the lane is judged on rounds 2-5 alone
    ceiling = [verdict(1, 1.0, 0)] + [verdict(r, 1.0, 9 - r) for r in range(2, 6)]

    cases = [
        ("C1  rank 1, SHRINKING unresolved flips ", shrinking, None,     None),
        ("C2  rank 1, STATIC flips               ", static,    None,     "stall"),
        ("C3  rank 1, static flips, SHIP arrives ", shipped,   None,     None),
        ("C4  rank 1, static list, ROUTED        ", routed_v,  routed_r, None),
        ("C5  an unbeatable round, NOT cleared   ", ceiling,   None,     "stall"),
    ]

    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        print("PROGRESS AT THE CEILING — the guard must stop firing on progress, and must still fire\n")
        print("  case                                     expected   got")
        for label, vs, rl, expect in cases:
            got = run(tmp, vs, rl)
            good = got == expect
            ok &= good
            print("  %s  %-10s %-10s %s" % (label, expect or "(none)", got or "(none)",
                                            "ok" if good else "FAIL"))

        # C6 is C5 with the unbeatable round CLEARED for stall — it must stop holding the record.
        gp = os.path.join(tmp, "gate.json")
        json.dump({"rulings": []}, open(gp, "w"))
        pk = os.path.join(tmp, "park.json")
        json.dump({"lane": LANE, "guard": "stall", "rounds_covered": [1], "ruling": "fixture"},
                  open(pk, "w"))
        hd = os.path.join(tmp, "h")
        for f in os.listdir(hd):
            os.remove(os.path.join(hd, f))
        for v in ceiling:
            json.dump(v, open(os.path.join(hd, "r%03d.json" % v["round"]), "w"))
        got, _ = FC.guards(FC.history(hd), LANE, pk, gp)
        good = got is None
        ok &= good
        print("  C6  the same, round 1 CLEARED for stall    %-10s %-10s %s"
              % ("(none)", got or "(none)", "ok" if good else "FAIL"))

    print()
    if ok:
        print("PASS — C2 and C5 are the ones that keep it a guard: a lane that is not moving still")
        print("stops. C6 is the second half of the ruling: a cleared round does not hold a record.")
        return 0
    print("FAIL — do not ship this.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
