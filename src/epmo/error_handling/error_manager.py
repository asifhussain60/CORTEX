"""
CORTEX 3.0 Error Manager
========================

Centralized error management system with structured error classification,
detailed error codes, and intelligent error handling.
"""

import time
import uuid
import traceback
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ErrorCategory(Enum):
    """Error category classifications."""
    SYSTEM = "system"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    EXTERNAL_SERVICE = "external_service"
    DATA_PROCESSING = "data_processing"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Additional context information for errors."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    environment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CortexError(Exception):
    """
    Structured error class for CORTEX with detailed information
    and recovery guidance.
    """
    error_code: str
    message: str
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.UNKNOWN
    context: Optional[ErrorContext] = None
    cause: Optional[Exception] = None
    timestamp: float = field(default_factory=time.time)
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stack_trace: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    retry_after: Optional[float] = None
    is_transient: bool = False
    
    def __post_init__(self):
        """Initialize error with stack trace if not provided."""
        if not self.stack_trace:
            self.stack_trace = traceback.format_exc()
        
        # Set default recovery suggestions based on category
        if not self.recovery_suggestions:
            self.recovery_suggestions = self._get_default_recovery_suggestions()
    
    def _get_default_recovery_suggestions(self) -> List[str]:
        """Get default recovery suggestions based on error category."""
        suggestions = {
            ErrorCategory.NETWORK: [
                "Check network connectivity",
                "Retry request after delay",
                "Verify service endpoints are accessible"
            ],
            ErrorCategory.TIMEOUT: [
                "Increase timeout configuration",
                "Retry with exponential backoff",
                "Check system performance"
            ],
            ErrorCategory.RESOURCE: [
                "Check available memory and disk space",
                "Release unused resources",
                "Scale up system resources"
            ],
            ErrorCategory.CONFIGURATION: [
                "Verify configuration settings",
                "Check environment variables",
                "Validate configuration file syntax"
            ],
            ErrorCategory.AUTHENTICATION: [
                "Verify authentication credentials",
                "Check token expiration",
                "Refresh authentication tokens"
            ],
            ErrorCategory.VALIDATION: [
                "Validate input parameters",
                "Check data format and structure",
                "Verify required fields are present"
            ]
        }
        
        return suggestions.get(self.category, ["Contact support team", "Check system logs"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            'error_id': self.error_id,
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'timestamp': self.timestamp,
            'stack_trace': self.stack_trace,
            'recovery_suggestions': self.recovery_suggestions,
            'retry_after': self.retry_after,
            'is_transient': self.is_transient,
            'context': self.context.__dict__ if self.context else None,
            'cause': str(self.cause) if self.cause else None
        }
    
    def __str__(self) -> str:
        """String representation of the error."""
        return f"[{self.error_code}] {self.message} (Severity: {self.severity.value})"


class ErrorManager:
    """
    Centralized error management system for handling, categorizing,
    and tracking errors across CORTEX components.
    """
    
    def __init__(self):
        # Error tracking
        self._errors: Dict[str, CortexError] = {}
        self._error_counts: Dict[str, int] = {}
        self._error_lock = threading.RLock()
        
        # Error handlers
        self._error_handlers: Dict[str, List[Callable]] = {}
        self._category_handlers: Dict[ErrorCategory, List[Callable]] = {}
        self._severity_handlers: Dict[ErrorSeverity, List[Callable]] = {}
        
        # Error patterns for classification
        self._error_patterns = self._initialize_error_patterns()
        
        # Metrics
        self._error_metrics = {
            'total_errors': 0,
            'errors_by_severity': {severity: 0 for severity in ErrorSeverity},
            'errors_by_category': {category: 0 for category in ErrorCategory},
            'resolution_times': [],
            'recurring_errors': {}
        }
    
    def handle_error(
        self,
        exception: Exception,
        context: Optional[ErrorContext] = None,
        custom_message: Optional[str] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        recovery_suggestions: Optional[List[str]] = None
    ) -> CortexError:
        """
        Handle an exception and convert it to a structured CortexError.
        
        Args:
            exception: The original exception
            context: Additional context information
            custom_message: Custom error message override
            severity: Custom severity level
            category: Custom error category
            recovery_suggestions: Custom recovery suggestions
            
        Returns:
            Structured CortexError
        """
        # Classify the error if not provided
        if isinstance(exception, CortexError):
            cortex_error = exception
        else:
            error_classification = self._classify_error(exception)
            
            cortex_error = CortexError(
                error_code=error_classification['code'],
                message=custom_message or str(exception),
                severity=severity or error_classification['severity'],
                category=category or error_classification['category'],
                context=context,
                cause=exception,
                is_transient=error_classification['is_transient'],
                recovery_suggestions=recovery_suggestions or error_classification['recovery_suggestions']
            )
        
        # Store and track the error
        self._store_error(cortex_error)
        
        # Execute error handlers
        self._execute_error_handlers(cortex_error)
        
        # Update metrics
        self._update_error_metrics(cortex_error)
        
        return cortex_error
    
    def create_error(
        self,
        error_code: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[ErrorContext] = None,
        is_transient: bool = False,
        recovery_suggestions: Optional[List[str]] = None,
        retry_after: Optional[float] = None
    ) -> CortexError:
        """
        Create a new CortexError without an underlying exception.
        
        Args:
            error_code: Unique error code
            message: Error message
            severity: Error severity level
            category: Error category
            context: Additional context
            is_transient: Whether error is transient
            recovery_suggestions: Recovery suggestions
            retry_after: Suggested retry delay
            
        Returns:
            New CortexError
        """
        cortex_error = CortexError(
            error_code=error_code,
            message=message,
            severity=severity,
            category=category,
            context=context,
            is_transient=is_transient,
            recovery_suggestions=recovery_suggestions,
            retry_after=retry_after
        )
        
        self._store_error(cortex_error)
        self._execute_error_handlers(cortex_error)
        self._update_error_metrics(cortex_error)
        
        return cortex_error
    
    def get_error(self, error_id: str) -> Optional[CortexError]:
        """Get error by ID."""
        with self._error_lock:
            return self._errors.get(error_id)
    
    def get_recent_errors(self, limit: int = 50, severity_filter: Optional[ErrorSeverity] = None) -> List[CortexError]:
        """Get recent errors with optional severity filtering."""
        with self._error_lock:
            errors = list(self._errors.values())
            
            # Filter by severity if specified
            if severity_filter:
                errors = [e for e in errors if e.severity == severity_filter]
            
            # Sort by timestamp (most recent first)
            errors.sort(key=lambda e: e.timestamp, reverse=True)
            
            return errors[:limit]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        with self._error_lock:
            stats = {
                'total_errors': self._error_metrics['total_errors'],
                'errors_by_severity': dict(self._error_metrics['errors_by_severity']),
                'errors_by_category': dict(self._error_metrics['errors_by_category']),
                'most_common_errors': self._get_most_common_errors(),
                'error_rate_trend': self._calculate_error_rate_trend(),
                'avg_resolution_time': self._calculate_avg_resolution_time(),
                'recurring_errors_count': len(self._error_metrics['recurring_errors'])
            }
            
            # Convert enum keys to strings for JSON serialization
            stats['errors_by_severity'] = {
                severity.value: count 
                for severity, count in self._error_metrics['errors_by_severity'].items()
            }
            stats['errors_by_category'] = {
                category.value: count 
                for category, count in self._error_metrics['errors_by_category'].items()
            }
            
            return stats
    
    def register_error_handler(
        self,
        handler: Callable[[CortexError], None],
        error_code: Optional[str] = None,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None
    ) -> None:
        """
        Register error handler for specific error codes, categories, or severities.
        
        Args:
            handler: Error handler function
            error_code: Specific error code to handle
            category: Error category to handle
            severity: Error severity to handle
        """
        if error_code:
            if error_code not in self._error_handlers:
                self._error_handlers[error_code] = []
            self._error_handlers[error_code].append(handler)
        
        if category:
            if category not in self._category_handlers:
                self._category_handlers[category] = []
            self._category_handlers[category].append(handler)
        
        if severity:
            if severity not in self._severity_handlers:
                self._severity_handlers[severity] = []
            self._severity_handlers[severity].append(handler)
    
    def clear_old_errors(self, max_age_hours: float = 24.0) -> int:
        """
        Clear old errors from storage to prevent memory buildup.
        
        Args:
            max_age_hours: Maximum age of errors to keep
            
        Returns:
            Number of errors cleared
        """
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleared_count = 0
        
        with self._error_lock:
            error_ids_to_remove = []
            for error_id, error in self._errors.items():
                if error.timestamp < cutoff_time:
                    error_ids_to_remove.append(error_id)
            
            for error_id in error_ids_to_remove:
                del self._errors[error_id]
                cleared_count += 1
        
        logger.info(f"Cleared {cleared_count} old errors")
        return cleared_count
    
    def export_errors(self, filepath: str, format: str = "json") -> bool:
        """
        Export error data to file for analysis.
        
        Args:
            filepath: Output file path
            format: Export format (json, csv)
            
        Returns:
            True if export successful
        """
        try:
            with self._error_lock:
                if format.lower() == "json":
                    export_data = {
                        'export_timestamp': time.time(),
                        'statistics': self.get_error_statistics(),
                        'errors': [error.to_dict() for error in self._errors.values()]
                    }
                    
                    with open(filepath, 'w') as f:
                        json.dump(export_data, f, indent=2, default=str)
                
                elif format.lower() == "csv":
                    import csv
                    with open(filepath, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            'error_id', 'error_code', 'message', 'severity', 'category',
                            'timestamp', 'is_transient', 'component', 'operation'
                        ])
                        
                        for error in self._errors.values():
                            writer.writerow([
                                error.error_id,
                                error.error_code,
                                error.message,
                                error.severity.value,
                                error.category.value,
                                error.timestamp,
                                error.is_transient,
                                error.context.component if error.context else '',
                                error.context.operation if error.context else ''
                            ])
                else:
                    raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Exported {len(self._errors)} errors to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export errors: {e}")
            return False
    
    def _classify_error(self, exception: Exception) -> Dict[str, Any]:
        """Classify an exception into CORTEX error structure."""
        exception_type = type(exception).__name__
        exception_message = str(exception)
        
        # Check against known patterns
        for pattern in self._error_patterns:
            if (pattern['exception_type'] == exception_type or 
                any(keyword in exception_message.lower() for keyword in pattern['keywords'])):
                return {
                    'code': pattern['error_code'],
                    'severity': pattern['severity'],
                    'category': pattern['category'],
                    'is_transient': pattern['is_transient'],
                    'recovery_suggestions': pattern['recovery_suggestions']
                }
        
        # Default classification
        return {
            'code': f"UNKNOWN_{exception_type}",
            'severity': ErrorSeverity.MEDIUM,
            'category': ErrorCategory.UNKNOWN,
            'is_transient': False,
            'recovery_suggestions': ["Check error details and contact support"]
        }
    
    def _initialize_error_patterns(self) -> List[Dict[str, Any]]:
        """Initialize error classification patterns."""
        return [
            # Network errors
            {
                'exception_type': 'ConnectionError',
                'keywords': ['connection', 'network', 'unreachable'],
                'error_code': 'NETWORK_CONNECTION_ERROR',
                'severity': ErrorSeverity.HIGH,
                'category': ErrorCategory.NETWORK,
                'is_transient': True,
                'recovery_suggestions': ['Check network connectivity', 'Retry after delay']
            },
            {
                'exception_type': 'TimeoutError',
                'keywords': ['timeout', 'timed out'],
                'error_code': 'NETWORK_TIMEOUT',
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.TIMEOUT,
                'is_transient': True,
                'recovery_suggestions': ['Increase timeout', 'Retry with exponential backoff']
            },
            
            # Resource errors
            {
                'exception_type': 'MemoryError',
                'keywords': ['memory', 'out of memory'],
                'error_code': 'RESOURCE_MEMORY_ERROR',
                'severity': ErrorSeverity.CRITICAL,
                'category': ErrorCategory.RESOURCE,
                'is_transient': False,
                'recovery_suggestions': ['Free memory', 'Optimize resource usage', 'Scale up system']
            },
            {
                'exception_type': 'FileNotFoundError',
                'keywords': ['file not found', 'no such file'],
                'error_code': 'RESOURCE_FILE_NOT_FOUND',
                'severity': ErrorSeverity.HIGH,
                'category': ErrorCategory.RESOURCE,
                'is_transient': False,
                'recovery_suggestions': ['Check file path', 'Ensure file exists', 'Verify permissions']
            },
            
            # Validation errors
            {
                'exception_type': 'ValueError',
                'keywords': ['invalid', 'value error'],
                'error_code': 'VALIDATION_INVALID_VALUE',
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.VALIDATION,
                'is_transient': False,
                'recovery_suggestions': ['Validate input values', 'Check data format']
            },
            {
                'exception_type': 'TypeError',
                'keywords': ['type error', 'wrong type'],
                'error_code': 'VALIDATION_TYPE_ERROR',
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.VALIDATION,
                'is_transient': False,
                'recovery_suggestions': ['Check data types', 'Validate input parameters']
            },
            
            # System errors
            {
                'exception_type': 'PermissionError',
                'keywords': ['permission denied', 'access denied'],
                'error_code': 'SYSTEM_PERMISSION_ERROR',
                'severity': ErrorSeverity.HIGH,
                'category': ErrorCategory.AUTHORIZATION,
                'is_transient': False,
                'recovery_suggestions': ['Check file permissions', 'Verify user access rights']
            }
        ]
    
    def _store_error(self, error: CortexError) -> None:
        """Store error in internal tracking."""
        with self._error_lock:
            self._errors[error.error_id] = error
            
            # Track error frequency
            if error.error_code not in self._error_counts:
                self._error_counts[error.error_code] = 0
            self._error_counts[error.error_code] += 1
            
            # Identify recurring errors
            if self._error_counts[error.error_code] > 5:
                self._error_metrics['recurring_errors'][error.error_code] = self._error_counts[error.error_code]
    
    def _execute_error_handlers(self, error: CortexError) -> None:
        """Execute registered error handlers."""
        handlers_to_execute = []
        
        # Collect applicable handlers
        handlers_to_execute.extend(self._error_handlers.get(error.error_code, []))
        handlers_to_execute.extend(self._category_handlers.get(error.category, []))
        handlers_to_execute.extend(self._severity_handlers.get(error.severity, []))
        
        # Execute handlers
        for handler in handlers_to_execute:
            try:
                handler(error)
            except Exception as e:
                logger.warning(f"Error handler failed: {e}")
    
    def _update_error_metrics(self, error: CortexError) -> None:
        """Update error metrics."""
        self._error_metrics['total_errors'] += 1
        self._error_metrics['errors_by_severity'][error.severity] += 1
        self._error_metrics['errors_by_category'][error.category] += 1
    
    def _get_most_common_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently occurring errors."""
        sorted_errors = sorted(
            self._error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'error_code': code, 'count': count}
            for code, count in sorted_errors[:limit]
        ]
    
    def _calculate_error_rate_trend(self) -> Dict[str, float]:
        """Calculate error rate trend over time."""
        # Simplified trend calculation
        current_time = time.time()
        hour_ago = current_time - 3600
        day_ago = current_time - 86400
        
        recent_errors = len([
            e for e in self._errors.values()
            if e.timestamp > hour_ago
        ])
        
        daily_errors = len([
            e for e in self._errors.values()
            if e.timestamp > day_ago
        ])
        
        return {
            'errors_last_hour': recent_errors,
            'errors_last_day': daily_errors,
            'hourly_rate': recent_errors,
            'daily_rate': daily_errors
        }
    
    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average error resolution time."""
        if not self._error_metrics['resolution_times']:
            return 0.0
        return sum(self._error_metrics['resolution_times']) / len(self._error_metrics['resolution_times'])


# Global error manager instance
default_error_manager = ErrorManager()