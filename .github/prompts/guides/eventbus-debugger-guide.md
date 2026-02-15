# EventBus Debugger User Guide

**Authority:** PHASE-3 Stage 3 - ENH-089 Documentation  
**Version:** 1.0  
**Date:** 2026-02-13

---

## Overview

The EventBus Debugger provides comprehensive tools for monitoring, analyzing, and debugging event-driven workflows in CORTEX. It consists of three integrated components:

1. **Event Replay Debugger** - Filter and replay events for debugging
2. **Dead Letter Queue Inspector** - Analyze and retry failed events
3. **EventBus Health Monitor** - Monitor performance and health metrics

---

## Architecture

```
EventBus (cortex/core/event_bus.py)
    ↓
Event Logging (.cortex/events.jsonl)
    ↓
┌────────────────────────────────────┐
│ Event Replay Debugger              │ → Filter, replay, analyze
│ DLQ Inspector                      │ → Failed events, retry
│ EventBus Health Monitor            │ → Metrics, health checks
└────────────────────────────────────┘
```

---

## Event Class Enhancement

All events now include debugging metadata:

```python
from cortex.core.event_bus import Event

event = Event(
    type="test.started",
    payload={"test_id": "test_001"},
    correlation_id="req-123",    # Request tracing
    event_id="evt-456",          # Unique ID (auto-generated)
    source="TDDOrchestrator",    # Originating component
    priority=1,                  # 0=critical, 1=high, 2=normal, 3=low
    timestamp=datetime.now()     # Auto-generated
)
```

---

## Component 1: Event Replay Debugger

### Purpose

Replay events from log files for debugging distributed workflows and multi-cycle TDD operations.

### Basic Usage

```python
from cortex.infrastructure.event_replay_debugger import (
    EventReplayDebugger,
    ReplayFilter
)

# Initialize debugger
debugger = EventReplayDebugger(
    log_file=".cortex/events.jsonl"
)

# Filter events by correlation ID
replay_filter = ReplayFilter(correlation_id="req-123")
events = debugger.filter_events(replay_filter)

print(f"Found {len(events)} events for request req-123")
```

### Filtering Options

#### By Correlation ID

```python
# All events for a specific request
replay_filter = ReplayFilter(correlation_id="req-123")
events = debugger.filter_events(replay_filter)
```

#### By Event Type

```python
# All test failures
replay_filter = ReplayFilter(event_types=["test.failed", "test.error"])
events = debugger.filter_events(replay_filter)
```

#### By Source Component

```python
# All events from TDD Orchestrator
replay_filter = ReplayFilter(source="TDDOrchestrator")
events = debugger.filter_events(replay_filter)
```

#### By Priority

```python
# Critical events only
replay_filter = ReplayFilter(priority=0)
events = debugger.filter_events(replay_filter)
```

#### By Time Range

```python
# Events in last hour
now = datetime.now()
one_hour_ago = now - timedelta(hours=1)

replay_filter = ReplayFilter(
    time_range=(one_hour_ago.isoformat(), now.isoformat())
)
events = debugger.filter_events(replay_filter)
```

#### Combined Filters

```python
# Critical test failures from last 30 minutes
replay_filter = ReplayFilter(
    event_types=["test.failed"],
    priority=0,
    time_range=(
        (datetime.now() - timedelta(minutes=30)).isoformat(),
        datetime.now().isoformat()
    )
)
events = debugger.filter_events(replay_filter, limit=50)
```

### Replaying Events

```python
# Define handler
def event_handler(event: Event):
    print(f"Replaying: {event.type} from {event.source}")
    # Process event logic here

# Replay filtered events
result = debugger.replay_events(
    events=events,
    handler=event_handler,
    stop_on_error=False  # Continue on errors
)

print(f"Replayed: {result.events_replayed}/{result.events_matched}")
print(f"Errors: {len(result.errors)}")
print(f"Duration: {result.duration_ms}ms")
```

### Correlation Analysis

Analyze all events for a specific request:

