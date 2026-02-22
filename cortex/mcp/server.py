"""
MCP Server: Consolidated, Production-Ready Implementation.

This is the SINGLE entry point for ALL CORTEX functionality.
Implements JSON-RPC 2.0 compliant MCP protocol with:
- 24 production tools (WAVE-100 consolidation)
- Cross-platform support (macOS, Windows, Linux)
- Extensible architecture
- Comprehensive error handling
"""

import json
import logging
import sys
import time
import asyncio
import inspect
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import os

from cortex.mcp.mcp_tool_base import Tool, ToolResult, ToolCategory
from cortex.mcp.mcp_registry import ToolRegistry, get_registry


# ============================================================================
# MCP PROTOCOL DATA STRUCTURES
# ============================================================================

@dataclass
class MCPRequest:
    """JSON-RPC 2.0 MCP Request."""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    
    @classmethod
    def from_json(cls: object, data: str) -> "MCPRequest":
        """Parse JSON-RPC request."""
        parsed = json.loads(data)
        return cls(
            jsonrpc=parsed.get("jsonrpc", "2.0"),
            method=parsed.get("method", ""),
            params=parsed.get("params", {}),
            id=parsed.get("id"),
        )


@dataclass
class MCPResponse:
    """JSON-RPC 2.0 MCP Response."""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        response = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return json.dumps(response, default=str)


# ============================================================================
# MCP SERVER
# ============================================================================

