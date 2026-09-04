#!/usr/bin/env python3
"""THE INSTALL GATE — no build reaches the phone without a critic verdict for THAT EXACT BUILD.

    python3 .claude/skills/frame-critic/critic_gate.py            # 0 = install may proceed

One check, one implementation, two callers: `tools/tier0_harness/build_review_app.sh` runs it
before it exports, and a PreToolUse hook runs it against any shell command that would install.
Two callers and one implementation on purpose — a gate reimplemented in a second place is a gate
with two behaviours, and the second one is always the lenient one.

WHAT IT REQUIRES

    CRITIC-VERDICT.json exists                     a build nobody looked at does not ship
    its build_id equals this working tree's        the verdict must describe THESE pixels, not a
                                                   commit that happens to still be checked out
    its verdict reads PASS                         FAIL and VOID both mean no

THE OVERRIDE IS VISIBLE, WHICH IS THE WHOLE POINT

    YARL_SKIP_CRITIC=1 tools/tier0_harness/build_review_app.sh

installs, and stamps SKIPPED-REVIEW into the review marker so the phone says so on screen for as
long as that build is on it. An override nobody can see is indistinguishable from a gate that
does not work, and this repo has the logged instances: every process rule here that depended on
being remembered was eventually not remembered.

EXIT
    0   clear — a blind seat would ship this exact frame
    1   refused, and it prints exactly what to run
   10   refused, but YARL_SKIP_CRITIC=1 was set. The caller installs and MUST stamp the build
        SKIPPED-REVIEW. A distinct code rather than 0, because the caller has to be able to tell
        "this passed" from "this was waved through" — collapsing the two is how an override
        stops being visible.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import build_id as BID                                    # noqa: E402

VERDICT = os.path.join(REPO, "CRITIC-VERDICT.json")
STALL = os.path.join(REPO, "STALL-REPORT.md")
RUN = ".claude/skills/frame-critic/run_frame_critic.sh"


def check():
    """Returns (ok, lines). `ok` is whether an install may proceed."""
    L = []
    if not os.path.exists(VERDICT):
        return False, [
            "NO CRITIC VERDICT. CRITIC-VERDICT.json does not exist, so no one has looked at "
            "this build.",
            "",
            "Run the round:   %s" % RUN,
        ]
    try:
        v = json.load(open(VERDICT))
    except Exception as e:
        return False, ["CRITIC-VERDICT.json is unreadable (%s). A gate cannot pass on faith."
                       % e, "", "Run the round:   %s" % RUN]

    bid, det = BID.build_id()
    L.append("verdict:  %s   lane %s round %s   %s"
             % (v.get("verdict"), v.get("lane"), v.get("round"), v.get("timestamp")))
    L.append("build:    %s%s" % (det["commit"][:12], "  (+dirty)" if det["dirty"] else ""))

    if v.get("build_id") != bid:
        return False, L + [
            "",
            "THE VERDICT IS NOT ABOUT THIS BUILD.",
            "  verdict build_id  %s  (commit %s)" % ((v.get("build_id") or "?")[:16],
                                                     (v.get("commit") or "?")[:12]),
            "  this working tree  %s  (commit %s)" % (bid[:16], det["commit"][:12]),
            "",
            "The build id folds in every tracked change and every untracked file, so a "
            "recomposed family moves it even when the commit does not. Something has changed "
            "since the seat looked.",
            "",
            "Re-run the round:   %s" % RUN,
        ]

    if v.get("self_test"):
        return False, L + [
            "",
            "THIS VERDICT IS A SELF-TEST OF THE JUDGE, not a verdict on a build — its deck put a "
            "morgue frame in the build's slot. It cannot authorise an install.",
            "",
            "Run a real round:   %s" % RUN,
        ]

    # ── PASS-WITH-ROUTED-ITEMS ────────────────────────────────────────────────────────────────
    #
    # RULED (Rafe, 2026-09-03): a lawful third state, *"valid only with a quoted Rafe ruling and a
    # named destination lane — builder can never route."*
    #
    # It exists because a FAIL can contain items no round on this lane can ever discharge. The
    # wall lane's r003 asked for OBJECTS — rope, pins, salvaged timber standing in the scene — and
    # the review scene has no prop system at all. Grinding that lane produces nothing; the human
    # gate routes the item to the lane that owns it and the build goes to the walk.
    #
    # THE BUILDER CAN NEVER ROUTE, and the enforcement is not a signature — it is VISIBILITY.
    # Every disposition is required to carry Rafe's words verbatim, every one is printed here, and
    # the set is stamped into the review marker so the handset shows it. A routing the builder
    # invented is a quote Rafe does not recognise, on his own screen, while he is holding it. That
    # is the same principle SKIPPED-REVIEW already runs on: an override nobody can see from the
    # phone is the same as no gate.
    #
    # EVERY flip must be dispositioned. A state that discharges some items and stays silent about
    # the rest is a FAIL wearing a better name.
    if v.get("verdict") == "PASS-WITH-ROUTED-ITEMS":
        flips = list(v.get("flip_list", []))
        disp = list(v.get("dispositions", []))
        bad = []
        if len(disp) < len(flips):
            bad.append("%d flip items and only %d dispositions — every item must be dispositioned"
                       % (len(flips), len(disp)))
        for i, d in enumerate(disp):
            state = (d.get("state") or "").upper()
            if state not in ("ROUTED", "CLOSED", "PARKED"):
                bad.append("disposition %d: state %r is not ROUTED, CLOSED or PARKED" % (i, state))
            if not (d.get("ruling") or "").strip():
                bad.append("disposition %d (%s): no quoted ruling" % (i, state))
            if state == "ROUTED" and not (d.get("lane") or "").strip():
                bad.append("disposition %d: ROUTED with no destination lane" % i)
        if bad:
            return False, L + ["", "PASS-WITH-ROUTED-ITEMS IS NOT LAWFULLY FORMED:"] \
                   + ["  - %s" % b for b in bad] \
                   + ["", "It is valid ONLY with a quoted Rafe ruling per item and, for a routed "
                          "item, a named destination lane. The builder can never route."]
        L += ["", "PASS WITH ROUTED ITEMS — every flip carries a human disposition:"]
        for d in disp:
            L.append("  %-7s %s" % (d.get("state", "?").upper(),
                                    " ".join((d.get("item") or "").split())[:78]))
            if d.get("lane"):
                L.append("          -> %s" % d["lane"])
            L.append("          Rafe: %s" % " ".join((d.get("ruling") or "").split())[:78])
        L.append("")
        L.append("  These are drawn on the handset. A routing Rafe does not recognise is visible")
        L.append("  to him on his own screen while he is holding the build.")

    elif v.get("verdict") != "PASS":
        why = {"FAIL": "The seat would not ship this frame.",
               "VOID": "The seat did not catch the picture-plant. The judging layer is not "
                       "trustworthy and the round's findings are not read (LOOP-PROCESS §4). "
                       "STOP AND FIX — never ship past a void round."}
        out = L + ["", "VERDICT IS %s. %s" % (v.get("verdict"),
                                              why.get(v.get("verdict"), ""))]
        # ⚠ ONLY A FAIL HAS FINDINGS TO SHOW. This printed the flip list for every non-PASS
        # verdict, void included — on the most-read surface the mechanism has — which is exactly
        # the reading §4 forbids. The verdict now carries no readable `flip_list` on a void round
        # at all, so this loop is correct by construction as well as by intent; the belt is here
        # and the braces are in frame_critic.py.
        if v.get("verdict") == "FAIL":
            for f in v.get("flip_list", [])[:8]:
                out.append("  flip: %s" % f)
        else:
            out.append("  Its findings are withheld and are not evidence. Fix the judging layer,")
            out.append("  not the art: check that the plant is actually in the picture the seat")
            out.append("  saw, and that its defect is on the axis the seat was asked about.")
        out += ["", "Fix, then re-run the round:   %s" % RUN]
        return False, out

    # ── A LIVE GUARD BLOCKS. A HISTORICAL REPORT DOES NOT. ────────────────────────────────────
    #
    # RULED (Rafe, 2026-09-03): *"fix the gate to block on active guard state, not on the
    # existence of a STALL-REPORT.md file — a historical report must never gate installs; only a
    # live guard does."*
    #
    # This used to be `if os.path.exists(STALL)`, and a file's existence is not a fact about the
    # line. The floor lane's five-round-park report sat committed on main after that guard had
    # been RETIRED — the park was replaced by the progress guards — and the report went on
    # blocking installs for **every lane**, including lanes that had never stalled and including
    # any combined build. It also broke the gate's own proof: `prove_gate.py` failed two cases
    # ("PASS verdict for this build -> allow", "a gated build's marker carries no stamp") for no
    # reason but a stale document on disk.
    #
    # The guards are derived from the verdict files on disk and are recomputed here, so what
    # blocks an install is a guard that is firing NOW, on THIS lane. A report is a record of a
    # ruling trigger; records do not gate.
    try:
        import frame_critic as FC                              # noqa: PLC0415
        lane = (BID._git("rev-parse", "--abbrev-ref", "HEAD").strip() or "detached")
        guard, why = FC.guards(FC.history(), lane)
    except Exception as e:                                     # noqa: BLE001
        # A gate that cannot evaluate its own guards must refuse — it does not know that it is
        # safe, and "could not check" is not "clear".
        return False, L + ["", "CANNOT EVALUATE THE LOOP GUARDS (%s). A gate that does not know "
                               "whether the line is stalled does not open." % e]
    if guard:
        return False, L + [
            "",
            "A LOOP GUARD IS LIVE ON THIS LANE: %s" % guard,
            "  %s" % why,
            "",
            "This is a LOOP-PROCESS §1.1.4 ruling trigger. The line does not restart itself.",
        ]

    L.append("plant:    %s — caught" % v.get("plant", {}).get("file"))
    L.append("GATE OPEN — a blind seat would ship this exact frame.")
    return True, L


def main():
    ok, lines = check()
    skip = os.environ.get("YARL_SKIP_CRITIC") == "1"
    print("== FRAME CRITIC GATE")
    for l in lines:
        print(("   " + l) if l else "")
    if ok:
        return 0
    if skip:
        print()
        print("   YARL_SKIP_CRITIC=1 — INSTALLING ANYWAY.")
        print("   The build is stamped SKIPPED-REVIEW and the phone will say so on screen.")
        print("   Nothing walked on a SKIPPED-REVIEW build is a gate verdict.")
        return 10
    print()
    print("   REFUSING TO INSTALL. Override with YARL_SKIP_CRITIC=1 if you need the build on")
    print("   the phone for measurement — it installs, marked, and is not a gate build.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
