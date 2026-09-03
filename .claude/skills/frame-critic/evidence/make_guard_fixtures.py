#!/usr/bin/env python3
"""Write the synthetic verdict histories the guard proofs are driven against.

They are FIXTURES, not rounds: no build produced them and nothing in them is evidence about any
art. They exist so the three loop guards can be shown to fire — LOOP-PROCESS §4, bible §13.5, no
check's pass counts until it has demonstrated it can fail — while running the REAL `guards()` and
`write_stall()` rather than a copy of them.

Each fixture isolates one guard:

  two-strikes/      two consecutive FAILs whose flip lists carry THE SAME REQUEST, worded
                    differently. Exact string equality would miss it; that is the case the guard
                    has to catch, so it is the case the fixture presents.
  five-round-park/  five FAILs whose flip items are deliberately unrelated round to round, so
                    two-strikes cannot fire and the park guard is what is being tested.
  broken-judge/     two consecutive VOIDs. A void round has no findings, which is why the seat
                    block is bare and the flip list is empty.

  python3 .claude/skills/frame-critic/evidence/make_guard_fixtures.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "guard-fixtures")

PARK_FLIPS = [
    ["The passage mouth has no jamb; give the opening a vertical edge."],
    ["The lamp pool ends in a hard ring; ramp its outer two tiles."],
    ["Bindings never appear above waist height; place some on the upper courses."],
    ["The floor and the wall base share one value at the south run; drop the base."],
    ["The void beyond the wall is pure black with zero variance; give it rock."],
]

FIXTURE_NOTE = ("Synthetic verdict. Drives a loop guard against the real guards() and "
                "write_stall(). Not a round; not evidence about any build.")


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)


def park():
    for i in range(1, 6):
        write(os.path.join(BASE, "five-round-park", "r%03d-guard-park.json" % i), {
            "_fixture": FIXTURE_NOTE,
            "schema": "frame-critic/1", "verdict": "FAIL", "lane": "guard-park", "round": i,
            "surface": "wall", "commit": "0" * 40, "build_id": "fixture-park-%d" % i,
            "timestamp": "2026-09-03T%02d:00:00" % (8 + i),
            "deck": {"work_dir": "(fixture)",
                     "build": "tools/tier1_walls/evidence/fixture_p%d.png" % i},
            "seat": {"WORST_WHY": "Round %d: still not a frame anyone would ship." % i},
            "flip_list": PARK_FLIPS[i - 1], "transcript": "(fixture)"})


def broken_judge():
    for i in (1, 2):
        write(os.path.join(BASE, "broken-judge", "r%03d-guard-broken-judge.json" % i), {
            "_fixture": FIXTURE_NOTE,
            "schema": "frame-critic/1", "verdict": "VOID", "lane": "guard-broken-judge",
            "round": i, "surface": "wall", "commit": "0" * 40,
            "build_id": "fixture-void-%d" % i,
            "timestamp": "2026-09-03T%02d:00:00" % (8 + i),
            "deck": {"work_dir": "(fixture)",
                     "build": "tools/tier1_walls/evidence/fixture_v%d.png" % i},
            "plant": {"file": "grey-walls.png", "caught": False,
                      "verbatim": "Grey walls and ceiling; it looked better a few versions ago."},
            "seat": {"WORST_WHY": ""}, "flip_list": [], "transcript": "(fixture)"})


def no_stop():
    """THE NEGATIVE CONTROL, and it is the half that is usually skipped.

    A guard that always fires is exactly as useless as one that never does, and it is much harder
    to notice: every round STOPs, everyone stops reading the reason, and the mechanism is gone.

    Four rounds that must produce NO stop, each one aimed at a specific way the guards could be
    too eager:

      r1 FAIL  carrying flip A
      r2 PASS  — this breaks the streak. Two FAILs with a PASS between them are not consecutive.
      r3 FAIL  carrying flip A AGAIN. Across the whole lane it is the third appearance; the guard
               must still not fire, because r2 cleared it.
      r4 FAIL  carrying an unrelated flip B. The two most recent FAILs (r3, r4) are consecutive
               and share nothing, which is the ordinary state of a round that is making progress.

    And four rounds is one short of the park, so the park must hold its fire too.
    """
    A = "The wall top plane sits at the same value as the lit floor beside it; separate them."
    B = "The lamp pool ends in a hard ring; ramp its outer two tiles."
    rows = [("FAIL", [A]), ("PASS", []), ("FAIL", [A]), ("FAIL", [B])]
    for i, (verdict, flips) in enumerate(rows, start=1):
        write(os.path.join(BASE, "no-stop", "r%03d-guard-no-stop.json" % i), {
            "_fixture": FIXTURE_NOTE + " NEGATIVE CONTROL: no guard may fire on this history.",
            "schema": "frame-critic/1", "verdict": verdict, "lane": "guard-no-stop", "round": i,
            "surface": "wall", "commit": "0" * 40, "build_id": "fixture-nostop-%d" % i,
            "timestamp": "2026-09-03T%02d:00:00" % (8 + i),
            "deck": {"work_dir": "(fixture)",
                     "build": "tools/tier1_walls/evidence/fixture_n%d.png" % i},
            "seat": {"WORST_WHY": "Round %d." % i},
            "flip_list": flips, "transcript": "(fixture)"})


if __name__ == "__main__":
    park()
    broken_judge()
    no_stop()
    print("fixtures written under %s" % BASE)
    print("(two-strikes/ is authored by hand and committed — its wording is the point of it)")
