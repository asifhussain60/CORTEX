# CORTEX Operations Runbook

**Version:** 1.0.0  
**Last Updated:** 2026-02-15  
**Audience:** DevOps, SRE, Operations Teams

---

## Table of Contents

1. [Deployment Procedures](#deployment-procedures)
2. [Rollback Procedures](#rollback-procedures)
3. [Monitoring & Alerting](#monitoring--alerting)
4. [Incident Response](#incident-response)
5. [Troubleshooting Guide](#troubleshooting-guide)
6. [Maintenance Windows](#maintenance-windows)

---

## 1. Deployment Procedures

### 1.1 Pre-Deployment Checklist

**Before deploying CORTEX:**

- [ ] **All tests passing:** `pytest -n 8 --tb=short`
- [ ] **Zero P0 violations:** `/audit` command shows 0 P0 issues
- [ ] **MCP server health:** `curl http://localhost:8000/health` returns 200
- [ ] **Dependencies up-to-date:** `pip list --outdated` shows no critical packages
- [ ] **Documentation current:** README.md reflects current version
- [ ] **Audit trail complete:** AC_START/AC_COMPLETE markers present
- [ ] **Git clean:** `git status` shows no uncommitted changes
- [ ] **Backup completed:** Database and config backed up

### 1.2 Deployment Steps (Production)

**Environment:** Production  
**Duration:** ~15 minutes  
**Downtime:** Zero (rolling update)

```bash
# Step 1: Backup current state
cd /Users/asifhussain/PROJECTS/CORTEX
./scripts/backup.sh production

# Step 2: Pull latest code
git checkout CORTEX
git pull origin CORTEX

# Step 3: Update dependencies
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# Step 4: Run database migrations (if any)
python -m cortex.storage.migrations.migrate

# Step 5: Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "1.0.0"}

# Step 6: Smoke tests
pytest tests/smoke/ -v

# Step 7: Monitor logs for 5 minutes
tail -f logs/cortex.log

# Step 8: Verify orchestrators
curl http://localhost:8000/health/orchestrators | jq '.orchestrators | length'
# Expected: 28

# Step 9: Production validation
./scripts/validate-production.sh

# Step 10: Tag release
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

### 1.3 Deployment Validation

**Post-deployment checks:**

```bash
# Check 1: Health endpoints
curl http://localhost:8000/health | jq '.status'
# Expected: "healthy"

# Check 2: MCP tools available
curl http://localhost:8000/tools | jq '. | length'
# Expected: 24

# Check 3: Test MCP request
curl -X POST http://localhost:8000/tools/cortex_process_request \
  -H "Content-Type: application/json" \
  -d '{"request": "health check", "mode": "test"}'

# Check 4: Database connectivity
python -c "from cortex.storage import get_db_session; session = get_db_session(); print('DB OK')"

# Check 5: Git hooks active
git config core.hooksPath
# Expected: .githooks
```

**Success Criteria:**
- All 5 checks pass
- No error logs in last 5 minutes
- Response time <200ms (p95)

---

## 2. Rollback Procedures

### 2.1 Emergency Rollback

**Trigger Conditions:**
- P0 errors detected in production
- >5% error rate sustained for >2 minutes
- Database corruption detected
- Security breach confirmed

**Rollback Steps (< 5 minutes):**

```bash
# Step 1: Stop current deployment
pkill -f "python -m cortex.mcp"

# Step 2: Revert to previous version
git checkout v0.9.9  # Previous stable tag

# Step 3: Restore dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Step 4: Restore database (if needed)
./scripts/restore-db.sh production latest

# Step 5: Restart MCP server
python -m cortex.mcp.server &

# Step 6: Immediate health check
curl http://localhost:8000/health

# Step 7: Monitor for 5 minutes
tail -f logs/cortex.log | grep ERROR
```

### 2.2 Graceful Rollback

**When:** Non-critical issues, during maintenance window

```bash
# Step 1: Announce maintenance
# (Send notification to team)

# Step 2: Drain active connections
# Wait for ongoing operations to complete (~2 minutes)

# Step 3: Stop MCP server gracefully
kill -SIGTERM $(pgrep -f "python -m cortex.mcp")

# Step 4: Rollback code
git revert HEAD~1  # Revert last commit
git push origin CORTEX

# Step 5: Redeploy (follow deployment steps)

# Step 6: Validate (follow validation steps)
```

---

## 3. Monitoring & Alerting

### 3.1 Key Metrics

**Health Metrics:**
- MCP server uptime: Target >99.9%
- Request latency (p95): Target <200ms
- Error rate: Target <0.5%
- Test pass rate: Target 100%

**Resource Metrics:**
- CPU usage: Normal <30%, Alert >70%
- Memory usage: Normal <2GB, Alert >4GB
- Disk I/O: Normal <50MB/s, Alert >200MB/s
- Database connections: Normal <10, Alert >50

### 3.2 Prometheus Queries

**Key queries for dashboards:**

```promql
# Request rate
rate(cortex_tool_invocations_total[5m])

# Error rate
rate(cortex_tool_invocations_total{status="error"}[5m]) / rate(cortex_tool_invocations_total[5m])

# Latency (p95)
histogram_quantile(0.95, rate(cortex_request_duration_seconds_bucket[5m]))

# Orchestrator count
cortex_orchestrator_count

# Active operations
cortex_active_operations
```

### 3.3 Alert Rules

**Critical Alerts (PagerDuty):**

```yaml
alerts:
  - name: MCPServerDown
    condition: up{job="cortex-mcp"} == 0
    duration: 1m
    severity: critical
    action: Page on-call

  - name: HighErrorRate
    condition: rate(cortex_errors_total[5m]) > 0.05
    duration: 2m
    severity: critical
    action: Page on-call

  - name: HighLatency
    condition: cortex_request_duration_seconds{quantile="0.95"} > 2.0
    duration: 5m
    severity: warning
    action: Notify team

  - name: TestFailures
    condition: cortex_test_failures_total > 0
    duration: 1m
    severity: warning
    action: Notify team
```

**Dashboard:** See `deployment/grafana-dashboards/cortex-overview.json`

---

## 4. Incident Response

### 4.1 Incident Severity Levels

| Severity | Definition | Response Time | Escalation |
|----------|-----------|---------------|------------|
| **P0** | MCP server down, all users impacted | <5 min | Immediate page |
| **P1** | Degraded performance, >50% users impacted | <15 min | Page if unresolved in 30min |
| **P2** | Partial functionality loss, <50% users | <1 hour | Notify team lead |
| **P3** | Minor issue, workaround available | <4 hours | Log ticket |

### 4.2 Incident Response Workflow

**P0 Incident: MCP Server Down**

```
1. DETECT (Monitoring alert)
   ├─ Alert: MCPServerDown
   ├─ PagerDuty notification
   └─ On-call engineer notified

2. ACKNOWLEDGE (<2 minutes)
   ├─ Acknowledge alert in PagerDuty
   ├─ Join #cortex-incidents Slack channel
   └─ Post: "Investigating MCPServerDown alert"

3. DIAGNOSE (<5 minutes)
   ├─ Check health endpoint: curl http://localhost:8000/health
   ├─ Check logs: tail -100 logs/cortex.log
   ├─ Check process: ps aux | grep "python -m cortex.mcp"
   └─ Check disk space: df -h

4. MITIGATE (<10 minutes)
   ├─ If process dead: Restart MCP server
   ├─ If disk full: Clear logs, temp files
   ├─ If database issue: Restore from backup
   └─ If code issue: Emergency rollback

5. VALIDATE (<15 minutes)
   ├─ Health check passing
   ├─ Smoke tests passing
   ├─ Error rate <0.5%
   └─ Latency <200ms

6. COMMUNICATE (Throughout)
   ├─ Status updates every 5 minutes
   ├─ Post resolution in #cortex-incidents
   └─ Update status page

7. POSTMORTEM (Within 48 hours)
   ├─ Root cause analysis
   ├─ Timeline of events
   ├─ Action items to prevent recurrence
   └─ Share with team
```

### 4.3 Common Incidents

#### Incident: "Tests Failing in Production"

**Symptoms:**
- `pytest` shows failures
- CI/CD pipeline blocked
- MCP operations degraded

**Diagnosis:**
```bash
# Step 1: Run tests with verbose output
pytest -xvs --tb=long

# Step 2: Check for environment issues
python -c "import sys; print(sys.version)"
pip list | grep pytest

# Step 3: Check for dependency drift
./scripts/check-dependency-drift.sh
```

**Resolution:**
```bash
# Option A: Fix failing tests (if legitimate failure)
# (Follow TDD workflow)

# Option B: Update dependencies (if drift detected)
pip install -r requirements.txt --upgrade
pytest

# Option C: Rollback (if tests broken by recent change)
git revert HEAD
pytest
```

#### Incident: "High Latency (>2s p95)"

**Symptoms:**
- Slow response times
- User complaints
- Timeout errors

**Diagnosis:**
```bash
# Step 1: Check resource usage
top -o cpu | head -20
free -h

# Step 2: Check database performance
python -c "from cortex.storage import profile_db_queries; profile_db_queries()"

# Step 3: Check for N+1 queries
grep "SELECT" logs/cortex.log | wc -l
```

**Resolution:**
```bash
# Option A: Add database indexes (if query slow)
python -m cortex.storage.migrations.add_index --table=<table> --column=<column>

# Option B: Add caching (if repeated queries)
# (Implement Redis caching)

# Option C: Scale horizontally (if resource exhaustion)
# (Add more MCP server instances)
```

---

## 5. Troubleshooting Guide

### 5.1 MCP Server Won't Start

**Symptoms:**
- `python -m cortex.mcp.server` fails
- No process running
- Health endpoint unreachable

**Troubleshooting:**

```bash
# Check 1: Python version
python --version
# Expected: 3.9+

# Check 2: Dependencies installed
pip list | grep cortex
# Expected: cortex package present

# Check 3: Virtual environment
which python
# Expected: /path/to/CORTEX/.venv/bin/python

# Check 4: Port availability
lsof -i :8000
# Expected: No process (or kill existing)

# Check 5: Config file
cat .cortex/config.yaml
# Expected: Valid YAML

# Check 6: Database connection
python -c "from cortex.storage import test_db_connection; test_db_connection()"
```

**Solutions:**

```bash
# Solution 1: Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Solution 2: Clear port
kill $(lsof -t -i:8000)

# Solution 3: Reset config
cp .cortex/config.yaml.template .cortex/config.yaml

# Solution 4: Reset database
python -m cortex.storage.migrations.reset --confirm
```

### 5.2 Tests Passing Locally, Failing in CI

**Symptoms:**
- `pytest` passes on local machine
- GitHub Actions CI fails
- Same test, different environments

**Troubleshooting:**

```bash
# Check 1: Python version mismatch
# Local vs CI

# Check 2: Dependency versions
pip freeze > local-requirements.txt
# Compare with requirements.txt

# Check 3: Environment variables
env | grep CORTEX
# Check if CI has same vars

# Check 4: File paths (absolute vs relative)
# Check test uses Path(__file__).parent

# Check 5: Timezone differences
python -c "import time; print(time.tzname)"
```

**Solutions:**

```bash
# Solution 1: Pin dependency versions
pip freeze > requirements.txt

# Solution 2: Add environment variables to CI
# (GitHub Actions secrets)

# Solution 3: Use relative paths
# tests/conftest.py: WORKSPACE_ROOT = Path(__file__).parent.parent

# Solution 4: Set timezone in CI
# GitHub Actions: env: TZ: UTC
```

### 5.3 Git Hooks Not Running

**Symptoms:**
- `git commit` succeeds with violations
- Pre-commit checks skipped
- Governance bypassed

**Troubleshooting:**

```bash
# Check 1: Hooks path configured
git config core.hooksPath
# Expected: .githooks

# Check 2: Hook file exists
ls -la .githooks/pre-commit
# Expected: Executable file

# Check 3: Hook is executable
test -x .githooks/pre-commit && echo "Executable" || echo "Not executable"

# Check 4: Python available in hook
head -1 .githooks/pre-commit
# Expected: #!/usr/bin/env python3 or #!/bin/bash
```

**Solutions:**

```bash
# Solution 1: Set hooks path
git config core.hooksPath .githooks

# Solution 2: Make hook executable
chmod +x .githooks/pre-commit

# Solution 3: Reinstall hooks
./scripts/setup-git-hooks.sh

# Solution 4: Test hook manually
.githooks/pre-commit
# Should run validation checks
```

---

## 6. Maintenance Windows

### 6.1 Scheduled Maintenance

**Frequency:** Monthly (first Sunday, 2:00 AM - 4:00 AM UTC)

**Maintenance Tasks:**

1. **Dependency Updates** (30 min)
   ```bash
   pip list --outdated
   pip install <package> --upgrade
   pytest -n 8
   ```

2. **Database Cleanup** (20 min)
   ```bash
   python -m cortex.storage.vacuum
   python -m cortex.storage.reindex
   ```

3. **Log Rotation** (10 min)
   ```bash
   ./scripts/rotate-logs.sh
   du -sh logs/
   ```

4. **Security Scan** (30 min)
   ```bash
   pip install safety
   safety check
   bandit -r cortex/
   ```

5. **Performance Profiling** (30 min)
   ```bash
   python -m cortex.observability.profiler
   ```

### 6.2 Emergency Maintenance

**Trigger:** Critical security vulnerability, data corruption

**Process:**
1. **Announce:** Post to #cortex-incidents immediately
2. **Assess:** Determine severity and impact (< 15 minutes)
3. **Decide:** Patch in place vs rollback vs emergency release
4. **Execute:** Follow deployment or rollback procedure
5. **Validate:** Run full test suite + smoke tests
6. **Communicate:** Post resolution + postmortem plan

---

## 7. Contacts & Escalation

| Role | Contact | Escalation Path |
|------|---------|-----------------|
| **On-Call Engineer** | PagerDuty | → Team Lead → Director |
| **Team Lead** | Slack #cortex-team | → Director → VP Eng |
| **Database Admin** | Slack #cortex-db | → On-Call → Team Lead |
| **Security Team** | [security@cortex.ai](mailto:security@cortex.ai) | → CISO (immediate) |

**PagerDuty:** [cortex-oncall rotation]  
**Status Page:** [status.cortex.ai]  
**Runbook Updates:** [GitHub: .cortex/runbooks/]

---

**Version:** 1.0.0  
**Last Review:** 2026-02-15  
**Next Review:** 2026-03-15  
**Owner:** DevOps Team