```python
analysis = debugger.analyze_correlation("req-123")

print(f"Request: {analysis['correlation_id']}")
print(f"Events: {analysis['events_found']}")
print(f"Duration: {analysis['duration_ms']}ms")

# View timeline
for event in analysis['timeline']:
    print(f"  {event['timestamp']} - {event['type']} ({event['source']})")

# Event type distribution
print("\nEvent Types:")
for event_type, count in analysis['event_types'].items():
    print(f"  {event_type}: {count}")
```

---

## Component 2: DLQ Inspector

### Purpose

Analyze failed events, identify error patterns, and perform smart retries with exponential backoff.

### Basic Usage

```python
from cortex.infrastructure.dlq_inspector import (
    DLQInspector,
    RetryStrategy
)

# Initialize inspector
inspector = DLQInspector(
    dlq_file=".cortex/dlq.jsonl"
)

# Analyze DLQ
analysis = inspector.analyze_dlq()

print(f"Total failed: {analysis.total_failed}")
print(f"Retry eligible: {analysis.retry_eligible}")
print(f"\nRecommendations:")
for rec in analysis.recommendations:
    print(f"  {rec}")
```

### Adding Failed Events

```python
from cortex.core.event_bus import Event

# When event processing fails
try:
    process_event(event)
except Exception as e:
    inspector.add_failed_event(
        event=event,
        error_message=str(e)
    )
```

### Retrieving Failed Events

```python
# All failed events
failed_events = inspector.get_failed_events()

# Critical failures only
critical_failures = inspector.get_failed_events(priority=0)

# Failures from specific source
tdd_failures = inspector.get_failed_events(source="TDDOrchestrator")

# Limited results
recent_failures = inspector.get_failed_events(limit=10)
```

### Error Categorization

The inspector automatically categorizes errors:

- **timeout** - Timeouts and deadline exceeded
- **network** - Connection and network failures
- **authorization** - Permission and auth failures
- **not_found** - Resource not found (404)
- **validation** - Invalid input or data
- **other** - Uncategorized errors

```python
analysis = inspector.analyze_dlq()

for error_type, count in analysis.error_types.items():
    print(f"{error_type}: {count} failures")
```

### Smart Retry

```python
from cortex.infrastructure.dlq_inspector import RetryStrategy

# Configure retry strategy
strategy = RetryStrategy(
    max_retries=3,              # Maximum retry attempts
    backoff_seconds=60,         # Base backoff duration
    exponential=True,           # Exponential backoff
    retry_priorities=[0, 1, 2]  # Retry critical, high, normal
)

# Execute smart retry
result = inspector.smart_retry(strategy)

print(f"Eligible: {result['total_eligible']}")
print(f"Retried: {result['retried']}")
print(f"Skipped: {result['skipped']}")

# View skip reasons
for reason in result['reasons']:
    print(f"  {reason}")
```

### Retry Behavior

- **Exponential Backoff:** Wait time doubles after each retry
  - Retry 1: 60 seconds
  - Retry 2: 120 seconds
  - Retry 3: 240 seconds

- **Priority Filtering:** Only retry events matching configured priorities
- **Max Retries:** Stop after max_retries attempts

---

## Component 3: EventBus Health Monitor

### Purpose

Monitor EventBus performance metrics including throughput, latency, and failure rates.

### Basic Usage

```python
from cortex.observability.eventbus_health import EventBusHealthMonitor

# Initialize monitor
monitor = EventBusHealthMonitor(
    log_file=".cortex/events.jsonl",
    dlq_file=".cortex/dlq.jsonl",
    metrics_window_seconds=300  # 5-minute window
)

# Collect current metrics
metrics = monitor.collect_metrics()

print(f"Throughput: {metrics.throughput_per_second:.2f} events/sec")
print(f"Avg Latency: {metrics.avg_latency_ms:.0f}ms")
print(f"Failure Rate: {metrics.failure_rate * 100:.1f}%")
```

### Health Checks

```python
# Check overall health
health = monitor.check_health()

if health.healthy:
    print("✅ EventBus healthy")
else:
    print("⚠️ EventBus issues detected")
    
    for warning in health.warnings:
        print(f"  {warning}")
    
    print("\nRecommendations:")
    for rec in health.recommendations:
        print(f"  {rec}")
```

