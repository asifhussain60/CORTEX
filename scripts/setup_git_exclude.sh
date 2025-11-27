#!/bin/bash
# CORTEX Git Exclude Setup Script
# Configures .git/info/exclude to hide CORTEX files from git status
#
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.
# License: Proprietary

set -e

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
EXCLUDE_FILE="$REPO_ROOT/.git/info/exclude"

echo "🔧 Configuring Git local exclude for CORTEX..."

# Check if .git exists
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "❌ Not a Git repository. Run this from within a Git repository."
    exit 1
fi

# Ensure .git/info directory exists
mkdir -p "$REPO_ROOT/.git/info"

# Check if CORTEX exclusions already exist
if grep -q "CORTEX AI Assistant" "$EXCLUDE_FILE" 2>/dev/null; then
    echo "✅ CORTEX exclusions already configured"
    exit 0
fi

# Add CORTEX exclusions
cat >> "$EXCLUDE_FILE" << 'EOF'

# CORTEX AI Assistant - Local exclusion (not visible in git status)
# These files are already in .gitignore but this removes them from untracked status entirely
CORTEX/
.github/prompts/CORTEX.prompt.md
.github/prompts/cortex-story-builder.md
.github/prompts/modules/
.github/copilot-instructions.md
EOF

echo "✅ Git local exclude configured successfully"
echo "📊 Untracked file count should now be zero or near-zero"
echo ""
echo "Verify with: git status --porcelain"
