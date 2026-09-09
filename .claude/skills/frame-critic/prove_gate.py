#!/usr/bin/env python3
"""SHOW THE INSTALL GATE REFUSING — LOOP-PROCESS §4, bible §13.5.

    python3 .claude/skills/frame-critic/prove_gate.py

No check's pass counts until it has demonstrated it can fail, and that applies to this mechanism
exactly as it applies to everything it gates. Six cases, each driving the REAL `critic_gate.py`,
the REAL `build_review_app.sh` marker path and the REAL PreToolUse hook — never a copy of their
logic. `verify_on_device.sh --check-log` is the precedent and states the reason: a test that
reimplements the thing it tests proves the reimplementation.

    A  no verdict at all                    REFUSE
    B  a verdict for a different build      REFUSE  (this is the stale case, and it is the one
                                                     that matters: the commit can be identical)
    C  a FAIL verdict for this build        REFUSE
    D  the same, with YARL_SKIP_CRITIC=1    ALLOW, exit 10 — the caller must stamp the build
    E  a PASS verdict for this build        ALLOW
    F  the hook, on a command that installs REFUSE, and pass a command that does not

Plus the marker: build_review_app.sh under TIER0_MARKER_ONLY writes `reviewStatus` —
SKIPPED-REVIEW when it was waved through, null when it was gated.

⚠ IT MOVES THE REAL CRITIC-VERDICT.json ASIDE and puts it back in a `finally`. Nothing else in
the repo is touched.

⚠ AND DO NOT REDIRECT ITS OUTPUT INTO THE REPO. Any untracked file written into the tree while
the proof is running moves the build id under it, and cases C, E and E3 go red — which is the
mechanism working correctly and the test being wrong. It cost two runs to see. Capture outside
the tree and copy the transcript in afterwards:

    python3 .claude/skills/frame-critic/prove_gate.py > /tmp/GATE-PROOF.txt 2>&1
    cp /tmp/GATE-PROOF.txt .claude/skills/frame-critic/evidence/proofs/

The same is true of the round itself, and it is not a defect in either: a build id that ignored
new files in the tree would be a build id that could not see a new tile.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import build_id as BID                                    # noqa: E402

VERDICT = os.path.join(REPO, "CRITIC-VERDICT.json")
# THE BACKUP LIVES OUTSIDE THE REPO. Parked beside the verdict it would be an untracked file, and
# an untracked file is part of the build id — so the proof would have been changing the very
# number it exists to check. That is the same self-reference build_id.py already had to fix.
BACKUP = os.path.join(tempfile.gettempdir(), "frame-critic-prove-gate-verdict.bak")
GATE = os.path.join(HERE, "critic_gate.py")
HOOK = os.path.join(REPO, ".claude", "hooks", "critic_install_guard.sh")

FAILURES = []


def run(args, env=None, stdin=None, cwd=REPO):
    e = dict(os.environ)
    e.pop("YARL_SKIP_CRITIC", None)
    e.update(env or {})
    p = subprocess.run(args, cwd=cwd, env=e, input=stdin,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def synth(verdict, build_id, extra=None):
    v = {
        "schema": "frame-critic/1", "verdict": verdict, "lane": "prove-gate", "round": 1,
        "surface": "wall", "commit": BID.head(), "build_id": build_id,
        "timestamp": "2026-09-03T00:00:00",
        "plant": {"file": "grey-walls.png", "caught": True},
        "flip_list": ["The wall tops read as dim floor; separate the planes."],
        "seat": {}, "deck": {}, "transcript": "(fixture)",
        "_fixture": "Written by prove_gate.py to drive the gate. Not a round.",
    }
    v.update(extra or {})
    with open(VERDICT, "w") as f:
        json.dump(v, f, indent=1)


def case(name, want_rc, rc, out, want_text=None):
    ok = (rc == want_rc) and (want_text is None or want_text in out)
    print("\n%s %s" % ("PASS " if ok else "FAIL ", name))
    print("      exit %d (wanted %d)%s"
          % (rc, want_rc, "" if want_text is None else "; looked for %r" % want_text))
    for line in out.strip().splitlines():
        print("      | %s" % line)
    if not ok:
        FAILURES.append(name)


def case_silent(name, rc, out):
    """A hook that lets a command through says NOTHING. Silence is the pass condition, and it is
    checked rather than assumed: a hook printing anything on the allow path would be read by the
    harness as a decision."""
    ok = (rc == 0) and not out.strip()
    print("\n%s %s" % ("PASS " if ok else "FAIL ", name))
    print("      exit %d, output %s" % (rc, "(silent)" if not out.strip() else repr(out[:200])))
    if not ok:
        FAILURES.append(name)


def main():
    had = os.path.exists(VERDICT)
    if had:
        shutil.move(VERDICT, BACKUP)
    try:
        bid, _ = BID.build_id()

        # ---- A. nothing to go on ------------------------------------------------------------
        rc, out = run(["python3", GATE])
        case("A  no verdict -> refuse", 1, rc, out, "NO CRITIC VERDICT")

        # ---- B. the stale case ---------------------------------------------------------------
        # THE COMMIT IS IDENTICAL AND THE BUILD IS NOT. That is the whole reason the gate compares
        # a build id rather than a hash: an art session recomposes a family, the pixels change,
        # and `git rev-parse HEAD` says nothing has happened.
        synth("PASS", "a" * 64)
        rc, out = run(["python3", GATE])
        case("B  verdict for another build -> refuse", 1, rc, out, "NOT ABOUT THIS BUILD")

        # ---- C. a real verdict, and it is a no ----------------------------------------------
        synth("FAIL", bid)
        rc, out = run(["python3", GATE])
        case("C  FAIL verdict -> refuse", 1, rc, out, "VERDICT IS FAIL")

        # ---- D. the override, which is loud rather than silent -------------------------------
        rc, out = run(["python3", GATE], env={"YARL_SKIP_CRITIC": "1"})
        case("D  FAIL + YARL_SKIP_CRITIC -> allow, exit 10", 10, rc, out, "SKIPPED-REVIEW")

        # ---- D2. and the marker says so ------------------------------------------------------
        rc, out = run(["tools/tier0_harness/build_review_app.sh"],
                      env={"YARL_SKIP_CRITIC": "1", "TIER0_MARKER_ONLY": "1"})
        case("D2 the marker is stamped SKIPPED-REVIEW", 0, rc, out,
             '"reviewStatus": "SKIPPED-REVIEW"')

        # ---- E. the gate opens ----------------------------------------------------------------
        synth("PASS", bid)
        rc, out = run(["python3", GATE])
        case("E  PASS verdict for this build -> allow", 0, rc, out, "GATE OPEN")

        # ---- G. PASS-INSTALL, and it must be able to REFUSE ----------------------------------
        #
        # RULED (Rafe, 2026-09-08): PASS for a polish round against a seeded reference is
        # "rank above approved_capture AND no unrouted flags". §13.5 — the pass of a new state
        # counts for nothing until the state has been shown to fail, and the three ways it can
        # fail are the three halves of the rule: no reference to be above, not above it, and
        # items left outstanding. All four drive the real gate.
        ROUTED = [{"state": "ROUTED", "item": "wall tops read as noise",
                   "lane": "wall lane", "ruling": "route it - Rafe, fixture"}]

        synth("PASS-INSTALL", bid, {"progress": {"rank_position": 1, "approved_position": 2},
                                    "flip_list": [], "dispositions": []})
        rc, out = run(["python3", GATE])
        case("G1 PASS-INSTALL above the reference, nothing outstanding -> allow",
             0, rc, out, "GATE OPEN")

        synth("PASS-INSTALL", bid, {"progress": {"rank_position": 2, "approved_position": 1},
                                    "flip_list": [], "dispositions": []})
        rc, out = run(["python3", GATE])
        case("G2 PASS-INSTALL BELOW the reference -> refuse", 1, rc, out,
             "requires the build ABOVE the reference")

        synth("PASS-INSTALL", bid, {"progress": {"rank_position": 1, "approved_position": None},
                                    "flip_list": [], "dispositions": []})
        rc, out = run(["python3", GATE])
        case("G3 PASS-INSTALL with NO seeded reference in the deck -> refuse", 1, rc, out,
             "nothing here to be above")

        synth("PASS-INSTALL", bid, {"progress": {"rank_position": 1, "approved_position": 2},
                                    "dispositions": []})
        rc, out = run(["python3", GATE])
        case("G4 PASS-INSTALL with an undispositioned flip -> refuse", 1, rc, out,
             "every outstanding item carries one")

        synth("PASS-INSTALL", bid, {"progress": {"rank_position": 1, "approved_position": 2},
                                    "dispositions": ROUTED})
        rc, out = run(["python3", GATE])
        case("G5 PASS-INSTALL with the flip ROUTED by a quoted ruling -> allow",
             0, rc, out, "GATE OPEN")

        # ---- H. FLAG DISPOSITIONS BY CITATION — the builder's two states ----------------------
        #
        # RULED (Rafe, 2026-09-08): a flag matching an existing route/ruling is ROUTED-ALREADY and
        # must CITE it; a flag whose explanation measures false while the percept stands is
        # MEASURED-FALSE with the percept recorded. The builder may assert either BY CITATION and
        # still never routes a new item. §13.5 — each has to be shown refusing before its pass
        # counts, and the refusals are the citation checks: a clause that does not resolve, an
        # issue that appears nowhere, a measurement with no percept kept.
        P = {"rank_position": 1, "approved_position": 2}

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "ROUTED-ALREADY", "item": "joints fade at full light", "cites": "§13.4.1"}]})
        rc, out = run(["python3", GATE])
        case("H1 ROUTED-ALREADY citing a clause that RESOLVES -> allow", 0, rc, out, "GATE OPEN")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "ROUTED-ALREADY", "item": "x", "cites": "§99.9"}]})
        rc, out = run(["python3", GATE])
        case("H2 ROUTED-ALREADY citing a clause that does NOT resolve -> refuse",
             1, rc, out, "does not resolve")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "ROUTED-ALREADY", "item": "x", "cites": ""}]})
        rc, out = run(["python3", GATE])
        case("H3 ROUTED-ALREADY with NO citation -> refuse", 1, rc, out, "must CITE")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "ROUTED-ALREADY", "item": "x", "cites": "#999999"}]})
        rc, out = run(["python3", GATE])
        case("H4 ROUTED-ALREADY citing an issue that appears nowhere -> refuse",
             1, rc, out, "appears nowhere")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "MEASURED-FALSE", "item": "the falloff is off-centre",
             "measured": "both named points are wall cells; floor asymmetry runs the other way",
             "percept": "the right side does read brighter past three tiles"}]})
        rc, out = run(["python3", GATE])
        case("H5 MEASURED-FALSE with measurement AND percept -> allow", 0, rc, out, "GATE OPEN")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "MEASURED-FALSE", "item": "x", "measured": "numbers"}]})
        rc, out = run(["python3", GATE])
        case("H6 MEASURED-FALSE with no percept recorded -> refuse",
             1, rc, out, "no percept recorded")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "MEASURED-FALSE", "item": "x", "percept": "kept"}]})
        rc, out = run(["python3", GATE])
        case("H7 MEASURED-FALSE with no measurement -> refuse", 1, rc, out, "no measurement")

        # A FLAG FROM ANY SEAT IS AN OUTSTANDING ITEM, even with no flips recorded.
        synth("PASS-INSTALL", bid, {"progress": P, "flip_list": [], "dispositions": [],
                                    "panel": {"seats": 3, "flagged_by": 2}})
        rc, out = run(["python3", GATE])
        case("H8 a seat flagged the build and nothing is disposed -> refuse",
             1, rc, out, "not a majority test")

        # ---- J. THE AUTONOMY AMENDMENT — a cited flip disposes WITHOUT a human return ---------
        #
        # RULED (Rafe, 2026-09-08): "CC routes flags to issues with verified citations. Routing is
        # no longer a human-only act; the citation verifier is the laundering guard." The case the
        # amendment is FOR is J1: a flip that cites a clause which resolves is disposed by the
        # builder, the gate opens, and no human is involved anywhere in it. J2 and J3 are the
        # guard that makes J1 safe — an unresolvable citation and a bare assertion both refuse.
        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "ROUTED", "item": "joints fade at full light", "lane": "#194",
             "cites": "§13.4.1"}]})
        rc, out = run(["python3", GATE])
        case("J1 a flip ROUTED by the builder on a resolvable clause -> allow, no human",
             0, rc, out, "GATE OPEN")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "ROUTED", "item": "x", "lane": "#194", "cites": "§99.9"}]})
        rc, out = run(["python3", GATE])
        case("J2 builder ROUTED citing a clause that does NOT resolve -> refuse",
             1, rc, out, "does not resolve")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "ROUTED", "item": "x", "lane": "#194"}]})
        rc, out = run(["python3", GATE])
        case("J3 builder ROUTED with neither citation nor ruling -> refuse",
             1, rc, out, "neither a verified citation nor a quoted ruling")

        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "ROUTED", "item": "x", "cites": "§13.4.1"}]})
        rc, out = run(["python3", GATE])
        case("J4 ROUTED with no destination lane -> refuse", 1, rc, out, "no destination lane")

        # CLOSED and PARKED still need Rafe's words — they are statements about what a human
        # decided, where routing is a statement about where something belongs.
        synth("PASS-INSTALL", bid, {"progress": P, "dispositions": [
            {"state": "CLOSED", "item": "x", "cites": "§13.4.1"}]})
        rc, out = run(["python3", GATE])
        case("J5 CLOSED by citation alone -> refuse (only Rafe closes)",
             1, rc, out, "only Rafe creates these")

        # ---- K. INSTALL-LATEST — non-regression, not victory ---------------------------------
        #
        # RULED (Rafe, 2026-09-08). The three things the ruling asks to be proved: an EQUAL-RANK
        # build with its exit met installs; a build a MAJORITY ranks below does not; and the
        # guards, plants and citation checks are untouched (every case above still passes).
        #
        # "Equal rank" is one place below the reference — the tie the deck forbids, the same slack
        # §1.2.1 already uses for the asset bar.
        EXIT = {"claim": "the lane's shine is down and the wall-base seam is restored",
                "measured": "specular share 22.4% -> 18.8%; seam lane/flank 0.030 -> 0.639",
                "met": True}
        def seats(*pairs):
            return [{"seat": i + 1, "rank": r, "reference_rank": a, "not_below": r <= a + 1}
                    for i, (r, a) in enumerate(pairs)]

        synth("INSTALL-LATEST", bid, {"progress": {"rank_position": 2, "approved_position": 1},
                                      "item_exit": EXIT, "flip_list": [], "dispositions": [],
                                      "panel": {"seats": 3, "flagged_by": 0, "above_reference": 1,
                                                "per_seat": seats((1, 2), (2, 1), (2, 1))}})
        rc, out = run(["python3", GATE])
        case("K1 EQUAL-RANK build (tied 3 of 3) with its exit met -> allow",
             0, rc, out, "GATE OPEN")

        synth("INSTALL-LATEST", bid, {"progress": {"rank_position": 3, "approved_position": 1},
                                      "item_exit": EXIT, "flip_list": [], "dispositions": [],
                                      "panel": {"seats": 3, "flagged_by": 0, "above_reference": 0,
                                                "per_seat": seats((3, 1), (3, 1), (2, 1))}})
        rc, out = run(["python3", GATE])
        case("K2 a MAJORITY ranks the build below the reference -> refuse",
             1, rc, out, "that is a regression")

        synth("INSTALL-LATEST", bid, {"progress": {"rank_position": 2, "approved_position": 1},
                                      "item_exit": {"claim": "x", "measured": "", "met": True},
                                      "flip_list": [], "dispositions": [],
                                      "panel": {"seats": 3, "flagged_by": 0, "above_reference": 1,
                                                "per_seat": seats((1, 2), (2, 1), (2, 1))}})
        rc, out = run(["python3", GATE])
        case("K3 exit claimed met with NO measurement -> refuse", 1, rc, out, "carries no measurement")

        synth("INSTALL-LATEST", bid, {"progress": {"rank_position": 2, "approved_position": 1},
                                      "item_exit": {"claim": "x", "measured": "n", "met": False},
                                      "flip_list": [], "dispositions": [],
                                      "panel": {"seats": 3, "flagged_by": 0, "above_reference": 1,
                                                "per_seat": seats((1, 2), (2, 1), (2, 1))}})
        rc, out = run(["python3", GATE])
        case("K4 the item's exit NOT met -> refuse", 1, rc, out, "DID THE THING")

        synth("INSTALL-LATEST", bid, {"progress": {"rank_position": 2, "approved_position": None},
                                      "item_exit": EXIT, "flip_list": [], "dispositions": [],
                                      "panel": {"seats": 3, "flagged_by": 0, "per_seat": []}})
        rc, out = run(["python3", GATE])
        case("K5 no seeded reference in the deck -> refuse", 1, rc, out, "nothing here to be level with")

        synth("INSTALL-LATEST", bid, {"progress": {"rank_position": 2, "approved_position": 1},
                                      "item_exit": EXIT, "flip_list": [], "dispositions": [],
                                      "panel": {"seats": 3, "flagged_by": 2, "above_reference": 1,
                                                "per_seat": seats((1, 2), (2, 1), (2, 1))}})
        rc, out = run(["python3", GATE])
        case("K6 a seat flagged the build, nothing disposed -> refuse",
             1, rc, out, "not a majority test")

        # Leave a clean passing verdict behind: the cases below assume one, and a fixture that
        # silently changes the state its successors read is how a proof stops proving.
        synth("PASS", bid)

        # ---- E2. and a gated build carries no stamp -------------------------------------------
        rc, out = run(["tools/tier0_harness/build_review_app.sh"],
                      env={"TIER0_MARKER_ONLY": "1"})
        case("E2 a gated build's marker carries no stamp", 0, rc, out, '"reviewStatus": null')

        # ---- E3. a self-test verdict cannot open the gate --------------------------------------
        # It is a verdict on the JUDGE, produced from a deck whose build slot held a morgue frame.
        # Letting one install would be shipping a build on the strength of a round about a
        # different picture entirely.
        synth("PASS", bid, {"self_test": True})
        rc, out = run(["python3", GATE])
        case("E3 a self-test PASS cannot open the gate", 1, rc, out, "SELF-TEST")

        # ---- E4/E5. A LIVE GUARD BLOCKS; A HISTORICAL REPORT DOES NOT --------------------------
        #
        # RULED (Rafe, 2026-09-03): "fix the gate to block on active guard state, not on the
        # existence of a STALL-REPORT.md file - a historical report must never gate installs;
        # only a live guard does."
        #
        # The old check was `os.path.exists(STALL-REPORT.md)`, and a file's existence is not a
        # fact about the line: the floor lane's five-round-park report sat committed on main
        # after that guard had been RETIRED, and blocked installs for every lane - including
        # this proof, which failed E and E2 for no reason but a stale document on disk.
        #
        # Removing a blocking condition without showing that its replacement still bites is how
        # a gate quietly stops being one, so both directions are proved. Two consecutive VOIDs on
        # this lane are the broken-judge guard's own declared condition.
        lane = (BID._git("rev-parse", "--abbrev-ref", "HEAD").strip() or "detached")
        probes = [os.path.join(HERE, "history", "zz-proof-liveguard-%d.json" % i)
                  for i in (901, 902)]
        try:
            for i, pp in enumerate(probes):
                # A FUTURE timestamp, because history() orders by timestamp and the guard reads
                # the LAST rounds. Backdated probes sort to the front and prove nothing - which
                # is exactly how the first version of this case came back silent.
                json.dump({"lane": lane, "round": 901 + i, "verdict": "VOID",
                           "timestamp": "2099-01-01T00:00:0%d" % i,
                           "note": "synthetic; written and removed by prove_gate.py"},
                          open(pp, "w"), indent=2)
            synth("PASS", bid)
            rc, out = run(["python3", GATE])
            case("E4 a LIVE guard blocks an otherwise-passing build", 1, rc, out,
                 "A LOOP GUARD IS LIVE")
        finally:
            for pp in probes:
                if os.path.exists(pp):
                    os.remove(pp)

        synth("PASS", bid)
        rc, out = run(["python3", GATE])
        case("E5 and it opens again once the guard clears", 0, rc, out)

        # ---- F. the hook, which is the wall around the way past the script --------------------
        synth("FAIL", bid)
        payload = json.dumps({"tool_name": "Bash", "cwd": REPO, "session_id": "prove",
                              "tool_input": {"command":
                                             "xcrun devicectl device install app --device X a.app"}})
        rc, out = run(["bash", HOOK], stdin=payload)
        case("F1 hook denies a raw devicectl install", 0, rc, out, '"permissionDecision": "deny"')

        payload = json.dumps({"tool_name": "Bash", "cwd": REPO, "session_id": "prove",
                              "tool_input": {"command": "dotnet test --filter Category!=Slow"}})
        rc, out = run(["bash", HOOK], stdin=payload)
        case_silent("F2 hook lets non-install work through", rc, out)

        payload = json.dumps({"tool_name": "Bash", "cwd": REPO, "session_id": "prove",
                              "tool_input": {"command":
                                             "tools/tier0_harness/build_review_app.sh --no-install"}})
        rc, out = run(["bash", HOOK], stdin=payload)
        case_silent("F3 hook lets --no-install through", rc, out)

        payload = json.dumps({"tool_name": "Bash", "cwd": REPO, "session_id": "prove",
                              "tool_input": {"command":
                                             "YARL_SKIP_CRITIC=1 tools/tier1_walls/device.sh build"}})
        rc, out = run(["bash", HOOK], stdin=payload)
        case_silent("F4 hook honours the visible override", rc, out)
    finally:
        if os.path.exists(VERDICT):
            os.remove(VERDICT)
        if had:
            shutil.move(BACKUP, VERDICT)

    print("\n" + "=" * 70)
    if FAILURES:
        print("%d CASE(S) DID NOT BEHAVE AS DECLARED:" % len(FAILURES))
        for f in FAILURES:
            print("   * %s" % f)
        return 1
    print("EVERY CASE BEHAVED AS DECLARED. The gate refuses where it says it refuses,")
    print("opens where it says it opens, and the override is visible in the marker.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
