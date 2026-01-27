"""Observability Module - Monitoring and instrumentation for intent routing.

Author: CORTEX Framework
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """A single metric measurement."""
    
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Span:
    """A tracing span."""
    
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"
    
    def finish(self) -> None:
        """Finish the span and calculate duration."""
        self.end_time = datetime.now()
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_ms = delta.total_seconds() * 1000


class ObservabilityInstrument:
    """Instruments code for observability with metrics and tracing."""
    
    def __init__(self, service_name: str = "cortex"):
        """Initialize observability instrument.
        
        Args:
            service_name: Name of the service being instrumented
        """
        self.service_name = service_name
        self.metrics: List[Metric] = []
        self.spans: List[Span] = []
        self.active_spans: Dict[str, Span] = {}
        self.events: List[Dict[str, Any]] = []  # For record_event compatibility
    
    def record_event(
        self,
        event_type: str,
        component: str,
        details: Dict[str, Any]
    ) -> None:
        """Record an observability event (simplified API for testing).
        
        Args:
            event_type: Type of event
            component: Component name
            details: Event details
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "component": component,
            "details": details,
        }
        self.events.append(event)
        logger.debug(f"Recorded event: {event_type} from {component}")
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get recorded events.
        
        Returns:
            List of event dictionaries
        """
        return self.events.copy()
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.COUNTER,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric.
        
        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            tags: Optional tags for the metric
        """
        metric = Metric(
            name=f"{self.service_name}.{name}",
            value=value,
            metric_type=metric_type,
            tags=tags or {}
        )
        self.metrics.append(metric)
        logger.debug(f"Recorded metric: {metric.name}={value}")
    
    def start_span(self, operation: str, tags: Optional[Dict[str, Any]] = None) -> str:
        """Start a tracing span.
        
        Args:
            operation: Name of the operation
            tags: Optional tags for the span
            
        Returns:
            Span ID for use with finish_span
        """
        span_id = f"{operation}_{len(self.spans)}"
        span = Span(
            operation=operation,
            start_time=datetime.now(),
            tags=tags or {}
        )
        self.active_spans[span_id] = span
        logger.debug(f"Started span: {operation}")
        return span_id
    
    def finish_span(self, span_id: str, status: str = "success") -> None:
        """Finish a tracing span.
        
        Args:
            span_id: ID of the span to finish
            status: Status of the operation (success/error)
        """
        if span_id in self.active_spans:
            span = self.active_spans.pop(span_id)
            span.status = status
            span.finish()
            self.spans.append(span)
            logger.debug(f"Finished span: {span.operation} ({span.duration_ms:.2f}ms)")
    
    def trace(self, operation: str) -> Callable:
        """Decorator to automatically trace a function.
        
        Args:
            operation: Name of the operation
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                span_id = self.start_span(operation)
                try:
                    result = func(*args, **kwargs)
                    self.finish_span(span_id, "success")
                    return result
                except Exception as e:
                    self.finish_span(span_id, "error")
                    raise
            return wrapper
        return decorator
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recorded metrics.
        
        Returns:
            Dictionary with metric statistics
        """
        by_type = {}
        for metric in self.metrics:
            metric_type = metric.metric_type.value
            if metric_type not in by_type:
                by_type[metric_type] = []
            by_type[metric_type].append({
                "name": metric.name,
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat()
            })
        
        return {
            "service": self.service_name,
            "total_metrics": len(self.metrics),
            "by_type": by_type
        }
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get summary of tracing spans.
        
        Returns:
            Dictionary with trace statistics
        """
        total_spans = len(self.spans)
        successful = sum(1 for s in self.spans if s.status == "success")
        failed = total_spans - successful
        
        avg_duration = 0.0
        if self.spans:
            durations = [s.duration_ms for s in self.spans if s.duration_ms is not None]
            if durations:
                avg_duration = sum(durations) / len(durations)
        
        return {
            "service": self.service_name,
            "total_spans": total_spans,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_spans if total_spans > 0 else 0,
            "avg_duration_ms": avg_duration
        }


__all__ = ["ObservabilityInstrument", "Metric", "Span", "MetricType"]
