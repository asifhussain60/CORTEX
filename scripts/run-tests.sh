#!/usr/bin/env bash
# ==============================================================================
# CORTEX Test Runner — Fast, batched, non-hanging
# ==============================================================================
# Solves: Tests appearing to hang due to 16K+ test collection, no timeout,
#         per-test SQLite flushes, and no incremental feedback.
#
# Usage:
#   ./scripts/run-tests.sh              # Run all unit tests (default)
#   ./scripts/run-tests.sh smoke        # Smoke tests only (<30s)
#   ./scripts/run-tests.sh unit         # Unit tests with parallel execution
#   ./scripts/run-tests.sh integration  # Integration tests
#   ./scripts/run-tests.sh fast         # Fast subset (no slow, no integration)
#   ./scripts/run-tests.sh file <path>  # Single file
#   ./scripts/run-tests.sh dir <path>   # Single directory
#
# Author: Asif Hussain
# AC-ID: AC-TEST-PERF-001
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Defaults
TIMEOUT=30
MAXFAIL=10
WORKERS="auto"
VERBOSE="-q"
TB="--tb=short"

# Common ignores (always skip these problematic dirs)
COMMON_IGNORES=(
    "--ignore=tests/documentation"
    "--ignore=tests/cortex"
    "--ignore=tests/golden"
    "--ignore=tests/e2e"
    "--ignore=tests/_legacy_broken"
    "--ignore=tests/_skip"
    "--ignore=tests/_deprecated"
)

# Override pytest.ini addopts to prevent conflicts
OVERRIDE="-o addopts="

print_header() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  CORTEX Test Runner — $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_result() {
    local exit_code=$1
    if [ "$exit_code" -eq 0 ]; then
        echo -e "\n${GREEN}✅ All tests passed${NC}"
    elif [ "$exit_code" -eq 5 ]; then
        echo -e "\n${YELLOW}⚠️  No tests collected${NC}"
    else
        echo -e "\n${RED}❌ Tests failed (exit code: $exit_code)${NC}"
    fi
}

run_pytest() {
    local description="$1"
    shift
    print_header "$description"
    echo -e "${YELLOW}Timeout: ${TIMEOUT}s per test | Max failures: ${MAXFAIL}${NC}\n"

    local exit_code=0
    python3 -m pytest \
        --timeout="$TIMEOUT" \
        --maxfail="$MAXFAIL" \
        $VERBOSE \
        $TB \
        --no-header \
        "$OVERRIDE" \
        "${COMMON_IGNORES[@]}" \
        "$@" || exit_code=$?

    print_result "$exit_code"
    return "$exit_code"
}

MODE="${1:-unit}"
shift 2>/dev/null || true

case "$MODE" in
    smoke)
        run_pytest "Smoke Tests (<30s)" \
            tests/unit/ \
            -m "smoke" \
            --timeout=5 \
            --maxfail=3
        ;;
    
    unit)
        run_pytest "Unit Tests (parallel)" \
            tests/unit/ \
            -n "$WORKERS" \
            --dist loadscope
        ;;
    
    fast)
        run_pytest "Fast Tests (no slow, no integration)" \
            tests/unit/ \
            -m "not slow and not integration" \
            -n "$WORKERS" \
            --dist loadscope
        ;;
    
    integration)
        run_pytest "Integration Tests" \
            tests/integration/ \
            --timeout=60 \
            --maxfail=5
        ;;
    
    file)
        TARGET="${1:?Usage: run-tests.sh file <path>}"
        run_pytest "Single File: $TARGET" \
            "$TARGET" \
            -v \
            --timeout=60
        ;;
    
    dir)
        TARGET="${1:?Usage: run-tests.sh dir <path>}"
        run_pytest "Directory: $TARGET" \
            "$TARGET"
        ;;
    
    all)
        run_pytest "All Tests (unit + integration)" \
            tests/ \
            -n "$WORKERS" \
            --dist loadscope \
            --timeout=60
        ;;
    
    batch)
        # Run tests in batches by top-level test directory — gives incremental feedback
        print_header "Batched Test Run"
        TOTAL_EXIT=0
        
        # Discover test subdirectories
        DIRS=($(find tests/unit -mindepth 1 -maxdepth 1 -type d | sort))
        TOTAL_DIRS=${#DIRS[@]}
        CURRENT=0
        
        for dir in "${DIRS[@]}"; do
            CURRENT=$((CURRENT + 1))
            DIRNAME=$(basename "$dir")
            echo -e "\n${CYAN}[$CURRENT/$TOTAL_DIRS] Testing: $DIRNAME${NC}"
            
            local_exit=0
            python3 -m pytest \
                --timeout="$TIMEOUT" \
                --maxfail=5 \
                -q \
                --tb=line \
                --no-header \
                "$OVERRIDE" \
                "$dir" 2>&1 | tail -3 || local_exit=$?
            
            if [ "$local_exit" -ne 0 ] && [ "$local_exit" -ne 5 ]; then
                echo -e "${RED}  ❌ Failed in $DIRNAME${NC}"
                TOTAL_EXIT=1
            fi
        done
        
        if [ "$TOTAL_EXIT" -eq 0 ]; then
            echo -e "\n${GREEN}✅ All batches passed${NC}"
        else
            echo -e "\n${RED}❌ Some batches failed${NC}"
        fi
        exit "$TOTAL_EXIT"
        ;;
    
    *)
        echo "Usage: $0 {smoke|unit|fast|integration|file|dir|all|batch} [target]"
        echo ""
        echo "Modes:"
        echo "  smoke        Smoke tests only (<30s total)"
        echo "  unit         Unit tests with parallel execution (default)"
        echo "  fast         Fast subset (no slow/integration markers)"
        echo "  integration  Integration tests with 60s timeout"
        echo "  file <path>  Run single test file"
        echo "  dir <path>   Run tests in single directory"
        echo "  all          Full suite (unit + integration)"
        echo "  batch        Run unit tests directory-by-directory (incremental feedback)"
        exit 1
        ;;
esac
