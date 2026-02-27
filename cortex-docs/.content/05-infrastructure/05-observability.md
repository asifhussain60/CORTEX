# Observability

---
title: Observability — Tracing, Metrics & Logging
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/infrastructure/ + cortex/observability/ + deployment/prometheus.yml
order: 5
---

> **Brain analogy:** Observability is **proprioception** — the brain's awareness of its own body. You know where your hand is without looking at it. CORTEX knows its own state — latency, throughput, error rates — without external monitoring.

---

## Three Pillars

### 1. Tracing (OpenTelemetry)

| Component | Module |
|-----------|--------|
| Provider | `cortex/infrastructure/telemetry_provider.py` |
| Integration | `cortex/infrastructure/trace_integration.py` |
| Tracing | `cortex/infrastructure/tracing.py` |
| Trace Logger | `cortex/infrastructure/orchestrator_trace_logger.py` |
| Top-level | `cortex/opentelemetry_tracing.py` |

**What's traced:**
- Every MCP tool call (tool name, duration, result)
- Every orchestrator execution (intent type, routing, duration)
- Every LENS analysis (analyzers invoked, synthesis time)
- Every governance check (rule evaluated, pass/fail)

### 2. Metrics (Prometheus)

| Component | Module |
|-----------|--------|
| Metrics | `cortex/infrastructure/metrics_exporter.py` |
| Brain Health | `cortex/infrastructure/brain_health_metrics.py` |
| Prometheus | `cortex/infrastructure/infrastructure_prometheus.py` |
| Config (dev) | `deployment/prometheus.yml` |
| Config (prod) | `deployment/prometheus.prod.yml` |
| Dashboards | `deployment/grafana-dashboards/` |
| Top-level | `cortex/prometheus_metrics.py` |

**Key metrics:**
- `cortex_request_duration_seconds` — Request processing time
- `cortex_tool_invocations_total` — MCP tool call count
- `cortex_test_execution_seconds` — Test suite duration
- `cortex_governance_violations_total` — Rule violation count
- `cortex_lens_analysis_seconds` — LENS pipeline duration
- `cortex_circuit_breaker_state` — Circuit breaker open/closed

### 3. Logging (Structured)

| Component | Module |
|-----------|--------|
| Structured Logger | `cortex/infrastructure/structured_logger.py` |
| Tiered Logger | `cortex/infrastructure/tiered_logger.py` |
| Log Growth Monitor | `cortex/infrastructure/log_growth_monitor.py` |
| Database Log Rotation | `cortex/infrastructure/database_log_rotation.py` |
| Health Check Service | `cortex/health_check_service.py` |

**Log tiers:**
- `DEBUG` — Detailed execution flow
- `INFO` — Key events (tool calls, orchestrator routing)
- `WARNING` — Degraded state, retries
- `ERROR` — Failures requiring attention
- `CRITICAL` — System-level failures

---

## Observability Module

| Component | Location |
|-----------|----------|
| Observability package | `cortex/observability/` |
| Alert Manager | `cortex/infrastructure/alert_manager.py` |
| Threshold Monitor | `cortex/infrastructure/threshold_monitor.py` |
| Progress Tracker | `cortex/infrastructure/progress_tracker.py` |
| Progress Aggregator | `cortex/infrastructure/progress_aggregator.py` |

---

## Audit Trail

All operations are recorded in `CortexAuditDB` (SQLite WAL):

| Component | Module |
|-----------|--------|
| Audit Database | `cortex/infrastructure/audit_db.py` |
| Audit Logger | `cortex/infrastructure/audit_logger.py` |
| Enhanced Audit | `cortex/infrastructure/enhanced_audit_logger.py` |
| Hash Chain | `cortex/infrastructure/audit_hash_chain.py` |
| Evidence Bundle | `cortex/infrastructure/evidence_bundle.py` |
| Event Replay | `cortex/infrastructure/event_replay_debugger.py` |

**Hash chain integrity:** Each audit entry includes a cryptographic hash of the previous entry, creating a tamper-evident chain.

---

## Resilience Observability

Resilience patterns are observable through metrics and logs:

| Pattern | Module | Observable Signal |
|---------|--------|-------------------|
| Circuit Breaker | `circuit_breaker.py` | State transitions (closed → open → half-open) |
| Retry Handler | `retry_handler.py` | Retry count, backoff duration |
| Graceful Degradation | `graceful_degradation.py` | Degradation events |
| Fault Isolation | `fault_isolator.py` | Isolated component count |
| Bulkhead | `bulkhead_manager.py` | Resource partition utilization |
| Rate Limiter | `rate_limiter.py` | Throttled requests |
| DLQ Inspector | `dlq_inspector.py` | Dead letter queue depth |

---

## Grafana Dashboards

Pre-built dashboards in `deployment/grafana-dashboards/`:

- **System Overview** — Request rate, error rate, latency P50/P95/P99
- **Orchestrator Health** — Per-orchestrator execution time and error rate
- **Test Pipeline** — Test suite duration, pass rate, golden test status
- **Governance** — Rule violations over time, compliance percentage

---

## Practical Examples

**Business Leader:** "Every action is traceable. The audit trail is tamper-proof — hash-chain verification means nobody can edit history without detection."

**Product Owner:** "Grafana dashboards show real-time health. I can see test pass rates, governance compliance, and orchestrator performance at a glance."

**Developer:** "When something fails, I follow the trace — OpenTelemetry gives me the full call path from MCP tool call through orchestrator to LENS analysis. The structured logger shows exact parameters and return values."

---

*Verified against `cortex/infrastructure/` and `deployment/`*
