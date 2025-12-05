"""
Dashboard Launcher Module

Module wrapper for dashboard launcher orchestrator. Part of CORTEX operations system.

Triggered by: "load dashboard", "launch dashboard", "open dashboard"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Dict, Any

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class DashboardLauncherModule(BaseOperationModule):
    """
    Launch CORTEX dashboard with HTTP server.
    
    Features:
    - Auto-detect cortex-brain/dashboards/ui/ directory
    - Launch HTTP server on available port (8080-8089)
    - Auto-open browser to dashboard
    - Background server process
    - CORS support
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="dashboard_launcher",
            name="Dashboard Launcher",
            description="Launch CORTEX dashboard with HTTP server and auto-open browser",
            phase=OperationPhase.EXECUTION,
            priority=10
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute dashboard launch.
        
        Args:
            context: Operation context with optional keys:
                - port: int (default: 8080)
                - auto_open: bool (default: True)
                - source: str (default: "mock")
                - cortex_root: Path (auto-detected if not provided)
        
        Returns:
            OperationResult with launch status and server details
        """
        try:
            # Import orchestrator
            from src.orchestrators.dashboard_launcher import launch_dashboard
            
            # Extract options from context
            port = context.get("port", 8080)
            auto_open = context.get("auto_open", True)
            source = context.get("source", "mock")
            cortex_root = context.get("cortex_root", None)
            
            if cortex_root and isinstance(cortex_root, str):
                cortex_root = Path(cortex_root)
            
            self.log_info(f"Launching dashboard on port {port} (auto_open={auto_open}, source={source})")
            
            # Launch dashboard
            result = launch_dashboard(
                port=port,
                auto_open=auto_open,
                source=source,
                cortex_root=cortex_root
            )
            
            if result["success"]:
                self.log_info(f"Dashboard launched: {result['url']}")
                
                # Build response message
                message = [
                    f"✅ Dashboard server started successfully",
                    f"",
                    f"🌐 URL: {result['url']}",
                    f"🔌 Port: {result['port']}",
                    f"📁 Directory: {result['directory']}",
                    f"",
                    f"💡 Dashboard will open automatically in your browser",
                    f"🛑 Press Ctrl+C in the terminal to stop the server"
                ]
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="\n".join(message),
                    data={
                        "port": result["port"],
                        "url": result["url"],
                        "directory": result["directory"],
                        "auto_opened": auto_open,
                        "source": source,
                        "server_running": True
                    }
                )
            else:
                self.log_error(f"Failed to launch dashboard: {result['message']}")
                
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message=f"❌ Failed to launch dashboard: {result['message']}",
                    data=result,
                    errors=[result["message"]]
                )
        
        except ImportError as e:
            error_msg = f"Dashboard launcher orchestrator not found: {e}"
            self.log_error(error_msg)
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"❌ {error_msg}",
                errors=[error_msg]
            )
        
        except Exception as e:
            error_msg = f"Unexpected error launching dashboard: {str(e)}"
            self.log_error(error_msg)
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"❌ {error_msg}",
                errors=[str(e)]
            )
