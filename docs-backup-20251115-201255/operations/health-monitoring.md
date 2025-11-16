---
title: Health Monitoring
description: CORTEX health monitoring and diagnostics
author: 
generated: true
version: ""
last_updated: 
---

# Health Monitoring

**Purpose:** Documentation of health monitoring and diagnostics  
**Audience:** Operations teams, administrators  
**Version:**   
**Last Updated:** 

---

## Overview

CORTEX provides comprehensive health monitoring across all tiers and agents. Health checks run automatically and can be triggered on-demand.

---

## Health Check Components

### Tier Health

**Tier 0 (Instinct):**
- Protection layer status
- Rule validation
- Governance enforcement

**Tier 1 (Working Memory):**
- Database connectivity
- FIFO queue status
- Memory usage
- Query performance

**Tier 2 (Knowledge Graph):**
- Database connectivity
- Pattern count and quality
- Decay status
- Search performance

**Tier 3 (Context Intelligence):**
- Git analysis status
- File stability metrics
- Session analytics
- Code health trends

### Agent Health

- Agent availability
- Response times
- Error rates
- Success rates

---

## Health Commands

```bash
# Check overall health
python -m src.operations.health_check

# Check specific tier
python -m src.operations.health_check --tier tier1

# Check agent status
python -m src.operations.health_check --agents

# Generate health report
python -m src.operations.health_check --report
```

---

## Health Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| **Tier 1 Query Time** | <50ms | >100ms |
| **Tier 2 Search Time** | <150ms | >300ms |
| **Tier 3 Analysis Time** | <200ms | >400ms |
| **Agent Response Time** | <2s | >5s |
| **Test Pass Rate** | >95% | <90% |

---

## Configuration

Edit `cortex.config.json`:

```json
{
  "health_monitoring": {
    "enabled": true,
    "check_interval_minutes": 60,
    "alert_threshold": {
      "tier1_query_ms": 100,
      "tier2_search_ms": 300,
      "tier3_analysis_ms": 400
    }
  }
}
```

---

## Related Documentation

- **Operations Overview:** [Overview](overview.md)
- **Troubleshooting:** [Troubleshooting Guide](../guides/troubleshooting.md)
- **Configuration:** [Configuration Reference](../reference/configuration.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 