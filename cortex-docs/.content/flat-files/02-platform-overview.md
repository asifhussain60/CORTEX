# CORTEX Platform Overview

---
title: CORTEX — Cognitive Real-Time Execution Platform
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex/ + cortex-registry/cortex-master.yaml
consolidates: [00-getting-started-one-pager, 00-getting-started-how-cortex-works, 00-getting-started-key-concepts, 00-getting-started-inventory]
order: 1
---

> **CORTEX** (Cognitive Real-Time Execution) is a production-grade AI engineering framework that combines cognitive intelligence, automated governance, and a comprehensive orchestrator execution engine to help engineering teams ship faster — with confidence.

---

## The Core Idea

Traditional development tools answer questions. CORTEX thinks alongside your team.

When a developer makes a request — "implement this feature", "fix this bug", "audit this code" — CORTEX does not hand back a snippet. It classifies the intent, analyses the codebase with parallel analyzers, validates against governance rules, generates tests first (mandatory), and executes a coordinated multi-step workflow through the appropriate orchestrator. Every action is observable, auditable, and reversible.

The difference is like a calculator versus a brain. A calculator waits for instructions. A brain perceives the situation, reasons about the best approach, and acts — learning from every interaction.

---

## Platform at a Glance

CORTEX is built from one canonical Python package (`cortex`) with a single import namespace. There is no `cortex_intelligence`, no `cortex_lens`, no `cortex.brain`. Every import is `cortex.*`.

| Metric | Value |
|--------|-------|
| Canonical Package | `cortex` (single namespace, all imports `cortex.*`) |
| Orchestrator Files | 259 across 9 domains (core:102, domain:28, support:51, git:4, health:27, intelligence:16, persona:6, validation:12, workflow:6) |
| MCP Tools | 29 registered tools, Pylance-style stdio auto-start |
| CORE Governance Rules | 32 YAML files in `cortex-registry/core/`, enforced at pre-commit, CI, and runtime |
| Test Suite | ~7,581 tests collected (unit + preflight + golden + phase tiers) |
| Intent Types | 28 (IMPLEMENT, FIX, REFACTOR, AUDIT, DEBUG, and 23 more) |
| LENS Analyzers | Multiple parallel analyzer components, sub-second combined latency |
| Languages Analyzed | Python, TypeScript/JavaScript, C#/.NET, Angular, React, Vue |
| Intelligence Tiers | Quick (<200ms), Targeted (<2s), Full (<10s) |
| Parallel Testing | pytest-xdist with `-n auto --dist loadscope` |
| Debug Strategies | 8 strategies: 3 Python + 5 multi-stack (Frontend, HTML-Vision, API, SQL, DotNet) |
| RCA Engine | 4 methodologies: Five Whys, Fishbone, Fault Tree, Causal Chain |
| Workflow Templates | 79 templates across 17 categories |
| Phases Complete | 99 phases, under continuous development |

---

## Six Capability Domains

CORTEX organises capabilities into six cognitive domains, each analogous to a specialised region of the brain working in concert:

| Domain | What It Does | Key Metric |
|--------|-------------|------------|
| **Core Platform** | MCP gateway, multi-tier orchestrator dispatch, state management, health monitoring | 29 registered MCP tools, Pylance-style stdio |
| **Intelligence (LENS)** | Parallel code understanding covering AST, Git, Security, Patterns, Metrics, and more | Sub-second full analysis |
| **Brain (Perception → Reasoning → Action)** | Pattern recognition, strategy selection, execution planning — learns from every repository | Confidence scored 0.0–1.0 |
| **Decisioning** | Intent routing across 28 intent types to wired orchestrators; TDD workflow enforcement | IntentRouter with LENS classification |
| **Governance** | Pre-commit, CI, and runtime enforcement of 32 governance YAMLs; sweep completeness (CORE-064); WorkflowGateway enforcement | 10 enforcement agents, sub-second validation |
| **Extensibility** | Custom MCP tools, domain orchestrators, 79 workflow templates, enterprise patterns, work-item integrations | Hot-reload; zero core changes |

---

## How a Request Flows

Every request passes through a structured pipeline before any code is written. The entire journey is auditable.

**Stage −1 · Request Enrichment** — The RequestRephraseOrchestrator silently enriches the raw request with relevant governance context, a breaking-risk assessment, and design pillar considerations. The developer sees none of this; it happens automatically to ensure the MasterOrchestrator receives a fully contextualised request.

**Stage 0 · MCP Gateway** — The enriched request arrives at the MCP Gateway over JSON-RPC 2.0 via stdio transport. The gateway validates the message, routes to the correct MCP tool from the registered tools library, and enforces rate limiting.

