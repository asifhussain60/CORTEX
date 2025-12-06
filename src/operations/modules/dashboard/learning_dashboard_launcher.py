"""
Learning Dashboard Launcher

Launches HTTP server to serve learning documentation via Docsify.
Separate from metrics dashboard, serves generated learning documents.

Features:
- Port auto-fallback (8080-8089)
- Auto-open browser
- CORS enabled
- Serves cortex-brain/documents/learning/ directory
"""

import http.server
import socketserver
import webbrowser
import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers enabled."""
    
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
        """Suppress default logging to avoid clutter."""
        pass


class LearningDashboardLauncher:
    """
    Launches learning documentation dashboard with Docsify.
    
    Features:
    - Port auto-fallback (8080-8089)
    - Auto-open browser
    - CORS enabled
    - Document serving
    """
    
    DEFAULT_PORTS = range(8080, 8090)  # 8080-8089
    
    def __init__(self, dashboard_dir: Optional[Path] = None):
        """
        Initialize dashboard launcher.
        
        Args:
            dashboard_dir: Path to dashboard directory (default: cortex-brain/dashboards/learning/)
        """
        if dashboard_dir is None:
            dashboard_dir = Path(__file__).parent.parent.parent.parent.parent / "cortex-brain" / "dashboards" / "learning"
        
        self.dashboard_dir = Path(dashboard_dir)
        self.server: Optional[socketserver.TCPServer] = None
        self.port: Optional[int] = None
    
    def find_available_port(self) -> Optional[int]:
        """
        Find first available port in range 8080-8089.
        
        Returns:
            Available port number or None if all busy
        """
        for port in self.DEFAULT_PORTS:
            try:
                # Try to bind to port
                with socketserver.TCPServer(("", port), None) as test_server:
                    return port
            except OSError:
                continue
        
        return None
    
    def launch(self, auto_open: bool = True) -> bool:
        """
        Launch learning dashboard server.
        
        Args:
            auto_open: Whether to auto-open browser
            
        Returns:
            True if launched successfully, False otherwise
        """
        # Verify dashboard directory exists
        if not self.dashboard_dir.exists():
            logger.error(f"Dashboard directory not found: {self.dashboard_dir}")
            return False
        
        # Find available port
        self.port = self.find_available_port()
        if self.port is None:
            logger.error("No available ports in range 8080-8089")
            return False
        
        try:
            # Change to dashboard directory
            import os
            original_dir = os.getcwd()
            os.chdir(self.dashboard_dir)
            
            # Create server
            self.server = socketserver.TCPServer(("", self.port), CORSHTTPRequestHandler)
            
            url = f"http://localhost:{self.port}"
            logger.info(f"Learning dashboard launched at {url}")
            print(f"\n🎓 Learning Dashboard: {url}")
            print(f"📁 Serving: {self.dashboard_dir}")
            print(f"🔍 Full-text search enabled")
            print(f"📂 Browse 15 learning categories")
            print(f"\nPress Ctrl+C to stop server\n")
            
            # Auto-open browser
            if auto_open:
                time.sleep(1)  # Brief delay for server to start
                webbrowser.open(url)
            
            # Serve forever
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            logger.info("Learning dashboard stopped by user")
            self.stop()
            os.chdir(original_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to launch learning dashboard: {e}")
            if self.server:
                self.stop()
            os.chdir(original_dir)
            return False
    
    def stop(self):
        """Stop the dashboard server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            logger.info("Learning dashboard stopped")
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self.server is not None


def launch_learning_dashboard(auto_open: bool = True) -> bool:
    """
    Convenience function to launch learning dashboard.
    
    Args:
        auto_open: Whether to auto-open browser
        
    Returns:
        True if launched successfully
    """
    launcher = LearningDashboardLauncher()
    return launcher.launch(auto_open=auto_open)


if __name__ == "__main__":
    # Direct execution
    import sys
    
    auto_open = "--no-browser" not in sys.argv
    
    print("🎓 CORTEX Learning Dashboard Launcher")
    print("=" * 50)
    
    success = launch_learning_dashboard(auto_open=auto_open)
    sys.exit(0 if success else 1)
