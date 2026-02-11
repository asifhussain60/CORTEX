"""MCP server bootstrapper.

This module provides the MCPBootstrapper class that starts and
validates the MCP server for Claude integration.

PHASE-DEPLOYMENT-002: AC-DEP-002-04
"""

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ServerStartResult:
    """Result of server start operation.

    Attributes:
        started: Whether the server started successfully.
        pid: Process ID if started.
        port: Port the server is running on.
        error: Error message if start failed.
    """
    started: bool = False
    pid: Optional[int] = None
    port: int = 3000
    error: str = ""


@dataclass
class ServerStopResult:
    """Result of server stop operation.

    Attributes:
        stopped: Whether the server was stopped.
        error: Error message if stop failed.
    """
    stopped: bool = False
    error: str = ""


@dataclass
class HealthCheckResult:
    """Result of health check.

    Attributes:
        healthy: Whether the server is healthy.
        response: Health check response.
        error: Error message if check failed.
    """
    healthy: bool = False
    response: Dict = field(default_factory=dict)
    error: str = ""


@dataclass
class ConfigUpdateResult:
    """Result of Claude config update.

    Attributes:
        updated: Whether the config was updated.
        path: Path to the config file.
        error: Error message if update failed.
    """
    updated: bool = False
    path: str = ""
    error: str = ""


class MCPBootstrapper:
    """Bootstraps and manages the MCP server.

    Handles starting, stopping, and validating the MCP server,
    as well as configuring Claude Desktop integration.

    Attributes:
        workspace: Path to the workspace root.
        claude_config_path: Path to Claude Desktop config.
        port: Port to run the server on.
    """

    DEFAULT_PORT = 3000

    def __init__(
        self,
        workspace: Path,
        claude_config_path: Optional[Path] = None,
        port: int = DEFAULT_PORT,
    ) -> None:
        """Initialize the bootstrapper.

        Args:
            workspace: Path to the workspace root.
            claude_config_path: Path to Claude Desktop config.
            port: Port to run the server on.
        """
        self.workspace = Path(workspace)
        self.claude_config_path = Path(claude_config_path) if claude_config_path else None
        self.port = port
        self._process: Optional[subprocess.Popen] = None

    def start_server(self) -> ServerStartResult:
        """Start the MCP server as a subprocess.

        Returns:
            ServerStartResult with start details.
        """
        result = ServerStartResult(port=self.port)

        server_path = self.workspace / "cortex" / "mcp" / "server.py"

        if not server_path.exists():
            result.error = f"Server not found at {server_path}"
            return result

        try:
            self._process = subprocess.Popen(
                ["python", str(server_path)],
                cwd=str(self.workspace),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Give it a moment to start
            time.sleep(0.5)

            if self._process.poll() is None:
                # Process is still running
                result.started = True
                result.pid = self._process.pid
            else:
                result.error = "Server exited immediately"

        except Exception as e:
            result.error = str(e)

        return result

    def stop_server(self) -> ServerStopResult:
        """Stop the MCP server.

        Returns:
            ServerStopResult with stop details.
        """
        result = ServerStopResult()

        if self._process is None:
            result.stopped = True
            return result

        try:
            self._process.terminate()
            self._process.wait(timeout=5)
            result.stopped = True
        except subprocess.TimeoutExpired:
            self._process.kill()
            result.stopped = True
        except Exception as e:
            result.error = str(e)

        self._process = None
        return result

    def check_health(self, timeout: int = 5) -> HealthCheckResult:
        """Check if the MCP server is healthy.

        Args:
            timeout: Timeout for health check request.

        Returns:
            HealthCheckResult with health status.
        """
        result = HealthCheckResult()

        try:
            import requests

            response = requests.get(
                f"http://localhost:{self.port}/health",
                timeout=timeout,
            )

            if response.status_code == 200:
                result.healthy = True
                result.response = response.json()
            else:
                result.error = f"Unhealthy response: {response.status_code}"

        except ImportError:
            result.error = "requests library not available"
        except Exception as e:
            result.error = str(e)

        return result

    def get_registered_tools(self) -> List[Dict]:
        """Get list of registered MCP tools.

        Returns:
            List of tool definitions.
        """
        try:
            import requests

            response = requests.get(
                f"http://localhost:{self.port}/tools",
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("tools", [])

        except Exception:
            pass

        return []

    def update_claude_config(self) -> ConfigUpdateResult:
        """Update Claude Desktop config with MCP server.

        Returns:
            ConfigUpdateResult with update details.
        """
        result = ConfigUpdateResult()

        if self.claude_config_path is None:
            # Try to find Claude config
            possible_paths = [
                Path.home() / ".config" / "claude" / "claude_desktop_config.json",
                Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
            ]

            for path in possible_paths:
                if path.exists():
                    self.claude_config_path = path
                    break

        if self.claude_config_path is None or not self.claude_config_path.exists():
            # Create new config
            if self.claude_config_path is None:
                result.error = "Could not determine Claude config path"
                return result

            self.claude_config_path.parent.mkdir(parents=True, exist_ok=True)
            config = {"mcpServers": {}}
        else:
            config = json.loads(self.claude_config_path.read_text())

        # Add CORTEX MCP server
        config.setdefault("mcpServers", {})
        config["mcpServers"]["cortex"] = {
            "command": "python",
            "args": [str(self.workspace / "cortex" / "mcp" / "server.py")],
            "cwd": str(self.workspace),
        }

        self.claude_config_path.write_text(json.dumps(config, indent=2))

        result.updated = True
        result.path = str(self.claude_config_path)

        return result


def main() -> int:
    """CLI entry point for MCP bootstrapper.

    Returns:
        Exit code.
    """
    import sys

    workspace = Path.cwd()
    bootstrapper = MCPBootstrapper(workspace)

    if "--start" in sys.argv:
        result = bootstrapper.start_server()
        if result.started:
            print(f"✅ MCP server started (PID: {result.pid}, port: {result.port})")
            return 0
        else:
            print(f"❌ Failed to start MCP server: {result.error}")
            return 1

    if "--stop" in sys.argv:
        result = bootstrapper.stop_server()
        if result.stopped:
            print("✅ MCP server stopped")
            return 0
        else:
            print(f"❌ Failed to stop MCP server: {result.error}")
            return 1

    if "--health" in sys.argv:
        result = bootstrapper.check_health()
        if result.healthy:
            print("✅ MCP server is healthy")
            return 0
        else:
            print(f"❌ MCP server unhealthy: {result.error}")
            return 1

    if "--config" in sys.argv:
        result = bootstrapper.update_claude_config()
        if result.updated:
            print(f"✅ Updated Claude config: {result.path}")
            return 0
        else:
            print(f"❌ Failed to update config: {result.error}")
            return 1

    print("Usage: mcp_bootstrapper.py [--start|--stop|--health|--config]")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
