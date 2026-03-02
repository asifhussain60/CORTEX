"""
Dead Letter Queue Inspector for CORTEX EventBus.

Analyzes failed events, provides smart retry logic, and helps diagnose
event processing failures in distributed workflows.

Authority: WAVE-3 Stage 2 - ENH-089 EventBus Debugger
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import json

from cortex.core.event_bus import Event


@dataclass
class FailedEvent:
    """
    Failed event with error context.

    Attributes:
        event: Original event that failed
        error_message: Error description
        failure_time: When the failure occurred
        retry_count: Number of retry attempts
        last_retry: Last retry attempt timestamp
    """
    event: Event
    error_message: str
    failure_time: datetime
    retry_count: int = 0
    last_retry: Optional[datetime] = None


@dataclass
class RetryStrategy:
    """
    Retry strategy configuration.

    Attributes:
        max_retries: Maximum retry attempts
        backoff_seconds: Base backoff duration
        exponential: Use exponential backoff
        retry_priorities: Priority levels to retry (0=critical, 1=high, etc.)
    """
    max_retries: int = 3
    backoff_seconds: int = 60
    exponential: bool = True
    retry_priorities: List[int] = None

    def __post_init__(self):
        if self.retry_priorities is None:
            self.retry_priorities = [0, 1, 2]  # Critical, high, normal


@dataclass
class DLQAnalysis:
    """
    Dead Letter Queue analysis results.

    Attributes:
        total_failed: Total failed events
        retry_eligible: Events eligible for retry
        error_types: Error frequency by type
        failure_sources: Failure frequency by source
        priority_distribution: Failed events by priority
        recommendations: List of recommended actions
    """
    total_failed: int
    retry_eligible: int
    error_types: Dict[str, int]
    failure_sources: Dict[str, int]
    priority_distribution: Dict[int, int]
    recommendations: List[str]


class DLQInspector:
    """
    Dead Letter Queue Inspector for CORTEX EventBus.

    Analyzes failed events, provides smart retry logic, and helps diagnose
    event processing failures across orchestrators.
    """

    def __init__(self, dlq_file: str) -> None:
        """
        Initialize DLQ inspector.

        Args:
            dlq_file: Path to dead letter queue JSONL file
        """
        self.dlq_file = Path(dlq_file)
        self.dlq_file.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.dlq_file.exists():
            self.dlq_file.touch()

    def add_failed_event(
        self,
        event: Event,
        error_message: str
    ) -> None:
        """
        Add failed event to DLQ.

        Args:
            event: Failed event
            error_message: Error description
        """
        failed_event = FailedEvent(
            event=event,
            error_message=error_message,
            failure_time=datetime.now()
        )

        dlq_entry = {
            "event": {
                "type": event.type,
                "payload": event.payload,
                "correlation_id": event.correlation_id,
                "event_id": event.event_id,
                "source": event.source,
                "priority": event.priority,
                "timestamp": event.timestamp.isoformat()
            },
            "error_message": error_message,
            "failure_time": failed_event.failure_time.isoformat(),
            "retry_count": 0,
            "last_retry": None
        }

        with open(self.dlq_file, 'a') as f:
            f.write(json.dumps(dlq_entry) + '\n')

    def get_failed_events(
        self,
        priority: Optional[int] = None,
        source: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[FailedEvent]:
        """
        Retrieve failed events from DLQ.

        Args:
            priority: Filter by priority level
            source: Filter by source component
            limit: Maximum events to return

        Returns:
            List of FailedEvent objects
        """
        failed_events = []

        if not self.dlq_file.exists():
            return failed_events

        with open(self.dlq_file, 'r') as f:
            for line in f:
                try:
                    dlq_entry = json.loads(line.strip())

                    # Apply filters
                    event_data = dlq_entry["event"]
                    if priority is not None and event_data.get("priority") != priority:
                        continue
                    if source and event_data.get("source") != source:
                        continue

                    # Reconstruct FailedEvent
                    failed_event = self._reconstruct_failed_event(dlq_entry)
                    failed_events.append(failed_event)

                    if limit and len(failed_events) >= limit:
                        break

                except (json.JSONDecodeError, KeyError):
                    continue

        return failed_events

    def analyze_dlq(self) -> DLQAnalysis:
        """
        Analyze dead letter queue for patterns and recommendations.

        Returns:
            DLQAnalysis with statistics and recommendations
        """
        failed_events = self.get_failed_events()

        if not failed_events:
            return DLQAnalysis(
                total_failed=0,
                retry_eligible=0,
                error_types={},
                failure_sources={},
                priority_distribution={},
                recommendations=["✅ DLQ empty - no failed events"]
            )

        # Analyze error types
        error_types = {}
        for fe in failed_events:
            error_key = self._categorize_error(fe.error_message)
            error_types[error_key] = error_types.get(error_key, 0) + 1

        # Analyze failure sources
        failure_sources = {}
        for fe in failed_events:
            source = fe.event.source or "unknown"
            failure_sources[source] = failure_sources.get(source, 0) + 1

        # Analyze priority distribution
        priority_dist = {}
        for fe in failed_events:
            priority = fe.event.priority
            priority_dist[priority] = priority_dist.get(priority, 0) + 1

        # Count retry-eligible events
        retry_eligible = sum(
            1 for fe in failed_events
            if fe.retry_count < 3 and fe.event.priority <= 2
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            failed_events,
            error_types,
            failure_sources
        )

        return DLQAnalysis(
            total_failed=len(failed_events),
            retry_eligible=retry_eligible,
            error_types=error_types,
            failure_sources=failure_sources,
            priority_distribution=priority_dist,
            recommendations=recommendations
        )

    def smart_retry(
        self,
        strategy: RetryStrategy
    ) -> Dict[str, Any]:
        """
        Perform smart retry of failed events based on strategy.

        Args:
            strategy: Retry strategy configuration

        Returns:
            Retry results dictionary
        """
        failed_events = self.get_failed_events()

        retry_results = {
            "total_eligible": 0,
            "retried": 0,
            "skipped": 0,
            "reasons": []
        }

        for fe in failed_events:
            # Check if eligible for retry
            if not self._is_retry_eligible(fe, strategy):
                retry_results["skipped"] += 1
                continue

            retry_results["total_eligible"] += 1

            # Calculate backoff
            if self._should_retry_now(fe, strategy):
                retry_results["retried"] += 1
                # Actual retry would happen here via EventBus.publish()
                # For now, just mark as retried in logs
                self._mark_retried(fe)
            else:
                retry_results["reasons"].append(
                    f"Event {fe.event.event_id}: Backoff not elapsed"
                )

        return retry_results

    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message into error type."""
        error_lower = error_message.lower()

        if "timeout" in error_lower:
            return "timeout"
        elif "connection" in error_lower or "network" in error_lower:
            return "network"
        elif "permission" in error_lower or "auth" in error_lower:
            return "authorization"
        elif "not found" in error_lower or "404" in error_lower:
            return "not_found"
        elif "validation" in error_lower or "invalid" in error_lower:
            return "validation"
        else:
            return "other"

    def _generate_recommendations(
        self,
        failed_events: List[FailedEvent],
        error_types: Dict[str, int],
        failure_sources: Dict[str, int]
    ) -> List[str]:
        """Generate actionable recommendations based on DLQ analysis."""
        recommendations = []

        # Error type recommendations
        if error_types.get("timeout", 0) > 5:
            recommendations.append(
                "⚠️ High timeout rate - consider increasing timeout thresholds"
            )

        if error_types.get("network", 0) > 3:
            recommendations.append(
                "⚠️ Network failures detected - check connectivity"
            )

        if error_types.get("authorization", 0) > 0:
            recommendations.append(
                "🔒 Authorization failures - verify credentials/permissions"
            )

        # Source recommendations
        top_source = max(failure_sources.items(), key=lambda x: x[1])
        if top_source[1] > 10:
            recommendations.append(
                f"🎯 Focus on {top_source[0]} - highest failure source ({top_source[1]} events)"
            )

        # Retry recommendations
        retry_eligible = sum(
            1 for fe in failed_events
            if fe.retry_count < 3
        )
        if retry_eligible > 0:
            recommendations.append(
                f"🔄 {retry_eligible} events eligible for retry"
            )

        return recommendations or ["✅ No critical issues detected"]

    def _is_retry_eligible(
        self,
        failed_event: FailedEvent,
        strategy: RetryStrategy
    ) -> bool:
        """Check if event is eligible for retry."""
        # Max retries check
        if failed_event.retry_count >= strategy.max_retries:
            return False

        # Priority check
        if failed_event.event.priority not in strategy.retry_priorities:
            return False

        return True

    def _should_retry_now(
        self,
        failed_event: FailedEvent,
        strategy: RetryStrategy
    ) -> bool:
        """Check if backoff period has elapsed."""
        if failed_event.last_retry is None:
            # First retry - use failure time
            elapsed = datetime.now() - failed_event.failure_time
        else:
            elapsed = datetime.now() - failed_event.last_retry

        # Calculate backoff
        if strategy.exponential:
            backoff = strategy.backoff_seconds * (2 ** failed_event.retry_count)
        else:
            backoff = strategy.backoff_seconds

        return elapsed >= timedelta(seconds=backoff)

    def _mark_retried(self, failed_event: FailedEvent) -> None:
        """Mark event as retried in DLQ (increment retry count)."""
        import logging
        logging.getLogger(__name__).debug(
            "_mark_retried: event_id=%s retry_count=%d -> %d",
            failed_event.event_id,
            failed_event.retry_count,
            failed_event.retry_count + 1,
        )
        failed_event.retry_count += 1

    def _reconstruct_failed_event(self, dlq_entry: Dict[str, Any]) -> FailedEvent:
        """Reconstruct FailedEvent from DLQ entry."""
        event_data = dlq_entry["event"]

        event = Event(
            type=event_data["type"],
            payload=event_data["payload"],
            correlation_id=event_data.get("correlation_id"),
            event_id=event_data.get("event_id", "unknown"),
            source=event_data.get("source"),
            priority=event_data.get("priority", 2),
            timestamp=datetime.fromisoformat(event_data["timestamp"])
        )

        return FailedEvent(
            event=event,
            error_message=dlq_entry["error_message"],
            failure_time=datetime.fromisoformat(dlq_entry["failure_time"]),
            retry_count=dlq_entry.get("retry_count", 0),
            last_retry=(
                datetime.fromisoformat(dlq_entry["last_retry"])
                if dlq_entry.get("last_retry")
                else None
            )
        )
