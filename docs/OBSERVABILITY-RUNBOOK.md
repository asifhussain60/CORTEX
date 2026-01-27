# CORTEX MCP Server - Observability Runbook

**Version:** 1.0  
**Last Updated:** 2026-01-27  
**Audience:** DevOps, SRE, Platform Engineers  
**Authority:** Phase 7.2 MCP Observability Documentation

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Health Monitoring](#health-monitoring)
3. [Metrics & Alerting](#metrics--alerting)
4. [Troubleshooting](#troubleshooting)
5. [Common Issues](#common-issues)
6. [Deployment Operations](#deployment-operations)
7. [Emergency Procedures](#emergency-procedures)

---

## Overview

CORTEX MCP Server provides comprehensive observability through:

- **Health Endpoints:** Real-time service health checks
- **Prometheus Metrics:** Performance and usage metrics
- **Structured Logging:** Audit trail and error tracking
- **Tool Discovery:** Runtime API inspection

**Critical Endpoints:**
- Health: `http://localhost:3000/health`
- Metrics: `http://localhost:3000/metrics`
- Wiring Health: `http://localhost:3000/health/wiring`
- Orchestrator Health: `http://localhost:3000/health/orchestrators`

---

## Health Monitoring

### Basic Health Check

**Endpoint:** `GET /health`

**Expected Response (Healthy):**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T12:00:00Z",
  "uptime_seconds": 3600.5,
  "checks": {
    "service": "ok",
    "requests": 1234,
    "errors": 5
  }
}
```

**Check from CLI:**
```bash
# Basic health
curl -f http://localhost:3000/health

# With pretty output
curl -s http://localhost:3000/health | jq '.'

# Check specific field
curl -s http://localhost:3000/health | jq -r '.status'
```

**Exit Codes:**
- `0` - Healthy
- `22` - Unhealthy (HTTP 404/500)

---

### Wiring System Health

**Endpoint:** `GET /health/wiring`

**Purpose:** Verify orchestrator wiring integrity

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T12:00:00Z",
  "uptime_seconds": 3600.5,
  "checks": {
    "wiring_hash": "a1b2c3d4e5f6g7h8",
    "orchestrator_count": 23,
    "wired_count": 23,
    "wiring_status": "complete"
  }
}
```

**Alert Conditions:**
```bash
# Check if wiring is complete
if [ "$(curl -s http://localhost:3000/health/wiring | jq -r '.checks.wiring_status')" != "complete" ]; then
  echo "⚠️  Wiring incomplete - check logs"
fi

# Check orchestrator count
WIRED=$(curl -s http://localhost:3000/health/wiring | jq -r '.checks.wired_count')
if [ "$WIRED" -lt 20 ]; then
  echo "⚠️  Only $WIRED orchestrators wired (expected 23)"
fi
```

---

### Orchestrator Health

**Endpoint:** `GET /health/orchestrators?name={orchestrator_name}`

**Example:**
```bash
# Check specific orchestrator
curl http://localhost:3000/health/orchestrators?name=MasterOrchestrator

# Check all critical orchestrators
for orch in MasterOrchestrator TDDOrchestrator IntentRouter; do
  status=$(curl -s "http://localhost:3000/health/orchestrators?name=$orch" | jq -r '.checks.availability')
  echo "$orch: $status"
done
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T12:00:00Z",
  "uptime_seconds": 3600.5,
  "checks": {
    "orchestrator": "MasterOrchestrator",
    "availability": "available",
    "last_invocation": "2026-01-27T11:59:45Z"
  }
}
```

---

## Metrics & Alerting

### Prometheus Metrics

**Endpoint:** `GET /metrics`

**Key Metrics:**

| Metric | Type | Description |
|--------|------|-------------|
| `cortex_requests_total` | Counter | Total requests processed |
| `cortex_errors_total` | Counter | Total errors encountered |
| `cortex_request_duration_seconds` | Histogram | Request latency distribution |
| `cortex_orchestrator_invocations` | Counter | Per-orchestrator call counts |
| `cortex_wiring_health` | Gauge | Wiring system health (0=unhealthy, 1=healthy) |

**Query Examples (PromQL):**
```promql
# Request rate (last 5 minutes)
rate(cortex_requests_total[5m])

# Error rate
rate(cortex_errors_total[5m])

# P95 latency
histogram_quantile(0.95, rate(cortex_request_duration_seconds_bucket[5m]))

# P99 latency
histogram_quantile(0.99, rate(cortex_request_duration_seconds_bucket[5m]))

# Most-used orchestrator
topk(5, cortex_orchestrator_invocations)

# Error percentage
(rate(cortex_errors_total[5m]) / rate(cortex_requests_total[5m])) * 100
```

---

### Alert Rules

**Recommended Prometheus Alerts:**

**File:** `deployment/prometheus-alerts.yml`

```yaml
groups:
  - name: cortex_critical
    interval: 30s
    rules:
      # High Error Rate
      - alert: CortexHighErrorRate
        expr: rate(cortex_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "CORTEX error rate above 5%"
          description: "{{ $value | humanizePercentage }} errors in last 5 minutes"
          runbook: "https://docs.cortex.ai/runbooks/high-error-rate"
      
      # High Latency
      - alert: CortexHighLatency
        expr: histogram_quantile(0.95, rate(cortex_request_duration_seconds_bucket[5m])) > 1.0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CORTEX P95 latency above 1 second"
          description: "P95 latency is {{ $value }}s"
          runbook: "https://docs.cortex.ai/runbooks/high-latency"
      
      # Wiring System Degraded
      - alert: CortexWiringDegraded
        expr: cortex_wiring_health < 1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "CORTEX wiring system degraded"
          description: "Wiring health score: {{ $value }}"
          runbook: "https://docs.cortex.ai/runbooks/wiring-degraded"
      
      # Service Down
      - alert: CortexServiceDown
        expr: up{job="cortex-mcp"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "CORTEX MCP Server is down"
          description: "Service unreachable for 1+ minute"
          runbook: "https://docs.cortex.ai/runbooks/service-down"
      
      # Low Request Rate (Potential Issue)
      - alert: CortexLowRequestRate
        expr: rate(cortex_requests_total[5m]) < 0.1
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "CORTEX receiving unusually low traffic"
          description: "Only {{ $value }} requests/sec in last 5m"
```

---

### Grafana Dashboards

**Recommended Panels:**

**1. Request Overview**
```json
{
  "title": "Request Rate",
  "targets": [
    {
      "expr": "rate(cortex_requests_total[5m])"
    }
  ],
  "type": "graph"
}
```

**2. Error Rate**
```json
{
  "title": "Error Percentage",
  "targets": [
    {
      "expr": "(rate(cortex_errors_total[5m]) / rate(cortex_requests_total[5m])) * 100"
    }
  ],
  "type": "singlestat",
  "thresholds": "5,10"
}
```

**3. Latency Heatmap**
```json
{
  "title": "Request Latency Distribution",
  "targets": [
    {
      "expr": "rate(cortex_request_duration_seconds_bucket[5m])"
    }
  ],
  "type": "heatmap"
}
```

**4. Orchestrator Activity**
```json
{
  "title": "Top Orchestrators",
  "targets": [
    {
      "expr": "topk(10, cortex_orchestrator_invocations)"
    }
  ],
  "type": "bargauge"
}
```

---

## Troubleshooting

### Service Won't Start

**Symptoms:**
- Server fails to launch
- Port binding errors
- Import errors

**Diagnostic Steps:**

1. **Check port availability:**
```bash
# Is port 3000 in use?
lsof -i :3000
netstat -an | grep 3000

# Kill process using port
kill -9 $(lsof -t -i:3000)
```

2. **Check Python environment:**
```bash
# Verify Python version
python --version  # Should be 3.9+

# Check required packages
pip list | grep -E "(fastapi|uvicorn|pydantic)"

# Reinstall dependencies
pip install -r requirements.txt
```

3. **Check wiring specification:**
```bash
# Validate wiring.yaml syntax
python -c "import yaml; yaml.safe_load(open('cortex/wiring/specifications/wiring.yaml'))"

# Check for duplicate orchestrator names
grep -E "^  - name:" cortex/wiring/specifications/wiring.yaml | sort | uniq -d
```

4. **Check logs:**
```bash
# Docker logs
docker logs cortex-mcp --tail 100

# File logs
tail -f logs/cortex-mcp.log
```

---

### High Error Rate

**Symptoms:**
- `cortex_errors_total` increasing rapidly
- Alert: `CortexHighErrorRate` firing

**Diagnostic Steps:**

1. **Identify error types:**
```bash
# Check recent logs for errors
docker logs cortex-mcp --since 10m | grep ERROR

# Count error types
docker logs cortex-mcp --since 1h | grep ERROR | awk '{print $NF}' | sort | uniq -c | sort -rn
```

2. **Check orchestrator health:**
```bash
# Test each orchestrator
for orch in $(curl -s http://localhost:3000/health/wiring | jq -r '.checks.orchestrators[]'); do
  curl -s "http://localhost:3000/health/orchestrators?name=$orch"
done
```

3. **Review audit trail:**
```bash
# Check failed operations
grep "AC_COMPLETE.*success=False" logs/cortex-mcp.log | tail -20
```

**Resolution:**
- Restart unhealthy orchestrators
- Check for resource exhaustion (CPU/memory)
- Review recent code deployments
- Scale horizontally if traffic surge

---

### High Latency

**Symptoms:**
- P95 latency > 1 second
- Alert: `CortexHighLatency` firing
- Slow user experience

**Diagnostic Steps:**

1. **Identify slow operations:**
```bash
# Check request duration by method
curl -s http://localhost:3000/metrics | grep cortex_request_duration_seconds_sum

# Calculate average latency per method
curl -s http://localhost:3000/metrics | \
  awk '/cortex_request_duration_seconds/{print}' | \
  grep -v "^#"
```

2. **Check resource utilization:**
```bash
# Docker stats
docker stats cortex-mcp --no-stream

# CPU/Memory usage
top -b -n 1 | grep cortex
```

3. **Profile slow orchestrators:**
```bash
# Check which orchestrators are slow
curl -s http://localhost:3000/metrics | \
  grep cortex_orchestrator_invocations | \
  sort -t'=' -k2 -rn | head -10
```

**Resolution:**
- Add caching (LENS results, routing decisions)
- Optimize database queries
- Increase worker threads
- Profile and optimize hot paths
- Consider async processing for heavy operations

---

### Wiring System Degraded

**Symptoms:**
- `cortex_wiring_health` < 1
- Alert: `CortexWiringDegraded` firing
- Missing orchestrators

**Diagnostic Steps:**

1. **Check wiring status:**
```bash
# Get detailed wiring health
curl -s http://localhost:3000/health/wiring | jq '.'

# Compare expected vs actual
EXPECTED=23
ACTUAL=$(curl -s http://localhost:3000/health/wiring | jq -r '.checks.wired_count')
echo "Expected: $EXPECTED, Actual: $ACTUAL, Missing: $((EXPECTED - ACTUAL))"
```

2. **Check wiring specification:**
```bash
# Count orchestrators in spec
grep -c "^  - name:" cortex/wiring/specifications/wiring.yaml

# Check for syntax errors
python -c "
import yaml
with open('cortex/wiring/specifications/wiring.yaml') as f:
    spec = yaml.safe_load(f)
    print(f'Orchestrators in spec: {len(spec.get(\"orchestrators\", []))}')
"
```

3. **Check orchestrator imports:**
```bash
# Test imports
python -c "
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
print('Imports successful')
"
```

**Resolution:**
- Fix wiring.yaml syntax errors
- Ensure all orchestrator modules exist
- Check for circular import dependencies
- Restart server to reload wiring
- Use hot-reload watcher for development

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'cortex.orchestrators.xyz'"

**Cause:** Orchestrator module doesn't exist or import path incorrect

**Resolution:**
```bash
# Verify file exists
ls -la cortex/orchestrators/path/to/orchestrator.py

# Check __init__.py files
find cortex/orchestrators -name "__init__.py"

# Update wiring.yaml with correct path
vim cortex/wiring/specifications/wiring.yaml
```

---

### Issue: Port 3000 Already in Use

**Cause:** Another process using port 3000

**Resolution:**
```bash
# Find process
lsof -i :3000

# Kill process
kill -9 $(lsof -t -i:3000)

# Or use different port
export PORT=3001
```

---

### Issue: Health Endpoint Returns 404

**Cause:** Server not started or routes not registered

**Resolution:**
```bash
# Check if server is running
curl -v http://localhost:3000/health

# Check server logs
docker logs cortex-mcp | grep "health"

# Restart server
docker restart cortex-mcp
```

---

### Issue: Prometheus Not Scraping Metrics

**Cause:** Network issue or incorrect Prometheus config

**Resolution:**
```bash
# Test metrics endpoint
curl http://localhost:3000/metrics

# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets

# Verify Prometheus config
cat deployment/prometheus.yml
```

---

## Deployment Operations

### Docker Deployment

**Start Server:**
```bash
# Production mode
docker-compose -f docker-compose.prod.yml up -d cortex-mcp

# Development mode (with hot-reload)
docker-compose -f docker-compose.dev.yaml up cortex-mcp
```

**Health Check:**
```bash
# Wait for healthy status
until curl -f http://localhost:3000/health; do
  echo "Waiting for CORTEX to be healthy..."
  sleep 2
done
echo "✅ CORTEX is healthy!"
```

**View Logs:**
```bash
# Follow logs
docker logs -f cortex-mcp

# Last 100 lines
docker logs cortex-mcp --tail 100

# Since timestamp
docker logs cortex-mcp --since "2026-01-27T12:00:00"
```

**Restart Server:**
```bash
# Graceful restart
docker restart cortex-mcp

# Force restart
docker kill cortex-mcp && docker start cortex-mcp
```

---

### Monitoring Stack Deployment

**Deploy Prometheus + Grafana:**
```bash
# Start monitoring stack
docker-compose -f docker-compose.prod.yml up -d prometheus grafana

# Verify Prometheus is scraping
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job=="cortex-mcp")'

# Access Grafana
open http://localhost:3001
# Default: admin / admin
```

**Import Grafana Dashboard:**
```bash
# Copy dashboard JSON to Grafana container
docker cp dashboards/cortex-overview.json grafana:/var/lib/grafana/dashboards/

# Or import via UI
# Grafana > Dashboards > Import > Upload JSON
```

---

### Kubernetes Deployment

**Health Probes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cortex-mcp
spec:
  template:
    spec:
      containers:
      - name: cortex-mcp
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health/wiring
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
```

**Service Monitor (Prometheus Operator):**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cortex-mcp
spec:
  selector:
    matchLabels:
      app: cortex-mcp
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
```

---

## Emergency Procedures

### Server Completely Down

**Immediate Actions:**
1. Check if server process is running
2. Review last 100 log lines for errors
3. Attempt restart
4. If restart fails, check port conflicts
5. Verify wiring specification syntax
6. Check disk space and memory

**Commands:**
```bash
# 1. Check process
docker ps | grep cortex-mcp

# 2. Check logs
docker logs cortex-mcp --tail 100

# 3. Restart
docker restart cortex-mcp

# 4. Check port
lsof -i :3000

# 5. Validate wiring
python -c "import yaml; yaml.safe_load(open('cortex/wiring/specifications/wiring.yaml'))"

# 6. Check resources
df -h
free -h
```

---

### High Error Rate Incident

**Immediate Actions:**
1. Check error logs for patterns
2. Identify failing orchestrator
3. Temporarily disable failing orchestrator if needed
4. Roll back recent deployments
5. Scale horizontally if traffic surge

**Commands:**
```bash
# 1. Error patterns
docker logs cortex-mcp --since 10m | grep ERROR | sort | uniq -c

# 2. Check orchestrators
curl http://localhost:3000/health/orchestrators

# 3. Disable orchestrator (edit wiring.yaml)
# Comment out failing orchestrator, save, hot-reload triggers

# 4. Rollback
docker-compose down
git checkout HEAD~1
docker-compose up -d

# 5. Scale
docker-compose up -d --scale cortex-mcp=3
```

---

### Database Connection Lost

**Immediate Actions:**
1. Check database connectivity
2. Verify credentials
3. Check network rules
4. Restart database connection pool
5. Failover to replica if available

**Commands:**
```bash
# 1. Test connection
nc -zv database-host 5432

# 2. Check credentials
env | grep DATABASE

# 3. Network test
ping database-host
traceroute database-host

# 4. Restart CORTEX (resets connection pool)
docker restart cortex-mcp

# 5. Failover (update DATABASE_URL)
export DATABASE_URL="postgresql://replica-host/cortex"
docker restart cortex-mcp
```

---

## Support Contacts

**On-Call Rotation:**
- Primary: DevOps Team
- Secondary: Platform Engineering
- Escalation: CORTEX Core Team

**Communication Channels:**
- Slack: `#cortex-alerts`
- PagerDuty: `cortex-mcp` service
- Email: `cortex-oncall@company.com`

---

## Appendix

### Useful Commands Cheatsheet

```bash
# Health checks
curl http://localhost:3000/health
curl http://localhost:3000/health/wiring
curl http://localhost:3000/health/orchestrators?name=MasterOrchestrator

# Metrics
curl http://localhost:3000/metrics
curl -s http://localhost:3000/metrics | grep cortex_requests_total

# Logs
docker logs cortex-mcp --tail 100 --follow
docker logs cortex-mcp --since 10m | grep ERROR

# Restart
docker restart cortex-mcp
docker-compose restart cortex-mcp

# Resource monitoring
docker stats cortex-mcp --no-stream
docker inspect cortex-mcp | jq '.[0].State'

# Network debugging
docker exec cortex-mcp curl localhost:3000/health
docker network inspect cortex_default
```

---

**Runbook Version:** 1.0  
**Last Updated:** 2026-01-27  
**Maintained By:** CORTEX Platform Team  
**Review Cycle:** Quarterly
