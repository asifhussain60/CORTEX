"""
Learning Event Collector

Thread-safe event capture system for learning library.
Captures milestone events from orchestrators/agents with <10ms overhead.

Features:
- Fire-and-forget event emission (no orchestrator blocking)
- Milestone filtering (only significant events)
- Thread-safe event storage
- In-memory queue with persistent storage (Phase 2)
- Performance monitoring (<10ms per event)

Usage:
    from src.learning.event_collector import LearningEventCollector
    from src.learning.event_taxonomy import EventType, LearningEvent
    
    collector = LearningEventCollector()
    
    # Emit event (non-blocking, <10ms)
    event = LearningEvent(
        event_type=EventType.PLAN_APPROVED,
        component="PlanningOrchestrator",
        metadata={"plan_id": "feature-xyz", "phases": 4}
    )
    collector.capture_event(event)
    
    # Retrieve milestone events
    milestones = collector.get_milestone_events()

Author: Asif Hussain
Version: 1.0.0 (Phase 1 - Event Infrastructure)
"""

import threading
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from src.learning.event_taxonomy import (
    LearningEvent,
    EventType,
    EventCategory,
    EventTier,
    get_must_have_events,
)


class LearningEventCollector:
    """
    Thread-safe collector for learning events.
    
    Captures events from orchestrators/agents and filters for milestones.
    Guarantees <10ms overhead per event emission.
    
    Attributes:
        events: List of all captured events (in-memory)
        milestone_events: Filtered list of milestone events only
        enabled: Whether collection is active
        performance_stats: Timing data for overhead monitoring
    """
    
    def __init__(self, enabled: bool = True, filter_must_have_only: bool = True):
        """
        Initialize event collector.
        
        Args:
            enabled: Whether to capture events (default True)
            filter_must_have_only: Only capture must-have events in Phase 1 (default True)
        """
        self._events: List[LearningEvent] = []
        self._lock = threading.Lock()
        self._enabled = enabled
        self._filter_must_have_only = filter_must_have_only
        self._must_have_types = set(get_must_have_events())
        self._performance_stats: Dict[str, List[float]] = {
            "capture_times": [],
            "filter_times": [],
        }
        
    @property
    def enabled(self) -> bool:
        """Check if collector is enabled."""
        return self._enabled
    
    def enable(self):
        """Enable event collection."""
        self._enabled = True
    
    def disable(self):
        """Disable event collection."""
        self._enabled = False
    
    def capture_event(self, event: LearningEvent) -> bool:
        """
        Capture a learning event (thread-safe, <10ms).
        
        This is the main entry point for orchestrators/agents.
        Fire-and-forget: Returns immediately, no blocking.
        
        Args:
            event: LearningEvent to capture
            
        Returns:
            True if event was captured, False if filtered out or disabled
        """
        if not self._enabled:
            return False
        
        start_time = time.perf_counter()
        
        # Filter must-have events only in Phase 1
        if self._filter_must_have_only and event.event_type not in self._must_have_types:
            return False
        
        # Thread-safe append
        with self._lock:
            self._events.append(event)
        
        # Performance tracking
        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms
        with self._lock:
            self._performance_stats["capture_times"].append(elapsed)
        
        return True
    
    def get_all_events(self) -> List[LearningEvent]:
        """
        Get all captured events (thread-safe).
        
        Returns:
            Copy of all events
        """
        with self._lock:
            return self._events.copy()
    
    def get_milestone_events(self) -> List[LearningEvent]:
        """
        Get only milestone events (thread-safe).
        
        Milestones are significant learning moments:
        - Plan approved (not plan created)
        - Phase completed (not phase started)
        - Work item completed (not created)
        
        Returns:
            List of milestone events
        """
        start_time = time.perf_counter()
        
        with self._lock:
            milestones = [e for e in self._events if e.is_milestone()]
        
        # Performance tracking
        elapsed = (time.perf_counter() - start_time) * 1000
        with self._lock:
            self._performance_stats["filter_times"].append(elapsed)
        
        return milestones
    
    def get_events_by_type(self, event_type: EventType) -> List[LearningEvent]:
        """
        Get all events of a specific type (thread-safe).
        
        Args:
            event_type: EventType to filter by
            
        Returns:
            List of matching events
        """
        with self._lock:
            return [e for e in self._events if e.event_type == event_type]
    
    def get_events_by_category(self, category: EventCategory) -> List[LearningEvent]:
        """
        Get all events in a learning category (thread-safe).
        
        Args:
            category: EventCategory to filter by
            
        Returns:
            List of matching events
        """
        with self._lock:
            return [e for e in self._events if e.event_type.category == category]
    
    def get_events_by_component(self, component: str) -> List[LearningEvent]:
        """
        Get all events from a specific component (thread-safe).
        
        Args:
            component: Component name (e.g., "PlanningOrchestrator")
            
        Returns:
            List of matching events
        """
        with self._lock:
            return [e for e in self._events if e.component == component]
    
    def get_events_since(self, since: datetime) -> List[LearningEvent]:
        """
        Get events captured after a specific time (thread-safe).
        
        Args:
            since: Datetime to filter from
            
        Returns:
            List of events after timestamp
        """
        with self._lock:
            return [e for e in self._events if e.timestamp > since]
    
    def get_recent_events(self, hours: int = 24) -> List[LearningEvent]:
        """
        Get events from the last N hours (thread-safe).
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent events
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        return self.get_events_since(cutoff)
    
    def clear_events(self):
        """Clear all captured events (thread-safe)."""
        with self._lock:
            self._events.clear()
            self._performance_stats["capture_times"].clear()
            self._performance_stats["filter_times"].clear()
    
    def get_event_count(self) -> int:
        """Get total event count (thread-safe)."""
        with self._lock:
            return len(self._events)
    
    def get_milestone_count(self) -> int:
        """Get milestone event count (thread-safe)."""
        return len(self.get_milestone_events())
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for overhead monitoring.
        
        Returns:
            Dict with capture times, average overhead, max overhead
        """
        with self._lock:
            capture_times = self._performance_stats["capture_times"].copy()
            filter_times = self._performance_stats["filter_times"].copy()
        
        if not capture_times:
            return {
                "total_events": 0,
                "avg_capture_time_ms": 0,
                "max_capture_time_ms": 0,
                "avg_filter_time_ms": 0,
                "max_filter_time_ms": 0,
                "overhead_target_met": True,  # No events = no overhead
            }
        
        avg_capture = sum(capture_times) / len(capture_times)
        max_capture = max(capture_times)
        avg_filter = sum(filter_times) / len(filter_times) if filter_times else 0
        max_filter = max(filter_times) if filter_times else 0
        
        return {
            "total_events": len(capture_times),
            "avg_capture_time_ms": round(avg_capture, 2),
            "max_capture_time_ms": round(max_capture, 2),
            "avg_filter_time_ms": round(avg_filter, 2),
            "max_filter_time_ms": round(max_filter, 2),
            "overhead_target_met": avg_capture < 10.0,  # <10ms target
        }
    
    def get_category_distribution(self) -> Dict[str, int]:
        """
        Get event count by category.
        
        Returns:
            Dict mapping category names to event counts
        """
        with self._lock:
            distribution: Dict[str, int] = {}
            for event in self._events:
                category = event.event_type.category.value
                distribution[category] = distribution.get(category, 0) + 1
            return distribution
    
    def get_component_distribution(self) -> Dict[str, int]:
        """
        Get event count by component.
        
        Returns:
            Dict mapping component names to event counts
        """
        with self._lock:
            distribution: Dict[str, int] = {}
            for event in self._events:
                distribution[event.component] = distribution.get(event.component, 0) + 1
            return distribution


# Global singleton instance for convenience
_global_collector: Optional[LearningEventCollector] = None


def get_global_collector() -> LearningEventCollector:
    """
    Get or create global event collector singleton.
    
    Orchestrators can use this for convenience:
        from src.learning.event_collector import get_global_collector
        get_global_collector().capture_event(event)
    
    Returns:
        Global LearningEventCollector instance
    """
    global _global_collector
    if _global_collector is None:
        _global_collector = LearningEventCollector()
    return _global_collector


def reset_global_collector():
    """Reset global collector (useful for testing)."""
    global _global_collector
    _global_collector = None
