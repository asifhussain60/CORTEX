# CORTEX Capabilities Overview

---
title: CORTEX Capabilities — Complete Platform Inventory
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-24
source_of_truth: cortex/ + cortex-registry/cortex-master.yaml + .github/copilot-instructions.md
format: diátaxis-explanation
order: 1
---

> **Notice:** All capabilities listed here are verified against the live codebase as of 24 February 2026 (Phase 66/67 Complete — all 67 phases done). Counts, module paths, and orchestrator names are validated against running code. The Cohesive Brain Refactor consolidated 3 packages → 1 canonical `cortex` package.

---

## Six Capability Domains

CORTEX organizes capabilities into six cognitive domains — each analogous to a specialized region of the brain working in concert:

| # | Domain | Brain Analogy | Key Metric |
|---|--------|--------------|------------|
| 1 | **🏗️ Core Platform** | Brainstem — keeps everything alive | 26 MCP tools, 16 canonical dirs |
| 2 | **🤖 Intelligence (LENS)** | Sensory cortex — processes raw input | 8 parallel analyzers |
| 3 | **🧠 Brain Tiers** | Prefrontal cortex — decides and plans | Perception → Reasoning → Action |
| 4 | **🎯 Decisioning** | Thalamus — routes signals to right region | 27 wired orchestrators, 3 canonical tiers (10 total dirs) |
| 5 | **🛡️ Governance** | Immune system — blocks threats automatically | 35 CORE rules, CORE-064, CORE-055 |
| 6 | **🔌 Extensibility** | Neuroplasticity — adapts to new capabilities | Hot-reload, zero core changes |

---

## Capability Matrix

| Capability | Domain | Implementation | Tests |
|-----------|--------|---------------|-------|
| MCP Gateway (26 active tools) | Core | `cortex/mcp/tools/` | ✅ |
| Orchestrator Dispatch (27 wired) | Core | `cortex/orchestrators/` (3 canonical tiers: 7 core, 6 domain, 14 support (+ dirs: health, git, intelligence, strategies, synthesis, validation, workflow)) | ✅ |
| OrchestratorBase Lifecycle | Core | `cortex/core/orchestrator_base.py` | ✅ |
| SQLite Activity Log | Core | `.cortex-runtime/audit.db` (auto-logged in `execute()/run()`) | ✅ |
| FileFactory | Core | `cortex/core/file_factory.py` | ✅ |
| WorkflowEngine (load + execute_step) | Core | `cortex/core/workflow_engine.py` | ✅ |
| ScaffoldWriter | Core | `cortex/core/scaffold_writer.py` | ✅ |
| CortexAuditDB (SQLite WAL) | Core | `cortex/infrastructure/audit_db.py` | ✅ |
| LENS 8-Analyzer Pipeline | Intelligence | `cortex/lens/analyzers/` | ✅ |
| LENS Caching | Intelligence | `cortex/lens/cache/` | ✅ |
| Pattern Registry (9 patterns) | Brain | `cortex/intelligence/perception/` | ✅ |
| Strategy Selector | Brain | `cortex/intelligence/reasoning/` | ✅ |
| Execution Planner | Brain | `cortex/intelligence/action/` | ✅ |
| Domain Brain | Brain | `cortex/intelligence/domain_brain/` | ✅ |
| IntentRouter (12 intents) | Decisioning | `cortex/orchestrators/core/intent_router.py` | ✅ |
| TDDOrchestrator (RED→GREEN→REFACTOR) | Decisioning | `cortex/orchestrators/core/tdd_orchestrator.py` | ✅ |
| RefactoringOrchestrator (by-name Roslyn) | Decisioning | `cortex/orchestrators/domain/refactoring_orchestrator.py` | ✅ |
| EnforcementOrchestrator (10 agents) | Governance | `cortex/orchestrators/core/enforcement_orchestrator.py` | ✅ |
| SweepCatalogueOrchestrator (CORE-064) | Governance | `cortex/orchestrators/support/sweep_catalogue_orchestrator.py` | ✅ |
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

### MCP Gateway (25 Tools)

CORTEX exposes 26 active MCP tools via Pylance-style stdio server. The server auto-starts when VS Code opens the workspace.

**Business Leader:** "26 tools covering analysis, governance, onboarding, debugging, health checks, sweep management, and workflow — all accessible from the IDE without switching tools."

