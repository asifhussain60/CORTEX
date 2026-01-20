"""
MCP Protocol Server - MCP Implementation with stdio transport.

Implements Model Context Protocol v2024-11-05 specification for communication
with Claude Desktop, VS Code, and other MCP clients.

Transport: stdio (JSON-RPC 2.0)
Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)

AC-MCP-001-01: MCP SDK Server Implementation

Note: Uses custom JSON-RPC implementation as fallback for Python 3.9 compatibility
when mcp>=1.0.0 (requires Python 3.10+) is not available.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Callable, Union
import logging
from dataclasses import dataclass

from src.mcp.decorator import get_registered_tools, get_tool


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr to avoid interfering with stdio protocol
)
logger = logging.getLogger("cortex-mcp-server")


@dataclass
class MCPRequest:
    """JSON-RPC 2.0 request."""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[int, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d: Dict[str, Any] = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.params is not None:
            d["params"] = self.params
        if self.id is not None:
            d["id"] = self.id
        return d
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, data: str) -> "MCPRequest":
        """Create from JSON string."""
        d = json.loads(data)
        return cls(
            jsonrpc=d.get("jsonrpc", "2.0"),
            method=d.get("method", ""),
            params=d.get("params"),
            id=d.get("id")
        )


@dataclass
class MCPResponse:
    """JSON-RPC 2.0 response."""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[int, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d: Dict[str, Any] = {"jsonrpc": self.jsonrpc}
        if self.result is not None:
            d["result"] = self.result
        if self.error is not None:
            d["error"] = self.error
        if self.id is not None:
            d["id"] = self.id
        return d
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class CORTEXMCPServer:
    """
    CORTEX MCP Server with JSON-RPC 2.0 and stdio transport.
    
    Features:
    - JSON-RPC 2.0 message protocol
    - Stdio-based communication (no TCP)
    - Dynamic tool discovery
    - Parameter validation
    - Error handling and recovery
    """
    
    def __init__(self, server_name: str = "cortex-mcp", server_version: str = "1.0.0"):
        """
        Initialize CORTEX MCP Server.
        
        Args:
            server_name: Name of the server
            server_version: Version string (semver)
        """
        self.server_name = server_name
        self.server_version = server_version
        self.server: Optional[Any] = None  # Placeholder for future SDK integration
    
    async def handle_initialize(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle initialize request.
        
        Args:
            params: Request parameters
        
        Returns:
            Server capabilities
        """
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": self.server_name,
                "version": self.server_version
            }
        }
    
    async def handle_tools_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle tools/list request.
        
        Args:
            params: Request parameters
        
        Returns:
            List of available tools
        """
        tools: List[Dict[str, Any]] = []
        
        for tool_name, metadata in get_registered_tools().items():
            tool: Dict[str, Any] = {
                "name": tool_name,
                "description": metadata.description,
                "inputSchema": metadata.parameters
            }
            tools.append(tool)
        
        logger.info(f"Listed {len(tools)} tools")
        return {"tools": tools}
    
    async def handle_tools_call(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle tools/call request.
        
        Args:
            params: Request parameters with 'name' and 'arguments'
        
        Returns:
            Tool execution result
        """
        if not params:
            raise ValueError("Missing parameters")
        
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        metadata = get_tool(tool_name)
        if not metadata or not metadata.func:
            error_msg = f"Tool '{tool_name}' not found"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # Call the tool function
            result = metadata.func(**arguments)
            
            # Convert result to JSON-serializable format
            if isinstance(result, str):
                result_text = result
            elif isinstance(result, (dict, list)):
                result_text = json.dumps(result)
            else:
                result_text = str(result) if result is not None else ""
            
            logger.info(f"Tool '{tool_name}' executed successfully")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
        
        except TypeError as e:
            error_msg = f"Invalid parameters for '{tool_name}': {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error executing '{tool_name}': {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle a JSON-RPC request.
        
        Args:
            request: MCPRequest
        
        Returns:
            MCPResponse
        """
        try:
            if request.method == "initialize":
                result = await self.handle_initialize(request.params)
            elif request.method == "tools/list":
                result = await self.handle_tools_list(request.params)
            elif request.method == "tools/call":
                result = await self.handle_tools_call(request.params)
            else:
                raise ValueError(f"Unknown method: {request.method}")
            
            return MCPResponse(
                result=result,
                id=request.id
            )
        
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return MCPResponse(
                error={
                    "code": -32603,
                    "message": str(e)
                },
                id=request.id
            )
    
    async def run(self) -> None:
        """
        Run the MCP server reading from stdin and writing to stdout.
        
        This method implements JSON-RPC 2.0 protocol over stdio.
        """
        logger.info(f"Starting {self.server_name} v{self.server_version}")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Get stdin and stdout as async streams
            reader, _ = await loop.connect_read_pipe(
                lambda: asyncio.StreamReaderProtocol(asyncio.StreamReader()),
                sys.stdin.buffer
            )
            _, writer = await loop.connect_write_pipe(
                lambda: asyncio.StreamWriter(None, None, None, None),
                sys.stdout.buffer
            )
            
            # Read and process JSON-RPC messages
            while True:
                try:
                    line = await reader.readline()
                    if not line:
                        break
                    
                    # Parse JSON-RPC request
                    request_data = json.loads(line.decode())
                    request = MCPRequest(
                        jsonrpc=request_data.get("jsonrpc", "2.0"),
                        method=request_data.get("method", ""),
                        params=request_data.get("params"),
                        id=request_data.get("id")
                    )
                    
                    # Handle request
                    response = await self.handle_request(request)
                    
                    # Send response
                    response_json = response.to_json() + "\n"
                    writer.write(response_json.encode())
                    await writer.drain()
                
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {str(e)}")
                    error_response = MCPResponse(
                        error={"code": -32700, "message": "Parse error"}
                    )
                    writer.write((error_response.to_json() + "\n").encode())
                    await writer.drain()
        
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("Server stopped")


async def main() -> None:
    """Entry point for MCP server."""
    server = CORTEXMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
