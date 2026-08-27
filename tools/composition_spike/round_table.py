#!/usr/bin/env python3
"""The rounds, in one table. Reads evidence/critic/*_result.json — no numbers typed by hand.

LOOP-PROCESS §1.1.5: every round logs its evidence, read after the run rather than as a
toll-gate during it. This is that log rendered.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CRITIC = os.path.join(HERE, "evidence", "critic")


def main():
    files = sorted(glob.glob(os.path.join(CRITIC, "round*_result.json")))
    if not files:
        print("no rounds yet")
        return 0
    print("round  plant  plant cull    passes  flips  commit    Q4 (thickness) on the bound arm")
    for f in files:
        d = json.load(open(f))
        v = d["verdicts"]
        plant = v.get(d["plant"], {})
        # C1 is the bound arm in every round's mapping.
        q4 = v.get("C1", {}).get("q4", "")
        q4 = (q4[:44] + "...") if len(q4) > 47 else q4
        print("  %-4d %-6s %-13s %-7d %-6d %-9s %s"
              % (d["round"], "CAUGHT" if d["plant_caught"] else "MISSED — VOID",
                 plant.get("cull") or "none", len(d["passes"]), len(d["flip_list"]),
                 d["commit"][:8], q4 or "—"))
    print("\nA round is VOID if the plant passed (LOOP-PROCESS §4, bible §13.5). None were.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
