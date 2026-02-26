# CORTEX: Platform Overview

---
title: CORTEX — Cognitive Real-Time Execution Platform
type: overview
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-25
source_of_truth: cortex/ + cortex-registry/cortex-master.yaml
phases_complete: [Phase 65, Phase 66, Phase 67, Phase 68, Phase 69]
format: one-pager
order: 1
---

> **What is CORTEX?** A production-grade AI engineering framework that combines cognitive intelligence, automated governance, and a 27-orchestrator execution engine to help engineering teams ship faster — with confidence.

---

## The Core Idea

Traditional development tools answer questions. CORTEX **thinks alongside your team**.

When a developer makes a request — "implement this feature", "fix this bug", "audit this code" — CORTEX doesn't hand back a snippet. It classifies intent, analyses the codebase with 10 parallel LENS analyzers, validates against 35 CORE governance rules, generates tests first (mandatory), and executes a coordinated multi-step workflow through the appropriate orchestrator. Every action is observable, auditable, and reversible.

Think of it like the difference between a calculator and a brain. A calculator waits for instructions. A brain perceives the situation, reasons about the best approach, and acts — learning from every interaction.

---

## Platform at a Glance

```
  ┌───────────────────────────────────────────────────────────────┐
  │              CORTEX PLATFORM v1.0.0 (Phase 79-D Complete)       │
  │       1 Package · 27 Orchestrators · 39 MCP Tools (37 active)            │
  │       Intelligence Matrix · WorkflowEngine FSM               │
  │                                                               │
  │  ┌──────────────┐  ┌───────────────────┐  ┌───────────────┐  │
  │  │ MCP Gateway  │─▶│  Orchestration    │─▶│ Intelligence  │  │
  │  │ 39 tools     │  │  3 canonical tiers│  │ LENS + Brain  │  │
  │  │ stdio/HTTP   │  │  27 wired         │  │ Matrix (15×15)│  │
  │  └──────────────┘  └───────────────────┘  └───────────────┘  │
  │         │                   │                     │           │
  │         ▼                   ▼                     ▼           │
  │  ┌──────────────┐  ┌───────────────────┐  ┌───────────────┐  │
  │  │ Governance   │  │  Testing          │  │ Git Registry  │  │
  │  │ 35 CORE rules│  │  16,259 tests     │  │ YAML SSOT     │  │
  │  │ CORE-064     │  │  486 golden       │  │ 69 Phases     │  │
  │  └──────────────┘  └───────────────────┘  └───────────────┘  │
  └───────────────────────────────────────────────────────────────┘
```

---

## Six Capability Domains

| Domain | What It Does | Key Metric |
|--------|-------------|------------|
| **🏗️ Core Platform** | MCP gateway, 27-orchestrator dispatch, state management, health monitoring | 39 MCP tools (37 active), Pylance-style stdio |
| **🤖 Intelligence (LENS)** | 10-analyzer parallel code understanding — AST, Git, Security, Patterns, Metrics, and more | 300–800ms full analysis |
| **🧠 Brain (Perception → Reasoning → Action)** | Pattern recognition, strategy selection, execution planning — learns from every repo | Confidence scored 0.0–1.0 |
| **🔗 Intelligence Matrix** | 15×15 cross-capability wiring map — ensures all intelligence subsystems are connected | 50% coverage gate enforced |
| **🎯 Decisioning** | Intent routing across 10+ intent types to 27 wired orchestrators; TDD workflow enforcement | IntentRouter with LENS classification |
| **🛡️ Governance** | Pre-commit + CI + runtime enforcement of 35 active CORE rules; CORE-064 sweep completeness | 10 agents, <150ms validation |
| **⚙️ WorkflowEngine** | YAML→FSM→ConvergenceLoop runtime (Phase 67); StepStateMachine + StepHandlerRegistry | Convergence gate in TDD + audit templates |
| **🔌 Extensibility** | Custom MCP tools, domain orchestrators, workflow templates, enterprise patterns | Hot-reload; zero core changes |

