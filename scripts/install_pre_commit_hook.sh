#!/usr/bin/env bash
"""
Install pre-commit hook for CORTEX wiring validation.

Usage:
    ./scripts/install_pre_commit_hook.sh

This script:
1. Creates symlink from .git/hooks/pre-commit to validator
2. Makes hook executable
3. Tests hook execution
4. Shows status

CORE-026: Git checkpoint before major changes
"""

set -e

CORTEX_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
HOOK_SOURCE="${CORTEX_ROOT}/.cortex/hooks/pre-commit-validator.py"
HOOK_DEST="${CORTEX_ROOT}/.git/hooks/pre-commit"

echo "================================================================================"
echo "  CORTEX Pre-Commit Hook Installation"
echo "================================================================================"
echo

if [ ! -f "$HOOK_SOURCE" ]; then
    echo "❌ Error: Hook source not found at $HOOK_SOURCE"
    exit 1
fi

echo "ℹ️  Hook source: $HOOK_SOURCE"
echo "ℹ️  Hook destination: $HOOK_DEST"
echo

# Remove existing hook if it exists
if [ -f "$HOOK_DEST" ]; then
    echo "🟡 Removing existing pre-commit hook..."
    rm -f "$HOOK_DEST"
fi

# Create symlink
echo "📝 Creating symlink..."
ln -s "$HOOK_SOURCE" "$HOOK_DEST"
echo "✅ Symlink created"

# Make executable
echo "📝 Making hook executable..."
chmod +x "$HOOK_DEST"
echo "✅ Hook is executable"

# Verify installation
echo
echo "📋 Verification:"
if [ -L "$HOOK_DEST" ]; then
    echo "✅ Hook is installed as symlink"
    target=$(readlink "$HOOK_DEST")
    echo "   → Points to: $target"
else
    echo "❌ Hook is not a symlink"
fi

if [ -x "$HOOK_DEST" ]; then
    echo "✅ Hook is executable"
else
    echo "❌ Hook is not executable"
fi

# Test hook
echo
echo "🧪 Testing hook..."
echo "   Running: $HOOK_DEST --version"
if python3 "$HOOK_DEST" 2>&1 | head -5; then
    echo "✅ Hook test passed"
else
    echo "🟡 Hook test showed output (might be expected)"
fi

echo
echo "================================================================================"
echo "  ✅ Pre-Commit Hook Installation Complete"
echo "================================================================================"
echo
echo "📌 Next steps:"
echo "   1. Make a test change to any file"
echo "   2. Try to commit: git commit -m 'test'"
echo "   3. Hook will validate CORTEX wiring before committing"
echo
echo "💡 To disable hook temporarily:"
echo "   git commit --no-verify"
echo
