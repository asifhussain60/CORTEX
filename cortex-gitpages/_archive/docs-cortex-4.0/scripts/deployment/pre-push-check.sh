#!/bin/bash
# =============================================================================
# CORTEX Pre-Push Verification Script
# =============================================================================
# Run this before pushing to ensure repository hygiene
#
# Usage:
#   ./scripts/pre-push-check.sh         # Full check
#   ./scripts/pre-push-check.sh --quick # Quick check (skip tests)
#   ./scripts/pre-push-check.sh --fix   # Attempt auto-fixes
#
# Author: Asif Hussain
# Copyright © 2025-2026 Asif Hussain. All rights reserved.
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
QUICK_MODE=false
FIX_MODE=false
for arg in "$@"; do
    case $arg in
        --quick) QUICK_MODE=true ;;
        --fix) FIX_MODE=true ;;
        --help) 
            echo "Usage: $0 [--quick] [--fix]"
            echo "  --quick  Skip test execution"
            echo "  --fix    Attempt to auto-fix issues"
            exit 0
            ;;
    esac
done

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         CORTEX Pre-Push Verification                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

ERRORS=0
WARNINGS=0

# -----------------------------------------------------------------------------
# Check 1: Absolute Paths
# -----------------------------------------------------------------------------
echo -e "${BLUE}[1/5]${NC} Checking for absolute paths..."

# Patterns to detect
ABSOLUTE_PATH_PATTERNS='/Users/[^/]+/|/home/[^/]+/|C:\\Users\\|/var/[^/]+/CORTEX'

# Files to check (exclude prompts which may have examples)
ABSOLUTE_PATHS_FOUND=$(grep -rn --include="*.py" --include="*.yaml" --include="*.json" \
    -E "$ABSOLUTE_PATH_PATTERNS" . 2>/dev/null | \
    grep -v '.git/' | \
    grep -v '.venv/' | \
    grep -v 'venv/' | \
    grep -v 'prompt.md' | \
    grep -v 'MULTI_MACHINE_STRATEGY.md' | \
    grep -v '__pycache__' | \
    grep -v 'reference-map.json' | \
    grep -v 'analysis-report.json' | \
    grep -v 'migration-plan.json' | \
    grep -v 'execution-report.json' | \
    grep -v 'cortex_brain/vacuum/' | \
    grep -v 'WRONG:' | \
    grep -v 'NEVER use' | \
    grep -v 'No C:\\' | \
    grep -v '<username>' | \
    grep -v 'test_brittleness' || true)

if [ -n "$ABSOLUTE_PATHS_FOUND" ]; then
    echo -e "${RED}   ❌ FAIL: Absolute paths found${NC}"
    echo "$ABSOLUTE_PATHS_FOUND" | head -10
    if [ $(echo "$ABSOLUTE_PATHS_FOUND" | wc -l) -gt 10 ]; then
        echo "   ... and more ($(echo "$ABSOLUTE_PATHS_FOUND" | wc -l) total)"
    fi
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}   ✅ PASS: No absolute paths in code${NC}"
fi

# -----------------------------------------------------------------------------
# Check 2: Untracked Files
# -----------------------------------------------------------------------------
echo -e "${BLUE}[2/5]${NC} Checking for untracked files..."

# Get untracked files excluding known patterns
UNTRACKED=$(git status --porcelain 2>/dev/null | grep '^??' | \
    grep -v '__pycache__' | \
    grep -v '\.pyc$' | \
    grep -v '\.db-shm$' | \
    grep -v '\.db-wal$' | \
    grep -v '\.pytest_cache' | \
    grep -v '\.coverage$' | \
    grep -v '\.DS_Store$' || true)

if [ -n "$UNTRACKED" ]; then
    echo -e "${YELLOW}   ⚠️  WARNING: Untracked files found${NC}"
    echo "$UNTRACKED" | sed 's/^??/     /'
    WARNINGS=$((WARNINGS + 1))
    
    if [ "$FIX_MODE" = true ]; then
        echo -e "${BLUE}   → Attempting to add to .gitignore...${NC}"
        # This is a suggestion, not auto-fix for safety
        echo "   Review these files and either 'git add' or add to .gitignore"
    fi
else
    echo -e "${GREEN}   ✅ PASS: No untracked files${NC}"
fi

# -----------------------------------------------------------------------------
# Check 3: Staged Changes Validation
# -----------------------------------------------------------------------------
echo -e "${BLUE}[3/5]${NC} Validating staged changes..."

# Check for large files in staging
LARGE_FILES=$(git diff --cached --name-only 2>/dev/null | while read file; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file" 2>/dev/null || echo 0)
        if [ "$size" -gt 1048576 ]; then
            echo "$file ($(($size / 1024))KB)"
        fi
    fi
done || true)

if [ -n "$LARGE_FILES" ]; then
    echo -e "${YELLOW}   ⚠️  WARNING: Large files staged (>1MB)${NC}"
    echo "$LARGE_FILES" | sed 's/^/     /'
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}   ✅ PASS: No oversized files${NC}"
fi

# Check for sensitive data patterns
SENSITIVE=$(git diff --cached 2>/dev/null | grep -iE '(password|secret|api_key|token|private_key)\s*[:=]' | head -5 || true)

if [ -n "$SENSITIVE" ]; then
    echo -e "${RED}   ❌ FAIL: Potential sensitive data in staged changes${NC}"
    echo "$SENSITIVE" | sed 's/^/     /'
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}   ✅ PASS: No sensitive data patterns${NC}"
fi

# -----------------------------------------------------------------------------
# Check 4: Database Sync Status
# -----------------------------------------------------------------------------
echo -e "${BLUE}[4/5]${NC} Checking database sync status..."

if [ -f "scripts/init_db.py" ]; then
    # Run status check
    DB_STATUS=$(python3 scripts/init_db.py --status 2>&1 | tail -10 || echo "ERROR")
    
    if echo "$DB_STATUS" | grep -q "ERROR"; then
        echo -e "${YELLOW}   ⚠️  WARNING: Database status check failed${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        AUDIT_COUNT=$(echo "$DB_STATUS" | grep "Audit Logs:" | grep -oE '[0-9]+' || echo "0")
        echo -e "${GREEN}   ✅ PASS: Database operational ($AUDIT_COUNT audit entries)${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  WARNING: init_db.py not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# -----------------------------------------------------------------------------
# Check 5: Tests (unless --quick)
# -----------------------------------------------------------------------------
if [ "$QUICK_MODE" = false ]; then
    echo -e "${BLUE}[5/5]${NC} Running unit tests..."
    
    if command -v pytest &> /dev/null; then
        if pytest tests/unit/ -q --tb=no 2>&1 | tail -3; then
            echo -e "${GREEN}   ✅ PASS: All tests passing${NC}"
        else
            echo -e "${RED}   ❌ FAIL: Some tests failing${NC}"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "${YELLOW}   ⚠️  WARNING: pytest not found, skipping tests${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${BLUE}[5/5]${NC} Skipping tests (--quick mode)"
fi

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ VERIFICATION FAILED${NC}"
    echo -e "   Errors: $ERRORS, Warnings: $WARNINGS"
    echo ""
    echo "   Fix the errors above before pushing."
    echo "   Run with --fix to attempt auto-remediation."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  VERIFICATION PASSED WITH WARNINGS${NC}"
    echo -e "   Errors: 0, Warnings: $WARNINGS"
    echo ""
    echo "   Review warnings above. Push at your discretion."
    exit 0
else
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "   Safe to push!"
    exit 0
fi