---

## How a Request Flows

```
Developer request ("implement auth middleware")
      │
      ▼
[Stage -1] RequestRephraseOrchestrator ── enriches with governance + risk context
      │
      ▼
[Stage 0] MCP Gateway ── validates JSON-RPC, routes to tool
      │
      ▼
[Stage 1] IntentRouter ── LENS-based classification → IMPLEMENT
      │
      ├─ IMPLEMENT/FIX ──▶ TDDOrchestrator  (RED → GREEN → REFACTOR)
      ├─ ANALYZE       ──▶ LENS Synthesis    (10-analyzer parallel scan)
      ├─ REFACTOR      ──▶ RefactoringOrchestrator (semantic, multi-language)
      ├─ PLAN          ──▶ PlanningOrchestrator
      ├─ AUDIT         ──▶ EnforcementOrchestrator + Audit Coordinator
      ├─ DESIGN        ──▶ Design Orchestrator
      └─ DEBUG         ──▶ DebuggerOrchestrator
                │
                ▼
      [Governance Gate] ── 10 enforcement agents, blocks non-compliant actions
                │
                ▼
      [Intelligence Layer] ── perception → reasoning → action plan
                │
                ▼
      Result delivered inline (CORE-002: no report files created)
```

---

## The Brain in Three Sentences

CORTEX's **Perception Layer** (in `cortex/intelligence/perception/`) scans every repository for known signatures — frameworks, patterns, risk indicators — and scores confidence for each match.
The **Reasoning Layer** (in `cortex/intelligence/reasoning/`) selects the best strategy from that pattern data, weighing historical success rates and context.
The **Action Layer** (in `cortex/intelligence/action/`) converts the chosen strategy into a step-by-step execution plan with built-in TDD gates and rollback.

This three-layer model means CORTEX improves with every project it touches — patterns learned in one repository inform recommendations in the next.

---

## Governance Is Not Optional

Every action runs through governance enforcement:

1. **Pre-Commit Gate** — EnforcementOrchestrator with 10 agents blocks violations before code changes
2. **CI Pipeline** — Automated validation in continuous integration
3. **Runtime Enforcement** — Rules checked during orchestrator execution

35 active CORE rules are enforced automatically; the most critical include:
- **CORE-002** — All output inline (never create .md/.txt report files)
- **CORE-008** — TDD mandatory (write failing test first, no exceptions)
- **CORE-011** — Type hints on all functions
- **CORE-012** — Docstrings on all public APIs
- **CORE-028** — File naming: snake_case only
- **CORE-035** — Single canonical implementation (no duplicates)
- **CORE-048** — Holistic validation gate before IMPLEMENT/FIX/REFACTOR
- **CORE-049** — Silent autonomous execution (progress bars only)
- **CORE-055** — Golden Test Tier Contract (486 golden tests always pass)
- **CORE-064** — Sweep Completeness Contract (no partial sweeps across session boundaries)

---

## What Developers Experience

| Workflow | Without CORTEX | With CORTEX |
|----------|---------------|-------------|
| New feature | Write code, hope tests follow | RED → GREEN → REFACTOR, enforced by CORE-008 |
| Code review | Manual checklist | Automated 8-analyzer LENS intelligence scan |
| Governance | Periodic audit | Continuous, every request, every commit |
| Onboarding new repo | Days of reading | LENS onboarding + infrastructure catalog |
| Refactoring | Risky, manual | Semantic refactor with regression scoring |
| Test quality | Subjective | Scored 0–9 by TestQualityGate; <7 flagged |

---

## Technology Foundations

