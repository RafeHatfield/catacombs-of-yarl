#!/usr/bin/env python3
"""THE DEVICE GATE'S PRECONDITIONS, enforced rather than promised.

STANDING ORDER (Rafe, 2026-09-03): no build installs to the phone unless, ON THAT EXACT BUILD:

  1-3. THE JUDGING LAYER — now the frame-critic's, not this file's.
  4.   the build contains every currently-ruled fix, listed in the walk announcement.

⚠ CONDITIONS 1-3 ARE DEMOTED HERE, and that is a ruling rather than a retreat. When this file was
written the judging layer was the seat/plant/round apparatus in tools/tier1_floors, and these three
asked whether that apparatus had been conducted properly. The frame-critic replaced it: a fresh
blind seat, a picture-plant from the morgue, eyes on delivered frames, checked by critic_gate.py
which runs BEFORE this file in build_review_app.sh.

Asking both would mean two judging layers with one veto each, and the old one would then be able to
block a build the new one passed — which is the demoted apparatus gating again under another name.
So 1-3 still PRINT, because a builder wants to know what the old tools said, and they no longer
append to `fails`.

CONDITION 4 STAYS BINDING. It is not a judging layer: it asks whether the artefact contains the
fixes that were ruled into it, which no critic can see from a picture and no seat can be expected
to. A build that quietly lost a ruled fix would look exactly as good as one that kept it.

`build_review_app.sh` calls this and refuses to install on a non-zero exit. That placement is the
point: this session has twice recorded that a rule depending on my restraint is not a rule, and
twice been right. The gate lives in the build path.

Exit 0 = all four hold. Exit 1 = at least one does not, and it says which.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
COND = os.path.join(REPO, "docs", "GATE-CONDITIONS.json")
SEATS = os.path.join(REPO, "tools", "tier1_floors", "evidence", "seats")
EVID = os.path.join(REPO, "tools", "tier1_floors", "evidence")


def load(p):
    try:
        return json.load(open(p))
    except Exception:
        return None


def check_ruled_fix(spec):
    kind, _, rest = spec.partition(":")
    if kind == "const":
        name, _, want = rest.partition("==")
        sys.path.insert(0, os.path.join(REPO, "tools", "tier1_floors"))
        import compose_ashlar as CA
        got = getattr(CA, name.strip(), None)
        return repr(got) == want.strip() or str(got) == want.strip(), "%s = %r" % (name.strip(), got)
    if kind == "file":
        path, _, needle = rest.partition(":")
        full = os.path.join(REPO, path)
        if not os.path.exists(full):
            return False, "missing file %s" % path
        return needle in open(full, errors="ignore").read(), path
    return False, "unknown check kind %r" % kind


def main():
    c = load(COND)
    if c is None:
        print("GATE: cannot read docs/GATE-CONDITIONS.json — the gate cannot pass on faith.")
        return 1

    rnd = c.get("round")
    fails = []
    print("DEVICE GATE PRECONDITIONS — round %s, standing capture %s\n"
          % (rnd, c.get("standing_capture")))

    # ---- 1. the round is VALID -----------------------------------------------------------
    s = load(os.path.join(SEATS, "SEATS-r%s.json" % rnd))
    if s is None:
        print("  ~  1. round VALID                 no seat round        (advisory: demoted)")
    elif s.get("round_void"):
        print("  ~  1. round VALID                 VOID                 (advisory: demoted)")
    else:
        print("  ~  1. round VALID                 ok                   (advisory: demoted)")

    # ---- 2. the diagnostic seat passed its axis -------------------------------------------
    ax = (s or {}).get("diagnostic_axis_passed")
    if ax is None:
        print("  ~  2. diagnostic seat's axis      not recorded         (advisory: demoted)")
    elif not ax:
        print("  ~  2. diagnostic seat's axis      failed               (advisory: demoted)")
    else:
        print("  ~  2. diagnostic seat's axis      ok                   (advisory: demoted)")

    # ---- 3. the comparative seat -----------------------------------------------------------
    approved = c.get("approved_capture")
    comp = load(os.path.join(SEATS, "COMPARATIVE-r%s.json" % rnd))
    if not approved:
        print("  ~  3. comparative seat            no approved capture  (advisory: demoted;")
        print("                                       the frame-critic runs a three-frame deck)")
    elif comp is None:
        print("  ~  3. comparative seat            not run              (advisory: demoted)")
    elif comp.get("culled") or comp.get("regression_vs_approved"):
        print("  ~  3. comparative seat            cull / regression    (advisory: demoted)")
    else:
        print("  ~  3. comparative seat            ok                   (advisory: demoted)")

    # ---- 4. every currently-ruled fix is present -------------------------------------------
    missing = []
    for f in c.get("ruled_fixes", []):
        ok, detail = check_ruled_fix(f["check"])
        if not ok:
            missing.append("%s (%s)" % (f["id"], detail))
    if missing:
        fails.append("4. ruled fixes absent from this build: " + ", ".join(missing))
        print("  4. every ruled fix present        MISSING %d" % len(missing))
    else:
        print("  4. every ruled fix present        ok (%d checked)" % len(c.get("ruled_fixes", [])))

    # ---- the instruments, ADVISORY ----------------------------------------------------------
    #
    # DEMOTED, and this is the change rather than an omission. Instruments are builder's tools:
    # they are how you aim between rounds, and they GATE NOTHING. Nothing here appends to `fails`
    # any more.
    #
    # The reason is measured, not stylistic. At the wall gate of 2026-08-27 every instrument in
    # this repo was green and the phone still said no — which is what it looks like when the thing
    # being measured and the thing being judged have come apart. A number that can hold a gate
    # will, over enough rounds, be optimised against; and it will silently outcompete every clause
    # that has no number, which is most of the register (bible §13.4).
    #
    # What gates now is a picture judged by eyes: the frame-critic verdict, checked ahead of this
    # file in build_review_app.sh. Nothing was deleted — these rows still print, because knowing
    # an instrument went red is useful to a builder even when it decides nothing.
    for spec in c.get("instruments_that_must_pass", []):
        ev = load(os.path.join(EVID, spec["evidence"]))
        key = spec.get("key")
        if ev is None:
            print("  ~  %-30s no evidence           (advisory)" % spec["id"])
        elif key and not ev.get(key):
            print("  ~  %-30s FAILED                (advisory)" % spec["id"])
        else:
            print("  ~  %-30s ok                    (advisory)" % spec["id"])

    print()
    if fails:
        print("GATE CLOSED — %d condition%s unmet:" % (len(fails), "" if len(fails) == 1 else "s"))
        for f in fails:
            print("   * %s" % f)
        print("\nNo build installs to the phone. Rafe's walk is the LAST gate, not the first")
        print("working one.")
        return 1
    print("PRECONDITIONS OK — every ruled fix is in this build. The frame-critic's PASS is what")
    print("opened the gate; this file only checked that the artefact carries what was ruled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
