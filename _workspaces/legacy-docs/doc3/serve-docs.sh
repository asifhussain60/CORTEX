#!/bin/bash

################################################################################
# CORTEX Documentation Server (Mac/Linux)
# One-click: Kill existing → Start server → Open browser
# Serves static HTML on port 8080
#
# Usage: 
#   chmod +x serve-docs.sh
#   ./serve-docs.sh
################################################################################

set -e

PORT=8080

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located (docs/)
DOCS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "========================================"
echo -e "${BLUE}   🧠 CORTEX Documentation Server${NC}"
echo "   Platform: $(uname -s)"
echo "========================================"
echo ""

# Detect Python executable
PYTHON_EXE=""
if command -v python3 &> /dev/null; then
    PYTHON_EXE="python3"
elif command -v python &> /dev/null; then
    PYTHON_EXE="python"
else
    echo -e "${RED}ERROR: Python not found${NC}"
    echo "Please install Python 3.x"
    exit 1
fi

echo "[1/3] Checking port $PORT..."

# Kill any existing process on port 8080
PIDS=$(lsof -ti:$PORT 2>/dev/null || true)
if [ ! -z "$PIDS" ]; then
    echo -e "${YELLOW}   Found existing process(es) on port $PORT${NC}"
    echo "$PIDS" | xargs kill -9 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}   ✅ Port cleared${NC}"
else
    echo -e "${GREEN}   ✅ Port $PORT available${NC}"
fi

# Start HTTP server in background
echo "[2/3] Starting HTTP server..."
cd "$DOCS_DIR"
nohup "$PYTHON_EXE" -m http.server $PORT > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Verify server is running
if lsof -i:$PORT > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Server running (PID: $SERVER_PID)${NC}"
    echo "   📂 Serving: $DOCS_DIR"
    
    # Open browser
    echo "[3/3] Opening browser..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "http://localhost:$PORT/index.html"
        echo -e "${GREEN}   ✅ Browser opened${NC}"
    elif command -v xdg-open &> /dev/null; then
        # Linux with xdg-open
        xdg-open "http://localhost:$PORT/index.html" 2>/dev/null &
        echo -e "${GREEN}   ✅ Browser opened${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Please open manually: http://localhost:$PORT/index.html${NC}"
    fi
    
    echo ""
    echo "========================================"
    echo -e "${GREEN}   🌐 Server: http://localhost:$PORT/index.html${NC}"
    echo -e "${BLUE}   ℹ️  To stop: kill $SERVER_PID${NC}"
    echo "========================================"
    echo ""
else
    echo -e "${RED}   ❌ Failed to start server${NC}"
    exit 1
fi
