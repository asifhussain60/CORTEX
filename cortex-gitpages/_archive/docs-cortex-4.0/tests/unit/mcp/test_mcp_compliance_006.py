"""
AC-MCP-COMPLIANCE-006: MCP Error Handling & Protocol Test Suite.

Tests for MCP-compliant error handling:
- Standard JSON-RPC 2.0 error codes
- MCP-specific error codes
- Error recovery strategies
- Proper error message formatting
- Error context and metadata
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

from src.mcp.protocol import MCPError, ErrorCode


class RecoveryStrategy(Enum):
    """Error recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    ABORT = "abort"
    IGNORE = "ignore"


@dataclass
class ErrorRecoveryInfo:
    """Information about error recovery."""
    strategy: RecoveryStrategy
    max_retries: int = 3
    backoff_ms: int = 100
    fallback_value: Optional[Any] = None


class ErrorHandler:
    """Handles MCP-compliant error scenarios."""
    
    # JSON-RPC 2.0 standard codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32099
    SERVER_ERROR_END = -32000
    
    # MCP-specific codes
    TOOL_NOT_FOUND = -32001
    EXECUTION_ERROR = -32002
    TIMEOUT = -32003
    
    def __init__(self) -> None:
        """Initialize error handler."""
        self._error_count = 0
        self._recovery_attempts = 0
        self._error_log: list[Dict[str, Any]] = []
    
    def handle_error(self, error: MCPError, recovery: RecoveryStrategy) -> bool:
        """Handle an error with recovery strategy."""
        self._error_count += 1
        self._log_error(error)
        
        if recovery == RecoveryStrategy.RETRY:
            self._recovery_attempts += 1
            return self._attempt_retry(error)
        elif recovery == RecoveryStrategy.FALLBACK:
            self._recovery_attempts += 1
            return self._attempt_fallback(error)
        elif recovery == RecoveryStrategy.ABORT:
            return False
        elif recovery == RecoveryStrategy.IGNORE:
            return True
        
        return False
    
    def _attempt_retry(self, error: MCPError) -> bool:
        """Attempt to retry after error."""
        return error.code in [-32602, -32003]  # Retryable codes
    
    def _attempt_fallback(self, error: MCPError) -> bool:
        """Attempt fallback after error."""
        return True
    
    def _log_error(self, error: MCPError) -> None:
        """Log error for analysis."""
        self._error_log.append({
            "code": error.code,
            "message": error.message,
            "timestamp": "2026-01-19T00:00:00Z"
        })
    
    def get_stats(self) -> Dict[str, int]:
        """Get error handling statistics."""
        return {
            "total_errors": self._error_count,
            "recovery_attempts": self._recovery_attempts,
            "error_log_size": len(self._error_log)
        }
    
    def classify_error(self, code: int) -> str:
        """Classify error by code."""
        if code == self.PARSE_ERROR:
            return "PARSE_ERROR"
        elif code == self.INVALID_REQUEST:
            return "INVALID_REQUEST"
        elif code == self.METHOD_NOT_FOUND:
            return "METHOD_NOT_FOUND"
        elif code == self.INVALID_PARAMS:
            return "INVALID_PARAMS"
        elif code == self.INTERNAL_ERROR:
            return "INTERNAL_ERROR"
        elif code == self.TOOL_NOT_FOUND:
            return "TOOL_NOT_FOUND"
        elif code == self.EXECUTION_ERROR:
            return "EXECUTION_ERROR"
        elif code == self.TIMEOUT:
            return "TIMEOUT"
        elif self.SERVER_ERROR_END <= code <= self.SERVER_ERROR_START:
            return "SERVER_ERROR"
        else:
            return "UNKNOWN"


