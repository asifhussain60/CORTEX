# =============================================================================
# CORTEX Makefile
# =============================================================================
# Quick commands for development workflow
# =============================================================================

.PHONY: verify test test-all test-fast test-smoke test-batch help validate-wiring

# Default target
help:
	@echo ""
	@echo "🧠 CORTEX Development Commands"
	@echo "════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  make verify           Run production readiness verification"
	@echo "  make validate-wiring  Validate wiring.yaml accuracy (--strict mode)"
	@echo "  make test             Run wiring tests"
	@echo "  make test-all         Run all tests (with timeout + maxfail)"
	@echo "  make test-fast        Run fast unit tests (no slow/integration)"
	@echo "  make test-smoke       Run smoke tests only (<30s)"
	@echo "  make test-batch       Run tests directory-by-directory (incremental feedback)"
	@echo ""

# Run production readiness verification
verify:
	@PYTHONPATH=. .venv/bin/python _workspaces/docker-plan/verify_prod_ready.py --skip-docker

# Validate wiring.yaml accuracy (Phase 76 S1 T6)
validate-wiring:
	@echo "🔍 Validating wiring.yaml accuracy (--strict mode)..."
	@python3 cortex/validation/wiring_validator.py --strict

# Run wiring tests
test:
	@python3 scripts/run_tests.py dir tests/wiring

# Run all tests (with timeout + maxfail to prevent hanging)
# Cross-platform: delegates to run_tests.py (works on macOS, Linux, Windows)
test-all:
	@python3 scripts/run_tests.py all

# Run fast unit tests (no slow/integration markers) — uses CortexXdistPlugin batch runner
# Unix:    ./scripts/run-tests.sh fast   (delegates to run_tests.py)
# Windows: python3 scripts/run_tests.py fast
test-fast:
	@python3 scripts/run_tests.py fast

# Run smoke tests (<30s total) — uses CortexXdistPlugin batch runner
test-smoke:
	@python3 scripts/run_tests.py smoke

# Run tests using canonical CortexXdistPlugin batch runner (cross-platform)
# Unix:    ./scripts/run-tests.sh batch  (delegates to run_tests.py)
# Windows: python3 scripts/run_tests.py batch
test-batch:
	@python3 scripts/run_tests.py batch
