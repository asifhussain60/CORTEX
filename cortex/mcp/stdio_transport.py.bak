"""
MCP stdio Transport - JSON-RPC 2.0 over stdin/stdout.

Implements stdio transport for Model Context Protocol (MCP) allowing
Copilot to communicate with CORTEX MCP server via stdin/stdout.

Author: CORTEX Framework
"""

import sys
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def run_stdio_server(server: Any) -> int:
    """
    Run MCP server with stdio transport.
    
    Reads JSON-RPC 2.0 requests from stdin, processes via server,
    writes responses to stdout. Blocks until EOF or error.
    
    Args:
        server: MCPServer instance to handle requests
        
    Returns:
        int: Exit code (0 for success)
    """
    logger.info("Starting stdio transport (JSON-RPC 2.0)")
    
    try:
        while True:
            # Read line from stdin
            line = sys.stdin.readline()
            if not line:  # EOF
                logger.info("stdin closed, shutting down")
                break
                
            line = line.strip()
            if not line:  # Empty line
                continue
                
            try:
                # Parse JSON-RPC request
                request_data = json.loads(line)
                logger.debug(f"Received request: {request_data}")
                
                # Handle request
                response = handle_jsonrpc_request(server, request_data)
                
                # Send response if not None (notifications don't get responses)
                if response is not None:
                    response_json = json.dumps(response)
                    print(response_json)  # Write to stdout
                    sys.stdout.flush()
                    logger.debug(f"Sent response: {response}")
                    
            except json.JSONDecodeError as e:
                # Invalid JSON - send parse error
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": str(e)
                    },
                    "id": None
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                logger.warning(f"Parse error: {e}")
                
            except Exception as e:
                # Internal error
                error_response = {
                    "jsonrpc": "2.0", 
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    },
                    "id": request_data.get("id") if 'request_data' in locals() else None
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                logger.error(f"Internal error: {e}", exc_info=True)
                
        return 0
        
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down")
        return 0
    except Exception as e:
        logger.error(f"stdio transport error: {e}", exc_info=True)
        return 1


def handle_jsonrpc_request(server: Any, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Handle a JSON-RPC 2.0 request.
    
    Args:
        server: MCPServer instance
        request: JSON-RPC request dictionary
        
    Returns:
        Response dictionary or None for notifications
    """
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")
    
    # Handle MCP methods
    if method == "initialize":
        return handle_initialize(request_id, params)
    elif method == "tools/list":
        return handle_tools_list(server, request_id)
    elif method == "tools/call":
        return handle_tools_call(server, request_id, params)
    else:
        # Method not found
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": f"Unknown method: {method}"
            },
            "id": request_id
        }


def handle_initialize(request_id: Optional[str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle initialize request."""
    return {
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "CORTEX",
                "version": "7.0"
            }
        },
        "id": request_id
    }


def handle_tools_list(server: Any, request_id: Optional[str]) -> Dict[str, Any]:
    """Handle tools/list request."""
    try:
        tools = server.list_tools()
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools},
            "id": request_id
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": f"Failed to list tools: {str(e)}"
            },
            "id": request_id
        }


def handle_tools_call(server: Any, request_id: Optional[str], params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/call request."""
    try:
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": "Missing tool name"
                },
                "id": request_id
            }
        
        # Call tool via server
        response = server.call_tool(tool_name, arguments, str(request_id) if request_id else "unknown")
        
        # Convert MCPResponse to JSON-RPC response
        if response.error:
            return {
                "jsonrpc": "2.0",
                "error": response.error,
                "id": request_id
            }
        else:
            return {
                "jsonrpc": "2.0",
                "result": response.result,
                "id": request_id
            }
            
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error", 
                "data": f"Tool call failed: {str(e)}"
            },
            "id": request_id
        }