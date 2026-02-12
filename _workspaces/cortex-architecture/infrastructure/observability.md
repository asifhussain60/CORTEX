# Observability

**Purpose:** Monitoring, logging, and tracing for CORTEX  
**Audience:** SRE, DevOps  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Metrics](#metrics)
- [Logging](#logging)
- [Tracing](#tracing)
- [Alerting](#alerting)
- [Dashboards](#dashboards)
- [Related Documents](#related-documents)

---

## Overview

CORTEX implements the three pillars of observability: metrics, logs, and traces.

```
┌─────────────────────────────────────────────────────────────────┐
│                 OBSERVABILITY STACK                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     CORTEX Services                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ Metrics  │  │  Logs    │  │  Traces  │              │   │
│  │  │ Exporter │  │ Emitter  │  │ Exporter │              │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘              │   │
│  └───────┼─────────────┼─────────────┼─────────────────────┘   │
│          │             │             │                          │
│          ▼             ▼             ▼                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │
│  │  Prometheus  │ │    Loki      │ │    Jaeger    │           │
│  │  (Metrics)   │ │   (Logs)     │ │  (Traces)    │           │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘           │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      Grafana                             │   │
│  │              (Unified Visualization)                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Metrics

### Prometheus Integration

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Request metrics
REQUEST_COUNT = Counter(
    'cortex_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'cortex_request_duration_seconds',
    'Request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Cache metrics
CACHE_HITS = Counter(
    'cortex_cache_hits_total',
    'Cache hits',
    ['cache_level']  # l1, l2, l3
)

CACHE_MISSES = Counter(
    'cortex_cache_misses_total',
    'Cache misses',
    ['cache_level']
)

# Orchestrator metrics
ORCHESTRATOR_COUNT = Gauge(
    'cortex_orchestrators_registered',
    'Number of registered orchestrators'
)

ORCHESTRATOR_LATENCY = Histogram(
    'cortex_orchestrator_duration_seconds',
    'Orchestrator execution time',
    ['orchestrator', 'intent']
)

# LENS metrics
LENS_ANALYSIS_TIME = Histogram(
    'cortex_lens_analysis_seconds',
    'LENS analysis duration',
    ['analyzer']
)

# Middleware
class MetricsMiddleware:
    async def __call__(self, request, call_next):
        start = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
```

### Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `cortex_requests_total` | Counter | Total requests |
| `cortex_request_duration_seconds` | Histogram | Request latency |
| `cortex_cache_hits_total` | Counter | Cache hits |
| `cortex_orchestrators_registered` | Gauge | Active orchestrators |
| `cortex_lens_analysis_seconds` | Histogram | LENS analysis time |
| `cortex_errors_total` | Counter | Error count |

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - /etc/prometheus/rules/*.yaml

scrape_configs:
  - job_name: 'cortex-mcp'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: cortex-mcp
    metrics_path: /metrics

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

---

## Logging

### Structured Logging

```python
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
async def handle_request(request: MCPRequest):
    log = logger.bind(
        request_id=request.id,
        tool=request.tool,
        client_id=request.client_id
    )
    
    log.info("processing_request")
    
    try:
        result = await process(request)
        log.info("request_completed", status="success")
        return result
    except Exception as e:
        log.error("request_failed", error=str(e), exc_info=True)
        raise
```

### Log Format

```json
{
    "timestamp": "2026-02-10T14:30:00.123456Z",
    "level": "info",
    "event": "processing_request",
    "request_id": "req-12345",
    "tool": "cortex_lens_analyze",
    "client_id": "client-001",
    "service": "cortex-mcp",
    "pod": "cortex-mcp-abc123"
}
```

### Log Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed debugging info |
| INFO | Normal operations |
| WARNING | Potential issues |
| ERROR | Errors requiring attention |
| CRITICAL | System failures |

---

## Tracing

### OpenTelemetry Integration

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("cortex.mcp")

# Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name=os.environ.get("JAEGER_HOST", "jaeger"),
    agent_port=int(os.environ.get("JAEGER_PORT", 6831)),
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Usage
async def handle_request(request: MCPRequest):
    with tracer.start_as_current_span(
        "handle_request",
        attributes={
            "request.id": request.id,
            "request.tool": request.tool,
        }
    ) as span:
        # Intent classification
        with tracer.start_as_current_span("classify_intent"):
            intent = await classify_intent(request)
            span.set_attribute("intent", intent.value)
        
        # LENS analysis
        with tracer.start_as_current_span("lens_analysis"):
            context = await lens_analyze(request.target)
        
        # Orchestrator execution
        with tracer.start_as_current_span("orchestrator_execution"):
            result = await orchestrator.process(request, context)
        
        return result
```

### Trace Structure

```
├─ handle_request (root span)
│  ├─ classify_intent
│  ├─ lens_analysis
│  │  ├─ git_analyzer
│  │  ├─ ast_analyzer
│  │  └─ comment_analyzer
│  ├─ orchestrator_execution
│  │  ├─ validation
│  │  └─ execution
│  └─ response_formatting
```

---

## Alerting

### Alert Rules

```yaml
# alerts.yaml
groups:
  - name: cortex-alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(cortex_errors_total[5m])) 
          / sum(rate(cortex_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
      
      # High latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, 
            rate(cortex_request_duration_seconds_bucket[5m])
          ) > 2.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High P95 latency"
          description: "P95 latency is {{ $value | humanizeDuration }}"
      
      # Low cache hit rate
      - alert: LowCacheHitRate
        expr: |
          sum(rate(cortex_cache_hits_total[5m]))
          / (sum(rate(cortex_cache_hits_total[5m])) 
             + sum(rate(cortex_cache_misses_total[5m]))) < 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }}"
      
      # Orchestrator unavailable
      - alert: OrchestratorDown
        expr: cortex_orchestrators_registered < 20
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Orchestrators unavailable"
          description: "Only {{ $value }} orchestrators registered"
```

### Alert Routing

```yaml
# alertmanager.yml
route:
  receiver: 'default'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@example.com'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<key>'
  
  - name: 'slack'
    slack_configs:
      - api_url: '<webhook>'
        channel: '#cortex-alerts'
```

---

## Dashboards

### Grafana Dashboard (JSON)

```json
{
  "title": "CORTEX Overview",
  "panels": [
    {
      "title": "Request Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "sum(rate(cortex_requests_total[5m]))",
          "legendFormat": "Requests/sec"
        }
      ]
    },
    {
      "title": "Latency Distribution",
      "type": "heatmap",
      "targets": [
        {
          "expr": "sum(rate(cortex_request_duration_seconds_bucket[5m])) by (le)"
        }
      ]
    },
    {
      "title": "Error Rate",
      "type": "gauge",
      "targets": [
        {
          "expr": "sum(rate(cortex_errors_total[5m])) / sum(rate(cortex_requests_total[5m]))"
        }
      ]
    },
    {
      "title": "Cache Hit Rate",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(cortex_cache_hits_total[5m])) / (sum(rate(cortex_cache_hits_total[5m])) + sum(rate(cortex_cache_misses_total[5m])))"
        }
      ]
    }
  ]
}
```

### Dashboard Categories

| Dashboard | Purpose |
|-----------|---------|
| CORTEX Overview | High-level system health |
| Request Latency | P50/P95/P99 latencies |
| Error Analysis | Error rates by type |
| Cache Performance | Hit rates, evictions |
| Orchestrator Status | Registration, latency |

---

## Related Documents

- [Infrastructure Overview](overview.md) — Architecture
- [Deployment](deployment.md) — Deployment
- [Scalability](scalability.md) — Scaling

---

*Part of CORTEX Architecture Documentation*
