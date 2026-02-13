# Runbook

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Operations, SRE

## Overview

This runbook covers common operational procedures for CORTEX system maintenance, incident response, and routine operations.

## System Health Check

### Quick Health Verification

```powershell
# 1. Check MCP server status
python -m cortex.mcp.server --health

# 2. Verify database connectivity
python -c "
from cortex_brain.state import get_db
db = get_db()
print('DB OK' if db else 'DB FAIL')
"

# 3. Run smoke tests
pytest tests/e2e/smoke/ -v --tb=short
```

### Health Endpoints

| Endpoint | Expected Response | Alert Threshold |
|----------|-------------------|-----------------|
| `/health` | `{"status": "healthy"}` | Any non-200 |
| `/ready` | `{"ready": true}` | > 3s latency |
| `/metrics` | Prometheus format | N/A |

## Common Issues

### Issue: Database Locked

**Symptoms:**
- `sqlite3.OperationalError: database is locked`
- Slow governance rule queries

**Resolution:**
```powershell
# 1. Find processes holding the lock
Get-Process python | Where-Object { $_.Handles -gt 100 }

# 2. Gracefully stop MCP server
# (Send SIGTERM or Ctrl+C)

# 3. If stuck, force kill
Get-Process python | Stop-Process -Force

# 4. Verify lock released
python -c "
import sqlite3
conn = sqlite3.connect('cortex_brain/state/governance.db')
conn.execute('SELECT 1')
print('Lock cleared')
"
```

### Issue: High Memory Usage

**Symptoms:**
- Memory > 2GB for MCP server
- OOM kills in container

**Resolution:**
```powershell
# 1. Check current memory
Get-Process python | Select-Object ProcessName, WorkingSet64

# 2. Force garbage collection
python -c "
import gc
gc.collect()
print(f'Collected: {gc.get_stats()}')
"

# 3. Restart with memory limit
# In production, use container limits
```

### Issue: MCP Tool Timeout

**Symptoms:**
- Tool calls return after > 30s
- `TimeoutError` in logs

**Resolution:**
```powershell
# 1. Check which tool is slow
# Look at recent logs
Get-Content logs/mcp.log -Tail 50 | Select-String "duration"

# 2. Check for blocking operations
# Tools should be async

# 3. Increase timeout (temporary)
$env:CORTEX_TOOL_TIMEOUT = "60"
python -m cortex.mcp.server
```

### Issue: Governance Rule Not Applied

**Symptoms:**
- Expected BLOCKED response returns success
- CORE-* rule violation allowed

**Resolution:**
```powershell
# 1. Verify rule exists
python -c "
from cortex_brain.tier0.governance import load_rules
rules = load_rules()
print([r.id for r in rules])
"

# 2. Check tier precedence
# tier0 should always override

# 3. Clear rule cache
python -c "
from cortex.core.governance import RuleCache
RuleCache.clear()
"
```

## Routine Operations

### Daily Tasks

| Task | Command | Frequency |
|------|---------|-----------|
| Health check | `pytest tests/e2e/smoke/ -v` | Every 4 hours |
| Log rotation | Automatic (logrotate) | Daily |
| Metrics scrape | Prometheus automatic | 15s |

### Weekly Tasks

| Task | Command | Day |
|------|---------|-----|
| Full test suite | `pytest tests/ -v` | Monday |
| Dependency audit | `pip-audit` | Wednesday |
| Database vacuum | See below | Friday |

### Database Maintenance

```powershell
# Weekly vacuum
python -c "
import sqlite3
conn = sqlite3.connect('cortex_brain/state/governance.db')
conn.execute('VACUUM')
conn.execute('ANALYZE')
print('Maintenance complete')
"
```

## Incident Response

### Severity Levels

| Level | Definition | Response Time |
|-------|------------|---------------|
| P1 | System down | 15 minutes |
| P2 | Major degradation | 1 hour |
| P3 | Minor issue | 4 hours |
| P4 | Low impact | 24 hours |

### P1 Incident Checklist

1. [ ] Acknowledge incident
2. [ ] Check system health endpoints
3. [ ] Review recent deployments
4. [ ] Check error logs
5. [ ] Rollback if needed
6. [ ] Communicate status
7. [ ] Document root cause

### Rollback Procedure

```powershell
# 1. Identify last good version
git log --oneline -10

# 2. Rollback code
git checkout <commit-hash>

# 3. Restart services
# (Container orchestrator handles this)

# 4. Verify health
pytest tests/e2e/smoke/ -v
```

## Monitoring Alerts

### Critical Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| `cortex_down` | Health check fails 3x | Page on-call |
| `high_error_rate` | >5% 5xx responses | Investigate |
| `db_connection_fail` | DB unreachable | Check infra |

### Warning Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| `high_latency` | p95 > 5s | Monitor |
| `disk_space_low` | <20% free | Clean logs |
| `memory_high` | >80% usage | Scale or restart |

## Related

- [Disaster Recovery](6-disaster-recovery.md)
- [Scaling Guide](7-scaling-guide.md)
- [Troubleshooting](4-troubleshooting.md)
