#!/usr/bin/env python3
"""Write the synthetic verdict histories the guard proofs are driven against.

They are FIXTURES, not rounds: no build produced them and nothing in them is evidence about any
art. They exist so the loop guards can be shown to fire — LOOP-PROCESS §4, bible §13.5, no check's
pass counts until it has demonstrated it can fail — while running the REAL `guards()` and
`write_stall()` rather than a copy of them.

Each fixture isolates ONE guard, and every fixture has to be checked against the others too: a
history that fires two guards proves nothing about either, because the first one to be reached
would have fired whatever the second one did.

  broken-judge/     two consecutive VOIDs. A void round has no findings, which is why the seat
                    block is bare and the flip list is empty.
  no-change/        two consecutive FAILs whose delivered frames are literally the same. The rank
                    moves between them, so it is not the stall guard being tested; the flip
                    lists share nothing, so it is not thrash either.
  thrash/           two consecutive FAILs carrying THE SAME REQUEST, worded differently, with
                    the rank score going DOWN. The pictures differ, so no-change cannot fire.
  stall/            a new best at round 1, then three readable rounds that never beat it. Flip
                    lists are all unrelated and every picture differs, so neither thrash nor
                    no-change can fire first.
  ceiling/          fifteen rounds that keep improving, so every progress guard stays quiet and
                    only the backstop is left. This one is deliberately awkward to build, and
                    that is the point: if the ceiling is easy to reach while the lane is
                    improving, the ceiling is set wrong.
  no-stop/          THE NEGATIVE CONTROL. A lane doing well enough that nothing may fire.

  python3 .claude/skills/frame-critic/evidence/make_guard_fixtures.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "guard-fixtures")
sys.path.insert(0, os.path.dirname(HERE))
import frame_critic as FC                                  # noqa: E402

FIXTURE_NOTE = ("Synthetic verdict. Drives a loop guard against the real guards() and "
                "write_stall(). Not a round; not evidence about any build.")

# ── THE FIXTURES' PICTURES ARE REAL PICTURES ─────────────────────────────────────────────────
#
# A fixture that invented a capture signature could not go wrong the way the real thing went
# wrong. `no-change` is driven by frames the morgue actually holds; the other lanes need
# signatures far enough apart NOT to trip it, so they use real frames too and the distances are
# measured rather than asserted.
#
# THE CALIBRATION THIS ENCODES, and it is the reason the fixtures are built this way.
# `washed-slab-lane.png` and `tile-quantized-wear.png` are two consecutive real builds that Rafe
# culled for two DIFFERENT defects. A 256-bit perceptual hash put them **2 bits apart — the whole
# declared floor** — so the first version of this guard would have stopped that lane on a round
# where the art genuinely moved. They are the `thrash` lane's two pictures here, which means the
# fixture goes red the moment that calibration is lost again.
MORGUE = os.path.join(os.path.dirname(HERE), "morgue")
CROP = [0, 90, 750, 1001]
_FRAMES = ["keyline-floor.png", "washed-slab-lane.png", "tile-quantized-wear.png",
           "grey-walls.png"]


def pic(seed):
    """A real frame's capture signature. Distinct seeds give distinct pictures; the same seed
    twice gives literally the same picture, which is what `no-change` needs."""
    return FC.signature(os.path.join(MORGUE, _FRAMES[seed % len(_FRAMES)]), CROP)


def row(lane, rnd, verdict, pos, n, flips, sig, series, hour=8):
    return {
        "_fixture": FIXTURE_NOTE,
        "schema": "frame-critic/1", "verdict": verdict, "lane": lane, "round": rnd,
        "surface": "wall", "commit": "0" * 40, "build_id": "fixture-%s-%d" % (lane, rnd),
        "timestamp": "2026-09-04T%02d:00:00" % (hour + rnd),
        "deck": {"work_dir": "(fixture)",
                 "build": "tools/tier1_walls/evidence/fixture_%s_%d.png" % (lane, rnd)},
        "build_frame": {"path": "(fixture)", "sha256": sig[:64]},
        "seat": {"WORST_WHY": "Round %d." % rnd},
        "flip_list": flips,
        "progress": {
            "rank_position": pos, "deck_size": n,
            "rank_score": None if pos is None else (n - pos) / float(n - 1),
            "capture_signature": sig, "series": series,
        },
        "transcript": "(fixture)",
    }


def emit(lane, rows):
    """Write a lane's rows, giving each verdict the series as it stood when that round ran."""
    series = []
    for i, r in enumerate(rows, start=1):
        p = r["progress"]
        r["progress"]["series"] = list(series) + [dict(
            round=r["round"], verdict=r["verdict"], rank_position=p["rank_position"],
            deck_size=p["deck_size"], rank_score=p["rank_score"],
            capture_signature=p["capture_signature"])]
        series = r["progress"]["series"]
        d = os.path.join(BASE, lane)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "r%03d-%s.json" % (r["round"], lane)), "w") as f:
            json.dump(r, f, indent=1)


