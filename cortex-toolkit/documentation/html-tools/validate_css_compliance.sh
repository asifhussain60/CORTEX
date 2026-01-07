#!/bin/bash
# CSS Compliance Validator for CORTEX Knowledge Library
# Version: 1.0
# Author: Asif Hussain
# Purpose: Ensure single CSS file usage (main.css only) across all knowledge pages

echo "🎨 CSS Compliance Validator for Knowledge Library"
echo "=================================================="

KNOWLEDGE_DIR="docs/knowledge"
CSS_VIOLATIONS=0
INLINE_STYLE_VIOLATIONS=0
BROKEN_CSS_REFS=0

# Check 1: Verify single CSS file usage (main.css only)
echo ""
echo "✅ Check 1: Single CSS File Usage"
echo "Expected: <link rel=\"stylesheet\" href=\"../assets/css/main.css\">"

for file in $KNOWLEDGE_DIR/*.html; do
    filename=$(basename "$file")
    
    # Check for non-existent CSS files
    if grep -q 'documentation-styling-standards.css' "$file"; then
        echo "❌ $filename: References NON-EXISTENT 'documentation-styling-standards.css'"
        ((BROKEN_CSS_REFS++))
    fi
    
    # Check for duplicate main.css links
    main_css_count=$(grep -c 'href="../assets/css/main.css"' "$file" 2>/dev/null || echo 0)
    if [ "$main_css_count" -gt 1 ]; then
        echo "⚠️  $filename: Duplicate main.css links ($main_css_count times)"
        ((CSS_VIOLATIONS++))
    elif [ "$main_css_count" -eq 0 ]; then
        echo "❌ $filename: Missing main.css link"
        ((CSS_VIOLATIONS++))
    fi
    
    # Check for other local CSS files (forbidden)
    if grep -Eq 'href="\.\./assets/css/(?!main\.css)' "$file"; then
        echo "❌ $filename: References alternate CSS file (FORBIDDEN)"
        ((CSS_VIOLATIONS++))
    fi
done

# Check 2: Inline style detection
echo ""
echo "✅ Check 2: Inline Style Detection"
echo "Expected: ZERO inline styles (except story button exception)"

for file in $KNOWLEDGE_DIR/*.html; do
    filename=$(basename "$file")
    
    # Count inline styles (skip index.html which may have grid layouts)
    if [ "$filename" != "index.html" ]; then
        inline_count=$(grep -c 'style="' "$file" 2>/dev/null || echo 0)
        if [ "$inline_count" -gt 0 ]; then
            echo "❌ $filename: $inline_count inline style(s) detected"
            grep -n 'style="' "$file" | head -3
            ((INLINE_STYLE_VIOLATIONS++))
        fi
    fi
done

# Check 3: Verify main.css exists and is valid
echo ""
echo "✅ Check 3: Verify main.css File"
if [ -f "docs/assets/css/main.css" ]; then
    size=$(du -h docs/assets/css/main.css | awk '{print $1}')
    echo "✅ main.css exists ($size)"
    
    # Check for key glassmorphism variables
    if grep -q 'bg-primary.*#0a0e27' docs/assets/css/main.css && \
       grep -q 'bg-secondary.*#1a1f3a' docs/assets/css/main.css; then
        echo "✅ Dark blue theme variables present"
    else
        echo "⚠️  Theme variables may be missing or incorrect"
    fi
else
    echo "❌ main.css NOT FOUND at docs/assets/css/main.css"
    ((CSS_VIOLATIONS++))
fi

# Summary
echo ""
echo "=================================================="
echo "📊 CSS Compliance Summary"
echo "=================================================="
echo "Broken CSS references: $BROKEN_CSS_REFS"
echo "CSS link violations: $CSS_VIOLATIONS"
echo "Inline style violations: $INLINE_STYLE_VIOLATIONS"

TOTAL_VIOLATIONS=$((BROKEN_CSS_REFS + CSS_VIOLATIONS + INLINE_STYLE_VIOLATIONS))

if [ $TOTAL_VIOLATIONS -eq 0 ]; then
    echo ""
    echo "✅ ALL CHECKS PASSED - 100% CSS Compliance"
    exit 0
else
    echo ""
    echo "❌ FAILED - $TOTAL_VIOLATIONS violations found"
    echo ""
    echo "🔧 Required Actions:"
    [ $BROKEN_CSS_REFS -gt 0 ] && echo "  1. Replace 'documentation-styling-standards.css' with 'main.css'"
    [ $CSS_VIOLATIONS -gt 0 ] && echo "  2. Fix CSS link issues (missing, duplicate, or alternate files)"
    [ $INLINE_STYLE_VIOLATIONS -gt 0 ] && echo "  3. Remove all inline styles, define classes in main.css"
    exit 1
fi
