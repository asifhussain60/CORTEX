# CORTEX Architecture Documentation

---
title: CORTEX Architecture Overview
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-23
source_of_truth: cortex/ + cortex-registry/ + .github/copilot-instructions.md
format: diátaxis-explanation
voice: third-person-blended
---

> **Notice:** This documentation represents CORTEX as verified against live code on 23 February 2026. All metrics, module paths, and counts are validated against the running codebase. Every `cortex_intelligence/`, `cortex_lens/`, and `cortex.brain` reference has been eliminated — those packages were dissolved during the Cohesive Brain Refactor.

---

## Executive Summary

### CORTEX: Cognitive Real-Time Execution

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI engineering framework. Think of it as a **development nervous system** — the way your brain coordinates sensory input, decision-making, and motor execution in milliseconds, CORTEX coordinates code analysis, governance enforcement, and workflow execution for every development request.

**What makes it different from other dev tools:**

- Traditional tools answer questions. CORTEX **orchestrates entire workflows** — from intent classification through TDD enforcement to code delivery.
- One canonical Python package (`cortex`), 17 wired orchestrators across 3 tiers, 26 MCP tools, 35 active CORE rules governance rules.
- TDD is not optional. CORE-008 mandates RED → GREEN → REFACTOR on every IMPLEMENT/FIX request. No exceptions.
- Everything is Git-backed. No PostgreSQL, no MongoDB — just YAML files in `cortex-registry/` versioned alongside your code.

---

## System Metrics (23 Feb 2026 — Live)

| Metric | Value | Status |
|--------|-------|--------|
| **Package** | 1 canonical (`cortex`) | ✅ 3→1 consolidation complete |
| **Orchestrators** | 17 wired (7 core, 3 domain, 7 support) | ✅ IOrchestrator protocol enforced |
| **MCP Tools** | 26 active (28 total — 2 deprecated) | ✅ Pylance-style stdio server |
| **Top-level Dirs** | 16 canonical under `cortex/` | ✅ 59→16 cleanup complete |
| **Governance Rules** | 35 active CORE rules | ✅ Enforced at pre-commit + CI + runtime |
| **Test Suite** | 15,739 tests collected | ✅ Parallel xdist batch runner |
| **Parallel Testing** | pytest-xdist (`-n auto --dist loadscope`) | ✅ CortexXdistPlugin batch runner |
| **Enterprise Patterns** | 9 patterns in registry | ✅ mediator, strategy, observer, factory, etc. |
| **Sweep Completeness** | CORE-064 enforced via SweepCatalogueOrchestrator | ✅ No partial sweeps across sessions |
| **ScaffoldWriter** | Disk-emission for workflow pipeline artefacts | ✅ Gap G2 closed (BadMonolith) |
| **Roslyn by-name rename** | Symbol rename without byte offset | ✅ Gap G3 closed (BadMonolith) |

---

### Architecture at a Glance

```
  ┌───────────────────────────────────────────────────────────────┐
  │                     CORTEX PLATFORM v1.0.0                    │
  │             1 Package · 17 Orchestrators · 26 MCP Tools       │
  │                                                               │
  │  ┌─────────────┐   ┌──────────────────┐   ┌───────────────┐  │
  │  │ MCP Gateway │──▶│  Orchestration   │──▶│ Intelligence  │  │
  │  │ 26 tools    │   │  17 wired        │   │ LENS + Brain  │  │
  │  └─────────────┘   │  3 tiers         │   │ 8 analyzers   │  │
  │         │          └──────────────────┘   └───────────────┘  │
  │         ▼                   │                     │           │
  │  ┌─────────────┐   ┌──────────────────┐   ┌───────────────┐  │
  │  │ Governance  │   │  Testing         │   │ Registry      │  │
  │  │ 35 rules    │   │  15,739 tests    │   │ Git-backed    │  │
  │  │ CORE-064    │   │  xdist batch     │   │ YAML SSOT     │  │
  │  └─────────────┘   └──────────────────┘   └───────────────┘  │
  └───────────────────────────────────────────────────────────────┘
```

---

### Practical Daily Experience

**Business Leader:** "I see a platform where 17 governance rules are automatically enforced on every commit across all teams. Test quality is scored 0–9 and anything below 7 gets flagged. Zero governance violations reach production — the system blocks them at the gate."

**Product Owner:** "When I request a feature, I know TDD is enforced — not by policy, but by the system. The TDDOrchestrator writes the failing test first, then implements. I can pull sprint work items from ADO directly into developer context via `cortex_fetch_work_items`. I never chase test coverage; it's automatic."

**Developer:** "I type a request in VS Code. CORTEX enriches it (Stage -1), classifies intent (Stage 1), runs 8 parallel LENS analyzers, enforces governance, and executes. Everything imports from one package: `from cortex.orchestrators.core import TDDOrchestrator`. No more hunting through 3 packages."

---

## Key Changes Today (21 Feb 2026)

| Feature | Description |
|---------|-------------|
| **ScaffoldWriter** | New `cortex/core/scaffold_writer.py` — disk-emission of workflow `scaffold_files` so pipeline steps can depend on each other without halting mid-run (BadMonolith Gap G2) |
| **WorkflowEngine.load() + execute_step()** | SDO-compatible API in `cortex/core/workflow_engine.py` — all 8 BadMonolith steps execute end-to-end |
| **Roslyn by-name rename** | `RoslynAdapter` + `RefactoringService.cs` accept `symbol_name` key (no byte offset required) — Gap G3 |
| **CORE-064** | Sweep Completeness Contract — `SweepCatalogueOrchestrator` prevents partial sweeps across session boundaries |
| **CORE-055** | Golden Test Tier Contract — 696 golden tests always pass; zero regression allowed |
| **cortex_sweep_status** | MCP tool for CORE-064 sweep catalogue query/management |
| **cortex_fetch_work_items** | Phase 15 — provider-agnostic ADO/Jira/custom work item access via MCP |
| **SQLite Activity Log** | `OrchestratorBase.execute()/run()` auto-logs to `.cortex-runtime/audit.db` (never blocks execution) |
| **Zero CORE violations** | CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (duplicates) all at 0 |
| **L1 wiring fixes** | 6 wiring failures resolved; `RefactoringOrchestrator.health_check` bug fixed |

---

## Where to Go Next

| I want to understand… | Read this |
|-----------------------|-----------|
| Platform in one page | `00-getting-started/01-one-pager.md` |
| Core terminology | `00-getting-started/02-key-concepts.md` |
| End-to-end request flow | `00-getting-started/03-how-cortex-works.md` |
| Intelligence architecture | `00-getting-started/04-brain-tier-architecture.md` |
| Quick start (5 minutes) | `00-getting-started/05-quick-start.md` |
| All capabilities | `01-capabilities/01-overview.md` |
| LENS code intelligence | `02-lens/01-overview.md` |
| Orchestration pipeline | `03-orchestration/01-overview.md` |
| MCP tools catalog | `04-mcp/03-tools-catalog.md` |
| ADO / work item integration | `04-mcp/06-work-item-integration.md` |
| Infrastructure & deployment | `05-infrastructure/01-overview.md` |
| Architecture diagrams | `07-diagrams/01-overview.md` |
| Glossary | `glossary.md` |

---

*CORTEX v1.0.0 · 23 February 2026 · 17 wired orchestrators · 26 MCP tools · 35 CORE rules · 15,739 tests · 696 golden · Source of truth: `cortex-registry/planning/cortex-refactor-master.yaml`*

