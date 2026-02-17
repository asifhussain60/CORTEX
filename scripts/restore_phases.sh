#!/bin/bash
# Restore all phase files from git history
# Author: CORTEX Architect
# Date: 2026-02-17

set -e

COMMIT="1b1e7ddee^"
BASE_PATH="cortex-registry/_cortex-master/phases"
TARGET_PATH="cortex-registry/_cortex-master/phases"

echo "🔄 Restoring phase files from git history..."
echo "Commit: $COMMIT"
echo ""

# Get list of all phase files from git
git ls-tree -r --name-only "$COMMIT" "$BASE_PATH" | grep "\.yaml$" | while read -r file; do
    # Extract phase number and name
    filename=$(basename "$file")
    
    # Determine target folder based on source path
    if [[ "$file" =~ /completed/ ]]; then
        target_dir="$TARGET_PATH/completed"
    elif [[ "$file" =~ /active/ ]]; then
        # Active phases should go to planned
        target_dir="$TARGET_PATH/planned"
    elif [[ "$file" =~ /deferred/ ]]; then
        target_dir="$TARGET_PATH/deferred"
    else
        target_dir="$TARGET_PATH/completed"
    fi
    
    target_file="$target_dir/$filename"
    
    # Restore file from git
    if git show "$COMMIT:$file" > "$target_file" 2>/dev/null; then
        echo "✓ Restored: $filename → $(basename $target_dir)/"
    else
        echo "✗ Failed: $filename"
    fi
done

echo ""
echo "📊 Phase restoration summary:"
echo "  Completed: $(ls -1 $TARGET_PATH/completed/*.yaml 2>/dev/null | wc -l)"
echo "  Planned: $(ls -1 $TARGET_PATH/planned/*.yaml 2>/dev/null | wc -l)"
echo "  Deferred: $(ls -1 $TARGET_PATH/deferred/*.yaml 2>/dev/null | wc -l)"
echo ""
echo "✅ Phase restoration complete!"
