#!/usr/bin/env python3
"""
CORTEX Documentation Server
Serves docs folder via HTTP for local development and testing.
Usage: python3 serve_docs.py [port]
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Default port
PORT = 8000 if len(sys.argv) < 2 else int(sys.argv[1])

# Change to docs directory
DOCS_DIR = Path(__file__).parent.parent / "docs"
os.chdir(DOCS_DIR)

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers for local development"""
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format with color"""
        print(f"📄 {args[0]} - {args[1]}")

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 CORTEX Documentation Server")
    print("=" * 70)
    print(f"📁 Serving: {DOCS_DIR}")
    print(f"🌐 URLs:")
    print(f"   Main Site:  http://localhost:{PORT}/")
    print(f"   Story:      http://localhost:{PORT}/story/viewer.html")
    print(f"   SKULL:      http://localhost:{PORT}/governance/skull-rulebook.html")
    print("=" * 70)
    print(f"✅ Server running on port {PORT}")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    try:
        with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {PORT} is already in use")
            print(f"💡 Try a different port: python3 serve_docs.py 8001")
        else:
            print(f"\n❌ Error: {e}")
        sys.exit(1)