- **Protocol:** Model Context Protocol (JSON-RPC 2.0) — works with VS Code Copilot, Claude, Cursor
- **Transport:** stdio (development) / HTTP (production)
- **Package:** 1 canonical Python package (`cortex`) — all imports use `cortex.*`
- **Storage:** Git-backed registry — no PostgreSQL, no MongoDB required
- **Testing:** pytest-xdist parallel execution (`-n auto --dist loadscope`); 16,259 tests (486 golden, 177 phase)
- **Observability:** OpenTelemetry tracing, Prometheus metrics, Grafana dashboards, SQLite audit log (`.cortex-runtime/audit.db`)
- **Languages analyzed by LENS:** Python, TypeScript/JavaScript, C#/.NET, Angular, React, Vue

---

## Acronyms & Key Terms

| Acronym | Full Form | Purpose |
|---------|-----------|---------|
| **CORTEX** | **CO**gnitive **R**eal-**T**ime **EX**ecution | The platform itself — an AI engineering framework that perceives, reasons, and acts |
| **LENS** | **L**anguage → **E**xamination → **N**avigation → **S**ynthesis | 10-analyzer parallel code intelligence pipeline (AST, Git, Security, Config, DB, Dependency, etc.) |
| **OPJ** | **O**perational **P**attern **J**ournal | Learning subsystem that records, consults, and promotes patterns from every operation |
| **MCP** | **M**odel **C**ontext **P**rotocol | JSON-RPC 2.0 communication protocol between AI hosts (Copilot, Claude, Cursor) and CORTEX |
| **TDD** | **T**est-**D**riven **D**evelopment | Mandatory RED → GREEN → REFACTOR cycle enforced by CORE-008 |
| **FSM** | **F**inite **S**tate **M**achine | StepStateMachine execution model for workflow steps (PENDING → RUNNING → CHECKING → PASSED/FAILED) |
| **STS** | **S**harpen **T**he **S**aw | Playbook-driven refactoring demos — 61 anti-pattern detection across security, SOLID, quality, performance |
| **BLUF** | **B**ottom **L**ine **U**p **F**ront | Adaptive 3-tier communication: BLUF_ONLY (executive), HYBRID (summary + details), FULL_DETAIL (complete) |
| **SDLC** | **S**oftware **D**evelopment **L**ife**C**ycle | Workflow intelligence engine that selects and executes SDLC templates from the registry |
| **SOLID** | **S**ingle Responsibility, **O**pen/Closed, **L**iskov, **I**nterface Segregation, **D**ependency Inversion | Design principle compliance checker with SQLite audit trail |
| **DoR** | **D**efinition **o**f **R**eady | Per-turn confidence tracking displayed before every IMPLEMENT/FIX/REFACTOR operation |
| **AC** | **A**ctivity **C**ontrol | Cross-cutting tracing markers (`AC_START` / `AC_COMPLETE`) on every orchestrator invocation |
| **IC** | **I**ntelligence **C**apability | 20 intelligence capabilities in the Intelligence Matrix (IC-001 through IC-020) |
| **CC** | **C**ORTEX **C**apability | 20 platform capabilities in the Intelligence Matrix (CC-001 through CC-020) |
| **CORE** | **C**ORTEX **O**perational **R**ule **E**nforcement | 35 immutable governance rules (CORE-002, CORE-008, CORE-011, etc.) |

---

## Capability Dimensions — Grouped by Function

### 🤖 Intelligence Layer

The intelligence subsystem gives CORTEX its "brain" — the ability to perceive, learn, reason, and act.

