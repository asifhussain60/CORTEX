"""
Error Handler for CORTEX 4.0 Orchestrators

Provides centralized error handling with:
- Exception classification and logging
- Recovery strategy determination
- Retry logic
- Error aggregation and reporting
- Context preservation

Supports:
- Orchestrator-level errors
- Phase-level errors
- Configuration errors
- External service errors (MCP, Brain, etc.)
"""

import logging
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"              # Warning, doesn't prevent execution
    MEDIUM = "medium"        # Error, may allow continued execution
    HIGH = "high"            # Critical error, should stop execution
    CRITICAL = "critical"    # Fatal error, requires immediate attention


class ErrorCategory(Enum):
    """Error categories for classification."""
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    PHASE_EXECUTION = "phase_execution"
    BRAIN_TIER = "brain_tier"
    MCP_GATEWAY = "mcp_gateway"
    TEMPLATE = "template"
    EXTERNAL_SERVICE = "external_service"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for an error."""
    orchestrator_name: str
    phase_name: Optional[str] = None
    operation: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Error:
    """Error information."""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    traceback_str: Optional[str] = None
    recoverable: bool = True
    retry_count: int = 0
    max_retries: int = 3
    
    @property
    def should_retry(self) -> bool:
        """Check if error should be retried."""
        return self.recoverable and self.retry_count < self.max_retries
    
    @property
    def is_critical(self) -> bool:
        """Check if error is critical."""
        return self.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]


class OrchestratorError(Exception):
    """Base exception for orchestrator errors."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        super().__init__(message)
        self.severity = severity
        self.timestamp = datetime.now()


class PhaseError(OrchestratorError):
    """Exception for phase-specific errors."""
    
    def __init__(self, phase_name: str, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        super().__init__(f"Phase '{phase_name}' error: {message}", severity)
        self.phase_name = phase_name


class ConfigurationError(OrchestratorError):
    """Exception for configuration errors."""
    
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}", ErrorSeverity.HIGH)


