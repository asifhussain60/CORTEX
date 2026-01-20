"""
Tests for MCP Server Integration

AC-AR-007-01: MCP server starts and accepts connections
AC-AR-007-02: Orchestrators exposed as MCP tools
AC-AR-007-03: Governance context included in MCP responses
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from cortex.mcp.server import MCPServer, MCPConnection, MCPToolInfo
from cortex.orchestrators.core.orchestrator_registry import OrchestratorRegistry
from cortex.core.decorators.orchestrator_decorator import (
    orchestrator,
    clear_orchestrator_registry,
)
from cortex.core.interfaces import IOrchestrator, OperationMode
from cortex.core.result import Ok, Err, Result
from typing import Any, Dict


class MockOrchestrator(IOrchestrator):
    """Mock orchestrator for testing"""
    
    def __init__(self, domain: str):
        self.domain = domain
    
    def get_name(self) -> str:
        return f"{self.domain}_orchestrator"
    
    def get_version(self) -> str:
        return "1.0"
    
    def initialize(self) -> Result[str]:
        return Ok("Initialized")
    
    def get_mode(self) -> OperationMode:
        return OperationMode.PLANNING
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        return Ok({})
    
    def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
        return Ok({})
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        return Ok([])


@pytest.mark.ac("AR-007-01")
class TestMCPServerStartup:
    """Test AC-AR-007-01: MCP server starts and accepts connections"""
    
    def setup_method(self):
        """Setup for each test"""
        MCPServer.reset_instance()
        OrchestratorRegistry.reset_instance()
        clear_orchestrator_registry()
        
        # Register test orchestrators
        @orchestrator(domain="governance", capabilities=["validate", "enforce"])
        class GovernanceOrch(IOrchestrator):
            def get_name(self) -> str:
                return "GovernanceOrchestrator"
            
            def get_version(self) -> str:
                return "2.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
        
        @orchestrator(domain="audit", capabilities=["log", "report"])
        class AuditOrch(IOrchestrator):
            def get_name(self) -> str:
                return "AuditOrchestrator"
            
            def get_version(self) -> str:
                return "1.5"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
    
    def test_server_initialization(self):
        """Test server can be initialized"""
        server = MCPServer(host="127.0.0.1", port=8000)
        
        assert server.host == "127.0.0.1"
        assert server.port == 8000
        assert not server.is_running
        assert not server.is_listening
    
    def test_server_start(self):
        """Test server can start"""
        server = MCPServer(host="127.0.0.1", port=8000)
        result = server.start()
        
        assert result.is_ok()
        assert server.is_running
        assert server.is_listening
    
    def test_server_start_loads_tools(self):
        """Test server loads tools on start"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        # Should have loaded tools
        assert len(server.tools) > 0
        tools = server.get_tools()
        assert len(tools) > 0
    
    def test_server_cannot_start_twice(self):
        """Test server cannot start if already running"""
        server = MCPServer(host="127.0.0.1", port=8000)
        
        # Start first time
        result1 = server.start()
        assert result1.is_ok()
        
        # Try to start again
        result2 = server.start()
        assert result2.is_err()
    
    def test_server_stop(self):
        """Test server can be stopped"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        result = server.stop()
        
        assert result.is_ok()
        assert not server.is_running
        assert not server.is_listening
    
    def test_server_status(self):
        """Test server status reporting"""
        server = MCPServer(host="127.0.0.1", port=9000)
        server.start()
        
        status = server.get_status()
        
        assert status["is_running"] == True
        assert status["is_listening"] == True
        assert "host" in status
        assert "tools_available" in status
    
    def test_server_singleton(self):
        """Test server singleton pattern"""
        server1 = MCPServer.instance()
        server2 = MCPServer.instance()
        
        assert server1 is server2


class TestMCPServerConnections:
    """Test connection management"""
    
    def setup_method(self):
        """Setup for each test"""
        MCPServer.reset_instance()
        OrchestratorRegistry.reset_instance()
        clear_orchestrator_registry()
        
        @orchestrator(domain="test")
        class TestOrch(IOrchestrator):
            def get_name(self) -> str:
                return "TestOrchestrator"
            
            def get_version(self) -> str:
                return "1.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
    
    def test_accept_connection(self):
        """Test accepting client connection"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        result = server.accept_connection("client1", "192.168.1.100:50000")
        
        assert result.is_ok()
        connection = result.unwrap()
        assert connection.client_id == "client1"
        assert connection.is_active
    
    def test_connection_not_accepted_when_server_stopped(self):
        """Test connection rejected when server not listening"""
        server = MCPServer(host="127.0.0.1", port=8000)
        
        result = server.accept_connection("client1", "192.168.1.100:50000")
        
        assert result.is_err()
    
    def test_max_connections_enforced(self):
        """Test max connections limit is enforced"""
        server = MCPServer(host="127.0.0.1", port=8000, max_connections=2)
        server.start()
        
        # Accept 2 connections
        result1 = server.accept_connection("client1", "192.168.1.100:50000")
        assert result1.is_ok()
        
        result2 = server.accept_connection("client2", "192.168.1.101:50001")
        assert result2.is_ok()
        
        # Try to accept 3rd (should fail)
        result3 = server.accept_connection("client3", "192.168.1.102:50002")
        assert result3.is_err()
    
    def test_close_connection(self):
        """Test closing a connection"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        # Accept and close
        server.accept_connection("client1", "192.168.1.100:50000")
        result = server.close_connection("client1")
        
        assert result.is_ok()
        assert len(server.connections) == 0
    
    def test_get_connections(self):
        """Test getting list of connections"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        server.accept_connection("client1", "192.168.1.100:50000")
        server.accept_connection("client2", "192.168.1.101:50001")
        
        connections = server.get_connections()
        
        assert len(connections) == 2
        assert any(c["client_id"] == "client1" for c in connections)


