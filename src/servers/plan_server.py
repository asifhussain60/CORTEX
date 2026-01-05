"""
CORTEX Plan Server - Live HTML Plan Viewer
Serves plan-viewer.html on localhost:8150 with real-time updates

Features:
- Single port (8150) for all plans
- Check/reuse/kill existing servers
- Real-time progress updates via JSON API
- CORS enabled for local development
- Daemon thread (runs in background)
"""

import http.server
import socketserver
import json
import threading
import time
import signal
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

try:
    import psutil
except ImportError:
    print("⚠️  psutil not installed - port management disabled")
    psutil = None

PLAN_SERVER_PORT = 8150


class PlanRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for plan viewer with CORS and live updates."""
    
    plan_folder: Optional[Path] = None
    
    def log_message(self, format: str, *args) -> None:
        """Suppress request logging to avoid terminal clutter."""
        pass  # Silent operation
    
    def do_GET(self):
        """Handle GET requests with CORS headers and API endpoints."""
        
        # API endpoints
        if self.path == '/api/plan':
            self.serve_plan()
            return
        elif self.path == '/api/progress':
            self.serve_progress()
            return
        elif self.path == '/api/health':
            self.serve_health()
            return
        
        # Static files (HTML, CSS, JS)
        try:
            if self.path == '/':
                self.path = '/plan-viewer.html'
            
            # Serve file with CORS headers
            self.send_response(200)
            
            if self.path.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif self.path.endswith('.json'):
                self.send_header('Content-type', 'application/json')
            elif self.path.endswith('.yaml'):
                self.send_header('Content-type', 'text/yaml')
            else:
                self.send_header('Content-type', 'text/plain')
            
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            # Read and serve file
            file_path = Path.cwd() / self.path.lstrip('/')
            if file_path.exists():
                self.wfile.write(file_path.read_bytes())
            else:
                self.wfile.write(b'File not found')
                
        except Exception as e:
            self.send_error(500, f"Error serving file: {e}")
    
    def serve_plan(self):
        """Serve plan definition from master-plan.yaml as JSON."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        if not self.plan_folder:
            self.wfile.write(json.dumps({"error": "No plan loaded"}).encode())
            return
        
        try:
            # Find master plan YAML (pattern: [A-Z0-9]{3}-*.yaml)
            yaml_files = list(self.plan_folder.glob("[A-Z0-9][A-Z0-9][A-Z0-9]-*.yaml"))
            
            if yaml_files:
                with open(yaml_files[0], 'r') as f:
                    plan_data = yaml.safe_load(f)
                self.wfile.write(json.dumps(plan_data, indent=2).encode())
            else:
                # Fallback: create minimal plan structure
                self.wfile.write(json.dumps({
                    "plan": {
                        "id": "N/A",
                        "title": "Plan Not Found",
                        "phases": []
                    }
                }).encode())
                
        except Exception as e:
            self.wfile.write(json.dumps({"error": f"Failed to load plan: {e}"}).encode())
    
    def serve_progress(self):
        """Serve current progress from progress-tracker.json."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        if not self.plan_folder:
            self.wfile.write(json.dumps({"error": "No plan loaded"}).encode())
            return
        
        try:
            tracker_path = self.plan_folder / "tracking" / "progress-tracker.json"
            if tracker_path.exists():
                self.wfile.write(tracker_path.read_bytes())
            else:
                # Default progress structure
                self.wfile.write(json.dumps({
                    "progress": {
                        "overall_percent": 0,
                        "current_phase": 1,
                        "total_phases": 0
                    }
                }).encode())
        except Exception as e:
            self.wfile.write(json.dumps({"error": f"Failed to load progress: {e}"}).encode())
    
    def serve_health(self):
        """Health check endpoint."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps({
            "status": "healthy",
            "port": PLAN_SERVER_PORT,
            "plan_folder": str(self.plan_folder) if self.plan_folder else None
        }).encode())


