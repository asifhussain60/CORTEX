#!/usr/bin/env bash
# CORTEX Pre-Execution Verification Script
# Purpose: Validate environment before autonomous wave execution
# Authority: master-plan.yaml v3.0
# Date: 2026-02-14

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0
WARNINGS=0
PASSES=0

echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo "${BLUE}CORTEX Pre-Execution Verification (master-plan.yaml v3.0)${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

# Function to check success
check_pass() {
    local check_name=$1
    echo "${GREEN}✅${NC} $check_name"
    ((PASSES++))
}

# Function to check warning
check_warn() {
    local check_name=$1
    echo "${YELLOW}⚠️${NC} $check_name"
    ((WARNINGS++))
}

# Function to check failure
check_fail() {
    local check_name=$1
    echo "${RED}❌${NC} $check_name"
    ((FAILURES++))
}

# ============================================================================
echo "${BLUE}1. PYTHON ENVIRONMENT${NC}\n"

# Check Python version
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
    PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)
    
    if [[ $PY_MAJOR -ge 3 ]] && [[ $PY_MINOR -ge 9 ]]; then
        check_pass "Python $PY_VERSION (≥3.9 required)"
    else
        check_fail "Python $PY_VERSION (need ≥3.9)"
    fi
else
    check_fail "Python not found in PATH"
fi

# Check virtual environment
if [[ -n "$VIRTUAL_ENV" ]] || [[ -d ".venv" ]] || [[ -d "venv" ]]; then
    check_pass "Virtual environment activated or detected"
else
    check_warn "Virtual environment not detected (try: python -m venv .venv && source .venv/bin/activate)"
fi

# Check requirements.txt exists
if [[ -f "requirements.txt" ]]; then
    check_pass "requirements.txt present"
else
    check_fail "requirements.txt missing"
fi

# ============================================================================
echo "\n${BLUE}2. GIT CONFIGURATION${NC}\n"

# Check branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" == "CORTEX" ]]; then
    check_pass "On CORTEX branch (CORE-052 ✅)"
else
    check_fail "Not on CORTEX branch (current: $CURRENT_BRANCH, CORE-052 ❌)"
fi

# Check git hooks
HOOKS_PATH=$(git config core.hooksPath 2>/dev/null || echo "NOT SET")
if [[ "$HOOKS_PATH" == ".githooks" ]]; then
    check_pass "Git hooks configured (.githooks) ✅"
else
    check_warn "Git hooks not configured (run: git config core.hooksPath .githooks)"
fi

# Check .githooks/post-checkout exists
if [[ -f ".githooks/post-checkout" ]]; then
    check_pass ".githooks/post-checkout exists"
else
    check_warn ".githooks/post-checkout not found"
fi

# ============================================================================
echo "\n${BLUE}3. CORTEX SETUP${NC}\n"

# Check setup-mcp.py
if [[ -f ".cortex/setup-mcp.py" ]]; then
    check_pass ".cortex/setup-mcp.py exists"
else
    check_fail ".cortex/setup-mcp.py missing"
fi

# Check .cortex/setup.log
if [[ -f ".cortex/setup.log" ]]; then
    if grep -q "✅ SETUP COMPLETE" .cortex/setup.log 2>/dev/null; then
        check_pass ".cortex/setup.log shows SETUP COMPLETE"
    else
        check_warn ".cortex/setup.log exists but may be incomplete"
    fi
else
    check_warn ".cortex/setup.log not found (run: python .cortex/setup-mcp.py)"
fi

# ============================================================================
echo "\n${BLUE}4. VSCODE CONFIGURATION${NC}\n"

# Check .vscode/settings.json exists
if [[ -f ".vscode/settings.json" ]]; then
    check_pass ".vscode/settings.json exists"
    
    # Check if settings.json is tracked by git
    if git ls-files --error-unmatch .vscode/settings.json &>/dev/null; then
        check_fail ".vscode/settings.json IS tracked by git (CORE-051 ❌ - remove with: git rm --cached .vscode/settings.json)"
    else
        check_pass ".vscode/settings.json NOT tracked (CORE-051 ✅)"
    fi
