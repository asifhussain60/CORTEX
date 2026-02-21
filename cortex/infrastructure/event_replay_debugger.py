"""
Event Replay Debugger for CORTEX EventBus.

Provides event filtering, replay, and analysis capabilities for debugging
distributed workflows and multi-cycle TDD operations.

Authority: WAVE-3 Stage 2 - ENH-089 EventBus Debugger
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import json

from cortex.core.event_bus import Event


@dataclass
class ReplayFilter:
    """
    Filter criteria for event replay.
    
    Attributes:
        correlation_id: Filter by request correlation ID
        event_types: Filter by event type(s)
        source: Filter by originating component
        priority: Filter by priority level
        time_range: Tuple of (start_time, end_time) ISO-8601 strings
    """
    correlation_id: Optional[str] = None
    event_types: Optional[List[str]] = None
    source: Optional[str] = None
    priority: Optional[int] = None
    time_range: Optional[tuple[str, str]] = None


@dataclass
class ReplayResult:
    """
    Result of event replay operation.
    
    Attributes:
        events_replayed: Number of events replayed
        events_matched: Total events matching filter
        success: Whether replay completed successfully
        errors: List of error messages
        duration_ms: Replay duration in milliseconds
    """
    events_replayed: int
    events_matched: int
    success: bool
    errors: List[str]
    duration_ms: float


class EventReplayDebugger:
    """
    Event replay debugger for CORTEX EventBus.
    
    Provides filtering, replay, and analysis of event streams for debugging
    distributed workflows, multi-cycle TDD, and orchestrator communication.
    """
    
    def __init__(self, log_file: str) -> None:
        """
        Initialize event replay debugger.
        
        Args:
            log_file: Path to EventBus JSONL log file
        """
        self.log_file = Path(log_file)
        if not self.log_file.exists():
            raise FileNotFoundError(f"Event log not found: {log_file}")
    
    def filter_events(
        self,
        replay_filter: ReplayFilter,
        limit: Optional[int] = None
    ) -> List[Event]:
        """
        Filter events from log file based on criteria.
        
        Args:
            replay_filter: Filter criteria
            limit: Maximum number of events to return
            
        Returns:
            List of matching Event objects
        """
        matched_events = []
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    
                    # Apply filters
                    if not self._matches_filter(log_entry, replay_filter):
                        continue
                    
                    # Reconstruct Event object
                    event = self._reconstruct_event(log_entry)
                    matched_events.append(event)
                    
                    if limit and len(matched_events) >= limit:
                        break
                        
                except (json.JSONDecodeError, KeyError) as e:
                    # Skip malformed entries
                    continue
        
        return matched_events
    
    def replay_events(
        self,
        events: List[Event],
        handler: Callable[[Event], None],
        stop_on_error: bool = False
    ) -> ReplayResult:
        """
        Replay events through a handler function.
        
        Args:
            events: Events to replay
            handler: Function to process each event
            stop_on_error: Stop replay on first error
            
        Returns:
            ReplayResult with statistics
        """
        start_time = datetime.now()
        errors = []
        replayed = 0
        
        for event in events:
            try:
                handler(event)
                replayed += 1
            except Exception as e:
                errors.append(f"Event {event.event_id}: {str(e)}")
                if stop_on_error:
                    break
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return ReplayResult(
            events_replayed=replayed,
            events_matched=len(events),
            success=len(errors) == 0,
            errors=errors,
            duration_ms=duration_ms
        )
    
    def analyze_correlation(
        self,
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Analyze all events for a specific correlation ID.
        
        Args:
            correlation_id: Request correlation ID to analyze
            
        Returns:
            Analysis dictionary with event timeline and statistics
        """
        replay_filter = ReplayFilter(correlation_id=correlation_id)
        events = self.filter_events(replay_filter)
        
        if not events:
            return {
                "correlation_id": correlation_id,
                "events_found": 0,
                "timeline": []
            }
        
        # Build timeline
        timeline = []
        for event in events:
            timeline.append({
                "timestamp": event.timestamp.isoformat(),
                "type": event.type,
                "source": event.source,
                "priority": event.priority,
                "event_id": event.event_id
            })
        
        # Calculate statistics
        event_types = {}
        sources = {}
        for event in events:
            event_types[event.type] = event_types.get(event.type, 0) + 1
            if event.source:
                sources[event.source] = sources.get(event.source, 0) + 1
        
        return {
            "correlation_id": correlation_id,
            "events_found": len(events),
            "timeline": sorted(timeline, key=lambda x: x["timestamp"]),
            "event_types": event_types,
            "sources": sources,
            "duration_ms": (
                events[-1].timestamp - events[0].timestamp
            ).total_seconds() * 1000 if len(events) > 1 else 0
        }
    
    def _matches_filter(
        self,
        log_entry: Dict[str, Any],
        replay_filter: ReplayFilter
    ) -> bool:
        """
        Check if log entry matches filter criteria.
        
        Args:
            log_entry: Parsed log entry from JSONL
            replay_filter: Filter criteria
            
        Returns:
            True if entry matches all filter criteria
        """
        payload = log_entry.get("payload", {})
        
        # Correlation ID filter
        if replay_filter.correlation_id:
            if payload.get("correlation_id") != replay_filter.correlation_id:
                return False
        
        # Event type filter
        if replay_filter.event_types:
            if log_entry.get("type") not in replay_filter.event_types:
                return False
        
        # Source filter
        if replay_filter.source:
            if payload.get("source") != replay_filter.source:
                return False
        
        # Priority filter
        if replay_filter.priority is not None:
            if payload.get("priority") != replay_filter.priority:
                return False
        
        # Time range filter
        if replay_filter.time_range:
            start_str, end_str = replay_filter.time_range
            timestamp = datetime.fromisoformat(log_entry.get("timestamp", ""))
            start_time = datetime.fromisoformat(start_str)
            end_time = datetime.fromisoformat(end_str)
            
            if not (start_time <= timestamp <= end_time):
                return False
        
        return True
    
    def _reconstruct_event(self, log_entry: Dict[str, Any]) -> Event:
        """
        Reconstruct Event object from log entry.
        
        Args:
            log_entry: Parsed log entry from JSONL
            
        Returns:
            Reconstructed Event object
        """
        payload = log_entry.get("payload", {})
        
        return Event(
            type=log_entry.get("type", "unknown"),
            payload=payload,
            correlation_id=payload.get("correlation_id"),
            event_id=payload.get("event_id", "unknown"),
            source=payload.get("source"),
            priority=payload.get("priority", 2),
            timestamp=datetime.fromisoformat(
                log_entry.get("timestamp", datetime.now().isoformat())
            )
        )
