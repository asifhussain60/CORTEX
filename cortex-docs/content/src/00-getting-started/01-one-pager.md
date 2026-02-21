# CORTEX: Platform Overview

---
title: CORTEX — Cognitive Real-Time Execution Platform
type: overview
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-21
source_of_truth: cortex/ + cortex-registry/planning/cortex-refactor-master.yaml
format: one-pager
order: 1
---

> **What is CORTEX?** A production-grade AI engineering framework that combines cognitive intelligence, automated governance, and a 22-orchestrator execution engine to help engineering teams ship faster — with confidence.

---

## The Core Idea

Traditional development tools answer questions. CORTEX **thinks alongside your team**.

When a developer makes a request — "implement this feature", "fix this bug", "audit this code" — CORTEX doesn't hand back a snippet. It classifies intent, analyses the codebase with 8 parallel LENS analyzers, validates against 22 governance rules, generates tests first (mandatory), and executes a coordinated multi-step workflow through the appropriate orchestrator. Every action is observable, auditable, and reversible.

Think of it like the difference between a calculator and a brain. A calculator waits for instructions. A brain perceives the situation, reasons about the best approach, and acts — learning from every interaction.

---

## Platform at a Glance

```
  ┌───────────────────────────────────────────────────────────────┐
  │                  CORTEX PLATFORM v1.0.0                       │
  │                  1 Package · 22 Orchestrators · 25 MCP Tools  │
  │                                                               │
  │  ┌──────────────┐  ┌───────────────────┐  ┌───────────────┐  │
  │  │ MCP Gateway  │─▶│  Orchestration    │─▶│ Intelligence  │  │
  │  │ 25 tools     │  │  3 tiers          │  │ LENS + Brain  │  │
  │  │ stdio/HTTP   │  │  22 wired         │  │ 8 analyzers   │  │
  │  └──────────────┘  └───────────────────┘  └───────────────┘  │
  │         │                   │                     │           │
  │         ▼                   ▼                     ▼           │
  │  ┌──────────────┐  ┌───────────────────┐  ┌───────────────┐  │
  │  │ Governance   │  │  Testing          │  │ Git Registry  │  │
  │  │ 22 CORE rules│  │  15,328 tests     │  │ YAML SSOT     │  │
  │  │ CORE-064     │  │  601 golden       │  │ 9 patterns    │  │
  │  └──────────────┘  └───────────────────┘  └───────────────┘  │
  └───────────────────────────────────────────────────────────────┘
```

---

## Six Capability Domains

| Domain | What It Does | Key Metric |
|--------|-------------|------------|
| **🏗️ Core Platform** | MCP gateway, 22-orchestrator dispatch, state management, health monitoring | 25 MCP tools, Pylance-style stdio |
| **🤖 Intelligence (LENS)** | 8-analyzer parallel code understanding — AST, Git, Security, Patterns, Metrics, and more | 300–800ms full analysis |
| **🧠 Brain (Perception → Reasoning → Action)** | Pattern recognition, strategy selection, execution planning — learns from every repo | Confidence scored 0.0–1.0 |
| **🎯 Decisioning** | Intent routing across 10+ intent types to 22 wired orchestrators; TDD workflow enforcement | IntentRouter with LENS classification |
| **🛡️ Governance** | Pre-commit + CI + runtime enforcement of 22 active CORE rules; CORE-064 sweep completeness | 7 agents, <150ms validation |
| **🔌 Extensibility** | Custom MCP tools, domain orchestrators, workflow templates, enterprise patterns | Hot-reload; zero core changes |

---

## How a Request Flows

```
Developer request ("implement auth middleware")
      │
      ▼
[Stage -1] RequestRephraseOrchestrator ── enriches with governance + risk context
      │
      ▼
[Stage 0] MCP Gateway ── validates JSON-RPC, routes to tool
      │
      ▼
[Stage 1] IntentRouter ── LENS-based classification → IMPLEMENT
      │
      ├─ IMPLEMENT/FIX ──▶ TDDOrchestrator  (RED → GREEN → REFACTOR)
      ├─ ANALYZE       ──▶ LENS Synthesis    (8-analyzer parallel scan)
      ├─ REFACTOR      ──▶ RefactoringOrchestrator (semantic, multi-language)
      ├─ PLAN          ──▶ PlanningOrchestrator
      ├─ AUDIT         ──▶ EnforcementOrchestrator + Audit Coordinator
      ├─ DESIGN        ──▶ Design Orchestrator
      └─ DEBUG         ──▶ DebuggerOrchestrator
                │
                ▼
      [Governance Gate] ── 7 enforcement agents, blocks non-compliant actions
                │
                ▼
      [Intelligence Layer] ── perception → reasoning → action plan
                │
                ▼
      Result delivered inline (CORE-002: no report files created)
```

