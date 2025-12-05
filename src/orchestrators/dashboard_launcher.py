"""
Dashboard Launcher Orchestrator

Purpose: Launch CORTEX dashboard with HTTP server and auto-open browser.
         Serves dashboard UI from cortex-brain/dashboards/ui/ directory.

Trigger: "load dashboard", "/CORTEX load dashboard", "launch dashboard", "open dashboard"

Features:
- Auto-detect cortex-brain/dashboards/ui/ directory
- Launch HTTP server on available port (default: 8080, fallback: 8081-8089)
- Auto-open browser to dashboard with mock data source
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
    
    def _find_available_port(self, start_port: int = 8080, max_attempts: int = 10) -> Optional[int]:
        """
        Find an available port starting from start_port.
        
        Args:
            start_port: Port to start searching from
            max_attempts: Maximum number of ports to try
        
        Returns:
            Available port number or None if none found
        """
        for port in range(start_port, start_port + max_attempts):
            try:
                with socketserver.TCPServer(("", port), None) as test_server:
                    return port
            except OSError:
                continue
        return None
    
    def start(self, auto_open: bool = True, source: str = "mock") -> Dict[str, Any]:
        """
        Start HTTP server and optionally open browser.
        
        Args:
            auto_open: Auto-open browser to dashboard
            source: Data source to load (mock, noor-canvas, etc.)
        
        Returns:
            Result dict with success, port, url, message
        """
        try:
            # Change to dashboard directory
            import os
            original_dir = os.getcwd()
            os.chdir(str(self.dashboard_dir))
            
            # Find available port
            available_port = self._find_available_port(self.port)
            if available_port is None:
                return {
                    "success": False,
                    "message": f"No available ports found in range {self.port}-{self.port + 9}",
                    "port": None,
                    "url": None
                }
            
            self.port = available_port
            
            # Create server
            self.server = socketserver.TCPServer(("", self.port), CORSHTTPRequestHandler)
            self.server.allow_reuse_address = True
            
            # Start server in background thread
            self.server_thread = threading.Thread(
                target=self.server.serve_forever,
                daemon=True,
                name="DashboardServerThread"
            )
            self.server_thread.start()
            self._running = True
            
            # Construct dashboard URL (index.html is in ui/ subdirectory)
            url = f"http://localhost:{self.port}/ui/index.html?source={source}"
            
            # Wait briefly for server to start
            time.sleep(0.5)
            
            # Auto-open browser
            if auto_open:
                try:
                    webbrowser.open(url)
                    logger.info(f"Opened dashboard in browser: {url}")
                except Exception as e:
                    logger.warning(f"Failed to auto-open browser: {e}")
            
            # Restore original directory
            os.chdir(original_dir)
            
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
