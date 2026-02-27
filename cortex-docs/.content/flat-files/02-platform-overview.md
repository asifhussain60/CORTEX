# CORTEX Platform Overview

---
title: CORTEX — Cognitive Real-Time Execution Platform
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/ + cortex-registry/cortex-master.yaml
consolidates: [00-getting-started-one-pager, 00-getting-started-how-cortex-works, 00-getting-started-key-concepts, 00-getting-started-inventory]
order: 1
---

> **CORTEX** (Cognitive Real-Time Execution) is a production-grade AI engineering framework that combines cognitive intelligence, automated governance, and a 51-orchestrator execution engine to help engineering teams ship faster — with confidence.

---

## The Core Idea

Traditional development tools answer questions. CORTEX thinks alongside your team.

When a developer makes a request — "implement this feature", "fix this bug", "audit this code" — CORTEX does not hand back a snippet. It classifies the intent, analyses the codebase with parallel analyzers, validates against 38 governance rules, generates tests first (mandatory), and executes a coordinated multi-step workflow through the appropriate orchestrator. Every action is observable, auditable, and reversible.

The difference is like a calculator versus a brain. A calculator waits for instructions. A brain perceives the situation, reasons about the best approach, and acts — learning from every interaction.

---

## Platform at a Glance

CORTEX is built from one canonical Python package (`cortex`) with a single import namespace. There is no `cortex_intelligence`, no `cortex_lens`, no `cortex.brain`. Every import is `cortex.*`.

| Metric | Value |
|--------|-------|
| Canonical Package | `cortex` (single namespace, all imports `cortex.*`) |
| Wired Orchestrators | 51 across 4 tiers (17 core, 7 domain, 23 support, 4 git) |
| MCP Tools | 28 registered / 39 target, Pylance-style stdio auto-start |
| CORE Governance Rules | 38 active (+ 2 AC rules), enforced at pre-commit, CI, and runtime |
| Test Suite | 16,942 collected (unit + preflight + golden + phase tiers) |
| LENS Analyzers | 15 parallel analyzer components, 300–800ms combined latency |
| Languages Analyzed | Python, TypeScript/JavaScript, C#/.NET, Angular, React, Vue |
| Intelligence Tiers | Quick (<200ms), Targeted (<2s), Full (<10s) |
| Parallel Testing | pytest-xdist with `-n auto --dist loadscope` |

---

## Six Capability Domains

CORTEX organises capabilities into six cognitive domains, each analogous to a specialised region of the brain working in concert:

| Domain | What It Does | Key Metric |
|--------|-------------|------------|
| **Core Platform** | MCP gateway, 51-orchestrator dispatch, state management, health monitoring | 28 registered MCP tools (39 target), Pylance-style stdio |
| **Intelligence (LENS)** | 15-component parallel code understanding covering AST, Git, Security, Patterns, Metrics, and more | 300–800ms full analysis |
| **Brain (Perception → Reasoning → Action)** | Pattern recognition, strategy selection, execution planning — learns from every repository | Confidence scored 0.0–1.0 |
| **Decisioning** | Intent routing across 10+ intent types to 51 wired orchestrators; TDD workflow enforcement | IntentRouter with LENS classification |
| **Governance** | Pre-commit, CI, and runtime enforcement of 38 active CORE rules; sweep completeness (CORE-064) | 10 enforcement agents, <150ms validation |
| **Extensibility** | Custom MCP tools, domain orchestrators, workflow templates, enterprise patterns, work-item integrations | Hot-reload; zero core changes |

---

## How a Request Flows

Every request passes through a structured pipeline before any code is written. The entire journey is auditable.

**Stage −1 · Request Enrichment (15–35ms)** — The RequestRephraseOrchestrator silently enriches the raw request with relevant governance context, a breaking-risk assessment, and design pillar considerations. The developer sees none of this; it happens automatically to ensure the MasterOrchestrator receives a fully contextualised request.

**Stage 0 · MCP Gateway (5–15ms)** — The enriched request arrives at the MCP Gateway over JSON-RPC 2.0 via stdio transport. The gateway validates the message, routes to the correct MCP tool (28 registered tools; 39 target), and enforces rate limiting.

**Stage 1 · Intent Classification (20–40ms)** — IntentRouter uses LENS-based intelligence to determine what the request is asking for: IMPLEMENT, FIX, REFACTOR, ANALYZE, PLAN, AUDIT, DESIGN, DEBUG, INVESTIGATE, QUERY, DIGEST, or REPHRASE. Confidence above 0.85 routes immediately. Between 0.60 and 0.84, the system routes but asks a clarifying question. Below 0.60, the user is asked to rephrase.

**Stage 2 · LENS Analysis (300–800ms)** — When the orchestrator needs to understand the codebase, LENS runs its parallel analyzers: AST structure, Git history, comment coverage, import dependencies, security vulnerabilities, architecture patterns, complexity metrics, business domain detection, and technology stack fingerprinting. All run simultaneously and produce a unified awareness of the code.

