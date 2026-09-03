#!/usr/bin/env python3
"""THE DEVICE GATE — four conditions, checked on the build, before anything reaches the phone.

    python3 tools/tier1_walls/install_gate.py --round 12
    python3 tools/tier1_walls/install_gate.py --round 12 --announce

STANDING ORDER (Rafe, effective immediately). *"No build installs to the phone unless, on that
exact build:"*

  1. **its round is VALID** — plant caught, seat verdict standing. *"A void judging layer means
     STOP AND FIX, never ship-to-Rafe."*
  2. **the round's diagnostic seat passed its axis** — the seat answered the question the round
     was run to ask, rather than culling for something else.
  3. **a whole-frame comparative seat has run and not culled** — a fresh blind seat shown this
     build's standing capture beside BOTH the asset bar and the last Rafe-approved capture of the
     same surface, asked which is better made and whether it would ship this frame. *"A cull or a
     regression-vs-approved verdict blocks the install."*
  4. **the build contains every currently-ruled fix**, listed in the walk announcement.

*"Rafe's walk returns to being the LAST gate, not the first working one. These conditions are
checkable in the report; a build announcement missing any of the four is itself a defect."*

WHY THIS IS A SCRIPT AND NOT A CHECKLIST. Every process rule in this directory that depended on
being remembered was eventually not remembered — the plant that stopped being in the picture, the
withholding I walked around, the hue ruling that was never built. `device.sh build` calls this and
refuses on a failure, so the gate is the thing that installs rather than a paragraph beside it.

THE RULED-FIX REGISTER below is the fourth condition made checkable. Adding a ruling means adding
a row: a name, how to verify it on the built artefacts, and the ruling it came from. A fix that
cannot be checked from the artefacts does not belong in the register — it belongs in a report.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
EV = os.path.join(HERE, "evidence")
SEATS = os.path.join(EV, "seats")
WALLS = os.path.join(REPO, "src/Presentation/assets/tier1_walls")
CAP = os.path.join(REPO, "src/Presentation/assets/tier1_cap")


def _man(d):
    return json.load(open(os.path.join(d, "MANIFEST.json")))


# ── THE RULED-FIX REGISTER ────────────────────────────────────────────────────────────────────
# name -> (ruling it came from, predicate over the built artefacts)
def _void_ring_zero():
    return _man(WALLS)["void_ring"] == 0


def _cap_rung_three():
    return _man(CAP)["top_rung"] == 3


def _hue_shift_zero():
    return abs(float(_man(CAP).get("hue_shift", 1.0))) < 1e-9


def _quarry_tint():
    """The wall family must carry the floor's chroma, not the neutral tint that read grey."""
    t = _man(WALLS).get("quarry_tint")
    c = _man(CAP).get("quarry_tint")
    if t is None or c is None:
        return False
    mx, mn = max(t), min(t)
    return (mx - mn) / max(mx, 1e-6) > 0.10          # neutral was 0.015


def _ambient_anchored_occlusion():
    src = open(os.path.join(REPO, "src/Presentation/Map/Tier1FloorOverlays.cs")).read()
    return "RelativeIlluminationAtTile" in src


RULED_FIXES = {
    "void_ring 0 (§12.1 ring outline)": ("2026-09-01", _void_ring_zero),
    "cap rung 3 (round 10, A)": ("2026-09-02", _cap_rung_three),
    "cap hue_shift 0 (same quarry)": ("2026-09-02", _hue_shift_zero),
    "quarry tint on walls and cap": ("2026-09-02", _quarry_tint),
    "ambient-anchored occlusion (round 10, C)": ("2026-09-02", _ambient_anchored_occlusion),
}


def seat(rnd, name):
    p = os.path.join(SEATS, "r%d_%s.json" % (rnd, name))
    return json.load(open(p)) if os.path.exists(p) else None


def check(rnd, axis_label):
    out = []

    w2 = seat(rnd, "W2")
    if w2 is None:
        out.append((1, False, "no plant seat for round %d — the round has not been controlled" % rnd))
    elif not w2.get("caught"):
        out.append((1, False, "plant MISSED — round %d is VOID. STOP AND FIX, never ship." % rnd))
    else:
        adj = (w2.get("adjudicator") or {}).get("verdict", "?")
        out.append((1, True, "round %d VALID — plant caught (adjudicator: %s)" % (rnd, adj)))

    w1 = seat(rnd, "W1")
    if w1 is None:
        out.append((2, False, "no diagnostic seat for round %d" % rnd))
    else:
        ans = (w1.get("fields") or {}).get(axis_label)
        if not ans or len(ans.strip()) < 20:
            out.append((2, False, "diagnostic seat did not answer its axis (%s)" % axis_label))
        else:
            out.append((2, True, "diagnostic seat answered %s: %s"
                        % (axis_label, " ".join(ans.split())[:90])))

    w5 = seat(rnd, "W5")
    if w5 is None:
        out.append((3, False, "no comparative seat (W5) — run it against the bar AND the last "
                              "Rafe-approved capture"))
    else:
        culled = (w5.get("fields", {}).get("CULL", "").strip().upper()
                  not in ("", "NONE", "NONE."))
        regressed = bool(w5.get("regression_vs_approved"))
        if culled:
            out.append((3, False, "comparative seat CULLED: %s"
                        % " ".join(w5["fields"]["CULL"].split())[:90]))
        elif regressed:
            out.append((3, False, "comparative seat calls this a REGRESSION against the approved "
                                  "capture"))
        else:
            out.append((3, True, "comparative seat ran, did not cull, no regression"))

    missing = []
    for name, (_when, pred) in RULED_FIXES.items():
        try:
            if not pred():
                missing.append(name)
        except Exception as e:                                   # noqa: BLE001
            missing.append("%s (uncheckable: %s)" % (name, e))
    if missing:
        out.append((4, False, "build is MISSING ruled fixes: " + "; ".join(missing)))
    else:
        out.append((4, True, "all %d ruled fixes present" % len(RULED_FIXES)))

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--axis", default="Q12",
                    help="the label of the round's own diagnostic question")
    ap.add_argument("--announce", action="store_true",
                    help="print the walk announcement. Refuses unless all four conditions pass — "
                         "an announcement missing any of them is itself a defect.")
    a = ap.parse_args()

    rows = check(a.round, a.axis)
    print("DEVICE GATE — round %d\n" % a.round)
    for n, ok, msg in rows:
        print("  (%d) %-4s %s" % (n, "OK" if ok else "FAIL", msg))
    passed = all(ok for _, ok, _ in rows)

    print("\n  VERDICT: %s" % ("CLEAR TO INSTALL" if passed else
                               "BLOCKED — this build does not go to the phone"))

    if a.announce:
        if not passed:
            print("\n  REFUSING to write an announcement for a build that is blocked.")
            return 1
        commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
        print("\n" + "=" * 78)
        print("WALK ANNOUNCEMENT — round %d, commit %s" % (a.round, commit[:8]))
        print("=" * 78)
        print("\nGate conditions, all four:")
        for n, _ok, msg in rows:
            print("  (%d) %s" % (n, msg))
        print("\nRulings this build contains:")
        for name, (when, _p) in RULED_FIXES.items():
            print("  - %s   [%s]" % (name, when))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
