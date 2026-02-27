# Infrastructure & Observability Stack
# Cross-cutting concerns: tracing, metrics, resilience, security

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     INFRASTRUCTURE LAYER                                     │
│                     cortex/infrastructure/ (50+ modules)                     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                    OBSERVABILITY (3 PILLARS)                         │    │
│  │                                                                      │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │    │
│  │  │  TRACING         │  │  METRICS         │  │  LOGGING         │    │    │
│  │  │  OpenTelemetry   │  │  Prometheus      │  │  SQLite WAL      │    │    │
│  │  │                  │  │                  │  │                  │    │    │
│  │  │  cortex/         │  │  cortex/         │  │  .cortex-        │    │    │
│  │  │  opentelemetry_  │  │  prometheus_     │  │  runtime/traces/ │    │    │
│  │  │  tracing.py      │  │  metrics.py      │  │  orchestrator-   │    │    │
│  │  │                  │  │                  │  │  traces.db       │    │    │
│  │  │  Spans:          │  │  Counters:       │  │                  │    │    │
│  │  │  • Request trace │  │  • Request count │  │  Tables:         │    │    │
│  │  │  • Orchestrator  │  │  • Error rate    │  │  • audit_sessions│    │    │
│  │  │    execution     │  │  • Latency P50   │  │  • audit_stage_  │    │    │
│  │  │  • LENS analysis │  │  • Latency P99   │  │    log           │    │    │
│  │  │  • Governance    │  │  Gauges:         │  │  • audit_        │    │    │
│  │  │    validation    │  │  • Active orchs  │  │    violations    │    │    │
│  │  │                  │  │  • Queue depth   │  │  • workflow_     │    │    │
│  │  │  Export:         │  │  Histograms:     │  │    cycles        │    │    │
│  │  │  Jaeger / OTLP   │  │  • Response time │  │  • workflow_runs │    │    │
│  │  └─────────────────┘  │  • Analysis time  │  └─────────────────┘    │    │
│  │                        │                  │                          │    │
│  │                        │  Export:          │  AC Markers on every    │    │
│  │                        │  Prometheus /     │  orchestrator call:     │    │
│  │                        │  Grafana          │  AC_START → AC_COMPLETE │    │
│  │                        └─────────────────┘                          │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                    RESILIENCE (9 PATTERNS)                           │    │
│  │                                                                      │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │    │
│  │  │ Circuit      │ │ Retry with   │ │ Bulkhead     │                  │    │
│  │  │ Breaker      │ │ Exponential  │ │ Isolation    │                  │    │
│  │  │              │ │ Backoff      │ │              │                  │    │
│  │  │ CLOSED→OPEN  │ │ max 3 tries  │ │ Thread pool  │                  │    │
│  │  │ →HALF_OPEN   │ │ jitter       │ │ per service  │                  │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘                  │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │    │
│  │  │ Timeout      │ │ Fallback     │ │ Rate Limit   │                  │    │
│  │  │ Guard        │ │ Strategy     │ │              │                  │    │
│  │  │              │ │              │ │ Token bucket │                  │    │
│  │  │ Configurable │ │ Default →    │ │ per tool     │                  │    │
│  │  │ per operation│ │ last known   │ │              │                  │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘                  │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  │    │
│  │  │ Graceful     │ │ Health Check │ │ Load Shed    │                  │    │
│  │  │ Degradation  │ │ Probe        │ │              │                  │    │
│  │  │              │ │              │ │ Drop lowest  │                  │    │
│  │  │ Reduce scope │ │ Liveness +   │ │ priority at  │                  │    │
│  │  │ not quality  │ │ readiness    │ │ high load    │                  │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘                  │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                    SECURITY                                          │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │    │
│  │  │ Secret Redaction  │  │ PII Removal      │  │ Input Validation │    │    │
│  │  │                   │  │                  │  │                  │    │    │
│  │  │ SanitizationOrch. │  │ Regex-based      │  │ JSON-RPC schema  │    │    │
│  │  │ scans all output  │  │ pattern matching │  │ validation       │    │    │
│  │  │ before delivery   │  │ before storage   │  │ on all inputs    │    │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘    │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```
