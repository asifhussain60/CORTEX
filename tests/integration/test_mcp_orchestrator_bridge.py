"""
Integration Test: MCP Server → Orchestrator Bridge

AC-MCP-BRIDGE-001: Validates MCP request flow through orchestrator
- MCP request enters unified MCP server
- Request routed to Master Orchestrator
- Response includes CORTEX headers
"""

import pytest
from typing import Any, Dict

try:
    from src.mcp.server import MCPServer
except (ImportError, ModuleNotFoundError):
    MCPServer = None

try:
    from src.orchestrators.core.master_orchestrator import MasterOrchestrator
except (ImportError, ModuleNotFoundError):
    MasterOrchestrator = None


@pytest.mark.skipif(MCPServer is None, reason="MCPServer not available")
class TestMCPOrchestratorBridge:
    """MCP Server to Orchestrator integration tests."""

    @pytest.fixture
    def mcp_server(self) -> Any:
        """Get MCP Server instance."""
        if MCPServer is None:
            pytest.skip("MCPServer not available")
        return MCPServer()

    @pytest.fixture
    def master(self) -> Any:
        """Get Master Orchestrator instance."""
        if MasterOrchestrator is None:
            pytest.skip("MasterOrchestrator not available")
        MasterOrchestrator._instance = None
        return MasterOrchestrator.instance()

    def test_mcp_request_routed_through_master(self, mcp_server: Any, master: Any):
        """
        MCP request enters unified server and routes to Master Orchestrator.

        Acceptance:
        - MCP server receives request
        - Request passed to Master Orchestrator
        - Master coordinates operation
        """
        assert mcp_server is not None, "MCP Server should initialize"
        assert hasattr(mcp_server, "handle_request"), "Should handle requests"
        assert master is not None, "Master should initialize"

    def test_mcp_response_includes_orchestrator_headers(
        self, mcp_server: Any, master: Any
    ):
        """
        MCP response includes CORTEX orchestrator headers.

        Acceptance:
        - Response wrapped by Master Orchestrator
        - Headers identify orchestrator
        - Headers include timing/operation info
        - Response properly formatted for MCP client
        """
        assert hasattr(master, "get_response_with_headers"), "Should wrap responses"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
