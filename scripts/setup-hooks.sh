#!/bin/bash
# =============================================================================
# CORTEX Git Hooks Setup Script
# =============================================================================
# Authority: CORE-035 (Single Canonical Implementation)
# AC-ID: AC-HOOKS-SETUP-001
#
# This script configures Git to use version-controlled hooks from .cortex/hooks/
# Run once after cloning the repository.
#
# Usage:
#   ./scripts/setup-hooks.sh
#   # or
#   make setup-hooks
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  🔧 CORTEX Git Hooks Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Get repository root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ -z "$REPO_ROOT" ]; then
    echo -e "${RED}❌ Not in a git repository${NC}"
    exit 1
fi

cd "$REPO_ROOT"

# Check if .cortex/hooks exists
if [ ! -d ".cortex/hooks" ]; then
    echo -e "${RED}❌ .cortex/hooks directory not found${NC}"
    echo -e "${YELLOW}   Expected: $REPO_ROOT/.cortex/hooks${NC}"
    exit 1
fi

# Configure git to use .cortex/hooks as the hooks directory
echo -e "${BLUE}Configuring git hooks path...${NC}"
git config core.hooksPath .cortex/hooks

# Verify configuration
HOOKS_PATH=$(git config --get core.hooksPath)

if [ "$HOOKS_PATH" = ".cortex/hooks" ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ Git hooks configured successfully!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Hooks directory: ${BLUE}.cortex/hooks/${NC}"
    echo -e "  Active hooks:"
    
    for hook in "$REPO_ROOT/.cortex/hooks"/*; do
        if [ -f "$hook" ] && [ -x "$hook" ]; then
            echo -e "    • ${GREEN}$(basename "$hook")${NC}"
        fi
    done
    
    echo ""
    echo -e "  ${YELLOW}These hooks will run automatically on git operations:${NC}"
    echo -e "    • pre-commit  → Before each commit (naming, placement, copyright)"
    echo -e "    • pre-push    → Before each push (12 production readiness checks)"
    echo ""
else
    echo -e "${RED}❌ Failed to configure git hooks path${NC}"
    exit 1
fi
