---
name: create-issue
description: Use when creating, filing, or opening a GitHub issue or ticket for Catacombs of YARL — covers the required native issue Type, thread label, milestone, sub-issue structure, and body discipline. Also use when correcting an existing issue's labels, Type, or milestone.
---

# Issue / ticket creation contract

All work tracking lives in GitHub Issues + the "Catacombs of Yarl — Release"
Project board. When creating any issue, follow this exactly. Do not
reintroduce the taxonomy this replaces.

**Type — use the native issue Type, not a label.**
Set Type to one of `Bug`, `Feature`, `Task`. After creating the issue:

```bash
gh issue create --repo RafeHatfield/catacombs-of-yarl \
  --title "…" --body "…" --milestone "…" --label "thread:<name>"
# then set native Type (works on any gh version):
gh api -X PATCH repos/RafeHatfield/catacombs-of-yarl/issues/<N> -f type="Feature"
```

If this gh version supports `gh issue create --type "Feature"`, that shortcut
is equivalent and preferred. **Never create or apply `type:feature`,
`type:bug`, or `type:task` labels** — those label definitions have been
deleted; native Type is the single source of truth for those three.

**Story / idea — these stay as labels** (native Type covers only bug/feature/
task): apply `type:story` or `type:idea` where they apply. Epic→story→task
structure uses native sub-issues (`--parent`), or a `parent: #N` body note
plus post-hoc linking if this gh version lacks `--parent`.

**Thread — apply exactly one `thread:*` label** (`thread:foundation|voice|
launch|combat|spine|art`). Do **not** attempt to set the Project "Thread"
field yourself — `gh issue create` cannot write Project fields. A workflow
(`.github/workflows/set-thread-field.yml`) reads the label and populates the
field automatically. Your only obligation is the correct label; the field
follows. Every issue must carry exactly one thread label so the workflow can
resolve it.

**Milestone — assign one** where the work maps to `M1–M7`. Leave unset only
when the roadmap genuinely provides no home (e.g. most art-conformance work),
and flag that rather than guessing.

**Meta labels** as applicable: `exit-gate`, `blocked`, `needs-ruling`.

**Cross-cutting work files to Foundation.** If an issue spans threads, it
carries `thread:foundation` and names the coordination in its body — never a
second thread label, and never a duplicate issue under the other thread.
Reference the Foundation issue number from dependent threads instead.

**Body discipline:** current factual state only — no historical narrative.
2–5 lines: current state, exit condition, and a link to the relevant
`ROADMAP_release_2026-07.md` section or rubric file. Gate *definitions* live
in the roadmap; issues carry live *state*. Do not duplicate definitions.
