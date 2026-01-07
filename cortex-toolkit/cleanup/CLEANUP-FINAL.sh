#!/bin/bash

# Final Cleanup - Keep only cortex5-enhancement-epic
# All other plans moved to archives

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ACTIVE_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active"
ARCHIVE_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/archives/cleanup-final-$(date +%Y%m%d-%H%M%S)"
DRY_RUN=${DRY_RUN:-true}

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  CORTEX Final Cleanup - Keep Only cortex5-enhancement-epic ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}⚠️  DRY RUN MODE - No changes will be made${NC}"
    echo -e "${YELLOW}   Set DRY_RUN=false to execute${NC}"
    echo ""
fi

# Create archive directory
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$ARCHIVE_DIR"
    echo -e "${GREEN}Created archive: $ARCHIVE_DIR${NC}"
fi

cd "$ACTIVE_DIR"

echo -e "${BLUE}Plans to ARCHIVE (move to archives):${NC}"
echo ""

for dir in */; do
    dir_name="${dir%/}"
    
    # Skip cortex5-enhancement-epic (keep this one)
    if [ "$dir_name" = "cortex5-enhancement-epic" ]; then
        echo -e "${GREEN}✓ KEEP: $dir_name (correct plan)${NC}"
        continue
    fi
    
    # Archive everything else
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN] ARCHIVE: $dir_name${NC}"
    else
        echo -e "${RED}[EXECUTE] ARCHIVE: $dir_name${NC}"
        mv "$dir_name" "$ARCHIVE_DIR/"
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}✓ Dry run completed${NC}"
    echo -e "${YELLOW}✓ No changes made${NC}"
    echo -e "${YELLOW}✓ Set DRY_RUN=false to execute${NC}"
else
    echo -e "${GREEN}✓ Cleanup completed${NC}"
    echo -e "${GREEN}✓ Archive location: $ARCHIVE_DIR${NC}"
    echo -e "${GREEN}✓ Only cortex5-enhancement-epic remains in active/${NC}"
fi

echo ""
echo -e "${BLUE}Note:${NC} docs-orchestrator-v2 plan from other machine can be added manually"
echo ""