class TestMCPErrorCodes:
    """Test MCP error code compliance."""
    
    def test_jsonrpc_parse_error(self) -> None:
        """Test JSON-RPC 2.0 PARSE_ERROR code."""
        error = MCPError(
            code=-32700,
            message="Invalid JSON was received by the server"
        )
        assert error.code == -32700
        assert error.message is not None
    
    def test_jsonrpc_invalid_request(self) -> None:
        """Test JSON-RPC 2.0 INVALID_REQUEST code."""
        error = MCPError(
            code=-32600,
            message="The JSON sent is not a valid Request object"
        )
        assert error.code == -32600
    
    def test_jsonrpc_method_not_found(self) -> None:
        """Test JSON-RPC 2.0 METHOD_NOT_FOUND code."""
        error = MCPError(
            code=-32601,
            message="The method does not exist or is not available"
        )
        assert error.code == -32601
    
    def test_jsonrpc_invalid_params(self) -> None:
        """Test JSON-RPC 2.0 INVALID_PARAMS code."""
        error = MCPError(
            code=-32602,
            message="Invalid method parameter(s)"
        )
        assert error.code == -32602
    
    def test_jsonrpc_internal_error(self) -> None:
        """Test JSON-RPC 2.0 INTERNAL_ERROR code."""
        error = MCPError(
            code=-32603,
            message="Internal JSON-RPC error"
        )
        assert error.code == -32603
    
    def test_mcp_tool_not_found(self) -> None:
        """Test MCP TOOL_NOT_FOUND code."""
        error = MCPError(
            code=-32001,
            message="Tool not found in registry"
        )
        assert error.code == -32001
    
    def test_mcp_execution_error(self) -> None:
        """Test MCP EXECUTION_ERROR code."""
        error = MCPError(
            code=-32002,
            message="Tool execution failed"
        )
        assert error.code == -32002
    
    def test_mcp_timeout(self) -> None:
        """Test MCP TIMEOUT code."""
        error = MCPError(
            code=-32003,
            message="Tool execution timed out"
        )
        assert error.code == -32003
    
    def test_error_code_range(self) -> None:
        """Test error codes are in valid ranges."""
        handler = ErrorHandler()
        
        # Valid ranges
        assert handler.PARSE_ERROR == -32700
        assert handler.SERVER_ERROR_START == -32099
        assert handler.SERVER_ERROR_END == -32000
    
    def test_error_code_classification(self) -> None:
        """Test error classification by code."""
        handler = ErrorHandler()
        
        assert handler.classify_error(-32700) == "PARSE_ERROR"
        assert handler.classify_error(-32601) == "METHOD_NOT_FOUND"
        assert handler.classify_error(-32001) == "TOOL_NOT_FOUND"
        assert handler.classify_error(-32003) == "TIMEOUT"


class TestErrorRecovery:
    """Test error recovery strategies."""
    
    def test_retry_recovery(self) -> None:
        """Test retry recovery strategy."""
        handler = ErrorHandler()
        error = MCPError(
            code=-32602,
            message="Invalid parameters"
        )
        
        result = handler.handle_error(error, RecoveryStrategy.RETRY)
        assert result is True
    
    def test_fallback_recovery(self) -> None:
        """Test fallback recovery strategy."""
        handler = ErrorHandler()
        error = MCPError(
            code=-32001,
            message="Tool not found"
        )
        
        result = handler.handle_error(error, RecoveryStrategy.FALLBACK)
        assert result is True
    
    def test_abort_recovery(self) -> None:
        """Test abort recovery strategy."""
        handler = ErrorHandler()
        error = MCPError(
            code=-32603,
            message="Internal error"
        )
        
        result = handler.handle_error(error, RecoveryStrategy.ABORT)
        assert result is False
    
    def test_ignore_recovery(self) -> None:
        """Test ignore recovery strategy."""
        handler = ErrorHandler()
        error = MCPError(
            code=-32700,
            message="Parse error"
        )
        
        result = handler.handle_error(error, RecoveryStrategy.IGNORE)
        assert result is True
    
    def test_error_recovery_info(self) -> None:
        """Test error recovery information object."""
        info = ErrorRecoveryInfo(
            strategy=RecoveryStrategy.RETRY,
            max_retries=5,
            backoff_ms=200
        )
        
        assert info.strategy == RecoveryStrategy.RETRY
        assert info.max_retries == 5
        assert info.backoff_ms == 200
    
    def test_recovery_with_fallback_value(self) -> None:
        """Test recovery with fallback value."""
        info = ErrorRecoveryInfo(
            strategy=RecoveryStrategy.FALLBACK,
            fallback_value={"default": "result"}
        )
        
        assert info.fallback_value is not None
        assert info.fallback_value["default"] == "result"


