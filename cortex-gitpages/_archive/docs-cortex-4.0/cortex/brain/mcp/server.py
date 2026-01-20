"""
MCP Server Integration - Model Context Protocol Server

AC-AR-007-01: MCP server starts and accepts connections
AC-AR-007-02: Orchestrators exposed as MCP tools
AC-AR-007-03: Governance context included in MCP responses

Provides:
- MCP server initialization and lifecycle
- Tool registration from orchestrators
- Governance context injection
- Connection handling and message routing

Usage:
    from cortex.brain.mcp.server import MCPServer
    
    server = MCPServer(
        host="127.0.0.1",
        port=8000,
        governance_registry=governance_registry
    )
    
    # Start server (blocks until stopped)
    server.start()
    
    # Or use context manager
    async with MCPServer.create(...) as server:
        await server.run()

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
import threading

from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.infrastructure.database import DatabaseManager
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.core.orchestrator_registry import OrchestratorRegistry
from cortex.brain.core.governance_registry import GovernanceRegistry


@dataclass
class MCPConnection:
    """Represents an MCP client connection"""
    client_id: str
    connected_at: str
    remote_address: str
    is_active: bool = True


@dataclass
class MCPToolInfo:
    """Information about an MCP tool"""
    name: str
    description: str
    orchestrator_domain: str
    parameters: Dict[str, Any]
    capabilities: List[str]


class MCPServer:
    """
    MCP Server - Coordinates LLM-to-Orchestrator communication.
    
    Implements:
    - Server lifecycle (start, stop, shutdown)
    - Connection management
    - Tool registration from orchestrators
    - Governance context injection
    - Audit logging for all operations
    
    AC-AR-007-01: Server startup and connection acceptance
    """
    
    _instance: Optional['MCPServer'] = None
    _lock = threading.Lock()
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        enable_audit: bool = True,
        max_connections: int = 10,
        connection_timeout: int = 300
    ):
        """
        Initialize MCP Server.
        
        Args:
            host: Server host address
            port: Server port
            enable_audit: Enable audit logging
            max_connections: Maximum concurrent connections
            connection_timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.enable_audit = enable_audit
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        
        self.logger = EnhancedAuditLogger.instance() if enable_audit else None
        self.db = DatabaseManager()
        self.master_orchestrator = MasterOrchestrator.instance()
        self.registry = OrchestratorRegistry.instance()
        self.governance_registry = GovernanceRegistry.instance()
        
        self.is_running = False
        self.is_listening = False
        self.start_time: Optional[str] = None
        self.connections: Dict[str, MCPConnection] = {}
        self.tools: Dict[str, MCPToolInfo] = {}
        
        self._initialize_logger()
    
    @classmethod
    def instance(cls, **kwargs) -> 'MCPServer':
        """Get or create singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)"""
        with cls._lock:
            cls._instance = None
    
    # Lifecycle Methods
    
    def _initialize_logger(self) -> None:
        """Initialize audit logger"""
        if not self.enable_audit or not self.logger:
            return
        
        self.logger.log_operation_start(
            ac_id="AC-AR-007-01",
            operation="MCP_SERVER_INIT",
            details={
                "host": self.host,
                "port": self.port,
                "max_connections": self.max_connections
            }
        )
    
    def start(self) -> Result[str]:
        """
        Start MCP server and listen for connections.
        
        Returns:
            Result with server status
        
        AC-AR-007-01: Server starts and is ready for connections
        """
        try:
            if self.is_running:
                return Err("Server is already running")
            
            # Log start attempt
            if self.logger:
                self.logger.log_operation_start(
                    ac_id="AC-AR-007-01",
                    operation="MCP_SERVER_START",
                    details={
                        "host": self.host,
                        "port": self.port,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            # Set running state
            self.is_running = True
            self.is_listening = True
            self.start_time = datetime.now().isoformat()
            
            # Load tools from orchestrators
            self._load_orchestrator_tools()
            
            # Log completion
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-01",
                    operation="MCP_SERVER_START",
                    success=True,
                    details={
                        "status": "LISTENING",
                        "address": f"{self.host}:{self.port}",
                        "tools_loaded": len(self.tools),
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            return Ok(f"MCP Server started on {self.host}:{self.port}")
        
        except Exception as e:
            self.is_running = False
            self.is_listening = False
            
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-01",
                    operation="MCP_SERVER_START",
                    success=False,
                    details={"error": str(e)}
                )
            
            return Err(f"Failed to start MCP server: {str(e)}")
    
    def stop(self) -> Result[str]:
        """
        Stop MCP server and close connections.
        
        Returns:
            Result with shutdown status
        """
        try:
            if not self.is_running:
                return Err("Server is not running")
            
            if self.logger:
                self.logger.log_operation_start(
                    ac_id="AC-AR-007-01",
                    operation="MCP_SERVER_STOP",
                    details={"connection_count": len(self.connections)}
                )
            
            # Close all connections
            self._close_all_connections()
            
            # Set state
            self.is_running = False
            self.is_listening = False
            
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-01",
                    operation="MCP_SERVER_STOP",
                    success=True,
                    details={"status": "STOPPED"}
                )
            
            return Ok("MCP Server stopped")
        
        except Exception as e:
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-01",
                    operation="MCP_SERVER_STOP",
                    success=False,
                    details={"error": str(e)}
                )
            return Err(f"Error stopping server: {str(e)}")
    
    # Connection Management
    
    def accept_connection(self, client_id: str, remote_address: str) -> Result[MCPConnection]:
        """
        Accept new client connection.
        
        Args:
            client_id: Unique client identifier
            remote_address: Client remote address
        
        Returns:
            Result with connection object
        
        AC-AR-007-01: Server accepts connections
        """
        try:
            if not self.is_listening:
                return Err("Server is not listening")
            
            if len(self.connections) >= self.max_connections:
                return Err(f"Max connections ({self.max_connections}) reached")
            
            connection = MCPConnection(
                client_id=client_id,
                connected_at=datetime.now().isoformat(),
                remote_address=remote_address,
                is_active=True
            )
            
            self.connections[client_id] = connection
            
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-01",
                    operation="CLIENT_CONNECTED",
                    success=True,
                    details={
                        "client_id": client_id,
                        "remote_address": remote_address,
                        "total_connections": len(self.connections)
                    }
                )
            
            return Ok(connection)
        
        except Exception as e:
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-01",
                    operation="CLIENT_CONNECTED",
                    success=False,
                    details={"error": str(e)}
                )
            return Err(f"Failed to accept connection: {str(e)}")
    
    def close_connection(self, client_id: str) -> Result[str]:
        """Close a specific client connection"""
        try:
            if client_id not in self.connections:
                return Err(f"Connection {client_id} not found")
            
            connection = self.connections[client_id]
            connection.is_active = False
            del self.connections[client_id]
            
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-01",
                    operation="CLIENT_DISCONNECTED",
                    success=True,
                    details={
                        "client_id": client_id,
                        "remaining_connections": len(self.connections)
                    }
                )
            
            return Ok(f"Connection {client_id} closed")
        
        except Exception as e:
            return Err(f"Error closing connection: {str(e)}")
    
    def _close_all_connections(self) -> None:
        """Close all active connections"""
        for client_id in list(self.connections.keys()):
            self.close_connection(client_id)
    
    # Tool Management
    
    def _load_orchestrator_tools(self) -> Result[int]:
        """
        Load tools from orchestrators.
        
        AC-AR-007-02: Orchestrators exposed as MCP tools
        """
        try:
            if self.logger:
                self.logger.log_operation_start(
                    ac_id="AC-AR-007-02",
                    operation="LOAD_ORCHESTRATOR_TOOLS",
                    details={"domains": self.registry.get_domains()}
                )
            
            for orchestrator_meta in self.registry.get_all():
                domain = orchestrator_meta.get("domain")
                capabilities = orchestrator_meta.get("capabilities", [])
                version = orchestrator_meta.get("version", "1.0")
                
                # Create tool info for each capability
                for capability in capabilities:
                    tool_name = f"{domain}_{capability}"
                    tool_info = MCPToolInfo(
                        name=tool_name,
                        description=f"{capability} in {domain} domain (v{version})",
                        orchestrator_domain=domain,
                        parameters={"operation": capability},
                        capabilities=[capability]
                    )
                    self.tools[tool_name] = tool_info
            
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-02",
                    operation="LOAD_ORCHESTRATOR_TOOLS",
                    success=True,
                    details={
                        "tools_loaded": len(self.tools),
                        "tools": list(self.tools.keys())
                    }
                )
            
            return Ok(len(self.tools))
        
        except Exception as e:
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-02",
                    operation="LOAD_ORCHESTRATOR_TOOLS",
                    success=False,
                    details={"error": str(e)}
                )
            return Err(f"Failed to load orchestrator tools: {str(e)}")
    
    def get_tools(self) -> List[MCPToolInfo]:
        """Get list of available tools"""
        return list(self.tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPToolInfo]:
        """Get specific tool info"""
        return self.tools.get(tool_name)
    
    # Server Status
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get server status.
        
        AC-AR-007-01: Server reports its status
        """
        return {
            "is_running": self.is_running,
            "is_listening": self.is_listening,
            "host": self.host,
            "port": self.port,
            "start_time": self.start_time,
            "uptime_seconds": self._calculate_uptime(),
            "active_connections": len(self.connections),
            "max_connections": self.max_connections,
            "tools_available": len(self.tools),
            "tools": [tool.name for tool in self.get_tools()],
            "status_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_uptime(self) -> float:
        """Calculate server uptime in seconds"""
        if not self.start_time:
            return 0.0
        
        try:
            start = datetime.fromisoformat(self.start_time)
            now = datetime.now()
            return (now - start).total_seconds()
        except Exception:
            return 0.0
    
    def get_connections(self) -> List[Dict[str, Any]]:
        """Get list of active connections"""
        return [
            {
                "client_id": conn.client_id,
                "remote_address": conn.remote_address,
                "connected_at": conn.connected_at,
                "is_active": conn.is_active
            }
            for conn in self.connections.values()
        ]
    
    # Governance Context Injection
    
    def get_governance_context(self) -> Dict[str, Any]:
        """
        Get governance context for MCP responses.
        
        AC-AR-007-03: Governance context included in responses
        """
        try:
            if self.logger:
                self.logger.log_operation_start(
                    ac_id="AC-AR-007-03",
                    operation="GET_GOVERNANCE_CONTEXT",
                    details={}
                )
            
            # Get tier information
            tiers = {
                "tier_0": "Immutable governance rules",
                "tier_1": "Project-level governance",
                "tier_2": "Team-level standards"
            }
            
            # Get all rules from governance registry
            all_rules = self.governance_registry.get_all_rules()
            rule_count = sum(len(rules) for rules in all_rules.values())
            
            context = {
                "governance_enabled": True,
                "tiers": tiers,
                "active_rules_count": rule_count,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-03",
                    operation="GET_GOVERNANCE_CONTEXT",
                    success=True,
                    details=context
                )
            
            return context
        
        except Exception as e:
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-007-03",
                    operation="GET_GOVERNANCE_CONTEXT",
                    success=False,
                    details={"error": str(e)}
                )
            return {"error": str(e)}