**Stage 1 · Intent Classification** — IntentRouter uses LENS-based intelligence to determine what the request is asking for: IMPLEMENT, FIX, REFACTOR, ANALYZE, PLAN, AUDIT, DESIGN, DEBUG, INVESTIGATE, QUERY, DIGEST, REPHRASE, WORKFLOW_COMPOSE, or one of the other twenty-eight recognised intent types. High confidence routes immediately. Medium confidence routes but asks a clarifying question. Low confidence asks the user to rephrase.

**Stage 2 · LENS Analysis (300–800ms)** — When the orchestrator needs to understand the codebase, LENS runs its parallel analyzers: AST structure, Git history, comment coverage, import dependencies, security vulnerabilities, architecture patterns, complexity metrics, business domain detection, and technology stack fingerprinting. All run simultaneously and produce a unified awareness of the code.

**Stage 3 · Brain Intelligence (50–200ms)** — The intelligence system processes LENS data through three cognitive tiers. Perception scans repository signatures against known patterns and scores confidence. Reasoning evaluates strategies weighted by historical success rates. Action builds a step-by-step execution plan with TDD gates and rollback points.

**Stage 4 · Governance Gate** — The EnforcementOrchestrator coordinates multiple enforcement agents covering TDD compliance, security, naming conventions, architecture integrity, and more. The result is PASS, WARNING, or BLOCKED. A BLOCKED result halts the operation immediately with no files changed.

**Stage 5 · Execution** — The designated orchestrator executes the plan. For IMPLEMENT and FIX intents, the TDDOrchestrator enforces the RED → GREEN → REFACTOR cycle: write failing tests first, implement minimum code to pass, then improve the code while keeping all tests green. For REFACTOR, semantic transformations are applied with regression scoring. For ANALYZE, LENS produces a full multi-analyzer report delivered inline.

**Stage 6 · Result Delivery** — Results are delivered inline per CORE-002 (no report files created). The audit trail is recorded in CortexAuditDB (SQLite with WAL mode) stored in `.cortex-runtime/`.

The complete pipeline from request to result typically takes between 500ms and 2 seconds for most operations, with full auditability at every stage.

---

## Key Concepts

### Orchestrators

An orchestrator is a specialised processing engine for one category of work. CORTEX has 259 orchestrator files across 9 domains (core, domain, support, git, health, intelligence, persona, validation, workflow), all satisfying the IOrchestrator protocol via OrchestratorProtocolMixin.

Every orchestrator follows a five-step lifecycle: setup, govern, execute, validate, teardown. Governance audit is wired into teardown, and both execute and run operations auto-log start and end markers to the SQLite audit database. This audit logging is non-blocking — a failure to log never prevents execution.

All inter-orchestrator communication flows through the MasterOrchestrator, ensuring every handoff is auditable, governance gates are checked between dispatches, and no circular dependencies form.

**Core Tier (17):** MasterOrchestrator (central coordinator), IntentRouter (intent classification), TDDOrchestrator (test-first enforcement), EnforcementOrchestrator (governance gate), WorkflowOrchestrator (YAML template execution), ConversationOrchestrator (multi-turn state), AuditOrchestrator (19-point production scan), plus stage orchestrators, response formatting, meta-audit, holistic validation, challenge engine, SOLID validation, and security vulnerability scanning.

