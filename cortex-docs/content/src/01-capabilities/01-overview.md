# CORTEX Capabilities Overview

---
title: CORTEX Capabilities — Complete Platform Inventory
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-21
source_of_truth: cortex/ + cortex-registry/ + cortex-registry/planning/cortex-refactor-master.yaml
format: diátaxis-explanation
order: 1
---

> **Notice:** All capabilities listed here are verified against the live codebase as of 21 February 2026. Counts, module paths, and orchestrator names are validated against running code. The 12-phase Cohesive Brain Refactor consolidated 3 packages → 1, 120 orchestrators → 52, and 59 directories → 16.

---

## Six Capability Domains

CORTEX organizes capabilities into six cognitive domains — each analogous to a specialized region of the brain working in concert:

| # | Domain | Brain Analogy | Key Metric |
|---|--------|--------------|------------|
| 1 | **🏗️ Core Platform** | Brainstem — keeps everything alive | 24 MCP tools, 16 canonical dirs |
| 2 | **🤖 Intelligence (LENS)** | Sensory cortex — processes raw input | 8 parallel analyzers |
| 3 | **🧠 Brain Tiers** | Prefrontal cortex — decides and plans | Perception → Reasoning → Action |
| 4 | **🎯 Decisioning** | Thalamus — routes signals to right region | 52 orchestrators, 10 domains |
| 5 | **🛡️ Governance** | Immune system — blocks threats automatically | 17 CORE rules, 7 agents |
| 6 | **🔌 Extensibility** | Neuroplasticity — adapts to new capabilities | Hot-reload, zero core changes |

---

## Capability Matrix

| Capability | Domain | Implementation | Tests |
|-----------|--------|---------------|-------|
| MCP Gateway (24 tools) | Core | `cortex/mcp/tools/` | ✅ |
| Orchestrator Dispatch (52 classes) | Core | `cortex/orchestrators/` (10 domains) | ✅ |
| OrchestratorBase Lifecycle | Core | `cortex/core/orchestrator_base.py` | ✅ |
| FileFactory | Core | `cortex/core/file_factory.py` | ✅ |
| WorkflowEngine | Core | `cortex/core/workflow_engine.py` | ✅ |
| CortexAuditDB (SQLite WAL) | Core | `cortex/infrastructure/audit_db.py` | ✅ |
| LENS 8-Analyzer Pipeline | Intelligence | `cortex/lens/analyzers/` | ✅ |
| LENS Caching | Intelligence | `cortex/lens/cache/` | ✅ |
| Pattern Registry (9 patterns) | Brain | `cortex/intelligence/perception/` | ✅ |
| Strategy Selector | Brain | `cortex/intelligence/reasoning/` | ✅ |
| Execution Planner | Brain | `cortex/intelligence/action/` | ✅ |
| Domain Brain | Brain | `cortex/intelligence/domain_brain/` | ✅ |
| IntentRouter (12 intents) | Decisioning | `cortex/orchestrators/core/intent_router.py` | ✅ |
| TDDOrchestrator (RED→GREEN→REFACTOR) | Decisioning | `cortex/orchestrators/core/tdd_orchestrator.py` | ✅ |
| RefactoringOrchestrator | Decisioning | `cortex/orchestrators/core/refactoring_orchestrator.py` | ✅ |
| EnforcementOrchestrator (7+1 agents) | Governance | `cortex/orchestrators/core/enforcement_orchestrator.py` | ✅ |
| TestQualityGate (0–9 scoring) | Governance | `cortex/testing/quality_gate.py` | ✅ |
| PreCommitEnforcement | Governance | `cortex/orchestrators/core/pre_commit_enforcement_orchestrator.py` | ✅ |
| Parallel Test Framework | Testing | `cortex/testing/framework/` | ✅ |
| InfrastructureDetector | Extensibility | `cortex/intelligence/infrastructure/` | ✅ |
| Workflow Templates | Extensibility | `cortex-registry/workflows/templates/` | ✅ |
| Enterprise Patterns (9) | Extensibility | `cortex-registry/patterns/` | ✅ |
| **WorkItemProvider (ADO/Jira/custom)** | **Extensibility** | `cortex/repositories/` + `cortex/mcp/tools/work_item_tool.py` | ✅ |

---

## 1. 🏗️ Core Platform

The **brainstem** of CORTEX — it keeps everything alive and coordinated.

### MCP Gateway (23 Tools)

CORTEX exposes 24 canonical MCP tools via Pylance-style stdio server. The server auto-starts when VS Code opens the workspace.

**Business Leader:** "24 tools covering analysis, governance, onboarding, debugging, health checks, and workflow management — all accessible from the IDE without switching tools."

**Product Owner:** "Each tool maps to a user capability. `cortex_onboard_repository` brings in a new codebase. `cortex_validate_compliance` checks rules. `cortex_score_tests` evaluates test quality."

**Developer:** "I call `cortex_tools_catalog` to discover all tools. Each tool has typed parameters, docstrings, and returns structured results. MCP handles the JSON-RPC plumbing."

### OrchestratorBase Lifecycle

Every orchestrator follows a 5-step lifecycle: **setup → govern → execute → validate → teardown**. This is enforced by `cortex/core/orchestrator_base.py`. Governance audit is wired into `teardown()`.

### FileFactory & WorkflowEngine

