#!/bin/bash
# ============================================================================
# CORTEX Repository Dashboard Launcher (macOS/Linux)
# ============================================================================
# Serves company/dashboards via HTTP on localhost:8888 and opens browser
#
# Usage: ./repo-dashboard.sh [repo-name]
#        ./repo-dashboard.sh ksessions
#        ./repo-dashboard.sh              # Opens index.html
# ============================================================================

set -e

PORT=8888
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_NAME="${1:-}"

echo ""
echo "============================================================"
echo "   CORTEX Repository Dashboard Launcher"
echo "============================================================"
echo ""

# Step 1: Kill any existing process on port
echo "[1/3] Checking for existing process on port $PORT..."
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "      Killing existing process on port $PORT..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "      Port $PORT cleared."
else
    echo "      Port $PORT is available."
fi

# Step 2: Change to dashboard directory
cd "$SCRIPT_DIR"

# Step 3: Determine URL
if [ -z "$REPO_NAME" ]; then
    URL="http://localhost:$PORT/index.html"
else
    URL="http://localhost:$PORT/spa/dashboard.html?repo=../$REPO_NAME"
fi

echo ""
echo "[2/3] Opening browser..."
echo "      URL: $URL"

# Open browser (works on macOS and Linux)
if command -v open &> /dev/null; then
    # macOS
    open "$URL"
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "$URL"
else
    echo "      Please open manually: $URL"
fi

# Step 4: Start Python HTTP server
echo ""
echo "[3/3] Starting HTTP server on http://localhost:$PORT ..."
echo ""
echo "============================================================"
echo "   Dashboard running at: $URL"
echo "   Press Ctrl+C to stop the server"
echo "============================================================"
echo ""
echo "Server logs:"
echo "------------"

# Try python3 first, then python
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m http.server $PORT
else
    echo "ERROR: Python not found. Please install Python 3."
    exit 1
fi
