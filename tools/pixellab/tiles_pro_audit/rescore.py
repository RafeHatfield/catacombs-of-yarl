#!/usr/bin/env python3
"""Re-derive the bar's clauses from the SAVED critic transcripts under a stricter reading.

⚠ THE DEFECT THIS FIXES, RECORDED RATHER THAN QUIETLY PATCHED. `critic.score()` tests the
critic's THICKNESS line for negation with a substring match against a list that contains the
bare token "no". Substring matching makes "no" fire on *nothing*, *not*, *known*, and on any
sentence anywhere containing the word — so the clause could only ever come back False for a
prose answer of any length. The first seat returned `planes=False` on 38 of 38, which is
exactly what a stuck instrument looks like, and it had to be ruled out before the number could
be reported.

This file re-reads the same saved transcripts with word-boundary matching and an explicit
affirmative test, and prints BOTH derivations side by side. **The critic is not re-run and its
words do not change; only my reading of them does.** If the two derivations disagree, both go
in the report and the stricter one governs, because a clause that survives only under the loose
reading was never demonstrated.

Zero cost. No network. No new generation.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import critic as C  # noqa: E402

AFFIRM = (r"\byes\b", r"\bit (does|would|could)\b", r"\byou could\b", r"\bclearly\b",
          r"\bdefinitely\b", r"\bthere is a (clear|distinct|separate)\b")
NEGATE = (r"\bno\b", r"\bnot\b", r"\bnothing\b", r"\bnone\b", r"\bcannot\b", r"\bcan't\b",
          r"\bwould not\b", r"\bwouldn't\b", r"\bflat\b", r"\bbarely\b", r"\bpaint\b",
          r"\bstripe\b", r"\bpatch\b", r"\bfall\b", r"\bslide\b", r"\bunreliab")
NO_DIR = (r"\bno direction\b", r"\bnone\b", r"\bno single\b", r"\bnot directional\b",
          r"\bnon-?directional\b", r"\bambient\b", r"\bno (clear|obvious|apparent|specific|"
          r"discernible|consistent) direction\b", r"\bno light direction\b",
          r"\bno source\b", r"\bno one direction\b")
CANT = (r"\bcannot tell\b", r"\bcan'?t tell\b", r"\bcannot say\b", r"\bcannot determine\b",
        r"\bunclear\b", r"\bhard to tell\b", r"\bindeterminate\b", r"\bno idea\b",
        r"\bcould be anything\b", r"\bimpossible to tell\b")


def hits(text, pats):
    t = (text or "").lower()
    return [p for p in pats if re.search(p, t)]


def strict_score(rec):
    cull = (rec.get("cull") or "").strip().lower()
    culled = cull not in ("", "none", "n/a", "-")
    thick = rec.get("thickness") or ""
    role = rec.get("role") or ""
    light = rec.get("light") or ""

    neg = hits(thick, NEGATE)
    aff = hits(thick, AFFIRM)
    # A top surface counts only if the critic affirms one and does not negate it. Silence is
    # not an affirmation: an empty answer fails the clause.
    c1 = bool(thick.strip()) and bool(aff) and not neg
    c2 = bool(role.strip()) and not hits(role, CANT)
    c3 = bool(light.strip()) and bool(hits(light, NO_DIR)) and cull != "key-light"
    c4 = cull != "outline"
    return ({"two_planes": c1, "segment_identity": c2, "no_key_light": c3,
             "no_baked_outline": c4, "culled": culled},
            {"thickness_negations": neg, "thickness_affirmations": aff})


def selftest():
    """§4 applies to THIS readout too: a derivation that can only ever return False is not an
    instrument, it is a rubber stamp facing the other way. Two constructed records, one that
    plainly satisfies every clause and one that plainly fails each, with the answer known
    before the code runs."""
    good = {"cull": "none",
            "role": "An outside corner piece; it goes where two runs of wall meet.",
            "thickness": "Yes. There is a distinct cap two pixels deep with its own near-edge "
                         "value below it; you could set a lantern on it.",
            "light": "No direction. The values follow the planes, not a source.",
            "holds": "Iron straps over a driven pin at each end.",
            "happened": "It has been walked past for centuries and patched twice.",
            "verdict": "PASS", "why": "It reads as built structure at ship size."}
    bad = {"cull": "none", "role": "Cannot tell.",
           "thickness": "No, it is a flat stripe.",
           "light": "Upper left.", "holds": "Nothing.", "happened": "Cannot tell.",
           "verdict": "FAIL", "why": "flat"}
    ok = True
    for name, rec, expect in (("affirming record", good, True), ("failing record", bad, False)):
        cl, _ = strict_score(rec)
        got = all(cl[k] for k in ("two_planes", "segment_identity", "no_key_light",
                                  "no_baked_outline")) and not cl["culled"]
        flag = "PASS" if got == expect else "RED"
        if got != expect:
            ok = False
        print("  %-4s %-18s structural=%-5s expected=%-5s  %s"
              % (flag, name, got, expect,
                 " ".join("%s=%s" % (k, v) for k, v in sorted(cl.items()))))
    print("  -> the derivation %s" %
          ("can return BOTH answers; its zeroes count"
           if ok else "IS STUCK — do not read its output"))
    return ok


def main():
    print("== positive control on the derivation itself (§4, bible §13.5) ==")
    if not selftest():
        raise SystemExit("derivation self-test RED")
    labels = sys.argv[1:] or ["kitA0"]
    out = {}
    for label in labels:
        p = os.path.join(HERE, "critic", label, "result.json")
        if not os.path.exists(p):
            print("no result for", label)
            continue
        res = json.load(open(p))
        rows = []
        loose_n = strict_n = 0
        disagree = []
        for r in res["results"]:
            if r["kind"] != "candidate" or not r.get("raw"):
                continue
            loose = r.get("clauses") or {}
            strict, why = strict_score(r["raw"])
            ls = all(loose.get(k) for k in ("two_planes", "segment_identity",
                                            "no_key_light", "no_baked_outline")) \
                and not loose.get("culled")
            ss = all(strict[k] for k in ("two_planes", "segment_identity",
                                         "no_key_light", "no_baked_outline")) \
                and not strict["culled"]
            loose_n += ls
            strict_n += ss
            if ls != ss or any(loose.get(k) != strict[k] for k in strict):
                disagree.append({"tile": r["label"],
                                 "loose": loose, "strict": strict, "why": why,
                                 "thickness": r["raw"].get("thickness"),
                                 "role": r["raw"].get("role"),
                                 "light": r["raw"].get("light")})
            rows.append({"tile": r["label"], "loose_structural": ls,
                         "strict_structural": ss, "strict": strict, "loose": loose})
        print("\n== %s ==" % label)
        print("  loose derivation : %d structural of %d" % (loose_n, len(rows)))
        print("  STRICT derivation: %d structural of %d" % (strict_n, len(rows)))
        print("  clause-level disagreements: %d" % len(disagree))
        for d in disagree[:12]:
            ks = [k for k in d["strict"] if d["loose"].get(k) != d["strict"][k]]
            print("    %-9s %s   thickness=%r" %
                  (d["tile"], ",".join(ks), (d["thickness"] or "")[:90]))
        out[label] = {"loose_structural": loose_n, "strict_structural": strict_n,
                      "n_candidates": len(rows), "rows": rows, "disagreements": disagree}
    with open(os.path.join(HERE, "critic", "rescore.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print("\nwrote critic/rescore.json")
    print("The stricter derivation governs. A clause that holds only under the loose reading\n"
          "was never demonstrated.")


if __name__ == "__main__":
    main()
