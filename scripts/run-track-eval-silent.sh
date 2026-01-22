#!/bin/bash
# CORTEX Track:Eval Execution - Silent & Minimal
# Usage: ./scripts/run-track-eval-silent.sh [options]
# Options:
#   --verbose    Show detailed output
#   --save       Save results to JSON file
#   --commit     Auto-commit results
#   --phase N    Run only phase N (1-8)

set -e

CORTEX_ROOT="/Users/asifhussain/PROJECTS/CORTEX"
SCRIPT="${CORTEX_ROOT}/scripts/execute-track-eval-silent.py"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULTS_FILE="${CORTEX_ROOT}/eval-results-${TIMESTAMP}.json"
VERBOSE=0
SAVE=0
COMMIT=0
PHASE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose) VERBOSE=1; shift ;;
        --save) SAVE=1; shift ;;
        --commit) COMMIT=1; shift ;;
        --phase) PHASE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Change to CORTEX root
cd "$CORTEX_ROOT"

# Execute
if [ $VERBOSE -eq 1 ]; then
    # Show stderr + return JSON
    python "$SCRIPT" 2>&1 | tee /tmp/eval-stderr-${TIMESTAMP}.log > "$RESULTS_FILE"
    RESULT=$?
else
    # Silent: stderr only shows progress, stdout is JSON
    python "$SCRIPT" > "$RESULTS_FILE" 2>&1
    RESULT=$?
fi

# Extract summary
if [ -f "$RESULTS_FILE" ]; then
    SUMMARY=$(jq -r '.summary // "UNKNOWN"' "$RESULTS_FILE" 2>/dev/null || echo "UNKNOWN")
    BLOCKERS=$(jq -r '.blockers | length' "$RESULTS_FILE" 2>/dev/null || echo "0")
fi

# Output
echo ""
if [ $BLOCKERS -eq 0 ]; then
    echo "✓ Track:Eval completed successfully"
else
    echo "⚠ Track:Eval completed with $BLOCKERS blocker(s)"
fi
echo "  Results: $RESULTS_FILE"
echo ""

# Save if requested
if [ $SAVE -eq 1 ]; then
    echo "✓ Results saved to $RESULTS_FILE"
    # Also create a human-readable summary
    jq '.phases[] | "\(.phase): \(.status)"' "$RESULTS_FILE" > "${RESULTS_FILE%.json}-summary.txt"
    echo "  Summary: ${RESULTS_FILE%.json}-summary.txt"
fi

# Commit if requested
if [ $COMMIT -eq 1 ]; then
    git add "$RESULTS_FILE"
    git commit -m "EVAL-TRACK: Track:eval executed [${TIMESTAMP}] - Results: $RESULTS_FILE" 2>/dev/null || true
    echo "✓ Results committed to git"
fi

exit $RESULT