### Health Thresholds

Default thresholds can be customized:

```python
monitor = EventBusHealthMonitor(
    log_file=".cortex/events.jsonl",
    dlq_file=".cortex/dlq.jsonl"
)

# Customize thresholds
monitor.min_throughput = 1.0       # 1 event/sec minimum
monitor.max_latency_ms = 3000      # 3 second max latency
monitor.max_failure_rate = 0.02    # 2% max failure rate
```

### Metrics Distribution

```python
metrics = monitor.collect_metrics()

# Event type distribution
print("Event Types:")
for event_type, count in metrics.event_type_distribution.items():
    print(f"  {event_type}: {count}")

# Source distribution
print("\nSources:")
for source, count in metrics.source_distribution.items():
    print(f"  {source}: {count}")

# Priority distribution
print("\nPriorities:")
for priority, count in metrics.priority_distribution.items():
    priority_name = ["critical", "high", "normal", "low"][priority]
    print(f"  {priority_name}: {count}")
```

### Historical Metrics

```python
# Get metrics for last hour (5-minute intervals)
history = monitor.get_metrics_history(
    duration_minutes=60,
    interval_minutes=5
)

print(f"Collected {len(history)} snapshots\n")

for snapshot in history:
    print(f"Time: {snapshot.timestamp.strftime('%H:%M:%S')}")
    print(f"  Throughput: {snapshot.throughput_per_second:.2f} events/sec")
    print(f"  Latency: {snapshot.avg_latency_ms:.0f}ms")
    print(f"  Failure Rate: {snapshot.failure_rate * 100:.1f}%")
```

---

## Integration Patterns

### Pattern 1: Debug Failed TDD Cycle

```python
# 1. Find correlation ID from logs
correlation_id = "tdd-cycle-123"

# 2. Analyze all events for that cycle
debugger = EventReplayDebugger(".cortex/events.jsonl")
analysis = debugger.analyze_correlation(correlation_id)

print(f"TDD Cycle Timeline:")
for event in analysis['timeline']:
    print(f"  {event['timestamp']} - {event['type']}")

# 3. Check for failures in DLQ
inspector = DLQInspector(".cortex/dlq.jsonl")
failed_events = inspector.get_failed_events()

cycle_failures = [
    fe for fe in failed_events
    if fe.event.correlation_id == correlation_id
]

print(f"\nFailures: {len(cycle_failures)}")
for fe in cycle_failures:
    print(f"  {fe.error_message}")
```

### Pattern 2: Monitor Production Health

```python
import time

monitor = EventBusHealthMonitor(
    log_file=".cortex/events.jsonl",
    dlq_file=".cortex/dlq.jsonl"
)

while True:
    health = monitor.check_health()
    
    if not health.healthy:
        # Alert on health issues
        print(f"⚠️ ALERT: EventBus unhealthy")
        for warning in health.warnings:
            print(f"  {warning}")
        
        # Trigger automated response
        if not health.failure_rate_ok:
            inspector = DLQInspector(".cortex/dlq.jsonl")
            analysis = inspector.analyze_dlq()
            # Take action based on analysis
    
    time.sleep(60)  # Check every minute
```

### Pattern 3: Automated Retry with Alerting

```python
from datetime import datetime, timedelta

inspector = DLQInspector(".cortex/dlq.jsonl")

# Retry failed events hourly
strategy = RetryStrategy(
    max_retries=3,
    backoff_seconds=300,  # 5 minutes
    exponential=True,
    retry_priorities=[0, 1]  # Critical and high only
)

result = inspector.smart_retry(strategy)

# Alert if many retries skipped
if result['skipped'] > 10:
    print(f"⚠️ ALERT: {result['skipped']} events skipped for retry")
    
    # Analyze why
    analysis = inspector.analyze_dlq()
    print("\nError Patterns:")
    for error_type, count in analysis.error_types.items():
        print(f"  {error_type}: {count}")
```

---

## Best Practices

### 1. Use Correlation IDs Consistently

