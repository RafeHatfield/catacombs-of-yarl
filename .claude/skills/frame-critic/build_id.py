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
    PARK-CLEARED.json                       a ruling that clears a guard. Same: it describes a
                                            decision about the lane, and reaches no pixel.
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

# ══════════════════════════════════════════════════════════════════════════════════════════════
# THE ID HASHES SHIPPED INPUTS ONLY — RULED (Rafe, 2026-09-07). Bible §13.11, THIRD INSTANCE.
#
# **A hash broader than the thing it identifies measures the repo, not the build.**
#
# The occasion: a round returned a verdict, the human gate dispositioned every flip and ruled
# PASS-WITH-ROUTED-ITEMS — and the install refused, because ACTING ON THAT RULING had edited
# `frame_critic.py` and `ART-BIBLE-v0.md`. The delivered frame was byte-identical (8745c556), no
# game source, asset, shader or scene config had moved, and the gate still said "something has
# changed since the seat looked". Something had: the judge's own source and the documentation.
# Neither is in the build. **Implementing a ruling about a round invalidated that round's verdict.**
#
# The list below already carried the principle for the review layer's ARTEFACTS, in its own words:
# *they describe the build; they are not in it.* The review layer's SOURCE, and the docs, are the
# same category. This is that principle applied consistently rather than a new licence.
#
# WHAT IS HASHED: game source, assets, shaders, scene and theme configs, and the build scripts
# that affect the output — everything whose bytes can reach a pixel on the handset.
#
# ⚠ WHY A BLACKLIST AND NOT A WHITELIST, since "shipped inputs only" is whitelist language.
# The two fail in opposite directions and only one of them is survivable. A whitelist that forgets
# a shipped directory produces an id that does NOT move when the build does — the gate goes blind
# and says nothing. A blacklist that forgets a non-shipped directory produces an id that moves when
# it needn't — the gate is noisy and refuses a build it should have passed, which is what happened
# here and which is loud, visible and fixable in one line. **The failure mode is chosen, not
# inherited:** anything new in this repository counts toward the id until someone names it.
EXCLUDED = (
    # the review layer's ARTEFACTS — they describe the build
    "CRITIC-VERDICT.json",
    "STALL-REPORT.md",
    "PARK-CLEARED.json",
    "SEAT-REDRAWN.json",          # a ruling that re-draws one seat. Same: it describes a round.
    "GATE-RULING.json",
    # the review layer's SOURCE — the judge, its morgue, its controls, its law. Ruled
    # 2026-09-07. `.claude/skills/frame-critic/history/` was already here and is subsumed;
    # it is kept above in spirit by this broader prefix.
    ".claude/skills/",
    # documentation. The bible and the process law govern the build and are not in it, and a
    # ruling is almost always written down in the same breath as it is applied.
    "docs/",
    # the review build's own marker, written by the build script and removed after
    "src/Presentation/assets/tier0_harness/REVIEW_BUILD.json",
    # ── THE RUN'S OWN REPORTS — added 2026-09-08 under LOOP-PROCESS §1.1.5.2 ─────────────────
    #
    # A hash exclusion is ENGINEERING, not an escalation, and the law it is fixed under is the one
    # already in this list's own words: *they describe the build; they are not in it.* A report is
    # the archetype of that, and `a historical report never gates` is settled law.
    #
    # THE OCCASION, and it cost a night. `POLISH-REPORT.md` is the morning deliverable a run is
    # REQUIRED to write, and writing it after a round moved the build id, so the round's verdict
    # stopped describing the tree and the install refused. The report had reached no pixel. The
    # loop then escalated a hash to a human, which §1.1.4 now names as the defect.
    #
    # ⚠ SCOPED TO NAMED FILES, NEVER A PATTERN. `*.md` at the root would swallow anything anyone
    # dropped there, and the blacklist's chosen failure direction is an id that moves NEEDLESSLY
    # rather than one that fails to move — so each report is named, and `prove_build_id.py` case 6
    # holds the line by requiring that an unnamed root file STILL moves the id.
    "POLISH-REPORT.md",
    "RUN-REPORT.md",
    # The routing table is the record the amendment made auditable: `critic_gate` resolves a
    # ROUTED citation against it, and Rafe audits it at the walk. It describes where flags
    # went; it reaches no pixel. Named, like the reports, never a pattern.
    "ROUTING-TABLE.json",
)

# ── CAPTURE LOGS ARE RECORDS OF A BUILD, NOT INPUTS TO ONE — added 2026-09-08 ────────────────
#
# A capture log carries DIAG frame timings: `[DIAG 00000 F0 T1.121] === Session started ===`
# becomes `T3.588` on the next run of the same build. Re-capturing byte-identical pixels
# therefore moved the build id, and a verdict stopped describing its own tree over wall-clock
# noise. Measured: combined.png byte-identical at 839fb12f, combined.log 29 lines changed, every
# one of them a timing.
#
# §13.11 — an instrument's input must be no wider than the thing it measures. The id measures the
# BUILD; a log measures the RUN that produced a capture of it.
#
# ⚠ THE PNG STAYS HASHED, and that is what keeps this narrow. A shader, scene or asset change
# moves the delivered pixels and so moves the id; only the log's own timings fall out. The
# verdict pins the frame separately by sha in `build_frame`, so nothing about which pixels were
# judged rests on this.
def _is_capture_log(path):
    return path.endswith(".log") and "/evidence/" in path


def _git(*args, **kw):
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True, input=kw.get("stdin"))
    return r.stdout if r.returncode == 0 else ""


def head():
    return (_git("rev-parse", "HEAD").strip() or "UNKNOWN")


def _excluded(path):
    """A directory entry (trailing slash) excludes its subtree; a file entry excludes ITSELF.

    ⚠ IT USED TO PREFIX-MATCH EVERYTHING, and that quietly excluded a shipped input. The entry
    `src/Presentation/assets/tier0_harness/REVIEW_BUILD.json` names the GENERATED marker, which is
    written before the export and deleted after and is correctly ignored — but `startswith` also
    swallowed `REVIEW_BUILD.json.template`, which is the file that DECIDES WHAT THE DEVICE SHOWS:
    its scene, its theme, every family manifest, the rig values and the void ring. Editing it moved
    no id at all, so the gate was blind to a real change in what ships.

    That is the exact failure direction the 2026-09-07 ruling chose against — an id that does not
    move when the build does says nothing, where an id that moves needlessly is loud and fixable.
    Found by testing the narrowed id rather than by reading it: the ruling asked for a control that
    a scene config MUST move the id, and the template is one.
    """
    if _is_capture_log(path):
        return True
    for p in EXCLUDED:
        if p.endswith("/"):
            if path.startswith(p):
                return True
        elif path == p:
            return True
    return False


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