- **FileFactory** (`cortex/core/file_factory.py`) — canonical file creation with CORE-028 naming enforcement
- **WorkflowEngine** (`cortex/core/workflow_engine.py`) — reads workflow YAML templates and executes phase sequences

---

## 2. 🤖 Intelligence (LENS)

The **sensory cortex** — processes raw code into structured perception.

LENS (**L**anguage → **E**xamination → **N**avigation → **S**ynthesis) runs 8 specialized analyzers in parallel:

| Analyzer | Perception Type | Output |
|----------|----------------|--------|
| AST | Code structure | Classes, functions, imports, dependencies |
| Git History | Change patterns | Hot spots, author patterns, recent modifications |
| Comment | Documentation | Coverage gaps, TODO density, documentation quality |
| Import | Dependencies | Circular imports, stale imports, dependency graph |
| Security | Vulnerabilities | SQL injection, XSS, credentials, CVE patterns |
| Pattern | Architecture | Framework detection, architecture style matching |
| Metrics | Complexity | Cyclomatic complexity, coupling, LOC |
| Domain | Business context | Industry detection (finance, healthcare, etc.) |

**Business Leader:** "LENS gives every repo a 'health scan' in under a second — like an MRI for your codebase."

**Product Owner:** "The 8-analyzer report tells me exactly where quality gaps are. I don't need manual code reviews to find hot spots — LENS identifies them automatically."

**Developer:** "LENS runs in 300–800ms and gives me AST structure, security findings, complexity metrics, and dependency graphs — all in one pass. No separate tools needed."

---

## 3. 🧠 Brain Tiers

The **prefrontal cortex** — makes decisions and builds plans.

See `00-getting-started/04-brain-tier-architecture.md` for full detail. Summary:

| Tier | Location | Purpose |
|------|----------|---------|
| Perception | `cortex/intelligence/perception/` | Pattern matching against 9 enterprise patterns |
| Reasoning | `cortex/intelligence/reasoning/` | Strategy selection ranked by success rate |
| Action | `cortex/intelligence/action/` | Execution plan with TDD gates and rollback |

The brain learns: pattern confidence and strategy success rates update after every execution.

---

## 4. 🎯 Decisioning

The **thalamus** — routes every signal to the right processing region.

### IntentRouter

Classifies requests into 12+ intent types and routes to the correct orchestrator across 10 domains. Uses LENS intelligence for classification (20–40ms).

### TDD Workflow (CORE-008)

Every IMPLEMENT and FIX operation follows mandatory RED → GREEN → REFACTOR:
1. Write a failing test
2. Write minimum code to pass
3. Refactor while keeping tests green

This is not optional. CORE-008 is enforced at the architecture level.

### 52 Orchestrators Across 10 Domains

| Domain | Count | Key Orchestrators |
|--------|-------|------------------|
| core | 52 files | Master, IntentRouter, TDD, Enforcement, Planning, Refactoring, Security |
| domain | 30 files | Business, Ecommerce, Financial, Healthcare |
| health | 30 files | Health, Vacuum, Diagnostics |
| support | 38 files | Onboarding, Setup, Discovery, Recommendations |
| intelligence | 14 files | Intelligence, UnifiedAnalysis |
| validation | 11 files | HolisticValidation, Review, QualityAssurance |
| workflow | 13 files | Workflow, PhaseCompletion |
| git | 4 files | Git, GitPublish |
| strategies | 1 file | Strategy selection |
| synthesis | 1 file | Cross-domain synthesis |

---

## 5. 🛡️ Governance

The **immune system** — blocks threats automatically without conscious effort.

### 17 Active CORE Rules

Enforced at pre-commit, CI, and runtime. Full list in `cortex-registry/core/governance/skull-rules.yaml`.

### 7 Enforcement Agents + ExtendedGovernanceAgent

| Agent | Focus |
|-------|-------|
| TDD | CORE-008 enforcement |
| Security | Vulnerability detection |
| Compliance | CORE rule adherence |
| Naming | CORE-028 snake_case |
| Incremental | CORE-001 bounded execution |
| Architecture | Structural integrity |
| Markdown | CORE-002 no report files |
| Extended | CORE-058 through CORE-063 (SQLite WAL, MCP footprint, plan-first, challenge-first) |

### TestQualityGate

Scores every test 0–9. Formula: `Impact(0-3) + Likelihood(0-2) + Detection(0-2) + Efficiency(0-2) − Maintenance(0-2)`. Gate: ≥7 KEEP, 4–6 REVIEW, <4 DELETE.

---

## 6. 🔌 Extensibility

**Neuroplasticity** — the brain's ability to form new connections.

- **Custom MCP Tools:** Add tools to `cortex/mcp/tools/` — discovered automatically
- **Domain Orchestrators:** Add business-specific orchestrators to `cortex/orchestrators/domain/`
- **Workflow Templates:** Define new workflows in `cortex-registry/workflows/templates/`
- **Enterprise Patterns:** Register new patterns in `cortex-registry/patterns/`
- **Infrastructure Catalog:** `cortex-registry/company/` stores platform, API, and application definitions
- **Knowledge Base:** Add best-practice YAMLs to `cortex-registry/knowledge-base/`

All extensibility is hot-reload — no core changes required.

---

*All paths and counts verified against live codebase · 20 February 2026*