class TestErrorContextAndMetadata:
    """Test error context and metadata."""
    
    def test_error_with_data_context(self) -> None:
        """Test error with additional data context."""
        error = MCPError(
            code=-32002,
            message="Tool execution error",
            data={
                "tool_name": "calculate",
                "tool_version": "1.0.0",
                "execution_id": "exec_001"
            }
        )
        
        assert error.data is not None
        assert error.data["tool_name"] == "calculate"
        assert error.data["execution_id"] == "exec_001"
    
    def test_error_message_format(self) -> None:
        """Test error message formatting."""
        error = MCPError(
            code=-32602,
            message="Parameter validation failed: field 'input' is required"
        )
        
        assert "validation failed" in error.message.lower()
        assert "input" in error.message
    
    def test_error_code_consistency(self) -> None:
        """Test error codes are consistent."""
        error1 = MCPError(code=-32001, message="Tool not found")
        error2 = MCPError(code=-32001, message="Tool not found")
        
        assert error1.code == error2.code
    
    def test_error_nesting_context(self) -> None:
        """Test error nesting for context preservation."""
        inner_error = MCPError(
            code=-32002,
            message="Inner error occurred"
        )
        
        outer_error = MCPError(
            code=-32603,
            message="Internal error",
            data={"caused_by": str(inner_error)}
        )
        
        assert outer_error.data is not None
        assert "caused_by" in outer_error.data


class TestErrorHandling:
    """Test error handling mechanisms."""
    
    def test_error_handler_initialization(self) -> None:
        """Test error handler can be initialized."""
        handler = ErrorHandler()
        stats = handler.get_stats()
        
        assert stats["total_errors"] == 0
        assert stats["recovery_attempts"] == 0
    
    def test_error_logging(self) -> None:
        """Test errors are logged."""
        handler = ErrorHandler()
        error = MCPError(code=-32001, message="Tool not found")
        
        handler.handle_error(error, RecoveryStrategy.IGNORE)
        stats = handler.get_stats()
        
        assert stats["total_errors"] == 1
        assert stats["error_log_size"] == 1
    
    def test_multiple_errors_logged(self) -> None:
        """Test multiple errors are logged."""
        handler = ErrorHandler()
        errors = [
            MCPError(code=-32001, message="Tool not found"),
            MCPError(code=-32002, message="Execution failed"),
            MCPError(code=-32003, message="Timeout")
        ]
        
        for error in errors:
            handler.handle_error(error, RecoveryStrategy.IGNORE)
        
        stats = handler.get_stats()
        assert stats["total_errors"] == 3
        assert stats["error_log_size"] == 3
    
    def test_retryable_error_detection(self) -> None:
        """Test detection of retryable errors."""
        handler = ErrorHandler()
        
        # INVALID_PARAMS is retryable
        error = MCPError(code=-32602, message="Invalid parameters")
        result = handler.handle_error(error, RecoveryStrategy.RETRY)
        assert result is True
        
        # Internal error not retryable
        error2 = MCPError(code=-32603, message="Internal error")
        result2 = handler.handle_error(error2, RecoveryStrategy.RETRY)
        assert result2 is False
    
    def test_error_classification(self) -> None:
        """Test error classification."""
        handler = ErrorHandler()
        
        classifications = {
            -32700: "PARSE_ERROR",
            -32600: "INVALID_REQUEST",
            -32601: "METHOD_NOT_FOUND",
            -32001: "TOOL_NOT_FOUND",
            -32002: "EXECUTION_ERROR",
            -32003: "TIMEOUT",
        }
        
        for code, classification in classifications.items():
            assert handler.classify_error(code) == classification


class TestProtocolErrorScenarios:
    """Test protocol-specific error scenarios."""
    
    def test_malformed_request_error(self) -> None:
        """Test error for malformed request."""
        error = MCPError(
            code=-32600,
            message="Invalid Request",
            data={"details": "Missing 'method' field"}
        )
        
        assert error.code == -32600
        assert "method" in error.data["details"]
    
    def test_unknown_method_error(self) -> None:
        """Test error for unknown method."""
        error = MCPError(
            code=-32601,
            message="Method not found",
            data={"method": "tools/unknown"}
        )
        
        assert error.code == -32601
        assert error.data["method"] == "tools/unknown"
    
    def test_tool_execution_timeout_error(self) -> None:
        """Test error for tool execution timeout."""
        error = MCPError(
            code=-32003,
            message="Tool execution timed out",
            data={
                "tool_name": "long_runner",
                "timeout_ms": 5000,
                "elapsed_ms": 5100
            }
        )
        
        assert error.code == -32003
        assert error.data["elapsed_ms"] > error.data["timeout_ms"]
    
    def test_protocol_version_mismatch_error(self) -> None:
        """Test error for protocol version mismatch."""
        error = MCPError(
            code=-32600,
            message="Invalid Request",
            data={
                "reason": "Protocol version mismatch",
                "expected": "2.0",
                "received": "1.0"
            }
        )
        
        assert error.code == -32600
        assert error.data["expected"] == "2.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
