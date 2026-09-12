#!/usr/bin/env python3
"""THE BROKEN-JUDGE CLEARANCE MUST BE SHOWN TO FAIL — §13.5, and it is the riskiest clear here.

    python3 .claude/skills/frame-critic/prove_judge_clear.py

A clearance that clears whatever it is pointed at is not a clearance, it is an off switch. The
2026-09-06 law — *a proven-blind judge is never laundered by a park* — is what this must not
become, so the guard re-derives the clearance's premise from the history instead of trusting the
marker. These cases are that property, stated as behaviour.

The one that matters most is C: a marker naming a round in which a LIVE plant was missed clears
nothing, however well-formed it is and whoever signed it.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frame_critic as FC  # noqa: E402

LANE = "clearlane"
RULING = "STOP cleared by ruling: the judge is proven working on two tonal plants at 100%."


def void(rnd, misses):
    """A VOID round. `misses` is a list of (seat_caught, plant_file)."""
    return {
        "schema": 1, "lane": LANE, "round": rnd, "verdict": "VOID",
        "timestamp": "2026-09-11T00:%02d:00" % rnd,
        "build_frame": {"sha256": chr(97 + rnd) * 64},
        "plant": {"caught": False},
        "progress": {"rank_score": 0.5, "capture_signature": chr(97 + rnd) * 64},
        "panel": {"per_seat": [{"caught": c, "plant": p} for c, p in misses]},
    }


def ok(rnd):
    return {
        "schema": 1, "lane": LANE, "round": rnd, "verdict": "INSTALL-LATEST",
        "timestamp": "2026-09-11T00:%02d:00" % rnd,
        "build_frame": {"sha256": chr(97 + rnd) * 64},
        "plant": {"caught": True},
        "progress": {"rank_score": 0.9, "capture_signature": chr(97 + rnd) * 64},
        "panel": {"per_seat": [{"caught": True, "plant": "live.png"}]},
    }


MORGUE_RETIRED = {"entries": [
    {"file": "retired.png", "retired_as_control": {"why": "measured, not a control"}},
    {"file": "live.png"},
]}


def guard_with(tmp, verdicts, marker, morgue=MORGUE_RETIRED):
    hd = os.path.join(tmp, "h")
    os.makedirs(hd, exist_ok=True)
    for f in os.listdir(hd):
        os.remove(os.path.join(hd, f))
    for v in verdicts:
        json.dump(v, open(os.path.join(hd, "r%03d.json" % v["round"]), "w"))
    jc = os.path.join(tmp, "JUDGE-CLEARED.json")
    if marker is None:
        if os.path.exists(jc):
            os.remove(jc)
    else:
        json.dump(marker, open(jc, "w"))
    real_jc, real_morgue = FC.JUDGE_CLEAR, FC._morgue_for_clear
    FC.JUDGE_CLEAR = jc
    FC._morgue_for_clear = lambda: morgue
    try:
        name, _ = FC.guards(FC.history(hd), LANE,
                            os.path.join(tmp, "none.json"), os.path.join(tmp, "g.json"))
    finally:
        FC.JUDGE_CLEAR, FC._morgue_for_clear = real_jc, real_morgue
    return name


CASES = []


def case(name, got, want):
    CASES.append((name, got, want))
    print("%-4s %-62s guard=%s" % ("PASS" if got == want else "FAIL", name, got))


def main():
    print("PROVE — the broken-judge clearance, and that it can fail (§13.5)\n")
    tmp = tempfile.mkdtemp(prefix="judgeclear-")

    # round 3 missed a RETIRED plant; round 4 missed a RETIRED plant. Both excusable.
    retired_both = [ok(1), ok(2),
                    void(3, [(True, "live.png"), (False, "retired.png")]),
                    void(4, [(False, "retired.png")])]
    # round 3 missed a LIVE plant; round 4 missed the retired one. Only 4 is excusable.
    mixed = [ok(1), ok(2),
             void(3, [(False, "live.png")]),
             void(4, [(False, "retired.png")])]

    mk = lambda rounds, lane=LANE, ruling=RULING: [
        {"lane": lane, "guard": "broken-judge", "rounds_covered": rounds, "ruling": ruling}]

    case("A  two VOIDs, NO marker -> the guard fires",
         guard_with(tmp, retired_both, None), "broken-judge")
    case("B  marker covering both, both misses retired -> cleared",
         guard_with(tmp, retired_both, mk([3, 4])), None)
    case("C  marker covering a round whose miss was a LIVE plant -> clears NOTHING",
         guard_with(tmp, mixed, mk([3, 4])), "broken-judge")
    case("D  marker covering only the retired round -> cleared, and that is enough",
         guard_with(tmp, mixed, mk([4])), None)
    case("E  marker with no quoted ruling -> clears nothing",
         guard_with(tmp, retired_both, mk([3, 4], ruling="")), "broken-judge")
    case("F  marker for a different lane -> clears nothing",
         guard_with(tmp, retired_both, mk([3, 4], lane="otherlane")), "broken-judge")
    case("G  malformed marker -> clears nothing",
         guard_with(tmp, retired_both, {"nonsense": True}), "broken-judge")
    case("H  nothing is retired in the morgue -> clears nothing",
         guard_with(tmp, retired_both, mk([3, 4]), morgue={"entries": []}), "broken-judge")

    # ── THE TRANSITIONAL CLAUSE, which is a second escape hatch and needs its own failures ──
    #
    # A marker carrying `supersedes` may excuse a round voided under the OLD round-level plant
    # rule for the shape the NEW seat-level rule handles: exactly ONE live miss. It must not
    # reach any further than that.
    mk_sup = lambda rounds: [{"lane": LANE, "guard": "broken-judge", "rounds_covered": rounds,
                              "ruling": RULING,
                              "supersedes": "a correct plant missed still voids [the round]"}]

    one_live = [ok(1), ok(2),
                void(3, [(True, "live.png"), (False, "retired.png")]),
                void(4, [(True, "live.png"), (False, "live.png")])]   # ONE live miss in r4
    two_live = [ok(1), ok(2),
                void(3, [(True, "live.png"), (False, "retired.png")]),
                void(4, [(False, "live.png"), (False, "live.png")])]  # TWO live misses in r4

    case("J  `supersedes` marker, ONE live miss -> cleared (the re-draw may run)",
         guard_with(tmp, one_live, mk_sup([3, 4])), None)
    case("K  `supersedes` marker, TWO live misses -> clears NOTHING",
         guard_with(tmp, two_live, mk_sup([3, 4])), "broken-judge")
    case("L  the SAME one-live-miss history without `supersedes` -> clears nothing",
         guard_with(tmp, one_live, mk([3, 4])), "broken-judge")

    # ⚠ THE PROPERTY THAT KEEPS IT FROM BEING AN OFF SWITCH: a cleared guard still fires on
    # rounds AFTER the marker. Two fresh VOIDs past the covered ones stop the line again.
    later = retired_both + [void(5, [(False, "live.png")]), void(6, [(False, "live.png")])]
    case("I  cleared history, then two NEW VOIDs -> fires again",
         guard_with(tmp, later, mk([3, 4])), "broken-judge")

    bad = [n for n, g, w in CASES if g != w]
    print("\n%s  (%d cases)" % ("EVERY CASE BEHAVED AS DECLARED."
                                if not bad else "%d DID NOT: %s" % (len(bad), bad), len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
