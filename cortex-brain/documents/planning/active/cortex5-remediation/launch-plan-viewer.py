#!/usr/bin/env python3
"""
CORTEX v5 Remediation Epic - Plan Viewer Launcher
Automatically launches HTTP server and opens plan viewer in browser.

Usage:
    python3 launch-plan-viewer.py [--port PORT]

Author: Asif Hussain
Created: January 5, 2026
"""

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def find_available_port(start_port=8000, end_port=8010):
    """Find an available port in the specified range."""
    import socket
    
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"No available ports found in range {start_port}-{end_port}")


def launch_server(port):
    """Launch HTTP server in background."""
    epic_dir = Path(__file__).parent
    
    print(f"🚀 Starting HTTP server on port {port}...")
    print(f"📁 Serving from: {epic_dir}")
    
    try:
        # Start server in background (non-blocking)
        process = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port)],
            cwd=epic_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(1)
        
        # Check if server started successfully
        if process.poll() is None:
            print(f"✅ Server running at: http://localhost:{port}")
            return process
        else:
            stderr = process.stderr.read().decode()
            raise RuntimeError(f"Server failed to start: {stderr}")
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


def open_browser(port):
    """Open plan viewer in default browser."""
    url = f"http://localhost:{port}/plan-viewer.html"
    
    print(f"🌐 Opening browser: {url}")
    
    try:
        webbrowser.open(url)
        print("✅ Browser opened")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"📌 Please open manually: {url}")


def main():
    parser = argparse.ArgumentParser(
        description="Launch CORTEX v5 Remediation Epic plan viewer"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to use (default: auto-detect from 8000-8010)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧠 CORTEX v5.0 Remediation Epic - Plan Viewer Launcher")
    print("=" * 60)
    print()
    
    # Determine port
    if args.port:
        port = args.port
    else:
        try:
            port = find_available_port()
            print(f"🔍 Auto-detected available port: {port}")
        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)
    
    # Launch server
    server_process = launch_server(port)
    
    # Open browser (unless disabled)
    if not args.no_browser:
        time.sleep(0.5)  # Brief delay
        open_browser(port)
    else:
        print(f"📌 View plan at: http://localhost:{port}/plan-viewer.html")
    
    print()
    print("=" * 60)
    print("✅ PLAN VIEWER RUNNING")
    print("=" * 60)
    print()
    print("📊 Features:")
    print("  • Auto-refresh every 5 seconds")
    print("  • Real-time progress tracking")
    print("  • Task list visualization")
    print("  • Phase dependency graph")
    print()
    print("🛑 To stop: Press Ctrl+C in this terminal")
    print("=" * 60)
    print()
    
    try:
        # Keep script running (server in background)
        server_process.wait()
    except KeyboardInterrupt:
        print()
        print("🛑 Shutting down server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")


if __name__ == "__main__":
    main()
