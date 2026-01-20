"""MCP Error Handling - Protocol-compliant error handling and recovery."""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.mcp.protocol import ErrorCode, MCPError

@dataclass
class ErrorRecoveryStrategy:
    """Error recovery strategy."""
    retry: bool = False
    retry_count: int = 0
    retry_after_ms: int = 1000
    exponential_backoff: bool = False
    fallback_option: Optional[str] = None

class MCPErrorHandler:
    """MCP Protocol-compliant error handling."""
    
    # Error code mapping
    EXCEPTION_TO_ERROR_CODE = {
        ValueError: ErrorCode.INVALID_PARAMS,
        TypeError: ErrorCode.INVALID_PARAMS,
        KeyError: ErrorCode.INVALID_PARAMS,
        TimeoutError: ErrorCode.TIMEOUT,
        NotImplementedError: ErrorCode.UNSUPPORTED,
        RuntimeError: ErrorCode.INTERNAL_ERROR,
    }
    
    # Recovery strategies per error code
    RECOVERY_STRATEGIES = {
        ErrorCode.TIMEOUT: ErrorRecoveryStrategy(
            retry=True,
            retry_count=3,
            retry_after_ms=2000,
            exponential_backoff=True
        ),
        ErrorCode.INTERNAL_ERROR: ErrorRecoveryStrategy(
            retry=True,
            retry_count=2,
            retry_after_ms=5000
        ),
        ErrorCode.INVALID_PARAMS: ErrorRecoveryStrategy(
            retry=False
        ),
        ErrorCode.TOOL_NOT_FOUND: ErrorRecoveryStrategy(
            retry=False
        ),
    }
    
    @staticmethod
    def handle_exception(exception: Exception, context: Optional[Dict[str, Any]] = None) -> MCPError:
        """Handle exception and convert to MCP error."""
        error_code = MCPErrorHandler._get_error_code(exception)
        message = MCPErrorHandler._format_error_message(exception, error_code)
        
        data = {}
        if context:
            data["context"] = context
        
        # Add recovery info
        recovery = MCPErrorHandler.get_recovery_strategy(error_code)
        if recovery and recovery.retry:
            data["recovery"] = {
                "retry": recovery.retry,
                "retry_count": recovery.retry_count,
                "retry_after_ms": recovery.retry_after_ms,
                "exponential_backoff": recovery.exponential_backoff
            }
        
        return MCPError(
            code=error_code,
            message=message,
            data=data if data else None
        )
    
    @staticmethod
    def _get_error_code(exception: Exception) -> ErrorCode:
        """Map exception type to error code."""
        exc_type = type(exception)
        if exc_type in MCPErrorHandler.EXCEPTION_TO_ERROR_CODE:
            return MCPErrorHandler.EXCEPTION_TO_ERROR_CODE[exc_type]
        return ErrorCode.INTERNAL_ERROR
    
    @staticmethod
    def _format_error_message(exception: Exception, error_code: ErrorCode) -> str:
        """Format error message for MCP response."""
        message = str(exception)
        
        if error_code == ErrorCode.INVALID_PARAMS:
            return f"Invalid parameters: {message}"
        elif error_code == ErrorCode.TIMEOUT:
            return f"Execution timeout: {message}"
        elif error_code == ErrorCode.INTERNAL_ERROR:
            return f"Internal error: {message}"
        
        return message
    
    @staticmethod
    def get_recovery_strategy(error_code: ErrorCode) -> Optional[ErrorRecoveryStrategy]:
        """Get recovery strategy for error code."""
        return MCPErrorHandler.RECOVERY_STRATEGIES.get(error_code)
    
    @staticmethod
    def validate_error_response(error: MCPError) -> bool:
        """Validate MCP error response structure."""
        if not error.code:
            return False
        if not error.message:
            return False
        if not isinstance(error.code, ErrorCode):
            return False
        return True

class ErrorThrottler:
    """Throttles repeated errors from same tool."""
    
    def __init__(self, threshold: int = 10, window_ms: int = 60000):
        """Initialize throttler."""
        self.threshold = threshold
        self.window_ms = window_ms
        self.error_counts: Dict[str, list] = {}  # tool_id -> [timestamps]
    
    def record_error(self, tool_id: str) -> bool:
        """Record error. Returns True if throttling is triggered."""
        now = datetime.now().timestamp() * 1000  # Convert to ms
        
        if tool_id not in self.error_counts:
            self.error_counts[tool_id] = []
        
        # Remove old entries outside window
        cutoff = now - self.window_ms
        self.error_counts[tool_id] = [t for t in self.error_counts[tool_id] if t > cutoff]
        
        # Add current error
        self.error_counts[tool_id].append(now)
        
        # Check if threshold exceeded
        return len(self.error_counts[tool_id]) > self.threshold
    
    def get_error_rate(self, tool_id: str) -> float:
        """Get error rate for tool."""
        if tool_id not in self.error_counts or not self.error_counts[tool_id]:
            return 0.0
        
        now = datetime.now().timestamp() * 1000
        cutoff = now - self.window_ms
        recent_errors = [t for t in self.error_counts[tool_id] if t > cutoff]
        
        # Calculate rate: errors per second
        if self.window_ms > 0:
            return (len(recent_errors) / self.window_ms) * 1000
        return 0.0
    
    def is_throttled(self, tool_id: str) -> bool:
        """Check if tool is currently throttled."""
        return tool_id in self.error_counts and len(self.error_counts[tool_id]) > self.threshold
    
    def reset(self, tool_id: Optional[str] = None) -> None:
        """Reset throttle counters."""
        if tool_id:
            if tool_id in self.error_counts:
                del self.error_counts[tool_id]
        else:
            self.error_counts.clear()
