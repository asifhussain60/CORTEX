#!/bin/bash

# ==============================================================================
# Plan Viewer Dashboard Launcher
# ==============================================================================
# Opens the CORTEX 6.0 plan viewer dashboard in the default browser
# Usage: ./serve-dashboard.sh
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_FILE="$SCRIPT_DIR/plan-viewer.html"

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}🧠 CORTEX 6.0 Plan Viewer Dashboard${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if dashboard file exists
if [ ! -f "$DASHBOARD_FILE" ]; then
    echo -e "${YELLOW}⚠️  Dashboard file not found: $DASHBOARD_FILE${NC}"
    exit 1
fi

# Get absolute path for better cross-platform compatibility
DASHBOARD_URL="file://$(cd "$(dirname "$DASHBOARD_FILE")" && pwd)/$(basename "$DASHBOARD_FILE")"

echo -e "${GREEN}✅ Dashboard found${NC}"
echo -e "   Path: $DASHBOARD_FILE"
echo ""
echo -e "${BLUE}🚀 Launching dashboard in default browser...${NC}"
echo -e "   URL: $DASHBOARD_URL"
echo ""

# Open in browser (cross-platform)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$DASHBOARD_URL"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$DASHBOARD_URL" &>/dev/null || echo -e "${YELLOW}⚠️  Could not auto-open browser. Please open manually: $DASHBOARD_URL${NC}"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash / Cygwin)
    start "$DASHBOARD_URL"
else
    echo -e "${YELLOW}⚠️  Unknown OS. Please open manually: $DASHBOARD_URL${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dashboard launched successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Features:${NC}"
echo "   • Real-time progress tracking"
echo "   • Layer & phase visualization"
echo "   • Acceptance criteria coverage"
echo "   • Audit log viewer"
echo "   • Glassmorphism dark theme"
echo ""
echo -e "${BLUE}💡 Note:${NC} WebSocket updates will be available when the backend API is running."
echo "   To enable real-time updates, run: python3 -m src.orchestrators.dashboard.api"
echo ""
