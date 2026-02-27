# Glossary

---
title: CORTEX Glossary — Terminology Reference
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-27
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

**CORE-055** — Golden Test Tier Contract. 486 golden tests in `tests/golden/` must always pass. Zero regression allowed. Added 21 February 2026.

**CORE-064** — Sweep Completeness Contract. Every FIX/REFACTOR/AUDIT sweep must exhaust its full issue catalogue before closing. Enforced by `SweepCatalogueOrchestrator`. Added 21 February 2026.

**CORE Rules** — Governance rules identified by `CORE-nnn` IDs. 38 CORE rules active in `cortex-registry/core/tier0-skull/skull-rules.yaml` (+ 2 AC rules), all enforced at pre-commit + CI + runtime.

**cortex_learning** — MCP tool (Phase 83) for Unified Reinforcement Signal management. Six operations: `emit` (record signal), `history` (query signals), `decay` (age idle patterns), `promote` (elevate high-confidence patterns), `quarantine` (isolate low-confidence patterns), `metrics` (URS dashboard). Module: `cortex/mcp/tools/learning_tool.py`.

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

**Golden Tests** — 486 tests that must ALWAYS pass (CORE-055 Golden Test Tier Contract). Run with `pytest-xdist` parallel execution. Location: `tests/golden/`.

**GoldenScenario** — Dataclass in `cortex/testing/_golden_factory.py` that parametrizes end-to-end test scenarios. Fields: `scenario_id`, `description`, `setup`, `input_data`, `expected_output`, `orchestrator_refs`. Factory method `GoldenScenario.from_yaml()` loads scenarios from YAML fixtures. Used by `@pytest.mark.parametrize` to generate test cases.

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

**Knowledge Hydration** — The process of resolving and injecting domain knowledge into execution context before orchestrator execution. Resolution order: Company overlays → Knowledge base (static) → SDLC knowledge (dynamic) → Pattern registry → LENS real-time analysis. All resolved knowledge is merged into the orchestrator's execution context.

## L

**LENS** — **L**anguage → **E**xamination → **N**avigation → **S**ynthesis. Code intelligence system with 10 parallel analyzers producing unified analysis in 300–800ms. Location: `cortex/lens/`.

**LENS Analyzers** — 10 parallel analyzers: AST, Git History, Comment, Import, Security, Pattern, Metrics, Domain.

## M

**MasterOrchestrator** — Central entry point orchestrator. Runs 4-stage pipeline: Interaction → Intent → Intelligence → Execution. Location: `cortex/orchestrators/core/master_orchestrator.py`.

**MCP (Model Context Protocol)** — JSON-RPC 2.0 communication standard connecting IDEs to CORTEX. 28 registered tools (39 target) exposed via stdio transport.

## O

**OrchestratorBase** — Legacy abstract base class used by 2 orchestrators only (`ServiceDecompositionOrchestrator`, `BusinessKnowledgeIngestionOrchestrator`). The primary base for all 51 wired orchestrators is `OrchestratorProtocolMixin` (Phase 58) + `IOrchestrator` protocol. Module: `cortex/core/orchestrator_base.py`.

**OrchestratorEventBus** — Decoupled communication channel for inter-orchestrator messaging. Module: `cortex/infrastructure/orchestrator_event_bus.py`.

## P

**Perception Tier** — First intelligence tier. Observes, parses, and classifies raw input. Location: `cortex/intelligence/perception/`.

**Phase Tests** — 177 tests that validate specific phase milestone completion. Location: `tests/`.

**Pre-Commit Validator** — Validates code against governance rules before commit. Module: `cortex/infrastructure/pre_commit_validator.py`.

**Pylance-style MCP** — CORTEX's MCP server auto-starts when VS Code opens the workspace — same pattern as the Pylance language server. No manual startup required.

**pytest-xdist** — pytest plugin for parallel test execution. Used with `-n auto --dist loadscope` for unit tests and `-n 4 --dist loadfile` for integration tests.

## R

**Reasoning Tier** — Second intelligence tier. Analyzes perceptions, assesses risk, and produces execution plans. Location: `cortex/intelligence/reasoning/`.

**Red-Green-Refactor (RGR)** — The two-level quality cycle in CORTEX. **Level 1 (Unit RGR):** TDDOrchestrator enforces RED (write failing test) → GREEN (implement minimum) → REFACTOR (clean up) for each feature/fix. **Level 2 (Sweep RGR):** SweepCatalogueOrchestrator runs DETECT (scan codebase) → FIX (apply remediation) → RESCAN (verify exhaustive coverage) loops until p0==0 and p1==0 (CORE-064). The two levels compose: unit RGR runs inside sweep RGR for comprehensive quality assurance. See also: TDD, CORE-064.

