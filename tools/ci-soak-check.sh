#!/bin/bash
# CI soak regression check
# Run the dungeon soak, save JSONL, generate a report, and check key thresholds.
# Exit non-zero if any regression threshold is exceeded.
#
# Usage: bash tools/ci-soak-check.sh
# Must be run from the project root (the directory containing config/).
set -euo pipefail

FLOORS=6
RUNS=100
SEED=1337
REPORT_DIR=reports
mkdir -p "$REPORT_DIR"

echo "Running dungeon soak: $RUNS runs, $FLOORS floors, seed $SEED"
dotnet run --project tools/Harness -- \
    --dungeon --floors $FLOORS --runs $RUNS --seed $SEED \
    --jsonl "$REPORT_DIR/ci_soak.jsonl" \
    --report > "$REPORT_DIR/ci_soak_report.txt"

echo "Report saved to $REPORT_DIR/ci_soak_report.txt"
cat "$REPORT_DIR/ci_soak_report.txt"

# ─── Threshold checks via jq ──────────────────────────────────────────────────
# jq is standard on most CI environments (GitHub Actions, CircleCI, etc.).
# NOTE: Always use the "as $var" form for division — naive `length / length` always
# evaluates to 1.0 because it divides the filtered count by the filtered count.
#
# Example commands (enable by removing the leading # and setting FAIL_ON_THRESHOLD=1):

FAIL_ON_THRESHOLD=${FAIL_ON_THRESHOLD:-0}
FAILED=0

if command -v jq &>/dev/null; then
    # ── Overall survival rate (should be > 20%) ───────────────────────────────
    # Counts runs where outcome == "survived" divided by total runs.
    SURVIVAL_RATE=$(jq -s \
        '([.[] | select(.outcome == "survived")] | length) as $survived |
         (length) as $total |
         if $total > 0 then ($survived / $total * 100) else 0 end' \
        "$REPORT_DIR/ci_soak.jsonl")

    echo "Survival rate: ${SURVIVAL_RATE}%"

    if [ "$FAIL_ON_THRESHOLD" = "1" ]; then
        TOO_LOW=$(echo "$SURVIVAL_RATE < 20" | bc -l 2>/dev/null || echo "0")
        if [ "$TOO_LOW" = "1" ]; then
            echo "FAIL: Survival rate ${SURVIVAL_RATE}% is below 20% threshold"
            FAILED=1
        fi
    fi

    # ── Floor 1 death rate (should be < 15%) ─────────────────────────────────
    # Counts runs where per_floor[0].player_died == true divided by total runs.
    FLOOR1_DEATH_RATE=$(jq -s \
        '([.[] | select(.per_floor[0].player_died == true)] | length) as $died |
         (length) as $total |
         if $total > 0 then ($died / $total * 100) else 0 end' \
        "$REPORT_DIR/ci_soak.jsonl")

    echo "Floor 1 death rate: ${FLOOR1_DEATH_RATE}%"

    if [ "$FAIL_ON_THRESHOLD" = "1" ]; then
        TOO_HIGH=$(echo "$FLOOR1_DEATH_RATE > 15" | bc -l 2>/dev/null || echo "0")
        if [ "$TOO_HIGH" = "1" ]; then
            echo "FAIL: Floor 1 death rate ${FLOOR1_DEATH_RATE}% exceeds 15% threshold"
            FAILED=1
        fi
    fi

    # ── Exception count (should be 0) ─────────────────────────────────────────
    # Any run with outcome == "exception" indicates a code error, not a balance issue.
    EXCEPTION_COUNT=$(jq -s \
        '[.[] | select(.outcome == "exception")] | length' \
        "$REPORT_DIR/ci_soak.jsonl")

    echo "Exception count: $EXCEPTION_COUNT"

    if [ "$EXCEPTION_COUNT" != "0" ]; then
        echo "FAIL: $EXCEPTION_COUNT run(s) ended with exception outcome (code errors)"
        FAILED=1
    fi

else
    echo "WARNING: jq not found — skipping JSONL threshold checks."
    echo "Install jq to enable: https://stedolan.github.io/jq/"
fi

if [ "$FAILED" = "1" ]; then
    echo ""
    echo "CI soak check FAILED — see thresholds above."
    exit 1
fi

echo ""
echo "CI soak check passed."
