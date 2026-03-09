# Glossary

---
title: CORTEX Glossary — Terminology Reference
type: reference
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-03-09
source_of_truth: cortex/ (live codebase)
order: 99
---

> Alphabetical reference of all CORTEX terms. All module paths verified against the live codebase.

---

## A

**Action Tier** — Third intelligence tier. Executes plans produced by the Reasoning tier. Generates code, tests, and transformations. Location: `cortex/intelligence/action/`.

**ADO (Azure DevOps)** — The default work item ticketing system integrated with CORTEX. Selected by setting `WORK_ITEM_SOURCE=ado`. Requires `ADO_ORG_URL`, `ADO_PAT`, and `ADO_PROJECT` environment variables. Adapter: `cortex/repositories/ado/ado_provider.py`.

**ADOWorkItemProvider** — Concrete implementation of the `WorkItemProvider` Protocol for Azure DevOps. Exposes `fetch_user_stories`, `fetch_by_id`, and `health_check` methods backed by ADO REST API calls. Companies fill in the stub method bodies with their HTTP client and field mapping logic. Location: `cortex/repositories/ado/ado_provider.py`.

**AI Context Intelligence** — Phase 121 capability that scans, classifies, PII-guards, and disseminates AI artifacts (copilot-instructions.md, .cursorrules, etc.) from external repositories into the CORTEX registry hierarchy. Supports 8 vendors: GitHub Copilot, Cursor, Claude, Windsurf, Cline, Continue, Tabnine, OpenAI. Modules: `AIContextScanner`, `AIContentClassifier`, `AIPIIGuard`, `AIContextDisseminator`. Location: `cortex/infrastructure/repositories/`.

**AIContextDisseminator** — Routes classified AI context to 5 registry destinations: knowledge/, governance/, config/, patterns/, and metrics/. Part of AI Context Intelligence pipeline. Location: `cortex/infrastructure/repositories/ai_context_disseminator.py`.

**AIContextScanner** — Multi-vendor AI artifact detection supporting 8 vendors via YAML-driven configuration. Detects copilot-instructions.md, .cursorrules, .continue/config.json, and similar AI tooling artifacts. Location: `cortex/infrastructure/repositories/ai_context_scanner.py`.

**AIPIIGuard** — PII protection layer that strips author names, emails, API keys, and internal hostnames from AI context before registry storage. Location: `cortex/infrastructure/repositories/ai_pii_guard.py`.

**Anti-Repetition Ring Buffer** — Deque-based memory (n=10) that prevents the same quote or principle from appearing in consecutive CORTEX responses. Part of PrincipleSelector. Module: `cortex/intelligence/principle_selector.py`.

**Archetype Classifier** — Intelligence component that identifies the structural archetype of a codebase (monolith, modular monolith, microservices, serverless, event-driven, etc.) using LENS analysis signals. The classification drives strategy selection in the Reasoning tier and adjusts governance rule severity based on the detected architecture style. Archetype definitions are maintained in `cortex-registry/archetypes/archetype-definitions.yaml`. Module: `cortex/intelligence/perception/archetype_classifier.py`.

**Atom (Response Template)** — Tier 1 building block in the 3-tier LEGO response template system. Smallest reusable units: identity, quote, principle, intent-reflection, status-footer. Location: `cortex-registry/templates/response/atoms/`.

**Audit Database (CortexAuditDB)** — SQLite WAL database storing all operation records with hash-chain integrity. Location: `.cortex-runtime/`. Module: `cortex/infrastructure/audit_db.py`.

**Audit Hash Chain** — Cryptographic chain linking each audit entry to the previous one, creating a tamper-evident log. Module: `cortex/infrastructure/audit_hash_chain.py`.

## B

**Block (Response Template)** — Tier 2 building block in the 3-tier LEGO response template system. Assembled from atoms: engagement, metrics, proceed-gate, completion-state, content. Location: `cortex-registry/templates/response/blocks/`.

**Brain Tiers** — Three-layer intelligence architecture: Perception → Reasoning → Action. Located at `cortex/intelligence/{perception,reasoning,action}/`.