**Stage 3 · Brain Intelligence (50–200ms)** — The intelligence system processes LENS data through three cognitive tiers. Perception scans repository signatures against known patterns and scores confidence. Reasoning evaluates strategies weighted by historical success rates. Action builds a step-by-step execution plan with TDD gates and rollback points.

**Stage 4 · Governance Gate (<150ms)** — The EnforcementOrchestrator coordinates 10 enforcement agents covering TDD compliance, security, naming conventions, architecture integrity, and more. The result is PASS, WARNING, or BLOCKED. A BLOCKED result halts the operation immediately with no files changed.

**Stage 5 · Execution** — The designated orchestrator executes the plan. For IMPLEMENT and FIX intents, the TDDOrchestrator enforces the RED → GREEN → REFACTOR cycle: write failing tests first, implement minimum code to pass, then improve the code while keeping all tests green. For REFACTOR, semantic transformations are applied with regression scoring. For ANALYZE, LENS produces a full multi-analyzer report delivered inline.

**Stage 6 · Result Delivery** — Results are delivered inline per CORE-002 (no report files created). The audit trail is recorded in CortexAuditDB (SQLite with WAL mode) stored in `.cortex-runtime/`.

The complete pipeline from request to result typically takes between 500ms and 2 seconds for most operations, with full auditability at every stage.

---

## Key Concepts

### Orchestrators

An orchestrator is a specialised processing engine for one category of work. CORTEX has 51 wired orchestrators across four tiers, all satisfying the IOrchestrator protocol via OrchestratorProtocolMixin.

Every orchestrator follows a five-step lifecycle: setup, govern, execute, validate, teardown. Governance audit is wired into teardown, and both execute and run operations auto-log start and end markers to the SQLite audit database. This audit logging is non-blocking — a failure to log never prevents execution.

All inter-orchestrator communication flows through the MasterOrchestrator, ensuring every handoff is auditable, governance gates are checked between dispatches, and no circular dependencies form.

**Core Tier (17):** MasterOrchestrator (central coordinator), IntentRouter (intent classification), TDDOrchestrator (test-first enforcement), EnforcementOrchestrator (governance gate), WorkflowOrchestrator (YAML template execution), ConversationOrchestrator (multi-turn state), AuditOrchestrator (19-point production scan), plus stage orchestrators, response formatting, meta-audit, holistic validation, challenge engine, SOLID validation, and security vulnerability scanning.

