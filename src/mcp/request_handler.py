"""
MCP Request/Response Handler

Comprehensive request/response handling for MCP protocol including:
- Request validation and context management
- Response formatting (success, error, partial)
- Error handling and timeout management
- Streaming responses and progress callbacks
- Request metrics and caching
- Async support

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P1-T1.3
"""

import logging
import time
import hashlib
import json
import asyncio
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


logger = logging.getLogger("cortex.mcp.request_handler")


class ErrorCode(str, Enum):
    """MCP error codes"""
    INVALID_REQUEST = "invalid_request"
    INVALID_PARAMS = "invalid_params"
    METHOD_NOT_FOUND = "method_not_found"
    INTERNAL_ERROR = "internal_error"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"


class ValidationError(Exception):
    """Request validation error"""
    pass


@dataclass
class MCPRequest:
    """MCP request with context"""
    method: str
    params: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())


@dataclass
class MCPResponse:
    """MCP response"""
    status: str
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    request_id: Optional[str] = None
    duration_ms: float = 0.0
    from_cache: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {"status": self.status}
        
        if self.result is not None:
            data["result"] = self.result
        
        if self.error is not None:
            data["error"] = self.error
        
        if self.request_id:
            data["request_id"] = self.request_id
        
        if self.duration_ms:
            data["duration_ms"] = self.duration_ms
        
        if self.from_cache:
            data["from_cache"] = self.from_cache
        
        return data
    
    @classmethod
    def success(cls, result: Any, request_id: Optional[str] = None) -> "MCPResponse":
        """Create success response"""
        return cls(status="success", result=result, request_id=request_id)
    
    @classmethod
    def error(cls, code: ErrorCode, message: str, request_id: Optional[str] = None) -> "MCPResponse":
        """Create error response"""
        return cls(
            status="error",
            error={"code": code, "message": message},
            error_message=message,
            request_id=request_id
        )
    
    @classmethod
    def partial(cls, data: Any, request_id: Optional[str] = None) -> "MCPResponse":
        """Create partial/streaming response"""
        return cls(status="partial", result=data, request_id=request_id)


class RequestValidator:
    """Request validator"""
    
    VALID_METHODS = [
        "tools/list",
        "tools/call",
        "initialize",
        "ping"
    ]
    
    def validate(self, request: Dict[str, Any]) -> bool:
        """
        Validate request structure.
        
        Args:
            request: Request dict
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if "method" not in request:
            raise ValidationError("Missing required field: method")
        
        if not self.validate_method(request["method"]):
            raise ValidationError(f"Invalid method: {request['method']}")
        
        return True
    
    def validate_method(self, method: str) -> bool:
        """Validate method name"""
        return method in self.VALID_METHODS
    
    def validate_params(self, params: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate parameters against JSON Schema.
        
        Args:
            params: Parameters to validate
            schema: JSON Schema
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        required = schema.get("required", [])
        
        for field in required:
            if field not in params:
                raise ValidationError(f"Missing required parameter: {field}")
        
        # Type validation
        properties = schema.get("properties", {})
        for param_name, param_value in params.items():
            if param_name in properties:
                expected_type = properties[param_name].get("type")
                if expected_type == "string" and not isinstance(param_value, str):
                    raise ValidationError(f"Parameter '{param_name}' must be string")
                elif expected_type == "integer" and not isinstance(param_value, int):
                    raise ValidationError(f"Parameter '{param_name}' must be integer")
        
        return True


class RequestMetrics:
    """Request metrics collector"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_duration_ms = 0.0
    
    def record_request(self, success: bool, duration_ms: float):
        """Record request metrics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.total_duration_ms += duration_ms
    
    def get_stats(self) -> Dict[str, Any]:
        """Get metrics statistics"""
        avg_duration = self.total_duration_ms / self.total_requests if self.total_requests > 0 else 0
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            "average_duration_ms": avg_duration
        }


class ResponseCache:
    """Response cache"""
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.ttl = ttl
    
    def generate_key(self, request: Dict[str, Any]) -> str:
        """
        Generate cache key from request.
        
        Args:
            request: Request dict
            
        Returns:
            Cache key string
        """
        # Create deterministic key from method and params
        key_data = {
            "method": request.get("method"),
            "params": request.get("params", {})
        }
        key_json = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_json.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached response"""
        if key in self.cache:
            response, timestamp = self.cache[key]
            # Check TTL
            if time.time() - timestamp < self.ttl:
                return response
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, response: Any):
        """Cache response"""
        self.cache[key] = (response, time.time())
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()


