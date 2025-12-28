#!/bin/bash
# Image Status Verification for Story Chapters

echo "📊 Story Chapter Image Status Report"
echo "===================================="
echo ""

chapters=(
    "Prologue:2"
    "Chapter-01:3"
    "Chapter-02:2"
    "Chapter-03:2"
    "Chapter-04:1"
    "Chapter-05:1"
    "Chapter-06:1"
    "Chapter-07:2"
    "Chapter-08:1"
    "Chapter-09:2"
    "Chapter-10:1"
    "Chapter-11:2"
    "Chapter-12:1"
    "Chapter-13:1"
)

total_chapters=0
chapters_with_images=0

for chapter_info in "${chapters[@]}"; do
    IFS=':' read -r chapter expected_count <<< "$chapter_info"
    ((total_chapters++))
    
    if [ -f "$chapter/index.md" ]; then
        actual_count=$(grep -c 'src="../illustrations/images' "$chapter/index.md" 2>/dev/null || echo "0")
        
        if [ "$actual_count" -ge 1 ]; then
            echo "✅ $chapter: $actual_count image(s)"
            ((chapters_with_images++))
        else
            echo "❌ $chapter: NO IMAGES"
        fi
    else
        echo "⚠️  $chapter: index.md not found"
    fi
done

echo ""
echo "===================================="
echo "Summary: $chapters_with_images/$total_chapters chapters have images"

if [ "$chapters_with_images" -eq "$total_chapters" ]; then
    echo "✅ ALL CHAPTERS HAVE AT LEAST ONE IMAGE"
    exit 0
else
    echo "❌ Some chapters are missing images"
    exit 1
fi
