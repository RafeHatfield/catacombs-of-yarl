#!/usr/bin/env python3
"""THE POSITIVE CONTROL FOR A GUARD-CLEARING RULING — it must still fire afterwards.

§13.5 / LOOP-PROCESS §4: **no instrument's pass counts until it has demonstrated it can fail.**
A clearing mechanism has a sharper version of that obligation than most checks, because the
failure mode is silent and it points the wrong way: a "clear" that actually DISABLES the guard
looks identical to a working one on the day it is used, and only shows up as a lane that never
stops again.

So the property under test is not *does the clear work* — it is:

    **A CLEAR EXCLUDES NAMED HISTORY. IT DOES NOT SILENCE THE GUARD.**

Five cases, each with the answer declared before it runs:

  E1  the collision, uncleared          no-change FIRES        (else nothing needed clearing)
  E2  the collision, cleared            no guard               (the ruling takes effect)
  E3  cleared, then a FRESH no-change   no-change FIRES        ← THE ONE THAT MATTERS
  E4  a marker naming broken-judge      broken-judge FIRES     (a park never launders a blind judge)
  E5  a marker for another lane/guard   no-change FIRES        (a clear is not a wildcard)
  E6  no-change cleared, thrash live    thrash FIRES           (a clear is PER GUARD, not global)

E3 is the control. E2 without E3 would pass just as happily against a mechanism that deleted the
guard, which is exactly the bypass this must not be.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frame_critic as FC  # noqa: E402

LANE = "provelane"


def verdict(rnd, sig, vd="FAIL", plant_caught=True, score=1.0):
    """A verdict file shaped like the real thing, in the only fields the guards read."""
    return {
        "schema": 1, "lane": LANE, "round": rnd, "verdict": vd,
        "timestamp": "2026-09-06T00:%02d:00" % rnd,
        "build_frame": {"sha256": sig},
        "plant": {"caught": plant_caught},
        "progress": {"rank_score": score, "capture_signature": sig},
        "flip_list": ["a flip that does not repeat %d" % rnd],
    }


def run(tmp, verdicts, marker):
    hd = os.path.join(tmp, "h")
    os.makedirs(hd, exist_ok=True)
    for f in os.listdir(hd):
        os.remove(os.path.join(hd, f))
    for v in verdicts:
        json.dump(v, open(os.path.join(hd, "r%03d.json" % v["round"]), "w"))
    pk = os.path.join(tmp, "park.json")
    if marker is None:
        if os.path.exists(pk):
            os.remove(pk)
        pk_arg = os.path.join(tmp, "absent.json")
    else:
        json.dump(marker, open(pk, "w"))
        pk_arg = pk
    name, _ = FC.guards(FC.history(hd), LANE, pk_arg)
    return name


def main():
    same = "a" * 64          # one picture, twice -> no-change
    other = "b" * 64
    fresh = "c" * 64

    # ⚠ THE SCORES RISE, AND THAT IS NOT DECORATION. The first version of this fixture gave both
    # rounds the same rank score, and E2 came back `thrash` instead of `(none)` — because a clear
    # is PER GUARD, so clearing `no-change` correctly left `thrash` evaluating the very same two
    # rounds, and two equal scores satisfy its `no movement in rank` condition. The control caught
    # the ruled behaviour working and a fixture that could not see it. A rising score isolates
    # no-change as the only guard those rounds trip, which is what E2 is trying to assert.
    collision = [verdict(1, same, score=0.5), verdict(2, same, score=1.0)]
    blind = [verdict(1, other, vd="VOID", plant_caught=False),
             verdict(2, fresh, vd="VOID", plant_caught=False)]
    # rounds 1-2 are the cleared collision; 3-4 are a NEW pair on one picture
    after = [verdict(1, same, score=0.5), verdict(2, same, score=1.0),
             verdict(3, fresh, score=0.5), verdict(4, fresh, score=1.0)]

    clear_nc = {"lane": LANE, "guard": "no-change", "rounds_covered": [1, 2],
                "ruling": "fixture"}
    clear_judge = {"lane": LANE, "guard": "broken-judge", "rounds_covered": [1, 2],
                   "ruling": "fixture — must be refused"}
    clear_elsewhere = {"lane": "someone-else", "guard": "no-change", "rounds_covered": [1, 2],
                       "ruling": "fixture — wrong lane"}

    cases = [
        ("E1  collision, uncleared              ", collision, None,            "no-change"),
        ("E2  collision, cleared                ", collision, clear_nc,        None),
        ("E3  cleared, then a FRESH no-change   ", after,     clear_nc,        "no-change"),
        ("E4  marker names broken-judge         ", blind,     clear_judge,     "broken-judge"),
        ("E5  marker names another lane         ", collision, clear_elsewhere, "no-change"),
        ("E6  cleared guard, OTHER guard intact  ", [verdict(1, same, score=1.0),
                                                     verdict(2, same, score=1.0)],
                                                    clear_nc,        "thrash"),
    ]

    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        print("PROVING THE CLEAR — a clear excludes named history, it does not silence the guard\n")
        print("  case                                    expected        got")
        for label, verdicts, marker, expect in cases:
            got = run(tmp, verdicts, marker)
            good = got == expect
            ok &= good
            print("  %s %-15s %-15s %s"
                  % (label, expect or "(none)", got or "(none)", "ok" if good else "FAIL"))

    print()
    if ok:
        print("PASS — and E3 is the one that counts: after the ruling cleared rounds 1-2, a fresh")
        print("no-change pair at rounds 3-4 STILL STOPPED THE LINE. The clear is not a bypass.")
        return 0
    print("FAIL — the clearing mechanism does not behave as ruled. Do not ship it.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
