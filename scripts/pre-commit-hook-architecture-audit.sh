#!/bin/bash
#
# CORTEX Architecture Audit Pre-Commit Hook
# 
# This hook runs the architecture audit before every commit to ensure
# compliance with CORTEX Architecture Contract v5.0.
#
# Installation:
#   cp scripts/pre-commit-hook-architecture-audit.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# To bypass (emergency only):
#   git commit --no-verify
#

set -e

echo ""
echo "🔍 Running CORTEX Architecture Audit..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the architecture audit
python3 scripts/audit_master_orchestrator_architecture.py

AUDIT_EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $AUDIT_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ ARCHITECTURE AUDIT FAILED"
    echo ""
    echo "The architecture audit detected issues that violate the CORTEX"
    echo "Architecture Contract v5.0. Your commit has been blocked."
    echo ""
    echo "📋 Review the audit report:"
    echo "   cortex-brain/documents/reports/master-orchestrator-architecture-audit-$(date +%Y-%m-%d).json"
    echo ""
    echo "🔧 Fix the issues and try again."
    echo ""
    echo "⚠️  To bypass this check (EMERGENCY ONLY):"
    echo "   git commit --no-verify"
    echo ""
    exit 1
fi

echo ""
echo "✅ ARCHITECTURE AUDIT PASSED"
echo ""
echo "Your commit complies with CORTEX Architecture Contract v5.0."
echo ""

exit 0