class PlanServer:
    """Manages plan viewer server lifecycle with port management."""
    
    def __init__(self, plan_folder: Path, port: int = PLAN_SERVER_PORT):
        self.plan_folder = plan_folder
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None
    
    @staticmethod
    def check_port_in_use(port: int) -> bool:
        """Check if port is already in use."""
        if not psutil:
            return False
        
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
        except (psutil.AccessDenied, AttributeError):
            pass
        
        return False
    
    @staticmethod
    def kill_server_on_port(port: int) -> bool:
        """Kill any process using the port."""
        if not psutil:
            print("⚠️  Cannot kill server - psutil not available")
            return False
        
        killed = False
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port and conn.status == 'LISTEN':
                            print(f"🔪 Killing process {proc.pid} ({proc.name()}) on port {port}")
                            proc.send_signal(signal.SIGTERM)
                            time.sleep(0.5)
                            if proc.is_running():
                                proc.kill()
                            killed = True
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠️  Error killing server: {e}")
        
        return killed
    
    def start(self) -> str:
        """Start plan server, reusing or killing existing server."""
        
        # Check if server already running on this port
        if self.check_port_in_use(self.port):
            print(f"⚠️  Port {self.port} in use - attempting to kill existing server...")
            if self.kill_server_on_port(self.port):
                print(f"✅ Killed existing server on port {self.port}")
                time.sleep(1)  # Wait for port to be released
            else:
                print(f"⚠️  Could not kill server - may still be accessible")
        
        # Change to plan folder for serving static files
        original_cwd = Path.cwd()
        try:
            os.chdir(self.plan_folder)
            
            # Set plan folder for request handler
            PlanRequestHandler.plan_folder = self.plan_folder
            
            # Create server with reuse address option
            socketserver.TCPServer.allow_reuse_address = True
            self.server = socketserver.TCPServer(("", self.port), PlanRequestHandler)
            
            # Start in background daemon thread
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            url = f"http://localhost:{self.port}/plan-viewer.html"
            print(f"🌐 Plan viewer started: {url}")
            print(f"📁 Serving from: {self.plan_folder}")
            
            # Restore original working directory
            os.chdir(original_cwd)
            
            return url
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            os.chdir(original_cwd)
            raise
    
    def stop(self):
        """Stop the server."""
        if self.server:
            print(f"🛑 Stopping plan server on port {self.port}")
            self.server.shutdown()
            self.server = None
        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self.server is not None and self.thread is not None and self.thread.is_alive()


# Singleton instance management
_plan_server_instance: Optional[PlanServer] = None


def get_plan_server(plan_folder: Path, port: int = PLAN_SERVER_PORT) -> PlanServer:
    """
    Get or create plan server singleton.
    
    Args:
        plan_folder: Path to plan folder to serve
        port: Port number (default: 8150)
    
    Returns:
        PlanServer instance
    """
    global _plan_server_instance
    
    if _plan_server_instance is None:
        _plan_server_instance = PlanServer(plan_folder, port)
    else:
        # Update plan folder for existing server
        _plan_server_instance.plan_folder = plan_folder
        PlanRequestHandler.plan_folder = plan_folder
        print(f"🔄 Updated plan server to serve: {plan_folder}")
    
    return _plan_server_instance


def start_plan_viewer(plan_folder: Path, port: int = PLAN_SERVER_PORT) -> str:
    """
    Start plan viewer server (convenience function).
    
    Args:
        plan_folder: Path to plan folder
        port: Port number (default: 8150)
    
    Returns:
        URL to access plan viewer
    """
    server = get_plan_server(plan_folder, port)
    
    if server.is_running():
        print(f"✅ Plan server already running on port {port}")
        return f"http://localhost:{port}/plan-viewer.html"
    
    return server.start()


def stop_plan_viewer():
    """Stop plan viewer server (convenience function)."""
    global _plan_server_instance
    
    if _plan_server_instance:
        _plan_server_instance.stop()
        _plan_server_instance = None


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python plan_server.py <plan_folder_path>")
        sys.exit(1)
    
    plan_folder = Path(sys.argv[1])
    if not plan_folder.exists():
        print(f"❌ Plan folder not found: {plan_folder}")
        sys.exit(1)
    
    try:
        url = start_plan_viewer(plan_folder)
        print(f"\n✅ Server running: {url}")
        print("Press Ctrl+C to stop...")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        stop_plan_viewer()
        print("✅ Server stopped")
