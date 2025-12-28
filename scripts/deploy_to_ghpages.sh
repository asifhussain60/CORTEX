#!/usr/bin/env bash
# Quick GitHub Pages deployment - deploys docs/ to gh-pages branch
# Usage: ./scripts/deploy_to_ghpages.sh

set -e
echo "🚀 Deploying to GitHub Pages..."

# Switch to gh-pages or create if doesn't exist
if git show-ref --verify --quiet refs/heads/gh-pages; then
    git checkout gh-pages
else
    git checkout -b gh-pages origin/gh-pages 2>/dev/null || git checkout --orphan gh-pages
fi

# Clean and copy docs
find . -maxdepth 1 ! -name '.git' ! -name '.' ! -name '..' -exec rm -rf {} + 2>/dev/null || true
cp -R docs/* .
echo "" > .nojekyll

# Commit and push
git add -A
if ! git diff --cached --quiet; then
    git commit --no-verify -m "Deploy from $(git rev-parse --abbrev-ref @{-1})@$(git rev-parse --short @{-1})

Auto-deployment: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin gh-pages --force
    echo "✅ Deployed! Site will be live at:"
    echo "   https://asifhussain60.github.io/CORTEX/story/viewer.html"
else
    echo "⚠️  No changes to deploy"
fi

# Return to previous branch
git checkout -
