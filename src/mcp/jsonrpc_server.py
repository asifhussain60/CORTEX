"""
JSON-RPC 2.0 Server Implementation for Model Context Protocol (MCP)

Implements JSON-RPC 2.0 specification for MCP server communication.
Supports request/response, notifications, batch requests, and stdio transport.

Specification: https://www.jsonrpc.org/specification
MCP Protocol: https://modelcontextprotocol.io/

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P1-T1.1
"""

import json
import sys
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import IntEnum
import logging


logger = logging.getLogger("cortex.mcp.jsonrpc")


class JSONRPCErrorCode(IntEnum):
    """Standard JSON-RPC 2.0 error codes"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # Server error range: -32000 to -32099


@dataclass
class JSONRPCError:
    """JSON-RPC 2.0 error object"""
    code: int
    message: str
    data: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-RPC error dict"""
        result = {
            "code": self.code,
            "message": self.message
        }
        if self.data is not None:
            result["data"] = self.data
        return result


@dataclass
class JSONRPCRequest:
    """JSON-RPC 2.0 request message"""
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    id: Optional[Union[str, int]] = None
    jsonrpc: str = "2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-RPC request dict"""
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method
        }
        if self.params is not None:
            result["params"] = self.params
        if self.id is not None:
            result["id"] = self.id
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


@dataclass
class JSONRPCResponse:
    """JSON-RPC 2.0 response message"""
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None
    id: Optional[Union[str, int]] = None
    jsonrpc: str = "2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-RPC response dict"""
        response = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.error is not None:
            response["error"] = self.error.to_dict()
        else:
            response["result"] = self.result
        return response
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


