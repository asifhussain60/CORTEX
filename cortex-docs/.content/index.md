# CORTEX Architecture Documentation

---
title: CORTEX Architecture Overview
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/ + cortex-registry/cortex-master.yaml + .github/copilot-instructions.md
format: diátaxis-explanation
voice: third-person-blended
---

> **Notice:** This documentation represents CORTEX as verified against live code. All module paths and capabilities are validated against the running codebase. CORTEX is under continuous evolution — specific counts may change as the platform grows.

---

## Executive Summary

### CORTEX: Cognitive Real-Time Execution

CORTEX (**CO**gnitive **R**eal-**T**ime **EX**ecution) is a production-grade AI engineering framework. Think of it as a **development nervous system** — the way your brain coordinates sensory input, decision-making, and motor execution in milliseconds, CORTEX coordinates code analysis, governance enforcement, and workflow execution for every development request.

**What makes it different from other dev tools:**

- Traditional tools answer questions. CORTEX **orchestrates entire workflows** — from intent classification through TDD enforcement to code delivery.
- One canonical Python package (`cortex`), a comprehensive orchestrator ecosystem across four tiers (core, domain, support, git), a growing library of MCP tools, and an extensive set of CORE governance rules.
- TDD is not optional. CORE-008 mandates RED → GREEN → REFACTOR on every IMPLEMENT/FIX request. No exceptions.
- Everything is Git-backed. No PostgreSQL, no MongoDB — just YAML files in `cortex-registry/` versioned alongside your code.

---

## System Capabilities

| Metric | Value | Status |
|--------|-------|--------|
| **Package** | 1 canonical (`cortex`) | ✅ Consolidated to single namespace |
| **Orchestrators** | Comprehensive ecosystem across 4 tiers (core, domain, support, git) | ✅ IOrchestrator protocol enforced |
| **MCP Tools** | Growing library in `cortex/mcp/tools/` | ✅ Pylance-style stdio server |
| **Top-level Dirs** | Streamlined canonical layout under `cortex/` | ✅ Consolidated and clean |
| **Governance Rules** | Extensive CORE rules (+ AC rules) | ✅ Enforced at pre-commit + CI + runtime |
| **Test Suite** | Thousands of tests across unit, golden, and phase tiers | ✅ Parallel xdist batch runner |
| **Parallel Testing** | pytest-xdist (`-n auto --dist loadscope`) | ✅ CortexXdistPlugin batch runner |
| **Enterprise Patterns** | Multiple patterns in registry | ✅ mediator, strategy, observer, factory, etc. |
| **Sweep Completeness** | CORE-064 enforced via SweepCatalogueOrchestrator | ✅ No partial sweeps across sessions |
| **URS** | Unified Reinforcement Signal — closed-loop learning | ✅ Multiple wired surfaces, `cortex_learning` MCP tool |

---

### Architecture at a Glance

```
  ┌───────────────────────────────────────────────────────────────┐
  │                     CORTEX PLATFORM                           │
  │             1 Package · Multi-Tier Orchestration · MCP Tools  │
  │                                                               │
  │  ┌─────────────┐   ┌──────────────────┐   ┌───────────────┐  │
  │  │ MCP Gateway │──▶│  Orchestration   │──▶│ Intelligence  │  │
  │  │ Tools       │   │  Wired           │   │ LENS + Brain  │  │
  │  └─────────────┘   │  4 canonical tiers│   │ + URS         │  │
  │         │          └──────────────────┘   └───────────────┘  │
  │         ▼                   │                     │           │
  │  ┌─────────────┐   ┌──────────────────┐   ┌───────────────┐  │
  │  │ Governance  │   │  Testing         │   │ Registry      │  │
  │  │ CORE rules  │   │  Comprehensive   │   │ Git-backed    │  │
  │  │ CORE-064    │   │  xdist batch     │   │ YAML SSOT     │  │
  │  └─────────────┘   └──────────────────┘   └───────────────┘  │
  └───────────────────────────────────────────────────────────────┘
```

---

### Practical Daily Experience

**Business Leader:** "I see a platform where governance rules are automatically enforced on every commit across all teams. Test quality is scored and anything below the threshold gets flagged. Zero governance violations reach production — the system blocks them at the gate."

**Product Owner:** "When I request a feature, I know TDD is enforced — not by policy, but by the system. The TDDOrchestrator writes the failing test first, then implements. I can pull sprint work items from ADO directly into developer context via MCP tools. I never chase test coverage; it's automatic."

**Developer:** "I type a request in VS Code. CORTEX enriches it, classifies intent, runs parallel LENS analyzers, enforces governance, and executes. Every operation emits a reinforcement signal so the system learns what works. Everything imports from one package: `from cortex.orchestrators.core import TDDOrchestrator`. No more hunting through multiple packages."

---

*CORTEX · Cognitive Real-Time Execution · Source of truth: `cortex-registry/cortex-master.yaml`*

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
| Token optimization | `05-infrastructure/08-token-optimization.md` |
| Architecture diagrams | `07-diagrams/01-overview.md` |
| Golden tests & quality | `flat-files/14-golden-tests.md` |
| Sharpen The Saw (STS) | `flat-files/15-sharpen-the-saw.md` |
| SDLC workflow engine | `flat-files/16-sdlc-workflow-engine.md` |
| Workflow template library | `flat-files/17-workflow-template-library.md` |
| RGR quality cycle | `flat-files/18-rgr-quality-cycle.md` |
| Enterprise patterns & knowledge | `flat-files/19-enterprise-patterns-knowledge.md` |
| Security-first development | `flat-files/20-security-first.md` |
| Glossary | `glossary.md` |

---

*CORTEX · Cognitive Real-Time Execution · Comprehensive orchestration, governance, and intelligence · Source of truth: `cortex-registry/cortex-master.yaml`*

