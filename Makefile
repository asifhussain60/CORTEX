# =============================================================================
# CORTEX Makefile
# =============================================================================
# Quick commands for development workflow
# =============================================================================

.PHONY: setup-hooks verify test help

# Default target
help:
	@echo ""
	@echo "🧠 CORTEX Development Commands"
	@echo "════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  make setup-hooks    Configure git hooks (run after clone)"
	@echo "  make verify         Run production readiness verification"
	@echo "  make test           Run wiring tests"
	@echo "  make test-all       Run all tests"
	@echo ""

# Configure git to use version-controlled hooks
setup-hooks:
	@./scripts/setup-hooks.sh

# Run production readiness verification
verify:
	@PYTHONPATH=. .venv/bin/python _workspaces/docker-plan/verify-prod-ready.py --skip-docker

# Run wiring tests
test:
	@.venv/bin/python -m pytest tests/wiring -v

# Run all tests
test-all:
	@.venv/bin/python -m pytest tests/ -v
