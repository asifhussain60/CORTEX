"""
Error Handler for CORTEX 4.0 Orchestrators

Provides standardized error handling, recovery strategies, and logging.
"""

from enum import Enum
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging
import traceback


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"          # Informational, no action needed
    WARNING = "warning"    # Warning, operation can continue
    ERROR = "error"        # Error, phase failed but recoverable
    CRITICAL = "critical"  # Critical, orchestrator must stop


class RecoveryStrategy(Enum):
    """Error recovery strategies"""
    RETRY = "retry"              # Retry the failed operation
    SKIP = "skip"                # Skip phase and continue
    ROLLBACK = "rollback"        # Rollback changes and retry
    FAIL_FAST = "fail_fast"      # Stop immediately
    CONTINUE = "continue"        # Log and continue
    USER_INTERVENTION = "user"   # Require user decision


@dataclass
class OrchestratorError:
    """
    Structured error information for orchestrators.
    
    Attributes:
        phase: Phase where error occurred
        severity: Error severity level
        message: Human-readable error message
        exception: Original exception (if any)
        traceback: Stack trace
        recovery_strategy: Recommended recovery action
        context: Additional context data
        timestamp: When error occurred
    """
    phase: str
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    traceback: Optional[str] = None
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.FAIL_FAST
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Capture traceback if exception provided
        if self.exception and not self.traceback:
            self.traceback = ''.join(traceback.format_exception(
                type(self.exception),
                self.exception,
                self.exception.__traceback__
            ))


class ErrorHandler:
    """
    Centralized error handling for orchestrators.
    
    Features:
    - Structured error capture
    - Recovery strategy recommendation
    - Error history tracking
    - Retry logic with exponential backoff
    - User-friendly error messages
    """
    
    def __init__(self, orchestrator_name: str, max_retries: int = 3):
        """
        Initialize error handler.
        
        Args:
            orchestrator_name: Name of owning orchestrator
            max_retries: Maximum retry attempts for recoverable errors
        """
        self.orchestrator_name = orchestrator_name
        self.max_retries = max_retries
        self.errors: List[OrchestratorError] = []
        self.retry_counts: Dict[str, int] = {}
        self.logger = logging.getLogger(f"cortex.orchestration.{orchestrator_name}.errors")
    
    def handle_error(
        self,
        phase: str,
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        recovery_strategy: Optional[RecoveryStrategy] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> OrchestratorError:
        """
        Handle an error that occurred during orchestration.
        
        Args:
            phase: Phase where error occurred
            exception: The exception that was raised
            severity: Error severity level
            recovery_strategy: Recommended recovery action (auto-determined if not provided)
            context: Additional context data
            
        Returns:
            OrchestratorError object with full error details
        """
        # Auto-determine recovery strategy if not provided
        if recovery_strategy is None:
            recovery_strategy = self._determine_recovery_strategy(exception, severity)
        
        # Create structured error
        error = OrchestratorError(
            phase=phase,
            severity=severity,
            message=str(exception),
            exception=exception,
            recovery_strategy=recovery_strategy,
            context=context or {}
        )
        
        # Log error
        self._log_error(error)
        
        # Store in history
        self.errors.append(error)
        
        return error
    
    def can_retry(self, phase: str) -> bool:
        """
        Check if phase can be retried.
        
        Args:
            phase: Phase name to check
            
        Returns:
            True if retry attempts remain
        """
        retry_count = self.retry_counts.get(phase, 0)
        return retry_count < self.max_retries
    
    def record_retry(self, phase: str) -> int:
        """
        Record a retry attempt for a phase.
        
        Args:
            phase: Phase name
            
        Returns:
            Current retry count
        """
        self.retry_counts[phase] = self.retry_counts.get(phase, 0) + 1
        count = self.retry_counts[phase]
        self.logger.info(f"🔄 Retry attempt {count}/{self.max_retries} for phase: {phase}")
        return count
    
    def reset_retries(self, phase: str) -> None:
        """Reset retry counter for a phase"""
        if phase in self.retry_counts:
            del self.retry_counts[phase]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of all errors.
        
        Returns:
            Dictionary with error statistics
        """
        if not self.errors:
            return {
                "total_errors": 0,
                "by_severity": {},
                "by_phase": {},
                "critical_errors": []
            }
        
        by_severity = {}
        by_phase = {}
        critical_errors = []
        
        for error in self.errors:
            # Count by severity
            severity_key = error.severity.value
            by_severity[severity_key] = by_severity.get(severity_key, 0) + 1
            
            # Count by phase
            by_phase[error.phase] = by_phase.get(error.phase, 0) + 1
            
            # Track critical errors
            if error.severity == ErrorSeverity.CRITICAL:
                critical_errors.append({
                    "phase": error.phase,
                    "message": error.message,
                    "timestamp": error.timestamp.isoformat()
                })
        
        return {
            "total_errors": len(self.errors),
            "by_severity": by_severity,
            "by_phase": by_phase,
            "critical_errors": critical_errors
        }
    
    def has_critical_errors(self) -> bool:
        """Check if any critical errors occurred"""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)
    
    def clear_errors(self) -> None:
        """Clear all error history"""
        self.errors.clear()
        self.retry_counts.clear()
        self.logger.debug("🧹 Error history cleared")
    
    def _determine_recovery_strategy(
        self,
        exception: Exception,
        severity: ErrorSeverity
    ) -> RecoveryStrategy:
        """
        Auto-determine recovery strategy based on exception type and severity.
        
        Args:
            exception: The exception
            severity: Error severity
            
        Returns:
            Recommended recovery strategy
        """
        # Critical errors always fail fast
        if severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy.FAIL_FAST
        
        # Network/timeout errors should retry
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return RecoveryStrategy.RETRY
        
        # File not found can often continue
        if isinstance(exception, FileNotFoundError):
            return RecoveryStrategy.SKIP
        
        # Permission errors need user intervention
        if isinstance(exception, PermissionError):
            return RecoveryStrategy.USER_INTERVENTION
        
        # Value/Type errors usually indicate logic bugs - fail fast
        if isinstance(exception, (ValueError, TypeError, AttributeError)):
            return RecoveryStrategy.FAIL_FAST
        
        # Default: retry for errors, continue for warnings
        if severity == ErrorSeverity.ERROR:
            return RecoveryStrategy.RETRY
        else:
            return RecoveryStrategy.CONTINUE
    
    def _log_error(self, error: OrchestratorError) -> None:
        """Log error with appropriate level"""
        log_message = f"[{error.phase}] {error.message}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"🚨 CRITICAL: {log_message}")
        elif error.severity == ErrorSeverity.ERROR:
            self.logger.error(f"❌ ERROR: {log_message}")
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning(f"⚠️  WARNING: {log_message}")
        else:
            self.logger.info(f"ℹ️  INFO: {log_message}")
        
        # Log recovery strategy
        self.logger.debug(f"Recovery strategy: {error.recovery_strategy.value}")
        
        # Log traceback for errors and critical
        if error.traceback and error.severity in (ErrorSeverity.ERROR, ErrorSeverity.CRITICAL):
            self.logger.debug(f"Traceback:\n{error.traceback}")
