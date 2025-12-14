"""
CORTEX Enterprise Documentation - Local Preview Server
Serves the GitHub Pages site locally for testing before deployment

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path
import sys

# Configuration
PORT = 8000
DIRECTORY = Path(__file__).parent / "docs" / "gh-pages"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    """Start local preview server"""
    if not DIRECTORY.exists():
        print(f"❌ ERROR: Documentation directory not found at {DIRECTORY}")
        print(f"   Please ensure the GitHub Pages site has been generated.")
        sys.exit(1)
    
    print("="*80)
    print("🚀 CORTEX Enterprise Documentation - Local Preview Server")
    print("="*80)
    print(f"📁 Serving: {DIRECTORY}")
    print(f"🌐 URL: http://localhost:{PORT}")
    print(f"")
    print(f"Opening browser in 2 seconds...")
    print(f"Press Ctrl+C to stop the server")
    print("="*80)
    
    # Start server
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        # Open browser
        import time
        time.sleep(2)
        webbrowser.open(f"http://localhost:{PORT}")
        
        # Serve forever
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Server stopped")
            sys.exit(0)

if __name__ == "__main__":
    main()