class OrchestratorErrorHandler:
    """
    Centralized error handling for orchestrators.
    
    Features:
    - Exception classification and logging
    - Recovery strategy determination
    - Retry logic with backoff
    - Error aggregation and reporting
    - Context preservation
    
    Usage:
        handler = OrchestratorErrorHandler(orchestrator_name="MaintenanceOrchestrator")
        
        try:
            # Orchestrator logic
            pass
        except Exception as e:
            error = handler.handle_exception(e, phase_name="cleanup")
            if error.should_retry:
                # Retry logic
                pass
    """
    
    def __init__(self, orchestrator_name: str, max_retries: int = 3):
        """
        Initialize error handler.
        
        Args:
            orchestrator_name: Name of orchestrator using this handler
            max_retries: Default maximum retry attempts
        """
        self.orchestrator_name = orchestrator_name
        self.max_retries = max_retries
        self.errors: List[Error] = []
        self.logger = logging.getLogger(f"cortex.orchestrators.{orchestrator_name}.errors")
    
    def handle_exception(
        self,
        exc: Exception,
        phase_name: Optional[str] = None,
        operation: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Error:
        """
        Handle an exception with full context.
        
        Args:
            exc: Exception to handle
            phase_name: Name of phase where error occurred
            operation: Operation being performed
            parameters: Parameters passed to operation
        
        Returns:
            Error object with full context
        """
        # Classify error
        severity = self._classify_severity(exc)
        category = self._classify_category(exc)
        
        # Build context
        context = ErrorContext(
            orchestrator_name=self.orchestrator_name,
            phase_name=phase_name,
            operation=operation,
            parameters=parameters or {}
        )
        
        # Create error object
        error = Error(
            error_type=exc.__class__.__name__,
            error_message=str(exc),
            severity=severity,
            category=category,
            context=context,
            traceback_str=traceback.format_exc(),
            recoverable=self._is_recoverable(exc),
            max_retries=self.max_retries
        )
        
        # Log error
        self.log_error(error)
        
        # Store error
        self.errors.append(error)
        
        return error
    
    def log_error(self, error: Error) -> None:
        """
        Log error with appropriate level.
        
        Args:
            error: Error to log
        """
        log_msg = self._format_error_message(error)
        
        if error.severity == ErrorSeverity.LOW:
            self.logger.warning(log_msg)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.error(log_msg)
        elif error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.critical(log_msg)
            if error.traceback_str:
                self.logger.critical(f"Traceback:\n{error.traceback_str}")
    
    def should_retry(self, error: Error) -> bool:
        """
        Determine if error should be retried.
        
        Args:
            error: Error to evaluate
        
        Returns:
            True if retry should be attempted
        """
        # Don't retry critical errors
        if error.is_critical:
            return False
        
        # Don't retry if max retries exceeded
        if error.retry_count >= error.max_retries:
            return False
        
        # Don't retry non-recoverable errors
        if not error.recoverable:
            return False
        
        return True
    
    def get_recovery_strategy(self, error: Error) -> str:
        """
        Determine recovery strategy for error.
        
        Args:
            error: Error to evaluate
        
        Returns:
            Recovery strategy string (retry, skip, abort, manual)
        """
        # Configuration errors require manual intervention (check before critical)
        if error.category == ErrorCategory.CONFIGURATION:
            return "manual"
        
        # Critical errors require abort
        if error.is_critical:
            return "abort"
        
        # Retry if possible
        if error.should_retry:
            return "retry"
        
        # Skip non-critical errors that can't be retried
        if error.severity == ErrorSeverity.LOW:
            return "skip"
        
        # Abort for other cases
        return "abort"
    
    def get_errors(self, severity: Optional[ErrorSeverity] = None) -> List[Error]:
        """
        Get all errors, optionally filtered by severity.
        
        Args:
            severity: Filter by severity level
        
        Returns:
            List of errors
        """
        if severity is None:
            return self.errors.copy()
        return [e for e in self.errors if e.severity == severity]
    
    def has_critical_errors(self) -> bool:
        """
        Check if any critical errors exist.
        
        Returns:
            True if critical errors present
        """
        return any(e.is_critical for e in self.errors)
    
    def clear_errors(self) -> None:
        """Clear all stored errors."""
        self.errors.clear()
        self.logger.debug("Error history cleared")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of all errors.
        
        Returns:
            Dictionary with error statistics and details
        """
        total = len(self.errors)
        by_severity = {
            severity: len([e for e in self.errors if e.severity == severity])
            for severity in ErrorSeverity
        }
        by_category = {
            category: len([e for e in self.errors if e.category == category])
            for category in ErrorCategory
        }
        
        return {
            "total_errors": total,
            "by_severity": {s.value: count for s, count in by_severity.items()},
            "by_category": {c.value: count for c, count in by_category.items()},
            "critical_errors": self.has_critical_errors(),
            "errors": [
                {
                    "type": e.error_type,
                    "message": e.error_message,
                    "severity": e.severity.value,
                    "category": e.category.value,
                    "phase": e.context.phase_name,
                    "timestamp": e.context.timestamp.isoformat()
                }
                for e in self.errors
            ]
        }
    
    def _classify_severity(self, exc: Exception) -> ErrorSeverity:
        """
        Classify exception severity.
        
        Args:
            exc: Exception to classify
        
        Returns:
            ErrorSeverity level
        """
        # Configuration errors are high severity
        if isinstance(exc, (ConfigurationError, ValueError, TypeError)):
            return ErrorSeverity.HIGH
        
        # Phase errors are medium severity
        if isinstance(exc, PhaseError):
            return ErrorSeverity.MEDIUM
        
        # Orchestrator errors use their severity
        if isinstance(exc, OrchestratorError):
            return exc.severity
        
        # System errors are critical
        if isinstance(exc, (SystemError, MemoryError, OSError)):
            return ErrorSeverity.CRITICAL
        
        # Default to medium
        return ErrorSeverity.MEDIUM
    
    def _classify_category(self, exc: Exception) -> ErrorCategory:
        """
        Classify exception category.
        
        Args:
            exc: Exception to classify
        
        Returns:
            ErrorCategory
        """
        # Configuration errors
        if isinstance(exc, (ConfigurationError, ValueError)):
            return ErrorCategory.CONFIGURATION
        
        # Validation errors
        if isinstance(exc, (TypeError, AssertionError)):
            return ErrorCategory.VALIDATION
        
        # Phase errors
        if isinstance(exc, PhaseError):
            return ErrorCategory.PHASE_EXECUTION
        
        # Default to unknown
        return ErrorCategory.UNKNOWN
    
    def _is_recoverable(self, exc: Exception) -> bool:
        """
        Determine if exception is recoverable.
        
        Args:
            exc: Exception to evaluate
        
        Returns:
            True if recoverable
        """
        # System errors are not recoverable
        if isinstance(exc, (SystemError, MemoryError)):
            return False
        
        # Configuration errors are not recoverable without intervention
        if isinstance(exc, (ConfigurationError, ValueError)):
            return False
        
        # Most other errors are recoverable
        return True
    
    def _format_error_message(self, error: Error) -> str:
        """
        Format error for logging.
        
        Args:
            error: Error to format
        
        Returns:
            Formatted error message
        """
        parts = [
            f"[{error.severity.value.upper()}]",
            f"[{error.category.value}]",
            f"{error.error_type}: {error.error_message}"
        ]
        
        if error.context.phase_name:
            parts.insert(2, f"[phase={error.context.phase_name}]")
        
        if error.context.operation:
            parts.insert(2, f"[operation={error.context.operation}]")
        
        return " ".join(parts)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"OrchestratorErrorHandler(orchestrator='{self.orchestrator_name}', errors={len(self.errors)})"
