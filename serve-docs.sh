#!/bin/bash

################################################################################
# CORTEX MkDocs Server Launcher (Mac/Linux)
# One-click: Kill existing → Start server → Open browser
#
# Usage: 
#   chmod +x serve-docs.sh
#   ./serve-docs.sh
#
# For Windows: Use serve-docs.bat instead
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo ""
echo "========================================"
echo -e "${BLUE}   CORTEX Documentation Server${NC}"
echo "   Platform: $(uname -s)"
echo "========================================"
echo ""

# Detect Python executable
PYTHON_EXE=""
if [ -f ".venv/bin/python" ]; then
    PYTHON_EXE=".venv/bin/python"
elif [ -f ".venv/bin/python3" ]; then
    PYTHON_EXE=".venv/bin/python3"
elif command -v python3 &> /dev/null; then
    PYTHON_EXE="python3"
elif command -v python &> /dev/null; then
    PYTHON_EXE="python"
else
    echo -e "${RED}ERROR: Python not found${NC}"
    echo "Please install Python 3.8+ or activate virtual environment"
    exit 1
fi

echo "[1/4] Stopping existing server on port 8000..."

# Mac: Check if port is in use and kill process
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    PIDS=$(lsof -i :8000 -t 2>/dev/null || true)
    if [ ! -z "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        echo "   Stopped existing process(es)"
    fi
else
    # Linux
    PIDS=$(lsof -i :8000 -t 2>/dev/null || true)
    if [ ! -z "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null || true
        echo "   Stopped existing process(es)"
    fi
fi

sleep 1

# Check and install dependencies
echo "[2/4] Checking dependencies..."
if ! "$PYTHON_EXE" -m pip show mkdocs &>/dev/null; then
    echo "   Installing mkdocs and material theme..."
    "$PYTHON_EXE" -m pip install mkdocs mkdocs-material >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}   FAILED to install mkdocs${NC}"
        echo "   Please run: pip install mkdocs mkdocs-material"
        exit 1
    fi
fi
echo -e "${GREEN}   Dependencies OK${NC}"

# Start mkdocs serve
echo "[3/4] Starting MkDocs server..."
"$PYTHON_EXE" -m mkdocs serve --dev-addr 127.0.0.1:8000 &
MKDOCS_PID=$!

# Wait for server to start
sleep 3

# Open browser
echo "[4/4] Opening browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://127.0.0.1:8000/INDEX/"
elif command -v xdg-open &> /dev/null; then
    # Linux with xdg-open
    xdg-open "http://127.0.0.1:8000/INDEX/" 2>/dev/null &
elif command -v gnome-open &> /dev/null; then
    # Linux with gnome-open
    gnome-open "http://127.0.0.1:8000/INDEX/" 2>/dev/null &
else
    echo "   Skipping browser open (no browser launcher found)"
    echo "   Visit: http://127.0.0.1:8000/INDEX/"
fi

echo ""
echo "========================================"
echo -e "${GREEN}   Server running at http://127.0.0.1:8000${NC}"
echo "   Press Ctrl+C to stop"
echo "========================================"
echo ""

# Keep the script running and display server output
wait $MKDOCS_PID 2>/dev/null || true

echo ""
echo -e "${BLUE}   Server stopped${NC}"
echo ""
