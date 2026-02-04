"""
MCP Tool Definition for Dashboard Server Management.
Exposes dashboard_server.py functionality via MCP protocol.
"""

from cortex.mcp.decorators import mcp_tool, mcp_tool_group
from cortex.tools.dashboard_server import DashboardServerTool
import json


@mcp_tool_group(
    name="dashboard_server",
    description="Dashboard server management and health monitoring",
    version="1.0.0"
)
class DashboardServerTools:
    """MCP tools for dashboard server lifecycle and testing."""
    
    def __init__(self):
        self.tool = DashboardServerTool()
    
    @mcp_tool(
        name="kill_http_processes",
        description="Kill all HTTP processes on specified ports",
        input_schema={
            "type": "object",
            "properties": {
                "ports": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of ports to kill processes on",
                    "default": [8080, 8888]
                }
            },
            "required": []
        }
    )
    async def kill_http_processes(self, ports: list = None) -> dict:
        """Kill HTTP processes on specified ports."""
        if ports is None:
            ports = [8080, 8888]
        
        success, message = self.tool.kill_all_http_processes(ports)
        
        return {
            "success": success,
            "message": message,
            "ports_targeted": ports
        }
    
    @mcp_tool(
        name="start_dashboard_server",
        description="Start HTTP server on port 8080 serving dashboard",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    async def start_dashboard_server(self) -> dict:
        """Start the dashboard HTTP server."""
        success, message, pid = self.tool.start_server()
        
        return {
            "success": success,
            "message": message,
            "pid": pid,
            "port": 8080,
            "url": "http://localhost:8080"
        }
    
    @mcp_tool(
        name="check_server_health",
        description="Check if dashboard server is running and healthy",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    async def check_server_health(self) -> dict:
        """Check if server is running."""
        result = self.tool.check_server_running()
        
        return {
            "status": result.status.value,
            "message": result.message,
            "details": result.details,
            "timestamp": result.timestamp
        }
    
    @mcp_tool(
        name="check_server_logs",
        description="Check server logs for errors",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    async def check_server_logs(self) -> dict:
        """Check if server logs are clean."""
        result = self.tool.check_logs_clean()
        
        return {
            "status": result.status.value,
            "message": result.message,
            "details": result.details,
            "timestamp": result.timestamp
        }
    
    @mcp_tool(
        name="check_dashboard_data",
        description="Check if dashboard data is loaded",
        input_schema={
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository name",
                    "default": "KSESSIONS"
                }
            },
            "required": []
        }
    )
    async def check_dashboard_data(self, repo: str = "KSESSIONS") -> dict:
        """Check if dashboard data loaded."""
        result = self.tool.check_dashboard_data_loaded(repo)
        
        return {
            "status": result.status.value,
            "message": result.message,
            "details": result.details,
            "timestamp": result.timestamp
        }
    
    @mcp_tool(
        name="verify_tabs_generated",
        description="Verify all 8 dashboard tabs are generated and visible",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    async def verify_tabs_generated(self) -> dict:
        """Verify tabs are generated."""
        result = self.tool.verify_tabs_generated()
        
        return {
            "status": result.status.value,
            "message": result.message,
            "details": result.details,
            "timestamp": result.timestamp,
            "expected_tabs": [
                "Overview", "Metrics", "Security", "Dependencies",
                "Quality", "Use Cases", "LENS", "Refactoring"
            ]
        }
    
    @mcp_tool(
        name="run_dashboard_health_check",
        description="Run complete health check suite for dashboard",
        input_schema={
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository name",
                    "default": "KSESSIONS"
                }
            },
            "required": []
        }
    )
    async def run_dashboard_health_check(self, repo: str = "KSESSIONS") -> dict:
        """Run full health check."""
        return self.tool.run_full_health_check(repo)
    
    @mcp_tool(
        name="launch_dashboard",
        description="Launch dashboard in browser",
        input_schema={
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository name",
                    "default": "KSESSIONS"
                }
            },
            "required": []
        }
    )
    async def launch_dashboard(self, repo: str = "KSESSIONS") -> dict:
        """Launch dashboard."""
        success, message = self.tool.launch_dashboard(repo)
        
        return {
            "success": success,
            "message": message,
            "url": f"http://localhost:8080/spa/dashboard.html?repo={repo}"
        }
    
    @mcp_tool(
        name="dashboard_full_cycle",
        description="Full lifecycle: kill processes, start server, health check, launch",
        input_schema={
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository name",
                    "default": "KSESSIONS"
                },
                "ports_to_kill": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Ports to kill processes on",
                    "default": [8080, 8888]
                }
            },
            "required": []
        }
    )
    async def dashboard_full_cycle(self, repo: str = "KSESSIONS", ports_to_kill: list = None) -> dict:
        """Run full dashboard lifecycle."""
        if ports_to_kill is None:
            ports_to_kill = [8080, 8888]
        
        results = {
            "lifecycle": "full_cycle",
            "repo": repo,
            "steps": {}
        }
        
        # Step 1: Kill
        success, message = self.tool.kill_all_http_processes(ports_to_kill)
        results["steps"]["kill_processes"] = {
            "success": success,
            "message": message
        }
        
        # Step 2: Start
        success, message, pid = self.tool.start_server()
        results["steps"]["start_server"] = {
            "success": success,
            "message": message,
            "pid": pid
        }
        
        if not success:
            results["overall_status"] = "failed"
            return results
        
        # Step 3: Health Check
        health = self.tool.run_full_health_check(repo)
        results["steps"]["health_check"] = health
        
        # Step 4: Launch
        success, message = self.tool.launch_dashboard(repo)
        results["steps"]["launch"] = {
            "success": success,
            "message": message
        }
        
        # Overall status
        all_healthy = (
            results["steps"]["kill_processes"]["success"] and
            results["steps"]["start_server"]["success"] and
            health["overall_status"] == "healthy" and
            results["steps"]["launch"]["success"]
        )
        
        results["overall_status"] = "healthy" if all_healthy else "degraded"
        results["dashboard_url"] = f"http://localhost:8080/spa/dashboard.html?repo={repo}"
        
        return results
