# Glossary

---
title: CORTEX Glossary — Terminology Reference
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-21
source_of_truth: cortex/ (live codebase)
order: 99
---

> Alphabetical reference of all CORTEX terms. All module paths verified against the live codebase.

---

## A

**Action Tier** — Third intelligence tier. Executes plans produced by the Reasoning tier. Generates code, tests, and transformations. Location: `cortex/intelligence/action/`.

**ADO (Azure DevOps)** — The default work item ticketing system integrated with CORTEX. Selected by setting `WORK_ITEM_SOURCE=ado`. Requires `ADO_ORG_URL`, `ADO_PAT`, and `ADO_PROJECT` environment variables. Adapter: `cortex/repositories/ado/ado_provider.py`.

**ADOWorkItemProvider** — Concrete implementation of the `WorkItemProvider` Protocol for Azure DevOps. Exposes `fetch_user_stories`, `fetch_by_id`, and `health_check` methods backed by ADO REST API calls. Companies fill in the stub method bodies with their HTTP client and field mapping logic. Location: `cortex/repositories/ado/ado_provider.py`.

**Audit Database (CortexAuditDB)** — SQLite WAL database storing all operation records with hash-chain integrity. Location: `.cortex-runtime/`. Module: `cortex/infrastructure/audit_db.py`.

**Audit Hash Chain** — Cryptographic chain linking each audit entry to the previous one, creating a tamper-evident log. Module: `cortex/infrastructure/audit_hash_chain.py`.

## B

**Brain Tiers** — Three-layer intelligence architecture: Perception → Reasoning → Action. Located at `cortex/intelligence/{perception,reasoning,action}/`.

**Bulkhead** — Resilience pattern that partitions resources to prevent one failing component from consuming all capacity. Module: `cortex/infrastructure/bulkhead_manager.py`.

## C

**Canary Deployment** — Deployment strategy that routes a small percentage of traffic to new versions before full rollout. Config: `deployment/canary_config.yaml`.

**Circuit Breaker** — Resilience pattern that stops calls to failing services. States: Closed → Open → Half-Open. Module: `cortex/infrastructure/circuit_breaker.py`.

**Cohesive Brain Refactor** — 12-phase architectural transformation that unified `cortex_intelligence/`, `cortex_lens/`, and `cortex.brain` into the single `cortex` package. Completed February 2026.

**Confidence Score** — Numerical value (0.0–1.0) produced by IntentRouter indicating certainty of intent classification. Higher scores route to primary orchestrators.

**ConsolidatedTool** — Base class for all MCP tools. Provides consistent naming, parameter validation, execution, and audit trail. Module: `cortex/mcp/mcp_tool_base.py`.

**CORE-055** — Golden Test Tier Contract. 696 golden tests in `tests/golden/` must always pass. Zero regression allowed. Added 21 February 2026.

**CORE-064** — Sweep Completeness Contract. Every FIX/REFACTOR/AUDIT sweep must exhaust its full issue catalogue before closing. Enforced by `SweepCatalogueOrchestrator`. Added 21 February 2026.

**CORE Rules** — Governance rules identified by `CORE-nnn` IDs. 35 defined in `cortex-registry/core/tier0-skull/skull-rules.yaml` (33 CORE-* + 2 AC-PERMANENT-FIX), 22 actively enforced.

**cortex_process_request** — Mandatory MCP entry point. Routes ALL user requests through MasterOrchestrator 4-stage pipeline. Module: `cortex/mcp/tools/core.py`.

**cortex_fetch_work_items** — MCP tool (Phase 15) for provider-agnostic work item access. Fetches user stories, bugs, and tasks from the configured ticketing system (ADO, Jira, custom). Provider is selected via `WORK_ITEM_SOURCE` env var. Module: `cortex/mcp/tools/work_item_tool.py`.

## D

**Definition of Ready (DoR)** — Checklist presented in MasterOrchestrator Stage 1. Ensures scope, acceptance criteria, and dependencies are clear before execution.

