#!/bin/bash
# CORTEX Plan Viewer Launcher
# Quick launch script for this plan's viewer
# Author: Asif Hussain

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/../../../../../templates/plan-viewer/plan-viewer-server.py"

echo "🚀 Launching CORTEX Plan Viewer..."
python3 "$SERVER_SCRIPT" --plan-dir "$SCRIPT_DIR"
