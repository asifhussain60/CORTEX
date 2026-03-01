#!/usr/bin/env bash
# install-hooks.sh — Install CORTEX git hooks for new developers.
#
# Authority: Phase 99-D (Secure MCP wiring)
# AC-ID:    AC-P99-D-001
#
# Usage:
#   bash scripts/install-hooks.sh
#
# What it does:
#   1. Symlinks (or copies) .git/hooks/pre-commit from the canonical source.
#   2. Makes the hook executable.
#   3. Verifies the preflight test suite runs cleanly.
#
# Run once after cloning the repo or after a fresh workspace setup.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_FILE="$HOOKS_DIR/pre-commit"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🔧 CORTEX Git Hooks Installer (Phase 99-D)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ── 1. Ensure .git/hooks exists ───────────────────────────────────────────────
if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "${RED}ERROR: $HOOKS_DIR not found. Are you inside a git repo?${NC}"
    exit 1
fi

# ── 2. Make hook executable (it already lives in .git/hooks) ──────────────────
if [ -f "$HOOK_FILE" ]; then
    chmod +x "$HOOK_FILE"
    echo -e "  ${GREEN}✅ pre-commit hook made executable${NC}: $HOOK_FILE"
else
    echo -e "${RED}ERROR: pre-commit hook not found at $HOOK_FILE${NC}"
    echo "       Ensure you have pulled the latest changes from origin."
    exit 1
fi

# ── 3. Smoke-test: verify preflight suite runs ────────────────────────────────
echo ""
echo -e "  ${YELLOW}⏳ Verifying preflight test suite …${NC}"
cd "$REPO_ROOT"

if python3 -m pytest tests/preflight/ -q --tb=short --no-header 2>/tmp/cortex_install_preflight.log; then
    PASSED=$(grep -oE '[0-9]+ passed' /tmp/cortex_install_preflight.log | head -1 || echo "all")
    echo -e "  ${GREEN}✅ Preflight tests healthy${NC} ($PASSED)"
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  Preflight tests are currently failing in your environment.${NC}"
    echo -e "${RED}   Hook is installed but commits will be blocked until fixed.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    cat /tmp/cortex_install_preflight.log | tail -15
    echo ""
    echo "  Run: make test-preflight  — to see the full failure detail."
    echo ""
    # Non-fatal: hook is installed, environment needs fixing
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Git hooks installed successfully.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Every commit will now run:"
echo "    • Copyright / bare-except / type-hint checks"
echo "    • File placement (CORE-038) + naming (CORE-028) enforcement"
echo "    • CORE-035 duplicate detection"
echo "    • Stub detection"
echo "    • 🔒 Preflight gate: tests/preflight/ (< 10s)"
echo ""
echo "  To bypass in an emergency: git commit --no-verify"
echo "  To re-run manually: make test-preflight"
echo ""