```python
# Generate at request entry point
correlation_id = f"req-{uuid.uuid4()}"

# Pass through all event emissions
event = Event(
    type="processing.started",
    payload={},
    correlation_id=correlation_id,  # Always include
    source="MyOrchestrator"
)
```

### 2. Set Appropriate Priorities

```python
# Critical - system failures, data corruption
Event(type="database.corruption", priority=0)

# High - feature failures, user impact
Event(type="api.error", priority=1)

# Normal - routine operations
Event(type="cache.miss", priority=2)

# Low - debug/trace events
Event(type="debug.trace", priority=3)
```

### 3. Monitor DLQ Size

```python
inspector = DLQInspector(".cortex/dlq.jsonl")
analysis = inspector.analyze_dlq()

if analysis.total_failed > 100:
    print("⚠️ DLQ accumulation detected - investigate")
```

### 4. Regular Health Checks

```python
# Scheduled health check (cron job)
monitor = EventBusHealthMonitor(
    log_file=".cortex/events.jsonl",
    dlq_file=".cortex/dlq.jsonl"
)

health = monitor.check_health()

# Log to monitoring system
log_to_prometheus({
    "eventbus_healthy": 1 if health.healthy else 0,
    "eventbus_throughput": metrics.throughput_per_second,
    "eventbus_latency": metrics.avg_latency_ms,
    "eventbus_failure_rate": metrics.failure_rate
})
```

---

## Troubleshooting

### Issue: No Events in Log

**Symptoms:** `filter_events()` returns empty list

**Solutions:**
1. Verify EventBus initialized with `log_file` parameter
2. Check file permissions on `.cortex/events.jsonl`
3. Confirm events are being published
4. Verify time range filter if used

### Issue: High Failure Rate

**Symptoms:** `failure_rate > 0.05` (5%)

**Solutions:**
1. Use DLQInspector to analyze error patterns
2. Check for network/timeout issues
3. Verify event handlers are robust
4. Review error categorization for insights

### Issue: Replay Not Working

**Symptoms:** `replay_events()` shows 0 replayed

**Solutions:**
1. Verify handler function signature: `def handler(event: Event)`
2. Check for exceptions in handler
3. Use `stop_on_error=False` to continue past errors
4. Verify events match filter criteria

---

## API Reference Summary

### EventReplayDebugger

```python
debugger = EventReplayDebugger(log_file: str)

events = debugger.filter_events(
    replay_filter: ReplayFilter,
    limit: Optional[int] = None
) -> List[Event]

result = debugger.replay_events(
    events: List[Event],
    handler: Callable[[Event], None],
    stop_on_error: bool = False
) -> ReplayResult

analysis = debugger.analyze_correlation(
    correlation_id: str
) -> Dict[str, Any]
```

### DLQInspector

```python
inspector = DLQInspector(dlq_file: str)

inspector.add_failed_event(event: Event, error_message: str)

failed_events = inspector.get_failed_events(
    priority: Optional[int] = None,
    source: Optional[str] = None,
    limit: Optional[int] = None
) -> List[FailedEvent]

analysis = inspector.analyze_dlq() -> DLQAnalysis

result = inspector.smart_retry(strategy: RetryStrategy) -> Dict[str, Any]
```

### EventBusHealthMonitor

```python
monitor = EventBusHealthMonitor(
    log_file: str,
    dlq_file: str,
    metrics_window_seconds: int = 300
)

metrics = monitor.collect_metrics() -> EventMetrics

health = monitor.check_health() -> HealthStatus

history = monitor.get_metrics_history(
    duration_minutes: int = 60,
    interval_minutes: int = 5
) -> List[EventMetrics]
```

---

## See Also

- **Multi-Cycle TDD User Guide** - TDD workflow and event integration
- **EventBus Implementation** - `cortex/core/event_bus.py`
- **Event Schemas** - `cortex/models/events.py`
- **Orchestrator Event Patterns** - `cortex/wiring/specifications/`

---

**Version:** 1.0 | **Last Updated:** 2026-02-13  
**Authority:** PHASE-3 Stage 3 - ENH-089 EventBus Debugger Documentation