@pytest.mark.ac("AR-007-02")
class TestMCPServerTools:
    """Test AC-AR-007-02: Orchestrators exposed as MCP tools"""
    
    def setup_method(self):
        """Setup for each test"""
        MCPServer.reset_instance()
        OrchestratorRegistry.reset_instance()
        clear_orchestrator_registry()
        
        @orchestrator(
            domain="governance",
            version="2.0",
            capabilities=["validate", "enforce"]
        )
        class GovernanceOrch(IOrchestrator):
            def get_name(self) -> str:
                return "GovernanceOrchestrator"
            
            def get_version(self) -> str:
                return "2.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
    
    def test_tools_loaded_from_orchestrators(self):
        """Test tools are loaded from orchestrators"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        tools = server.get_tools()
        
        # Should have governance_validate and governance_enforce
        tool_names = [t.name for t in tools]
        assert "governance_validate" in tool_names
        assert "governance_enforce" in tool_names
    
    def test_tool_info_structure(self):
        """Test tool info has correct structure"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        tool = server.get_tool("governance_validate")
        
        assert tool is not None
        assert tool.name == "governance_validate"
        assert tool.orchestrator_domain == "governance"
        assert "validate" in tool.capabilities
    
    def test_get_specific_tool(self):
        """Test getting specific tool"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        tool = server.get_tool("governance_validate")
        
        assert tool is not None
        assert isinstance(tool, MCPToolInfo)
    
    def test_get_nonexistent_tool(self):
        """Test getting nonexistent tool returns None"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        tool = server.get_tool("nonexistent_tool")
        
        assert tool is None


@pytest.mark.ac("AR-007-03")
class TestMCPServerGovernance:
    """Test AC-AR-007-03: Governance context included in responses"""
    
    def setup_method(self):
        """Setup for each test"""
        MCPServer.reset_instance()
        OrchestratorRegistry.reset_instance()
        clear_orchestrator_registry()
        
        @orchestrator(domain="test")
        class TestOrch(IOrchestrator):
            def get_name(self) -> str:
                return "TestOrchestrator"
            
            def get_version(self) -> str:
                return "1.0"
            
            def initialize(self) -> Result[str]:
                return Ok("Initialized")
            
            def get_mode(self) -> OperationMode:
                return OperationMode.PLANNING
            
            def get_mcp_tools(self) -> Result[Dict[str, Any]]:
                return Ok({})
            
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result[Any]:
                return Ok({})
            
            def get_audit_trail(self, limit: int = 100) -> Result[list]:
                return Ok([])
    
    def test_governance_context_retrieval(self):
        """Test getting governance context"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        context = server.get_governance_context()
        
        assert "governance_enabled" in context
        assert "tiers" in context
        assert "timestamp" in context
    
    def test_governance_context_includes_tiers(self):
        """Test governance context includes tier information"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        context = server.get_governance_context()
        
        tiers = context.get("tiers", {})
        assert "tier_0" in tiers
        assert "tier_1" in tiers
        assert "tier_2" in tiers
    
    def test_governance_context_has_timestamp(self):
        """Test governance context includes timestamp"""
        server = MCPServer(host="127.0.0.1", port=8000)
        server.start()
        
        context = server.get_governance_context()
        timestamp = context.get("timestamp")
        
        # Should be ISO format timestamp
        assert timestamp is not None
        assert "T" in timestamp  # ISO format includes T


class TestMCPConnectionInfo:
    """Test MCPConnection dataclass"""
    
    def test_connection_creation(self):
        """Test creating MCPConnection"""
        conn = MCPConnection(
            client_id="test_client",
            connected_at="2026-01-14T10:00:00Z",
            remote_address="192.168.1.100:50000"
        )
        
        assert conn.client_id == "test_client"
        assert conn.is_active == True
    
    def test_connection_deactivation(self):
        """Test deactivating connection"""
        conn = MCPConnection(
            client_id="test_client",
            connected_at="2026-01-14T10:00:00Z",
            remote_address="192.168.1.100:50000"
        )
        
        conn.is_active = False
        assert conn.is_active == False


class TestMCPToolInfo:
    """Test MCPToolInfo dataclass"""
    
    def test_tool_info_creation(self):
        """Test creating MCPToolInfo"""
        tool = MCPToolInfo(
            name="governance_validate",
            description="Validate governance rules",
            orchestrator_domain="governance",
            parameters={"operation": "validate"},
            capabilities=["validate"]
        )
        
        assert tool.name == "governance_validate"
        assert tool.orchestrator_domain == "governance"
        assert "validate" in tool.capabilities