| Component | Module | What It Does |
|-----------|--------|-------------|
| **LENS Pipeline** | `cortex/lens/` | 10 parallel analyzers (AST, Git, Config, Database, API, Dependency, Tech Stack, Evolution, Polyglot, Vendor) scan any codebase in 300–800ms |
| **Perception Layer** | `cortex/intelligence/perception/` | Pattern registry that scans repositories for known signatures, frameworks, and risk indicators |
| **Reasoning Layer** | `cortex/intelligence/reasoning/` | Strategy selector that weighs historical success rates and context to pick the best approach |
| **Action Layer** | `cortex/intelligence/action/` | Execution planner that converts chosen strategy into step-by-step plans with TDD gates and rollback |
| **DomainBrain** | `cortex/intelligence/domain_brain/` | Business knowledge repository with LENS integration, conflict resolution, and orphan detection |
| **OPJ (Operational Pattern Journal)** | `cortex/intelligence/learning/opj_*.py` | Records success/failure patterns, consults prior patterns before execution, promotes high-confidence patterns to canonical rules |
| **UnifiedIntelligenceProvider** | `cortex/intelligence/provider.py` | Single interface consolidating all intelligence sources (LENS, Knowledge Graph, Profiles, YAMLs) with 3 execution tiers: quick/targeted/full |
| **KnowledgeSynthesisEngine** | `cortex/intelligence/knowledge/` | Merges LENS intelligence + Company knowledge + CORTEX knowledge into a unified context |
| **CompanyKnowledgeProvider** | `cortex/intelligence/knowledge/company_domain_loader.py` | Loads company-specific domain knowledge from `cortex-registry/company/domains/` YAMLs (API design standards, security standards, payment security) |
| **UniversalLearningLoop** | `cortex/intelligence/learning/universal_learning_loop.py` | Cross-session pattern capture — every orchestrator interaction feeds the learning subsystem |
| **Intelligence Matrix** | `cortex/intelligence/cross_cutting/` | 20×20 cross-capability wiring map (IC × CC) ensuring all intelligence subsystems are connected; ≥80% coverage gate enforced |

### 🏗️ Orchestration Engine

27 wired orchestrators across 3 tiers dispatch every request through the right execution path.

| Component | Module | What It Does |
|-----------|--------|-------------|
| **MasterOrchestrator** | `cortex/orchestrators/core/` | Central coordinator — receives classified intent, delegates to domain orchestrators, wired with OPJ |
| **IntentRouter** | `cortex/orchestrators/core/intent_router_impl.py` | LENS-based classification into 10+ intent types (IMPLEMENT, FIX, ANALYZE, REFACTOR, PLAN, AUDIT, etc.) |
| **TDDOrchestrator** | `cortex/orchestrators/core/tdd_orchestrator.py` | Enforces RED → GREEN → REFACTOR cycle; blocks implementation without failing tests first |
| **EnforcementOrchestrator** | `cortex/orchestrators/core/enforcement_orchestrator.py` | Pre-commit governance gate with 10 enforcement agents |
| **RequestRephraseOrchestrator** | `cortex/orchestrators/core/request_rephrase_orchestrator.py` | Stage -1 enrichment with governance context + risk assessment before intent routing |
| **WorkflowEngine** | `cortex/core/workflow_engine.py` | YAML → FSM → ConvergenceLoop runtime; executes workflow templates with convergence gates |
| **StepStateMachine** | `cortex/orchestrators/workflow/step_state_machine.py` | FSM-based step execution: PENDING → RUNNING → CHECKING → PASSED/RETRYING/FAILED/SKIPPED |
| **ConvergenceNeuron** | `cortex/orchestrators/core/convergence_neuron.py` | Evaluates success criteria for each workflow step; loops until convergence or max cycles |
| **ChallengeEngine** | `cortex/orchestrators/validation/challenge_engine.py` | Generates ≥2 alternatives with trade-offs before execution (the `/challenge` command) |
| **RefactoringOrchestrator** | `cortex/orchestrators/domain/refactoring_orchestrator.py` | Semantic refactoring across Python, TypeScript/JavaScript, C#/.NET |
| **SDLCWorkflowOrchestrator** | `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py` | Selects and executes SDLC workflow templates with knowledge context injection |

### 🛡️ Governance & Compliance

35 CORE rules + 2 AC rules enforced at pre-commit, CI, and runtime — governance is not optional.

