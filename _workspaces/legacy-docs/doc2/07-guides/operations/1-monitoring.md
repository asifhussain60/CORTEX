# Monitoring

**Status:** Production Ready | **Last Updated:** 2026-01-21

Comprehensive monitoring setup for CORTEX.

## Overview

Monitoring provides visibility into system health, performance, and user activity.

## Metrics to Monitor

| Metric | Target | Alert |
|--------|--------|-------|
| API Response Time | < 500ms | > 1s |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 70% | > 85% |
| Memory Usage | < 80% | > 90% |
| Database Connections | < 80 | > 100 |

## Implementation

```python
from cortex.observability.metrics import MetricsCollector

collector = MetricsCollector()
collector.record_request(duration=0.45, success=True)
collector.record_error("timeout")
```

## Related Resources

- [Monitoring Dashboard Tutorial](../../06-tutorials/operations/2-monitoring-dashboard.md)
- [Operations Guide](0-overview.md)
