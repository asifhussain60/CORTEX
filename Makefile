# =============================================================================
# CORTEX Makefile
# =============================================================================
# Quick commands for development workflow
# =============================================================================

.PHONY: setup-hooks verify test help validate-wiring

# Default target
help:
	@echo ""
	@echo "🧠 CORTEX Development Commands"
	@echo "════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  make setup-hooks      Configure git hooks (run after clone)"
	@echo "  make verify           Run production readiness verification"
	@echo "  make validate-wiring  Validate wiring.yaml accuracy (--strict mode)"
	@echo "  make test             Run wiring tests"
	@echo "  make test-all         Run all tests"
	@echo ""

# Configure git to use version-controlled hooks
setup-hooks:
	@./scripts/setup-hooks.sh

# Run production readiness verification
verify:
	@PYTHONPATH=. .venv/bin/python _workspaces/docker-plan/verify_prod_ready.py --skip-docker

# Validate wiring.yaml accuracy (Phase 76 S1 T6)
validate-wiring:
	@echo "🔍 Validating wiring.yaml accuracy (--strict mode)..."
	@python3 cortex/validation/wiring_validator.py --strict

# Run wiring tests
test:
	@.venv/bin/python -m pytest tests/wiring -v

# Run all tests
test-all:
	@.venv/bin/python -m pytest tests/ -v