---

## The Brain in Three Sentences

CORTEX's **Perception Layer** (in `cortex/intelligence/perception/`) scans every repository for known signatures — frameworks, patterns, risk indicators — and scores confidence for each match.
The **Reasoning Layer** (in `cortex/intelligence/reasoning/`) selects the best strategy from that pattern data, weighing historical success rates and context.
The **Action Layer** (in `cortex/intelligence/action/`) converts the chosen strategy into a step-by-step execution plan with built-in TDD gates and rollback.

This three-layer model means CORTEX improves with every project it touches — patterns learned in one repository inform recommendations in the next.

---

## Governance Is Not Optional

Every action runs through governance enforcement:

1. **Pre-Commit Gate** — EnforcementOrchestrator with 7 agents blocks violations before code changes
2. **CI Pipeline** — Automated validation in continuous integration
3. **Runtime Enforcement** — Rules checked during orchestrator execution

22 active CORE rules are enforced automatically; the most critical include:
- **CORE-008** — TDD mandatory (write failing test first, no exceptions)
- **CORE-002** — All output inline (never create .md/.txt report files)
- **CORE-011** — Type hints on all functions
- **CORE-012** — Docstrings on all public APIs
- **CORE-035** — Single canonical implementation (no duplicates)
- **CORE-028** — File naming: snake_case only
- **CORE-064** — Sweep Completeness Contract (no partial sweeps across session boundaries)
- **CORE-055** — Golden Test Tier Contract (601 golden tests always pass)

---

## What Developers Experience

| Workflow | Without CORTEX | With CORTEX |
|----------|---------------|-------------|
| New feature | Write code, hope tests follow | RED → GREEN → REFACTOR, enforced by CORE-008 |
| Code review | Manual checklist | Automated 8-analyzer LENS intelligence scan |
| Governance | Periodic audit | Continuous, every request, every commit |
| Onboarding new repo | Days of reading | LENS onboarding + infrastructure catalog |
| Refactoring | Risky, manual | Semantic refactor with regression scoring |
| Test quality | Subjective | Scored 0–9 by TestQualityGate; <7 flagged |

---

## Technology Foundations

- **Protocol:** Model Context Protocol (JSON-RPC 2.0) — works with VS Code Copilot, Claude, Cursor
- **Transport:** stdio (development) / HTTP (production)
- **Package:** 1 canonical Python package (`cortex`) — all imports use `cortex.*`
- **Storage:** Git-backed registry — no PostgreSQL, no MongoDB required
- **Testing:** pytest-xdist parallel execution (`-n auto --dist loadscope`); 15,328 tests, 601 golden
- **Observability:** OpenTelemetry tracing, Prometheus metrics, Grafana dashboards, SQLite audit log (`.cortex-runtime/audit.db`)
- **Languages analyzed by LENS:** Python, TypeScript/JavaScript, C#/.NET, Angular, React, Vue

---

## Where to Go Next

| I want to understand… | Read this |
|-----------------------|-----------|
| Core terminology | `00-getting-started/02-key-concepts.md` |
| End-to-end request lifecycle | `00-getting-started/03-how-cortex-works.md` |
| Intelligence architecture | `00-getting-started/04-brain-tier-architecture.md` |
| Quick start (5 minutes) | `00-getting-started/05-quick-start.md` |
| LENS intelligence details | `02-lens/01-overview.md` |
| Orchestration pipeline | `03-orchestration/01-overview.md` |
| Governance rules | `01-capabilities/07-governance-compliance.md` |
| MCP tools catalog | `04-mcp/03-tools-catalog.md` |
| Full capability inventory | `01-capabilities/01-overview.md` |

---

*CORTEX v1.0.0 · February 2026 · 22 wired orchestrators · 25 MCP tools · 22 CORE rules · 15,328 tests · Source of truth: `cortex-registry/planning/cortex-refactor-master.yaml`*
