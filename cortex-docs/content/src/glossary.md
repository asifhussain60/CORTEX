# Glossary

---
title: CORTEX Glossary — Terminology Reference
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/ (live codebase)
order: 99
---

> Alphabetical reference of all CORTEX terms. All module paths verified against the live codebase.

---

## A

**Action Tier** — Third intelligence tier. Executes plans produced by the Reasoning tier. Generates code, tests, and transformations. Location: `cortex/intelligence/action/`.

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

**CORE Rules** — Governance rules identified by `CORE-nnn` IDs. 35 defined in `cortex-registry/core/governance/skull-rules.yaml`, 17 actively enforced.

**CORTEX** — **CO**gnitive **R**eal-**T**ime **EX**ecution. An AI engineering framework with 52 orchestrators, 23 MCP tools, and 17 governance rules.

**cortex_process_request** — Mandatory MCP entry point. Routes ALL user requests through MasterOrchestrator 4-stage pipeline. Module: `cortex/mcp/tools/core.py`.

## D

**Definition of Ready (DoR)** — Checklist presented in MasterOrchestrator Stage 1. Ensures scope, acceptance criteria, and dependencies are clear before execution.

**Domain Brain** — Domain-specific knowledge module that provides context for business logic decisions. Location: `cortex/intelligence/domain_brain/`.

## E

**EnforcementOrchestrator** — Orchestrator that validates code against CORE governance rules. Coordinates 8 enforcement agents. Location: `cortex/orchestrators/core/`.

**Evidence Bundle** — Collection of audit records, test results, and governance checks packaged as compliance proof. Module: `cortex/infrastructure/evidence_bundle.py`.

**ExtendedGovernanceAgent** — Enforcement agent covering CORE-058 through CORE-063 rules.

## G

**Golden Tests** — 486 tests that must ALWAYS pass. Run serially (`-p no:xdist`) for deterministic results. Location: `tests/golden/`.

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

**MCP (Model Context Protocol)** — JSON-RPC 2.0 communication standard connecting IDEs to CORTEX. 23 canonical tools exposed via stdio transport.

## O

**OrchestratorBase** — Abstract base class for all 52 orchestrators. Provides lifecycle management, audit trail, and governance hooks. Module: `cortex/core/orchestrator_base.py`.

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

**SecurityOrchestrator** — Orchestrator handling security analysis, vulnerability detection, and security gate enforcement. Location: `cortex/orchestrators/core/`.

**skull-rules.yaml** — YAML file containing all 35 CORE governance rule definitions. Location: `cortex-registry/core/governance/skull-rules.yaml`.

**stdio Transport** — Standard input/output process communication. IDE writes JSON-RPC to stdin, CORTEX responds on stdout. No network ports required.

**Synthesis** — LENS synthesis phase that merges results from all 8 analyzers into a unified intelligence report.

## T

**TDD (Test-Driven Development)** — Mandatory development methodology (CORE-008). Cycle: RED (write failing test) → GREEN (implement minimum) → REFACTOR (clean up).

**TDDOrchestrator** — Orchestrator enforcing TDD cycle for IMPLEMENT, FIX, and TEST intents. Location: `cortex/orchestrators/core/tdd_orchestrator.py`.

**TestQualityGate** — Scoring system (0–9) evaluating test value. Formula: Impact + Likelihood + Detection + Efficiency - Maintenance.

**ToolResult** — Standard response object from MCP tool execution. Contains content (text), metadata, and audit reference.

## W

**WAL (Write-Ahead Logging)** — SQLite journaling mode used by CortexAuditDB. Enables concurrent reads during single-writer transactions.

**WorkflowEngine** — Executes workflow templates from `cortex-registry/workflows/`. Supports lifecycle and production template categories.

**Workflow Templates** — YAML-defined execution plans in `cortex-registry/workflows/templates/`. Categories: `lifecycle/` (development flow) and `production/` (deployment operations).

---

*Verified against live CORTEX codebase · 20 February 2026*