class MCPServer:
    """
    CORTEX MCP Server - Consolidated Production Server.
    
    Features:
    - 24 production tools (WAVE-100 consolidation)
    - Cross-platform support
    - JSON-RPC 2.0 compliance
    - Extensible tool registration
    - Comprehensive logging
    
    Usage:
        # As stdio server (for VS Code)
        server = MCPServer()
        server.run_stdio()
        
        # Programmatic invocation
        server = MCPServer()
        result = server.call_tool("cortex.lens", operation="analyze", target=".")
    """
    
    # JSON-RPC error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    def __init__(self, registry: Optional[ToolRegistry] = None) -> None:
        """
        Initialize MCP Server v2.
        
        Args:
            registry: Tool registry (uses global if not provided)
        """
        self.logger = logging.getLogger(__name__)
        self.registry = registry or get_registry()
        self._start_time = datetime.utcnow()
        
        self.logger.info(f"MCP Server v2 initialized with {self.registry.tool_count} tools")
    
    # ========================================================================
    # TOOL DISCOVERY (tools/list)
    # ========================================================================
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools in MCP schema format.
        
        Returns:
            List of tool definitions
        """
        return self.registry.to_mcp_schema()
    
    def list_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        List tools filtered by category.
        
        Args:
            category: Category name (core, intelligence, governance, operations, utilities)
            
        Returns:
            List of tool definitions in category
        """
        try:
            cat_enum = ToolCategory(category)
            tools = self.registry.list_by_category(cat_enum)
            return [
                {
                    "name": t.id,
                    "description": t.description,
                    "category": t.category.value,
                    "operations": t.operations,
                }
                for t in tools
            ]
        except ValueError:
            return []
    
    # ========================================================================
    # TOOL EXECUTION (tools/call)
    # ========================================================================
    
    def call_tool(self, tool_name: str, **params: Any) -> ToolResult:
        """
        Execute a tool by name.
        
        ENFORCEMENT: Injects orchestrator_context={'source': 'MasterOrchestrator'} 
        into all tool calls to enforce routing validation.
        
        Args:
            tool_name: Tool identifier
            **params: Tool parameters
            
        Returns:
            ToolResult with success/error and data
        """
        start_time = time.time()
        
        # PHASE 4: Inject orchestrator context into all tool calls
        # This ensures all tools validate routing through MasterOrchestrator
        params['orchestrator_context'] = {
            'source': 'MasterOrchestrator',
            'timestamp': datetime.now().isoformat(),
            'tool_name': tool_name
        }
        
        # Get tool implementation
        tool = self.registry.get(tool_name)
        
        if tool is None:
            # Check if tool exists in metadata (not yet implemented)
            metadata = self.registry.get_metadata(tool_name)
            if metadata:
                return ToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' is defined but not yet implemented",
                    metadata={"available_operations": metadata.operations}
                )
            return ToolResult(
                success=False,
                error=f"Unknown tool: {tool_name}",
                metadata={"available_tools": [t.id for t in self.registry.list_all()]}
            )
        
        # Validate parameters
        validation_error = tool.validate_params(**params)
        if validation_error:
            return ToolResult(
                success=False,
                error=validation_error
            )
        
        # Execute tool
        try:
            result = tool.execute(**params)
            
            # Handle async coroutines
            if inspect.iscoroutine(result):
                try:
                    loop = asyncio.get_running_loop()
                    # If we're already in an async context, schedule it
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        result = pool.submit(asyncio.run, result).result()
                except RuntimeError:
                    # No running loop, use asyncio.run
                    result = asyncio.run(result)
            
            # Add execution metadata
            result.metadata["execution_time_ms"] = int((time.time() - start_time) * 1000)
            result.metadata["tool"] = tool_name
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Tool execution failed: {tool_name}")
            return ToolResult(
                success=False,
                error=f"Execution failed: {str(e)}",
                metadata={"tool": tool_name, "execution_time_ms": int((time.time() - start_time) * 1000)}
            )
    
    # ========================================================================
    # JSON-RPC PROTOCOL
    # ========================================================================
    
    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle a JSON-RPC MCP request.
        
        Args:
            request: Parsed MCP request
            
        Returns:
            MCP response
        """
        try:
            method = request.method
            params = request.params
            
            # Route to appropriate handler
            if method == "tools/list":
                result = self.list_tools()
                return MCPResponse(result=result, id=request.id)
            
            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_params = params.get("arguments", {})
                
                tool_result = self.call_tool(tool_name, **tool_params)
                
                # Format response according to MCP protocol
                # Must have 'content' array with text items
                mcp_result = {
                    "content": [
                        {
                            "type": "text",
                            "text": tool_result.to_json()
                        }
                    ]
                }
                
                return MCPResponse(result=mcp_result, id=request.id)
            
            elif method == "initialize":
                # MCP initialization handshake
                return MCPResponse(
                    result={
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": False},
                        },
                        "serverInfo": {
                            "name": "cortex-mcp",
                            "version": "2.0.0",
                        },
                    },
                    id=request.id
                )
            
            elif method == "notifications/initialized":
                # Client confirmed initialization
                return MCPResponse(result={"status": "ready"}, id=request.id)
            
            else:
                return MCPResponse(
                    error={
                        "code": self.METHOD_NOT_FOUND,
                        "message": f"Unknown method: {method}",
                    },
                    id=request.id
                )
                
        except Exception as e:
            self.logger.exception("Request handling failed")
            return MCPResponse(
                error={
                    "code": self.INTERNAL_ERROR,
                    "message": str(e),
                },
                id=request.id
            )
    
    def handle_json(self, json_str: str) -> str:
        """
        Handle raw JSON-RPC request string.
        
        Args:
            json_str: JSON-RPC request as string
            
        Returns:
            JSON-RPC response as string
        """
        try:
            request = MCPRequest.from_json(json_str)
            response = self.handle_request(request)
            return response.to_json()
        except json.JSONDecodeError as e:
            return MCPResponse(
                error={
                    "code": self.PARSE_ERROR,
                    "message": f"Parse error: {str(e)}",
                }
            ).to_json()
    
    # ========================================================================
    # STDIO TRANSPORT (for VS Code integration)
    # ========================================================================
    
    def run_stdio(self) -> None:
        """
        Run server using stdio transport.
        
        This is the primary mode for VS Code Copilot integration.
        Reads JSON-RPC requests from stdin, writes responses to stdout.
        """
        self.logger.info("MCP Server v2 starting (stdio transport)")
        
        # Print startup banner
        print(json.dumps({
            "type": "startup",
            "server": "cortex-mcp",
            "version": "2.0.0",
            "tools": self.registry.tool_count,
        }), file=sys.stderr, flush=True)
        
        while True:
            try:
                # Read line from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Process request
                response = self.handle_json(line)
                
                # Write response to stdout
                print(response, flush=True)
                
            except KeyboardInterrupt:
                self.logger.info("Server shutdown requested")
                break
            except Exception as e:
                self.logger.exception("Unexpected error in stdio loop")
                error_response = MCPResponse(
                    error={
                        "code": self.INTERNAL_ERROR,
                        "message": str(e),
                    }
                ).to_json()
                print(error_response, flush=True)
    
    # ========================================================================
    # HEALTH & DIAGNOSTICS
    # ========================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """
        Get server health status.
        
        Returns:
            Health check results
        """
        uptime = datetime.utcnow() - self._start_time
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "uptime_seconds": int(uptime.total_seconds()),
            "tools": {
                "total": self.registry.tool_count,
                "by_category": {
                    cat.value: len(self.registry.list_by_category(cat))
                    for cat in ToolCategory
                },
            },
            "platform": {
                "os": os.name,
                "python_version": sys.version,
            },
        }


# ============================================================================
# MODULE ENTRY POINT
# ============================================================================

def main() -> None:
    """Entry point for python -m cortex.mcp"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    
    # Create and run server
    server = MCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