**Domain Brain** — Domain-specific knowledge module that provides context for business logic decisions. Location: `cortex/intelligence/domain_brain/`.

## E

**EnforcementOrchestrator** — Orchestrator that validates code against CORE governance rules. Coordinates 10 enforcement agents. Location: `cortex/orchestrators/core/`.

**Evidence Bundle** — Collection of audit records, test results, and governance checks packaged as compliance proof. Module: `cortex/infrastructure/evidence_bundle.py`.

**ExtendedGovernanceAgent** — Enforcement agent covering CORE-058 through CORE-063 rules.

## G

**Golden Tests** — 696 tests that must ALWAYS pass (CORE-055 Golden Test Tier Contract). Run with `pytest-xdist` parallel execution. Location: `tests/golden/`.

**Governance Agents** — 8 specialized agents that enforce specific CORE rule categories: TestNaming, FileNaming, ImportValidation, TypeHint, Docstring, DuplicateDetection, SecurityScan, ExtendedGovernance.

**Graceful Degradation** — Resilience pattern returning partial results when non-critical services fail. Module: `cortex/infrastructure/graceful_degradation.py`.

## H

**Hash Chain** — See Audit Hash Chain.

**HEXA-MODE** — Mode definitions loaded from YAML registry. Defines operational modes for different execution contexts.

## I

**IntentRouter** — Orchestrator that classifies requests into 12 intent types (IMPLEMENT, FIX, REFACTOR, etc.) and routes to appropriate domain orchestrators. Location: `cortex/orchestrators/core/intent_router.py`.

## J

**JSON-RPC 2.0** — Protocol used for MCP communication between IDE clients and CORTEX server. Standard request/response format over stdio transport.

## K

**Knowledge Base** — Domain knowledge stored in `cortex-registry/knowledge-base/` and managed by `cortex/knowledge/`.

## L

**LENS** — **L**anguage → **E**xamination → **N**avigation → **S**ynthesis. Code intelligence system with 8 parallel analyzers producing unified analysis in 300–800ms. Location: `cortex/lens/`.

**LENS Analyzers** — 8 parallel analyzers: AST, Git History, Comment, Import, Security, Pattern, Metrics, Domain.

## M

**MasterOrchestrator** — Central entry point orchestrator. Runs 4-stage pipeline: Interaction → Intent → Intelligence → Execution. Location: `cortex/orchestrators/core/master_orchestrator.py`.

**MCP (Model Context Protocol)** — JSON-RPC 2.0 communication standard connecting IDEs to CORTEX. 26 active tools exposed via stdio transport.

## O

**OrchestratorBase** — Legacy abstract base class used by 2 orchestrators only (`ServiceDecompositionOrchestrator`, `BusinessKnowledgeIngestionOrchestrator`). The primary base for all 17 wired orchestrators is `OrchestratorProtocolMixin` (Phase 58) + `IOrchestrator` protocol. Module: `cortex/core/orchestrator_base.py`.

**OrchestratorEventBus** — Decoupled communication channel for inter-orchestrator messaging. Module: `cortex/infrastructure/orchestrator_event_bus.py`.

## P

**Perception Tier** — First intelligence tier. Observes, parses, and classifies raw input. Location: `cortex/intelligence/perception/`.

**Phase Tests** — 177 tests that validate specific phase milestone completion. Location: `tests/`.

**Pre-Commit Validator** — Validates code against governance rules before commit. Module: `cortex/infrastructure/pre_commit_validator.py`.

**Pylance-style MCP** — CORTEX's MCP server auto-starts when VS Code opens the workspace — same pattern as the Pylance language server. No manual startup required.

**pytest-xdist** — pytest plugin for parallel test execution. Used with `-n auto --dist loadscope` for unit tests and `-n 4 --dist loadfile` for integration tests.

## R

**Reasoning Tier** — Second intelligence tier. Analyzes perceptions, assesses risk, and produces execution plans. Location: `cortex/intelligence/reasoning/`.

**Refactor Master** — Strategic planning document defining all 12 phases of the Cohesive Brain Refactor. File: `cortex-registry/planning/cortex-refactor-master.yaml`.

