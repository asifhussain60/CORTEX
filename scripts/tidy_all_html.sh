#!/bin/bash
# Fix all HTML files using HTML Tidy

DOCS_DIR="/Users/asifhussain/PROJECTS/CORTEX/docs"
FIXED_COUNT=0

echo "🧹 Tidying HTML files..."
echo ""

# Find all HTML files and tidy them
find "$DOCS_DIR" -name "*.html" -type f | while read -r file; do
    # Run tidy with:
    # -m: modify in place
    # -i: indent
    # -wrap 0: no line wrapping
    # -q: quiet mode
    # -utf8: use UTF-8
    # --tidy-mark no: don't add tidy meta tag
    tidy -m -i -wrap 0 -q -utf8 --tidy-mark no "$file" 2>/dev/null
    
    if [ $? -eq 0 ] || [ $? -eq 1 ]; then
        # Exit code 0 = no errors, 1 = warnings (both acceptable)
        echo "✅ Fixed: ${file#$DOCS_DIR/}"
        ((FIXED_COUNT++))
    fi
done

echo ""
echo "=========================================="
echo "✅ Tidied $FIXED_COUNT HTML files"
