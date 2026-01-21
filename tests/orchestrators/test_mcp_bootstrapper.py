"""Tests for MCP bootstrapper (PHASE-DEPLOYMENT-002 AC-DEP-002-04).

This module tests the MCP server bootstrap functionality.
"""

import json
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch, AsyncMock

import pytest


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary workspace.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the temporary workspace.
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Create MCP server structure
    mcp_dir = workspace / "cortex" / "mcp"
    mcp_dir.mkdir(parents=True)
    (mcp_dir / "server.py").write_text("# MCP Server placeholder")
    
    yield workspace


@pytest.fixture
def mcp_module():
    """Import the MCP bootstrapper module.
    
    Returns:
        The mcp_bootstrapper module.
    """
    from cortex.orchestrators.onboarding import mcp_bootstrapper
    return mcp_bootstrapper


class TestMCPServerStarts:
    """Tests for MCP server startup."""
    
    def test_mcp_server_starts(
        self, temp_workspace: Path, mcp_module
    ) -> None:
        """MCP server starts as subprocess.
        
        Args:
            temp_workspace: Path to temp workspace.
            mcp_module: The MCP bootstrapper module.
        """
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None  # Process running
            mock_popen.return_value = mock_process
            
            bootstrapper = mcp_module.MCPBootstrapper(temp_workspace)
            result = bootstrapper.start_server()
            
            assert result.started is True
    
    def test_mcp_server_stops(
        self, temp_workspace: Path, mcp_module
    ) -> None:
        """MCP server can be stopped.
        
        Args:
            temp_workspace: Path to temp workspace.
            mcp_module: The MCP bootstrapper module.
        """
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process
            
            bootstrapper = mcp_module.MCPBootstrapper(temp_workspace)
            bootstrapper.start_server()
            result = bootstrapper.stop_server()
            
            assert result.stopped is True


class TestMCPHealthEndpoint:
    """Tests for MCP health endpoint."""
    
    def test_mcp_health_endpoint(
        self, temp_workspace: Path, mcp_module
    ) -> None:
        """MCP health endpoint responds correctly.
        
        Args:
            temp_workspace: Path to temp workspace.
            mcp_module: The MCP bootstrapper module.
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"status": "healthy"}
            )
            
            bootstrapper = mcp_module.MCPBootstrapper(temp_workspace)
            health = bootstrapper.check_health()
            
            assert health.healthy is True


class TestMCPToolsRegistered:
    """Tests for MCP tool registration."""
    
    def test_mcp_tools_registered(
        self, temp_workspace: Path, mcp_module
    ) -> None:
        """MCP tools are registered in server.
        
        Args:
            temp_workspace: Path to temp workspace.
            mcp_module: The MCP bootstrapper module.
        """
        with patch('requests.get') as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {
                    "tools": [
                        {"name": "echo_tool"},
                        {"name": "query_tool"},
                    ]
                }
            )
            
            bootstrapper = mcp_module.MCPBootstrapper(temp_workspace)
            tools = bootstrapper.get_registered_tools()
            
            assert len(tools) >= 2


class TestClaudeDesktopConfig:
    """Tests for Claude Desktop configuration."""
    
    def test_claude_desktop_config_updated(
        self, temp_workspace: Path, mcp_module
    ) -> None:
        """Claude Desktop config is updated with MCP server.
        
        Args:
            temp_workspace: Path to temp workspace.
            mcp_module: The MCP bootstrapper module.
        """
        # Create mock Claude config location
        claude_config = temp_workspace / "claude-config.json"
        claude_config.write_text(json.dumps({"mcpServers": {}}))
        
        bootstrapper = mcp_module.MCPBootstrapper(
            temp_workspace,
            claude_config_path=claude_config
        )
        result = bootstrapper.update_claude_config()
        
        assert result.updated is True
        
        # Verify config was updated
        config = json.loads(claude_config.read_text())
        assert "cortex" in config.get("mcpServers", {})
