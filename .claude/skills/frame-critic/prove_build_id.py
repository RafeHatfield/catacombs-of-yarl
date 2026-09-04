#!/usr/bin/env python3
"""SHOW THE BUILD ID BEHAVING — the three properties the install gate rests on.

    python3 .claude/skills/frame-critic/prove_build_id.py

The gate's whole claim is *this verdict is about THIS build*, and it is only as good as the
identifier behind it. Three properties, and all three have to hold at once:

    1. IT MOVES WHEN THE BUILD MOVES.        A new file in the tree changes it. An identifier
                                             that never changes is not an identifier.
    2. IT DOES NOT MOVE WHEN GIT'S OPINION   Staging the same bytes must not change it. Under the
       MOVES.                                first implementation — a hash of `git diff HEAD` —
                                             committing the exact pixels that had just passed
                                             produced a different id and the gate refused a build
                                             it had approved seconds earlier.
    3. IT IGNORES THE REVIEW LAYER'S OWN     Writing CRITIC-VERDICT.json must not change it, or
       ARTEFACTS.                            writing the verdict invalidates the verdict. That is
                                             not hypothetical: it is what the first version did,
                                             and `prove_gate.py` found it.

Property 2 is checked against a **temporary git index** (`GIT_INDEX_FILE`), so the repository's
real staging area is never touched. Property 1 and 3 write a file into the tree and remove it in
a `finally`.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import build_id as BID                                    # noqa: E402

PROBE = os.path.join(REPO, "frame-critic-build-id-probe.tmp")
VERDICT = os.path.join(REPO, "CRITIC-VERDICT.json")

FAILURES = []


def check(name, ok, detail):
    print("\n%s %s" % ("PASS " if ok else "FAIL ", name))
    print("      %s" % detail)
    if not ok:
        FAILURES.append(name)


def id_with_temp_index():
    """The id as computed against a scratch index with everything staged into it.

    GIT_INDEX_FILE is inherited by every `git` call build_id() makes, which is exactly the point:
    the whole computation runs as if the tree had been staged, and the real index is untouched.
    """
    # THE INDEX IS NOT AT .git/index HERE. This repository is worked in git worktrees, where
    # `.git` is a FILE pointing into the main repository's `worktrees/<name>/` directory — so a
    # hardcoded path copies nothing, `git add -A` runs against an empty scratch index, and
    # `ls-files -s` returns nothing. The id then came back as the sha256 of the empty string and
    # the property looked violated. Ask git where its index is.
    idx = subprocess.run(["git", "-C", REPO, "rev-parse", "--git-path", "index"],
                         capture_output=True, text=True).stdout.strip()
    if not os.path.isabs(idx):
        idx = os.path.join(REPO, idx)
    tmp = tempfile.mkstemp(prefix="frame-critic-index-")[1]
    if os.path.exists(idx):
        shutil.copyfile(idx, tmp)
    old = os.environ.get("GIT_INDEX_FILE")
    try:
        os.environ["GIT_INDEX_FILE"] = tmp
        r = subprocess.run(["git", "-C", REPO, "add", "-A"], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("scratch-index `git add -A` failed: %s" % (r.stderr or r.stdout))
        return BID.build_id()[0]
    finally:
        if old is None:
            os.environ.pop("GIT_INDEX_FILE", None)
        else:
            os.environ["GIT_INDEX_FILE"] = old
        os.unlink(tmp)


def main():
    had_verdict = os.path.exists(VERDICT)
    base, _ = BID.build_id()
    print("baseline build id: %s" % base)

    try:
        # ---- 1. it moves when the build moves --------------------------------------------------
        with open(PROBE, "w") as f:
            f.write("a file that would be in the build\n")
        moved, _ = BID.build_id()
        check("1  a new file in the tree moves the id", moved != base,
              "with probe: %s" % moved)
        os.remove(PROBE)
        back, _ = BID.build_id()
        check("1b removing it puts the id back", back == base, "back to: %s" % back)

        # ---- 2. it does not move when git's opinion moves --------------------------------------
        staged = id_with_temp_index()
        check("2  staging the same bytes does not move the id", staged == base,
              "staged (scratch index): %s" % staged)

        # ---- 3. it ignores the review layer's own artefacts -------------------------------------
        # THE SELF-REFERENCE THAT BROKE THE FIRST VERSION. Writing the verdict must not invalidate
        # the verdict.
        #
        # ⚠ THIS USED TO SKIP ITSELF whenever a real CRITIC-VERDICT.json was on disk — which, once
        # the mechanism had shipped, was always. The most important of the three properties was
        # the one that stopped being checked the moment it started mattering. A real verdict is
        # moved aside and put back instead, the same way prove_gate.py does it.
        stash = None
        if had_verdict:
            stash = os.path.join(tempfile.gettempdir(), "frame-critic-prove-bid-verdict.bak")
            shutil.move(VERDICT, stash)
        try:
            with open(VERDICT, "w") as f:
                f.write('{"verdict": "PASS", "_probe": true}\n')
            with_verdict, _ = BID.build_id()
            check("3  writing CRITIC-VERDICT.json does not move the id", with_verdict == base,
                  "with a verdict on disk: %s" % with_verdict)
        finally:
            if os.path.exists(VERDICT):
                os.remove(VERDICT)
            if stash:
                shutil.move(stash, VERDICT)
    finally:
        if os.path.exists(PROBE):
            os.remove(PROBE)
        if not had_verdict and os.path.exists(VERDICT):
            try:
                import json
                if json.load(open(VERDICT)).get("_probe"):
                    os.remove(VERDICT)
            except Exception:
                pass

    print("\n" + "=" * 70)
    if FAILURES:
        print("%d PROPERTY(IES) DID NOT HOLD:" % len(FAILURES))
        for f in FAILURES:
            print("   * %s" % f)
        return 1
    print("ALL THREE HOLD. The id tracks the build, ignores git's bookkeeping, and does not")
    print("invalidate the verdict that records it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
