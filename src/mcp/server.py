"""
Model Context Protocol (MCP) v1.0 Server Implementation.

This module provides a lightweight MCP server for universal orchestrator invocation.
Implements protocol v1.0 specification with request/response handling, tool registration,
and error propagation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import time
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPVersion(str, Enum):
    """Supported MCP protocol versions."""
    V1_0 = "1.0"


class RequestStatus(str, Enum):
    """Request processing status."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class MCPRequest:
    """MCP protocol request structure."""
    version: str
    tool: str
    parameters: Dict[str, Any]
    request_id: Optional[str] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class MCPResponse:
    """MCP protocol response structure."""
    status: str
    tool: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: Optional[float] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class MCPServer:
    """
    MCP v1.0 Protocol Server.
    
    Provides universal tool invocation interface with:
    - Tool registration and discovery
    - Request validation and routing
    - Error handling and propagation
    - Metrics collection
    - Graceful shutdown
    """
    
    def __init__(self, version: str = MCPVersion.V1_0):
        """
        Initialize MCP server.
        
        Args:
            version: MCP protocol version (default: 1.0)
        """
        self.version = version
        self.tools: Dict[str, Callable] = {}
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_execution_time": 0.0
        }
        self._running = False
        logger.info(f"MCP Server v{version} initialized")
    
    def register_tool(self, name: str, handler: Callable) -> None:
        """
        Register a tool handler.
        
        Args:
            name: Tool name (unique identifier)
            handler: Callable that processes tool requests
            
        Raises:
            ValueError: If tool name already registered
        """
        if name in self.tools:
            raise ValueError(f"Tool '{name}' already registered")
        
        self.tools[name] = handler
        logger.info(f"Registered tool: {name}")
    
    def unregister_tool(self, name: str) -> None:
        """
        Unregister a tool handler.
        
        Args:
            name: Tool name to unregister
            
        Raises:
            KeyError: If tool not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not registered")
        
        del self.tools[name]
        logger.info(f"Unregistered tool: {name}")
    
    def list_tools(self) -> list[str]:
        """
        Get list of registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def validate_request(self, request_data: Dict[str, Any]) -> MCPRequest:
        """
        Validate and parse request data.
        
        Args:
            request_data: Raw request dictionary
            
        Returns:
            Parsed MCPRequest object
            
        Raises:
            ValueError: If request is malformed
        """
        # Check required fields
        required_fields = ["version", "tool", "parameters"]
        missing = [f for f in required_fields if f not in request_data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        
        # Validate version
        if request_data["version"] != self.version:
            raise ValueError(
                f"Unsupported protocol version: {request_data['version']} "
                f"(server supports {self.version})"
            )
        
        # Validate tool exists
        if request_data["tool"] not in self.tools:
            raise ValueError(
                f"Unknown tool: {request_data['tool']} "
                f"(available: {', '.join(self.list_tools())})"
            )
        
        # Validate parameters is dict
        if not isinstance(request_data["parameters"], dict):
            raise ValueError("Parameters must be a dictionary")
        
        return MCPRequest(
            version=request_data["version"],
            tool=request_data["tool"],
            parameters=request_data["parameters"],
            request_id=request_data.get("request_id"),
            timestamp=request_data.get("timestamp")
        )
    
    def handle_request(self, request_data: Dict[str, Any]) -> MCPResponse:
        """
        Handle an MCP request.
        
        Args:
            request_data: Request dictionary conforming to MCP protocol
            
        Returns:
            MCPResponse with result or error
        """
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # Validate request
            request = self.validate_request(request_data)
            logger.info(
                f"Processing request: {request.tool} "
                f"(id: {request.request_id or 'none'})"
            )
            
            # Get tool handler
            handler = self.tools[request.tool]
            
            # Execute tool
            try:
                result = handler(**request.parameters)
                execution_time = time.time() - start_time
                
                # Update metrics
                self.metrics["successful_requests"] += 1
                self.metrics["total_execution_time"] += execution_time
                
                response = MCPResponse(
                    status=RequestStatus.SUCCESS,
                    tool=request.tool,
                    result=result,
                    request_id=request.request_id,
                    execution_time=execution_time
                )
                
                logger.info(
                    f"Request completed: {request.tool} "
                    f"({execution_time:.3f}s)"
                )
                
                return response
                
            except Exception as e:
                # Tool execution error
                execution_time = time.time() - start_time
                error_msg = f"Tool execution failed: {str(e)}"
                logger.error(f"{error_msg} ({request.tool})", exc_info=True)
                
                self.metrics["failed_requests"] += 1
                
                return MCPResponse(
                    status=RequestStatus.ERROR,
                    tool=request.tool,
                    error=error_msg,
                    request_id=request.request_id,
                    execution_time=execution_time
                )
        
        except ValueError as e:
            # Request validation error
            execution_time = time.time() - start_time
            error_msg = f"Invalid request: {str(e)}"
            logger.error(error_msg)
            
            self.metrics["failed_requests"] += 1
            
            return MCPResponse(
                status=RequestStatus.ERROR,
                tool=request_data.get("tool", "unknown"),
                error=error_msg,
                request_id=request_data.get("request_id"),
                execution_time=execution_time
            )
        
        except Exception as e:
            # Unexpected error
            execution_time = time.time() - start_time
            error_msg = f"Server error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            self.metrics["failed_requests"] += 1
            
            return MCPResponse(
                status=RequestStatus.ERROR,
                tool=request_data.get("tool", "unknown"),
                error=error_msg,
                request_id=request_data.get("request_id"),
                execution_time=execution_time
            )
    
    def start(self) -> None:
        """Start the MCP server."""
        if self._running:
            logger.warning("Server already running")
            return
        
        self._running = True
        logger.info(f"MCP Server started (v{self.version})")
        logger.info(f"Registered tools: {', '.join(self.list_tools())}")
    
    def stop(self) -> None:
        """Stop the MCP server gracefully."""
        if not self._running:
            logger.warning("Server not running")
            return
        
        self._running = False
        logger.info("MCP Server stopped")
        logger.info(f"Final metrics: {self.get_metrics()}")
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get server metrics.
        
        Returns:
            Dictionary with request statistics
        """
        metrics = self.metrics.copy()
        
        # Calculate average execution time
        if metrics["successful_requests"] > 0:
            metrics["average_execution_time"] = (
                metrics["total_execution_time"] / metrics["successful_requests"]
            )
        else:
            metrics["average_execution_time"] = 0.0
        
        # Calculate success rate
        if metrics["total_requests"] > 0:
            metrics["success_rate"] = (
                metrics["successful_requests"] / metrics["total_requests"]
            )
        else:
            metrics["success_rate"] = 0.0
        
        return metrics
    
    def reset_metrics(self) -> None:
        """Reset server metrics to zero."""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_execution_time": 0.0
        }
        logger.info("Metrics reset")


# Decorator for tool registration
def mcp_tool(func: Callable) -> Callable:
    """
    Decorator to mark a function as an MCP tool.
    
    Usage:
        @mcp_tool
        def my_tool(param1: str, param2: int) -> dict:
            return {"result": "success"}
    """
    func._is_mcp_tool = True
    return func
