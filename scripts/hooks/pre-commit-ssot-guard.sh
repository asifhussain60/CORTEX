#!/bin/bash
# Pre-commit hook: SSOT Integrity Guard
# Prevents commits that violate SSOT constraints
# Install: cp scripts/hooks/pre-commit-ssot-guard.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

echo "🔍 SSOT Pre-commit Validation..."

CORTEX_ROOT="$(git rev-parse --show-toplevel)"
cd "$CORTEX_ROOT"

# Check 1: No hardcoded percentages in progress-tracker.json
if git diff --cached cortex-brain/tier1/tracking/progress-tracker.json | \
   grep -E '"completion_percentage":\s*[0-9]{2,3}(\.[0-9]+)?' > /dev/null 2>&1; then
    
    echo "❌ ERROR: Hardcoded percentages detected in progress-tracker.json"
    echo "   Percentages must be CALCULATED from AC counts, not hardcoded"
    echo "   Use: SSoTIntegrityValidator.fix_hardcoded_percentages()"
    exit 1
fi

# Check 2: AC counts should not be manually edited to null
if git diff --cached cortex-brain/tier1/tracking/progress-tracker.json | \
   grep -E '"(total_ac_count|completed_count)":\s*null' > /dev/null 2>&1; then
    
    echo "❌ ERROR: NULL AC counts detected in progress-tracker.json"
    echo "   Use SSoTIntegrityValidator to recalculate AC counts"
    exit 1
fi

# Check 3: AC-INDEX.yaml changes must not remove ACs without updating master-plan
if git diff --cached cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml | \
   grep -E '^\-\s+AC-[A-Z]+-[0-9]+:' > /dev/null 2>&1; then
    
    echo "⚠️  WARNING: AC-IDs being removed from AC-INDEX.yaml"
    echo "   Ensure these are removed from master-plan.yaml phase lists"
    echo "   Run: python3 -m src.tools.ssot_integrity_validator repair"
fi

# Check 4: Validate master-plan.yaml has valid phases
if git diff --cached cortex-brain/cx6-plan/master-plan.yaml > /dev/null 2>&1; then
    if ! python3 -c "import yaml; yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))" 2>/dev/null; then
        echo "❌ ERROR: master-plan.yaml has invalid YAML syntax"
        exit 1
    fi
fi

# Check 5: Validate AC-INDEX.yaml has valid YAML
if git diff --cached cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml > /dev/null 2>&1; then
    if ! python3 -c "import yaml; yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))" 2>/dev/null; then
        echo "❌ ERROR: AC-INDEX.yaml has invalid YAML syntax"
        exit 1
    fi
fi

echo "✅ SSOT integrity checks passed"
exit 0
