#!/usr/bin/env python3
"""WHICH BUILD IS THIS, EXACTLY — one identifier, used by the critic and by the gate.

    build id = sha256 over (path, git blob sha) for every file in the effective working tree

A commit hash alone cannot answer the question. Art sessions build dirty as a matter of course: a
family is recomposed, a manifest is rewritten, tiles land as untracked PNGs, and the commit does
not move. A gate comparing commits would happily install a build whose pixels had changed since
the verdict, which is the entire failure this mechanism exists to prevent.

TWO INVARIANCES ARE LOAD-BEARING, AND THE FIRST VERSION HAD NEITHER
-------------------------------------------------------------------
It hashed `git diff HEAD` plus the untracked file list, which answers "how does this tree differ
from HEAD" — a different question, and one whose answer moves when nothing about the build does:

  **COMMITTING must not change the id.** Under the diff scheme, committing the exact pixels that
  had just passed produced a different id and the gate refused a build it had approved seconds
  earlier. The verdict would have had to be re-run to land the PR that contained it.

  **STAGING must not change the id either**, for the same reason and one step earlier.

So the id is content-addressed. Every path is reduced to its **git blob sha**, which is the same
value whether the content is committed, staged, or sitting untracked in the worktree — so the id
depends on the bytes that make the build and on nothing else about git's opinion of them.

It is cheap. `git ls-files -s` reports the index blob shas without reading a single file; only
the paths that actually differ from the index, plus untracked ones, are hashed, and those go
through one batched `git hash-object`.

⚠ WHAT IS EXCLUDED, AND WHY IT HAS TO BE — found by `prove_gate.py`, which is what it is for.
--------------------------------------------------------------------------------------------
The first version folded in EVERYTHING, including `CRITIC-VERDICT.json` itself. That file is
untracked when it is first written, so **writing the verdict changed the build id the verdict had
just recorded.** The gate compared them, found them different, and refused — every time, for ever.
Four cases in the gate proof went red on it, all with one signature: `verdict build_id` fixed,
`this working tree` different on every single call.

So the review layer's own artefacts are excluded by name. The list is short, closed, and
deliberately contains nothing anyone builds from:

    CRITIC-VERDICT.json                     the verdict. It describes the build; it is not in it.
    STALL-REPORT.md                         a guard's report. Same.
    .claude/skills/frame-critic/history/    past verdicts. Same.
    …/tier0_harness/REVIEW_BUILD.json       the transient review marker, written by the build
                                            itself and removed on exit. If it moved the id, a
                                            build could not match its own verdict.

**Nothing that reaches the app is on this list**, and nothing may be added to it that does.
"""
import hashlib
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

EXCLUDED = (
    "CRITIC-VERDICT.json",
    "STALL-REPORT.md",
    ".claude/skills/frame-critic/history/",
    "src/Presentation/assets/tier0_harness/REVIEW_BUILD.json",
)


def _git(*args, **kw):
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True, input=kw.get("stdin"))
    return r.stdout if r.returncode == 0 else ""


def head():
    return (_git("rev-parse", "HEAD").strip() or "UNKNOWN")


def _excluded(path):
    return any(path == p or path.startswith(p) for p in EXCLUDED)


def _blob_shas(paths):
    """git blob sha per path, in one process. Missing paths come back as DELETED."""
    live = [p for p in paths if os.path.isfile(os.path.join(REPO, p))]
    out = {p: "DELETED" for p in paths}
    if live:
        res = _git("hash-object", "--stdin-paths", stdin="\n".join(live) + "\n").split()
        for p, sha in zip(live, res):
            out[p] = sha
    return out


def build_id():
    """The identifier. Returns (build_id, detail) where detail says what made it dirty."""
    tree = {}
    for line in _git("ls-files", "-s").splitlines():
        # "<mode> <sha> <stage>\t<path>"
        meta, _, path = line.partition("\t")
        if not path or _excluded(path):
            continue
        parts = meta.split()
        if len(parts) >= 2:
            tree[path] = parts[1]

    # Only the paths that actually differ from the index need reading.
    changed = [p for p in _git("diff", "--name-only").splitlines()
               if p.strip() and not _excluded(p)]
    untracked = [p for p in _git("ls-files", "--others", "--exclude-standard").splitlines()
                 if p.strip() and not _excluded(p)]
    for p, sha in _blob_shas(changed + untracked).items():
        if sha == "DELETED":
            tree.pop(p, None)
        else:
            tree[p] = sha

    h = hashlib.sha256()
    for p in sorted(tree):
        h.update(p.encode())
        h.update(b"\0")
        h.update(tree[p].encode())
        h.update(b"\n")

    detail = {
        "commit": head(),
        "dirty": bool(changed or untracked),
        "files": len(tree),
        "modified": changed[:50],
        "modified_count": len(changed),
        "untracked": untracked[:50],
        "untracked_count": len(untracked),
    }
    return h.hexdigest(), detail


if __name__ == "__main__":
    bid, det = build_id()
    print(bid)
    if "-v" in sys.argv:
        print("commit=%s dirty=%s files=%d modified=%d untracked=%d"
              % (det["commit"], det["dirty"], det["files"], det["modified_count"],
                 det["untracked_count"]), file=sys.stderr)