**Refactor Master** — Strategic planning document defining all phases of the CORTEX refactor. File: `cortex-registry/cortex-master.yaml` (thin index, ≤500 lines). Detail lives in `cortex-registry/_cortex-master/phases/`.

**ReinforcementEngine** — Core engine that receives `ReinforcementSignal` emissions, adjusts pattern confidence scores, and manages the promote/quarantine/decay lifecycle. Module: `cortex/intelligence/learning/reinforcement_signal.py`.

**ReinforcementSignal** — Dataclass carrying a typed feedback signal (see SignalType) from an orchestrator back to the learning subsystem. Fields: `signal_type`, `source`, `target_pattern`, `confidence_delta`, `context`, `timestamp`. Module: `cortex/intelligence/learning/reinforcement_signal.py`.

**RequestRephraseOrchestrator** — Orchestrator that clarifies ambiguous or incomplete requests before routing to execution. Location: `cortex/orchestrators/core/`.

## S

**ScaffoldWriter** — Emits `ScaffoldFile` objects produced by WorkflowEngine steps to disk (`mkdir -p`). Allows downstream pipeline steps whose `depends_on` gate checks for files to proceed without halting mid-run. Added today (BadMonolith Gap G2). Module: `cortex/core/scaffold_writer.py`.

**SDLC Workflow Engine** — The 7-phase software development lifecycle engine powered by `SDLCWorkflowOrchestrator`. Maps user intents (ANALYZE, DESIGN, IMPLEMENT, TEST, SECURITY, DEPLOY, REVIEW) to corresponding YAML workflow templates in `cortex-registry/workflows/templates/sdlc/`. Each phase includes knowledge hydration from `cortex-registry/knowledge/sdlc/`, security gates at every phase transition, and FSM-based execution via `WorkflowEngine`. Location: `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py`.

**SecurityOrchestrator** — Orchestrator handling security analysis, vulnerability detection, and security gate enforcement. Location: `cortex/orchestrators/core/`.

**Security-First Development** — CORTEX's 5-layer security architecture ensuring security is embedded at every development stage, not bolted on after the fact. Layers (outside-in): Runtime Protection → Audit & Compliance → Governance Enforcement → Code Analysis → Input Validation. Security gates enforce checks at every SDLC phase transition. Knowledge sources: `cortex-registry/knowledge-base/security/`, `cortex-registry/knowledge/sdlc/security-patterns.yaml`.

