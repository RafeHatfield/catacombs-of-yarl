#!/usr/bin/env bash
# PreToolUse guard for git commands. Enforces two CLAUDE.md rules mechanically:
#
#   1. Branch -> PR -> merge. No direct commits or pushes to main.
#   2. One working copy per session. A second session must not move HEAD or
#      stage files in a working copy another session is already holding.
#
# Reads the hook payload on stdin, emits a PreToolUse deny decision on violation
# and stays silent otherwise. Fails open: any unexpected state exits 0.

set -u

MAIN_BRANCH="main"
LOCK_STALE_SECONDS=7200 # another session's lock older than this is treated as dead

payload=$(cat)
cmd=$(printf '%s' "$payload" | jq -r '.tool_input.command // ""')
cwd=$(printf '%s' "$payload" | jq -r '.cwd // "."')
sid=$(printf '%s' "$payload" | jq -r '.session_id // "unknown"')

[ -n "$cmd" ] || exit 0
cd "$cwd" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

deny() {
  jq -n --arg r "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $r
    }
  }'
  exit 0
}

# Strip quoted strings so commit messages and PR bodies can mention "main"
# without tripping the ref checks below.
scan=$(printf '%s' "$cmd" | sed "s/'[^']*'//g; s/\"[^\"]*\"//g")

# Only inspect commands that actually invoke git.
printf '%s' "$scan" | grep -Eq '(^|[;&|]|[[:space:]])git[[:space:]]' || exit 0

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

# Split into independently-evaluated segments. One Bash call routinely chains
# unrelated commands, and a rule must only see the arguments of the invocation it
# is judging: `git push my-branch && gh pr create --base main` is legitimate, but
# scanning it whole makes the PR target look like the push target.
segments=$(printf '%s' "$scan" | tr '\n' ';' | sed 's/&&/;/g; s/||/;/g; s/|/;/g' | tr ';' '\n')

is_git_subcmd() { # $1 = segment, $2 = subcommand
  printf '%s' "$1" | grep -Eq "(^|[[:space:]])git([[:space:]]+-[^[:space:]]+)*[[:space:]]+$2([[:space:]]|$)"
}

# --- Rule 2 prerequisites (evaluated once) -----------------------------------

git_dir=$(git rev-parse --absolute-git-dir 2>/dev/null) || exit 0
lock="${git_dir}/claude-session.lock"
now=$(date +%s)
holder=""
age=0

if [ -f "$lock" ]; then
  holder=$(head -n1 "$lock" 2>/dev/null | cut -d' ' -f1)
  held_at=$(head -n1 "$lock" 2>/dev/null | cut -d' ' -f2)
  case "$held_at" in ''|*[!0-9]*) held_at=0 ;; esac
  age=$((now - held_at))
  if [ "$holder" = "$sid" ] || [ "$age" -ge "$LOCK_STALE_SECONDS" ]; then
    holder=""
  fi
fi

while IFS= read -r seg; do
  [ -n "$seg" ] || continue
  printf '%s' "$seg" | grep -Eq '(^|[[:space:]])git[[:space:]]' || continue

  # --- Rule 1: no direct commits or pushes to main ---------------------------

  if is_git_subcmd "$seg" push; then
    # Explicit main ref: `origin main`, `HEAD:main`, `:main`, `--set-upstream origin main`
    if printf '%s' "$seg" | grep -Eq "(^|[[:space:]:])${MAIN_BRANCH}([[:space:]]|$)"; then
      deny "Blocked: pushes to ${MAIN_BRANCH} are not allowed (CLAUDE.md: Branch -> PR -> merge). Push the feature branch and open a PR instead — CI status has to be visible before merge (FIND-006)."
    fi
    # Bare `git push` while sitting on main pushes main.
    if [ "$branch" = "$MAIN_BRANCH" ]; then
      deny "Blocked: HEAD is on ${MAIN_BRANCH}, so this push would land directly on ${MAIN_BRANCH} (CLAUDE.md: Branch -> PR -> merge). Create a branch first."
    fi
  fi

  if [ "$branch" = "$MAIN_BRANCH" ]; then
    for sub in commit merge rebase "cherry-pick" revert; do
      if is_git_subcmd "$seg" "$sub"; then
        deny "Blocked: 'git ${sub}' on ${MAIN_BRANCH} would create commits directly on ${MAIN_BRANCH} (CLAUDE.md: no direct commits to ${MAIN_BRANCH}). Branch first, then open a PR."
      fi
    done
  fi

  # --- Rule 2: one working copy per session ----------------------------------

  if [ -n "$holder" ]; then
    for sub in commit checkout switch reset stash add rm restore merge rebase "cherry-pick" push; do
      if is_git_subcmd "$seg" "$sub"; then
        deny "Blocked: another Claude Code session (${holder}, active ${age}s ago) is already holding this working copy. Two sessions sharing one checkout is how M1.4's item 1 got carried into ${MAIN_BRANCH} on an unrelated art PR. Use EnterWorktree for an isolated copy, or wait for that session to finish. To override a session you know is dead: rm '${lock}'"
      fi
    done
  fi
done <<SEGMENTS
$segments
SEGMENTS

# Claim / refresh the lock for this session.
printf '%s %s\n' "$sid" "$now" >"$lock" 2>/dev/null || true

exit 0
