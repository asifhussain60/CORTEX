#!/bin/bash
# Quick start script for CORTEX dashboards
# 
# Usage:
#   chmod +x dashboard-quick-start.sh
#   ./dashboard-quick-start.sh [open|serve|list]

set -e

CORTEX_ROOT="/Users/asifhussain/PROJECTS/CORTEX"
DASHBOARDS_DIR="$CORTEX_ROOT/company/dashboards"
REPOS_DIR="$DASHBOARDS_DIR/repos"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🎯 CORTEX Dashboard Quick Start"
echo "════════════════════════════════════════════════════════════════"
echo ""

case "${1:-list}" in
    open)
        echo "Opening CORTEX dashboard..."
        echo ""
        CORTEX_DASHBOARD="file://$REPOS_DIR/cortex/index.html"
        echo "URL: $CORTEX_DASHBOARD"
        echo ""
        open "$REPOS_DIR/cortex/index.html"
        ;;
    
    serve)
        echo "Starting HTTP server..."
        echo ""
        cd "$CORTEX_ROOT"
        echo "📍 Server will start at: http://localhost:8000"
        echo ""
        echo "View dashboards at:"
        echo "  - http://localhost:8000/company/dashboards/"
        echo "  - http://localhost:8000/company/dashboards/repos/cortex/"
        echo "  - http://localhost:8000/company/dashboards/repos/ksessions/"
        echo "  - http://localhost:8000/company/dashboards/repos/kashkole/"
        echo ""
        echo "Press Ctrl+C to stop the server"
        echo ""
        python3 -m http.server 8000
        ;;
    
    regenerate)
        echo "Regenerating dashboards..."
        echo ""
        cd "$CORTEX_ROOT"
        python3 generate_dashboard_html.py --clean
        echo ""
        echo "✅ Dashboards regenerated successfully!"
        ;;
    
    list|*)
        echo "Available dashboards:"
        echo ""
        for repo in cortex ksessions kashkole; do
            dashboard="$REPOS_DIR/$repo/index.html"
            if [ -f "$dashboard" ]; then
                size=$(ls -lh "$dashboard" | awk '{print $5}')
                echo "  ✅ $repo"
                echo "     File: $dashboard"
                echo "     Size: $size"
                echo "     File URL: file://$dashboard"
                echo ""
            else
                echo "  ❌ $repo (not found)"
                echo ""
            fi
        done
        
        echo "Usage:"
        echo "  ./dashboard-quick-start.sh open           # Open cortex dashboard"
        echo "  ./dashboard-quick-start.sh serve          # Start HTTP server"
        echo "  ./dashboard-quick-start.sh regenerate     # Regenerate all dashboards"
        echo "  ./dashboard-quick-start.sh list           # List all dashboards (default)"
        echo ""
        echo "Or open directly:"
        echo "  open file://$REPOS_DIR/cortex/index.html"
        echo "  open file://$REPOS_DIR/ksessions/index.html"
        echo "  open file://$REPOS_DIR/kashkole/index.html"
        echo ""
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
