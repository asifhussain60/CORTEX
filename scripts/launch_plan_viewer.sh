#!/bin/bash
# CORTEX Plan Viewer Launcher
# Kills any process on port 8000 and launches plan viewer server

cd "$(dirname "$0")/.."

PORT=8000
PLAN_VIEWER="cortex-brain/documents/planning/active/C50-cortex-v5-remediation/plan-viewer.html"

echo "🎯 CORTEX Plan Viewer Launcher"
echo "=================================="
echo ""

# Kill any process on port 8000
echo "🔪 Checking port $PORT..."
if lsof -ti:$PORT >/dev/null 2>&1; then
    echo "   ✗ Killing process on port $PORT..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 2
    echo "   ✅ Port cleared"
else
    echo "   ✓ Port is free"
fi

echo ""
echo "🚀 Starting plan viewer server on port $PORT..."

# Start server in background
python3 scripts/serve_plan_viewer.py $PORT &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to initialize..."
sleep 2

# Verify server is running
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "❌ Failed to start server"
    exit 1
fi

echo "✅ Server started (PID: $SERVER_PID)"
echo ""
echo "🎯 Plan Viewer: http://localhost:$PORT/$PLAN_VIEWER"
echo ""

# Open browser (after server is confirmed running)
if command -v open &> /dev/null; then
    # macOS
    echo "🌐 Opening browser..."
    open "http://localhost:$PORT/$PLAN_VIEWER" 2>/dev/null
elif command -v xdg-open &> /dev/null; then
    # Linux
    echo "🌐 Opening browser..."
    xdg-open "http://localhost:$PORT/$PLAN_VIEWER" 2>/dev/null
elif command -v start &> /dev/null; then
    # Windows
    echo "🌐 Opening browser..."
    start "http://localhost:$PORT/$PLAN_VIEWER" 2>/dev/null
fi

echo ""
echo "📊 Auto-refresh: 10 seconds"
echo "⏹️  To stop: fg (then Ctrl+C) or kill $SERVER_PID"
echo ""
echo "=================================="

# Keep script running to show server logs
wait $SERVER_PID
