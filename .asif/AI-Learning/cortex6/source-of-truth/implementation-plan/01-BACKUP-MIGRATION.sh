#!/bin/bash
# ==============================================================================
# CORTEX 6.0 - Backup Migration Script (macOS/Linux)
# ==============================================================================
# Purpose: Move existing CORTEX files to __backup before greenfield build
# Author: Asif Hussain
# Version: 1.0.0
# ==============================================================================

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORTEX_ROOT="${1:-$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")}"

echo "=============================================="
echo "CORTEX 6.0 Backup Migration Script"
echo "=============================================="
echo ""
echo "CORTEX Root: $CORTEX_ROOT"
echo ""

# Confirm before proceeding
read -p "This will move ALL files to __backup. Continue? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# Create backup directory
BACKUP_DIR="$CORTEX_ROOT/__backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR_VERSIONED="$BACKUP_DIR/$TIMESTAMP"

echo ""
echo "Creating backup directory: $BACKUP_DIR_VERSIONED"
mkdir -p "$BACKUP_DIR_VERSIONED"

# Move all files and folders (except __backup)
echo "Moving files to backup..."
cd "$CORTEX_ROOT"

for item in * .*; do
    # Skip special entries
    if [[ "$item" == "." || "$item" == ".." || "$item" == "__backup" ]]; then
        continue
    fi
    
    # Skip if doesn't exist (glob didn't match)
    if [[ ! -e "$item" ]]; then
        continue
    fi
    
    echo "  Moving: $item"
    mv "$item" "$BACKUP_DIR_VERSIONED/"
done

# Move backup directory back to root
mv "$BACKUP_DIR_VERSIONED" "$CORTEX_ROOT/__backup_temp"
rm -rf "$BACKUP_DIR"
mv "$CORTEX_ROOT/__backup_temp" "$CORTEX_ROOT/__backup"

echo ""
echo "=============================================="
echo "Backup Complete!"
echo "=============================================="
echo ""
echo "Backup location: $CORTEX_ROOT/__backup"
echo "Workspace is now empty and ready for greenfield build."
echo ""
echo "Next steps:"
echo "  1. Open $CORTEX_ROOT in VS Code"
echo "  2. Load source-of-truth/02-COPILOT-BUILD-PROMPT.md in Copilot"
echo "  3. Follow the build instructions"
echo ""
echo "To restore from backup:"
echo "  mv __backup/* ."
echo ""
