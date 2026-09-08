#!/usr/bin/env python3
"""THE NONE SENTINEL READS THE ANSWER, NOT THE PROSE — and it still says NONE when NONE is meant.

§13.5 / LOOP-PROCESS §4: no check's pass counts until it has demonstrated it can fail. This drives
the REAL parser (`frame_critic.parse`), never a copy of it, and it proves both directions plus the
one thing a parser change actually has to prove — that it does not silently re-decide history.

    A  a body whose ANSWER is a list and whose PROSE contains "none"   -> the list      (the bug)
    B  a body whose ANSWER is NONE                                     -> []            (can fail)
    C  a body whose answer is NONE and whose prose names frames        -> []
    D  every transcript in history/ parses to the same slots as before -> no verdict moves
    E  a seat that elaborates per frame is deduplicated, so
       `every_frame_flagged` can be true at all                        -> the signal works

D is the load-bearing one. A parser fix applied after a round has been seen is exactly the shape
LOOP-PROCESS §8 warns about, so the scope is measured rather than claimed: the old behaviour is
reconstructed here, verbatim, and every committed transcript is run through both.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frame_critic as FC   # noqa: E402


def old_slots(body, n):
    """The parser as it shipped, kept here so the comparison is against the real thing."""
    if re.search(r"\bNONE\b", body, re.I):
        return []
    return [int(x) for x in re.findall(r"\d+", body) if 1 <= int(x) <= n]


CASES = [
    ("A prose 'none' must not eat a real list",
     "1, 2, 3, 4\n\n- **1** the biggest object in the room carries none of it.",
     [1, 2, 3, 4]),
    ("B a genuine NONE answer is still NONE",
     "NONE", []),
    ("C NONE answered, frames named only in the reasoning",
     "NONE\n\n- nothing in 1 or 3 rises to a glance-level defect.", []),
    ("E per-frame elaboration is deduplicated",
     "1, 2, 3\n- **2** ...\n- **1, 3** ...\n- **1, 2** ...", [1, 2, 3]),
]


def main():
    bad = 0
    print("== the sentinel, both directions")
    for name, body, want in CASES:
        got = FC._slots(body, 4)
        ok = got == want
        bad += not ok
        print("   %-46s %-14s %s" % (name, got, "ok" if ok else "FAILED, wanted %s" % want))

    print("\n== D: no committed verdict moves")
    moved = []
    for p in sorted(glob.glob(os.path.join(HERE, "history", "*-transcript.txt"))):
        txt = open(p).read()
        try:
            r = FC.parse(txt, 4)
        except Exception as e:
            print("   %-44s PARSE ERROR %s" % (os.path.basename(p), e))
            bad += 1
            continue
        for label, key in (("FLAGGED", "_flagged"), ("SHIP", "_ship")):
            o = sorted(set(old_slots(r[label], 4)))
            n = sorted(set(r[key]))
            if o != n:
                moved.append((os.path.basename(p), label, o, n))
    if not moved:
        print("   every transcript parses to the same slots as before — nothing re-decided.")
    else:
        for f, label, o, n in moved:
            print("   %-44s %-8s was %-12s now %s" % (f, label, o, n))
        print("\n   ⚠ Each line above is a round whose reading CHANGED. That is not automatically")
        print("   wrong — the change exists to correct a misreading — but it is the thing a")
        print("   parser fix must never do silently, so it is listed rather than counted.")

    print("\n== F: what the corrected reading does to every verdict ever recorded")
    print("   %-42s %-6s %-9s %-9s %s" % ("verdict", "plant", "recorded", "now", "verdict"))
    import json
    for vp in sorted(glob.glob(os.path.join(HERE, "history", "*.json"))):
        d = json.load(open(vp))
        tp = vp.replace(".json", "-transcript.txt")
        if not os.path.exists(tp) or "plant" not in d:
            continue
        plant = d["plant"].get("slot")
        slots = (d.get("deck") or {}).get("slots") or {}
        bslot = next((int(k) for k, v in slots.items() if v.get("what") == "build"), None)
        r = FC.parse(open(tp).read(), len(slots) or 4)
        now, _ = FC.plant_caught(r, plant, bslot)
        rec = d["plant"].get("caught")
        if now != rec:
            print("   %-42s %-6s %-9s %-9s %s   <== CHANGES"
                  % (os.path.basename(vp)[:42], plant, rec, now, d.get("verdict")))
    print("   (only rounds whose plant-catch CHANGES are listed; the rest are unmoved)")
    print("   Nothing here is rewritten. A recorded verdict stands as it was recorded;")
    print("   this is the impeachment LOOP-PROCESS §8 asks for, in the same report.")

    print("\n%s" % ("ALL CASES PASS" if bad == 0 else "%d CASE(S) FAILED" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
