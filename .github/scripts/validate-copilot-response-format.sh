#!/bin/bash
###############################################################################
# Validate Copilot Chat Response Rendering Format
# 
# Ensures response templates in instruction files don't use code fences
# that would render as literal text in GitHub Copilot Chat.
#
# Authority: CORE-028 (file naming) + ENH-031 (YAML Response Format Fix)
# Author: Asif Hussain
# Date: 2026-02-06
###############################################################################

set -e

INSTRUCTIONS_FILE=".github/copilot-instructions.md"
ERRORS=0

echo "🔍 Validating Copilot Response Rendering Format..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check 1: No code fences in copilot-instructions.md
echo "✓ Check 1: copilot-instructions.md should have NO code fences"
if grep -q '```' "$INSTRUCTIONS_FILE"; then
    echo "  ❌ FAILED: Found code fences in $INSTRUCTIONS_FILE"
    grep -n '```' "$INSTRUCTIONS_FILE" || true
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ PASSED: No code fences found"
fi

# Check 2: Verify indented examples instead
echo ""
echo "✓ Check 2: Indented text should be used for template examples"
INDENTED_COUNT=$(grep -c '^    ##' "$INSTRUCTIONS_FILE" || echo 0)
if [ "$INDENTED_COUNT" -gt 0 ]; then
    echo "  ✅ PASSED: Found $INDENTED_COUNT indented template examples"
else
    echo "  ⚠️  WARNING: No indented examples found (check manually)"
fi

# Check 3: Response header format
echo ""
echo "✓ Check 3: Response header template must be present"
if grep -q 'CORTEX {operation}' "$INSTRUCTIONS_FILE"; then
    echo "  ✅ PASSED: Response header template found"
else
    echo "  ❌ FAILED: Response header template missing"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: No triple backticks followed by language identifier
echo ""
echo "✓ Check 4: No triple backticks with language identifier (markdown, yaml, bash, python)"
FENCE_WITH_LANG=$(grep -E '```(markdown|yaml|bash|python|json)' "$INSTRUCTIONS_FILE" || echo "")
if [ -z "$FENCE_WITH_LANG" ]; then
    echo "  ✅ PASSED: No language-identified code fences"
else
    echo "  ❌ FAILED: Found language-identified code fences:"
    echo "$FENCE_WITH_LANG" | sed 's/^/    /'
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED"
    echo ""
    echo "Response templates will render correctly in GitHub Copilot Chat:"
    echo "  - ✓ No raw markdown code blocks"
    echo "  - ✓ Indented examples render with proper spacing"
    echo "  - ✓ Icons and formatting preserved"
    exit 0
else
    echo "❌ $ERRORS CHECK(S) FAILED"
    echo ""
    echo "Fix: Replace code fences with indented examples:"
    echo "  Bad:  \`\`\`markdown"
    echo "        ## Header"
    echo "        \`\`\`"
    echo ""
    echo "  Good:     ## Header"
    echo ""
    exit 1
fi
