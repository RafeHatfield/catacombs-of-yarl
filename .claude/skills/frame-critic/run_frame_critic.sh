#!/bin/zsh
# ONE COMMAND, END TO END: capture the build, assemble the deck, seat a blind critic, write the
# verdict.
#
#   .claude/skills/frame-critic/run_frame_critic.sh
#   .claude/skills/frame-critic/run_frame_critic.sh --no-capture      # replay on the frame on disk
#   .claude/skills/frame-critic/run_frame_critic.sh --build-frame <p> # the plant self-test
#
# What it captures, what it crops, which frame Rafe last approved and where the asset bar lives
# are all in docs/FRAME-CRITIC.json. Nothing content-specific lives in this skill.
#
# EXIT: 0 PASS · 1 FAIL · 2 VOID · 3 STOP (a loop guard fired; read STALL-REPORT.md) · 4 refused
set -e
HERE="${0:A:h}"
REPO="${HERE:h:h:h}"
cd "$REPO"

# The seat is a fresh `claude -p` (LOOP-PROCESS §3.1). Nothing else in the round needs it, and a
# missing binary should say so here rather than three minutes into a capture.
command -v claude >/dev/null 2>&1 || {
  echo "no \`claude\` on PATH — the blind seat is a fresh claude -p process (LOOP-PROCESS §3.1)." >&2
  exit 4
}

exec python3 "$HERE/frame_critic.py" "$@"
