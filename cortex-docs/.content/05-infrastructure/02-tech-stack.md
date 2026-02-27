# Tech Stack

---
title: Technology Stack & Dependencies
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: requirements.txt + pyproject.toml
order: 2
---

> **Brain analogy:** The tech stack is the **biochemistry** of the brain — the neurotransmitters (Python), enzymes (pytest), and hormones (OpenTelemetry) that make everything work at the molecular level.

---

## Core Language & Runtime

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.9+ |
| Package | `cortex` | Single canonical (v1.0.0) |
| Entry point | `python3 -m cortex.mcp` | Pylance-style stdio |

---

## Framework Dependencies

### Testing

| Dependency | Purpose |
|------------|---------|
| `pytest` | Test framework — 16,942 tests |
| `pytest-xdist` | Parallel execution (`-n auto --dist loadscope`) |
| `pytest-cov` | Coverage measurement |
| `pytest-timeout` | Test timeout enforcement |
| `pytest-mock` | Mocking utilities |

### Observability

| Dependency | Purpose |
|------------|---------|
| `opentelemetry-api` | Distributed tracing API |
| `opentelemetry-sdk` | Tracing SDK implementation |
| `prometheus-client` | Metrics exposition |

### Data & Storage

| Dependency | Purpose |
|------------|---------|
| `sqlite3` (stdlib) | CortexAuditDB (WAL mode) |
| `pyyaml` | YAML governance rules, registry |
| `json` (stdlib) | JSON-RPC 2.0, configuration |

### Code Analysis

| Dependency | Purpose |
|------------|---------|
| `ast` (stdlib) | AST analysis (LENS analyzer) |
| `pathlib` (stdlib) | Cross-platform path handling |
| `typing` (stdlib) | Type hints (CORE-011) |

### Infrastructure

| Dependency | Purpose |
|------------|---------|
| `asyncio` (stdlib) | Async orchestrator execution |
| `subprocess` (stdlib) | Git operations, process spawning |
| `logging` (stdlib) | Structured logging foundation |
| `hashlib` (stdlib) | Hash-chain audit integrity |

---

## Development Tools

| Tool | Purpose |
|------|---------|
| VS Code | Primary IDE |
| Copilot Chat | MCP client (tool calling) |
| pre-commit | Pre-commit governance hooks |
| Make | Build automation (`Makefile`) |

---

## Deployment Stack

| Component | Technology | File |
|-----------|------------|------|
| Containerization | Docker | `deployment/docker/` |
| Orchestration | Kubernetes | `deployment/kubernetes/` |
| Reverse Proxy | Nginx | `deployment/nginx.conf`, `nginx.prod.conf` |
| Metrics | Prometheus | `deployment/prometheus.yml` |
| Dashboards | Grafana | `deployment/grafana-dashboards/` |

---

## Registry Format

| Format | Usage |
|--------|-------|
| YAML | Governance rules, workflow templates, patterns |
| JSON | MCP protocol messages, configuration |
| SQLite | Audit database, runtime state |
| HTML/CSS | Documentation dashboards |
| Markdown | Development documentation |

---

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Python 3.9+ | Minimum version for `typing` features needed by CORE-011 |
| Single package (`cortex`) | CORE-035 — no duplicate implementations |
| stdio transport | Zero-config, IDE-managed lifecycle |
| SQLite WAL | Concurrent reads, single-writer, no external DB server |
| pytest-xdist | 16,942 tests must run in reasonable time |
| YAML registry | Human-readable governance rules, version-controlled |

---

## Practical Examples

**Product Owner:** "Pure Python, no external database servers, no message queues. The entire platform runs with `pip install -r requirements.txt` and a VS Code workspace."

**Developer:** "Python 3.9+ with stdlib for most heavy lifting. pytest-xdist for parallel testing. SQLite WAL for audit. YAML for governance rules. Everything is file-based and version-controlled."

---

*Verified against `requirements.txt` and `pyproject.toml` · 25 February 2026*
