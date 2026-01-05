#!/usr/bin/env python3
"""
CORTEX Plan Viewer Launcher - Enterprise Audit Logger
Auto-launches HTTP server and opens browser for plan-viewer.html

Author: Asif Hussain
Version: 1.0.0
Created: January 5, 2026
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def find_plan_root():
    """Find plan root directory containing plan-viewer.html"""
    current = Path.cwd()
    
    # Check current directory
    if (current / "plan-viewer.html").exists():
        return current
    
    # Check if we're in a subdirectory
    for parent in current.parents:
        if (parent / "plan-viewer.html").exists():
            return parent
    
    return None


def find_project_root(plan_root):
    """Find CORTEX project root (where HTTP server should run from)"""
    current = plan_root
    
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent
    
    return None


def main():
    """Launch HTTP server and open plan viewer in browser"""
    print("🚀 CORTEX Plan Viewer Launcher")
    print("=" * 60)
    
    # Find plan root
    plan_root = find_plan_root()
    if not plan_root:
        print("❌ Error: Cannot find plan-viewer.html")
        print("   Make sure you're in the plan directory or a subdirectory")
        return 1
    
    print(f"📁 Plan root: {plan_root}")
    
    # Find project root
    project_root = find_project_root(plan_root)
    if not project_root:
        print("❌ Error: Cannot find CORTEX project root (.git directory)")
        print("   HTTP server needs to run from project root")
        return 1
    
    print(f"🏠 Project root: {project_root}")
    
    # Construct relative path from project root to plan viewer
    try:
        rel_path = plan_root.relative_to(project_root)
        viewer_url_path = rel_path / "plan-viewer.html"
    except ValueError:
        print("❌ Error: Plan root is not within project root")
        return 1
    
    # Port for plan viewers (CORTEX standard)
    port = 8150
    
    # Check if server already running
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"✅ Server already running on port {port}")
            url = f"http://localhost:{port}/{viewer_url_path}"
            print(f"\n🌐 Opening browser: {url}")
            webbrowser.open(url)
            return 0
    except:
        pass
    
    # Start HTTP server
    print(f"\n🚀 Starting HTTP server on port {port}...")
    print(f"   Server root: {project_root}")
    
    try:
        server_process = subprocess.Popen(
            ["python3", "-m", "http.server", str(port)],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(2)
        
        # Check if server started successfully
        if server_process.poll() is not None:
            print("❌ Error: Server failed to start")
            stdout, stderr = server_process.communicate()
            if stderr:
                print(f"   {stderr.decode()}")
            return 1
        
        print(f"✅ Server started successfully (PID: {server_process.pid})")
        
        # Open browser
        url = f"http://localhost:{port}/{viewer_url_path}"
        print(f"\n🌐 Opening browser: {url}")
        webbrowser.open(url)
        
        print("\n" + "=" * 60)
        print("📊 Plan Viewer Status:")
        print(f"   URL: {url}")
        print(f"   Server PID: {server_process.pid}")
        print("\n💡 Tips:")
        print("   - Leave this terminal open to keep server running")
        print("   - Press Ctrl+C to stop the server")
        print("   - Viewer auto-refreshes every 30 seconds")
        print("=" * 60)
        
        # Keep script running
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error launching server: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
