#!/usr/bin/env python3
"""
CORTEX Neural Observatory Dashboard Server
===========================================
AC-DO-004-01: Dashboard Server with Process Management

FEATURES:
- Serves FastAPI backend (port 8000) + Static frontend (port 8080)
- Detects and kills orphaned HTTP processes on same ports
- Launches in external terminal (not VS Code integrated)
- Cross-platform support (macOS, Windows, Linux)
- Health checks and auto-recovery
- Graceful shutdown with cleanup

ARCHITECTURE:
- FastAPI Backend: http://localhost:8000/api/*
- Static Frontend: http://localhost:8080 (serves index.html)
- WebSocket Stream: ws://localhost:8000/ws/audit

USAGE:
    # From project root
    python src/dashboard/serve.py
    
    # Or make executable
    chmod +x src/dashboard/serve.py
    ./src/dashboard/serve.py

GOVERNANCE:
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- CORE-026: Checkpoint protocol (manual git commit)
"""
import os
import sys
import platform
import subprocess
import time
import signal
import atexit
from pathlib import Path
from typing import Optional, List, Tuple
import socket
import psutil  # type: ignore


# =============================================================================
# CONFIGURATION
# =============================================================================

BACKEND_PORT = 8000
FRONTEND_PORT = 8080
BACKEND_HOST = "127.0.0.1"
FRONTEND_HOST = "127.0.0.1"

# Detect project root (3 levels up from this file)
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DASHBOARD_DIR = SCRIPT_DIR
FRONTEND_DIR = DASHBOARD_DIR / "frontend"
API_DIR = DASHBOARD_DIR / "api"

# Process tracking
BACKEND_PROCESS: Optional[subprocess.Popen] = None
FRONTEND_PROCESS: Optional[subprocess.Popen] = None


# =============================================================================
# UTILITIES
# =============================================================================