**Bulkhead** — Resilience pattern that partitions resources to prevent one failing component from consuming all capacity. Module: `cortex/infrastructure/bulkhead_manager.py`.

## C

**Canary Deployment** — Deployment strategy that routes a small percentage of traffic to new versions before full rollout. Config: `deployment/canary_config.yaml`.

**Circuit Breaker** — Resilience pattern that stops calls to failing services. States: Closed → Open → Half-Open. Module: `cortex/infrastructure/circuit_breaker.py`.

**Code Review Orchestrator** — Domain orchestrator that performs structured, multi-stage code review. Examines code quality, security posture, pattern adherence, documentation coverage, and governance compliance in a single coordinated pass. Produces prioritised findings with severity, remediation guidance, and links to the relevant governance rule. Exposed via the `cortex_review` MCP tool and triggered by the REVIEW intent type. Location: `cortex/orchestrators/domain/code_review_orchestrator.py`.

**Cohesive Brain Refactor** — Multi-phase architectural transformation that unified multiple packages into the single `cortex` package.

**Composition (Response Template)** — Tier 3 building block in the 3-tier LEGO response template system. Terminal outputs assembled from blocks: implement, fix, refactor, debug, audit-fix, health, vacuum, educational. Location: `cortex-registry/templates/response/compositions/`.

**Confidence Score** — Numerical value (0.0–1.0) produced by IntentRouter indicating certainty of intent classification. Higher scores route to primary orchestrators.

**ConsolidatedTool** — Base class for all MCP tools. Provides consistent naming, parameter validation, execution, and audit trail. Module: `cortex/mcp/mcp_tool_base.py`.

**Content Library (EpochShuffler)** — Centralised content management facade that provides anti-repetition guarantees across all content pools: quotes (120 entries), principles (90 entries), and analogies. The EpochShuffler algorithm ensures every item in a pool is used exactly once before any item repeats — like a playlist that plays every song before reshuffling. Accessed via `ContentLibraryFacade`. Module: `cortex/intelligence/content_library_facade.py`.

**ContentLibraryFacade** — Single entry point for all content selection operations (quotes, principles, analogies). Delegates to pool-specific EpochShuffler instances and enforces anti-repetition ring buffers. Replaces direct access to `atom-quote.yaml` and `high-value-principles.yaml`. Module: `cortex/intelligence/content_library_facade.py`.

**CORE-055** — Golden Test Tier Contract. Golden tests in `tests/golden/` must always pass. Zero regression allowed.

**CORE-064** — Sweep Completeness Contract. Every FIX/REFACTOR/AUDIT sweep must exhaust its full issue catalogue before closing. Enforced by `SweepCatalogueOrchestrator`.

**CORE Rules** — Governance rules identified by `CORE-nnn` IDs. An extensive set of CORE rules active in `cortex-registry/core/tier0-skull/skull-rules.yaml` (+ AC rules), all enforced at pre-commit + CI + runtime.

**cortex_ado** — MCP tool for Azure DevOps work item synthesis. Pulls user stories, bugs, and tasks from ADO boards, enriches them with LENS context, and injects sprint-aware acceptance criteria into the intelligence pipeline. Extends the provider-agnostic `WorkItemProvider` protocol. Module: `cortex/mcp/tools/ado_tool.py`.

**cortex_feedback** — MCP tool for structured user feedback capture. Records satisfaction signals, improvement suggestions, and correction notes against specific CORTEX responses. Feedback flows into the Unified Reinforcement Signal for confidence adjustment. Implemented by `cortex/orchestrators/support/feedback_orchestrator.py`; exposed via `cortex/tools/feedback_agent.py`.

**cortex_learning** — MCP tool for Unified Reinforcement Signal management. Six operations: `emit` (record signal), `history` (query signals), `decay` (age idle patterns), `promote` (elevate high-confidence patterns), `quarantine` (isolate low-confidence patterns), `metrics` (URS dashboard). Module: `cortex/mcp/tools/learning_tool.py`.

**cortex_process_request** — Mandatory MCP entry point. Routes ALL user requests through MasterOrchestrator 4-stage pipeline. Module: `cortex/mcp/tools/core.py`.