| Component | Module | What It Does |
|-----------|--------|-------------|
| **CORE Rules** | `cortex-registry/core/tier0-skull/` | 35 immutable rules (CORE-002 through CORE-064) — the "skull" of CORTEX |
| **EnforcementOrchestrator** | `cortex/orchestrators/core/enforcement_orchestrator.py` | Pre-commit gate with 10 enforcement agents; blocks non-compliant changes |
| **SweepCatalogueOrchestrator** | `cortex/orchestrators/support/sweep_catalogue_orchestrator.py` | CORE-064: tracks sweep completeness — no partial sweeps allowed |
| **SOLIDOrchestrator** | `cortex/orchestrators/validation/solid_orchestrator.py` | SOLID principle compliance checker with SQLite audit trail |
| **HolisticValidationOrchestrator** | `cortex/orchestrators/validation/holistic_validation_orchestrator.py` | CORE-048: full validation gate before any IMPLEMENT/FIX/REFACTOR |
| **SecurityVulnerabilityOrchestrator** | `cortex/orchestrators/validation/security_vulnerability_orchestrator.py` | Security vulnerability scanning and risk assessment |
| **TestQualityGate** | `cortex/testing/quality_gate.py` | 7-step algorithm scoring tests 0–9; <7 flagged; identifies KEEP/REVIEW/DELETE |
| **GovernanceAuditor** | `cortex/governance/governance_auditor.py` | Runtime governance violation detection and audit reporting |

### 🔌 MCP Tools — 39 Tools (37 Active)

MCP tools are the external interface — how AI hosts (VS Code Copilot, Claude, Cursor) interact with CORTEX.

| Category | Tools | Purpose |
|----------|-------|---------|
| **Core (4)** | `cortex_process_request`, `cortex_challenge`, `cortex_classify`, `cortex_request_lifecycle` | Request processing, intent classification, challenge generation |
| **Intelligence (6)** | `cortex_lens`, `cortex_knowledge`, `cortex_git`, `cortex_generate_tests`, `cortex_intelligence_matrix`, `cortex_brain_query` | LENS analysis, knowledge retrieval, git intelligence, test generation, matrix querying, brain queries |
| **Governance (4)** | `cortex_governance`, `cortex_validate`, `cortex_load`, `cortex_validate_request` | Rule enforcement, compliance validation, rule loading, request validation |
| **Operations (7)** | `cortex_debug`, `cortex_refactor`, `cortex_plan`, `cortex_onboard`, `cortex_dashboard`, `cortex_workflow`, `cortex_scaffold_files` | Debugging, refactoring, planning, repo onboarding, dashboards, workflow execution, file scaffolding |
| **Utilities (9)** | `cortex_verify`, `cortex_ask`, `cortex_vacuum`, `cortex_tools_catalog`, `cortex_total_recall`, `cortex_metrics`, `cortex_check`, `cortex_vision`, `cortex_orchestrator` | Verification, education, cleanup, tool discovery, recall, metrics, health, vision analysis, orchestrator control |
| **Toolkit (5)** | `cortex_diagnose`, `cortex_verify_env`, `cortex_cleanup`, `cortex_validate_gov`, `cortex_analyze` | Environment diagnostics, setup verification, cleanup, governance validation, code analysis |
| **Specialized (4)** | `cortex_health_scan`, `cortex_vacuum_execute`, `cortex_master_plan`, `cortex_git_push` | Health monitoring, vacuum cleanup, master plan management, git orchestration |
| **Scoring & Quality (1)** | `cortex_score_tests` | Test quality scoring (0–9 scale, 7-step algorithm) |
| **Learning (1)** | `cortex_query_opj` | Query the Operational Pattern Journal for prior patterns and success rates |
| **Discovery (2)** | `cortex_list_workflow_templates`, `cortex_sweep_status` | Workflow template listing, sweep completeness status (CORE-064) |

### 🧠 Intelligence Matrix — 20 × 20 Wiring Map

