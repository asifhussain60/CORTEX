"""
MCP Server - Model Context Protocol Server for CORTEX

Exposes CORTEX orchestrator capabilities through MCP protocol.
Implements tools/list and tools/call methods for capability discovery and execution.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P1-T1.2
"""

import logging
from typing import Dict, Any, List, Optional
from src.mcp.capability_registry import get_capability_registry, CapabilityRegistry
from src.mcp.jsonrpc_server import JSONRPCServer


logger = logging.getLogger("cortex.mcp.server")


class MCPServer:
    """
    Model Context Protocol Server for CORTEX.
    
    Exposes orchestrator capabilities as MCP tools that can be discovered
    and invoked by MCP clients.
    
    MCP Protocol Methods:
        - tools/list: List all available tools
        - tools/call: Execute a tool with arguments
    
    Usage:
        server = MCPServer()
        
        # List tools
        tools = server.handle_tools_list({})
        
        # Call tool
        result = server.handle_tools_call({
            "name": "plan",
            "arguments": {"request": "plan user auth"}
        })
    """
    
    def __init__(
        self,
        capability_registry: Optional[CapabilityRegistry] = None,
        master_orchestrator = None
    ):
        """
        Initialize MCP server.
        
        Args:
            capability_registry: CapabilityRegistry instance (default: global singleton)
            master_orchestrator: MasterOrchestrator instance for tool execution
        """
        self.capability_registry = capability_registry or get_capability_registry()
        self.master_orchestrator = master_orchestrator
        self.jsonrpc_server = JSONRPCServer()
        
        # Register MCP methods
        self.jsonrpc_server.register_method("tools/list", self.handle_tools_list)
        self.jsonrpc_server.register_method("tools/call", self.handle_tools_call)
        
        logger.info("MCPServer initialized with capability registry")
    
    def handle_tools_list(self, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle tools/list request.
        
        Returns all available tools (capabilities) in MCP format.
        
        Args:
            params: Optional parameters (not used currently)
            
        Returns:
            Dict with "tools" key containing list of tool definitions
        """
        capabilities = self.capability_registry.list_all()
        
        tools = []
        for cap in capabilities:
            tools.append(cap.to_mcp_tool())
        
        logger.info(f"Listed {len(tools)} tools")
        
        return {
            "tools": tools
        }
    
    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/call request.
        
        Executes a tool with provided arguments by routing to the appropriate
        orchestrator.
        
        Args:
            params: Tool call parameters
                - name: Tool name
                - arguments: Tool arguments dict
                
        Returns:
            Dict with "content" key containing tool execution results
            
        Raises:
            ValueError: If tool not found or parameters invalid
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name is required")
        
        # Get capability
        capability = self.capability_registry.get(tool_name)
        if not capability:
            raise ValueError(f"Tool not found: {tool_name}")
        
        # Validate parameters
        capability.validate_parameters(arguments)
        
        # Execute via master orchestrator
        if self.master_orchestrator:
            # Build request string for orchestrator
            # Format: "{tool_name} {arguments_as_text}"
            request_parts = [tool_name]
            for key, value in arguments.items():
                request_parts.append(f"{key}: {value}")
            request = " ".join(request_parts)
            
            logger.info(f"Executing tool '{tool_name}' via orchestrator")
            result = self.master_orchestrator.handle_request(request)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }
        else:
            # No orchestrator available - return mock response
            logger.warning(f"No orchestrator available for tool '{tool_name}'")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool '{tool_name}' called with arguments: {arguments}"
                    }
                ]
            }
    
    def start(self):
        """
        Start MCP server (stdio transport).
        
        Runs the JSON-RPC server loop reading from stdin and writing to stdout.
        """
        from src.mcp.jsonrpc_server import StdioTransport
        
        transport = StdioTransport()
        logger.info("MCP Server starting (stdio transport)")
        
        try:
            while True:
                # Read message from stdin
                raw_message = transport.read_message()
                if not raw_message:
                    break
                
                # Handle via JSON-RPC server
                response = self.jsonrpc_server.handle_message(raw_message)
                
                # Write response if not a notification
                if response is not None:
                    transport.write_message(response.to_json())
        
        except KeyboardInterrupt:
            logger.info("MCP Server shutting down (KeyboardInterrupt)")
        except Exception as e:
            logger.error(f"MCP Server error: {e}", exc_info=True)
        finally:
            transport.close()
            logger.info("MCP Server stopped")


# Entry point for running as standalone MCP server
if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        stream=sys.stderr  # Log to stderr, stdout is for JSON-RPC
    )
    
    print("CORTEX MCP Server starting...", file=sys.stderr)
    print("Protocol: JSON-RPC 2.0 over stdio", file=sys.stderr)
    print("Available tools: tools/list", file=sys.stderr)
    print("Execute tool: tools/call", file=sys.stderr)
    
    # Create and start server
    server = MCPServer()
    server.start()
