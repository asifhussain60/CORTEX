#!/usr/bin/env bash
# ==============================================================================
# CORTEX Test Runner — Unix thin wrapper
# ==============================================================================
# Cross-platform logic lives in scripts/run_tests.py (Python).
# This shell wrapper exists only for Unix convenience (make targets, CI).
# On Windows: use `python3 scripts/run_tests.py [mode]` directly, or
#             use the VS Code tasks defined in .vscode/tasks.json.
#
# Usage:
#   ./scripts/run-tests.sh              # unit tests (default)
#   ./scripts/run-tests.sh smoke        # Smoke tests only (<30s)
#   ./scripts/run-tests.sh unit         # Unit tests with parallel execution
#   ./scripts/run-tests.sh integration  # Integration tests
#   ./scripts/run-tests.sh fast         # Fast subset (no slow, no integration)
#   ./scripts/run-tests.sh batch        # Canonical CORTEX batch runner
#   ./scripts/run-tests.sh file <path>  # Single file
#   ./scripts/run-tests.sh dir <path>   # Single directory
#
# Author: Asif Hussain
# AC-ID: AC-TEST-PERF-001
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Delegate all logic to the cross-platform Python runner.
exec python3 "$SCRIPT_DIR/run_tests.py" "$@"