**cortex_fetch_work_items** — MCP tool for provider-agnostic work item access. Fetches user stories, bugs, and tasks from the configured ticketing system (ADO, Jira, custom). Provider is selected via `WORK_ITEM_SOURCE` env var. Module: `cortex/mcp/tools/work_item_tool.py`.

**cortex_review** — MCP tool exposing the Code Review Orchestrator. Accepts a unified diff (PR), runs the 6-stage review pipeline (structure → security → patterns → documentation → governance → synthesis), and returns an APPROVE / REQUEST_CHANGES / BLOCK verdict with P0–P3 prioritised findings. Module: `cortex/mcp/tools/cortex_review.py`.

## D

**Defence in Depth** — Security architecture principle where multiple independent layers of protection ensure no single point of failure can allow a threat to reach production. In CORTEX, five security layers operate at commit time, build time, runtime, static analysis, and release gates — like a building with a perimeter fence, locked doors, key cards, CCTV, and alarms.

**Definition of Ready (DoR)** — Checklist presented in MasterOrchestrator Stage 1. Ensures scope, acceptance criteria, and dependencies are clear before execution.

**Distill / DISTILL Intent** — A CORTEX intent type (Phase 129) that reduces a multi-turn conversation to an executable, context-dense prompt. The 5-stage pipeline (segment → reconstruct → reconcile → synthesise → compress) eliminates noise while preserving all goals, decisions, and constraints. Exposed as the `cortex_distill` MCP tool.

**Document Ingest Pipeline** — 5-component system for converting external documents (Word, Excel, PowerPoint, PDF, YAML, Markdown) into structured knowledge within `cortex-registry/`. Components: FileClassifier (9 categories, PII rejection), DocumentReader (lazy-loaded Office/PDF libraries with graceful degradation), KnowledgeExtractor (YAML normalization, text-to-knowledge), ContentRouter (14-domain routing table), DocumentIngestOrchestrator (pipeline coordinator with OPJ integration and teardown support). Phase 144 delivery. Location: `cortex/orchestrators/support/ingest/`.

**Documentation Intelligence** — Knowledge domain containing 60+ best practices across 10 sub-domains: technical documentation, API documentation, ADRs, runbooks, release notes, onboarding documentation, knowledge management, documentation testing, accessibility, and governance. Registered in Knowledge INDEX.yaml with domain signal: `document|documentation|docs|writing|readme|runbook|adr|release.notes`. Phase 145 delivery. Location: `cortex-registry/knowledge/best-practices/documentation/documentation-intelligence.yaml`.

**Domain Brain** — Domain-specific knowledge module that provides context for business logic decisions. Location: `cortex/intelligence/domain_brain/`.

## E

**EnforcementOrchestrator** — Orchestrator that validates code against CORE governance rules. Coordinates multiple enforcement agents. Location: `cortex/orchestrators/core/`.

**EpochShuffler** — Anti-repetition algorithm that guarantees every item in a content pool is selected exactly once before any item repeats. Named after the machine-learning concept of epoch-based data shuffling. Powers the Content Library's quote, principle, and analogy pools. See also: Content Library (EpochShuffler), ContentLibraryFacade. Module: `cortex/intelligence/content_library_facade.py`.

**Evidence Bundle** — Collection of audit records, test results, and governance checks packaged as compliance proof. Module: `cortex/infrastructure/evidence_bundle.py`.

**ExtendedGovernanceAgent** — Enforcement agent covering CORE-058 through CORE-063 rules.

## F

**Feedback / FEEDBACK Intent** — A CORTEX intent type for structured user feedback. When triggered, the FeedbackOrchestrator captures satisfaction signals, improvement suggestions, or correction notes and routes them into the Unified Reinforcement Signal for confidence adjustment. Exposed as the `cortex_feedback` MCP tool. Location: `cortex/orchestrators/support/feedback_orchestrator.py`.

**FeedbackOrchestrator** — Support orchestrator that processes FEEDBACK intent requests. Validates feedback structure, links it to the originating request via audit trail, and emits a reinforcement signal based on the feedback sentiment. Location: `cortex/orchestrators/support/feedback_orchestrator.py`.

