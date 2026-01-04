#!/usr/bin/env python3
"""
CORTEX Plan Viewer Server
Serves the entire CORTEX directory with CORS support for plan-viewer.html
Usage: python3 serve_plan_viewer.py [port]
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Default port
PORT = 8000 if len(sys.argv) < 2 else int(sys.argv[1])

# Change to CORTEX root directory
CORTEX_ROOT = Path(__file__).parent.parent
os.chdir(CORTEX_ROOT)

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
        path = args[0].split()[1] if len(args) > 0 and ' ' in args[0] else args[0]
        status = args[1]
        
        # Highlight JSON file requests
        if '.json' in path:
            print(f"📊 {status} - {path}")
        elif 'plan-viewer.html' in path:
            print(f"🎯 {status} - {path}")
        else:
            print(f"📄 {status} - {path}")

if __name__ == "__main__":
    plan_viewer_path = "cortex-brain/documents/planning/active/C50-cortex-v5-remediation/plan-viewer.html"
    
    print("=" * 80)
    print("🎯 CORTEX Plan Viewer Server")
    print("=" * 80)
    print(f"📁 Serving: {CORTEX_ROOT}")
    print(f"🌐 Plan Viewer URL:")
    print(f"   http://localhost:{PORT}/{plan_viewer_path}")
    print(f"\n📊 Data sources (auto-loaded by viewer):")
    print(f"   - tracking/epic-progress-tracker.json")
    print(f"   - tracking/child-plan-registry.json")
    print("=" * 80)
    print(f"✅ Server running on port {PORT}")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 80)
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
            print(f"💡 Run: lsof -ti:{PORT} | xargs kill -9")
        else:
            print(f"\n❌ Error: {e}")
        sys.exit(1)
