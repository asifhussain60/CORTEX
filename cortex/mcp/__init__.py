"""
CORTEX MCP Module: Model Context Protocol Implementation.

MCP v2.0 ARCHITECTURE (WAVE-100):
    All new code should use cortex.mcp.v2 which provides:
    - 24 consolidated production tools (75% reduction from 98)
    - Business capability alignment
    - Cross-platform support
    - Comprehensive test coverage

    Usage:
        from cortex.mcp.v2 import MCPServerV2
        from cortex.mcp.v2.tools import CortexProcessRequest

LEGACY v1 (deprecated - kept for backward compatibility):
    The original MCP implementation is still available but deprecated.
    Existing code will continue to work.

Exports (v2 - recommended):
    MCPServerV2: MCP v2 server with 24 production tools
    
Exports (v1 - deprecated):
    MCPServer: Original MCP server (use MCPServerV2 instead)
    Tool: Abstract base class for MCP tools
    ToolDefinition: Tool definition data model
    ToolParameter: Tool parameter definition
    MCPRequest: JSON-RPC request model
    MCPResponse: JSON-RPC response model
    MCPError: JSON-RPC error model
    MCPToolsCatalog: Unified MCP tools registry (CORE-035 SSOT)
    get_mcp_tools_catalog: Get catalog singleton
    sync_mcp_tools: Sync tools from orchestrators
    OrchestratorMCPServer: Unified MCP facade for orchestrators
    get_orchestrator_mcp_server: Get orchestrator server singleton
"""

# ===========================================================================
# MCP v2 (RECOMMENDED) - Import first for fast access
# ===========================================================================
from cortex.mcp import v2
from cortex.mcp.v2 import MCPServerV2
from cortex.mcp.v2.base import ToolCategory as ToolCategoryV2

# ===========================================================================
# MCP v1 (DEPRECATED - kept for backward compatibility)
# ===========================================================================
from cortex.mcp.decorators import MCP_TOOLS_REGISTRY, mcp_tool
from cortex.mcp.endpoints import (
    call_tool,
    filter_tools_by_domain,
    get_tool_count,
    get_tool_metadata,
    is_tool_registered,
    list_tools_endpoint,
)
from cortex.mcp.mcp_tools_catalog import (
    MCPToolMetadata,
    MCPToolsCatalog,
    ToolStatus,
    get_mcp_tools_catalog,
    sync_mcp_tools,
)
from cortex.mcp.orchestrator_mcp_server import (
    CapabilityMetadata,
    CapabilityRequest,
    CapabilityResponse,
    ContextType,
    ExecutionContext,
    IOrchestratorAdapter,
    OrchestratorMCPServer,
    get_orchestrator_mcp_server,
)
from cortex.mcp.server import (
    MCPError,
    MCPRequest,
    MCPResponse,
    MCPServer,
    SampleTool,
    Tool,
    ToolDefinition,
    ToolParameter,
)
from cortex.mcp.unified_tool_discovery import (
    MCPTool,
    ToolCategory,
    UnifiedMCPToolDiscovery,
    get_unified_discovery,
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
    # Unified tool discovery (AC-MCP-CENTRALIZED-DISCOVERY - CORE-035)
    "UnifiedMCPToolDiscovery",
    "get_unified_discovery",
    "MCPTool",
    "ToolCategory",
]