**Framework Self-Analyzer (CortexFrameworkAnalyzer)** — Intelligence component that introspects CORTEX's own architecture at runtime — counting orchestrators, MCP tools, governance rules, workflow templates, and intent types. Powers the `refresh_prompt_suite.py` script and enables CORTEX to validate its documentation against its live implementation. Detects architecture drift between code and documentation as P0/P1 violations. Module: `cortex/intelligence/framework_analyzer.py`.

## G

**Golden Tests** — Tests that must ALWAYS pass (CORE-055 Golden Test Tier Contract). Run with `pytest-xdist` parallel execution. Location: `tests/golden/`.

**GoldenScenario** — Dataclass in `cortex/testing/_golden_factory.py` that parametrizes end-to-end test scenarios. Fields: `scenario_id`, `description`, `setup`, `input_data`, `expected_output`, `orchestrator_refs`. Factory method `GoldenScenario.from_yaml()` loads scenarios from YAML fixtures. Used by `@pytest.mark.parametrize` to generate test cases.

**Governance Agents** — Specialized agents that enforce specific CORE rule categories: TestNaming, FileNaming, ImportValidation, TypeHint, Docstring, DuplicateDetection, SecurityScan, ExtendedGovernance.

**Graceful Degradation** — Resilience pattern returning partial results when non-critical services fail. Module: `cortex/infrastructure/graceful_degradation.py`.

## H

**Hash Chain** — See Audit Hash Chain.

**HEXA-MODE** — Mode definitions loaded from YAML registry. Defines operational modes for different execution contexts.

## I

**IntentRouter** — Orchestrator that classifies requests into multiple intent types (IMPLEMENT, FIX, REFACTOR, etc.) and routes to appropriate domain orchestrators. Location: `cortex/orchestrators/core/intent_router.py`.

**Introduce / INTRODUCE Intent** — A CORTEX intent type for interactive, role-based onboarding. When triggered, CORTEX presents tailored capability overviews for the detected role (Business Leader, Product Owner, Software Engineer, or Curious Learner) and invites exploration through guided prompts.

## J

**JSON-RPC 2.0** — Protocol used for MCP communication between IDE clients and CORTEX server. Standard request/response format over stdio transport.

## K

**Knowledge Base** — Domain knowledge stored in `cortex-registry/knowledge-base/` and managed by `cortex/knowledge/`.

**Knowledge Guidance Traceability** — Decision audit trail system where every knowledge consultation emits a DecisionTraceabilityLogger.log_decision() call with RESOLUTION type, recording module path, domain, entry count, confidence, and rationale. Provides auditable evidence of which knowledge was consulted for every guidance resolution. QW-006 compliance. Phase 143 delivery. Wired into `KnowledgeGuidanceEngine`. Module: `cortex/core/knowledge_guidance_engine.py`.

**Knowledge Hydration** — The process of resolving and injecting domain knowledge into execution context before orchestrator execution. Resolution order: Company overlays → Knowledge base (static) → SDLC knowledge (dynamic) → Pattern registry → LENS real-time analysis. All resolved knowledge is merged into the orchestrator's execution context.

## L

**LEGO Architecture (Response Templates)** — 3-tier modular system for composing CORTEX responses. Tier 1: Atoms (5 primitives). Tier 2: Blocks (5 composites). Tier 3: Compositions (8 terminal formats). Enables consistent, reusable response structures. Phase 120 delivery. Location: `cortex-registry/templates/response/`.

**LENS** — **L**anguage → **E**xamination → **N**avigation → **S**ynthesis. Code intelligence system with multiple parallel analyzers producing unified analysis. Location: `cortex/lens/`.

**LENS Analyzers** — Parallel analyzers including: AST, Git History, Comment, Import, Security, Pattern, Metrics, Domain, and more.

## M

**MasterOrchestrator** — Central entry point orchestrator. Runs 4-stage pipeline: Interaction → Intent → Intelligence → Execution. Location: `cortex/orchestrators/core/master_orchestrator.py`.

**MCP (Model Context Protocol)** — JSON-RPC 2.0 communication standard connecting IDEs to CORTEX. A growing library of registered tools exposed via stdio transport.

