#!/usr/bin/env python3
"""
CORTEX Plan Viewer Server Manager
Manages HTTP server for plan viewers with auto-restart and port management
Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import http.server
import socketserver
import os
import sys
import json
import signal
import psutil
from pathlib import Path
from typing import Optional, Dict, List
import argparse


class PlanViewerServer:
    """Manages HTTP server for CORTEX plan viewers"""
    
    DEFAULT_PORT = 8050
    PORT_RANGE = range(8050, 8060)
    PID_FILE = Path.home() / ".cortex" / "plan-viewer-server.pid"
    SERVER_REGISTRY = Path.home() / ".cortex" / "plan-viewer-servers.json"
    
    def __init__(self, plan_dir: Path, port: Optional[int] = None):
        self.plan_dir = Path(plan_dir).resolve()
        self.port = port or self.DEFAULT_PORT
        self.server = None
        self.ensure_cortex_dir()
    
    def ensure_cortex_dir(self):
        """Ensure .cortex directory exists"""
        self.PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def find_available_port(self) -> int:
        """Find an available port in the range"""
        import socket
        for port in self.PORT_RANGE:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"No available ports in range {self.PORT_RANGE}")
    
    def is_server_running(self, port: int) -> bool:
        """Check if server is running on port"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
    
    def get_running_servers(self) -> Dict[int, Dict]:
        """Get list of running plan viewer servers"""
        if not self.SERVER_REGISTRY.exists():
            return {}
        
        try:
            with open(self.SERVER_REGISTRY, 'r') as f:
                servers = json.load(f)
            
            # Filter out dead servers
            active_servers = {}
            for port, info in servers.items():
                if self.is_server_running(int(port)):
                    active_servers[port] = info
            
            # Update registry with active servers only
            if active_servers != servers:
                self.save_server_registry(active_servers)
            
            return active_servers
        except:
            return {}
    
    def save_server_registry(self, servers: Dict):
        """Save server registry"""
        with open(self.SERVER_REGISTRY, 'w') as f:
            json.dump(servers, f, indent=2)
    
    def register_server(self, port: int, plan_dir: Path, pid: int):
        """Register a running server"""
        servers = self.get_running_servers()
        servers[str(port)] = {
            "plan_dir": str(plan_dir),
            "pid": pid,
            "url": f"http://localhost:{port}"
        }
        self.save_server_registry(servers)
    
    def stop_server_on_port(self, port: int) -> bool:
        """Stop server running on specific port"""
        servers = self.get_running_servers()
        port_str = str(port)
        
        if port_str in servers:
            pid = servers[port_str].get('pid')
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"✅ Stopped server on port {port} (PID: {pid})")
                    del servers[port_str]
                    self.save_server_registry(servers)
                    return True
                except ProcessLookupError:
                    # Process already dead
                    del servers[port_str]
                    self.save_server_registry(servers)
                    return True
                except PermissionError:
                    print(f"❌ Permission denied to stop PID {pid}")
                    return False
        return False
    
    def find_server_for_plan(self, plan_dir: Path) -> Optional[int]:
        """Find if a server is already running for this plan"""
        servers = self.get_running_servers()
        plan_dir_str = str(plan_dir.resolve())
        
        for port, info in servers.items():
            if info['plan_dir'] == plan_dir_str:
                return int(port)
        return None
    
    def start(self, restart: bool = False, open_browser: bool = True):
        """Start the plan viewer server"""
        # Check if server already running for this plan
        existing_port = self.find_server_for_plan(self.plan_dir)
        
        if existing_port:
            if restart:
                print(f"🔄 Restarting server for {self.plan_dir.name}...")
                self.stop_server_on_port(existing_port)
            else:
                print(f"✅ Server already running for {self.plan_dir.name}")
                url = f"http://localhost:{existing_port}"
                print(f"📍 URL: {url}")
                
                if open_browser:
                    self.open_browser(url)
                return existing_port
        
        # Find available port
        if not self.is_server_running(self.port):
            port = self.port
        else:
            port = self.find_available_port()
            print(f"ℹ️  Port {self.port} busy, using {port} instead")
        
        # Change to plan directory
        os.chdir(self.plan_dir)
        
        # Create request handler
        Handler = http.server.SimpleHTTPRequestHandler
        
        try:
            # Start server in background
            with socketserver.TCPServer(("", port), Handler) as httpd:
                httpd.allow_reuse_address = True
                
                # Register server
                self.register_server(port, self.plan_dir, os.getpid())
                
                url = f"http://localhost:{port}"
                print(f"\n{'='*60}")
                print(f"🚀 CORTEX Plan Viewer Server")
                print(f"{'='*60}")
                print(f"📁 Plan: {self.plan_dir.name}")
                print(f"📍 URL:  {url}")
                print(f"🔌 Port: {port}")
                print(f"{'='*60}")
                print(f"\n✅ Server started successfully!")
                print(f"🌐 Open browser: {url}/plan-viewer.html")
                print(f"\n⏹️  Press Ctrl+C to stop\n")
                
                if open_browser:
                    self.open_browser(url)
                
                # Serve forever
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\n\n🛑 Server stopped by user")
                    self.stop_server_on_port(port)
        
        except OSError as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)
    
    def open_browser(self, url: str):
        """Open browser to plan viewer"""
        import webbrowser
        import time
        
        time.sleep(0.5)  # Give server time to start
        viewer_url = f"{url}/plan-viewer.html"
        try:
            webbrowser.open(viewer_url)
            print(f"🌐 Opening browser: {viewer_url}")
        except:
            print(f"ℹ️  Could not open browser automatically")
            print(f"   Please open manually: {viewer_url}")
    
    @classmethod
    def list_servers(cls):
        """List all running plan viewer servers"""
        server_manager = cls(Path.cwd())
        servers = server_manager.get_running_servers()
        
        if not servers:
            print("ℹ️  No plan viewer servers currently running")
            return
        
        print(f"\n{'='*60}")
        print(f"🚀 CORTEX Plan Viewer Servers")
        print(f"{'='*60}\n")
        
        for port, info in servers.items():
            plan_name = Path(info['plan_dir']).name
            print(f"📁 {plan_name}")
            print(f"   URL:  {info['url']}")
            print(f"   Port: {port}")
            print(f"   PID:  {info['pid']}")
            print()
    
    @classmethod
    def stop_all(cls):
        """Stop all running plan viewer servers"""
        server_manager = cls(Path.cwd())
        servers = server_manager.get_running_servers()
        
        if not servers:
            print("ℹ️  No servers to stop")
            return
        
        print(f"🛑 Stopping {len(servers)} server(s)...")
        for port in list(servers.keys()):
            server_manager.stop_server_on_port(int(port))
        
        print("✅ All servers stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CORTEX Plan Viewer Server Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server for current plan
  python plan-viewer-server.py

  # Start server for specific plan
  python plan-viewer-server.py --plan-dir /path/to/plan

  # Restart existing server
  python plan-viewer-server.py --restart

  # List running servers
  python plan-viewer-server.py --list

  # Stop all servers
  python plan-viewer-server.py --stop-all

  # Stop specific port
  python plan-viewer-server.py --stop 8050
        """
    )
    
    parser.add_argument(
        '--plan-dir',
        type=Path,
        default=Path.cwd(),
        help='Path to plan directory (default: current directory)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help=f'Port to use (default: auto-detect from {PlanViewerServer.PORT_RANGE})'
    )
    
    parser.add_argument(
        '--restart',
        action='store_true',
        help='Restart server if already running'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not open browser automatically'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all running servers'
    )
    
    parser.add_argument(
        '--stop-all',
        action='store_true',
        help='Stop all running servers'
    )
    
    parser.add_argument(
        '--stop',
        type=int,
        metavar='PORT',
        help='Stop server on specific port'
    )
    
    args = parser.parse_args()
    
    # Handle list command
    if args.list:
        PlanViewerServer.list_servers()
        return
    
    # Handle stop-all command
    if args.stop_all:
        PlanViewerServer.stop_all()
        return
    
    # Handle stop specific port
    if args.stop:
        server = PlanViewerServer(Path.cwd())
        if server.stop_server_on_port(args.stop):
            print(f"✅ Server on port {args.stop} stopped")
        else:
            print(f"❌ No server running on port {args.stop}")
        return
    
    # Start server
    server = PlanViewerServer(
        plan_dir=args.plan_dir,
        port=args.port
    )
    
    server.start(
        restart=args.restart,
        open_browser=not args.no_browser
    )


if __name__ == "__main__":
    main()
