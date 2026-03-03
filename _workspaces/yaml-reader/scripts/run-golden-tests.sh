#!/bin/bash
# CORTEX YAML Reader - Validation Script
# Ensures master-index.yaml is compatible with both Python and JavaScript parsers

set -e

echo "🔍 CORTEX YAML Reader Validation"
echo "=================================="
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Run golden test
echo "Running golden test suite..."
python3 test_yaml_loader.py

# Summary
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ALL TESTS PASSED"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Open index.html in browser"
    echo "  2. Click 'Open File(s)'"
    echo "  3. Select ../master-index.yaml"
    echo "  4. Verify tree/cards/graph views render correctly"
    echo ""
    echo "Or run:"
    echo "  open index.html"
    exit 0
else
    echo ""
    echo "❌ TESTS FAILED"
    echo "Fix errors above before using YAML Reader"
    exit 1
fi
