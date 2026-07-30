#!/usr/bin/env bash
# SessionStart hook. Claims this working copy for the session and warns loudly
# if another live session already holds it, before any work is done in it.
#
# Enforcement of the rule lives in guard-git.sh; this exists so the collision is
# visible at session start rather than at the first blocked git command.

set -u

LOCK_STALE_SECONDS=7200

payload=$(cat)
cwd=$(printf '%s' "$payload" | jq -r '.cwd // "."')
sid=$(printf '%s' "$payload" | jq -r '.session_id // "unknown"')

cd "$cwd" 2>/dev/null || exit 0
git_dir=$(git rev-parse --absolute-git-dir 2>/dev/null) || exit 0

lock="${git_dir}/claude-session.lock"
now=$(date +%s)

if [ -f "$lock" ]; then
  holder=$(head -n1 "$lock" 2>/dev/null | cut -d' ' -f1)
  held_at=$(head -n1 "$lock" 2>/dev/null | cut -d' ' -f2)
  case "$held_at" in ''|*[!0-9]*) held_at=0 ;; esac
  age=$((now - held_at))

  if [ -n "$holder" ] && [ "$holder" != "$sid" ] && [ "$age" -lt "$LOCK_STALE_SECONDS" ]; then
    msg="Another Claude Code session (${holder}) touched this working copy ${age}s ago. CLAUDE.md requires one working copy per session — use EnterWorktree before editing, or confirm that session is finished."
    jq -n --arg m "$msg" '{
      systemMessage: $m,
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: ("WORKING COPY CONTESTED. " + $m + " Do not edit or run git state-changing commands in this checkout until resolved; git commands are blocked by the guard-git hook while the other session stays active.")
      }
    }'
    exit 0
  fi
fi

printf '%s %s\n' "$sid" "$now" >"$lock" 2>/dev/null || true
exit 0