def get_platform() -> str:
    """
    Detect current operating system.
    
    Returns:
        str: 'windows', 'macos', or 'linux'
    """
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def find_processes_on_port(port: int) -> List[psutil.Process]:
    """
    Find all processes listening on specified port.
    
    Args:
        port: Port number to check
        
    Returns:
        List of psutil.Process objects using the port
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            connections = proc.connections(kind='inet')
            for conn in connections:
                if conn.status == 'LISTEN' and conn.laddr.port == port:
                    processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


def kill_orphaned_processes(port: int) -> int:
    """
    Kill all processes listening on specified port.
    
    Args:
        port: Port number to clean up
        
    Returns:
        Number of processes killed
    """
    processes = find_processes_on_port(port)
    killed = 0
    
    for proc in processes:
        try:
            print(f"ΓÜá∩╕Å  Killing orphaned process PID {proc.pid} ({proc.name()}) on port {port}")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                proc.kill()  # Force kill if not responding
            killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"ΓÜá∩╕Å  Could not kill PID {proc.pid}: {e}")
    
    return killed


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """
    Check if port is available for binding.
    
    Args:
        port: Port number to check
        host: Host address to check
        
    Returns:
        True if port is available, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def wait_for_port(port: int, host: str = "127.0.0.1", timeout: int = 10) -> bool:
    """
    Wait for port to become available (server started).
    
    Args:
        port: Port number to check
        host: Host address to check
        timeout: Maximum seconds to wait
        
    Returns:
        True if port is listening, False if timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, port))
                return True
            except (socket.error, ConnectionRefusedError):
                time.sleep(0.5)
    return False


def get_python_executable() -> str:
    """
    Get the correct Python executable path.
    
    Returns:
        Path to Python executable (respects virtual environments)
    """
    return sys.executable


def open_in_external_terminal(command: str, title: str = "CORTEX Dashboard") -> bool:
    """
    Launch command in external terminal window (not VS Code integrated).
    
    Args:
        command: Shell command to execute
        title: Window title for terminal
        
    Returns:
        True if successfully launched, False otherwise
    """
    os_type = get_platform()
    
    try:
        if os_type == "macos":
            # macOS: Use osascript to launch Terminal.app
            applescript = f'''
            tell application "Terminal"
                activate
                do script "{command}"
                set custom title of front window to "{title}"
            end tell
            '''
            subprocess.Popen(['osascript', '-e', applescript])
            return True
            
        elif os_type == "windows":
            # Windows: Use PowerShell in new window
            ps_command = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "{command}" -WindowStyle Normal'
            subprocess.Popen(['powershell', '-Command', ps_command], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            return True
            
        else:  # Linux
            # Try common terminal emulators
            terminals = [
                ['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'],
                ['konsole', '-e', 'bash', '-c', f'{command}; exec bash'],
                ['xterm', '-e', f'{command}; bash'],
            ]
            
            for terminal_cmd in terminals:
                try:
                    subprocess.Popen(terminal_cmd)
                    return True
                except FileNotFoundError:
                    continue
            
            print("Γ¥î No suitable terminal emulator found on Linux")
            return False
            
    except Exception as e:
        print(f"Γ¥î Failed to launch external terminal: {e}")
        return False


# =============================================================================
# SERVER MANAGEMENT
# =============================================================================

def start_backend_server() -> Tuple[bool, Optional[subprocess.Popen]]:
    """
    Start FastAPI backend server on port 8000.
    
    Returns:
        Tuple of (success: bool, process: Optional[Popen])
    """
    global BACKEND_PROCESS
    
    print(f"≡ƒÜÇ Starting FastAPI backend on http://{BACKEND_HOST}:{BACKEND_PORT}")
    
    # Kill orphaned processes
    killed = kill_orphaned_processes(BACKEND_PORT)
    if killed:
        print(f"   Cleaned up {killed} orphaned process(es)")
        time.sleep(1)  # Wait for port cleanup
    
    # Verify port is available
    if not is_port_available(BACKEND_PORT, BACKEND_HOST):
        print(f"Γ¥î Port {BACKEND_PORT} still in use after cleanup")
        return False, None
    
    # Start uvicorn server
    python_exec = get_python_executable()
    api_main = API_DIR / "main.py"
    
    cmd = [
        python_exec, "-m", "uvicorn",
        "src.dashboard.api.main:app",
        "--host", BACKEND_HOST,
        "--port", str(BACKEND_PORT),
        "--reload",
        "--log-level", "info"
    ]
    
    try:
        BACKEND_PROCESS = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait for server to start
        if wait_for_port(BACKEND_PORT, BACKEND_HOST, timeout=10):
            print(f"Γ£à Backend ready: http://{BACKEND_HOST}:{BACKEND_PORT}")
            print(f"   API Docs: http://{BACKEND_HOST}:{BACKEND_PORT}/docs")
            return True, BACKEND_PROCESS
        else:
            print("Γ¥î Backend failed to start within 10 seconds")
            if BACKEND_PROCESS:
                BACKEND_PROCESS.terminate()
            return False, None
            
    except Exception as e:
        print(f"Γ¥î Failed to start backend: {e}")
        return False, None


def start_frontend_server() -> Tuple[bool, Optional[subprocess.Popen]]:
    """
    Start static file server for frontend on port 8080.
    
    Returns:
        Tuple of (success: bool, process: Optional[Popen])
    """
    global FRONTEND_PROCESS
    
    print(f"≡ƒÜÇ Starting static frontend on http://{FRONTEND_HOST}:{FRONTEND_PORT}")
    
    # Kill orphaned processes
    killed = kill_orphaned_processes(FRONTEND_PORT)
    if killed:
        print(f"   Cleaned up {killed} orphaned process(es)")
        time.sleep(1)
    
    # Verify port is available
    if not is_port_available(FRONTEND_PORT, FRONTEND_HOST):
        print(f"Γ¥î Port {FRONTEND_PORT} still in use after cleanup")
        return False, None
    
    # Start Python's built-in HTTP server
    python_exec = get_python_executable()
    
    cmd = [
        python_exec, "-m", "http.server",
        str(FRONTEND_PORT),
        "--bind", FRONTEND_HOST,
        "--directory", str(FRONTEND_DIR)
    ]
    
    try:
        FRONTEND_PROCESS = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait for server to start
        if wait_for_port(FRONTEND_PORT, FRONTEND_HOST, timeout=10):
            print(f"Γ£à Frontend ready: http://{FRONTEND_HOST}:{FRONTEND_PORT}")
            return True, FRONTEND_PROCESS
        else:
            print("Γ¥î Frontend failed to start within 10 seconds")
            if FRONTEND_PROCESS:
                FRONTEND_PROCESS.terminate()
            return False, None
            
    except Exception as e:
        print(f"Γ¥î Failed to start frontend: {e}")
        return False, None


def cleanup_servers() -> None:
    """
    Gracefully shutdown both servers.
    """
    global BACKEND_PROCESS, FRONTEND_PROCESS
    
    print("\n≡ƒ¢æ Shutting down servers...")
    
    for name, process in [("Backend", BACKEND_PROCESS), ("Frontend", FRONTEND_PROCESS)]:
        if process and process.poll() is None:
            print(f"   Stopping {name} (PID {process.pid})")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"   Force killing {name}")
                process.kill()
    
    print("Γ£à Cleanup complete")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main() -> int:
    """
    Main entry point for dashboard server.
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("=" * 80)
    print("CORTEX NEURAL OBSERVATORY DASHBOARD SERVER")
    print("=" * 80)
    print(f"Platform: {get_platform()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Dashboard Dir: {DASHBOARD_DIR}")
    print()
    
    # Verify directories exist
    if not FRONTEND_DIR.exists():
        print(f"Γ¥î Frontend directory not found: {FRONTEND_DIR}")
        return 1
    
    if not API_DIR.exists():
        print(f"Γ¥î API directory not found: {API_DIR}")
        return 1
    
    # Register cleanup handler
    atexit.register(cleanup_servers)
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    
    # Start backend
    backend_success, backend_proc = start_backend_server()
    if not backend_success:
        return 1
    
    print()
    
    # Start frontend
    frontend_success, frontend_proc = start_frontend_server()
    if not frontend_success:
        cleanup_servers()
        return 1
    
    print()
    print("=" * 80)
    print("≡ƒÄë DASHBOARD READY")
    print("=" * 80)
    print(f"Frontend: http://{FRONTEND_HOST}:{FRONTEND_PORT}")
    print(f"Backend:  http://{BACKEND_HOST}:{BACKEND_PORT}")
    print(f"API Docs: http://{BACKEND_HOST}:{BACKEND_PORT}/docs")
    print(f"WebSocket: ws://{BACKEND_HOST}:{BACKEND_PORT}/ws/audit")
    print()
    print("Press Ctrl+C to stop servers")
    print("=" * 80)
    print()
    
    # Monitor processes
    try:
        while True:
            time.sleep(5)
            
            # Check if processes are still running
            if backend_proc and backend_proc.poll() is not None:
                print("Γ¥î Backend process died unexpectedly")
                break
            
            if frontend_proc and frontend_proc.poll() is not None:
                print("Γ¥î Frontend process died unexpectedly")
                break
            
    except KeyboardInterrupt:
        print("\nΓÜá∩╕Å  Received interrupt signal")
    
    cleanup_servers()
    return 0


if __name__ == "__main__":
    sys.exit(main())
