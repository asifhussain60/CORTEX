#!/bin/bash

# CORTEX5 Enhancement Epic - Structure Cleanup
# Fix nested child plans and standardize folder structure

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

EPIC_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/cortex5-enhancement-epic"
ARCHIVE_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/archives/epic-nested-children-$(date +%Y%m%d-%H%M%S)"
DRY_RUN=${DRY_RUN:-true}

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  CORTEX5 Enhancement Epic - Structure Cleanup         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}⚠️  DRY RUN MODE${NC}"
    echo ""
fi

# Create archive
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$ARCHIVE_DIR"
    echo -e "${GREEN}Created archive: $ARCHIVE_DIR${NC}"
fi

cd "$EPIC_DIR"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 1: Remove Nested Child Plans${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# These are continuation/child plans that shouldn't be nested
NESTED_PLANS=(
    "c5-epic-from-p1"
    "c5-epic-phase-1"
    "c5-epic-w-phase-1"
    "c5-plan-epic-from"
    "fix-plan-folder-place"
    "inv-plan-folder-bug"
    "script-consol-gov"
    "tdd-plan-orch-struct"
    "test-epic-child-place"
)

for plan in "${NESTED_PLANS[@]}"; do
    if [ -d "$plan" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}[DRY RUN] ARCHIVE: $plan/ (nested child plan)${NC}"
        else
            echo -e "${RED}[EXECUTE] ARCHIVE: $plan/ (nested child plan)${NC}"
            mv "$plan" "$ARCHIVE_DIR/"
        fi
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 2: Consolidate Documents${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Move investigation report to reports/
if [ -f "INVESTIGATION-REPORT.md" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN] MOVE: INVESTIGATION-REPORT.md → reports/structure-investigation-20260106.md${NC}"
    else
        echo -e "${GREEN}[EXECUTE] MOVE: INVESTIGATION-REPORT.md → reports/structure-investigation-20260106.md${NC}"
        mkdir -p reports/
        mv INVESTIGATION-REPORT.md reports/structure-investigation-20260106.md
    fi
fi

# Remove duplicate markdown files
DUPLICATE_DOCS=(
    "FIX-PLAN-FOLDER-PLACEMENT.md"
    "GOVERNANCE-RULE-SCRIPT-ORGANIZATION.md"
)

for doc in "${DUPLICATE_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}[DRY RUN] REMOVE: $doc (duplicate/redundant)${NC}"
        else
            echo -e "${RED}[EXECUTE] REMOVE: $doc (duplicate/redundant)${NC}"
            mv "$doc" "$ARCHIVE_DIR/"
        fi
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 3: Create Missing Standard Folders${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Create standard 5-folder structure
STANDARD_FOLDERS=(
    "analysis"
    "artifacts"
    "context"
    "reports"
    "tracking"
)

for folder in "${STANDARD_FOLDERS[@]}"; do
    if [ ! -d "$folder" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}[DRY RUN] CREATE: $folder/${NC}"
        else
            echo -e "${GREEN}[EXECUTE] CREATE: $folder/${NC}"
            mkdir -p "$folder"
        fi
    else
        echo -e "${GREEN}✓ EXISTS: $folder/${NC}"
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 4: Validate Final Structure${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

echo -e "${GREEN}Expected structure after cleanup:${NC}"
echo ""
echo "cortex5-enhancement-epic/"
echo "├── README.md"
echo "├── A19-cortex-50-remedi-with.md"
echo "├── CORTEX5-SNOWBALL.md"
echo "├── PHASE-0.5-COMPLETE.md"
echo "├── analysis/"
echo "├── artifacts/"
echo "├── context/"
echo "├── reports/"
echo "└── tracking/"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}✓ Dry run completed${NC}"
    echo -e "${YELLOW}✓ No changes made${NC}"
    echo -e "${YELLOW}✓ Set DRY_RUN=false to execute${NC}"
else
    echo -e "${GREEN}✓ Epic structure cleanup completed${NC}"
    echo -e "${GREEN}✓ Archive: $ARCHIVE_DIR${NC}"
    echo -e "${GREEN}✓ Epic now follows Planning System v5 standard${NC}"
fi

echo ""
