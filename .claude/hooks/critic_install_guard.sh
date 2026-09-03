#!/usr/bin/env bash
# PreToolUse guard: no build reaches the phone without a frame-critic verdict for that build.
#
# WHY A HOOK EXISTS AS WELL AS THE SCRIPT CHECK. `build_review_app.sh` already calls
# `critic_gate.py` and refuses. A gate living only inside the thing it gates is one `xcrun
# devicectl device install` away from being decorative — and this repo's whole ledger of process
# failures is rules that depended on being remembered. The script check is the gate; this is the
# wall around the way past it.
#
# It matches only the commands that PUT SOMETHING ON A DEVICE. Building, capturing, testing and
# every other shell command pass straight through: the eyes-only rule governs art rounds, and
# gating non-art work would teach everyone to disable the hook.
#
# Fails OPEN. Any unexpected state exits 0 — a guard that blocks the session when jq is missing
# is a guard that gets removed.

set -u

payload=$(cat)
cmd=$(printf '%s' "$payload" | jq -r '.tool_input.command // ""' 2>/dev/null) || exit 0
cwd=$(printf '%s' "$payload" | jq -r '.cwd // "."' 2>/dev/null) || exit 0

[ -n "$cmd" ] || exit 0
cd "$cwd" 2>/dev/null || exit 0

toplevel=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
GATE="$toplevel/.claude/skills/frame-critic/critic_gate.py"
[ -f "$GATE" ] || exit 0

# The override is honoured here too, and for the same reason it is honoured in the script: a
# blocked-and-unbypassable gate gets disabled wholesale, and a disabled gate protects nothing.
# The build it produces is stamped SKIPPED-REVIEW and says so on the phone.
printf '%s' "$cmd" | grep -q 'YARL_SKIP_CRITIC=1' && exit 0

# WHAT COUNTS AS AN INSTALL. Named explicitly rather than by a broad pattern, because a guard
# that fires on the wrong thing is a guard the operator learns to work around.
#   build_review_app.sh    the review-build path (its own --no-install form is allowed through)
#   device.sh build        a session's own slot on the handset
#   ios_build.sh           the export/install chain underneath both
#   devicectl … install    the raw install, which is the way past all three
scan=$(printf '%s' "$cmd" | sed "s/'[^']*'//g; s/\"[^\"]*\"//g")
installs=0
printf '%s' "$scan" | grep -Eq 'devicectl[[:space:]].*[[:space:]]install' && installs=1
printf '%s' "$scan" | grep -Eq '(ios_build\.sh|build_review_app\.sh)' && installs=1
printf '%s' "$scan" | grep -Eq 'device\.sh[[:space:]]+build' && installs=1
# --no-install builds nothing onto a device and is explicitly allowed: a build you cannot walk is
# still worth compiling, and blocking it only teaches the operator to reach for the override.
printf '%s' "$scan" | grep -q -- '--no-install' && installs=0
[ "$installs" = "1" ] || exit 0

# 0 = clear, 10 = refused but YARL_SKIP_CRITIC is set in the environment rather than written into
# the command. Both let the command through; 10's build carries the SKIPPED-REVIEW stamp.
out=$(python3 "$GATE" 2>&1); rc=$?
[ "$rc" = "0" ] || [ "$rc" = "10" ] && exit 0

jq -n --arg r "$out" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: ("This command installs a build to the device, and the frame-critic gate refuses it.\n\n" + $r + "\n\nArt rounds are judged by eyes on delivered frames (CLAUDE.md). Run the round, or prefix the command with YARL_SKIP_CRITIC=1 to install a build stamped SKIPPED-REVIEW.")
  }
}'
exit 0
