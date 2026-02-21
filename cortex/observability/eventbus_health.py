"""
EventBus Health Monitor for CORTEX.

Collects metrics on event throughput, latency, and failures to monitor
the health of distributed workflows and orchestrator communication.

Authority: WAVE-3 Stage 2 - ENH-089 EventBus Debugger
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from cortex.core.event_bus import Event


@dataclass
class EventMetrics:
    """
    EventBus metrics snapshot.
    
    Attributes:
        timestamp: When metrics were captured
        throughput_per_second: Events processed per second
        avg_latency_ms: Average event processing latency
        failure_rate: Percentage of failed events
        event_type_distribution: Events by type
        source_distribution: Events by source
        priority_distribution: Events by priority
    """
    timestamp: datetime
    throughput_per_second: float
    avg_latency_ms: float
    failure_rate: float
    event_type_distribution: Dict[str, int]
    source_distribution: Dict[str, int]
    priority_distribution: Dict[int, int]


@dataclass
class HealthStatus:
    """
    EventBus health status.
    
    Attributes:
        healthy: Overall health status
        throughput_ok: Throughput within acceptable range
        latency_ok: Latency within acceptable range
        failure_rate_ok: Failure rate within acceptable range
        warnings: List of warning messages
        recommendations: List of recommended actions
    """
    healthy: bool
    throughput_ok: bool
    latency_ok: bool
    failure_rate_ok: bool
    warnings: List[str]
    recommendations: List[str]


class EventBusHealthMonitor:
    """
    EventBus health monitor for CORTEX.
    
    Collects and analyzes event metrics to monitor the health of distributed
    workflows, orchestrator communication, and event processing performance.
    """
    
    def __init__(
        self,
        log_file: str,
        dlq_file: str,
        metrics_window_seconds: int = 300
    ) -> None:
        """
        Initialize EventBus health monitor.
        
        Args:
            log_file: Path to EventBus JSONL log file
            dlq_file: Path to DLQ JSONL log file
            metrics_window_seconds: Time window for metrics calculation (default 5 min)
        """
        self.log_file = Path(log_file)
        self.dlq_file = Path(dlq_file)
        self.metrics_window = timedelta(seconds=metrics_window_seconds)
        
        # Health thresholds
        self.min_throughput = 0.1  # events/sec
        self.max_latency_ms = 5000  # 5 seconds
        self.max_failure_rate = 0.05  # 5%
    
    def collect_metrics(self) -> EventMetrics:
        """
        Collect current EventBus metrics.
        
        Returns:
            EventMetrics snapshot
        """
        now = datetime.now()
        cutoff_time = now - self.metrics_window
        
        # Parse events from log
        events = self._parse_events_since(cutoff_time)
        
        if not events:
            return EventMetrics(
                timestamp=now,
                throughput_per_second=0.0,
                avg_latency_ms=0.0,
                failure_rate=0.0,
                event_type_distribution={},
                source_distribution={},
                priority_distribution={}
            )
        
        # Calculate throughput
        duration_seconds = self.metrics_window.total_seconds()
        throughput = len(events) / duration_seconds
        
        # Calculate latency (time between events)
        latencies = []
        for i in range(1, len(events)):
            latency = (events[i].timestamp - events[i-1].timestamp).total_seconds() * 1000
            latencies.append(latency)
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        # Count failed events
        failed_count = self._count_failed_events_since(cutoff_time)
        failure_rate = failed_count / len(events) if events else 0.0
        
        # Analyze distributions
        event_types = {}
        sources = {}
        priorities = {}
        
        for event in events:
            event_types[event.type] = event_types.get(event.type, 0) + 1
            if event.source:
                sources[event.source] = sources.get(event.source, 0) + 1
            priorities[event.priority] = priorities.get(event.priority, 0) + 1
        
        return EventMetrics(
            timestamp=now,
            throughput_per_second=throughput,
            avg_latency_ms=avg_latency,
            failure_rate=failure_rate,
            event_type_distribution=event_types,
            source_distribution=sources,
            priority_distribution=priorities
        )
    
    def check_health(self) -> HealthStatus:
        """
        Check EventBus health status.
        
        Returns:
            HealthStatus with diagnostics
        """
        metrics = self.collect_metrics()
        
        warnings = []
        recommendations = []
        
        # Check throughput
        throughput_ok = metrics.throughput_per_second >= self.min_throughput
        if not throughput_ok:
            warnings.append(
                f"⚠️ Low throughput: {metrics.throughput_per_second:.2f} events/sec "
                f"(threshold: {self.min_throughput})"
            )
            recommendations.append(
                "Check if event publishers are functioning correctly"
            )
        
        # Check latency
        latency_ok = metrics.avg_latency_ms <= self.max_latency_ms
        if not latency_ok:
            warnings.append(
                f"⚠️ High latency: {metrics.avg_latency_ms:.0f}ms "
                f"(threshold: {self.max_latency_ms}ms)"
            )
            recommendations.append(
                "Review event handler performance and optimize processing"
            )
        
        # Check failure rate
        failure_rate_ok = metrics.failure_rate <= self.max_failure_rate
        if not failure_rate_ok:
            warnings.append(
                f"⚠️ High failure rate: {metrics.failure_rate * 100:.1f}% "
                f"(threshold: {self.max_failure_rate * 100:.1f}%)"
            )
            recommendations.append(
                "Inspect DLQ for error patterns using DLQInspector.analyze_dlq()"
            )
        
        # Check for event distribution anomalies
        if metrics.source_distribution:
            top_source = max(
                metrics.source_distribution.items(),
                key=lambda x: x[1]
            )
            if top_source[1] > len(metrics.source_distribution) * 0.8:
                warnings.append(
                    f"⚠️ Event concentration: {top_source[0]} accounts for "
                    f"{top_source[1] / sum(metrics.source_distribution.values()) * 100:.0f}% of events"
                )
        
        healthy = throughput_ok and latency_ok and failure_rate_ok
        
        if healthy and not warnings:
            recommendations.append("✅ EventBus operating normally")
        
        return HealthStatus(
            healthy=healthy,
            throughput_ok=throughput_ok,
            latency_ok=latency_ok,
            failure_rate_ok=failure_rate_ok,
            warnings=warnings or ["✅ No warnings"],
            recommendations=recommendations
        )
    
    def get_metrics_history(
        self,
        duration_minutes: int = 60,
        interval_minutes: int = 5
    ) -> List[EventMetrics]:
        """
        Get historical metrics over a time period.
        
        Args:
            duration_minutes: Total duration to analyze
            interval_minutes: Interval between metric snapshots
            
        Returns:
            List of EventMetrics snapshots
        """
        history = []
        now = datetime.now()
        
        # Calculate snapshots
        for i in range(duration_minutes // interval_minutes):
            end_time = now - timedelta(minutes=i * interval_minutes)
            start_time = end_time - timedelta(minutes=interval_minutes)
            
            # Parse events in this interval
            events = self._parse_events_between(start_time, end_time)
            
            if events:
                # Calculate metrics for this interval
                throughput = len(events) / (interval_minutes * 60)
                
                # Simple average latency for interval
                latencies = []
                for j in range(1, len(events)):
                    latency = (
                        events[j].timestamp - events[j-1].timestamp
                    ).total_seconds() * 1000
                    latencies.append(latency)
                avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
                
                # Count failures
                failed_count = self._count_failed_events_between(start_time, end_time)
                failure_rate = failed_count / len(events) if events else 0.0
                
                # Distributions
                event_types = {}
                sources = {}
                priorities = {}
                
                for event in events:
                    event_types[event.type] = event_types.get(event.type, 0) + 1
                    if event.source:
                        sources[event.source] = sources.get(event.source, 0) + 1
                    priorities[event.priority] = priorities.get(event.priority, 0) + 1
                
                metrics = EventMetrics(
                    timestamp=end_time,
                    throughput_per_second=throughput,
                    avg_latency_ms=avg_latency,
                    failure_rate=failure_rate,
                    event_type_distribution=event_types,
                    source_distribution=sources,
                    priority_distribution=priorities
                )
                
                history.append(metrics)
        
        return list(reversed(history))  # Chronological order
    
    def _parse_events_since(self, cutoff_time: datetime) -> List[Event]:
        """Parse events from log file since cutoff time."""
        events = []
        
        if not self.log_file.exists():
            return events
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(log_entry["timestamp"])
                    
                    if timestamp < cutoff_time:
                        continue
                    
                    # Reconstruct Event
                    payload = log_entry.get("payload", {})
                    event = Event(
                        type=log_entry.get("type", "unknown"),
                        payload=payload,
                        correlation_id=payload.get("correlation_id"),
                        event_id=payload.get("event_id", "unknown"),
                        source=payload.get("source"),
                        priority=payload.get("priority", 2),
                        timestamp=timestamp
                    )
                    events.append(event)
                    
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        return sorted(events, key=lambda e: e.timestamp)
    
    def _parse_events_between(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Event]:
        """Parse events from log file between two times."""
        events = []
        
        if not self.log_file.exists():
            return events
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(log_entry["timestamp"])
                    
                    if not (start_time <= timestamp <= end_time):
                        continue
                    
                    # Reconstruct Event
                    payload = log_entry.get("payload", {})
                    event = Event(
                        type=log_entry.get("type", "unknown"),
                        payload=payload,
                        correlation_id=payload.get("correlation_id"),
                        event_id=payload.get("event_id", "unknown"),
                        source=payload.get("source"),
                        priority=payload.get("priority", 2),
                        timestamp=timestamp
                    )
                    events.append(event)
                    
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        return sorted(events, key=lambda e: e.timestamp)
    
    def _count_failed_events_since(self, cutoff_time: datetime) -> int:
        """Count failed events in DLQ since cutoff time."""
        if not self.dlq_file.exists():
            return 0
        
        count = 0
        with open(self.dlq_file, 'r') as f:
            for line in f:
                try:
                    dlq_entry = json.loads(line.strip())
                    failure_time = datetime.fromisoformat(dlq_entry["failure_time"])
                    
                    if failure_time >= cutoff_time:
                        count += 1
                        
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        return count
    
    def _count_failed_events_between(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> int:
        """Count failed events in DLQ between two times."""
        if not self.dlq_file.exists():
            return 0
        
        count = 0
        with open(self.dlq_file, 'r') as f:
            for line in f:
                try:
                    dlq_entry = json.loads(line.strip())
                    failure_time = datetime.fromisoformat(dlq_entry["failure_time"])
                    
                    if start_time <= failure_time <= end_time:
                        count += 1
                        
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        return count
