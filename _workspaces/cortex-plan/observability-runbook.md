# CORTEX Observability Runbook

**Version:** 1.0  
**Last Updated:** 2026-01-27  
**Owner:** CORTEX Platform Team  
**Phase:** 7.2 (MCP Observability Documentation)

---

## Table of Contents
1. [Overview](#overview)
2. [Health Endpoints](#health-endpoints)
3. [Prometheus Metrics](#prometheus-metrics)
4. [Grafana Dashboards](#grafana-dashboards)
5. [Alert Configuration](#alert-configuration)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Production Deployment](#production-deployment)

---

## Overview

This runbook provides operational guidance for monitoring CORTEX in production environments. CORTEX implements cloud-native observability through:

- **Health Endpoints:** HTTP health checks for service status
- **Prometheus Metrics:** Time-series metrics for performance monitoring
- **Grafana Dashboards:** Visual monitoring and alerting
- **Hot-Reload Watcher:** Configuration change detection

**Target Audience:** DevOps engineers, SREs, platform operators

---

## Health Endpoints

### 1. System Health Check

**Endpoint:** `GET /health`

**Purpose:** Overall system health status

**Usage:**
```bash
# Check system health
curl http://localhost:8000/health

# With verbose output
curl -v http://localhost:8000/health

# From Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Response Format:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T10:30:00Z",
  "version": "6.2.0",
  "components": {
    "wiring": "healthy",
    "orchestrators": 23,
    "database": "connected",
    "mcp_server": "running"
  },
  "uptime_seconds": 3600
}
```

**Status Codes:**
- `200 OK` - System healthy
- `503 Service Unavailable` - System degraded or unhealthy
- `500 Internal Server Error` - Health check failed

---

### 2. Wiring Health Check

**Endpoint:** `GET /health/wiring`

**Purpose:** Check orchestrator wiring configuration

**Usage:**
```bash
curl http://localhost:8000/health/wiring
```

**Response Format:**
```json
{
  "status": "healthy",
  "wiring_file": "/app/cortex/wiring/specifications/wiring.yaml",
  "last_modified": "2026-01-27T09:15:00Z",
  "orchestrators_wired": 23,
  "validation": "passed",
  "hot_reload": "enabled"
}
```

**Status Codes:**
- `200 OK` - Wiring configuration valid
- `503 Service Unavailable` - Wiring configuration invalid or corrupted
- `404 Not Found` - Wiring file missing

---

### 3. Orchestrator Health Check

**Endpoint:** `GET /health/orchestrators`

**Purpose:** Check individual orchestrator status

**Usage:**
```bash
curl http://localhost:8000/health/orchestrators

# Check specific orchestrator
curl http://localhost:8000/health/orchestrators?name=TDDOrchestrator
```

**Response Format:**
```json
{
  "status": "healthy",
  "orchestrators": [
    {
      "name": "MasterOrchestrator",
      "status": "healthy",
      "invocations": 1523,
      "last_invocation": "2026-01-27T10:29:45Z",
      "average_latency_ms": 125
    },
    {
      "name": "TDDOrchestrator",
      "status": "healthy",
      "invocations": 847,
      "last_invocation": "2026-01-27T10:28:30Z",
      "average_latency_ms": 89
    }
  ],
  "total_orchestrators": 23,
  "healthy_count": 23,
  "degraded_count": 0
}
```

**Status Codes:**
- `200 OK` - All orchestrators healthy
- `503 Service Unavailable` - One or more orchestrators degraded

---

## Prometheus Metrics

### Metrics Endpoint

**Endpoint:** `GET /metrics`

**Purpose:** Prometheus-compatible metrics scraping

**Usage:**
```bash
# Fetch metrics manually
curl http://localhost:8000/metrics

# Prometheus scrape configuration (prometheus.yml)
scrape_configs:
  - job_name: 'cortex-mcp'
    static_configs:
      - targets: ['cortex-mcp:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
```

---

### Available Metrics

#### 1. Orchestrator Count
```prometheus
# HELP cortex_orchestrator_count Total number of registered orchestrators
# TYPE cortex_orchestrator_count gauge
cortex_orchestrator_count 23
```

**Use Cases:**
- Detect orchestrator unwiring events
- Track wiring configuration changes
- Alert on unexpected orchestrator count drops

---

#### 2. Tool Invocations
```prometheus
# HELP cortex_tool_invocations_total Total MCP tool invocations
# TYPE cortex_tool_invocations_total counter
cortex_tool_invocations_total{tool="semantic_search"} 1245
cortex_tool_invocations_total{tool="run_in_terminal"} 893
cortex_tool_invocations_total{tool="read_file"} 2341
```

**Use Cases:**
- Monitor tool usage patterns
- Identify high-traffic tools
- Capacity planning

---

#### 3. Wiring Reload Events
```prometheus
# HELP cortex_wiring_reload_total Total hot-reload events
# TYPE cortex_wiring_reload_total counter
cortex_wiring_reload_total{status="success"} 15
cortex_wiring_reload_total{status="failure"} 2
```

**Use Cases:**
- Track configuration changes
- Detect failed reloads
- Audit wiring modifications

---

#### 4. Request Duration
```prometheus
# HELP cortex_request_duration_seconds Request latency histogram
# TYPE cortex_request_duration_seconds histogram
cortex_request_duration_seconds_bucket{le="0.1"} 1523
cortex_request_duration_seconds_bucket{le="0.5"} 2341
cortex_request_duration_seconds_bucket{le="1.0"} 2456
cortex_request_duration_seconds_bucket{le="5.0"} 2489
cortex_request_duration_seconds_bucket{le="+Inf"} 2500
cortex_request_duration_seconds_sum 3125.45
cortex_request_duration_seconds_count 2500
```

**Use Cases:**
- Monitor P50, P95, P99 latency
- Detect performance regressions
- SLA monitoring

---

#### 5. Error Counter
```prometheus
# HELP cortex_errors_total Total errors by type
# TYPE cortex_errors_total counter
cortex_errors_total{type="wiring_error"} 2
cortex_errors_total{type="orchestrator_failure"} 1
cortex_errors_total{type="tool_timeout"} 5
cortex_errors_total{type="database_error"} 0
```

**Use Cases:**
- Error rate monitoring
- Error classification
- Alert on error spikes

---

## Grafana Dashboards

### Dashboard Setup

**1. Add Prometheus Data Source**
```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "access": "proxy",
  "isDefault": true
}
```

**2. Import Dashboard Template**
```bash
# Dashboard JSON available at:
# _workspaces/cortex-plan/grafana-dashboard-cortex.json
```

---

### Key Dashboard Panels

#### Panel 1: System Health (Gauge)
```promql
# Query
up{job="cortex-mcp"}

# Thresholds
0-0.5: Red (Down)
0.5-1: Green (Up)
```

---

#### Panel 2: Orchestrator Count (Stat)
```promql
# Query
cortex_orchestrator_count

# Alert if < 23 (expected count)
```

---

#### Panel 3: Request Rate (Graph)
```promql
# Query
rate(cortex_tool_invocations_total[5m])

# Legend: {{tool}}
```

---

#### Panel 4: Error Rate (Graph)
```promql
# Query
rate(cortex_errors_total[5m])

# Legend: {{type}}
# Alert if > 10 errors/min
```

---

#### Panel 5: P95 Latency (Graph)
```promql
# Query
histogram_quantile(0.95, rate(cortex_request_duration_seconds_bucket[5m]))

# Alert if > 5s
```

---

#### Panel 6: Hot-Reload Events (Counter)
```promql
# Query
increase(cortex_wiring_reload_total[1h])

# Legend: {{status}}
```

---

## Alert Configuration

### AlertManager Rules

**File:** `deployment/alertmanager.yml`

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'cortex-ops'

receivers:
  - name: 'cortex-ops'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#cortex-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname']
```

---

### Prometheus Alert Rules

**File:** `deployment/prometheus-rules.yml`

```yaml
groups:
  - name: cortex_alerts
    interval: 30s
    rules:
      # Critical: Service Down
      - alert: CORTEXServiceDown
        expr: up{job="cortex-mcp"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "CORTEX MCP server is down"
          description: "CORTEX MCP server {{ $labels.instance }} has been down for 1 minute"

      # High: Error Rate Spike
      - alert: CORTEXHighErrorRate
        expr: rate(cortex_errors_total[5m]) > 10
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/min (threshold: 10)"

      # High: Orchestrator Unwired
      - alert: CORTEXOrchestratorUnwired
        expr: cortex_orchestrator_count < 23
        for: 2m
        labels:
          severity: high
        annotations:
          summary: "Orchestrator count dropped"
          description: "Expected 23 orchestrators, found {{ $value }}"

      # Medium: Slow Requests
      - alert: CORTEXSlowRequests
        expr: histogram_quantile(0.95, rate(cortex_request_duration_seconds_bucket[5m])) > 5
        for: 10m
        labels:
          severity: medium
        annotations:
          summary: "P95 latency exceeded threshold"
          description: "P95 latency is {{ $value }}s (threshold: 5s)"

      # Medium: Wiring Reload Failure
      - alert: CORTEXWiringReloadFailed
        expr: increase(cortex_wiring_reload_total{status="failure"}[1h]) > 0
        for: 5m
        labels:
          severity: medium
        annotations:
          summary: "Wiring reload failed"
          description: "{{ $value }} wiring reload failures in last hour"
```

---

### Alert Severity Levels

| Severity | Response Time | Escalation | Examples |
|----------|---------------|------------|----------|
| **Critical** | Immediate (< 5 min) | On-call engineer | Service down, database unreachable |
| **High** | 15 minutes | Team lead | High error rate, orchestrator unwired |
| **Medium** | 1 hour | Business hours | Slow requests, reload failures |
| **Low** | Next business day | Backlog | Metrics drift, non-critical warnings |

---

## Troubleshooting Guide

### Symptom: Health Endpoint Returns 503

**Diagnostic Steps:**
```bash
# 1. Check health endpoint details
curl -v http://localhost:8000/health

# 2. Check database connection
docker exec cortex-mcp python -c "from cortex.brain.core.state_manager import get_state_manager; print(get_state_manager())"

# 3. Check wiring file syntax
docker exec cortex-mcp python -c "import yaml; yaml.safe_load(open('cortex/wiring/specifications/wiring.yaml'))"

# 4. Check orchestrator registration logs
docker logs cortex-mcp | grep "orchestrator registration"
```

**Common Causes:**
- ❌ Database connection lost (state_manager failure)
- ❌ Wiring file corrupted (YAML syntax error)
- ❌ Orchestrator failed to initialize

**Resolution:**
```bash
# Restart service
docker-compose restart cortex-mcp

# Check logs for errors
docker logs -f cortex-mcp

# Verify wiring file
cat cortex/wiring/specifications/wiring.yaml | python -m yaml

# Restore wiring from backup
cp cortex/wiring/specifications/wiring.yaml.backup cortex/wiring/specifications/wiring.yaml
```

---

### Symptom: Metrics Not Appearing in Prometheus

**Diagnostic Steps:**
```bash
# 1. Verify /metrics endpoint accessible
curl http://localhost:8000/metrics

# 2. Check Prometheus targets
open http://localhost:9090/targets

# 3. Check Prometheus logs
docker logs prometheus

# 4. Test scrape manually
curl -v http://cortex-mcp:8000/metrics
```

**Common Causes:**
- ❌ Network connectivity issue (Docker network misconfigured)
- ❌ Prometheus scrape config incorrect
- ❌ CORTEX MCP server not exposing metrics

**Resolution:**
```bash
# Check Docker network
docker network inspect cortex-network

# Verify Prometheus config
cat deployment/prometheus.prod.yml

# Restart Prometheus
docker-compose restart prometheus

# Check CORTEX MCP server
docker exec cortex-mcp curl http://localhost:8000/metrics
```

---

### Symptom: Wiring Changes Not Hot-Reloading

**Diagnostic Steps:**
```bash
# 1. Check wiring_watcher status
docker logs cortex-mcp | grep "wiring_watcher"

# 2. Verify file permissions
docker exec cortex-mcp ls -la cortex/wiring/specifications/wiring.yaml

# 3. Check hot-reload metrics
curl http://localhost:8000/metrics | grep wiring_reload

# 4. Test manual reload
docker exec cortex-mcp python -c "from cortex.mcp.wiring_watcher import reload_wiring; reload_wiring()"
```

**Common Causes:**
- ❌ File permissions prevent watcher from detecting changes
- ❌ Wiring watcher process crashed
- ❌ YAML syntax error preventing reload

**Resolution:**
```bash
# Fix file permissions
docker exec cortex-mcp chmod 644 cortex/wiring/specifications/wiring.yaml

# Restart watcher
docker-compose restart cortex-mcp

# Validate YAML before editing
python -m yaml cortex/wiring/specifications/wiring.yaml

# Check watcher logs
docker logs cortex-mcp | grep "FileSystemEventHandler"
```

---

### Symptom: High Error Rate Alert

**Diagnostic Steps:**
```bash
# 1. Check error breakdown by type
curl http://localhost:8000/metrics | grep cortex_errors_total

# 2. Check recent error logs
docker logs --since 10m cortex-mcp | grep ERROR

# 3. Check tool timeout errors
docker logs cortex-mcp | grep "timeout"

# 4. Check orchestrator failures
docker logs cortex-mcp | grep "orchestrator_failure"
```

**Common Causes:**
- ❌ Tool timeout (long-running operations)
- ❌ Orchestrator initialization failure
- ❌ Database query timeout
- ❌ External API rate limiting

**Resolution:**
```bash
# Increase tool timeout (if needed)
export CORTEX_TOOL_TIMEOUT=300  # 5 minutes

# Restart service to clear transient errors
docker-compose restart cortex-mcp

# Check external API status
curl https://api.github.com/rate_limit  # Example

# Review orchestrator logs for failures
docker logs cortex-mcp | grep "orchestrator_failure" -A 10
```

---

### Symptom: Slow Request Latency (P95 > 5s)

**Diagnostic Steps:**
```bash
# 1. Check current latency distribution
curl http://localhost:8000/metrics | grep request_duration_seconds

# 2. Check tool invocation patterns
curl http://localhost:8000/metrics | grep tool_invocations_total

# 3. Check database query performance
docker exec cortex-mcp python -c "from cortex.brain.core.state_manager import get_state_manager; print(get_state_manager().get_stats())"

# 4. Check orchestrator latency
curl http://localhost:8000/health/orchestrators | jq '.orchestrators[] | select(.average_latency_ms > 1000)'
```

**Common Causes:**
- ❌ Database query slow (missing indexes)
- ❌ External API latency (GitHub, GitLab)
- ❌ Large file operations (semantic search)
- ❌ Orchestrator initialization overhead

**Resolution:**
```bash
# Add database indexes (if needed)
# See: cortex/brain/core/state_manager.py

# Cache external API responses
# See: cortex/brain/analysis/remote_cache.py

# Optimize semantic search
# Reduce file count in workspace

# Profile slow orchestrators
docker exec cortex-mcp python -m cProfile -s cumulative cortex/orchestrators/core/master_orchestrator.py
```

---

## Production Deployment

### Docker-Compose Monitoring Stack

**File:** `docker-compose.monitoring.yml`

**Services:**
- Prometheus (metrics collection)
- Grafana (visualization)
- AlertManager (alerting)

**Usage:**
```bash
# Start CORTEX with monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Check service status
docker-compose ps

# Access Grafana
open http://localhost:3000  # admin/changeme

# Access Prometheus
open http://localhost:9090

# Access AlertManager
open http://localhost:9093

# Stop monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml down
```

---

### Environment Variables

```bash
# Prometheus configuration
PROMETHEUS_RETENTION_TIME=30d
PROMETHEUS_SCRAPE_INTERVAL=15s

# Grafana configuration
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=changeme
GF_INSTALL_PLUGINS=redis-datasource

# AlertManager configuration
ALERTMANAGER_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

### Volume Persistence

```yaml
volumes:
  prometheus_data:  # Metrics storage (time-series database)
  grafana_data:     # Dashboard configurations
  alertmanager_data:  # Alert state and silences
```

**Backup Strategy:**
```bash
# Backup Prometheus data
docker run --rm -v cortex_prometheus_data:/data -v $(pwd):/backup busybox tar czf /backup/prometheus-backup.tar.gz /data

# Restore Prometheus data
docker run --rm -v cortex_prometheus_data:/data -v $(pwd):/backup busybox tar xzf /backup/prometheus-backup.tar.gz -C /
```

---

### Network Configuration

```yaml
networks:
  cortex-network:
    external: true  # Uses existing CORTEX network
```

**Verify Network:**
```bash
# Check network exists
docker network ls | grep cortex-network

# Inspect network
docker network inspect cortex-network

# Verify connectivity
docker exec cortex-mcp ping prometheus -c 3
```

---

## Maintenance Tasks

### Daily Tasks
- [ ] Check Grafana dashboard for anomalies
- [ ] Review alert notifications (Slack/email)
- [ ] Verify backup jobs completed

### Weekly Tasks
- [ ] Review error rate trends
- [ ] Check disk usage (Prometheus data)
- [ ] Update Grafana dashboard as needed
- [ ] Review and update alert thresholds

### Monthly Tasks
- [ ] Prometheus data retention cleanup (older than 30d)
- [ ] Grafana dashboard export (backup)
- [ ] Review alert escalation patterns
- [ ] Update runbook with new troubleshooting steps

---

## References

### Documentation
- [Phase 7.2 Completion Report](../../docs/phases/phase-7.2-observability-completion-report.md)
- [CORTEX Copilot Instructions](../../.github/copilot-instructions.md)
- [Docker Deployment Guide](../../docs/DOCKER-DEPLOYMENT-GUIDE.md)

### Implementation Files
- `cortex/mcp/health_checker.py` - Health endpoints
- `cortex/mcp/metrics_collector.py` - Prometheus metrics
- `cortex/mcp/tool_discovery.py` - Tool discovery
- `cortex/mcp/startup_banner.py` - Startup banner
- `cortex/mcp/wiring_watcher.py` - Hot-reload watcher

### External Resources
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

---

**Last Updated:** 2026-01-27  
**Version:** 1.0  
**Maintained By:** CORTEX Platform Team
