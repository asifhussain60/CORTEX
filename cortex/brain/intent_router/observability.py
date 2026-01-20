"""AC-PHX-007-13: Observability Instrumentation"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ObservabilityEvent:
    """Observability event record."""
    timestamp: str
    event_type: str
    component: str
    details: Dict[str, Any]
    severity: str = "info"
    trace_id: Optional[str] = None


class ObservabilityInstrument:
    """Instruments intent router for observability."""
    
    def __init__(self) -> None:
        """Initialize observability instrument."""
        self.events: List[ObservabilityEvent] = []
        self._metrics: Dict[str, int] = {}
    
    def record_event(
        self,
        event_type: str,
        component: str,
        details: Dict[str, Any],
        severity: str = "info",
        trace_id: Optional[str] = None
    ) -> None:
        """Record observability event.
        
        Args:
            event_type: Type of event (e.g., 'classification', 'routing')
            component: Component name (e.g., 'classifier', 'router')
            details: Event details dictionary
            severity: Event severity ('debug', 'info', 'warning', 'error')
            trace_id: Optional trace ID for distributed tracing
        """
        event = ObservabilityEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            component=component,
            details=details,
            severity=severity,
            trace_id=trace_id
        )
        self.events.append(event)
        
        # Update metrics
        metric_key = f"{component}.{event_type}"
        self._metrics[metric_key] = self._metrics.get(metric_key, 0) + 1
        
        # Log based on severity
        log_msg = f"[{component}] {event_type}: {details}"
        if severity == "error":
            logger.error(log_msg)
        elif severity == "warning":
            logger.warning(log_msg)
        elif severity == "debug":
            logger.debug(log_msg)
        else:
            logger.info(log_msg)
    
    def get_events(
        self,
        component: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[ObservabilityEvent]:
        """Get recorded events with optional filtering.
        
        Args:
            component: Filter by component name
            event_type: Filter by event type
            severity: Filter by severity
            
        Returns:
            List of matching events
        """
        filtered = self.events
        
        if component:
            filtered = [e for e in filtered if e.component == component]
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if severity:
            filtered = [e for e in filtered if e.severity == severity]
        
        return filtered
    
    def get_metrics(self) -> Dict[str, int]:
        """Get event metrics by component and type.
        
        Returns:
            Dictionary of metrics (component.event_type -> count)
        """
        return self._metrics.copy()
    
    def clear_events(self) -> None:
        """Clear all recorded events (useful for testing)."""
        self.events.clear()
        self._metrics.clear()

