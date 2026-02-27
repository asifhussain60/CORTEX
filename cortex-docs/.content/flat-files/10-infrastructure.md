---
title: Infrastructure
consolidates:
  - 05-infrastructure-overview.md
  - 05-infrastructure-tech-stack.md
  - 05-infrastructure-deployment.md
  - 05-infrastructure-ci-cd.md
  - 05-infrastructure-observability.md
  - 05-infrastructure-scalability.md
  - 05-infrastructure-ado-integration.md
last_verified: 2026-02-27
source_of_truth: cortex/infrastructure/ + deployment/ + cortex/observability/
audience: [Business Leaders, Product Owners, Software Developers]
---

# Infrastructure

CORTEX infrastructure provides audit and compliance, caching, circuit breakers, database management, deployment, health monitoring, logging, observability, resilience, and security. Every action is recorded in an immutable audit trail. The system is designed to survive component failures through nine production-grade resilience patterns.

---

## Technology Stack

### Core Language and Runtime

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.9 or higher |
| Package | cortex | Single canonical |
| Entry point | python3 -m cortex.mcp | Pylance-style stdio |

### Key Dependencies

| Category | Dependencies |
|----------|-------------|
| Testing | pytest, pytest-xdist (parallel), pytest-cov, pytest-timeout, pytest-mock |
| Observability | opentelemetry-api, opentelemetry-sdk, prometheus-client |
| Data and Storage | sqlite3 (stdlib WAL mode), pyyaml, json (stdlib) |
| Code Analysis | ast (stdlib), pathlib (stdlib), typing (stdlib) |
| Infrastructure | asyncio (stdlib), subprocess (stdlib), logging (stdlib), hashlib (stdlib) |

### Development Tools

VS Code as primary IDE, Copilot Chat as MCP client, pre-commit for governance hooks, and Make for build automation.

### Registry Formats

YAML for governance rules, workflow templates, and patterns. JSON for MCP protocol messages and configuration. SQLite for audit database and runtime state. HTML and CSS for documentation dashboards. Markdown for development documentation.

---

## Infrastructure Architecture

Location: `cortex/infrastructure/` — fifty or more modules.

| Capability | Key Modules |
|------------|-------------|
| Audit and Compliance | audit_db.py, audit_logger.py, audit_hash_chain.py, evidence_bundle.py |
| Caching | cache_manager.py |
| Circuit Breakers | circuit_breaker.py, git_circuit_breaker.py |
| Database Management | database.py, database_transaction_manager.py, database_log_rotation.py |
| Health Monitoring | brain_health_metrics.py, threshold_monitor.py |
| Logging | structured_logger.py, tiered_logger.py, log_growth_monitor.py |
| Resilience | retry_handler.py, fault_isolator.py, crash_recovery.py, graceful_degradation.py |
| Security | security/ subdirectory, secret_redactor.py, hash_verifier.py |

### CortexAuditDB — Institutional Memory

Location: `.cortex-runtime/` (SQLite WAL mode). Module: `cortex/infrastructure/audit_db.py`. Every operation is recorded with hash-chain integrity via `audit_hash_chain.py`. Each audit entry includes a cryptographic hash of the previous entry, creating a tamper-evident chain that detects any modification to historical records.

### Circuit Breakers

Module: `cortex/infrastructure/circuit_breaker.py`. States: Closed (normal operation) then Open (failures blocked after threshold exceeded) then Half-Open (testing recovery). When recovery succeeds the circuit returns to Closed. A specialised git circuit breaker at `git_circuit_breaker.py` wraps git operations specifically.

---

## Observability — Three Pillars

### Tracing (OpenTelemetry)

Modules: `telemetry_provider.py`, `trace_integration.py`, `tracing.py`, `orchestrator_trace_logger.py`, plus top-level `cortex/opentelemetry_tracing.py`.

What is traced: every MCP tool call (tool name, duration, result), every orchestrator execution (intent type, routing, duration), every LENS analysis (analyzers invoked, synthesis time), and every governance check (rule evaluated, pass or fail).

### Metrics (Prometheus)

Modules: `metrics_exporter.py`, `brain_health_metrics.py`, `infrastructure_prometheus.py`. Configuration: `deployment/prometheus.yml` (development) and `deployment/prometheus.prod.yml` (production). Dashboards: `deployment/grafana-dashboards/`.

Key metrics: cortex_request_duration_seconds, cortex_tool_invocations_total, cortex_test_execution_seconds, cortex_governance_violations_total, cortex_lens_analysis_seconds, cortex_circuit_breaker_state.

### Logging (Structured)

Modules: `structured_logger.py`, `tiered_logger.py`, `log_growth_monitor.py`. Log tiers: DEBUG (detailed execution flow), INFO (key events), WARNING (degraded state and retries), ERROR (failures requiring attention), CRITICAL (system-level failures). All logs use structured JSON with correlation IDs.

### Pre-built Grafana Dashboards

System Overview (request rate, error rate, latency P50/P95/P99), Orchestrator Health (per-orchestrator execution time and error rate), Test Pipeline (test suite duration, pass rate, golden test status), Governance (rule violations over time, compliance percentage).

---

## Resilience — Nine Patterns

