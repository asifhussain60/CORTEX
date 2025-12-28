#!/bin/bash
# CORTEX Documentation Server Launcher - Simplified
# Kills all HTTP servers on common ports, then launches CORTEX docs on port 8000

cd "$(dirname "$0")/.."

PORT=8000
COMMON_PORTS="8000 8001 8080 3000 5000 4200 9000"

echo "🚀 Launching CORTEX 4.0 Documentation Server..."
echo ""

# Kill ALL servers on common HTTP ports
echo "� Killing all HTTP servers on ports: $COMMON_PORTS"
for PORT_TO_KILL in $COMMON_PORTS; do
    if lsof -ti:$PORT_TO_KILL >/dev/null 2>&1; then
        echo "   ✗ Killing processes on port $PORT_TO_KILL..."
        lsof -ti:$PORT_TO_KILL | xargs kill -9 2>/dev/null
    fi
done

# Wait for all ports to be released
echo "   ⏳ Waiting for ports to be released..."
sleep 2

echo "✅ All servers killed"
echo ""
echo "🆕 Starting CORTEX 4.0 server on port $PORT..."

# Start server in background
python3 scripts/serve_docs.py $PORT &
SERVER_PID=$!

# Wait for server to start
sleep 1

# Verify server started successfully
if ! ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "❌ Failed to start server"
    exit 1
fi

echo "✅ Server started (PID: $SERVER_PID)"
echo ""
echo "📖 Main Site:  http://localhost:$PORT/"
echo "📚 Story:      http://localhost:$PORT/story/viewer.html"
echo "🛡️  SKULL:      http://localhost:$PORT/governance/skull-rulebook.html"
echo ""
echo "⏹️  To stop: Press Ctrl+C or run: kill $SERVER_PID"
echo ""

# Open browser (optional - comment out if not needed)
if command -v open &> /dev/null; then
    open "http://localhost:$PORT/" 2>/dev/null &
fi

# Wait for Ctrl+C
trap "kill $SERVER_PID 2>/dev/null; echo ''; echo '🛑 Server stopped'; exit 0" INT

# Keep script running
wait $SERVER_PID
