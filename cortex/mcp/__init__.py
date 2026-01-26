"""
CORTEX MCP Module: Model Context Protocol Implementation.

This module provides JSON-RPC 2.0 compliant Model Context Protocol for
tool management, discovery, and execution within the CORTEX system.

Exports:
    MCPServer: Main MCP protocol server
    Tool: Abstract base class for MCP tools
    ToolDefinition: Tool definition data model
    ToolParameter: Tool parameter definition
    MCPRequest: JSON-RPC request model
    MCPResponse: JSON-RPC response model
    MCPError: JSON-RPC error model
    MCPToolsCatalog: Unified MCP tools registry (CORE-035 SSOT)
    get_mcp_tools_catalog: Get catalog singleton
    sync_mcp_tools: Sync tools from orchestrators
    OrchestratorMCPServer: Unified MCP facade for orchestrators (AC-MCP-ORCHESTRATOR-001)
    get_orchestrator_mcp_server: Get orchestrator server singleton
"""

from cortex.mcp.server import (
    MCPServer,
    Tool,
    SampleTool,
    ToolDefinition,
    ToolParameter,
    MCPRequest,
    MCPResponse,
    MCPError,
)
from cortex.mcp.decorators import mcp_tool, MCP_TOOLS_REGISTRY
from cortex.mcp.endpoints import (
    list_tools_endpoint,
    get_tool_metadata,
    filter_tools_by_domain,
    get_tool_count,
    is_tool_registered,
    call_tool,
)
from cortex.mcp.mcp_tools_catalog import (
    MCPToolsCatalog,
    get_mcp_tools_catalog,
    sync_mcp_tools,
    MCPToolMetadata,
    ToolStatus,
)
from cortex.mcp.orchestrator_mcp_server import (
    OrchestratorMCPServer,
    get_orchestrator_mcp_server,
    IOrchestratorAdapter,
    ExecutionContext,
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResponse,
    ContextType,
)

__all__ = [
    # Core MCP server and tools
    "MCPServer",
    "Tool",
    "SampleTool",
    "ToolDefinition",
    "ToolParameter",
    "MCPRequest",
    "MCPResponse",
    "MCPError",
    # MCP decorators and registry
    "mcp_tool",
    "MCP_TOOLS_REGISTRY",
    # MCP endpoints
    "list_tools_endpoint",
    "get_tool_metadata",
    "filter_tools_by_domain",
    "get_tool_count",
    "is_tool_registered",
    "call_tool",
    # Unified MCP catalog (CORE-035 SSOT)
    "MCPToolsCatalog",
    "get_mcp_tools_catalog",
    "sync_mcp_tools",
    "MCPToolMetadata",
    "ToolStatus",
    # Unified orchestrator MCP server (AC-MCP-ORCHESTRATOR-001)
    "OrchestratorMCPServer",
    "get_orchestrator_mcp_server",
    "IOrchestratorAdapter",
    "ExecutionContext",
    "CapabilityMetadata",
    "CapabilityRequest",
    "CapabilityResponse",
    "ContextType",
]
