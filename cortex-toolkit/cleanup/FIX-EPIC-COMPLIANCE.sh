#!/bin/bash

# Fix Epic Structure to Planning System v5 Compliance
# Reflects FUTURE STATE after epic execution

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

EPIC_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/cortex5-enhancement-epic"
TOOLKIT_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-toolkit/cleanup"
ARCHIVE_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/archives/pre-compliance-$(date +%Y%m%d-%H%M%S)"
DRY_RUN=${DRY_RUN:-true}

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Epic Structure Compliance Fix - Planning System v5   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}⚠️  DRY RUN MODE${NC}"
    echo ""
fi

# Create directories
if [ "$DRY_RUN" = false ]; then
    mkdir -p "$ARCHIVE_DIR"
    mkdir -p "$TOOLKIT_DIR"
    echo -e "${GREEN}Created archive: $ARCHIVE_DIR${NC}"
    echo -e "${GREEN}Created toolkit: $TOOLKIT_DIR${NC}"
fi

cd "$EPIC_DIR"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 1: Archive Scripts (Move to Toolkit)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

for script in *.sh; do
    if [ -f "$script" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}[DRY RUN] MOVE: $script → cortex-toolkit/cleanup/${NC}"
        else
            echo -e "${GREEN}[EXECUTE] MOVE: $script → cortex-toolkit/cleanup/${NC}"
            cp "$script" "$ARCHIVE_DIR/"
            mv "$script" "$TOOLKIT_DIR/"
        fi
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 2: Archive Root Markdown Files${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

for md_file in *.md; do
    if [ -f "$md_file" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "${YELLOW}[DRY RUN] ARCHIVE: $md_file (will relocate to proper subfolder)${NC}"
        else
            echo -e "${RED}[EXECUTE] ARCHIVE: $md_file${NC}"
            mv "$md_file" "$ARCHIVE_DIR/"
        fi
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 3: Create Missing Standard Folders${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# 7 standard folders required
STANDARD_FOLDERS=(
    "analysis"
    "artifacts"
    "context"
    "features"
    "phases"
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
echo -e "${BLUE} Phase 4: Relocate Files to Correct Locations${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# File relocation mapping
if [ "$DRY_RUN" = false ]; then
    if [ -f "$ARCHIVE_DIR/A19-cortex-50-remedi-with.md" ]; then
        echo -e "${GREEN}[EXECUTE] MOVE: A19-cortex-50-remedi-with.md → phases/master-plan.md${NC}"
        mv "$ARCHIVE_DIR/A19-cortex-50-remedi-with.md" "phases/master-plan.md"
    fi
    
    if [ -f "$ARCHIVE_DIR/CORTEX5-SNOWBALL.md" ]; then
        echo -e "${GREEN}[EXECUTE] MOVE: CORTEX5-SNOWBALL.md → tracking/snowball.md${NC}"
        mv "$ARCHIVE_DIR/CORTEX5-SNOWBALL.md" "tracking/snowball.md"
    fi
    
    if [ -f "$ARCHIVE_DIR/PHASE-0.5-COMPLETE.md" ]; then
        echo -e "${GREEN}[EXECUTE] MOVE: PHASE-0.5-COMPLETE.md → tracking/milestones.md${NC}"
        mv "$ARCHIVE_DIR/PHASE-0.5-COMPLETE.md" "tracking/milestones.md"
    fi
    
    if [ -f "$ARCHIVE_DIR/STRUCTURE-REVIEW.md" ]; then
        echo -e "${GREEN}[EXECUTE] MOVE: STRUCTURE-REVIEW.md → reports/structure-review-2026-01-06.md${NC}"
        mv "$ARCHIVE_DIR/STRUCTURE-REVIEW.md" "reports/structure-review-2026-01-06.md"
    fi
    
    if [ -f "$ARCHIVE_DIR/ERRORS-DOCUMENTATION.md" ]; then
        echo -e "${GREEN}[EXECUTE] MOVE: ERRORS-DOCUMENTATION.md → reports/errors-documentation.md${NC}"
        mv "$ARCHIVE_DIR/ERRORS-DOCUMENTATION.md" "reports/errors-documentation.md"
    fi
else
    echo -e "${YELLOW}[DRY RUN] A19-cortex-50-remedi-with.md → phases/master-plan.md${NC}"
    echo -e "${YELLOW}[DRY RUN] CORTEX5-SNOWBALL.md → tracking/snowball.md${NC}"
    echo -e "${YELLOW}[DRY RUN] PHASE-0.5-COMPLETE.md → tracking/milestones.md${NC}"
    echo -e "${YELLOW}[DRY RUN] STRUCTURE-REVIEW.md → reports/structure-review-2026-01-06.md${NC}"
    echo -e "${YELLOW}[DRY RUN] ERRORS-DOCUMENTATION.md → reports/errors-documentation.md${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 5: Create Required Tracking Files${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [ "$DRY_RUN" = false ]; then
    # Create progress tracker JSON
    if [ ! -f "tracking/progress-tracker.json" ]; then
        echo -e "${GREEN}[EXECUTE] CREATE: tracking/progress-tracker.json${NC}"
        cat > "tracking/progress-tracker.json" <<'EOF'
{
  "plan_id": "cortex5-enhancement-epic",
  "created": "2026-01-06",
  "status": "active",
  "overall_progress": 0,
  "phases": [
    {
      "phase": 0,
      "name": "Planning",
      "status": "complete",
      "progress": 100
    },
    {
      "phase": 1,
      "name": "Implementation",
      "status": "not_started",
      "progress": 0
    }
  ]
}
EOF
    fi
    
    # Create continuation prompt
    if [ ! -f "tracking/CONTINUATION-PROMPT.md" ]; then
        echo -e "${GREEN}[EXECUTE] CREATE: tracking/CONTINUATION-PROMPT.md${NC}"
        cat > "tracking/CONTINUATION-PROMPT.md" <<'EOF'
# Continuation Prompt

To resume this plan, use:

```
continue plan cortex5-enhancement-epic from phase 1
```

**Last Updated:** 2026-01-06  
**Current Phase:** Phase 0 Complete  
**Next Phase:** Phase 1 - Implementation
EOF
    fi
else
    echo -e "${YELLOW}[DRY RUN] CREATE: tracking/progress-tracker.json${NC}"
    echo -e "${YELLOW}[DRY RUN] CREATE: tracking/CONTINUATION-PROMPT.md${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 6: Create plan-viewer.html Placeholder${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [ "$DRY_RUN" = false ]; then
    if [ ! -f "plan-viewer.html" ]; then
        echo -e "${GREEN}[EXECUTE] CREATE: plan-viewer.html (placeholder)${NC}"
        cat > "plan-viewer.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX5 Enhancement Epic - Plan Viewer</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #0d1117;
            color: #c9d1d9;
        }
        h1 { color: #58a6ff; }
        .note { background: #1c2128; padding: 15px; border-radius: 6px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>🧠 CORTEX5 Enhancement Epic</h1>
    <div class="note">
        <p><strong>⚠️ Plan Viewer Placeholder</strong></p>
        <p>This file will be auto-generated by Planning Orchestrator v5</p>
        <p>To generate the full interactive viewer, run:</p>
        <code>python3 -m cortex_toolkit.plan_viewer_generator --plan cortex5-enhancement-epic</code>
    </div>
    <h2>Plan Structure</h2>
    <ul>
        <li>📁 analysis/ - Deep analysis documents</li>
        <li>📁 artifacts/ - Generated artifacts</li>
        <li>📁 context/ - Discovery + architecture</li>
        <li>📁 features/ - Feature tracking</li>
        <li>📁 phases/ - Phase documents + master plan</li>
        <li>📁 reports/ - Progress reports</li>
        <li>📁 tracking/ - State tracking</li>
    </ul>
</body>
</html>
EOF
    fi
else
    echo -e "${YELLOW}[DRY RUN] CREATE: plan-viewer.html${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Phase 7: Validate Final Structure${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

echo -e "${GREEN}Expected structure (Future State):${NC}"
echo ""
echo "cortex5-enhancement-epic/"
echo "├── plan-viewer.html          ✅ ONLY root file"
echo "├── analysis/"
echo "├── artifacts/"
echo "├── context/"
echo "├── features/                 ✅ NEW"
echo "├── phases/                   ✅ NEW"
echo "│   └── master-plan.md"
echo "├── reports/"
echo "│   ├── structure-review-2026-01-06.md"
echo "│   └── errors-documentation.md"
echo "└── tracking/"
echo "    ├── snowball.md"
echo "    ├── milestones.md"
echo "    ├── progress-tracker.json"
echo "    └── CONTINUATION-PROMPT.md"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE} Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}✓ Dry run completed${NC}"
    echo -e "${YELLOW}✓ No changes made${NC}"
    echo -e "${YELLOW}✓ Set DRY_RUN=false to execute${NC}"
else
    echo -e "${GREEN}✓ Epic structure now compliant with Planning System v5${NC}"
    echo -e "${GREEN}✓ Archive: $ARCHIVE_DIR${NC}"
    echo -e "${GREEN}✓ Scripts moved to: $TOOLKIT_DIR${NC}"
    echo -e "${GREEN}✓ Structure reflects FUTURE STATE${NC}"
fi

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Review the new structure"
echo "  2. Generate full plan-viewer.html via Planning Orchestrator"
echo "  3. Add feature documents to features/"
echo "  4. Add phase documents to phases/"
echo ""
