# =============================================================================
# CORTEX Makefile
# =============================================================================
# Quick commands for development workflow
# Cross-platform: all targets delegate to python3 scripts/run_tests.py
#   macOS/Linux: make <target>
#   Windows:     python scripts\run_tests.py <mode>  (make unavailable)
# =============================================================================

.PHONY: verify test test-all test-fast test-smoke test-batch test-changed test-parallel help validate-wiring

# Default target
help:
	@echo ""
	@echo "🧠 CORTEX Development Commands"
	@echo "════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  make verify           Run production readiness verification"
	@echo "  make validate-wiring  Validate wiring.yaml accuracy (--strict mode)"
	@echo ""
	@echo "Test Modes (fastest → safest):"
	@echo "  make test-changed     testmon: only tests covering changed files  ← TDD loop"
	@echo "  make test-smoke       Smoke tests, parallel xdist (<30s target)"
	@echo "  make test-fast        Fast unit tests, parallel (no slow/integration)"
	@echo "  make test             Unit tests, parallel (xdist loadscope)"
	@echo "  make test-parallel    Full suite, parallel workers (max throughput)"
	@echo "  make test-batch       Full suite, sequential (canonical / CI safe)"
	@echo "  make test-all         Full suite, all dirs, sequential"
	@echo ""
	@echo "Environment overrides:"
	@echo "  CORTEX_WORKERS=4 make test-parallel   Use 4 workers instead of auto"
	@echo "  CORTEX_DISABLE_PARALLEL=true make test Force sequential (any mode)"
	@echo "  CORTEX_DISABLE_TESTMON=true make test-changed  Skip testmon DB"
	@echo ""

# Run production readiness verification
verify:
	@PYTHONPATH=. python3 _workspaces/docker-plan/verify_prod_ready.py --skip-docker

# Validate wiring.yaml accuracy (Phase 76 S1 T6)
validate-wiring:
	@echo "🔍 Validating wiring.yaml accuracy (--strict mode)..."
	@python3 cortex/validation/wiring_validator.py --strict

# TDD inner loop — only tests whose source files changed (testmon Layer 2)
test-changed:
	@python3 scripts/run_tests.py changed

# Run smoke tests in parallel (<30s total wall time)
test-smoke:
	@python3 scripts/run_tests.py smoke

# Run fast unit tests in parallel (no slow/integration markers)
test-fast:
	@python3 scripts/run_tests.py fast

# Run unit tests in parallel (default — xdist loadscope)
test:
	@python3 scripts/run_tests.py unit

# Run full suite with all available cores (max throughput)
test-parallel:
	@python3 scripts/run_tests.py parallel

# Run full suite sequentially (canonical / CI safe)
test-batch:
	@python3 scripts/run_tests.py batch

# Run all tests including all directories, sequential
test-all:
	@python3 scripts/run_tests.py all
