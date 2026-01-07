#!/usr/bin/env python3
"""
C50 Epic Plan Viewer Server Launcher
Automatically launches HTTP server and opens browser for plan-viewer.html
Non-blocking execution for seamless workflow continuation
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

def find_epic_root():
    """Find the C50 epic root directory"""
    current = Path.cwd()
    
    # Check if we're already in epic root
    if (current / 'plan-viewer.html').exists():
        return current
    
    # Check if we're in a child plan folder
    if current.name.startswith('C50-'):
        return current.parent
    
    # Search for C50 epic folder
    for search_dir in [current, current.parent, current.parent.parent]:
        c50_dir = search_dir / 'C50-cortex-v5-remediation'
        if c50_dir.exists() and (c50_dir / 'plan-viewer.html').exists():
            return c50_dir
    
    return None

def find_project_root(epic_root):
    """Find the CORTEX project root (where server should run from)"""
    # Navigate up from epic_root to find CORTEX project root
    # Expected: CORTEX/cortex-brain/documents/planning/active/C50-cortex-v5-remediation/
    
    current = epic_root
    
    # Go up 5 levels: C50 -> active -> planning -> documents -> cortex-brain -> CORTEX
    for _ in range(5):
        current = current.parent
        if current.name == 'CORTEX':
            return current
    
    # Fallback: Look for .git directory
    current = epic_root
    for _ in range(10):  # Max 10 levels up
        if (current / '.git').exists():
            return current
        if current.parent == current:  # Reached root
            break
        current = current.parent
    
    return None

def find_free_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    
    return None

def is_server_running(port):
    """Check if server is already running on port"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def launch_server_background(project_root, port):
    """Launch HTTP server in background (non-blocking)"""
    
    # Server MUST run from project root for correct relative paths
    # DO NOT change to epic_root - paths in HTML are relative to project root
    
    # Launch server in background
    if sys.platform == 'darwin':  # macOS
        # Use osascript to launch in new Terminal window
        script = f'''
tell application "Terminal"
    do script "cd '{project_root}' && python3 -m http.server {port}"
    activate
end tell
'''
        subprocess.Popen(['osascript', '-e', script])
    
    elif sys.platform == 'win32':  # Windows
        # Launch in new cmd window
        subprocess.Popen(
            f'start cmd /k "cd /d {project_root} && python -m http.server {port}"',
            shell=True
        )
    
    else:  # Linux
        # Launch in background with nohup
        subprocess.Popen(
            f'cd {project_root} && nohup python3 -m http.server {port} > /dev/null 2>&1 &',
            shell=True
        )
    
    # Wait for server to start
    for i in range(10):
        time.sleep(0.5)
        if is_server_running(port):
            return True
    
    return False

def open_plan_viewer(epic_root, project_root, port):
    """Open plan viewer in browser"""
    
    # Construct URL relative to project root
    plan_viewer_relative = epic_root.relative_to(project_root)
    url = f"http://localhost:{port}/{plan_viewer_relative}/plan-viewer.html"
    
    print(f"🌐 Opening: {url}")
    
    # Open in browser
    webbrowser.open(url)
    
    return url

def main():
    print("=" * 60)
    print("C50 EPIC PLAN VIEWER LAUNCHER")
    print("=" * 60)
    
    # Find epic root
    epic_root = find_epic_root()
    
    if not epic_root:
        print("❌ Error: Could not find C50 epic root directory")
        print("   Expected: plan-viewer.html in current or parent directory")
        sys.exit(1)
    
    print(f"📁 Epic Root: {epic_root}")
    
    # Find project root
    project_root = find_project_root(epic_root)
    
    if not project_root:
        print("❌ Error: Could not find CORTEX project root")
        print("   Expected: CORTEX/.git directory")
        sys.exit(1)
    
    print(f"📁 Project Root: {project_root}")
    
    # Check if plan-viewer.html exists
    plan_viewer = epic_root / 'plan-viewer.html'
    if not plan_viewer.exists():
        print(f"❌ Error: plan-viewer.html not found")
        print(f"   Expected: {plan_viewer}")
        sys.exit(1)
    
    print("✅ Found plan-viewer.html")
    
    # Find available port
    port = find_free_port()
    
    if not port:
        print("❌ Error: Could not find available port (tried 8000-8010)")
        sys.exit(1)
    
    print(f"🔌 Using port: {port}")
    
    # Check if server already running
    if is_server_running(port):
        print(f"⚡ Server already running on port {port}")
        url = open_plan_viewer(epic_root, project_root, port)
        print(f"\n✅ Plan viewer opened: {url}")
        print("   Server continues running in background")
        return
    
    # Launch server
    print(f"🚀 Launching server from project root...")
    
    if launch_server_background(project_root, port):
        print(f"✅ Server started on port {port}")
        
        # Open plan viewer
        url = open_plan_viewer(epic_root, project_root, port)
        
        print(f"\n" + "=" * 60)
        print("✅ PLAN VIEWER LAUNCHED")
        print("=" * 60)
        print(f"📊 URL: {url}")
        print(f"🖥️  Server: Running from {project_root.name}/")
        print(f"⏹️  Stop: Close the server terminal window")
        print("\n💡 You can continue working - server runs independently")
        print("=" * 60)
    
    else:
        print("❌ Error: Failed to start server")
        print("   Try manually: python3 -m http.server 8000")
        sys.exit(1)

if __name__ == '__main__':
    main()
