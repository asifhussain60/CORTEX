#!/bin/bash
# CORTEX Documentation Server Launcher
# Quick start script for local documentation testing
# Automatically kills existing servers to ensure latest changes are picked up

cd "$(dirname "$0")/.."

PORT=8000

echo "🚀 Launching CORTEX Documentation Server..."
echo ""

# Check if port is already in use
if lsof -ti:$PORT >/dev/null 2>&1; then
    echo "🔄 Port $PORT is already in use - killing existing server..."
    EXISTING_PIDS=$(lsof -ti:$PORT)
    
    for PID in $EXISTING_PIDS; do
        echo "   Killing process $PID..."
        kill -9 $PID 2>/dev/null
    done
    
    # Wait for port to be fully released (increased wait time)
    echo "   Waiting for port to be released..."
    sleep 3
    
    # Double-check port is free
    RETRY_COUNT=0
    while lsof -ti:$PORT >/dev/null 2>&1 && [ $RETRY_COUNT -lt 5 ]; do
        echo "   Port still in use, waiting..."
        sleep 1
        RETRY_COUNT=$((RETRY_COUNT + 1))
    done
    
    if lsof -ti:$PORT >/dev/null 2>&1; then
        echo "❌ Failed to release port $PORT after killing processes"
        echo "💡 Please manually kill: lsof -ti:$PORT | xargs kill -9"
        exit 1
    fi
    
    echo "✅ Existing server stopped, port released"
    echo ""
fi

echo "🆕 Starting fresh server on port $PORT..."

# Start server in background
python3 scripts/serve_docs.py $PORT &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Verify server started successfully
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "❌ Failed to start server"
    exit 1
fi

# Open browser
echo "🌐 Opening browser..."
if command -v open &> /dev/null; then
    open "http://localhost:$PORT/"
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:$PORT/"
else
    echo "⚠️  Could not auto-open browser. Please visit manually."
fi

echo ""
echo "✅ Server running (PID: $SERVER_PID)"
echo "📖 Documentation: http://localhost:$PORT/"
echo "📚 Story Viewer:  http://localhost:$PORT/story/viewer.html"
echo ""
echo "⏹️  To stop: Press Ctrl+C or run: kill $SERVER_PID"
echo ""

# Wait for Ctrl+C
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo '🛑 Server stopped'; exit 0" INT

# Keep script running
wait $SERVER_PID
