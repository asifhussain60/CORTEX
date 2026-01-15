"""
OpenTelemetry integration for distributed tracing and metrics.

This module provides the core OpenTelemetry exporter for CORTEX runtime,
enabling distributed tracing, span creation, and metrics collection across
the orchestration pipeline.

Attributes:
    DEFAULT_BATCH_SIZE: Default number of spans before batch export (50)
    DEFAULT_SHUTDOWN_TIMEOUT: Default shutdown timeout in seconds (30)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from pathlib import Path
import json
import logging

from src.core.observability.span_manager import SpanManager


@dataclass
class TraceConfig:
    """Configuration for OpenTelemetry tracing.
    
    Attributes:
        service_name: Name of the service for trace identification
        environment: Environment name (test, staging, production)
        endpoint: OpenTelemetry backend endpoint URL
        enabled: Whether tracing is enabled
        batch_size: Number of spans before batch export (default: 50)
        shutdown_timeout_seconds: Timeout for shutdown in seconds (default: 30)
    """
    service_name: str
    environment: str
    endpoint: str
    enabled: bool = True
    batch_size: int = 50
    shutdown_timeout_seconds: int = 30
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization.
        
        Raises:
            ValueError: If service_name is empty or environment is invalid
        """
        if not self.service_name or not self.service_name.strip():
            raise ValueError("service_name cannot be empty")
        
        valid_envs = {"test", "staging", "production", "development"}
        if self.environment not in valid_envs:
            raise ValueError(
                f"environment must be one of {valid_envs}, "
                f"got {self.environment}"
            )


class OtelExporter:
    """OpenTelemetry exporter for distributed tracing.
    
    Manages trace export, span creation, and context propagation for CORTEX
    observability system.
    
    Attributes:
        service_name: Name of the service for trace identification
        environment: Environment name (test, staging, production)
        endpoint: OpenTelemetry backend endpoint URL
        enabled: Whether tracing is enabled
        span_manager: SpanManager instance for span operations
        pending_spans: Count of spans pending export
    """
    
    def __init__(
        self,
        config: TraceConfig,
        audit_logger: Optional[Any] = None,
    ) -> None:
        """Initialize OpenTelemetry exporter.
        
        Args:
            config: TraceConfig instance with exporter configuration
            audit_logger: Optional AuditLogger for compliance logging
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate configuration
        if not isinstance(config, TraceConfig):
            raise TypeError("config must be TraceConfig instance")
        
        self.service_name: str = config.service_name
        self.environment: str = config.environment
        self.endpoint: str = config.endpoint
        self.enabled: bool = config.enabled
        self.batch_size: int = config.batch_size
        self.shutdown_timeout_seconds: int = config.shutdown_timeout_seconds
        
        self.audit_logger: Optional[Any] = audit_logger
        self.span_manager: SpanManager = SpanManager(exporter=self)
        self.pending_spans: int = 0
        
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._spans: List[Dict[str, Any]] = []
        self._export_callbacks: List[Callable] = []
        
        # Log AC_START
        if self.audit_logger:
            self.audit_logger.log_ac_event(
                ac_id="OB-001-01",
                operation="AC_START",
                details=f"OpenTelemetry exporter initialized for {self.service_name}",
            )

    def create_span(self, operation_name: str) -> Any:
        """Create a new span for an operation.
        
        Args:
            operation_name: Name of the operation to trace
            
        Returns:
            SpanContext instance for the operation
        """
        return self.span_manager.create_span(operation_name)

    def export_traces(self, traces: List[Dict[str, Any]]) -> bool:
        """Export traces to the configured backend.
        
        Args:
            traces: List of trace objects to export
            
        Returns:
            True if export successful, False otherwise
        """
        if not self.enabled:
            return True
        
        try:
            if not traces:
                return True
            
            # Log export attempt
            self._logger.debug(
                f"Exporting {len(traces)} traces to {self.endpoint}"
            )
            
            # In production, this would call the actual OTEL backend
            # For now, we simulate export
            export_data = {
                "service_name": self.service_name,
                "environment": self.environment,
                "timestamp": datetime.utcnow().isoformat(),
                "trace_count": len(traces),
                "traces": traces,
            }
            
            # Call registered export callbacks
            for callback in self._export_callbacks:
                callback(export_data)
            
            # Log AC_EXECUTE
            if self.audit_logger:
                self.audit_logger.log_ac_event(
                    ac_id="OB-001-01",
                    operation="AC_EXECUTE",
                    details=f"Exported {len(traces)} traces",
                )
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to export traces: {e}")
            return False

    def flush(self, timeout_seconds: Optional[int] = None) -> bool:
        """Flush pending spans to backend.
        
        Args:
            timeout_seconds: Timeout in seconds (uses default if None)
            
        Returns:
            True if flush successful, False otherwise
        """
        timeout = timeout_seconds or self.shutdown_timeout_seconds
        
        if self.pending_spans == 0:
            return True
        
        # Export pending spans
        if self._spans:
            result = self.export_traces(self._spans)
            if result:
                self._spans.clear()
                self.pending_spans = 0
            return result
        
        return True

    def register_export_callback(self, callback: Callable) -> None:
        """Register a callback to be called on trace export.
        
        Args:
            callback: Callable that receives exported trace data
        """
        self._export_callbacks.append(callback)

    def add_span(self, span_data: Dict[str, Any]) -> None:
        """Add a completed span to pending export queue.
        
        Args:
            span_data: Span data dictionary
        """
        if not self.enabled:
            # Don't track pending spans if disabled
            return
        
        self._spans.append(span_data)
        self.pending_spans += 1
        
        # Check if batch size reached
        if self.pending_spans >= self.batch_size:
            self.flush()

    def __enter__(self) -> "OtelExporter":
        """Context manager entry.
        
        Returns:
            Self for context manager
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - ensures pending spans are flushed.
        
        Args:
            exc_type: Exception type if exception occurred
            exc_val: Exception value if exception occurred
            exc_tb: Exception traceback if exception occurred
        """
        self.flush(timeout_seconds=self.shutdown_timeout_seconds)
        
        # Log AC_COMPLETE
        if self.audit_logger and exc_type is None:
            self.audit_logger.log_ac_event(
                ac_id="OB-001-01",
                operation="AC_COMPLETE",
                details="OpenTelemetry exporter shutdown successfully",
            )

    def get_config_dict(self) -> Dict[str, Any]:
        """Get exporter configuration as dictionary.
        
        Returns:
            Dictionary containing exporter configuration
        """
        return {
            "service_name": self.service_name,
            "environment": self.environment,
            "endpoint": self.endpoint,
            "enabled": self.enabled,
            "batch_size": self.batch_size,
            "shutdown_timeout_seconds": self.shutdown_timeout_seconds,
        }
