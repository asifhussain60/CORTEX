# CORTEX: Platform Overview

---
title: CORTEX — Intelligent Development Acceleration Platform
type: overview
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-18
format: one-pager
order: 1
---

> **What is CORTEX?** An AI-native development acceleration platform that combines a cognitive intelligence layer, automated governance, and a rich orchestration engine to help engineering teams ship faster — with confidence.

---

## The Core Idea

Traditional development tools answer questions. CORTEX **thinks alongside your team**.

When a developer makes a request — "implement this feature", "fix this bug", "audit this code" — CORTEX doesn't hand back a snippet. It classifies intent, analyses the codebase, validates against governance rules, generates tests first, and executes a coordinated multi-step workflow. Every action is observable, auditable, and reversible.

---

## Platform at a Glance

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                      CORTEX PLATFORM                             │
  │                                                                  │
  │  ┌─────────────┐   ┌────────────────┐   ┌────────────────────┐  │
  │  │  MCP Gateway│──▶│ Orchestration  │──▶│  Intelligence (LENS)│ │
  │  │  26 tools   │   │ 20+ engines    │   │  8 parallel analyzers│ │
  │  └─────────────┘   └────────────────┘   └────────────────────┘  │
  │          │                  │                      │             │
  │          ▼                  ▼                      ▼             │
  │  ┌─────────────┐   ┌────────────────┐   ┌────────────────────┐  │
  │  │  Governance │   │  Brain (3-Layer│   │   Knowledge Base   │  │
  │  │  59 rules   │   │  Perception →  │   │   45+ YAML guides  │  │
  │  │  7 agents   │   │  Reasoning →   │   │   Git-backed SSOT  │  │
  │  └─────────────┘   │  Action)       │   └────────────────────┘  │
  │                    └────────────────┘                            │
  └──────────────────────────────────────────────────────────────────┘
```

---

## Six Capability Domains

| Domain | What It Does | Key Metric |
|--------|-------------|------------|
| **🏗️ Core Platform** | MCP gateway, service orchestration, state management, health monitoring | P50 gateway latency: 5ms |
| **🤖 AI & Intelligence (LENS)** | 8-analyzer parallel code understanding — AST, Git, Security, Patterns, Metrics and more | 300–800ms full analysis |
| **🧠 Brain (3-Layer Learning)** | Perception → Reasoning → Action pipeline that learns from every repository interaction | Confidence scored 0.0–1.0 |
| **🎯 Decisioning** | Intent routing across 12 intent types to 20+ orchestrators; TDD workflow enforcement | 95%+ routing accuracy |
| **🛡️ Governance** | 4-layer pre/runtime/post/production enforcement of 59 CORE rules; immutable audit trail | <150ms validation |
| **🔌 Extensibility** | Custom MCP tools, domain orchestrators, knowledge integration, plugin adapters | Hot-reload; zero core changes |

---

## How a Request Flows

```
Developer request
      │
      ▼
[Stage -1] Request Pre-Processor ──── adds governance context + risk assessment
      │
      ▼
[MCP Gateway] ──── validates protocol, classifies tool tier
      │
      ▼
[Intent Router] ──── LENS-based classification (20–40ms)
      │
      ├─ IMPLEMENT/FIX ──▶ TDD Orchestrator  (RED → GREEN → REFACTOR)
      ├─ ANALYZE       ──▶ LENS Synthesis     (full 8-analyzer scan)
      ├─ REFACTOR      ──▶ Refactoring Engine (semantic, multi-language)
      ├─ PLAN          ──▶ Planning Orchestrator
      └─ AUDIT         ──▶ Enforcement + Audit Coordinator
                │
                ▼
      [Governance Gate] ──── 7 agents, blocks non-compliant actions
                │
                ▼
      [Brain Layer] ──── patterns → strategies → execution plan
                │
                ▼
      Result delivered inline (no report files created)
```

---

## The Brain in Three Sentences

CORTEX's **Perception Layer** scans every repository for known signatures — frameworks, patterns, risk indicators — and scores confidence for each match.  
The **Reasoning Layer** selects the best strategy from that pattern data, weighing historical success rates and context.  
The **Action Layer** converts the chosen strategy into a step-by-step execution plan with built-in validation and rollback.

This three-layer model means CORTEX improves with every project it touches — patterns learned in one repository inform recommendations in the next.

---

## Governance Is Not Optional

Every action runs through four enforcement layers:

1. **Pre-Execution Gate** — blocks violations before any code changes
2. **Runtime Monitor** — halts and rolls back on critical violations mid-flight
3. **Post-Execution Audit** — records complete AC-marker trail; detects bypass attempts
4. **Production Gate** — enforces coverage thresholds and security scans before deploy

59 CORE rules are enforced automatically; the most critical include TDD-first (CORE-008), no report file sprawl (CORE-002), and MCP-first architecture (CORE-049).

---

## What Developers Experience

| Workflow | Without CORTEX | With CORTEX |
|----------|---------------|-------------|
| New feature | Write code, hope tests follow | RED → GREEN → REFACTOR, enforced |
| Code review | Manual checklist | Automated 8-analyzer intelligence report |
| Governance | Periodic audit | Continuous, every request |
| Onboarding new repo | Days of reading | LENS onboarding + SQLite dashboard |
| Refactoring | Risky, manual | Semantic refactor with regression scoring |

---

## Technology Foundations

- **Protocol:** Model Context Protocol (JSON-RPC 2.0) — works with VS Code Copilot, Claude, Cursor
- **Transport:** stdio (dev) / HTTP on port 8000 (production)
- **Storage:** Git-backed registry — no PostgreSQL, no MongoDB required
- **Observability:** OpenTelemetry tracing, Prometheus metrics, Grafana dashboards
- **Languages supported by LENS:** Python, TypeScript/JavaScript, C#/.NET, Angular, React, Vue

---

## Where to Go Next

| I want to understand… | Read this |
|-----------------------|-----------|
| The Brain tier in depth | `00-getting-started/brain-tier-architecture.md` |
| How CORTEX fits into my team | `00-getting-started/how-cortex-works.md` |
| LENS intelligence details | `02-lens/01-overview.md` |
| Orchestration pipeline | `03-orchestration/01-overview.md` |
| Governance rules | `01-capabilities/governance-compliance.md` |
| MCP tools catalog | `04-mcp/tools-catalog.md` |
| Full capability inventory | `01-capabilities/01-overview.md` |

---

*CORTEX v8.1 · February 2026 · Source of truth: `cortex/__wiring_contract__.yaml` + `cortex-registry/`*
