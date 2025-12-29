#!/bin/bash

cd /Users/asifhussain/PROJECTS/CORTEX/docs/story

echo "Checking image status across all chapters..."
echo ""

total_found=0
total_missing=0

for chapter in Prologue Chapter-{01..13}; do
    if [ -d "$chapter" ] && [ -f "$chapter/index.md" ]; then
        echo "=== $chapter ==="
        
        # Extract image paths from markdown
        while IFS= read -r line; do
            if [[ $line =~ src=\"\.\./illustrations/images/([^\"]+)\" ]]; then
                img_path="illustrations/images/${BASH_REMATCH[1]}"
                
                if [ -f "$img_path" ]; then
                    echo "  ✓ ${BASH_REMATCH[1]}"
                    ((total_found++))
                else
                    echo "  ✗ MISSING: ${BASH_REMATCH[1]}"
                    ((total_missing++))
                fi
            fi
        done < "$chapter/index.md"
        echo ""
    fi
done

echo "📊 SUMMARY:"
echo "Found: $total_found images"
echo "Missing: $total_missing images"