The Intelligence Matrix ensures every intelligence subsystem (IC) is connected to the right platform capability (CC).

**Intelligence Capabilities (IC-001 through IC-020):**

| ID | Name | Purpose |
|----|------|---------|
| IC-001 | LENS Analysis | 10-analyzer parallel code intelligence |
| IC-002 | SynthesisEngine | Knowledge synthesis across sources |
| IC-003 | DomainBrain | Business knowledge + pattern recognition |
| IC-004 | BrainTier-T1-Learned | Tier 1 learned patterns (persistent memory) |
| IC-005 | BrainTier-T2-Adaptive | Tier 2 adaptive patterns (session-aware) |
| IC-006 | BrainTier-T3-Scratch | Tier 3 scratch patterns (ephemeral) |
| IC-007 | IntelligenceOrchestrator | Cross-cutting intelligence coordination |
| IC-008 | ResponseTemplateGenerator | Structured response formatting |
| IC-009 | BlindSpotDetector | Identifies gaps in analysis coverage |
| IC-010 | KnowledgeIndexer | Indexes knowledge artifacts for retrieval |
| IC-011 | HierarchicalScannerAdapter | Filesystem scanning with depth control |
| IC-012 | KnowledgeIndexerDocGenBridge | Bridge between indexer and doc generation |
| IC-013 | IntelligenceWiringBridges | Cross-subsystem wiring connectors |
| IC-014 | CortexBrainQuery | MCP brain query interface |
| IC-015 | FormatResponseHook | Response formatting hooks |
| IC-016 | KnowledgeSynthesisEngine | Multi-source knowledge merging |
| IC-017 | UnifiedIntelligenceProvider | Single intelligence interface (quick/targeted/full) |
| IC-018 | DomainBrainAPI | Domain brain external API |
| IC-019 | LENSTechStackAnalyzer | Technology stack detection and analysis |
| IC-020 | KnowledgeRegistryProxy | Knowledge registry access proxy |

**CORTEX Capabilities (CC-001 through CC-020):**

| ID | Name | Purpose |
|----|------|---------|
| CC-001 | HierarchicalScanner | Filesystem scanning infrastructure |
| CC-002 | BatchProcessor | Bulk operation processing |
| CC-003 | DomainAdapter | Domain-specific adapters |
| CC-004 | DocGenPlaybook | Documentation generation pipeline |
| CC-005 | AuditFixPipeline | 9-stage audit + auto-fix pipeline |
| CC-006 | EnforcementOrchestrator | Pre-commit governance enforcement |
| CC-007 | VacuumOrchestrator | Markdown sprawl + root clutter cleanup |
| CC-008 | MCPToolRegistry | MCP tool registration and dispatch |
| CC-009 | SweepCatalogueOrchestrator | Sweep completeness contract tracking |
| CC-010 | TDDOrchestrator | Test-driven development enforcement |
| CC-011 | SynthesisEngineBridge | Synthesis engine integration bridge |
| CC-012 | RetrievalOptimizerBridge | Knowledge retrieval optimization |
| CC-013 | TDDStubGenerator | Test stub generation for TDD |
| CC-014 | ResponseTemplateHook | Response template formatting hooks |
| CC-015 | T1T2EnrichmentHooks | Tier 1/Tier 2 memory enrichment |
| CC-016 | OrchestratorProtocolMixin | Base protocol for all 27 orchestrators |
| CC-017 | AuditHashChain | Tamper-proof audit chain |
| CC-018 | CircuitBreaker | Fault tolerance and graceful degradation |
| CC-019 | SQLiteActivityLogger | Persistent activity logging to SQLite |
| CC-020 | MasterOrchestratorCoordinator | Top-level orchestration coordination |

### 📚 Knowledge & Company Context

CORTEX learns and adapts to your company's specific standards, domains, and patterns.

