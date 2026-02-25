# Alerting

**Status:** Production Ready | **Last Updated:** 2026-01-21

Configure alerts for CORTEX monitoring.

## Overview

Alerting enables rapid response to issues in production.

## Alert Types

### Critical (P1)
- System down
- Data loss
- Security breach

### High (P2)
- Error rate > 5%
- Response time > 5s
- Database unavailable

### Medium (P3)
- Error rate > 1%
- Response time > 2s
- High resource usage

### Low (P4)
- Warnings in logs
- Minor performance degradation

## Configuration

```yaml
alerts:
  api_error_rate:
    condition: error_rate > 0.01
    severity: P2
    actions:
      - notify_slack
      - create_incident
  
  response_time:
    condition: p95_latency > 2000
    severity: P3
    actions:
      - notify_slack
      - page_oncall
```

## Related Resources

- [Incident Response Tutorial](../../06-tutorials/operations/3-incident-response.md)
- [Operations Guide](0-overview.md)
