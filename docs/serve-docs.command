#!/bin/bash
# ============================================
# CORTEX GitPages Local Server (macOS)
# Double-click to run — .command files open
# in Terminal.app automatically on macOS.
#
# Port: 8000 (HTTP)
# Target: index.html in the same directory
# ============================================

# cd to the directory containing this script
# (works regardless of where you double-click from)
cd "$(dirname "$0")"

echo ""
echo "========================================"
echo "  CORTEX Documentation Server"
echo "  Platform: macOS"
echo "  Port: 8000"
echo "========================================"
echo ""

# [1/3] Kill any existing process on port 8000
echo "[1/3] Stopping existing server on port 8000..."
EXISTING_PID=$(lsof -ti tcp:8000 2>/dev/null)
if [ -n "$EXISTING_PID" ]; then
    kill -9 $EXISTING_PID 2>/dev/null
    echo "  Stopped PID $EXISTING_PID"
    sleep 1
else
    echo "  No existing server found"
fi

# [2/3] Check Python
echo "[2/3] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo "  ERROR: python3 not found in PATH"
    echo "  Install via: brew install python or https://python.org"
    read -p "Press Enter to close..."
    exit 1
fi
echo "  Python OK ($(python3 --version))"

# [3/3] Start server
echo "[3/3] Starting HTTP server..."
echo ""
echo "========================================"
echo "  SERVER RUNNING"
echo ""
echo "  URL: http://localhost:8000"
echo "  Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Open browser after a short delay (background)
(sleep 1 && open "http://localhost:8000") &

# Run server in foreground (Ctrl+C to stop)
python3 -m http.server 8000
