#!/usr/bin/env python3
"""THE DEVICE GATE'S PRECONDITIONS, enforced rather than promised.

STANDING ORDER (Rafe, 2026-09-03): no build installs to the phone unless, ON THAT EXACT BUILD:

  1. its round is VALID — plant caught, seat verdict standing. A void judging layer means STOP
     AND FIX, never ship-to-Rafe.
  2. the round's diagnostic seat passed its axis.
  3. a whole-frame COMPARATIVE seat has run and not culled — a fresh blind seat shown this build's
     standing capture beside BOTH the asset bar and the last Rafe-approved capture of the same
     surface, asked which is better made and whether it would ship this frame. A cull, or a
     regression against the approved capture, blocks the install.
  4. the build contains every currently-ruled fix, listed in the walk announcement.

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
        fails.append("1. no SEATS-r%s.json — the round has no judging layer at all" % rnd)
        print("  1. round VALID                    NO SEAT ROUND FOUND")
    elif s.get("round_void"):
        fails.append("1. round %s is VOID — stop and fix, never ship-to-Rafe" % rnd)
        print("  1. round VALID                    VOID")
    else:
        print("  1. round VALID                    ok (plant caught)")

    # ---- 2. the diagnostic seat passed its axis -------------------------------------------
    ax = (s or {}).get("diagnostic_axis_passed")
    if ax is None:
        fails.append("2. the round records no diagnostic-axis verdict; it cannot have passed one")
        print("  2. diagnostic seat's axis         NOT RECORDED")
    elif not ax:
        fails.append("2. the diagnostic seat did not pass its axis")
        print("  2. diagnostic seat's axis         FAILED")
    else:
        print("  2. diagnostic seat's axis         ok")

    # ---- 3. the comparative seat -----------------------------------------------------------
    approved = c.get("approved_capture")
    comp = load(os.path.join(SEATS, "COMPARATIVE-r%s.json" % rnd))
    if not approved:
        fails.append("3. no approved capture is declared, so the comparative seat cannot run — "
                     "see the note in GATE-CONDITIONS.json; naming it is Rafe's, not mine")
        print("  3. comparative seat               BLOCKED (no approved capture declared)")
    elif comp is None:
        fails.append("3. the comparative seat has not run on this build")
        print("  3. comparative seat               NOT RUN")
    elif comp.get("culled") or comp.get("regression_vs_approved"):
        fails.append("3. the comparative seat culled or found a regression against the approved "
                     "capture")
        print("  3. comparative seat               CULL / REGRESSION")
    else:
        print("  3. comparative seat               ok (no cull, no regression)")

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
    print("GATE OPEN — all four conditions hold on this build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
