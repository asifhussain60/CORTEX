#!/usr/bin/env python3
"""
CORTEX Dashboard External Launcher
===================================
AC-DO-004-02: External Terminal Launcher

Launches the dashboard server in an EXTERNAL terminal window (not VS Code).
This prevents the server from being killed when VS Code prompts are triggered.

USAGE:
    python src/dashboard/launch.py

    # Or make executable (macOS/Linux)
    chmod +x src/dashboard/launch.py
    ./src/dashboard/launch.py

CROSS-PLATFORM:
- macOS: Opens in Terminal.app
- Windows: Opens in PowerShell (new console)
- Linux: Opens in gnome-terminal/konsole/xterm
"""
import os
import platform
import subprocess
import sys
from pathlib import Path


def get_platform() -> str:
    """Get OS platform."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def launch_external_terminal() -> bool:
    """
    Launch dashboard server in external terminal.

    Returns:
        True if successfully launched, False otherwise
    """
    # Get paths
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent
    serve_script = script_dir / "serve-cortex-dashboard.py"

    # Build command
    python_exec = sys.executable
    command = f'cd "{project_root}" && "{python_exec}" "{serve_script}"'

    os_type = get_platform()

    print("🚀 Launching CORTEX Dashboard in external terminal...")
    print(f"   Platform: {os_type}")
    print(f"   Script: {serve_script}")
    print()

    try:
        if os_type == "macos":
            # macOS: Use Terminal.app
            applescript = f'''
            tell application "Terminal"
                activate
                do script "{command}"
                set custom title of front window to "CORTEX Dashboard Server"
            end tell
            '''
            subprocess.Popen(['osascript', '-e', applescript])
            print("✅ Launched in Terminal.app")
            print("   Check Terminal for server status")
            return True

        elif os_type == "windows":
            # Windows: Use PowerShell in new window
            ps_command = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd \\"{project_root}\\"; & \\"{python_exec}\\" \\"{serve_script}\\"" -WindowStyle Normal'
            subprocess.Popen(['powershell', '-Command', ps_command],
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("✅ Launched in PowerShell")
            print("   Check PowerShell window for server status")
            return True

        else:  # Linux
            # Try common terminal emulators
            terminals = [
                (['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'], 'gnome-terminal'),
                (['konsole', '-e', 'bash', '-c', f'{command}; exec bash'], 'konsole'),
                (['xterm', '-e', f'bash -c "{command}; bash"'], 'xterm'),
            ]

            for terminal_cmd, terminal_name in terminals:
                try:
                    subprocess.Popen(terminal_cmd)
                    print(f"✅ Launched in {terminal_name}")
                    print(f"   Check {terminal_name} window for server status")
                    return True
                except FileNotFoundError:
                    continue

            print("❌ No suitable terminal emulator found")
            print("   Install one of: gnome-terminal, konsole, xterm")
            return False

    except Exception as e:
        print(f"❌ Failed to launch external terminal: {e}")
        return False


def main() -> int:
    """Main entry point."""
    print("=" * 80)
    print("CORTEX NEURAL OBSERVATORY - EXTERNAL LAUNCHER")
    print("=" * 80)
    print()

    success = launch_external_terminal()

    if success:
        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Check the external terminal window for server status")
        print("2. Wait for 'DASHBOARD READY' message (~10 seconds)")
        print("3. Open browser: http://localhost:8080")
        print("4. API docs: http://localhost:8000/docs")
        print()
        print("To stop: Close the external terminal window or press Ctrl+C there")
        print("=" * 80)
        return 0
    else:
        print()
        print("❌ Launch failed. Try running directly:")
        print(f"   python {Path(__file__).parent / 'serve-cortex-dashboard.py'}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