| Pattern | Module | Purpose |
|---------|--------|---------|
| Circuit Breaker | circuit_breaker.py | Prevent cascading failures by stopping calls to failing services |
| Retry Handler | retry_handler.py, retry_strategy.py | Exponential backoff with jitter for transient failures |
| Graceful Degradation | graceful_degradation.py, degradation_manager.py | Return partial results when non-critical services fail |
| Fault Isolation | fault_isolator.py, bulkhead_manager.py | Bulkhead pattern — isolate failing components, partition resources |
| Rate Limiting | rate_limiter.py | Per-tool and per-orchestrator rate control |
| Crash Recovery | crash_recovery.py | Checkpoint-based recovery from audit trail |
| Connection Pooling | connection_pool.py | Efficient database and external service connections |
| Resource Tracking | resource_tracker.py | Memory, file handles, and database connection monitoring |
| File Locking | file_lock.py | Prevent concurrent writes to shared files |

### Hardening

Modules: `hardening_integration.py`, `startup_validator.py`, `lifecycle_manager.py`, `infrastructure_config.py`, `infrastructure_scanner.py`.

---

## Deployment Architecture

### Development (Local)

The default mode — MCP server runs in-process via VS Code through stdio transport. No Docker required, no network ports, IDE manages process lifecycle, and all registered MCP tools are available immediately.

### Production (Containerised)

Full deployment stack using Docker, Kubernetes, and Nginx. Configuration files in `deployment/`:

| File | Purpose |
|------|---------|
| docker/ | Containerised builds |
| kubernetes/ | K8s manifests (pods, services, ingress) |
| nginx.conf | Development reverse proxy |
| nginx.prod.conf | Production reverse proxy with SSL |
| prometheus.yml | Development metrics scraping |
| prometheus.prod.yml | Production metrics configuration |
| grafana-dashboards/ | Pre-built Grafana dashboard JSON |
| health_checks.yaml | Health check endpoint definitions |
| canary_config.yaml | Canary deployment parameters |
| mcp-gateway-config.yaml | MCP gateway routing configuration |

### Canary Deployments

CORTEX supports canary deployments: deploy new version to five percent of traffic, monitor health checks and error rate via Prometheus, gradually promote to twenty-five then fifty then one hundred percent, with automatic rollback if the error rate exceeds threshold.

### Horizontal Scaling

Kubernetes pod-based horizontal scaling. Each pod runs a full CORTEX instance sharing the audit database. Test parallelism uses all available CPU cores by default via pytest-xdist.

---

## CI/CD Pipeline

### Pipeline Stages

1. **Lint and Type Check**: CORE-011 (type hints), CORE-028 (snake_case file naming)
2. **Unit Tests (Parallel)**: pytest with xdist distributing by module scope across all cores
3. **Golden Tests (Serial)**: Golden tests run sequentially for deterministic results — must always pass
4. **Governance Validation**: Thirty-eight active CORE rules enforced by EnforcementOrchestrator
5. **Integration Tests**: Cross-orchestrator flows distributed by file
6. **Security Scan**: CORE-035 analysis, secret detection, import validation

### CI/CD Modules

| Module | Location | Purpose |
|--------|----------|---------|
| core_035_analyzer.py | cortex/infrastructure/ci_cd/ | Analyse for duplicate implementations |
| enforce_core_035.py | cortex/infrastructure/ci_cd/ | Enforce single canonical rule |
| production_release.py | cortex/infrastructure/ci_cd/ | Production release gating |
| pre_commit_validator.py | cortex/infrastructure/ | Pre-commit validation |

### Governance Gates Before Merge

| Gate | Rule | Action on Failure |
|------|------|-------------------|
| Type hints | CORE-011 | Block merge |
| Docstrings | CORE-012 | Block merge |
| File naming | CORE-028 | Block merge |
| No duplicates | CORE-035 | Block merge |
| TDD compliance | CORE-008 | Block merge |
| Holistic validation | CORE-048 | Block merge |

### Test Tiers

| Tier | Execution | Purpose |
|------|-----------|---------|
| Smoke | Parallel | Quick validation under sixty seconds |
| Unit | Parallel (loadscope) | Module-level correctness |
| Golden | Serial | Regression-proof specifications |
| Integration | Parallel (loadfile) | Cross-component flows |

---

## ADO Integration

CORTEX integrates with Azure DevOps through the provider-agnostic WorkItemProvider Protocol. The ADOWorkItemProvider fetches user stories, bugs, and tasks. The ADOContextMapper normalises them into structured sprint context consumed by UnifiedIntelligenceProvider.full().

### Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| WORK_ITEM_SOURCE | No (defaults to "ado") | Provider selector |
| ADO_ORG_URL | Yes | Azure DevOps organisation URL |
| ADO_PAT | Yes | Personal Access Token |
| ADO_PROJECT | Yes | Default project name |

### ADOContextMapper

Converts WorkItem objects into structured sprint context: sprint name (from System.IterationPath last segment), stories list, open count, and in-progress count. This context is injected into company_knowledge.domain_rules so orchestrators can cross-reference sprint items with LENS findings — for example, surfacing PCI-DSS rules automatically when a story touches the payment module.

### Custom Providers

To replace ADO with Jira or a custom system: set the WORK_ITEM_SOURCE environment variable, implement the WorkItemProvider Protocol, and register the provider. The MCP tool surface (`cortex_fetch_work_items`) remains unchanged regardless of the ticketing system.

---

*All module paths and infrastructure component counts verified against live codebase*
