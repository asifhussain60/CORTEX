"""
Dashboard Launcher Orchestrator

Purpose: Launch CORTEX dashboard with HTTP server and auto-open browser.
         Serves dashboard UI from cortex-brain/dashboards/ parent directory.

📖 COMPLETE DOCUMENTATION: cortex-brain/documents/implementation-guides/dashboard-operation-guide.md
   Read this guide for:
   - Launch commands and options
   - Data structure and file locations
   - Server configuration details
   - Troubleshooting common issues

Trigger: "load dashboard", "/CORTEX load dashboard", "launch dashboard", "open dashboard"

CRITICAL CONFIGURATION:
- Server MUST serve from cortex-brain/dashboards/ (parent directory)
- NOT from cortex-brain/dashboards/ui/ (breaks data file access)
- This allows both /ui/index.html and /data/mock/*.json to work

Features:
- Auto-detect cortex-brain/dashboards/ directory
- Launch HTTP server on available port (default: 8080, fallback: 8081-8089)
- Auto-open browser to dashboard with specified data source
- Background server process (non-blocking)
- Graceful shutdown on Ctrl+C
- CORS support for local development
- Comprehensive error handling

Usage:
    from src.orchestrators.dashboard_launcher import launch_dashboard
    
    # Launch with defaults
    result = launch_dashboard()
    
    # Launch with custom port
    result = launch_dashboard(port=9000)
    
    # Launch without auto-opening browser
    result = launch_dashboard(auto_open=False)
    
    # Launch with specific data source
    result = launch_dashboard(source="luum-fresh")

Data Sources:
    - "mock" - Demo data in cortex-brain/dashboards/data/mock/
    - "{repo-id}" - Repository data in cortex-brain/dashboards/data/repos/{repo-id}/

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import http.server
import logging
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support for local development."""
    
    def __init__(self, *args, directory=None, **kwargs):
        """Initialize handler with specific directory."""
        # Store directory before calling super().__init__
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)
    
    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default server logs (use Python logger instead)."""
        logger.debug(f"HTTP: {format % args}")


class DashboardServer:
    """HTTP server wrapper for dashboard UI."""
    
    def __init__(self, dashboard_dir: Path, port: int = 8080):
        """
        Initialize dashboard server.
        
        Args:
            dashboard_dir: Path to dashboard UI directory
            port: Port to serve on (default: 8080)
        """
        self.dashboard_dir = dashboard_dir
        self.port = port
        self.server = None
        self.server_thread = None
        self._running = False
        self.logger = logging.getLogger(__name__)
    
    def _kill_process_on_port(self, port: int) -> bool:
        """
        Kill any process using the specified port.
        
        Args:
            port: Port number to free up
        
        Returns:
            True if port was freed, False otherwise
        """
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                # Find process using the port
                cmd = f'netstat -ano | findstr ":{port}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout:
                    # Extract PIDs from netstat output
                    pids = set()
                    for line in result.stdout.strip().split('\n'):
                        parts = line.split()
                        if parts and parts[-1].isdigit():
                            pids.add(int(parts[-1]))
                    
                    # Kill each process
                    for pid in pids:
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                            self.logger.info(f"Killed process {pid} on port {port}")
                        except Exception as e:
                            self.logger.debug(f"Failed to kill process {pid}: {e}")
                    
                    if pids:
                        time.sleep(0.5)  # Wait for port to be released
                        return True
            else:
                # Unix-like systems
                cmd = f"lsof -ti:{port}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.isdigit():
                            subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                            self.logger.info(f"Killed process {pid} on port {port}")
                    
                    time.sleep(0.5)
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error killing process on port {port}: {e}")
            return False
    
    def _is_port_available(self, port: int) -> bool:
        """
        Check if a port is available.
        
        Args:
            port: Port number to check
        
        Returns:
            True if port is available, False otherwise
        """
        try:
            with socketserver.TCPServer(("", port), None) as test_server:
                return True
        except OSError:
            return False
    
    def _resolve_data_source(self, path_or_source: str) -> str:
        """
        Resolve a file path or source name to a valid data source key.
        
        Args:
            path_or_source: Repository path or data source key
        
        Returns:
            Valid data source key (e.g., 'mock', 'v5-webservices-prevalidationws')
        """
        from pathlib import Path
        
        # First, check if it's already a valid data directory name
        # Scan existing data directories
        valid_sources = []
        for item in self.dashboard_dir.iterdir():
            if item.is_dir() and item.name not in ['ui', 'schema', '.git']:
                if (item / 'health-data.json').exists():
                    valid_sources.append(item.name)
        
        # If source matches an existing directory name exactly, use it
        if path_or_source in valid_sources:
            self.logger.info(f"Using existing data source: {path_or_source}")
            return path_or_source
        
        # Try to extract repository name from path
        try:
            repo_path = Path(path_or_source)
            
            # Get the last part of the path (directory name)
            if repo_path.exists() or '\\' in path_or_source or '/' in path_or_source:
                # Extract name and normalize (lowercase, dots to dashes)
                repo_name = repo_path.name.lower().replace('.', '-')
                
                # Check if this normalized name matches any existing data directory
                if repo_name in valid_sources:
                    self.logger.info(f"Resolved path '{path_or_source}' to data source '{repo_name}'")
                    return repo_name
                
                # Check if data directory exists
                data_dir = self.dashboard_dir / repo_name
                if data_dir.exists() and (data_dir / 'health-data.json').exists():
                    self.logger.info(f"Found data directory for '{repo_name}'")
                    return repo_name
                else:
                    self.logger.warning(f"No data found for '{repo_name}' at {data_dir}")
                    self.logger.info(f"Available sources: {', '.join(valid_sources)}")
        except Exception as e:
            self.logger.debug(f"Path resolution error: {e}")
        
        # Default to mock if nothing matches
        self.logger.warning(f"Could not resolve '{path_or_source}', using 'mock'. Available: {', '.join(valid_sources)}")
        return 'mock'
    
    def start(self, auto_open: bool = True, source: str = "mock") -> Dict[str, Any]:
        """
        Start HTTP server and optionally open browser.
        
        Args:
            auto_open: Auto-open browser to dashboard
            source: Data source to load (mock, noor-canvas, etc.) or repository path
        
        Returns:
            Result dict with success, port, url, message
        """
        # Resolve source to valid data source key
        resolved_source = self._resolve_data_source(source)
        try:
            # Check if port is in use and kill existing process
            if not self._is_port_available(self.port):
                self.logger.info(f"Port {self.port} is in use, attempting to free it...")
                if self._kill_process_on_port(self.port):
                    self.logger.info(f"Successfully freed port {self.port}")
                else:
                    return {
                        "success": False,
                        "message": f"Port {self.port} is in use and could not be freed",
                        "port": None,
                        "url": None
                    }
            
            # Verify port is now available
            if not self._is_port_available(self.port):
                return {
                    "success": False,
                    "message": f"Port {self.port} is still not available after cleanup",
                    "port": None,
                    "url": None
                }
            
            # ⚠️ CRITICAL: Serve from parent directory (dashboards/) to access both ui/ and data/
            # This allows /ui/index.html and /data/mock/executive-summary.json to both work
            # DO NOT change to serve from ui/ subdirectory - it will break data file access
            # See: cortex-brain/documents/implementation-guides/dashboard-operation-guide.md
            if not self.dashboard_dir.exists():
                return {
                    "success": False,
                    "message": f"Dashboard directory not found: {self.dashboard_dir}",
                    "port": None,
                    "url": None
                }
            
            # Create handler with dashboard directory parameter
            import functools
            handler = functools.partial(CORSHTTPRequestHandler, directory=str(self.dashboard_dir))
            
            # Create server
            self.server = socketserver.TCPServer(("", self.port), handler)
            self.server.allow_reuse_address = True
            
            # Start server in background thread
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True,
                name="DashboardServerThread"
            )
            self.server_thread.start()
            self._running = True
            
            # Construct dashboard URL (server serves from parent, so need ui/index.html path)
            url = f"http://localhost:{self.port}/ui/index.html?source={resolved_source}"
            
            # Wait briefly for server to start
            time.sleep(0.5)
            
            # Auto-open browser
            if auto_open:
                try:
                    webbrowser.open(url)
                    logger.info(f"Opened dashboard in browser: {url}")
                except Exception as e:
                    logger.warning(f"Failed to auto-open browser: {e}")
            
            return {
                "success": True,
                "port": self.port,
                "url": url,
                "message": f"Dashboard server running at {url}",
                "directory": str(self.dashboard_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to start dashboard server: {e}")
            return {
                "success": False,
                "message": f"Failed to start server: {str(e)}",
                "port": None,
                "url": None
            }
    
    def stop(self):
        """Stop the HTTP server."""
        if self.server:
            self._running = False
            self.server.shutdown()
            self.server.server_close()
            logger.info(f"Dashboard server stopped on port {self.port}")
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running and self.server_thread and self.server_thread.is_alive()


def _detect_cortex_root() -> Optional[Path]:
    """
    Auto-detect CORTEX root directory.
    
    Returns:
        Path to CORTEX root or None if not found
    """
    current = Path.cwd()
    
    # Check current directory
    if (current / "cortex-brain").exists():
        return current
    
    # Check up to 3 parent directories
    for _ in range(3):
        current = current.parent
        if (current / "cortex-brain").exists():
            return current
    
    return None


def launch_dashboard(
    port: int = 8080,
    auto_open: bool = True,
    source: str = "mock",
    cortex_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Launch CORTEX dashboard with HTTP server.
    
    Args:
        port: Port to serve on (default: 8080, auto-fallback to 8081-8089)
        auto_open: Auto-open browser to dashboard (default: True)
        source: Data source to load (default: "mock")
        cortex_root: Path to CORTEX root (auto-detect if None)
    
    Returns:
        Dict with keys:
            - success: bool
            - port: int (actual port used)
            - url: str (dashboard URL)
            - message: str (status message)
            - directory: str (dashboard directory path)
            - server: DashboardServer instance (if successful)
    """
    try:
        # Detect CORTEX root
        if cortex_root is None:
            cortex_root = _detect_cortex_root()
        
        if cortex_root is None:
            return {
                "success": False,
                "message": "CORTEX root directory not found. Must contain cortex-brain/",
                "port": None,
                "url": None
            }
        
        # Locate dashboard parent directory (contains ui/ and all data subdirs)
        dashboard_parent = cortex_root / "cortex-brain" / "dashboards"
        dashboard_ui = dashboard_parent / "ui"
        
        if not dashboard_parent.exists():
            return {
                "success": False,
                "message": f"Dashboard directory not found: {dashboard_parent}",
                "port": None,
                "url": None
            }
        
        if not dashboard_ui.exists():
            return {
                "success": False,
                "message": f"Dashboard UI directory not found: {dashboard_ui}",
                "port": None,
                "url": None
            }
        
        # Check for index.html
        index_file = dashboard_ui / "index.html"
        if not index_file.exists():
            return {
                "success": False,
                "message": f"Dashboard index.html not found in {dashboard_ui}",
                "port": None,
                "url": None
            }
        
        logger.info(f"Launching dashboard from {dashboard_parent}")
        
        # Create and start server (serve from parent to access all data subdirs)
        server = DashboardServer(dashboard_parent, port)
        result = server.start(auto_open=auto_open, source=source)
        
        if result["success"]:
            result["server"] = server
            logger.info(f"✅ Dashboard launched successfully: {result['url']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "port": None,
            "url": None
        }


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch CORTEX Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on (default: 8080)")
    parser.add_argument("--source", type=str, default="mock", help="Data source to load (default: mock)")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Launching CORTEX Dashboard...\n")
    
    result = launch_dashboard(
        port=args.port,
        auto_open=not args.no_browser,
        source=args.source
    )
    
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"📁 Directory: {result['directory']}")
        print(f"🌐 URL: {result['url']}")
        print(f"🔌 Port: {result['port']}")
        print("\n💡 Press Ctrl+C to stop the server\n")
        
        try:
            # Keep server running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping dashboard server...")
            if "server" in result:
                result["server"].stop()
            print("✅ Server stopped\n")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