@dataclass
class JSONRPCNotification:
    """JSON-RPC 2.0 notification message (no id, no response expected)"""
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    jsonrpc: str = "2.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-RPC notification dict"""
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method
        }
        if self.params is not None:
            result["params"] = self.params
        # Notifications MUST NOT include "id"
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class JSONRPCServer:
    """
    JSON-RPC 2.0 Server
    
    Handles JSON-RPC 2.0 protocol messages, method routing, and error handling.
    Supports both single requests and batch requests.
    
    Usage:
        server = JSONRPCServer()
        server.register_method("echo", lambda params: params)
        
        response = server.handle_message('{"jsonrpc": "2.0", "method": "echo", "params": {"msg": "hi"}, "id": 1}')
        print(response.to_json())
    """
    
    def __init__(self):
        self.methods: Dict[str, Callable] = {}
        logger.info("JSONRPCServer initialized")
    
    def register_method(self, name: str, handler: Callable[[Optional[Any]], Any]):
        """
        Register a method handler
        
        Args:
            name: Method name
            handler: Callable that takes params and returns result
        """
        self.methods[name] = handler
        logger.debug(f"Registered method: {name}")
    
    def parse_request(self, raw_message: str) -> JSONRPCRequest:
        """
        Parse raw JSON string into JSONRPCRequest
        
        Args:
            raw_message: Raw JSON string
            
        Returns:
            JSONRPCRequest object
            
        Raises:
            json.JSONDecodeError: If JSON is invalid
            ValueError: If required fields are missing
        """
        data = json.loads(raw_message)
        
        if not isinstance(data, dict):
            raise ValueError("Request must be a JSON object")
        
        if data.get("jsonrpc") != "2.0":
            raise ValueError("Missing or invalid 'jsonrpc' field")
        
        if "method" not in data:
            raise ValueError("Missing 'method' field")
        
        return JSONRPCRequest(
            method=data["method"],
            params=data.get("params"),
            id=data.get("id"),
            jsonrpc=data["jsonrpc"]
        )
    
    def _handle_single_request(self, request: JSONRPCRequest) -> Optional[JSONRPCResponse]:
        """
        Handle a single JSON-RPC request
        
        Args:
            request: Parsed JSONRPCRequest
            
        Returns:
            JSONRPCResponse or None (for notifications)
        """
        # Check if this is a notification (no id)
        is_notification = request.id is None
        
        # Check if method exists
        if request.method not in self.methods:
            if is_notification:
                # Notifications don't return responses even for errors
                logger.warning(f"Notification for unknown method: {request.method}")
                return None
            return JSONRPCResponse(
                error=JSONRPCError(
                    code=JSONRPCErrorCode.METHOD_NOT_FOUND,
                    message=f"Method not found: {request.method}"
                ),
                id=request.id
            )
        
        # Call method handler
        try:
            handler = self.methods[request.method]
            result = handler(request.params)
            
            if is_notification:
                # Notifications don't return responses
                return None
            
            return JSONRPCResponse(
                result=result,
                id=request.id
            )
            
        except Exception as e:
            logger.error(f"Error executing method {request.method}: {e}", exc_info=True)
            
            if is_notification:
                # Notifications don't return responses even for errors
                return None
            
            return JSONRPCResponse(
                error=JSONRPCError(
                    code=JSONRPCErrorCode.INTERNAL_ERROR,
                    message=str(e)
                ),
                id=request.id
            )
    
    def handle_message(self, raw_message: str) -> Optional[JSONRPCResponse]:
        """
        Handle a single JSON-RPC message
        
        Args:
            raw_message: Raw JSON string
            
        Returns:
            JSONRPCResponse or None (for notifications or parse errors with no id)
        """
        try:
            request = self.parse_request(raw_message)
            return self._handle_single_request(request)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return JSONRPCResponse(
                error=JSONRPCError(
                    code=JSONRPCErrorCode.PARSE_ERROR,
                    message=f"Parse error: {str(e)}"
                ),
                id=None  # No id available
            )
            
        except ValueError as e:
            logger.error(f"Invalid request: {e}")
            return JSONRPCResponse(
                error=JSONRPCError(
                    code=JSONRPCErrorCode.INVALID_REQUEST,
                    message=f"Invalid Request: {str(e)}"
                ),
                id=None  # May not have valid id
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return JSONRPCResponse(
                error=JSONRPCError(
                    code=JSONRPCErrorCode.INTERNAL_ERROR,
                    message=f"Internal error: {str(e)}"
                ),
                id=None
            )
    
    def handle_batch(self, raw_message: str) -> List[JSONRPCResponse]:
        """
        Handle a batch of JSON-RPC requests
        
        Args:
            raw_message: Raw JSON array string
            
        Returns:
            List of JSONRPCResponse objects (excludes None responses from notifications)
        """
        try:
            data = json.loads(raw_message)
            
            if not isinstance(data, list):
                raise ValueError("Batch request must be a JSON array")
            
            if len(data) == 0:
                raise ValueError("Batch request cannot be empty")
            
            responses = []
            for item in data:
                # Convert each item to JSON string for individual handling
                item_json = json.dumps(item)
                response = self.handle_message(item_json)
                
                # Only include responses (notifications return None)
                if response is not None:
                    responses.append(response)
            
            return responses
            
        except json.JSONDecodeError as e:
            logger.error(f"Batch JSON parse error: {e}")
            return [JSONRPCResponse(
                error=JSONRPCError(
                    code=JSONRPCErrorCode.PARSE_ERROR,
                    message=f"Parse error: {str(e)}"
                ),
                id=None
            )]
            
        except ValueError as e:
            logger.error(f"Invalid batch request: {e}")
            return [JSONRPCResponse(
                error=JSONRPCError(
                    code=JSONRPCErrorCode.INVALID_REQUEST,
                    message=f"Invalid Request: {str(e)}"
                ),
                id=None
            )]


class StdioTransport:
    """
    Stdio Transport Layer for MCP
    
    Handles communication via stdin/stdout using newline-delimited JSON messages.
    This is the standard transport for Model Context Protocol servers.
    
    Protocol:
        - Each message is a single line (newline-delimited)
        - Messages are JSON-RPC 2.0 formatted
        - Server reads from stdin, writes to stdout
    
    Usage:
        transport = StdioTransport()
        
        while True:
            message = transport.read_message()
            if not message:
                break
            # Process message...
            transport.write_message(response_json)
    """
    
    def __init__(self, stdin=None, stdout=None):
        """
        Initialize stdio transport
        
        Args:
            stdin: Input stream (default: sys.stdin)
            stdout: Output stream (default: sys.stdout)
        """
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        logger.info("StdioTransport initialized")
    
    def read_message(self) -> Optional[str]:
        """
        Read one message from stdin
        
        Returns:
            Message string or None if EOF
        """
        try:
            line = self.stdin.readline()
            if not line:
                return None
            return line.rstrip('\n\r')
        except Exception as e:
            logger.error(f"Error reading from stdin: {e}")
            return None
    
    def write_message(self, message: str):
        """
        Write one message to stdout
        
        Args:
            message: Message string (newline will be added)
        """
        try:
            self.stdout.write(message + '\n')
            self.stdout.flush()
        except Exception as e:
            logger.error(f"Error writing to stdout: {e}")
    
    def close(self):
        """Close stdin and stdout"""
        try:
            if hasattr(self.stdin, 'close'):
                self.stdin.close()
            if hasattr(self.stdout, 'close'):
                self.stdout.close()
            logger.info("StdioTransport closed")
        except Exception as e:
            logger.error(f"Error closing transport: {e}")


# Example usage
if __name__ == "__main__":
    # Create server
    server = JSONRPCServer()
    
    # Register some example methods
    server.register_method("ping", lambda params: {"pong": True})
    server.register_method("echo", lambda params: params)
    server.register_method("add", lambda params: params["a"] + params["b"])
    
    # Create stdio transport
    transport = StdioTransport()
    
    print("JSON-RPC 2.0 Server ready (stdio transport)", file=sys.stderr)
    print("Send newline-delimited JSON-RPC messages", file=sys.stderr)
    print("Example: {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}", file=sys.stderr)
    
    # Message loop
    try:
        while True:
            raw_message = transport.read_message()
            if not raw_message:
                break
            
            # Handle message
            response = server.handle_message(raw_message)
            
            # Send response (if not a notification)
            if response is not None:
                transport.write_message(response.to_json())
    
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
    finally:
        transport.close()
