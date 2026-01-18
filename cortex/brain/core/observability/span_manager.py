"""
Span management for distributed tracing.

This module provides span creation, context propagation, and header injection
for W3C Trace Context compatibility across service boundaries.

Attributes:
    W3C_TRACEPARENT_HEADER: Header name for W3C trace context
    W3C_TRACESTATE_HEADER: Header name for W3C trace state
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Generator, ContextManager
from datetime import datetime
from contextlib import contextmanager
import uuid
import time
import logging


W3C_TRACEPARENT_HEADER = "traceparent"
W3C_TRACESTATE_HEADER = "tracestate"


@dataclass
class SpanContext:
    """Context for a single span in a trace.
    
    Attributes:
        trace_id: Unique identifier for entire trace
        span_id: Unique identifier for this span
        parent_span_id: Span ID of parent span (if any)
        flags: Trace flags (sampling, etc.)
        start_time: When span started (seconds since epoch)
        end_time: When span ended (seconds since epoch, 0 if not ended)
        name: Operation name
        attributes: Dictionary of span attributes
        status: Span status (OK, ERROR, or UNSET)
    """
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    flags: str = "01"
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    name: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    status: str = "UNSET"
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the span.
        
        Args:
            key: Attribute key
            value: Attribute value
        """
        self.attributes[key] = value

    def get_attribute(self, key: str) -> Any:
        """Get an attribute from the span.
        
        Args:
            key: Attribute key
            
        Returns:
            Attribute value or None if not found
        """
        return self.attributes.get(key)

    def set_error(self, message: str) -> None:
        """Mark span as error and record message.
        
        Args:
            message: Error message
        """
        self.status = "ERROR"
        self.set_attribute("error.message", message)

    def get_duration_ms(self) -> float:
        """Get span duration in milliseconds.
        
        Returns:
            Duration in milliseconds
        """
        if self.end_time == 0.0:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary representation.
        
        Returns:
            Dictionary with span data
        """
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.get_duration_ms(),
            "attributes": self.attributes,
            "status": self.status,
        }


class SpanManager:
    """Manager for creating and tracking spans.
    
    Provides span lifecycle management, context propagation, and W3C Trace
    Context header injection for distributed tracing.
    
    Attributes:
        exporter: OtelExporter instance for trace export
        current_span: Currently active span
        spans: All spans created by this manager
        span_counts: Count of spans per operation name
    """
    
    def __init__(self, exporter: Optional[Any] = None) -> None:
        """Initialize span manager.
        
        Args:
            exporter: OtelExporter instance (optional)
        """
        self.exporter: Optional[Any] = exporter
        self.current_span: Optional[SpanContext] = None
        self.spans: List[SpanContext] = []
        self.span_counts: Dict[str, int] = {}
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._trace_stack: List[SpanContext] = []

    @contextmanager
    def create_span(self, operation_name: str) -> Generator[SpanContext, None, None]:
        """Create a new span as a context manager.
        
        Args:
            operation_name: Name of the operation being traced
            
        Yields:
            SpanContext for the operation
        """
        # Generate IDs
        trace_id = self._get_or_create_trace_id()
        span_id = self._generate_span_id()
        parent_span_id = self.current_span.span_id if self.current_span else None
        
        # Create span context
        span = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            name=operation_name,
        )
        
        # Save previous span and set current
        previous_span = self.current_span
        self.current_span = span
        self._trace_stack.append(span)
        
        try:
            yield span
        except Exception as e:
            span.set_error(str(e))
            self._logger.error(f"Error in span {operation_name}: {e}")
            raise
        finally:
            # Record span completion
            span.end_time = time.time()
            self.spans.append(span)
            
            # Update counts
            self.span_counts[operation_name] = self.span_counts.get(operation_name, 0) + 1
            
            # Restore previous span
            self.current_span = previous_span
            self._trace_stack.pop()
            
            # Add to exporter if available
            if self.exporter:
                self.exporter.add_span(span.to_dict())

    def serialize_context(self) -> Optional[str]:
        """Serialize current span context for propagation.
        
        Returns:
            JSON string with trace context or None if no active span
        """
        if not self.current_span:
            return None
        
        context = {
            "trace_id": self.current_span.trace_id,
            "span_id": self.current_span.span_id,
            "parent_span_id": self.current_span.parent_span_id,
        }
        
        return json.dumps(context) if context else None

    def deserialize_context(self, context_str: str) -> Dict[str, Any]:
        """Deserialize span context from string.
        
        Args:
            context_str: JSON string with trace context
            
        Returns:
            Dictionary with context data
        """
        import json
        return json.loads(context_str)

    def get_propagation_headers(self) -> Dict[str, str]:
        """Get W3C Trace Context headers for propagation.
        
        Returns:
            Dictionary with traceparent and tracestate headers
        """
        if not self.current_span:
            return {}
        
        # Format: version-trace_id-parent_id-trace_flags
        traceparent = (
            f"00-{self.current_span.trace_id}-"
            f"{self.current_span.span_id}-{self.current_span.flags}"
        )
        
        headers = {
            W3C_TRACEPARENT_HEADER: traceparent,
        }
        
        # Add tracestate if available
        if self.exporter:
            service = getattr(self.exporter, "service_name", "unknown")
            headers[W3C_TRACESTATE_HEADER] = f"cortex={service}"
        
        return headers

    def get_span_count(self, operation_name: str) -> int:
        """Get count of spans for a specific operation.
        
        Args:
            operation_name: Name of operation
            
        Returns:
            Count of spans with this operation name
        """
        return self.span_counts.get(operation_name, 0)

    def get_all_spans(self) -> List[SpanContext]:
        """Get all spans created by this manager.
        
        Returns:
            List of all SpanContext instances
        """
        return self.spans.copy()

    def clear_spans(self) -> None:
        """Clear all recorded spans."""
        self.spans.clear()
        self.span_counts.clear()

    @staticmethod
    def _generate_span_id() -> str:
        """Generate a random span ID.
        
        Returns:
            16-character hex string
        """
        # W3C spec: 8 bytes = 16 hex characters
        return uuid.uuid4().hex[:16]

    def _get_or_create_trace_id(self) -> str:
        """Get current trace ID or create new one.
        
        Returns:
            32-character hex string (trace ID)
        """
        if self._trace_stack:
            # Use trace ID from current trace stack
            return self._trace_stack[0].trace_id
        
        # W3C spec: 16 bytes = 32 hex characters
        return uuid.uuid4().hex


# Import json at module level for serialization
import json