## O

**OrchestratorBase** — Legacy abstract base class used by a small number of orchestrators only. The primary base for all wired orchestrators is `OrchestratorProtocolMixin` + `IOrchestrator` protocol. Module: `cortex/core/orchestrator_base.py`.

**OrchestratorEventBus** — Decoupled communication channel for inter-orchestrator messaging. Module: `cortex/infrastructure/orchestrator_event_bus.py`.

## P

**Perception Tier** — First intelligence tier. Observes, parses, and classifies raw input. Location: `cortex/intelligence/perception/`.

**Phase Tests** — Tests that validate specific milestone completion. Location: `tests/`.

**Pre-Commit Validator** — Validates code against governance rules before commit. Module: `cortex/infrastructure/pre_commit_validator.py`.

**Principle Block Library** — Curated collection of 90 SDLC principles across 10 domains: TDD, refactoring, architecture, security, API design, testing, observability, code quality, documentation, and devops. Injected into analysis/design responses via PrincipleSelector. Phase 124 delivery (initial 30), expanded post-Phase 125. Location: `cortex-registry/knowledge/sdlc/high-value-principles.yaml`.

**PrincipleSelector** — Intelligence component that selects contextually relevant quotes and principles with anti-repetition guarantees. Uses weighted-random selection within theme-filtered candidates, ring buffer (n=10) for deduplication, and telemetry (p95 ≤ 3ms). Phases 123-124 delivery. Module: `cortex/intelligence/principle_selector.py`.

**Pylance-style MCP** — CORTEX's MCP server auto-starts when VS Code opens the workspace — same pattern as the Pylance language server. No manual startup required.

**PROTECTED_DIRS** — Constant in `cortex/orchestrators/health/constants.py` listing 15 directories that VacuumOrchestrator is permanently forbidden from modifying: cortex/, tests/, .github/, scripts/, deployment/, .vscode/, cortex-registry/, docs/, .git/, node_modules/, venv/, .venv/, __pycache__/, .pytest_cache/, .mypy_cache/. Used across all 8 vacuum stages. Phase 141 delivery.

**pytest-xdist** — pytest plugin for parallel test execution. Used with `-n auto --dist loadscope` for unit tests and `-n 4 --dist loadfile` for integration tests.

## Q

**Quote Library** — Curated collection of 120 literary quotes across 10 themes (quality, improvement, security, architecture, discipline, systems-thinking, strategy, flow, learning, universal) sourced from engineering and business literature. Provides contextual wisdom in response headers. Accessed via ContentLibraryFacade with EpochShuffler anti-repetition. Location: `cortex-registry/templates/response/atoms/atom-quote.yaml`.

**Quality Analysis Engine** — Intelligence component that evaluates codebase quality across multiple dimensions: structural complexity, test coverage adequacy, documentation completeness, dependency health, and governance compliance posture. Produces a composite quality score (0–100) with per-dimension breakdowns and trend tracking over time. Findings feed into the Code Review Orchestrator and the production readiness audit. Module: `cortex/intelligence/quality_analysis_engine.py`.

## R

**Reasoning Tier** — Second intelligence tier. Analyzes perceptions, assesses risk, and produces execution plans. Location: `cortex/intelligence/reasoning/`.

**Red-Green-Refactor (RGR)** — The two-level quality cycle in CORTEX. **Level 1 (Unit RGR):** TDDOrchestrator enforces RED (write failing test) → GREEN (implement minimum) → REFACTOR (clean up) for each feature/fix. **Level 2 (Sweep RGR):** SweepCatalogueOrchestrator runs DETECT (scan codebase) → FIX (apply remediation) → RESCAN (verify exhaustive coverage) loops until p0==0 and p1==0 (CORE-064). The two levels compose: unit RGR runs inside sweep RGR for comprehensive quality assurance. See also: TDD, CORE-064.

**Refactor Master** — Strategic planning document defining all phases of the CORTEX refactor. File: `cortex-registry/cortex-master.yaml` (thin index, ≤500 lines). Detail lives in `cortex-registry/_cortex-master/phases/`.