| Component | Location | What It Does |
|-----------|----------|-------------|
| **CompanyKnowledgeProvider** | `cortex/intelligence/knowledge/company_domain_loader.py` | Loads company-specific domain YAMLs (API standards, security, payments) with 5-min TTL cache |
| **KnowledgeRegistryProxy** | `cortex/knowledge/registry_proxy.py` | Proxies access to the knowledge base in `cortex-registry/knowledge-base/` |
| **Company Domains** | `cortex-registry/company/domains/` | YAML definitions for company-specific standards (API design, security, external standards) |
| **Knowledge Base** | `cortex-registry/knowledge-base/` | Architecture patterns, governance rules, repository profiles, security standards |
| **UnifiedIntelligenceContext** | `cortex/intelligence/knowledge/unified_intelligence_context.py` | Combines LENS + Company + CORTEX knowledge into a single context object |
| **BulkDigestOrchestrator** | `cortex/orchestrators/support/bulk_digest_orchestrator.py` | Intelligent markdown ingestion with routing, filtering, and cleanup |
| **RepositoryOnboardingOrchestrator** | `cortex/orchestrators/support/repository_onboarding_orchestrator.py` | LENS analysis + knowledge persistence for new repositories |

### ⚙️ Support & Health

| Component | Module | What It Does |
|-----------|--------|-------------|
| **HealthOrchestrator** | `cortex/orchestrators/health/health_orchestrator.py` | 22 orchestrator health endpoints — the `/health` command |
| **VacuumOrchestrator** | `cortex/orchestrators/health/vacuum_orchestrator.py` | Markdown sprawl + root clutter cleanup — the `/vacuum` command |
| **UpgradeOrchestrator** | `cortex/orchestrators/support/upgrade_orchestrator.py` | Preflight requirements validation, inflight upgrades from origin/main |
| **DebuggerOrchestrator** | `cortex/orchestrators/support/debugger_orchestrator.py` | EventBus-driven debug marker injection and session management |
| **AutoHealingMCPOrchestrator** | `cortex/orchestrators/support/auto_healing_mcp_orchestrator.py` | Self-healing MCP tool registration and fault recovery |
| **GitOrchestrator** | `cortex/orchestrators/git/git_orchestrator.py` | CORE enforcement → sanitization → async git push (replaces GitHub Actions) |
| **TestClassifierOrchestrator** | `cortex/orchestrators/support/test_classifier_orchestrator.py` | Classifies tests by tier (golden, phase, unit, integration) |
| **BLUF System** | `cortex/orchestrators/core/bluf_system.py` | Adaptive Bottom Line Up Front communication (3 response tiers) |

---

## Where to Go Next

| I want to understand… | Read this |
|-----------------------|-----------|
| Core terminology | `00-getting-started/02-key-concepts.md` |
| End-to-end request lifecycle | `00-getting-started/03-how-cortex-works.md` |
| Intelligence architecture | `00-getting-started/04-brain-tier-architecture.md` |
| Quick start (5 minutes) | `00-getting-started/05-quick-start.md` |
| Intelligence Matrix (15×15 wiring) | `00-getting-started/06-intelligence-matrix.md` |
| LENS intelligence details | `02-lens/01-overview.md` |
| Orchestration pipeline | `03-orchestration/01-overview.md` |
| Governance rules | `01-capabilities/05-governance-compliance.md` |
| MCP tools catalog | `04-mcp/03-tools-catalog.md` |
| Full capability inventory | `01-capabilities/01-overview.md` |
| WorkflowEngine FSM runtime | `03-orchestration/11-workflow-engine.md` |

---

*CORTEX v1.0.0 · February 2026 · Phase 79-D Complete · 27 wired orchestrators · 39 MCP tools (37 active) · 35 CORE rules (+ 2 AC) · 16,259 tests · cortex/core: 15 canonical subdirs · Source of truth: `cortex-registry/planning/cortex-refactor-master.yaml`*