**Domain Tier (7):** RefactoringOrchestrator (semantic code transformations across Python, TypeScript, C#), PlanningOrchestrator (phase decomposition and gap catalogues), DomainOrchestrator (domain-specific intelligence), DashboardOrchestrator (static dashboard generation), SDLCWorkflowOrchestrator (lifecycle template execution), EnhancedPlanningOrchestrator (ROI scoring and wave decomposition), and ServiceDecompositionOrchestrator.

**Support Tier (23):** Health monitoring, vacuum cleanup, upgrade management, bulk content digestion, sweep catalogue tracking (CORE-064), environment setup, repository onboarding, debugging, documentation site orchestration, auto-healing MCP, unified quality assurance, and more.

**Git Tier (4):** GitOrchestrator (commit, branch, merge, diff), GitPublishOrchestrator (structured commit and push), PreCommitEnforcementOrchestrator (CORE rule validation at commit time), and SanitizationOrchestrator (secret scanning and PII removal).

### MCP Gateway

The Model Context Protocol is the communication standard connecting IDEs to CORTEX. It uses JSON-RPC 2.0 passed over stdio in development and HTTP in production. The MCP server auto-starts when VS Code opens the workspace — identical to how Pylance starts. No manual startup is required.

CORTEX exposes 28 registered MCP tools (39 target) organised by category: core routing, governance and compliance, intelligence and LENS, planning and audit, testing and quality, diagnostics and health, automation and workflows, maintenance and cleanup, version control, documentation, and toolkit operations. The remaining 11 tools are in active planning phases.

### Git-Backed Registry

Instead of a database, CORTEX stores all configuration, governance rules, workflow templates, and knowledge in plain YAML files committed to Git in the `cortex-registry/` directory. This means every change is versioned and auditable, there is no database dependency, configuration is readable by both humans and machines, and rollback is simply `git revert`.

### LENS (Language → Examination → Navigation → Synthesis)

CORTEX's code intelligence engine. It runs specialised analyzers in parallel against any codebase and produces a unified context — structured intelligence that feeds the Brain's Perception → Reasoning → Action pipeline. See the dedicated LENS intelligence document for the full architecture.

### Brain Tiers (Perception → Reasoning → Action)

The three-layer cognitive core of CORTEX, housed in `cortex/intelligence/`. Perception recognises patterns in LENS data, Reasoning selects strategies based on those patterns, and Action builds step-by-step execution plans. See the dedicated intelligence architecture document for the full deep-dive.

### CORE Rules

38 numbered governance standards enforced automatically at pre-commit, CI, and runtime. The most critical include: CORE-002 (all output inline, no report files), CORE-008 (TDD mandatory), CORE-011 (type hints on all functions), CORE-012 (docstrings on all public APIs), CORE-028 (snake_case file naming), CORE-035 (single canonical implementation), CORE-048 (holistic validation gate), CORE-049 (silent autonomous execution), CORE-055 (golden test tier contract), and CORE-064 (sweep completeness, no partial fixes).

### Enforcement Agents

Ten specialised agents within the EnforcementOrchestrator check different categories of CORE rules before any code-mutating operation. A gate result is PASS, WARNING, or BLOCKED. A BLOCKED result stops the operation immediately with no files changed.

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

Nine architecture patterns are registered in the pattern registry: mediator, strategy, observer, factory, template-method, chain-of-responsibility, adapter, repository, and command. The Perception tier matches repository signatures against these patterns to inform strategy selection.

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
| Testing | pytest-xdist parallel execution; 16,942 tests collected |
| Observability | OpenTelemetry tracing, Prometheus metrics, Grafana dashboards, SQLite audit log |
| Audit Trail | CortexAuditDB (SQLite WAL mode) in `.cortex-runtime/` with AC_START and AC_COMPLETE markers on every orchestrator invocation |

---

## Acronyms and Key Terms

| Acronym | Full Form | Purpose |
|---------|-----------|---------|
| CORTEX | Cognitive Real-Time Execution | The platform — an AI engineering framework that perceives, reasons, and acts |
| LENS | Language → Examination → Navigation → Synthesis | 10-analyzer parallel code intelligence pipeline |
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
| CORE | CORTEX Operational Rule Enforcement | 38 immutable governance rules |

---

## Component Inventory Summary

### Orchestrators by Tier

| Tier | Count | Key Members |
|------|-------|-------------|
| Core | 17 | MasterOrchestrator, IntentRouter, TDDOrchestrator, EnforcementOrchestrator, WorkflowOrchestrator, AuditOrchestrator, ConversationOrchestrator |
| Domain | 7 | RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator, SDLCWorkflowOrchestrator, EnhancedPlanningOrchestrator |
| Support | 23 | HealthOrchestrator, VacuumOrchestrator, UpgradeOrchestrator, SweepCatalogueOrchestrator, DebuggerOrchestrator, OnboardingOrchestrator, AutoHealingMCPOrchestrator, CortexDocsOrchestrator |
| Git | 4 | GitOrchestrator, GitPublishOrchestrator, PreCommitEnforcementOrchestrator, SanitizationOrchestrator |

### MCP Tools by Category

| Category | Tools | Count |
|----------|-------|-------|
| Core & Routing | cortex_classify, cortex_orchestrator, cortex_request_lifecycle, cortex_challenge | 4 |
| Governance | cortex_governance, cortex_load, cortex_validate, cortex_validate_request, cortex_check | 5 |
| Intelligence | cortex_knowledge, cortex_refactor, cortex_vision, cortex_total_recall, cortex_ask | 5 |
| Planning & Audit | cortex_plan, cortex_onboard | 2 |
| Testing & Quality | cortex_generate_tests | 1 |
| Diagnostics | cortex_verify, cortex_debug, cortex_metrics | 3 |
| Automation | cortex_workflow, cortex_enrich | 2 |
| Maintenance | cortex_vacuum | 1 |
| VCS | cortex_git | 1 |
| Documentation | cortex_dashboard, cortex_tools_catalog | 2 |
| Toolkit | cortex_batch_transform, cortex_scan | 2 |

*28 registered as of 2026-02-26. Authoritative source: `cortex/mcp/mcp_registry.py`. Target: 39 tools — 11 in active planning phases.*

### LENS Analyzers

AST (code structure), Git History (change patterns), Comment (documentation quality), Import (dependency health), Security (vulnerability detection), Pattern (architecture signatures), Metrics (complexity measurement), Domain (business context), and Tech Stack (framework detection). All run in parallel with combined latency of 300–800ms.

### Supported Languages

Python (full AST, security, metrics, pattern analysis), TypeScript and JavaScript (full analysis), C# and .NET (full analysis), Angular, React, and Vue (framework-specific analysis).

---

## Workspace Structure

The CORTEX repository is organised into well-defined directories:

- **cortex/** — Python source across 20 directories: orchestrators, mcp/tools, core, testing, intelligence, lens, governance, infrastructure, and more
- **cortex-registry/** — YAML governance rules, patterns, planning phases, workflow templates, knowledge base, and company-specific configuration
- **tests/** — All tests mirroring the cortex/ structure, including golden, unit, integration, and phase tests
- **.cortex-runtime/** — Runtime data including SQLite databases, logs, and execution traces
- **cortex-docs/** — User-facing documentation site (HTML, CSS, generated content)
- **.github/** — CI/CD, prompts, agent specifications, and templates

---

*CORTEX v1.0.0 · February 2026 · 51 wired orchestrators · 28 registered MCP tools (39 target) · 38 CORE rules · 16,942 tests collected*
