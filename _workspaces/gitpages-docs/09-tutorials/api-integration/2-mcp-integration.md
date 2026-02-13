# Tutorial: MCP Integration

**Time:** 30 minutes | **Level:** Intermediate  
**Goal:** Implement MCP server integration with CORTEX

## Overview

MCP (Model Context Protocol) is a JSON-RPC 2.0 based protocol for AI tool integration. This tutorial shows how to implement an MCP server that exposes CORTEX functionality.

## Prerequisites

- [REST Client](1-rest-client.md) tutorial completed
- Understanding of JSON-RPC 2.0
- Python 3.8+

## Step 1: Basic MCP Server

```python
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self):
        self.tools = {}
        self.register_default_tools()
    
    def register_default_tools(self):
        """Register standard CORTEX tools."""
        self.register_tool(
            name="execute_orchestrator",
            description="Execute a CORTEX orchestrator",
            parameters={
                "type": "object",
                "properties": {
                    "orchestrator": {"type": "string"},
                    "content": {"type": "string"},
                    "user_id": {"type": "string"}
                },
                "required": ["orchestrator", "content", "user_id"]
            },
            handler=self.execute_orchestrator
        )
    
    def register_tool(self, name: str, description: str, parameters: Dict, handler):
        """Register a tool."""
        self.tools[name] = {
            "description": description,
            "parameters": parameters,
            "handler": handler
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request."""
        try:
            if request.get("method") == "tools/list":
                return self.handle_list_tools()
            elif request.get("method") == "tools/call":
                return self.handle_call_tool(request)
            else:
                return {"error": "Unknown method"}
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def handle_list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        tools = [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
            for name, info in self.tools.items()
        ]
        return {"result": {"tools": tools}}
    
    def handle_call_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool."""
        tool_name = request.get("params", {}).get("name")
        tool_args = request.get("params", {}).get("arguments", {})
        
        if tool_name not in self.tools:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        tool = self.tools[tool_name]
        result = tool["handler"](**tool_args)
        
        return {"result": result}
    
    def execute_orchestrator(self, orchestrator: str, content: str, user_id: str) -> Dict[str, Any]:
        """Execute orchestrator via MCP."""
        # Implementation would call CORTEX API
        return {
            "status": "success",
            "content": f"Executed {orchestrator}",
            "user_id": user_id
        }
```

## Step 2: HTTP Server Implementation

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class MCPHandler(BaseHTTPRequestHandler):
    mcp_server = MCPServer()
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length)
        request = json.loads(request_body)
        
        response = self.mcp_server.handle_request(request)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def start_mcp_server(port: int = 8001):
    """Start MCP server."""
    server = HTTPServer(('localhost', port), MCPHandler)
    print(f"MCP Server listening on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    start_mcp_server()
```

## Step 3: Client Usage

```python
import requests

def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """Call MCP tool."""
    response = requests.post(
        "http://localhost:8001",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
    )
    response.raise_for_status()
    return response.json()

# Execute orchestrator via MCP
result = call_mcp_tool(
    "execute_orchestrator",
    {
        "orchestrator": "hello_world",
        "content": "Hello",
        "user_id": "alice"
    }
)
print(result)
```

## MCP Protocol Specification

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {}
  },
  "id": 1
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "result": {},
  "id": 1
}
```

## Best Practices

1. **Tool discovery** - Always support tools/list
2. **Error handling** - Use JSON-RPC error codes
3. **Validation** - Validate parameters before execution
4. **Logging** - Log all tool calls for debugging
5. **Versioning** - Version your MCP interface

## Next Steps

- [Batch Operations](3-batch-operations.md) - Batch processing
- [MCP Protocol Specification](../../03-api-reference/mcp-protocol/0-specification.md) - Full spec