else
    check_warn ".vscode/settings.json not found (created by setup-mcp.py or post-checkout hook)"
fi

# Check .vscode/extensions.json
if [[ -f ".vscode/extensions.json" ]]; then
    check_pass ".vscode/extensions.json present"
else
    check_warn ".vscode/extensions.json not found"
fi

# ============================================================================
echo "\n${BLUE}5. TEST SUITE${NC}\n"

# Check if pytest is installed
if command -v pytest &> /dev/null; then
    check_pass "pytest installed"
    
    # Run quick test count
    TEST_COUNT=$(pytest --collect-only -q 2>/dev/null | grep "test session starts" -A 1 | tail -1 | awk '{print $1}' || echo "?")
    if [[ "$TEST_COUNT" != "?" ]]; then
        check_pass "Test collection successful (~$TEST_COUNT tests found)"
    fi
else
    check_fail "pytest not installed (pip install pytest)"
fi

# ============================================================================
echo "\n${BLUE}6. CORTEX MASTER PLAN${NC}\n"

# Check master-plan.yaml
if [[ -f "cortex-registry/_cortex-master/master-plan.yaml" ]]; then
    VERSION=$(grep "^# Version:" cortex-registry/_cortex-master/master-plan.yaml | head -1 | awk '{print $NF}')
    check_pass "master-plan.yaml present (version: $VERSION)"
else
    check_fail "master-plan.yaml missing"
fi

# Check VSCODE-AUTONOMOUS-EXECUTION-GUIDE.md
if [[ -f "cortex-registry/_cortex-master/VSCODE-AUTONOMOUS-EXECUTION-GUIDE.md" ]]; then
    check_pass "VSCODE-AUTONOMOUS-EXECUTION-GUIDE.md created ✅"
else
    check_warn "VSCODE-AUTONOMOUS-EXECUTION-GUIDE.md not found"
fi

# ============================================================================
echo "\n${BLUE}7. MASTER PLAN FILE HEALTH${NC}\n"

# Count files in _cortex-master
FILE_COUNT=$(ls -1 cortex-registry/_cortex-master/ 2>/dev/null | grep -v "^_" | wc -l)
if [[ $FILE_COUNT -le 100 ]]; then
    check_pass "_cortex-master/ has $FILE_COUNT root files (target: ≤20 after WAVE-1)"
else
    check_warn "_cortex-master/ has $FILE_COUNT root files (WAVE-1 will reduce this)"
fi

# ============================================================================
echo "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo "${BLUE}VERIFICATION SUMMARY${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

echo "Results:"
echo "  ${GREEN}✅ Passed: $PASSES${NC}"
echo "  ${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo "  ${RED}❌ Failures: $FAILURES${NC}\n"

# Determine readiness
if [[ $FAILURES -eq 0 ]]; then
    echo "${GREEN}✅ ENVIRONMENT READY FOR WAVE EXECUTION${NC}\n"
    echo "Next steps:"
    echo "  1. Open VSCode Copilot Chat (Cmd+I)"
    echo "  2. Copy WAVE command from VSCODE-AUTONOMOUS-EXECUTION-GUIDE.md"
    echo "  3. Paste into chat and press Enter"
    echo "  4. Monitor progress via ASCII bars (silent mode)"
    echo ""
    exit 0
else
    echo "${RED}❌ FIX FAILURES BEFORE PROCEEDING${NC}\n"
    echo "Resolution steps:"
    echo "  • Review failures above (marked with ❌)"
    echo "  • Most common: python .cortex/setup-mcp.py + reload VS Code"
    echo "  • Re-run this script: $0"
    echo ""
    exit 1
fi
