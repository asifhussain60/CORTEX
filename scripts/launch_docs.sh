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
sleep 1

# Verify server is running
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "❌ Failed to start server"
    exit 1
fi

echo "✅ Server started (PID: $SERVER_PID)"
echo ""
echo "📖 http://localhost:$PORT/"
echo ""
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Open browser (last step)
if command -v open &> /dev/null; then
    echo "🌐 Opening browser..."
    open "http://localhost:$PORT/" 2>/dev/null
fi

# Handle Ctrl+C
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo '🛑 Server stopped'; exit 0" INT

# Keep running
wait $SERVER_PID