**Domain Tier (7):** RefactoringOrchestrator (semantic code transformations across Python, TypeScript, C#), PlanningOrchestrator (phase decomposition and gap catalogues), DomainOrchestrator (domain-specific intelligence), DashboardOrchestrator (static dashboard generation), SDLCWorkflowOrchestrator (lifecycle template execution), EnhancedPlanningOrchestrator (ROI scoring and wave decomposition), and ServiceDecompositionOrchestrator.

**Support Tier:** Health monitoring, vacuum cleanup, upgrade management, bulk content digestion, sweep catalogue tracking (CORE-064), environment setup, repository onboarding, debugging, documentation site orchestration, auto-healing MCP, unified quality assurance, and more.

**Git Tier:** GitOrchestrator (commit, branch, merge, diff), GitPublishOrchestrator (structured commit and push), PreCommitEnforcementOrchestrator (CORE rule validation at commit time), and SanitizationOrchestrator (secret scanning and PII removal).

### MCP Gateway

The Model Context Protocol is the communication standard connecting IDEs to CORTEX. It uses JSON-RPC 2.0 passed over stdio in development and HTTP in production. The MCP server auto-starts when VS Code opens the workspace — identical to how Pylance starts. No manual startup is required.

CORTEX exposes 29 registered MCP tools organised by category: core routing, governance and compliance, intelligence and LENS, planning and audit, testing and quality, diagnostics and health, automation and workflows, maintenance and cleanup, version control, documentation, and toolkit operations.

### Git-Backed Registry

Instead of a database, CORTEX stores all configuration, governance rules, workflow templates, and knowledge in plain YAML files committed to Git in the `cortex-registry/` directory. This means every change is versioned and auditable, there is no database dependency, configuration is readable by both humans and machines, and rollback is simply `git revert`.

### LENS (Language → Examination → Navigation → Synthesis)

CORTEX's code intelligence engine. It runs specialised analyzers in parallel against any codebase and produces a unified context — structured intelligence that feeds the Brain's Perception → Reasoning → Action pipeline. See the dedicated LENS intelligence document for the full architecture.

### Brain Tiers (Perception → Reasoning → Action)

The three-layer cognitive core of CORTEX, housed in `cortex/intelligence/`. Perception recognises patterns in LENS data, Reasoning selects strategies based on those patterns, and Action builds step-by-step execution plans. See the dedicated intelligence architecture document for the full deep-dive.

### CORE Rules

Numbered governance standards enforced automatically at pre-commit, CI, and runtime. The most critical include: CORE-002 (all output inline, no report files), CORE-008 (TDD mandatory), CORE-011 (type hints on all functions), CORE-012 (docstrings on all public APIs), CORE-028 (snake_case file naming), CORE-035 (single canonical implementation), CORE-048 (holistic validation gate), CORE-049 (silent autonomous execution), CORE-055 (golden test tier contract), CORE-064 (sweep completeness, no partial fixes), and CORE-068 (universal convergence gate — detect→fix→rescan until zero P0/P1).

### Enforcement Agents

Specialised agents within the EnforcementOrchestrator check different categories of CORE rules before any code-mutating operation. A gate result is PASS, WARNING, or BLOCKED. A BLOCKED result stops the operation immediately with no files changed.

### Confidence Scores

A value between 0.0 and 1.0 that CORTEX assigns to decisions. Scores of 0.7 or above lead to auto-execution. Scores between 0.5 and 0.7 may prompt a clarification. Scores below 0.5 trigger a request for user guidance. These scores are used in pattern matching, intent classification, and strategy selection.

### TDD Workflow

Every IMPLEMENT and FIX operation follows RED → GREEN → REFACTOR. First, a failing test specifies the desired behaviour (RED). Then, minimum code is written to pass the test (GREEN). Finally, the code is improved while keeping all tests passing (REFACTOR). This is enforced by CORE-008 and the TDDOrchestrator — it is architecturally mandated, not a suggestion.

### Unified Reinforcement Signal (URS)

A closed-loop feedback system where orchestrators emit reinforcement signals after every operation. Signals are typed from STRONG_REWARD (+1.0) down to STRONG_PUNISHMENT (−1.0) and adjust pattern confidence scores over time. Patterns with high confidence and multiple rewards are promoted to top-tier knowledge. Patterns with low confidence and punishments are quarantined. Idle patterns decay over time.

### TestQualityGate

A scoring system that rates every test 0–9 based on impact, likelihood, detection capability, efficiency, and maintenance cost. Tests scoring 7 or above are kept, 4–6 are flagged for review, and below 4 are candidates for deletion.

### WorkflowEngine FSM

The runtime layer that executes YAML-defined workflow templates as a Finite State Machine. Steps progress through PENDING → RUNNING → CHECKING → PASSED or FAILED states. A StepHandlerRegistry maps step type identifiers to handler callables. The ConvergenceLoopExecutor loops through detect-fix-rescan cycles until all P0 and P1 violations are resolved.

### Enterprise Patterns

Architecture patterns are registered in the pattern registry, including mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, and command. The Perception tier matches repository signatures against these patterns to inform strategy selection.

### WorkItemProvider

A pluggable ticketing integration protocol that connects any ticketing system (Azure DevOps, Jira, or custom) to CORTEX through a single MCP surface. Companies implement a three-method contract once, and the `cortex_fetch_work_items` tool works identically regardless of which system sits behind it.

---

## Technology Foundations

| Aspect | Technology |
|--------|-----------|
| Protocol | Model Context Protocol (JSON-RPC 2.0) — works with VS Code Copilot, Claude, Cursor |
| Transport | stdio (development), HTTP (production) |
| Package | 1 canonical Python package (`cortex`) — all imports use `cortex.*` |
| Storage | Git-backed YAML registry — no external database required |
| Testing | pytest-xdist parallel execution; ~7,581 tests collected |
| Observability | OpenTelemetry tracing, Prometheus metrics, Grafana dashboards, SQLite audit log |
| Audit Trail | CortexAuditDB (SQLite WAL mode) in `.cortex-runtime/` with AC_START and AC_COMPLETE markers on every orchestrator invocation |

---

## Acronyms and Key Terms

| Acronym | Full Form | Purpose |
|---------|-----------|---------|
| CORTEX | Cognitive Real-Time Execution | The platform — an AI engineering framework that perceives, reasons, and acts |
| LENS | Language → Examination → Navigation → Synthesis | Multi-analyzer parallel code intelligence pipeline |
| MCP | Model Context Protocol | JSON-RPC 2.0 communication between AI hosts and CORTEX |
| TDD | Test-Driven Development | Mandatory RED → GREEN → REFACTOR cycle (CORE-008) |
| FSM | Finite State Machine | Step execution model for workflow steps |
| URS | Unified Reinforcement Signal | Closed-loop feedback adjusting pattern confidence |
| OPJ | Operational Pattern Journal | Learning subsystem recording success and failure patterns |
| BLUF | Bottom Line Up Front | Adaptive 3-tier communication for different audiences |
| SDLC | Software Development Lifecycle | Workflow intelligence engine for lifecycle templates |
| SOLID | Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion | Design principle compliance checker |
| DoR | Definition of Ready | Per-turn confidence tracking before operations |
| AC | Activity Control | Cross-cutting tracing markers on every orchestrator invocation |
| IC | Intelligence Capability | Intelligence subsystems in the Intelligence Matrix |
| CC | CORTEX Capability | Platform capabilities in the Intelligence Matrix |
| CORE | CORTEX Operational Rule Enforcement | Immutable governance rules enforced at every stage |

---

## Component Inventory Summary

### Orchestrators by Tier

| Tier | Key Members |
|------|-------------|
| Core | MasterOrchestrator, IntentRouter, TDDOrchestrator, EnforcementOrchestrator, WorkflowOrchestrator, AuditOrchestrator, ConversationOrchestrator |
| Domain | RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator, SDLCWorkflowOrchestrator, EnhancedPlanningOrchestrator |
| Support | HealthOrchestrator, VacuumOrchestrator, UpgradeOrchestrator, SweepCatalogueOrchestrator, DebuggerOrchestrator, OnboardingOrchestrator, AutoHealingMCPOrchestrator, CortexDocsOrchestrator |
| Git | GitOrchestrator, GitPublishOrchestrator, PreCommitEnforcementOrchestrator, SanitizationOrchestrator |

### MCP Tools by Category

| Category | Tools |
|----------|-------|
| Core & Routing | cortex_classify, cortex_orchestrator, cortex_request_lifecycle, cortex_challenge |
| Governance | cortex_governance, cortex_load, cortex_validate, cortex_validate_request, cortex_check |
| Intelligence | cortex_knowledge, cortex_refactor, cortex_vision, cortex_total_recall, cortex_ask |
| Planning & Audit | cortex_plan, cortex_onboard |
| Testing & Quality | cortex_generate_tests |
| Diagnostics | cortex_verify, cortex_debug, cortex_metrics |
| Automation | cortex_workflow, cortex_enrich |
| Maintenance | cortex_vacuum |
| VCS | cortex_git |
| Documentation | cortex_dashboard, cortex_tools_catalog |
| Toolkit | cortex_batch_transform, cortex_scan |

*Authoritative source: `cortex/mcp/mcp_registry.py`. The tool library continues to grow with each release.*

### LENS Analyzers

AST (code structure), Git History (change patterns), Comment (documentation quality), Import (dependency health), Security (vulnerability detection), Pattern (architecture signatures), Metrics (complexity measurement), Domain (business context), and Tech Stack (framework detection). All run in parallel with sub-second combined latency.

### Supported Languages

Python (full AST, security, metrics, pattern analysis), TypeScript and JavaScript (full analysis), C# and .NET (full analysis), Angular, React, and Vue (framework-specific analysis).

---

## Workspace Structure

The CORTEX repository is organised into well-defined directories:

- **cortex/** — Python source across streamlined directories: orchestrators, mcp/tools, core, testing, intelligence, lens, governance, infrastructure, and more
- **cortex-registry/** — YAML governance rules, patterns, planning phases, workflow templates, knowledge base, and company-specific configuration
- **tests/** — All tests mirroring the cortex/ structure, including golden, unit, integration, and phase tests
- **.cortex-runtime/** — Runtime data including SQLite databases, logs, and execution traces
- **cortex-docs/** — User-facing documentation site (HTML, CSS, generated content)
- **.github/** — CI/CD, prompts, agent specifications, and templates

---

*CORTEX · Cognitive Real-Time Execution · Source of truth: `cortex-registry/cortex-master.yaml`*
