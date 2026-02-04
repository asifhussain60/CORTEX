#!/usr/bin/env python3
"""
Simple HTTP Server for CORTEX Dashboard
Serves the dashboard SPA without requiring complex API setup
"""
import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# Get paths
SCRIPT_DIR = Path(__file__).parent.absolute()
DASHBOARD_DIR = SCRIPT_DIR.parent  # Parent of backend = dashboard root
FRONTEND_DIR = DASHBOARD_DIR / "frontend" / "public"

class CORTEXDashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for dashboard SPA"""
    
    def do_GET(self):
        """Handle GET requests with SPA routing"""
        # Default to index.html for SPA
        if self.path == "/" or not self.path.startswith("/"):
            self.path = "/index.html"
        
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def end_headers(self):
        """Add CORS headers"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        SimpleHTTPRequestHandler.end_headers(self)

def start_server(port=8000, host="127.0.0.1"):
    """Start the HTTP server"""
    # Change to frontend directory
    os.chdir(FRONTEND_DIR)
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, CORTEXDashboardHandler)
    
    print(f"")
    print(f"╔════════════════════════════════════════════════════════════════╗")
    print(f"║        CORTEX Dashboard - SPA HTTP Server                      ║")
    print(f"╚════════════════════════════════════════════════════════════════╝")
    print(f"")
    print(f"✅ Frontend Directory: {FRONTEND_DIR}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📊 Dashboard: http://{host}:{port}/index.html")
    print(f"🔗 LENS Dashboard: http://{host}:{port}/lens-dashboard.html")
    print(f"")
    print(f"⏸️  Press Ctrl+C to stop the server")
    print(f"")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n✅ Server stopped")
        sys.exit(0)

if __name__ == "__main__":
    # Verify frontend directory exists
    if not FRONTEND_DIR.exists():
        print(f"❌ Error: Frontend directory not found: {FRONTEND_DIR}")
        sys.exit(1)
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_server(port=port)
