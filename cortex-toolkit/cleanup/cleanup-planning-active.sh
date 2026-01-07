#!/bin/bash

# CORTEX Planning Active Directory Cleanup Script
# Version: 1.0.0
# Date: 2026-01-06
# Purpose: Clean up planning/active directory structure

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning"
ACTIVE_DIR="$BASE_DIR/active"
EPIC_DIR="$ACTIVE_DIR/cortex5-enhancement-epic"
BACKUP_DIR="$BASE_DIR/backups/cleanup-$(date +%Y%m%d-%H%M%S)"
DRY_RUN=${DRY_RUN:-true}  # Set to false to actually execute

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  CORTEX Planning Active Directory Cleanup Script      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}⚠️  DRY RUN MODE - No changes will be made${NC}"
    echo -e "${YELLOW}   Set DRY_RUN=false to execute changes${NC}"
    echo ""
fi

# Create backup directory
if [ "$DRY_RUN" = false ]; then
    echo -e "${GREEN}Creating backup at: $BACKUP_DIR${NC}"
    mkdir -p "$BACKUP_DIR"
fi

# Function to log actions
log_action() {
    local action=$1
    local target=$2
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN] $action: $target${NC}"
    else
        echo -e "${GREEN}[EXECUTE] $action: $target${NC}"
    fi
}

# Function to backup and remove
backup_and_remove() {
    local dir=$1
    local reason=$2
    
    if [ -d "$dir" ]; then
        log_action "REMOVE" "$dir ($reason)"
        if [ "$DRY_RUN" = false ]; then
            cp -r "$dir" "$BACKUP_DIR/$(basename $dir)"
            rm -rf "$dir"
        fi
    fi
}

# Function to move directory
move_directory() {
    local src=$1
    local dest=$2
    local reason=$3
    
    if [ -d "$src" ]; then
        log_action "MOVE" "$src → $dest ($reason)"
        if [ "$DRY_RUN" = false ]; then
            cp -r "$src" "$BACKUP_DIR/$(basename $src)"
            mv "$src" "$dest"
        fi
    fi
}

# Function to rename directory
rename_directory() {
    local old=$1
    local new=$2
    local reason=$3
    
    if [ -d "$old" ]; then
        log_action "RENAME" "$(basename $old) → $(basename $new) ($reason)"
        if [ "$DRY_RUN" = false ]; then
            cp -r "$old" "$BACKUP_DIR/$(basename $old)"
            mv "$old" "$new"
        fi
    fi
}

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 1: Remove UUID-based Plans (Duplicates)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

cd "$EPIC_DIR" || exit 1

# Remove UUID-based plans (assumed duplicates)
for uuid_plan in plan-*; do
    if [ -d "$uuid_plan" ]; then
        backup_and_remove "$uuid_plan" "UUID-based duplicate"
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 2: Move Child Plans to Top Level${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Move child plans to top level active directory
for child_plan in a19-*; do
    if [ -d "$child_plan" ] && [ "$child_plan" != "a19-holistic-review-cortex" ]; then
        move_directory "$child_plan" "$ACTIVE_DIR/$child_plan" "Child plan relocation"
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 3: Rename Long Folder Names${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Rename folders exceeding 22 characters
if [ -d "continue-cortex5-enhancement-epic-phase-1" ]; then
    rename_directory "continue-cortex5-enhancement-epic-phase-1" "c5-epic-phase-1" "Name >22 chars"
fi

if [ -d "continue-cortex5-enhancement-epic-with-phase-1" ]; then
    rename_directory "continue-cortex5-enhancement-epic-with-phase-1" "c5-epic-w-phase-1" "Name >22 chars"
fi

if [ -d "continue-cortex5-enhancement-epic-from-phase-1--" ]; then
    rename_directory "continue-cortex5-enhancement-epic-from-phase-1--" "c5-epic-from-p1" "Name >22 chars"
fi

if [ -d "continue-plan-cortex5-enhancement-epic-from" ]; then
    rename_directory "continue-plan-cortex5-enhancement-epic-from" "c5-plan-epic-from" "Name >22 chars"
fi

if [ -d "fix-for-incorrect-plan-folder-placement---child" ]; then
    rename_directory "fix-for-incorrect-plan-folder-placement---child" "fix-plan-folder-place" "Name >22 chars"
fi

if [ -d "investigate-plan-folder-path-bug---child-plans" ]; then
    rename_directory "investigate-plan-folder-path-bug---child-plans" "inv-plan-folder-bug" "Name >22 chars"
fi

if [ -d "test-epic-child-placement-feature-inside-cortex5" ]; then
    rename_directory "test-epic-child-placement-feature-inside-cortex5" "test-epic-child-place" "Name >22 chars"
fi

if [ -d "script-consolidation-governance-for" ]; then
    rename_directory "script-consolidation-governance-for" "script-consol-gov" "Name >22 chars"
fi

if [ -d "tdd-planning-orchestrator-folder-structure" ]; then
    rename_directory "tdd-planning-orchestrator-folder-structure" "tdd-plan-orch-struct" "Name >22 chars"
fi

# Also handle continue-plan-plan case
if [ -d "continue-plan-plan-5ef62288-0f08-459a-8192" ]; then
    backup_and_remove "continue-plan-plan-5ef62288-0f08-459a-8192" "UUID continuation duplicate"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 4: Standardize Folder Structure${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Function to standardize folder structure
standardize_structure() {
    local plan_dir=$1
    
    if [ ! -d "$plan_dir" ]; then
        return
    fi
    
    log_action "STANDARDIZE" "$plan_dir"
    
    if [ "$DRY_RUN" = false ]; then
        # Create standard folders if missing
        mkdir -p "$plan_dir/analysis"
        mkdir -p "$plan_dir/artifacts"
        mkdir -p "$plan_dir/context"
        mkdir -p "$plan_dir/reports"
        mkdir -p "$plan_dir/tracking"
        
        # Remove non-standard folders
        if [ -d "$plan_dir/integration" ]; then
            echo -e "${YELLOW}  Moving integration/ to artifacts/${NC}"
            mv "$plan_dir/integration"/* "$plan_dir/artifacts/" 2>/dev/null || true
            rmdir "$plan_dir/integration" 2>/dev/null || true
        fi
        
        if [ -d "$plan_dir/features" ]; then
            echo -e "${YELLOW}  Moving features/ to analysis/${NC}"
            mv "$plan_dir/features"/* "$plan_dir/analysis/" 2>/dev/null || true
            rmdir "$plan_dir/features" 2>/dev/null || true
        fi
    fi
}

# Standardize all remaining plans
for plan_dir in */; do
    if [ -d "$plan_dir" ]; then
        standardize_structure "$plan_dir"
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}✓ Dry run completed successfully${NC}"
    echo -e "${YELLOW}✓ No changes were made${NC}"
    echo -e "${YELLOW}✓ Review the log above and set DRY_RUN=false to execute${NC}"
else
    echo -e "${GREEN}✓ Cleanup completed successfully${NC}"
    echo -e "${GREEN}✓ Backup created at: $BACKUP_DIR${NC}"
    echo -e "${GREEN}✓ All changes applied${NC}"
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Review the changes"
echo "  2. Fix syntax errors in src/utils/plan_folder_manager.py"
echo "  3. Run validation: python3 -m src.utils.validate_planning_structure"
echo ""
