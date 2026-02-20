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
	@.venv/bin/python -m pytest tests/wiring -v --timeout=30

# Run all tests (with timeout + maxfail to prevent hanging)
test-all:
	@.venv/bin/python -m pytest tests/ -v --timeout=30 --maxfail=10 --ignore=tests/documentation --ignore=tests/cortex --ignore=tests/golden --ignore=tests/e2e

# Run fast unit tests (no slow/integration markers)
test-fast:
	@.venv/bin/python -m pytest tests/unit/ -q --timeout=15 --maxfail=10 -m "not slow and not integration"

# Run smoke tests (<30s total)
test-smoke:
	@.venv/bin/python -m pytest tests/unit/ -q --timeout=5 --maxfail=3 -m "smoke"

# Run tests directory-by-directory for incremental terminal feedback
test-batch:
	@./scripts/run-tests.sh batch
