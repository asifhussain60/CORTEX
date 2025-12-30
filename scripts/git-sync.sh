#!/bin/bash
# CORTEX Git Sync Automation
# Usage: ./scripts/git-sync.sh "commit message" [branch]

set -e  # Exit on error

COMMIT_MSG="${1:-chore: sync workspace changes}"
BRANCH="${2:-CORTEX-4.0}"

echo "🔄 CORTEX Git Sync Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Phase 1: Status Check
echo "📊 Phase 1: Checking status..."
git status --short

# Phase 2: Stage Changes
echo "📦 Phase 2: Staging changes..."
git add -A
STAGED_COUNT=$(git diff --cached --name-only | wc -l | tr -d ' ')
echo "✅ Staged: $STAGED_COUNT files"

# Phase 3: Commit
echo "💾 Phase 3: Committing changes..."
if git diff --cached --quiet; then
    echo "⚠️  Nothing to commit"
else
    git commit -m "$COMMIT_MSG"
    echo "✅ Committed successfully"
fi

# Phase 4: Pull & Merge (Non-Interactive)
echo "⬇️  Phase 4: Pulling from origin..."
GIT_EDITOR=true git pull origin "$BRANCH" --no-rebase

# Phase 5: Verify Clean State
echo "🔍 Phase 5: Verifying state..."
if git status | grep -q "nothing to commit"; then
    echo "✅ Working tree clean"
else
    echo "⚠️  Uncommitted changes detected"
    git status
    exit 1
fi

# Phase 6: Push
echo "⬆️  Phase 6: Pushing to origin..."
git push origin "$BRANCH"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CORTEX Git Sync Complete!"
echo ""
echo "Latest commit:"
git log --oneline -1
echo ""
echo "Branch status:"
git status --short --branch
