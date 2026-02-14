#!/bin/bash
# CORTEX Master Dashboard Launcher
# Automatically starts HTTP server and opens dashboard in browser

DASHBOARD_DIR="/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/dashboard"
PORT=8893

echo "🚀 CORTEX Master Dashboard Launcher"
echo "===================================="
echo ""

# Check if server is already running
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Server already running on port $PORT"
else
    echo "🔧 Starting HTTP server..."
    cd "$DASHBOARD_DIR" && python3 -m http.server $PORT > /tmp/cortex-dashboard.log 2>&1 &
    SERVER_PID=$!
    echo "✅ Server started (PID: $SERVER_PID)"
    sleep 2
fi

echo ""
echo "📊 Dashboard URL: http://localhost:$PORT/index.html"
echo "📦 JSON Data URL: http://localhost:$PORT/data/plan-summary.json"
echo ""
echo "Opening dashboard in browser..."
open "http://localhost:$PORT/index.html"

echo ""
echo "✅ Dashboard opened!"
echo ""
echo "📋 Expected values:"
echo "   • Progress: 95%"
echo "   • Active phases: 1"
echo "   • Completed phases: 19"
echo ""
echo "🔍 Check browser console for: '✅ Dashboard data loaded from plan-summary.json'"
echo ""
echo "To stop server: pkill -f 'python3 -m http.server $PORT'"
echo "To view logs: tail -f /tmp/cortex-dashboard.log"