**RequestRephraseOrchestrator** — Orchestrator that clarifies ambiguous or incomplete requests before routing to execution. Location: `cortex/orchestrators/core/`.

## S

**ScaffoldWriter** — Emits `ScaffoldFile` objects produced by WorkflowEngine steps to disk (`mkdir -p`). Allows downstream pipeline steps whose `depends_on` gate checks for files to proceed without halting mid-run. Added today (BadMonolith Gap G2). Module: `cortex/core/scaffold_writer.py`.

**SecurityOrchestrator** — Orchestrator handling security analysis, vulnerability detection, and security gate enforcement. Location: `cortex/orchestrators/core/`.

**skull-rules.yaml** — YAML file containing all 35 CORE governance rule definitions (33 CORE-* + 2 AC-PERMANENT-FIX). Location: `cortex-registry/core/tier0-skull/skull-rules.yaml`.

**stdio Transport** — Standard input/output process communication. IDE writes JSON-RPC to stdin, CORTEX responds on stdout. No network ports required.

**SweepCatalogueOrchestrator** — CORE-064 enforcement engine. Tracks open/resolved items in every FIX/REFACTOR/AUDIT sweep using SQLite WAL (`cortex-runtime/sweeps/{sweep_id}.db`). No partial sweep can close without `assert_exhausted()` or `approve_wont_fix()`. MCP tool: `cortex_sweep_status`. Location: `cortex/orchestrators/support/sweep_catalogue_orchestrator.py`.

**Sweep Completeness Contract** — See CORE-064. Every sweep must exhaust its full catalogue before closing.

**Synthesis** — LENS synthesis phase that merges results from all 8 analyzers into a unified intelligence report.

## T

**TDD (Test-Driven Development)** — Mandatory development methodology (CORE-008). Cycle: RED (write failing test) → GREEN (implement minimum) → REFACTOR (clean up).

**TDDOrchestrator** — Orchestrator enforcing TDD cycle for IMPLEMENT, FIX, and TEST intents. Location: `cortex/orchestrators/core/tdd_orchestrator.py`.

**TestQualityGate** — Scoring system (0–9) evaluating test value. Formula: Impact + Likelihood + Detection + Efficiency - Maintenance.

**ToolResult** — Standard response object from MCP tool execution. Contains content (text), metadata, and audit reference.

## W

**WAL (Write-Ahead Logging)** — SQLite journaling mode used by CortexAuditDB. Enables concurrent reads during single-writer transactions.

**WorkflowEngine** — Executes workflow templates from `cortex-registry/workflows/`. Exposes `load()` to parse YAML templates and `execute_step()` (SDO-compatible API) to run individual steps. Wired to `ScaffoldWriter` so scaffold artefacts are persisted to disk. Module: `cortex/core/workflow_engine.py`.

**WorkItem** — Canonical dataclass representing a work item across all ticketing systems. Fields: `id`, `title`, `description`, `state`, `type`, `tags`, `url`, `raw`. The `raw` field carries the full unmodified API response so company-specific fields (Area Path, Sprint, Custom.* ADO fields, Jira components) survive intact. Module: `cortex/repositories/work_item_provider.py`.

**WorkItemProvider** — `@runtime_checkable` Protocol defining the integration contract for all ticketing systems. Three required methods: `fetch_user_stories(project, **kwargs)`, `fetch_by_id(item_id)`, `health_check()`. Companies implement once; CORTEX routes through the same MCP surface regardless of backend. Module: `cortex/repositories/work_item_provider.py`.

**WORK_ITEM_SOURCE** — Environment variable that selects the active `WorkItemProvider`. Default: `"ado"` (Azure DevOps). Factory: `cortex/repositories/provider_factory.py`.

**Workflow Templates** — YAML-defined execution plans in `cortex-registry/workflows/templates/`. Categories: `lifecycle/` (development flow) and `production/` (deployment operations).

---

*Verified against live CORTEX codebase · 21 February 2026*
