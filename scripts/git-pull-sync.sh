#!/bin/bash
# CORTEX Git Pull Sync - Safe cross-machine synchronization
# Author: Asif Hussain
# Copyright © 2025 Asif Hussain. All rights reserved.

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Parse arguments
SAFE_MODE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --safe|-s)
            SAFE_MODE=true
            shift
            ;;
        --dry-run|-d)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --safe, -s       Use rebase instead of hard reset (preserves local changes)"
            echo "  --dry-run, -d    Show what would be done without making changes"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0               Standard sync (hard reset to match remote)"
            echo "  $0 --safe        Safe sync (rebase local changes)"
            echo "  $0 --dry-run     Preview changes without executing"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo ""
echo -e "${CYAN}======================================================================${NC}"
echo -e "${CYAN}  🔄 CORTEX Git Pull Sync${NC}"
echo -e "${CYAN}======================================================================${NC}"

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "\n📍 Current Branch: ${YELLOW}${CURRENT_BRANCH}${NC}"

# Check for uncommitted changes
STATUS=$(git status --porcelain)
if [ -n "$STATUS" ] && [ "$DRY_RUN" = false ]; then
    echo -e "\n${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    echo "$STATUS"
    
    if [ "$SAFE_MODE" = true ]; then
        echo -e "\nThese changes will be ${GREEN}preserved and rebased${NC}"
    else
        echo -e "\nThese changes will be ${RED}LOST with hard reset${NC}"
    fi
    
    read -p $'\nContinue? (yes/no): ' response
    if [ "$response" != "yes" ]; then
        echo -e "\n${RED}❌ Sync cancelled${NC}"
        exit 1
    fi
fi

if [ "$DRY_RUN" = true ]; then
    echo -e "\n${MAGENTA}🔍 DRY RUN MODE - No changes will be made${NC}"
fi

# Fetch all changes
echo -e "\n${CYAN}📡 Fetching from remote...${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "   ${GRAY}Would run: git fetch --all --prune${NC}"
else
    git fetch --all --prune
    echo -e "   ${GREEN}✅ Fetch complete${NC}"
fi

# Show what will be deleted/changed
echo -e "\n${CYAN}📊 Changes from remote:${NC}"
DIFF=$(git diff --name-status "origin/$CURRENT_BRANCH" || echo "")
if [ -n "$DIFF" ]; then
    while IFS=$'\t' read -r status file; do
        case $status in
            D)
                echo -e "   ${RED}🗑️  DELETE: $file${NC}"
                ;;
            A)
                echo -e "   ${GREEN}➕ ADD:    $file${NC}"
                ;;
            M)
                echo -e "   ${YELLOW}📝 MODIFY: $file${NC}"
                ;;
            *)
                echo -e "   ${GRAY}$status $file${NC}"
                ;;
        esac
    done <<< "$DIFF"
else
    echo -e "   ${GREEN}✅ Already up to date${NC}"
fi

# Perform sync
echo -e "\n${CYAN}🔄 Syncing...${NC}"
if [ "$DRY_RUN" = true ]; then
    if [ "$SAFE_MODE" = true ]; then
        echo -e "   ${GRAY}Would run: git pull --rebase origin $CURRENT_BRANCH${NC}"
    else
        echo -e "   ${GRAY}Would run: git reset --hard origin/$CURRENT_BRANCH${NC}"
    fi
else
    if [ "$SAFE_MODE" = true ]; then
        echo -e "   ${YELLOW}Using safe rebase mode...${NC}"
        git pull --rebase origin "$CURRENT_BRANCH"
    else
        echo -e "   ${YELLOW}Using hard reset (exact match with remote)...${NC}"
        git reset --hard "origin/$CURRENT_BRANCH"
    fi
    echo -e "   ${GREEN}✅ Sync complete${NC}"
fi

# Clean up untracked files from deleted directories
echo -e "\n${CYAN}🧹 Checking for orphaned files...${NC}"
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -n "$UNTRACKED" ]; then
    echo -e "   ${YELLOW}Found untracked files:${NC}"
    while IFS= read -r file; do
        echo -e "     ${GRAY}- $file${NC}"
    done <<< "$UNTRACKED"
    
    if [ "$DRY_RUN" = false ]; then
        read -p $'\n   Remove untracked files? (yes/no): ' response
        if [ "$response" = "yes" ]; then
            git clean -fd
            echo -e "   ${GREEN}✅ Untracked files removed${NC}"
        fi
    else
        echo -e "   ${GRAY}Would prompt to remove with: git clean -fd${NC}"
    fi
else
    echo -e "   ${GREEN}✅ No orphaned files${NC}"
fi

# Final status
echo -e "\n${CYAN}📊 Final Status:${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "   ${MAGENTA}(DRY RUN - no changes made)${NC}"
else
    FINAL_STATUS=$(git status --short)
    if [ -n "$FINAL_STATUS" ]; then
        git status --short
    else
        echo -e "   ${GREEN}✅ Working tree clean${NC}"
    fi
fi

echo ""
echo -e "${CYAN}======================================================================${NC}"
echo -e "${GREEN}  ✅ CORTEX Git Pull Sync Complete${NC}"
echo -e "${CYAN}======================================================================${NC}"
echo ""
