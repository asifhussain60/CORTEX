#!/usr/bin/env python3
"""
Plan Viewer Server Launcher
Auto-launches HTTP server and opens browser for plan-viewer.html
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
    
    # Check if we're in plan root
    if (current / 'plan-viewer.html').exists():
        return current
    
    # Check if script is in plan directory
    script_dir = Path(__file__).parent
    if (script_dir / 'plan-viewer.html').exists():
        return script_dir
    
    # Search parent directories
    for parent in current.parents:
        if (parent / 'plan-viewer.html').exists():
            return parent
    
    return None


def find_project_root(plan_root):
    """Find CORTEX project root (where HTTP server should run from)"""
    current = plan_root
    
    # Look for .git directory (project root indicator)
    for _ in range(10):  # Max 10 levels up
        if (current / '.git').exists():
            return current
        if current.parent == current:  # Reached filesystem root
            break
        current = current.parent
    
    return None


def main():
    """Launch HTTP server and open plan viewer in browser"""
    print("🚀 CORTEX Plan Viewer Launcher")
    print("=" * 50)
    
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
        viewer_url = f"http://localhost:8000/{rel_path}/plan-viewer.html"
    except ValueError:
        print(f"❌ Error: Plan directory not under project root")
        return 1
    
    print(f"🌐 Viewer URL: {viewer_url}")
    print()
    
    # Check if server is already running
    try:
        import urllib.request
        urllib.request.urlopen('http://localhost:8000', timeout=1)
        server_running = True
        print("✅ HTTP server already running on port 8000")
    except:
        server_running = False
    
    # Start HTTP server if not running
    if not server_running:
        print("🔧 Starting HTTP server on port 8000...")
        try:
            subprocess.Popen(
                [sys.executable, "-m", "http.server", "8000"],
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ HTTP server started")
            
            # Wait for server to start
            print("⏳ Waiting for server startup...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Failed to start HTTP server: {e}")
            return 1
    
    # Open browser
    print("🌐 Opening browser...")
    try:
        webbrowser.open(viewer_url)
        print("✅ Plan viewer opened in browser")
        print()
        print("📊 Real-time progress tracking enabled (30s refresh)")
        print("🛑 To stop server: Press Ctrl+C in terminal where server is running")
        return 0
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"   Please manually open: {viewer_url}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
