#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# bot-analysis.sh — one-command bot-analysis cadence run
#
# Generates an enriched bot-run transcript batch (fresh harness per run, so
# entity IDs stay deterministic and transcripts are replay-valid), then runs
# the Analyst predicate pipeline and writes findings.md + aggregate.json.
#
# Usage:
#   ./scripts/bot-analysis.sh [OPTIONS]
#
# Options:
#   --runs N        Number of bot runs  (default: 300)
#   --seed N        Fixed base seed — same N games every invocation (regression mode)
#                   (default: 1337)
#   --explore       Vary the base seed using the current epoch second, so each
#                   invocation samples fresh games (exploration mode)
#   --floors N      Floors per run     (default: 10)
#   --out DIR       Output root directory (default: reports/bot-analysis)
#   -h / --help     Show this message
#
# Seed modes:
#   Default (fixed seed): every run of this script plays the same N games.
#   Good for regression — compare successive findings.md files with the same
#   population. Run counts above the seed space don't loop; seeds are
#   baseSeed+0 through baseSeed+N-1, so N ≤ ~2 billion is safe.
#
#   --explore: base seed = $(date +%s). Every invocation draws fresh games;
#   good for coverage sweeps or spotting intermittent issues. Results are not
#   directly comparable across invocations.
#
# Exit codes:
#   0   Clean batch — no bug candidates found
#   1   Tool error (build failure, bad argument, missing file)
#   2   Bug candidates found — review findings.md
#
# Example — regression baseline (default):
#   ./scripts/bot-analysis.sh
#
# Example — exploration sweep, 500 runs:
#   ./scripts/bot-analysis.sh --runs 500 --explore
#
# Example — quick smoke, custom output:
#   ./scripts/bot-analysis.sh --runs 20 --out /tmp/smoke
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

RUNS=300
SEED=1337
FLOORS=10
OUT="reports/bot-analysis"
EXPLORE=0

RUBRIC="config/rubric/v1.yaml"
HARNESS_PROJ="tools/Harness"
ANALYST_PROJ="tools/Analyst"

usage() {
    sed -n '/^# Usage:/,/^# ───/p' "$0" | grep '^#' | sed 's/^# \?//'
    exit 0
}

die() { echo "ERROR: $*" >&2; exit 1; }

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --runs)    RUNS="$2";    shift 2 ;;
        --seed)    SEED="$2";    shift 2 ;;
        --explore) EXPLORE=1;    shift ;;
        --floors)  FLOORS="$2";  shift 2 ;;
        --out)     OUT="$2";     shift 2 ;;
        -h|--help) usage ;;
        *) die "Unknown option: $1" ;;
    esac
done

if [[ $EXPLORE -eq 1 ]]; then
    SEED=$(date +%s)
    echo "Exploration mode: base seed = ${SEED} (epoch second)" >&2
fi

# ── Resolve paths relative to the repo root (script works from any cwd) ──────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

[[ -f "$RUBRIC" ]] || die "Rubric not found: $RUBRIC (run from repo root or check the path)"

TRANSCRIPT_DIR="${OUT}/transcripts"
FINDINGS="${OUT}/findings.md"
AGGREGATE_JSON="${OUT}/aggregate.json"

mkdir -p "$TRANSCRIPT_DIR"
echo "─────────────────────────────────────────────────────" >&2
echo "Bot analysis run" >&2
echo "  runs:     $RUNS" >&2
echo "  seed:     $SEED  ($([ $EXPLORE -eq 0 ] && echo 'regression' || echo 'exploration'))" >&2
echo "  floors:   $FLOORS" >&2
echo "  out:      $OUT" >&2
echo "─────────────────────────────────────────────────────" >&2

# ── Step 1: generate transcripts ──────────────────────────────────────────────
# Fresh harness per run is enforced by the Harness CLI (each --llm-transcript run
# builds a new DungeonFloorBuilder). Do not add batching here; that would pool
# the harness and drift entity IDs.
echo "[1/2] Generating ${RUNS} transcripts (floors=${FLOORS}, seed=${SEED})..." >&2
dotnet run --project "$HARNESS_PROJ" -c Release -- \
    --dungeon \
    --llm-transcript "$TRANSCRIPT_DIR" \
    --floors "$FLOORS" \
    --runs "$RUNS" \
    --seed "$SEED"

TRANSCRIPT_COUNT=$(find "$TRANSCRIPT_DIR" -name "*.jsonl" | wc -l | tr -d ' ')
echo "  generated: ${TRANSCRIPT_COUNT} transcripts" >&2

# ── Step 2: analyze ───────────────────────────────────────────────────────────
echo "[2/2] Analyzing with Analyst predicate pipeline..." >&2
dotnet run --project "$ANALYST_PROJ" -c Release -- \
    --batch "$TRANSCRIPT_DIR" \
    --rubric "$RUBRIC" \
    --aggregate "$FINDINGS" \
    --aggregate-json "$AGGREGATE_JSON"

ANALYST_EXIT=$?

echo "─────────────────────────────────────────────────────" >&2
echo "Output:" >&2
echo "  findings:  $FINDINGS" >&2
echo "  aggregate: $AGGREGATE_JSON" >&2

# Exit code mirrors the Analyst:
#   0 = clean batch
#   2 = bug candidates found
# (exit 1 is a tool error; set -e handles that above)
exit $ANALYST_EXIT
