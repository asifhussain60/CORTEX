#!/bin/bash
# CORTEX Stub Detection Script
# Detects functions with only 'pass' statements (stubs)
# Exit code 1 if stubs found, 0 if clean

set -e

echo "🔍 Scanning for stub implementations..."

# Find functions that end with ': pass' or only contain pass
STUB_FUNCTIONS=$(grep -rn "^\s*def\s\+.*:\s*$" cortex/ 2>/dev/null | grep -v "__init__" | grep -v "# pragma: stub-allowed" || true)

# Find standalone pass statements that might indicate stubs
PASS_ONLY=$(grep -rn "^\s*pass\s*$" cortex/ 2>/dev/null | grep -v "# pragma: stub-allowed" | grep -v "__pycache__" || true)

# Count findings
STUB_COUNT=$(echo "$STUB_FUNCTIONS" | grep -c "def" || echo "0")
PASS_COUNT=$(echo "$PASS_ONLY" | wc -l | tr -d ' ')

if [ "$STUB_COUNT" -gt 0 ]; then
    echo "❌ STUB FUNCTIONS DETECTED ($STUB_COUNT found):"
    echo ""
    echo "$STUB_FUNCTIONS"
    echo ""
    echo "⚠️  Stubs are not allowed. Implement proper functionality or add comment:"
    echo "    # pragma: stub-allowed"
    echo ""
    exit 1
fi

if [ "$PASS_COUNT" -gt 5 ]; then
    echo "⚠️  WARNING: $PASS_COUNT 'pass' statements found (may indicate stubs):"
    echo ""
    echo "$PASS_ONLY" | head -10
    echo ""
    echo "If legitimate (e.g., abstract methods), add comment: # pragma: stub-allowed"
    echo ""
fi

echo "✅ No stub functions detected"
exit 0