def broken_judge():
    rows = []
    for i in (1, 2):
        r = row("broken-judge", i, "VOID", None, 3, [], pic(100 + i), [])
        r["plant"] = {"file": "grey-walls.png", "caught": False,
                      "verbatim": "Grey walls and ceiling; it looked better a few versions ago."}
        rows.append(r)
    emit("broken-judge", rows)


def no_change():
    # THE SAME PICTURE TWICE. Rank improves between them and the flip lists are unrelated, so
    # neither stall nor thrash can be the guard that fires.
    same = pic(7)
    emit("no-change", [
        row("no-change", 1, "FAIL", 3, 4, ["The passage mouth has no jamb."], same, []),
        row("no-change", 2, "FAIL", 2, 4, ["The void beyond the wall is pure black."], same, []),
    ])


def thrash():
    # THE SAME REQUEST, DIFFERENTLY WORDED, and the rank goes backwards. The two pictures differ
    # by many bits so no-change cannot fire first.
    a = "The wall top plane sits at the same value as the lit floor beside it; separate the planes."
    b = "Separate the wall top plane from the lit floor value beside it; they sit at the same value."
    emit("thrash", [
        row("thrash", 1, "FAIL", 2, 4, [a, "The lamp pool has a hard edge; soften it."], pic(1), []),
        row("thrash", 2, "FAIL", 3, 4, [b, "The corridor floor is one uniform dither."], pic(2), []),
    ])


def stall():
    # A NEW BEST AT ROUND 1, then three readable rounds that never beat it. Every flip item is
    # unrelated to every other and every picture differs, so stall is the only guard available.
    flips = [
        ["The passage mouth has no jamb; give the opening a vertical edge."],
        ["The lamp pool ends in a hard ring; ramp its outer two tiles."],
        ["Bindings never appear above waist height; place some on the upper courses."],
        ["The void beyond the wall is pure black with zero variance; give it rock."],
    ]
    # ranks: 1 (best, score 1.00), then 2, 3, 2 — none beats 1.00.
    emit("stall", [
        row("stall", i + 1, "FAIL", p, 4, flips[i], pic(20 + i), [])
        for i, p in enumerate([1, 2, 3, 2])
    ])


def ceiling():
    """FIFTEEN ROUNDS THAT KEEP IMPROVING — the only lane for which the ceiling is the right
    guard, and therefore the only honest way to test it.

    Every round sets a strictly new best, so stall cannot fire; every flip item is unique, so
    thrash cannot; every picture differs, so no-change cannot. The backstop is all that is left.

    ⚠ THE DECK IS TWENTY FRAMES WIDE, WHICH NO REAL ROUND IS. A real deck holds three or four, so
    it offers three or four distinct rank scores — not enough to improve fifteen times running.
    The width is the fixture buying fifteen strictly increasing scores and nothing else; it is not
    a claim about how a round is dealt. Recorded here rather than left for a reader to notice.
    """
    rows = []
    for i in range(1, 16):
        rows.append(row("ceiling", i, "FAIL", 21 - i, 20,
                        ["Round %d asks for something nothing else asked for: item %d." % (i, i)],
                        pic(300 + i), []))
    emit("ceiling", rows)


def no_stop():
    """THE NEGATIVE CONTROL, and it is the half that is usually skipped.

    A guard that always fires is exactly as useless as one that never does, and much harder to
    notice: every round STOPs, everyone stops reading the reason, and the mechanism is gone.

    Four rounds that must produce NO stop, each putting a specific temptation in front of a
    specific guard:

      r1 FAIL  rank 3/4, flip A                     — a bad start
      r2 PASS  rank 1/4                             — breaks any FAIL streak
      r3 FAIL  rank 2/4, flip A AGAIN               — flip A's third appearance overall. The
                                                      advisory may speak; no guard may fire,
                                                      because r2 broke the consecutive pair.
      r4 FAIL  rank 1/4, flip B, and A recurs        — a NEW BEST, so thrash must hold its fire
                                                      even though r3 and r4 are consecutive FAILs
                                                      sharing flip A. This is the case the old
                                                      two-strikes guard got wrong.

    Four rounds is well under the ceiling, every picture differs, and a new best lands at r4, so
    stall has nothing either.
    """
    A = "The wall top plane sits at the same value as the lit floor beside it; separate them."
    B = "The lamp pool ends in a hard ring; ramp its outer two tiles."
    rows = [("FAIL", 3, [A]), ("PASS", 1, []), ("FAIL", 2, [A]), ("FAIL", 1, [B, A])]
    emit("no-stop", [row("no-stop", i + 1, v, p, 4, f, pic(40 + i), [])
                     for i, (v, p, f) in enumerate(rows)])


if __name__ == "__main__":
    for fn in (broken_judge, no_change, thrash, stall, ceiling, no_stop):
        fn()
    print("fixtures written under %s" % BASE)
