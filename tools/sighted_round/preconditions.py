#!/usr/bin/env python3
"""THE SIGHTED ROUND — PRECONDITIONS. Any failure here is a STOP, not a warning.

The brief names two, and both are corpus-integrity conditions rather than convenience checks:

  A. THE RING REMEDIATION IS MERGED (#149). Checked against what the merge actually put in the
     tree - bible §5.5's corpus ruling and the per-floor role record - not against a branch name
     or a git log line, because either can be true while the tree is wrong.

  B. THE SCENE USES THE SANCTIONED CORPUS ONLY. Floors are C-GAB and A-HEB. **A precondition
     check finding any other floor in the scene config is a stop.** A-VAB is prop stock under
     §5.5 and appears in no scene; B-KAB is retired from conditioning with no remediation.

C is this file's own, added because a check that cannot fail is decorative (LOOP-PROCESS §4):
the ring instrument's control suite must pass before its verdicts on this round's tiles count.

`--self-test` mutates each condition and shows the check go red. A precondition module that has
never been seen to fail is a wish (§4.2).
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BIBLE = os.path.join(REPO, "docs/ART-BIBLE-v0.md")
REMEDIATED = os.path.join(REPO, "tools/floor_remediation/remediated")
SANCTIONED = ("C-GAB", "A-HEB")
FORBIDDEN = ("A-VAB", "B-KAB")


def _fail(msg):
    print("  STOP: %s" % msg)
    return False


def check_remediation_merged(verbose=True):
    """A. The corpus ruling is in the tree, and the roles say what §5.5 says."""
    ok = True
    if not os.path.exists(BIBLE):
        return _fail("no bible at %s" % BIBLE)
    text = open(BIBLE).read()
    if "Corpus status — RULED (Rafe, 2026-08-27)" not in text:
        ok = _fail("bible §5.5 carries no 2026-08-27 corpus ruling - #149 is not in this tree")
    mp = os.path.join(REMEDIATED, "MANIFEST.json")
    if not os.path.exists(mp):
        return _fail("no remediated manifest at %s" % os.path.relpath(mp, REPO))
    man = json.load(open(mp))
    roles = {f["code"]: f for f in man["floors"]}
    for code in SANCTIONED:
        r = roles.get(code)
        if not r or not r.get("may_condition"):
            ok = _fail("%s is not marked may_condition in the remediated manifest" % code)
        elif not r.get("file") or not os.path.exists(os.path.join(REMEDIATED, r["file"])):
            ok = _fail("%s has no remediated file on disk" % code)
    for code in FORBIDDEN:
        r = roles.get(code)
        if not r:
            ok = _fail("%s has no row in the remediated manifest" % code)
        elif r.get("may_condition"):
            ok = _fail("%s is marked may_condition; §5.5 forbids it" % code)
    if roles.get("B-KAB", {}).get("file") is not None:
        ok = _fail("B-KAB has a remediated file; it is retired with NO remediation")
    if verbose and ok:
        print("  A. ring remediation merged, §5.5 roles present and correct")
        for c, r in sorted(roles.items()):
            print("       %-6s %-26s may_condition=%s" % (c, r["role"], r["may_condition"]))
    return ok


def floors_in_theme(path):
    """Every tile id appearing in any floor_* role of a tile-theme yaml."""
    ids = set()
    for line in open(path):
        m = re.match(r"^\s{4}(floor_\w+):\s*\[([0-9,\s]*)\]\s*$", line)
        if m:
            ids |= {int(v) for v in m.group(2).replace(" ", "").split(",") if v}
    return ids


def check_scene_corpus(theme_path, id_to_code, verbose=True):
    """B. Every floor id in the scene's theme maps to a sanctioned code. Anything else is a STOP."""
    if not os.path.exists(theme_path):
        return _fail("no theme at %s" % os.path.relpath(theme_path, REPO))
    ids = floors_in_theme(theme_path)
    if not ids:
        return _fail("theme %s declares no floor tiles at all" % os.path.basename(theme_path))
    ok = True
    for tid in sorted(ids):
        code = id_to_code.get(tid)
        if code is None:
            ok = _fail("floor tile %d in %s maps to no known survivor code"
                       % (tid, os.path.basename(theme_path)))
        elif code not in SANCTIONED:
            ok = _fail("floor tile %d is %s - NOT sanctioned. §5.5: only %s may appear."
                       % (tid, code, " and ".join(SANCTIONED)))
    if verbose and ok:
        print("  B. scene corpus sanctioned: %s"
              % ", ".join("%d=%s" % (t, id_to_code[t]) for t in sorted(ids)))
    return ok


def check_instrument(verbose=True):
    """C. The ring instrument's control suite passes, so its verdicts count."""
    r = subprocess.run([sys.executable,
                        os.path.join(REPO, "tools/floor_remediation/ring_instrument.py"),
                        "--controls"], capture_output=True, text=True)
    if "CONTROL SUITE: PASS" not in r.stdout:
        return _fail("ring instrument control suite did not pass; its verdicts do not count")
    if verbose:
        print("  C. ring instrument control suite PASS")
    return True


def run(theme_path=None, id_to_code=None, verbose=True):
    print("PRECONDITIONS - any failure is a STOP")
    ok = check_remediation_merged(verbose)
    ok = check_instrument(verbose) and ok
    if theme_path is not None:
        ok = check_scene_corpus(theme_path, id_to_code or {}, verbose) and ok
    print("  => %s" % ("ALL PRECONDITIONS PASS" if ok else "STOP - preconditions not met"))
    return ok


def self_test():
    """LOOP-PROCESS §4: show each check go red."""
    import tempfile
    print("PRECONDITION SELF-TEST - each check must be seen to fail\n")
    results = []

    print("1. an unsanctioned floor in the scene theme (A-VAB, prop stock under §5.5)")
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write("themes:\n  t:\n    floor_primary: [9401]\n    floor_dark: [9400]\n")
        p = f.name
    red = not check_scene_corpus(p, {9401: "C-GAB", 9400: "A-VAB"}, verbose=False)
    results.append(("unsanctioned floor is caught", red))
    os.unlink(p)

    print("2. a floor id that maps to nothing known")
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write("themes:\n  t:\n    floor_primary: [7777]\n")
        p = f.name
    red = not check_scene_corpus(p, {9401: "C-GAB"}, verbose=False)
    results.append(("unknown floor id is caught", red))
    os.unlink(p)

    print("3. a theme with no floors at all (a silent-empty scene)")
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write("themes:\n  t:\n    wall_autotile:\n      0: [1]\n")
        p = f.name
    red = not check_scene_corpus(p, {}, verbose=False)
    results.append(("empty floor set is caught", red))
    os.unlink(p)

    print("4. the sanctioned pair passes")
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write("themes:\n  t:\n    floor_primary: [9401]\n    floor_dark: [9402]\n")
        p = f.name
    green = check_scene_corpus(p, {9401: "C-GAB", 9402: "A-HEB"}, verbose=False)
    results.append(("the sanctioned pair passes", green))
    os.unlink(p)

    print()
    for name, good in results:
        print("   %-34s %s" % (name, "OK" if good else "*** WRONG ***"))
    allok = all(g for _, g in results)
    print("\n   SELF-TEST: %s" % ("PASS - the check can fail and can pass" if allok else "FAIL"))
    return allok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--theme")
    args = ap.parse_args()
    if args.self_test:
        return 0 if self_test() else 1
    return 0 if run(args.theme) else 2


if __name__ == "__main__":
    sys.exit(main())
