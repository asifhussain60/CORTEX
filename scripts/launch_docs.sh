#!/bin/bash
# CORTEX Documentation Server Launcher
# Quick start script for local documentation testing

cd "$(dirname "$0")/.."

echo "🚀 Launching CORTEX Documentation Server..."
echo ""

# Start server in background
python3 scripts/serve_docs.py 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Open browser
echo "🌐 Opening browser..."
open "http://localhost:8000/"

echo ""
echo "✅ Server running (PID: $SERVER_PID)"
echo "📖 Documentation: http://localhost:8000/"
echo "📚 Story Viewer:  http://localhost:8000/story/viewer.html"
echo ""
echo "⏹️  To stop: Press Ctrl+C or run: kill $SERVER_PID"
echo ""

# Wait for Ctrl+C
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo '🛑 Server stopped'; exit 0" INT

# Keep script running
wait $SERVER_PID
