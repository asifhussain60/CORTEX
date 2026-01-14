#!/bin/bash
# Post-merge hook: Auto-reconcile SSOT after merge
# Runs SSoT validator to detect and repair merge conflicts in state
# Install: cp scripts/hooks/post-merge-ssot-reconcile.sh .git/hooks/post-merge && chmod +x .git/hooks/post-merge

set -e

echo "🔄 SSOT Post-merge Reconciliation..."

CORTEX_ROOT="$(git rev-parse --show-toplevel)"
cd "$CORTEX_ROOT"

# Check if SSOT files were modified in the merge
if git diff HEAD~1 HEAD --name-only | \
   grep -E "(AC-INDEX|master-plan|progress-tracker)" > /dev/null 2>&1; then
    
    echo "🔧 SSOT files modified in merge, running validation..."
    
    # Run validator (non-blocking - just report issues)
    python3 src/tools/ssot_integrity_validator.py || true
    
    # If critical issues, suggest repair
    if python3 src/tools/ssot_integrity_validator.py 2>&1 | grep -i "critical" > /dev/null 2>&1; then
        echo ""
        echo "⚠️  CRITICAL ISSUES DETECTED in SSOT after merge!"
        echo "   To auto-repair, run: python3 src/tools/ssot_integrity_validator.py repair"
        echo ""
    fi
fi

echo "✅ Post-merge reconciliation complete"
exit 0
