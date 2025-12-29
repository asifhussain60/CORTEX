#!/bin/bash
# CORTEX 4.0 Documentation Server
# Kills any process on port 8000 and launches fresh server

cd "$(dirname "$0")/.."

PORT=8000

echo "🚀 CORTEX 4.0 Documentation Server"
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
echo "🚀 Starting server on port $PORT..."

# Start server in background
python3 scripts/serve_docs.py $PORT &
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
echo "📖 Documentation: http://localhost:$PORT/"
echo ""

# Open browser (after server is confirmed running)
if command -v open &> /dev/null; then
    # macOS
    echo "🌐 Opening browser..."
    open "http://localhost:$PORT/" 2>/dev/null
elif command -v xdg-open &> /dev/null; then
    # Linux
    echo "🌐 Opening browser..."
    xdg-open "http://localhost:$PORT/" 2>/dev/null &
elif command -v start &> /dev/null; then
    # Windows (Git Bash)
    echo "🌐 Opening browser..."
    start "http://localhost:$PORT/" 2>/dev/null
fi

echo ""
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Handle Ctrl+C
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo '🛑 Server stopped'; exit 0" INT

# Keep running
wait $SERVER_PID
