# Deployment

---
title: Deployment Architecture
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: deployment/
order: 3
---

> **Brain analogy:** Deployment is the **body's growth and maturation process** — from development (embryo) to staging (adolescence) to production (adulthood). Each stage has its own protections and validations.

---

## Deployment Modes

### Development (Local)

The default mode — MCP server runs in-process via VS Code:

```
VS Code → python3 -m cortex.mcp → stdio → Tool execution
```

- No Docker required
- No network ports
- IDE manages process lifecycle
- All 24 MCP tools available immediately

### Production (Containerized)

Full deployment stack using Docker + Kubernetes + Nginx:

```
[Client] → [Nginx (Reverse Proxy)]
              │
              ├── [CORTEX API Containers (K8s Pods)]
              │     ├── MCP Gateway
              │     └── Orchestrator Engine
              │
              ├── [Prometheus (Metrics)]
              │
              └── [Grafana (Dashboards)]
```

---

## Deployment Configuration Files

| File | Purpose |
|------|---------|
| `deployment/docker/` | Dockerfile(s) for containerized builds |
| `deployment/kubernetes/` | K8s manifests (pods, services, ingress) |
| `deployment/nginx.conf` | Development reverse proxy |
| `deployment/nginx.prod.conf` | Production reverse proxy with SSL |
| `deployment/prometheus.yml` | Development metrics scraping |
| `deployment/prometheus.prod.yml` | Production metrics configuration |
| `deployment/grafana-dashboards/` | Pre-built Grafana dashboard JSON |
| `deployment/health_checks.yaml` | Health check endpoint definitions |
| `deployment/canary_config.yaml` | Canary deployment parameters |
| `deployment/mcp-gateway-config.yaml` | MCP gateway routing configuration |
| `deployment/hooks/` | Deployment lifecycle hooks |
| `deployment/requirements.txt` | Production-specific dependencies |

---

## Canary Deployments

CORTEX supports canary deployments via `deployment/canary_config.yaml`:

1. **Deploy canary** — New version to 5% of traffic
2. **Monitor** — Health checks + error rate via Prometheus
3. **Promote** — Gradually increase to 25% → 50% → 100%
4. **Rollback** — Automatic rollback if error rate exceeds threshold

MCP tools for deployment management: `cortex/mcp/tools/deployment/`

| Tool | Purpose |
|------|---------|
| `canary_deployer.py` | Manage canary rollout percentages |
| `health_checker.py` | Validate deployment health |
| `release_builder.py` | Build release artifacts |
| `rollback.py` | Execute rollback operations |
| `sanitizer.py` | Pre-deployment sanitization checks |

---

## Health Checks

Defined in `deployment/health_checks.yaml`:

| Check | Type | Interval |
|-------|------|----------|
| MCP Server | Liveness | 30s |
| Orchestrator Engine | Readiness | 15s |
| Audit Database | Health | 60s |
| LENS Analyzers | Readiness | 30s |
| Governance Rules | Startup | Once |

---

## Pre-Deployment Validation

Before any deployment, CORTEX runs:

1. **Full test suite** — 15,333 tests must pass
2. **Golden tests** — 486 golden tests must pass (serial, deterministic)
3. **Governance check** — 17 active CORE rules enforced
4. **Security scan** — `cortex/infrastructure/security/` validators
5. **Pre-commit hooks** — `deployment/hooks/` + `cortex/infrastructure/pre_commit_validator.py`

---

## Practical Examples

**Business Leader:** "Development is zero-infrastructure — just open VS Code. Production uses standard Docker + Kubernetes with canary deployments for safe rollouts."

**Product Owner:** "Canary deployments mean we can ship features to 5% of traffic first, monitor for issues, and either promote or rollback automatically."

**Developer:** "I develop locally with stdio transport — no Docker needed. When I push to main, CI runs the full test suite, governance checks, and golden tests. Deployment is automated with canary support."

---

*Verified against `deployment/` directory · 20 February 2026*
