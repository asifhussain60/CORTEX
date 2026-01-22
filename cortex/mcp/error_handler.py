"""MCP Error Handler - Error handling and recovery for MCP operations.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorRecoveryStrategy(Enum):
    """Error recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    IGNORE = "ignore"


@dataclass
class ErrorResponse:
    """Error response object."""
    code: str  # Will be set from ErrorCode enum
    message: str


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    
    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_attempted: bool = False
    recovery_successful: bool = False


class ErrorThrottler:
    """Throttles error reporting to prevent flooding."""
    
    def __init__(self, max_errors_per_minute: int = 10, threshold: Optional[int] = None):
        """Initialize error throttler.
        
        Args:
            max_errors_per_minute: Maximum errors to report per minute
            threshold: Threshold for recording errors per tool
        """
        self.max_errors = max_errors_per_minute
        self.threshold = threshold if threshold is not None else max_errors_per_minute
        self.error_timestamps: List[datetime] = []
        self.error_counts: Dict[str, int] = {}  # error_type -> count
    
    def should_report(self, error_type: str) -> bool:
        """Check if error should be reported.
        
        Args:
            error_type: Type of error
            
        Returns:
            True if error should be reported, False if throttled
        """
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Remove old timestamps
        self.error_timestamps = [ts for ts in self.error_timestamps if ts > cutoff]
        
        if len(self.error_timestamps) < self.max_errors:
            self.error_timestamps.append(now)
            return True
        
        return False
    
    def record_error(self, error_type: str) -> bool:
        """Record an error and check if threshold exceeded.
        
        Args:
            error_type: Type or ID of error
            
        Returns:
            True if threshold exceeded, False otherwise
        """
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        
        self.error_counts[error_type] += 1
        
        # Return True when threshold is exceeded
        return self.error_counts[error_type] > self.threshold
    
    def get_error_rate(self, error_type: str) -> float:
        """Get error rate for a specific error type.
        
        Args:
            error_type: Type or ID of error
            
        Returns:
            Error rate (count / threshold)
        """
        count = self.error_counts.get(error_type, 0)
        return count / self.threshold if self.threshold > 0 else 0.0
    
    def is_throttled(self, error_type: str) -> bool:
        """Check if an error type is currently throttled.
        
        Args:
            error_type: Type or ID of error
            
        Returns:
            True if throttled, False otherwise
        """
        count = self.error_counts.get(error_type, 0)
        return count > self.threshold
    
    def reset(self, error_type: Optional[str] = None) -> None:
        """Reset throttler state.
        
        Args:
            error_type: Specific error type to reset, or None to reset all
        """
        if error_type is None:
            self.error_timestamps.clear()
            self.error_counts.clear()
        else:
            if error_type in self.error_counts:
                del self.error_counts[error_type]


class MCPErrorHandler:
    """Handles errors in MCP operations with recovery strategies."""
    
    def __init__(self):
        """Initialize error handler."""
        self.error_history: List[ErrorRecord] = []
        self.throttler = ErrorThrottler()
        self.recovery_strategies: Dict[str, ErrorRecoveryStrategy] = {}
        self.max_retry_attempts = 3
    
    def register_strategy(self, error_type: str, strategy: ErrorRecoveryStrategy) -> None:
        """Register a recovery strategy for an error type.
        
        Args:
            error_type: Type of error
            strategy: Recovery strategy to use
        """
        self.recovery_strategies[error_type] = strategy
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ) -> bool:
        """Handle an error with appropriate recovery strategy.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            severity: Severity level of the error
            
        Returns:
            True if error was handled successfully, False otherwise
        """
        error_type = type(error).__name__
        
        # Create error record
        record = ErrorRecord(
            error_type=error_type,
            message=str(error),
            severity=severity,
            context=context or {}
        )
        
        # Check throttling
        if not self.throttler.should_report(error_type):
            logger.debug(f"Error throttled: {error_type}")
            return False
        
        # Add to history
        self.error_history.append(record)
        
        # Get recovery strategy
        strategy = self.recovery_strategies.get(error_type, ErrorRecoveryStrategy.RETRY)
        
        # Attempt recovery
        record.recovery_attempted = True
        success = self._attempt_recovery(error, strategy, context)
        record.recovery_successful = success
        
        return success
    
    def _attempt_recovery(
        self,
        error: Exception,
        strategy: ErrorRecoveryStrategy,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Attempt error recovery using specified strategy.
        
        Args:
            error: The exception
            strategy: Recovery strategy
            context: Error context
            
        Returns:
            True if recovery successful
        """
        if strategy == ErrorRecoveryStrategy.RETRY:
            return self._retry_operation(context)
        elif strategy == ErrorRecoveryStrategy.FALLBACK:
            return self._use_fallback(context)
        elif strategy == ErrorRecoveryStrategy.CIRCUIT_BREAK:
            return self._circuit_break(context)
        else:  # IGNORE
            return True
    
    def _retry_operation(self, context: Optional[Dict[str, Any]]) -> bool:
        """Retry the operation.
        
        Args:
            context: Operation context
            
        Returns:
            True if retry successful
        """
        # Stub implementation
        logger.info("Retry operation (stub)")
        return False
    
    def _use_fallback(self, context: Optional[Dict[str, Any]]) -> bool:
        """Use fallback strategy.
        
        Args:
            context: Operation context
            
        Returns:
            True if fallback successful
        """
        logger.info("Using fallback strategy (stub)")
        return True
    
    def _circuit_break(self, context: Optional[Dict[str, Any]]) -> bool:
        """Trigger circuit breaker.
        
        Args:
            context: Operation context
            
        Returns:
            True if circuit breaker triggered
        """
        logger.warning("Circuit breaker triggered (stub)")
        return True
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error history.
        
        Returns:
            Dictionary with error statistics
        """
        total_errors = len(self.error_history)
        by_type = {}
        by_severity = {}
        recovered = sum(1 for r in self.error_history if r.recovery_successful)
        
        for record in self.error_history:
            by_type[record.error_type] = by_type.get(record.error_type, 0) + 1
            by_severity[record.severity.value] = by_severity.get(record.severity.value, 0) + 1
        
        return {
            "total_errors": total_errors,
            "by_type": by_type,
            "by_severity": by_severity,
            "recovered": recovered,
            "recovery_rate": recovered / total_errors if total_errors > 0 else 0
        }
    
    @staticmethod
    def handle_exception(exc: Exception) -> ErrorResponse:
        """Handle an exception and return appropriate error response.
        
        Args:
            exc: The exception to handle
            
        Returns:
            ErrorResponse with appropriate error code
        """
        from cortex.mcp.protocol import ErrorCode
        
        error_map = {
            ValueError: ErrorCode.INVALID_PARAMS,
            TypeError: ErrorCode.INVALID_PARAMS,
            TimeoutError: ErrorCode.TIMEOUT,
            KeyError: ErrorCode.NOT_FOUND,
            PermissionError: ErrorCode.UNAUTHORIZED,
            RuntimeError: ErrorCode.EXECUTION_ERROR,
        }
        
        error_code = error_map.get(type(exc), ErrorCode.INTERNAL_ERROR)
        
        response = ErrorResponse(
            code=error_code.value,
            message=str(exc)
        )
        response.code = error_code
        return response


__all__ = ["MCPErrorHandler", "ErrorThrottler", "ErrorRecoveryStrategy", "ErrorSeverity", "ErrorRecord", "ErrorResponse"]
