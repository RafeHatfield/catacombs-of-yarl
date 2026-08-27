#!/usr/bin/env python3
"""Per-clause pass rates across the judged sets.

"0 structural candidates" is the bar's answer and it is not the useful part. The useful part is
WHICH of the four clauses is doing the killing, because a set that fails one clause on every
piece and clears the other three is a completely different object from a set that fails all
four — and the wall gauntlet's incumbent failed all four.

Counts come from the STRICT derivation (`rescore.py`), over the critic's own saved prose.
Nothing is re-run and no image is re-judged.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rescore as R  # noqa: E402

CLAUSES = [("two_planes", "1. two planes — a top surface, not a stripe"),
           ("segment_identity", "2. segment identity — the piece has a role"),
           ("no_key_light", "3. §6.3-legal — no named light direction"),
           ("no_baked_outline", "4. §12.1 — no baked outline")]


def main():
    labels = sys.argv[1:] or ["kitA0", "kitB"]
    table = {}
    for label in labels:
        p = os.path.join(HERE, "critic", label, "result.json")
        if not os.path.exists(p):
            continue
        res = json.load(open(p))
        cands = [r for r in res["results"] if r["kind"] == "candidate" and r.get("raw")]
        counts = {k: 0 for k, _ in CLAUSES}
        culled = 0
        culls = {}
        for r in cands:
            cl, _ = R.strict_score(r["raw"])
            for k, _ in CLAUSES:
                counts[k] += bool(cl[k])
            if cl["culled"]:
                culled += 1
                c = (r["raw"].get("cull") or "?").strip().lower()
                culls[c] = culls.get(c, 0) + 1
        table[label] = {"n": len(cands), "counts": counts, "culled": culled, "culls": culls}

    print("%-44s %s" % ("clause", "  ".join("%-14s" % l for l in table)))
    for k, name in CLAUSES:
        cells = []
        for l in table:
            t = table[l]
            cells.append("%d/%d (%3.0f%%)" % (t["counts"][k], t["n"],
                                              100.0 * t["counts"][k] / t["n"]))
        print("%-44s %s" % (name, "  ".join("%-14s" % c for c in cells)))
    print("%-44s %s" % ("mechanically culled",
                        "  ".join("%-14s" % ("%d/%d" % (table[l]["culled"], table[l]["n"]))
                                  for l in table)))
    for l in table:
        if table[l]["culls"]:
            print("    %s culls: %s" % (l, table[l]["culls"]))
    allfour = {}
    for label in table:
        res = json.load(open(os.path.join(HERE, "critic", label, "result.json")))
        n = 0
        for r in res["results"]:
            if r["kind"] != "candidate" or not r.get("raw"):
                continue
            cl, _ = R.strict_score(r["raw"])
            if all(cl[k] for k, _ in CLAUSES) and not cl["culled"]:
                n += 1
        allfour[label] = n
    print("%-44s %s" % ("ALL FOUR = structural candidates",
                        "  ".join("%-14s" % ("%d/%d" % (allfour[l], table[l]["n"]))
                                  for l in table)))
    for label in table:
        table[label]["structural"] = allfour[label]

    with open(os.path.join(HERE, "critic", "clause_table.json"), "w") as f:
        json.dump(table, f, indent=2, sort_keys=True)
    print("\nwrote critic/clause_table.json")


if __name__ == "__main__":
    main()
