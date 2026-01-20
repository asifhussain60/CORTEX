#!/usr/bin/env python3
"""
CORTEX Dashboard Launcher (Root Level)
======================================
Simple one-click launcher for the CORTEX Neural Observatory Dashboard.
Works on macOS, Windows, and Linux.

USAGE:
    # From project root
    python launch-dashboard.py
    
    # Or double-click this file (if Python is associated)
    
    # Or make executable (macOS/Linux)
    chmod +x launch-dashboard.py
    ./launch-dashboard.py

WHAT IT DOES:
1. Opens a new external terminal (not VS Code)
2. Starts FastAPI backend (port 8000)
3. Starts static frontend (port 8080)
4. Automatically kills orphaned processes
5. Shows you the dashboard URL

CROSS-PLATFORM:
- macOS: Terminal.app
- Windows: PowerShell (new console)
- Linux: gnome-terminal/konsole/xterm
"""
import os
import sys
import platform
import subprocess
from pathlib import Path


def get_platform() -> str:
    """Detect OS platform."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def main() -> int:
    """Launch dashboard in external terminal."""
    print("=" * 80)
    print("CORTEX NEURAL OBSERVATORY DASHBOARD LAUNCHER")
    print("=" * 80)
    print()
    
    # Get paths
    project_root = Path(__file__).parent.absolute()
    serve_script = project_root / "src" / "dashboard" / "serve-cortex-dashboard.py"
    
    # Verify script exists
    if not serve_script.exists():
        print(f"❌ Server script not found: {serve_script}")
        print()
        print("Expected location: src/dashboard/serve-cortex-dashboard.py")
        print("Please run from the CORTEX project root directory.")
        return 1
    
    # Build command
    python_exec = sys.executable
    command = f'cd "{project_root}" && "{python_exec}" "{serve_script}"'
    
    os_type = get_platform()
    
    print(f"🚀 Launching dashboard in external terminal...")
    print(f"   Platform: {os_type}")
    print(f"   Python: {python_exec}")
    print(f"   Server: {serve_script.name}")
    print()
    
    try:
        if os_type == "macos":
            # macOS: Launch in Terminal.app
            applescript = f'''
            tell application "Terminal"
                activate
                do script "{command}"
                set custom title of front window to "CORTEX Dashboard Server"
            end tell
            '''
            subprocess.Popen(['osascript', '-e', applescript])
            print("✅ Launched in Terminal.app")
            
        elif os_type == "windows":
            # Windows: Launch in PowerShell
            ps_command = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd \\"{project_root}\\"; & \\"{python_exec}\\" \\"{serve_script}\\"" -WindowStyle Normal'
            subprocess.Popen(['powershell', '-Command', ps_command], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("✅ Launched in PowerShell")
            
        else:  # Linux
            # Try common terminal emulators
            terminals = [
                (['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'], 'gnome-terminal'),
                (['konsole', '-e', 'bash', '-c', f'{command}; exec bash'], 'konsole'),
                (['xterm', '-e', f'bash -c "{command}; bash"'], 'xterm'),
            ]
            
            launched = False
            for terminal_cmd, terminal_name in terminals:
                try:
                    subprocess.Popen(terminal_cmd)
                    print(f"✅ Launched in {terminal_name}")
                    launched = True
                    break
                except FileNotFoundError:
                    continue
            
            if not launched:
                print("❌ No suitable terminal emulator found")
                print("   Install one of: gnome-terminal, konsole, xterm")
                print()
                print("   Or run directly:")
                print(f"   python {serve_script}")
                return 1
        
        print()
        print("=" * 80)
        print("DASHBOARD STARTING")
        print("=" * 80)
        print("⏱️  Please wait ~10 seconds for servers to start...")
        print()
        print("Check the external terminal window for:")
        print("  • 'Backend ready' message")
        print("  • 'Frontend ready' message")
        print("  • 'DASHBOARD READY' banner")
        print()
        print("Once ready, open your browser:")
        print("  🌐 Frontend: http://localhost:8080")
        print("  📡 Backend:  http://localhost:8000")
        print("  📚 API Docs: http://localhost:8000/docs")
        print()
        print("To stop: Close the terminal window or press Ctrl+C there")
        print("=" * 80)
        return 0
        
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        print()
        print("Try running directly:")
        print(f"   python {serve_script}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