**ReinforcementEngine** — Core engine that receives `ReinforcementSignal` emissions, adjusts pattern confidence scores, and manages the promote/quarantine/decay lifecycle. Module: `cortex/intelligence/learning/reinforcement_signal.py`.

**ReinforcementSignal** — Dataclass carrying a typed feedback signal (see SignalType) from an orchestrator back to the learning subsystem. Fields: `signal_type`, `source`, `target_pattern`, `confidence_delta`, `context`, `timestamp`. Module: `cortex/intelligence/learning/reinforcement_signal.py`.

**RequestRephraseOrchestrator** — Orchestrator that clarifies ambiguous or incomplete requests before routing to execution. Location: `cortex/orchestrators/core/`.

**Response Rendering Rules** — 14 mandatory formatting rules enforced on all CORTEX response templates via golden tests: R1 (blank lines after headings), R2 (blank lines around lists), R3 (table formatting), R4 (no empty headers), R5 (no hard-wrap), R6 (single H1), Rule 1 (no tree characters), Rule 3 (no long lines), Rule 4 (max 5 columns). Phase 146 delivery. Tests: `tests/golden/test_response_rendering_rules_golden.py`.

**REVIEW / Code Review Intent** — Intent type routed to the Code Review Orchestrator. Triggers multi-pass code review across the changed-file set: structural analysis, security audit, governance compliance, test-coverage gap detection, and style conformance. Reviews are emitted inline as structured comments with severity (P0–P3) and fix suggestions. MCP tool: `cortex_review`. See also: Code Review Orchestrator.

## S

**ScaffoldWriter** — Emits `ScaffoldFile` objects produced by WorkflowEngine steps to disk (`mkdir -p`). Allows downstream pipeline steps whose `depends_on` gate checks for files to proceed without halting mid-run. Added today (BadMonolith Gap G2). Module: `cortex/core/scaffold_writer.py`.

**SDLC Workflow Engine** — The 7-phase software development lifecycle engine powered by `SDLCWorkflowOrchestrator`. Maps user intents (ANALYZE, DESIGN, IMPLEMENT, TEST, SECURITY, DEPLOY, REVIEW) to corresponding YAML workflow templates in `cortex-registry/workflows/templates/sdlc/`. Each phase includes knowledge hydration from `cortex-registry/knowledge/sdlc/`, security gates at every phase transition, and FSM-based execution via `WorkflowEngine`. Location: `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py`.

**SecurityOrchestrator** — Orchestrator handling security analysis, vulnerability detection, and security gate enforcement. Location: `cortex/orchestrators/core/`.

**Security-First Development** — CORTEX's 5-layer security architecture ensuring security is embedded at every development stage, not bolted on after the fact. Layers (outside-in): Runtime Protection → Audit & Compliance → Governance Enforcement → Code Analysis → Input Validation. Security gates enforce checks at every SDLC phase transition. Knowledge sources: `cortex-registry/knowledge-base/security/`, `cortex-registry/knowledge/sdlc/security-patterns.yaml`.

