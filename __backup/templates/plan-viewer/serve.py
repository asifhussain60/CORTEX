#!/usr/bin/env python3
"""
CORTEX 6.0 Plan Viewer HTTP Server
Simple development server for viewing the plan-viewer with hot reload
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8090
DIRECTORY = Path(__file__).parent

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support"""
    
    def end_headers(self):
        # Enable CORS for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Colorful logging
        message = format % args
        if '200' in message:
            print(f"\033[92m✓\033[0m {message}")
        elif '404' in message:
            print(f"\033[93m⚠\033[0m {message}")
        else:
            print(f"\033[94mℹ\033[0m {message}")

def main():
    """Start the HTTP server"""
    os.chdir(DIRECTORY)
    
    handler = CORSHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("\n" + "="*60)
        print("🚀 CORTEX 6.0 Plan Viewer Server")
        print("="*60)
        print(f"\n📡 Server running at: \033[96mhttp://localhost:{PORT}\033[0m")
        print(f"📂 Serving directory: {DIRECTORY}")
        print(f"\n🔗 Open in browser:")
        print(f"   Main Dashboard: \033[96mhttp://localhost:{PORT}/cortex-plan-viewer.html\033[0m")
        print(f"   Phase 1 Detail: \033[96mhttp://localhost:{PORT}/phase-detail-viewer.html?phase=1\033[0m")
        print(f"\n⌨️  Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n\033[93m✋ Shutting down server...\033[0m")
            httpd.shutdown()
            print("\033[92m✓ Server stopped successfully\033[0m\n")
            sys.exit(0)

if __name__ == "__main__":
    main()
