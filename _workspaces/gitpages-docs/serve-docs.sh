#!/bin/bash
# ============================================================================
# CORTEX GitPages Local Server (macOS/Linux)
# One-click: Kill existing → Start HTTP server → Open browser
#
# Port: 8080 (HTTP)
# Target: index.html in current directory
# ============================================================================

set -e
cd "$(dirname "$0")"

echo ""
echo "======================================================================="
echo "  CORTEX Documentation Server"
echo "  Platform: $(uname -s)"
echo "  Port: 8080"
echo "======================================================================="
echo ""

# Kill any existing HTTP processes on port 8080
echo "[1/4] Stopping existing server on port 8080..."
if lsof -ti:8080 >/dev/null 2>&1; then
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    echo "  ✓ Stopped existing process"
    sleep 1
else
    echo "  ✓ No existing server running"
fi

# Check for Python (needed for http.server)
echo "[2/4] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "  ✗ ERROR: Python 3 not found in PATH"
    echo "  Please install Python 3 or add to PATH"
    exit 1
fi
echo "  ✓ Python 3 OK"

# Start HTTP server
echo "[3/4] Starting HTTP server..."
echo "  URL: http://localhost:8080"
python3 -m http.server 8080 >/dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Verify server started
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "  ✗ ERROR: Failed to start server"
    exit 1
fi
echo "  ✓ Server started (PID: $SERVER_PID)"

# Open default browser
echo "[4/4] Opening browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:8080
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:8080 2>/dev/null || echo "  ℹ Open http://localhost:8080 manually"
else
    echo "  ℹ Open http://localhost:8080 manually"
fi
echo "  ✓ Browser launched"

echo ""
echo "======================================================================="
echo "  Server running at http://localhost:8080"
echo "  Press Ctrl+C to stop (PID: $SERVER_PID)"
echo "======================================================================="
echo ""

# Keep script running and handle Ctrl+C
trap "echo ''; echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null; echo 'Server stopped'; exit 0" INT TERM

# Wait for server process
wait $SERVER_PID 2>/dev/null