**Sharpen The Saw (STS)** — Demo repository ecosystem at `cortex-sts/CortexLabs/` used to showcase CORTEX capabilities. Contains `BadMonolith/` (intentionally problematic C#/.NET monolith with 0 tests, god classes, no DI) and `Refactored/` (the transformed result). Three primary usage scenarios: (1) onboarding demos, (2) digest comparison, (3) live refactoring workshops. Playbook reference: PB-STS-001. CORE rules are exempted from STS code since it's intentionally bad for demonstration.

**SignalType** — Enum defining URS reinforcement signal strengths: `STRONG_REWARD` (+1.0), `MILD_REWARD` (+0.5), `NEUTRAL` (0.0), `MILD_PUNISHMENT` (−0.5), `STRONG_PUNISHMENT` (−1.0). Used by all orchestrators that emit learning feedback. Module: `cortex/intelligence/learning/reinforcement_signal.py`.

**skull-rules.yaml** — YAML file containing all CORE governance rule definitions (+ AC-PERMANENT-FIX rules). Location: `cortex-registry/core/tier0-skull/skull-rules.yaml`.

**stdio Transport** — Standard input/output process communication. IDE writes JSON-RPC to stdin, CORTEX responds on stdout. No network ports required.

**SweepCatalogueOrchestrator** — CORE-064 enforcement engine. Tracks open/resolved items in every FIX/REFACTOR/AUDIT sweep using SQLite WAL (`cortex-runtime/sweeps/{sweep_id}.db`). No partial sweep can close without `assert_exhausted()` or `approve_wont_fix()`. Location: `cortex/orchestrators/support/sweep_catalogue_orchestrator.py`. (Note: `cortex_sweep_status` MCP tool is not yet registered in `mcp_registry.py` — sweep status is queried via the orchestrator directly.)

**Sweep Completeness Contract** — See CORE-064. Every sweep must exhaust its full catalogue before closing.

**Synthesis** — LENS synthesis phase that merges results from all 8 analyzers into a unified intelligence report.

## T

**TDD (Test-Driven Development)** — Mandatory development methodology (CORE-008). Cycle: RED (write failing test) → GREEN (implement minimum) → REFACTOR (clean up).

**TDDOrchestrator** — Orchestrator enforcing TDD cycle for IMPLEMENT, FIX, and TEST intents. Location: `cortex/orchestrators/core/tdd_orchestrator.py`.

**TestQualityGate** — Scoring system (0–9) evaluating test value. Formula: Impact + Likelihood + Detection + Efficiency - Maintenance.

**Thin Index Contract** — Governance rule requiring `cortex-master.yaml` to remain a reference index only (≤500 lines). Phase detail lives in dedicated files under `cortex-registry/planning/phases/`. Prevents context exhaustion from bloated plan files.

**Threat Model Engine** — Security intelligence component that generates threat models for a given codebase surface. Applies STRIDE classification (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) to entry points, data flows, and trust boundaries. Produces a ranked threat catalogue with risk scores and recommended mitigations. Integrates with the Security Orchestrator and the `/audit fix` pipeline Layer 5 security gate. Module: `cortex/intelligence/threat_model_engine.py`.

**3-Tier Loading Model** — Token optimization architecture with three progressive context tiers: T0 (Auto — `copilot-instructions.md`, ~300 tokens, every session), T1 (Prompt — user-selected prompt file, ~1,500–2,700 tokens), T2 (Agent — lazy-loaded specialist agents, ~1,000–5,000 tokens each). Reduces session bootstrap from ~50,000 tokens to ~3,000 tokens (94% reduction). See `05-infrastructure/08-token-optimization.md`.

**Token Optimization** — The set of strategies CORTEX uses to maximize productive turns in GitHub Copilot Chat sessions. Seven strategies: 3-Tier Loading Model, Lazy Agent Loading, LENS Intelligence Tiering, Request Rephrase compression, Continuation Prompt compression, YAML Lazy Loading with LRU caching, and Silent Autonomous Execution (CORE-049). Implementation spans `cortex/core/prompt_agent_integration.py`, `cortex/core/intelligence_mixin.py`, `cortex/core/yaml_loaders.py`, and `.github/templates/cortex-response-templates.md`.

**ToolResult** — Standard response object from MCP tool execution. Contains content (text), metadata, and audit reference.

## U

**Unified Reinforcement Signal (URS)** — Closed-loop learning system where every orchestrator operation emits a typed reinforcement signal that adjusts pattern confidence scores. Five signal strengths (STRONG_REWARD → STRONG_PUNISHMENT). Patterns with high confidence are promoted to top-tier knowledge; patterns with low confidence are quarantined. Idle patterns decay over time. Multiple integration surfaces wired across key orchestrators and intelligence components. MCP tool: `cortex_learning`. Module: `cortex/intelligence/learning/reinforcement_signal.py`.

**Universal Repo Intelligence** — Intelligence subsystem that extracts structured understanding from any repository regardless of language or framework. Employs 8 parallel extractors: dependency graph, architecture topology, test coverage map, API surface catalogue, configuration schema, build pipeline model, documentation index, and contributor-ownership matrix. Results feed into LENS analysis, onboarding workflows, and the Archetype Classifier. Module: `cortex/intelligence/repo_intelligence.py`.

## V

**Vacuum Recency Guard** — Safety mechanism within the Vacuum Orchestrator that prevents deletion of recently modified files. Files touched within a configurable grace window (default: 7 days) are excluded from vacuum sweeps even if they match cleanup heuristics. Protects work-in-progress artefacts from aggressive workspace cleaning. Enforced during all 8 vacuum stages. Module: `cortex/orchestrators/health/vacuum_orchestrator.py`.

**Vacuum Source Protection** — Hardened safety system ensuring VacuumOrchestrator NEVER modifies files inside protected directories. Comprises: PROTECTED_DIRS constant (15 directories), validate_safe_run() pre-flight check (dry-run with path verification), RollbackManager SHA validation (40-character hex regex), and 8 golden tests (GV-012..GV-019). Phase 141 delivery. Module: `cortex/orchestrators/health/vacuum_orchestrator.py`, `cortex/orchestrators/health/constants.py`.

**validate_safe_run()** — Pre-flight safety check in VacuumOrchestrator that runs a dry-run with recency_guard_hours=0, inspects all planned operations against PROTECTED_DIRS, and returns a list of warnings. If warnings are non-empty, the vacuum operation aborts. Phase 141 delivery. Module: `cortex/orchestrators/health/vacuum_orchestrator.py`.

## W

**WAL (Write-Ahead Logging)** — SQLite journaling mode used by CortexAuditDB. Enables concurrent reads during single-writer transactions.

**WorkflowGateway SSOT** — Single Source of Truth pattern for intent→template mappings. WorkflowGateway._MODE_TEMPLATE_MAP is the canonical map; SubPhaseComposer imports from it via get_mode_template_map() rather than maintaining a duplicate. Phase 142 delivery (DRY refactor). Module: `cortex/orchestrators/workflow/workflow_gateway.py`.

**WorkflowEngine** — Executes workflow templates from `cortex-registry/workflows/`. Exposes `load()` to parse YAML templates and `execute_step()` (SDO-compatible API) to run individual steps. Wired to `ScaffoldWriter` so scaffold artefacts are persisted to disk. Module: `cortex/core/workflow_engine.py`.

**WorkItem** — Canonical dataclass representing a work item across all ticketing systems. Fields: `id`, `title`, `description`, `state`, `type`, `tags`, `url`, `raw`. The `raw` field carries the full unmodified API response so company-specific fields (Area Path, Sprint, Custom.* ADO fields, Jira components) survive intact. Module: `cortex/repositories/work_item_provider.py`.

**WorkItemProvider** — `@runtime_checkable` Protocol defining the integration contract for all ticketing systems. Three required methods: `fetch_user_stories(project, **kwargs)`, `fetch_by_id(item_id)`, `health_check()`. Companies implement once; CORTEX routes through the same MCP surface regardless of backend. Module: `cortex/repositories/work_item_provider.py`.

**WORK_ITEM_SOURCE** — Environment variable that selects the active `WorkItemProvider`. Default: `"ado"` (Azure DevOps). Factory: `cortex/repositories/provider_factory.py`.

**Workflow Templates** — YAML-defined execution plans in `cortex-registry/workflows/templates/`. Multiple categories including `sdlc/` (development lifecycle), `audit/` (production readiness), `governance/` (rule enforcement), `onboarding/` (repository analysis), `testing/` (test strategy), `security/` (vulnerability management), and `primitives/` (atomic categories: analysis, execution, governance, validation, intelligence). Templates compose from primitives to form complex workflows. Executed by `WorkflowEngine`. Company-specific customizations go in `cortex-registry/company/`.

**Workflow Template Primitives** — Atomic, reusable building blocks in `cortex-registry/workflows/templates/primitives/`. Categories include: `analysis/` (AST scan, security scan), `execution/` (TDD cycle, scaffold emit), `governance/` (sweep catalogue open/close, golden promotion), `validation/` (detect-fix-rescan-loop, schema validate), `intelligence/` (LENS pipeline, knowledge resolve). Templates compose from these primitives.

---

*Verified against live CORTEX codebase*