**Sharpen The Saw (STS)** — Demo repository ecosystem at `cortex-sts/CortexLabs/` used to showcase CORTEX capabilities. Contains `BadMonolith/` (intentionally problematic C#/.NET monolith with 0 tests, god classes, no DI) and `Refactored/` (the transformed result). Three primary usage scenarios: (1) onboarding demos, (2) digest comparison, (3) live refactoring workshops. Playbook reference: PB-STS-001. CORE rules are exempted from STS code since it's intentionally bad for demonstration.

**SignalType** — Enum defining URS reinforcement signal strengths: `STRONG_REWARD` (+1.0), `MILD_REWARD` (+0.5), `NEUTRAL` (0.0), `MILD_PUNISHMENT` (−0.5), `STRONG_PUNISHMENT` (−1.0). Used by all orchestrators that emit learning feedback. Module: `cortex/intelligence/learning/reinforcement_signal.py`.

**skull-rules.yaml** — YAML file containing all 38 CORE governance rule definitions (+ 2 AC-PERMANENT-FIX). Location: `cortex-registry/core/tier0-skull/skull-rules.yaml`.

**stdio Transport** — Standard input/output process communication. IDE writes JSON-RPC to stdin, CORTEX responds on stdout. No network ports required.

**SweepCatalogueOrchestrator** — CORE-064 enforcement engine. Tracks open/resolved items in every FIX/REFACTOR/AUDIT sweep using SQLite WAL (`cortex-runtime/sweeps/{sweep_id}.db`). No partial sweep can close without `assert_exhausted()` or `approve_wont_fix()`. Location: `cortex/orchestrators/support/sweep_catalogue_orchestrator.py`. (Note: `cortex_sweep_status` MCP tool is not yet registered in `mcp_registry.py` — sweep status is queried via the orchestrator directly.)

**Sweep Completeness Contract** — See CORE-064. Every sweep must exhaust its full catalogue before closing.

**Synthesis** — LENS synthesis phase that merges results from all 8 analyzers into a unified intelligence report.

## T

**TDD (Test-Driven Development)** — Mandatory development methodology (CORE-008). Cycle: RED (write failing test) → GREEN (implement minimum) → REFACTOR (clean up).

**TDDOrchestrator** — Orchestrator enforcing TDD cycle for IMPLEMENT, FIX, and TEST intents. Location: `cortex/orchestrators/core/tdd_orchestrator.py`.

**TestQualityGate** — Scoring system (0–9) evaluating test value. Formula: Impact + Likelihood + Detection + Efficiency - Maintenance.

**Thin Index Contract** — Governance rule requiring `cortex-master.yaml` to remain a reference index only (≤500 lines). Phase detail lives in dedicated files under `cortex-registry/planning/phases/`. Prevents context exhaustion from bloated plan files.

**3-Tier Loading Model** — Token optimization architecture with three progressive context tiers: T0 (Auto — `copilot-instructions.md`, ~300 tokens, every session), T1 (Prompt — user-selected prompt file, ~1,500–2,700 tokens), T2 (Agent — lazy-loaded specialist agents, ~1,000–5,000 tokens each). Reduces session bootstrap from ~50,000 tokens to ~3,000 tokens (94% reduction). See `05-infrastructure/08-token-optimization.md`.

**Token Optimization** — The set of strategies CORTEX uses to maximize productive turns in GitHub Copilot Chat sessions. Seven strategies: 3-Tier Loading Model, Lazy Agent Loading, LENS Intelligence Tiering, Request Rephrase compression, Continuation Prompt compression, YAML Lazy Loading with LRU caching, and Silent Autonomous Execution (CORE-049). Implementation spans `cortex/core/prompt_agent_integration.py`, `cortex/core/intelligence_mixin.py`, `cortex/core/yaml_loaders.py`, and `.github/templates/cortex-response-templates.md`.

**ToolResult** — Standard response object from MCP tool execution. Contains content (text), metadata, and audit reference.

## U

**Unified Reinforcement Signal (URS)** — Closed-loop learning system (Phase 83) where every orchestrator operation emits a typed reinforcement signal that adjusts pattern confidence scores. Five signal strengths (STRONG_REWARD → STRONG_PUNISHMENT). Patterns with ≥0.9 confidence are promoted to T1 knowledge; patterns ≤0.3 are quarantined. Idle patterns decay 0.1 per 30 days. 10 integration surfaces wired across OPJMixin, TDDOrchestrator, EnforcementOrchestrator, TrainerOrchestrator, TestValueScorer, KnowledgeSynthesisEngine, IntelligenceMatrixBuilder, and LENSOrchestrator. MCP tool: `cortex_learning`. Module: `cortex/intelligence/learning/reinforcement_signal.py`.

## W

**WAL (Write-Ahead Logging)** — SQLite journaling mode used by CortexAuditDB. Enables concurrent reads during single-writer transactions.

**WorkflowEngine** — Executes workflow templates from `cortex-registry/workflows/`. Exposes `load()` to parse YAML templates and `execute_step()` (SDO-compatible API) to run individual steps. Wired to `ScaffoldWriter` so scaffold artefacts are persisted to disk. Module: `cortex/core/workflow_engine.py`.

**WorkItem** — Canonical dataclass representing a work item across all ticketing systems. Fields: `id`, `title`, `description`, `state`, `type`, `tags`, `url`, `raw`. The `raw` field carries the full unmodified API response so company-specific fields (Area Path, Sprint, Custom.* ADO fields, Jira components) survive intact. Module: `cortex/repositories/work_item_provider.py`.

**WorkItemProvider** — `@runtime_checkable` Protocol defining the integration contract for all ticketing systems. Three required methods: `fetch_user_stories(project, **kwargs)`, `fetch_by_id(item_id)`, `health_check()`. Companies implement once; CORTEX routes through the same MCP surface regardless of backend. Module: `cortex/repositories/work_item_provider.py`.

**WORK_ITEM_SOURCE** — Environment variable that selects the active `WorkItemProvider`. Default: `"ado"` (Azure DevOps). Factory: `cortex/repositories/provider_factory.py`.

**Workflow Templates** — YAML-defined execution plans in `cortex-registry/workflows/templates/`. 17 categories including `sdlc/` (7-phase development lifecycle), `audit/` (production readiness), `governance/` (rule enforcement), `onboarding/` (repository analysis), `testing/` (test strategy), `security/` (vulnerability management), and `primitives/` (5 atomic categories: analysis, execution, governance, validation, intelligence). Templates compose from primitives to form complex workflows. Executed by `WorkflowEngine`. Company-specific customizations go in `cortex-registry/company/`.

**Workflow Template Primitives** — Atomic, reusable building blocks in `cortex-registry/workflows/templates/primitives/`. Five categories: `analysis/` (AST scan, security scan), `execution/` (TDD cycle, scaffold emit), `governance/` (sweep catalogue open/close, golden promotion), `validation/` (detect-fix-rescan-loop, schema validate), `intelligence/` (LENS pipeline, knowledge resolve). Templates compose from these primitives.

---

*Verified against live CORTEX codebase · 27 February 2026 (Phase 84 Complete)*
