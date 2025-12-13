# Orchestration Metrics System

**Feature 10 - Orchestrator Enhancement Plan v2.0**

## Overview

Silent background metrics collection for orchestrator engagement tracking. Provides visibility into which orchestrators handle requests, execution efficiency, and performance trends.

## Features

- **Silent Collection**: <5ms overhead per operation
- **Daily Organization**: Metrics stored in `logs/orchestration-metrics/{YYYY-MM-DD}/`
- **Individual JSON Files**: Each start/complete event gets its own file
- **Automatic Instrumentation**: `@with_orchestration_metrics` decorator
- **7-Day Reports**: Aggregate statistics with success rates and durations
- **30-Day Retention**: Automatic archival to `archives/` subfolder

## Quick Start

### Using the Decorator

```python
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics

class MyOrchestrator:
    @with_orchestration_metrics("MyOrchestrator")
    def execute(self, context):
        # Your orchestration logic
        return result
```

### Manual Collection

```python
from src.operations.utilities import OrchestrationMetricsCollector

collector = OrchestrationMetricsCollector()

# Start engagement
event_id = collector.log_engagement_start(
    orchestrator_name="PlanningOrchestrator",
    operation_type="plan_generation"
)

# ... orchestrator execution ...

# Complete engagement
collector.log_engagement_complete(
    event_id=event_id,
    status="success",  # or "error"
    result_summary="Plan generated successfully"
)
```

### Generating Reports

```python
# 7-day report
report = collector.generate_report(days=7)

print(f"Total engagements: {report['total_engagements']}")
print(f"Overall success rate: {report['success_rate']:.1f}%")
print(f"Average duration: {report['avg_duration_ms']:.2f}ms")

# Per-orchestrator statistics
for orchestrator, stats in report['orchestrators'].items():
    print(f"{orchestrator}: {stats['total_engagements']} engagements")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    print(f"  Avg duration: {stats['avg_duration_ms']:.2f}ms")
```

## File Structure

```
logs/orchestration-metrics/
├── 2025-12-13/
│   ├── planningorchestrator-abc123de-start.json
│   ├── planningorchestrator-abc123de-complete.json
│   ├── tddorchestrator-def456gh-start.json
│   └── tddorchestrator-def456gh-complete.json
└── archives/  (30+ days old)
    └── 2025-11-12/
        └── ...
```

### Event JSON Schema

**Start Event:**
```json
{
  "event_type": "start",
  "event_id": "abc123de-f456-7890-abcd-ef1234567890",
  "orchestrator_name": "PlanningOrchestrator",
  "operation_type": "plan_generation",
  "timestamp": "2025-12-13T07:30:45.123456",
  "metadata": {}
}
```

**Complete Event:**
```json
{
  "event_type": "complete",
  "event_id": "abc123de-f456-7890-abcd-ef1234567890",
  "orchestrator_name": "PlanningOrchestrator",
  "timestamp": "2025-12-13T07:32:15.654321",
  "status": "success",
  "result_summary": "Generated 5-phase plan",
  "error": null,
  "duration_ms": 90531.198,
  "metadata": {}
}
```

## Instrumented Orchestrators

The following orchestrators are instrumented with automatic metrics collection:

1. **SystemMaintenanceOrchestrator** - `execute()`
2. **PlanningOrchestrator** - `execute_plan_autonomously()`, `generate_incremental_plan()`
3. **TDDImplementationOrchestrator** - `start_session()`
4. **GitCheckpointOrchestrator** - `create_checkpoint()`
5. **DocumentationOrchestrator** - `document_phase_completion()`
6. **PlanExecutionOrchestrator** - `execute_plan()`

## Performance

- **Collection overhead**: <5ms per operation (validated)
- **Storage**: Individual JSON files (100-500 bytes each)
- **Report generation**: <200ms for 7 days of data
- **Retention policy**: <50ms for cleanup

## API Reference

### OrchestrationMetricsCollector

#### Methods

**`log_engagement_start(orchestrator_name, operation_type, event_id=None, metadata=None) -> str`**
- Log orchestrator engagement start event
- Returns: `event_id` for matching with completion

**`log_engagement_complete(event_id, status="success", result_summary=None, error_message=None, duration_ms=None, metadata=None) -> bool`**
- Log orchestrator engagement completion
- Automatically calculates `duration_ms` from start timestamp if not provided
- Returns: `True` if logged successfully

**`generate_report(days=7) -> Dict[str, Any]`**
- Generate aggregated metrics report
- Returns: Dictionary with `total_engagements`, `orchestrators`, `by_day`, `time_period`, `avg_duration_ms`, `success_rate`

**`apply_retention_policy(days=30) -> int`**
- Archive metrics data older than specified days
- Returns: Number of folders archived

### @with_orchestration_metrics Decorator

**Usage:**
```python
@with_orchestration_metrics("OrchestratorName")
def my_method(self, ...):
    ...
```

**Behavior:**
- Logs `engagement_start` before function execution
- Logs `engagement_complete` after function execution
- Tracks duration automatically
- Records success/error status
- Re-raises exceptions after logging

## Git Isolation

Metrics are automatically excluded from git via `.gitignore`:
```
logs/orchestration-metrics/
```

## Integration

Metrics collection is integrated with:
- **Feature 9 (Visual Progress Bars)**: ProgressRenderer shows real-time progress
- **Feature 13 (Vision API)**: VisionContextMiddleware tracks image analysis
- **Future Feature 15 (Analytics Dashboard)**: Will consume metrics for visualizations

## Troubleshooting

### Metrics not appearing

```python
# Check if folder exists
from pathlib import Path
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
metrics_dir = Path("logs/orchestration-metrics") / today

print(f"Metrics directory: {metrics_dir}")
print(f"Exists: {metrics_dir.exists()}")
print(f"Files: {list(metrics_dir.glob('*.json'))}")
```

### Performance issues

```python
# Check collection performance
import time

collector = OrchestrationMetricsCollector()

start = time.time()
event_id = collector.log_engagement_start("Test", "test_op")
elapsed = (time.time() - start) * 1000

print(f"Collection time: {elapsed:.2f}ms (should be <5ms)")
```

## Version History

- **v1.0.0** (2025-12-13): Initial release
  - Silent background collection (<5ms)
  - Daily folder organization
  - Individual JSON file storage
  - @with_orchestration_metrics decorator
  - 7-day report generation
  - 30-day retention policy

## Author

**Asif Hussain**  
GitHub: github.com/asifhussain60/CORTEX  
Version: 3.8.1