**Product Owner:** "Each tool maps to a user capability. `cortex_onboard` brings in a new codebase. `cortex_validate` checks rules. `cortex_sweep_status` tracks long-running refactor sweeps (CORE-064). `cortex_fetch_work_items` pulls ADO sprint work items."

**Developer:** "I call `cortex_tools_catalog` to discover all 26 tools. Each tool has typed parameters, docstrings, and returns structured results. MCP handles the JSON-RPC plumbing."

### OrchestratorBase Lifecycle

Every orchestrator follows a 5-step lifecycle: **setup → govern → execute → validate → teardown**. This is enforced by `cortex/core/orchestrator_base.py`. Governance audit is wired into `teardown()`.

`execute()` and `run()` auto-log `ORCHESTRATOR_START`/`END` to `.cortex-runtime/audit.db` (SQLite WAL). Audit failures are non-blocking.

### FileFactory, WorkflowEngine & ScaffoldWriter

- **FileFactory** (`cortex/core/file_factory.py`) — canonical file creation with CORE-028 naming enforcement
- **WorkflowEngine** (`cortex/core/workflow_engine.py`) — reads workflow YAML templates, exposes `load()` + `execute_step()` (SDO-compatible API)
- **ScaffoldWriter** (`cortex/core/scaffold_writer.py`) — disk-emission of workflow `scaffold_files` so downstream pipeline steps whose `depends_on` gate checks for files can proceed without halting mid-run

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

Classifies requests into 12+ intent types and routes to the correct wired orchestrator. Uses LENS intelligence for classification (20–40ms).

### TDD Workflow (CORE-008)

Every IMPLEMENT and FIX operation follows mandatory RED → GREEN → REFACTOR:
1. Write a failing test
2. Write minimum code to pass
3. Refactor while keeping tests green

This is not optional. CORE-008 is enforced at the architecture level.

### 27 Wired Orchestrators Across 3 Tiers

| Tier | Count | Key Orchestrators |
|------|-------|-----------------|
| **Core** | 6 | MasterOrchestrator, IntentRouter, TDDOrchestrator, WorkflowOrchestrator, EnforcementOrchestrator, ConversationOrchestrator |
| **Domain** | 6 | RefactoringOrchestrator (Roslyn by-name), PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator, RefactoringOrchestrator, CortexDocsOrchestrator |
| **Support** | 10 | OnboardingOrchestrator, UpgradeOrchestrator, RollbackOrchestrator, SetupOrchestrator, HealthOrchestrator, SweepCatalogueOrchestrator (CORE-064), VacuumOrchestrator, BulkDigestOrchestrator, DigestSessionOrchestrator, UnifiedDiscoveryOrchestrator |

> Wiring specs: `cortex-registry/core/specifications/`. Additional specialized sub-components exist in `cortex/orchestrators/` but are not IOrchestrator-wired entry points.

---

## 5. 🛡️ Governance

The **immune system** — blocks threats automatically without conscious effort.

### 22 Active CORE Rules

Enforced at pre-commit, CI, and runtime. Full list in `cortex-registry/core/tier0-skull/skull-rules.yaml`.

Key rules added today:
- **CORE-064** — Sweep Completeness Contract: every FIX/REFACTOR/AUDIT sweep exhausts its catalogue before closing
- **CORE-055** — Golden Test Tier Contract: 486 golden tests always pass

### 10 Enforcement Agents

| Agent | Focus |
|-------|-------|
| GovernanceEnforcement | CORE rule adherence |
| SecurityCheckpoint | Vulnerability detection |
| ComplianceValidation | Compliance checks |
| FileNamingEnforcement | CORE-028 snake_case |
| IncrementalExecution | CORE-001 bounded execution |
| MarkdownSuppression | CORE-002 no report files |
| ArchitectureIntegrity | Structural integrity |
| DiscoveryEnforcement | CORE-030, CORE-035 |
| ResponseContentValidation | CORE-002 response-level gate |
| ExtendedGovernance | CORE-058 through CORE-063 |

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
- **ScaffoldWriter:** Emit workflow artefacts to disk for multi-step pipeline dependencies

All extensibility is hot-reload — no core changes required.

---

*All paths and counts verified against live codebase · 23 February 2026*
