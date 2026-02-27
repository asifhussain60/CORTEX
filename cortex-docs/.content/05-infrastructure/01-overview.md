# Infrastructure Overview

---
title: Infrastructure — The Body That Houses the Brain
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/infrastructure/ + deployment/
order: 1
---

> **Brain analogy:** Infrastructure is the **skull, blood vessels, and immune system** — the body that protects, nourishes, and monitors the brain. The skull (security) shields against damage, blood vessels (databases, caches) deliver nutrients (data), and the immune system (health checks, circuit breakers) fights infection (failures).

---

## What CORTEX Infrastructure Provides

| Capability | Brain Analogy | Module |
|------------|---------------|--------|
| Audit & Compliance | Memory formation | `audit_db.py`, `audit_logger.py`, `audit_hash_chain.py` |
| Caching | Short-term memory | `cache_manager.py` |
| Circuit Breakers | Pain reflex | `circuit_breaker.py`, `git_circuit_breaker.py` |
| Database Management | Long-term memory | `database.py`, `database_transaction_manager.py` |
| Deployment | Body growth | `deployment/`, `kubernetes/`, `docker/` |
| Health Monitoring | Vital signs | `brain_health_metrics.py`, `threshold_monitor.py` |
| Logging | Journaling | `structured_logger.py`, `tiered_logger.py` |
| Observability | Self-awareness | `telemetry_provider.py`, `tracing.py`, `metrics_exporter.py` |
| Resilience | Immune system | `retry_handler.py`, `fault_isolator.py`, `crash_recovery.py` |
| Security | Skull & blood-brain barrier | `security/`, `secret_redactor.py`, `hash_verifier.py` |

---

## Architecture Layers

```
[Application Layer — 27 Wired Orchestrators (3 Tiers)]
         │
         ▼
[Infrastructure Layer — cortex/infrastructure/]
    ├── Audit: CortexAuditDB (SQLite WAL) + hash chain
    ├── Cache: Multi-level caching with TTL
    ├── Resilience: Circuit breakers, retry, degradation
    ├── Observability: OpenTelemetry + Prometheus
    ├── Security: Redaction, validation, pre-commit
    └── Database: Transaction management, log rotation
         │
         ▼
[Deployment Layer — deployment/]
    ├── Docker: Containerized builds
    ├── Kubernetes: Pod specifications
    ├── Nginx: Reverse proxy (dev + prod)
    ├── Prometheus: Metrics collection
    └── Grafana: Dashboard visualization
```

---

## Key Components

### CortexAuditDB — The Institutional Memory

- **Location:** `.cortex-runtime/` (SQLite WAL mode)
- **Module:** `cortex/infrastructure/audit_db.py`
- **Purpose:** Every operation recorded with hash-chain integrity
- **Features:** Write-ahead logging, concurrent reads, tamper detection

### Circuit Breakers — The Pain Reflex

- **Module:** `cortex/infrastructure/circuit_breaker.py`
- **States:** Closed (normal) → Open (failing) → Half-Open (testing recovery)
- **Scope:** Git operations, external APIs, database connections

### Structured Logging — The Journal

- **Module:** `cortex/infrastructure/structured_logger.py`
- **Tiers:** `tiered_logger.py` — DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Format:** Structured JSON with correlation IDs

---

## Infrastructure File Count

| Category | Files | Location |
|----------|-------|----------|
| Core infrastructure | 50+ modules | `cortex/infrastructure/` |
| Deployment | 12+ configs | `deployment/` |
| Security | Subdirectory | `cortex/infrastructure/security/` |
| CI/CD | Subdirectory | `cortex/infrastructure/ci_cd/` |
| LLM integration | Subdirectory | `cortex/infrastructure/llm/` |
| Collaboration | Subdirectory | `cortex/infrastructure/collaboration/` |

---

## Practical Examples

**Business Leader:** "Every action CORTEX takes is recorded in an immutable audit trail with hash-chain verification. If something goes wrong, we can trace exactly what happened, when, and why."

**Product Owner:** "Infrastructure runs silently — circuit breakers prevent cascading failures, retry handlers manage transient issues, and health monitors alert before problems impact users."

**Developer:** "I never interact with infrastructure directly. Circuit breakers wrap my git operations automatically. Audit logging happens behind the scenes. If my code creates a database transaction, `database_transaction_manager.py` handles rollback on failure."

---

*Verified against `cortex/infrastructure/` and `deployment/` · 25 February 2026*
