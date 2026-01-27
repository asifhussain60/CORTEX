"""MCP Server SDK

Author: CORTEX Framework
"""

import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union

@dataclass
class MCPRequest:
    """MCP SDK request following JSON-RPC 2.0 format."""
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None
    jsonrpc: str = "2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for JSON-RPC 2.0 format.
        
        Returns:
            dict: JSON-RPC 2.0 formatted request
        """
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
        }
        
        # Only include params if provided
        if self.params is not None:
            result["params"] = self.params
        
        # Only include id if provided (notifications have no id)
        if self.id is not None:
            result["id"] = self.id
        
        return result
    
    def to_json(self) -> str:
        """Convert request to JSON string.
        
        Returns:
            str: JSON string representation
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "MCPRequest":
        """Create request from JSON string.
        
        Args:
            json_str: JSON string to parse
            
        Returns:
            MCPRequest: Parsed request
        """
        data = json.loads(json_str)
        return cls(
            method=data["method"],
            params=data.get("params"),
            id=data.get("id"),
            jsonrpc=data.get("jsonrpc", "2.0")
        )


@dataclass
class MCPResponse:
    """MCP SDK response following JSON-RPC 2.0 format."""
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Union[str, int]] = None
    jsonrpc: str = "2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for JSON-RPC 2.0 format.
        
        Returns:
            dict: JSON-RPC 2.0 formatted response
        """
        response = {
            "jsonrpc": self.jsonrpc,
        }
        
        # Include either result or error (not both)
        if self.error is not None:
            response["error"] = self.error
        else:
            response["result"] = self.result
        
        # Include id if provided
        if self.id is not None:
            response["id"] = self.id
        
        return response
    
    def to_json(self) -> str:
        """Convert response to JSON string.
        
        Returns:
            str: JSON string representation
        """
        return json.dumps(self.to_dict())


class MCPServer:
    """MCP server SDK."""
    
    def handle(self, request: MCPRequest) -> dict:
        """Handle MCP request."""
        return {"status": "ok"}


class CORTEXMCPServer(MCPServer):
    """CORTEX MCP server."""
    
    def __init__(self):
        super().__init__()

__all__ = ["MCPRequest", "MCPResponse", "MCPServer", "CORTEXMCPServer"]