class RequestHandler:
    """
    MCP request handler.
    
    Handles request validation, orchestrator execution, error handling,
    and response formatting.
    """
    
    def __init__(
        self,
        master_orchestrator=None,
        timeout: Optional[float] = None,
        progress_callback: Optional[Callable] = None,
        metrics: Optional[RequestMetrics] = None,
        cache: Optional[ResponseCache] = None
    ):
        """
        Initialize request handler.
        
        Args:
            master_orchestrator: MasterOrchestrator instance
            timeout: Request timeout in seconds
            progress_callback: Callback for progress updates
            metrics: RequestMetrics instance
            cache: ResponseCache instance
        """
        self.master_orchestrator = master_orchestrator
        self.timeout = timeout
        self.progress_callback = progress_callback
        self.validator = RequestValidator()
        self.metrics = metrics or RequestMetrics()
        self.cache = cache
        self.partial_count = 0
    
    def handle(self, request: Dict[str, Any]) -> MCPResponse:
        """
        Handle a request.
        
        Args:
            request: Request dict
            
        Returns:
            MCPResponse
        """
        start_time = time.time()
        request_id = request.get("id", str(uuid.uuid4()))
        
        try:
            # Validation
            self.validator.validate(request)
            
            # Check cache if enabled
            if self.cache and request.get("cache", False):
                cache_key = self.cache.generate_key(request)
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    cached_response.from_cache = True
                    return cached_response
            
            # Validate tools/call parameters
            if request["method"] == "tools/call":
                params = request.get("params", {})
                if "name" not in params:
                    raise ValidationError("Missing required parameter: name")
                if "arguments" not in params:
                    raise ValidationError("Missing required parameter: arguments")
            
            # Send progress if callback available
            if self.progress_callback:
                self.progress_callback({"status": "processing", "request_id": request_id})
            
            # Execute via orchestrator
            if self.master_orchestrator:
                # Build request string with context
                context = request.get("context", {})
                method = request["method"]
                params = request.get("params", {})
                
                # Execute with timeout
                if self.timeout:
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Request timeout")
                    
                    try:
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(int(self.timeout))
                        
                        result = self.master_orchestrator.handle_request(
                            json.dumps(params) if method == "tools/call" else method
                        )
                        
                        signal.alarm(0)  # Cancel alarm
                    except TimeoutError:
                        duration_ms = (time.time() - start_time) * 1000
                        self.metrics.record_request(False, duration_ms)
                        return MCPResponse.error(
                            code=ErrorCode.TIMEOUT,
                            message=f"Request timeout after {self.timeout}s",
                            request_id=request_id
                        )
                else:
                    result = self.master_orchestrator.handle_request(
                        json.dumps(params) if method == "tools/call" else method
                    )
            else:
                result = {"message": "No orchestrator available"}
            
            # Create success response
            duration_ms = (time.time() - start_time) * 1000
            response = MCPResponse.success(result=result, request_id=request_id)
            response.duration_ms = duration_ms
            
            # Cache if enabled
            if self.cache and request.get("cache", False):
                cache_key = self.cache.generate_key(request)
                self.cache.set(cache_key, response)
            
            # Record metrics
            self.metrics.record_request(True, duration_ms)
            
            return response
            
        except ValidationError as e:
            duration_ms = (time.time() - start_time) * 1000
            self.metrics.record_request(False, duration_ms)
            raise
        
        except Exception as e:
            logger.error(f"Request handling error: {e}", exc_info=True)
            duration_ms = (time.time() - start_time) * 1000
            self.metrics.record_request(False, duration_ms)
            return MCPResponse.error(
                code=ErrorCode.INTERNAL_ERROR,
                message=str(e),
                request_id=request_id
            )
    
    def send_partial(self, data: Any, request_id: str):
        """
        Send partial/streaming response.
        
        Args:
            data: Partial data
            request_id: Request ID
        """
        self.partial_count += 1
        
        if self.progress_callback:
            self.progress_callback({
                "type": "partial",
                "data": data,
                "request_id": request_id
            })


class AsyncRequestHandler(RequestHandler):
    """Async request handler"""
    
    async def handle_async(self, request: Dict[str, Any]) -> MCPResponse:
        """
        Handle request asynchronously.
        
        Args:
            request: Request dict
            
        Returns:
            MCPResponse
        """
        # Run synchronous handler in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.handle, request)
