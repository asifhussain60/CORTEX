# CORTEX Architecture Diagrams

---
title: CORTEX Architecture Diagrams — Visual Reference
type: diagram
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-26
source_of_truth: cortex/ directory structure
consolidates: [07-diagrams-overview, 07-diagrams-high-level-architecture, 07-diagrams-request-flow, 07-diagrams-orchestrator-map, 07-diagrams-lens-pipeline, 07-diagrams-governance-flow, 07-diagrams-mcp-transport, 07-diagrams-testing-pyramid, 07-diagrams-brain-tier-model, 07-diagrams-golden-test-taxonomy]
order: 12
---

> **Complete visual reference** for every major CORTEX subsystem. Each diagram maps to a live implementation path — no hypothetical architecture.

---

## Diagram Index

| # | Diagram | Section |
|---|---------|---------|
| 1 | High-Level System Architecture | [System Architecture](#1-system-architecture) |
| 2 | End-to-End Request Flow | [Request Flow](#2-request-flow) |
| 3 | Orchestrator Hierarchy | [Orchestrator Map](#3-orchestrator-map) |
| 4 | LENS Analysis Pipeline | [LENS Pipeline](#4-lens-pipeline) |
| 5 | Governance Enforcement Flow | [Governance Flow](#5-governance-flow) |
| 6 | MCP stdio Transport | [MCP Transport](#6-mcp-transport) |
| 7 | Testing Pyramid and Execution | [Testing Pyramid](#7-testing-pyramid) |
| 8 | Brain Tier Intelligence Model | [Brain Tiers](#8-brain-tiers) |
| 9 | Golden Test Taxonomy | [Golden Tests](#9-golden-test-taxonomy) |

### Notation Guide

```
┌─────┐   Box: component or layer
│     │
└──┬──┘
   │      Solid line: data flow or control flow
   ▼      Arrow: direction of flow
──→│      Connection: interface or integration point
```

---

## 1. System Architecture

The six-layer architecture from IDE clients down to the configuration registry.

```
┌─────────────────────────────────────────────────────────────────┐
│                        IDE CLIENTS                              │
│         VS Code          Cursor        Claude Desktop           │
└──────────────┬──────────────┬──────────────┬────────────────────┘
               │              │              │
               └──────────────┼──────────────┘
                              │
                    JSON-RPC 2.0 (stdio)
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                    MCP GATEWAY                                  │
│              cortex/mcp/ — 28 registered tools (39 target)              │
│                              │                                  │
│         cortex_request_lifecycle (primary entry point)          │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   ORCHESTRATION LAYER                           │
│                              │                                  │
│    ┌─────────────────────────┼─────────────────────────┐        │
│    │           MasterOrchestrator                      │        │
│    │    (4-stage: Interaction → Intent →                │        │
│    │     Intelligence → Execution)                     │        │
│    └─────────────┬───────────┼───────────┬─────────────┘        │
│                  │           │           │                       │
│    ┌─────────────┴──┐  ┌────┴────┐  ┌───┴──────────┐           │
│    │ IntentRouter   │  │   TDD   │  │   Domain     │           │
│    │ (12 intents)   │  │ Orch.   │  │ Orchestrators│           │
│    └────────────────┘  └─────────┘  └──────────────┘           │
│                                                                 │
│    51 wired orchestrators: 17 core · 7 domain · 23 support · 4 git │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   INTELLIGENCE LAYER                            │
│                              │                                  │
│    ┌──────────────┐    ┌─────┴──────┐    ┌───────────────┐      │
│    │    LENS      │    │   Brain    │    │  Knowledge    │      │
│    │ 10 analyzers │    │  Tiers    │    │  Base         │      │
│    │ 300-800ms    │    │ P→R→A     │    │              │      │
│    └──────────────┘    └───────────┘    └───────────────┘      │
│                                                                 │
│    cortex/intelligence/ + cortex/lens/ + cortex/knowledge/      │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   GOVERNANCE LAYER                              │
│                              │                                  │
│    ┌──────────────┐    ┌─────┴──────┐    ┌───────────────┐      │
│    │ 38 Active    │    │Enforcement │    │   Audit DB    │      │
│    │ CORE Rules   │    │ Agents     │    │  (SQLite WAL) │      │
│    └──────────────┘    └───────────┘    └───────────────┘      │
│                                                                 │
│    cortex/governance/ + cortex-registry/core/                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                          │
│                              │                                  │
│    ┌─────────┐  ┌────────┐  ┌──────┐  ┌──────────┐  ┌───────┐  │
│    │ Tracing │  │Metrics │  │Cache │  │Resilience│  │Security│ │
│    │OTel    │  │Prom.  │  │Mgr  │  │CircuitBr.│  │Redact. │ │
│    └─────────┘  └────────┘  └──────┘  └──────────┘  └───────┘  │
│                                                                 │
│    cortex/infrastructure/ (50+ modules)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                   REGISTRY (Configuration)                      │
│                              │                                  │
│    cortex-registry/                                             │
│    ├── core/tier0-skull/ ← skull-rules.yaml (CORE rules, YAML) │
│    ├── patterns/          ← 9 enterprise patterns               │
│    ├── workflows/         ← Lifecycle + production templates    │
│    ├── planning/          ← Master plan index                   │
│    └── knowledge-base/    ← Domain knowledge                    │
└─────────────────────────────────────────────────────────────────┘
```

### Component Counts

| Layer | Components | Location |
|-------|------------|----------|
| MCP Gateway | 28 registered tools (39 target) | `cortex/mcp/tools/` |
| Orchestration | 51 wired orchestrators (17 core, 7 domain, 23 support, 4 git) | `cortex/orchestrators/` |
| Intelligence | 15 LENS analyzers + brain tiers | `cortex/lens/` + `cortex/intelligence/` |
| Governance | 38 CORE rules | `cortex/governance/` + `cortex-registry/core/` |
| Infrastructure | 50+ modules | `cortex/infrastructure/` |
| Registry | Rules, patterns, workflows | `cortex-registry/` |
| Tests | 16,942 collected | `tests/` |

---

## 2. Request Flow

The MasterOrchestrator 4-stage pipeline — every request traverses this path.

```
                    USER REQUEST
                    "Implement user auth"
                         │
                         ▼
┌────────────────────────────────────────────┐
│  STAGE 1: INTERACTION                      │
│  ┌──────────────────────────────────────┐  │
│  │  Display Definition of Ready (DoR)   │  │
│  │  ┌────────────────────────────────┐  │  │
│  │  │ • Scope clear?                 │  │  │
│  │  │ • Acceptance criteria defined? │  │  │
│  │  │ • Dependencies identified?     │  │  │
│  │  └────────────────────────────────┘  │  │
│  │  Await user approval                 │  │
│  └──────────────────────────────────────┘  │
└───────────────────┬────────────────────────┘
                    │ approved
                    ▼
┌────────────────────────────────────────────┐
│  STAGE 2: INTENT CLASSIFICATION            │
│  ┌──────────────────────────────────────┐  │
│  │  IntentRouter analyzes request       │  │
│  │                                      │  │
│  │  Input: "Implement user auth"        │  │
│  │  Output: IMPLEMENT (confidence: 0.95)│  │
│  │                                      │  │
│  │  12 intent types:                    │  │
│  │  IMPLEMENT, FIX, REFACTOR, ANALYZE,  │  │
│  │  TEST, DEBUG, ONBOARD, EXPLAIN,      │  │
│  │  REVIEW, DEPLOY, SECURITY, WORKFLOW  │  │
│  └──────────────────────────────────────┘  │
└───────────────────┬────────────────────────┘
                    │ intent: IMPLEMENT
                    ▼
┌────────────────────────────────────────────┐
│  STAGE 3: INTELLIGENCE PREFETCH            │
│  ┌──────────────────────────────────────┐  │
│  │  LENS Analysis (10 parallel analyzers)│  │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌─────────┐   │  │
│  │  │AST │ │Git │ │Imp │ │Security │   │  │
│  │  └────┘ └────┘ └────┘ └─────────┘   │  │
│  │  ┌─────┐ ┌────┐ ┌─────┐ ┌──────┐   │  │
│  │  │Commt│ │Patn│ │Metrc│ │Domain│   │  │
│  │  └─────┘ └────┘ └─────┘ └──────┘   │  │
│  │                                      │  │
│  │  → Synthesis → Confidence score      │  │
│  │  → 300-800ms total                   │  │
│  └──────────────────────────────────────┘  │
└───────────────────┬────────────────────────┘
                    │ LENS context ready
                    ▼
┌────────────────────────────────────────────┐
│  STAGE 4: EXECUTION                        │
│  ┌──────────────────────────────────────┐  │
│  │  Route to TDDOrchestrator            │  │
│  │                                      │  │
│  │  TDD Cycle:                          │  │
│  │  ┌─────┐   ┌───────┐   ┌──────────┐ │  │
│  │  │ RED │ → │ GREEN │ → │ REFACTOR │ │  │
│  │  │Write│   │Impl.  │   │Clean up  │ │  │
│  │  │test │   │minimum│   │all pass  │ │  │
│  │  └─────┘   └───────┘   └──────────┘ │  │
│  │                                      │  │
│  │  Governance gates enforced           │  │
│  │  Audit trail recorded                │  │
│  │  Result returned to user             │  │
│  └──────────────────────────────────────┘  │
└───────────────────┬────────────────────────┘
                    │
                    ▼
              STRUCTURED RESPONSE
              ┌──────────────────┐
              │ • Implementation │
              │ • Tests written  │
              │ • Tests passing  │
              │ • Audit ID       │
              └──────────────────┘
```

### Intent Routing Map

```
IntentRouter
    │
    ├── IMPLEMENT ──→ TDDOrchestrator
    ├── FIX ────────→ TDDOrchestrator
    ├── REFACTOR ───→ RefactoringOrchestrator
    ├── ANALYZE ────→ LENSSynthesis
    ├── TEST ───────→ TDDOrchestrator
    ├── DEBUG ──────→ DebugOrchestrator
    ├── ONBOARD ────→ OnboardingOrchestrator
    ├── EXPLAIN ────→ ExplanationOrchestrator
    ├── REVIEW ─────→ ReviewOrchestrator
    ├── DEPLOY ─────→ DeploymentOrchestrator
    ├── SECURITY ───→ SecurityOrchestrator
    └── WORKFLOW ───→ WorkflowOrchestrator
```

---

## 3. Orchestrator Map

51 wired orchestrators across 4 tiers, all satisfying the IOrchestrator protocol.

```
cortex/orchestrators/
├── core/       ← 17 wired entry points (MasterOrchestrator, IntentRouter, TDD…)
├── domain/     ← 7 wired domain orchestrators (Refactoring, Planning, Domain…)
├── support/    ← 23 wired support orchestrators (Onboarding, Health, Sweep…)
└── git/        ← 4 wired git orchestrators (Git, GitPublish, PreCommit, Sanitization)
```

### Orchestrator Hierarchy

```
OrchestratorProtocolMixin (cortex/core/orchestrator_protocol_mixin.py)
    │  51 wired orchestrators satisfy the IOrchestrator protocol
    │  Auto-logs every execute()/run() call to .cortex-runtime/audit.db (SQLite WAL)
    │
    ├── CORE TIER (17 wired)
    │   ├── MasterOrchestrator          ← Entry point, 4-stage pipeline
    │   ├── IntentRouter                ← 12+ intent classification (20–40ms)
    │   ├── TDDOrchestrator             ← RED → GREEN → REFACTOR
    │   ├── WorkflowOrchestrator        ← WorkflowEngine.load()/execute_step()
    │   ├── EnforcementOrchestrator     ← Governance rule enforcement
    │   ├── ConversationOrchestrator    ← Multi-turn conversation management
    │   ├── InteractionOrchestrator     ← User interaction flows
    │   ├── AuditOrchestrator           ← 19-point production scan
    │   ├── ResponseOrchestrator        ← Response formatting
    │   ├── MetaAuditOrchestrator       ← 23-check meta-audit
    │   ├── HolisticValidationOrchestrator ← CORE-048 gate
    │   ├── ChallengeOrchestrator       ← Alternative generation
    │   ├── SOLIDOrchestrator           ← Design principle compliance
    │   ├── SecurityOrchestrator        ← Vulnerability scanning
    │   ├── Stage1Orchestrator          ← Pipeline stage 1
    │   ├── Stage3Orchestrator          ← Pipeline stage 3
    │   └── Stage4Orchestrator          ← Pipeline stage 4
    │
    ├── DOMAIN TIER (7 wired)
    │   ├── RefactoringOrchestrator     ← Semantic refactoring (Python, TS, C#)
    │   ├── PlanningOrchestrator        ← Decomposition and gap catalogues
    │   ├── DomainOrchestrator          ← Domain-specific business logic
    │   ├── DashboardOrchestrator       ← Dashboard generation
    │   ├── SDLCWorkflowOrchestrator    ← Lifecycle template execution
    │   ├── EnhancedPlanningOrchestrator ← ROI scoring and wave decomposition
    │   └── ServiceDecompositionOrchestrator ← Service decomposition
    │
    ├── SUPPORT TIER (23 wired)
    │   ├── OnboardingOrchestrator      ← Repository onboarding (LENS analysis)
    │   ├── UpgradeOrchestrator         ← Upgrade lifecycle management
    │   ├── RollbackOrchestrator        ← Rollback & recovery
    │   ├── SetupOrchestrator           ← Environment setup
    │   ├── HealthOrchestrator          ← System health monitoring
    │   ├── SweepCatalogueOrchestrator  ← CORE-064 sweep completeness (SQLite WAL)
    │   ├── VacuumOrchestrator          ← Markdown sprawl cleanup
    │   ├── BulkDigestOrchestrator      ← Bulk content ingestion
    │   ├── DigestSessionOrchestrator   ← Digest session management
    │   ├── DebuggerOrchestrator        ← Debug session coordination
    │   ├── UnifiedDiscoveryOrchestrator ← Repository discovery
    │   ├── UnifiedQualityOrchestrator  ← Quality gate enforcement
    │   ├── AutoHealingMCPOrchestrator  ← MCP auto-healing
    │   ├── CortexDocsOrchestrator      ← Documentation generation
    │   └── ... (additional support orchestrators)
    │
    └── GIT TIER (4 wired)
        ├── GitOrchestrator             ← Commit, branch, merge, diff
        ├── GitPublishOrchestrator      ← Structured commit and push
        ├── PreCommitEnforcementOrchestrator ← CORE rule validation at commit
        └── SanitizationOrchestrator    ← Secret scanning and PII removal
```

### Cross-Orchestrator Communication

```
┌──────────────────┐     ┌──────────────────┐
│ MasterOrchestrator│────→│  IntentRouter    │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         │  routes to             │ classifies
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│ TDDOrchestrator  │◄───→│ LENS Analysis    │
└────────┬─────────┘     └──────────────────┘
         │
         │  enforces
         ▼
┌──────────────────┐     ┌──────────────────┐
│   Enforcement    │────→│  Audit DB        │
│   Orchestrator   │     │  (SQLite WAL)    │
└──────────────────┘     └──────────────────┘
```

All inter-orchestrator messaging uses the **OrchestratorEventBus** (`cortex/infrastructure/orchestrator_event_bus.py`) for decoupled communication.

---

## 4. LENS Pipeline

10-analyzer parallel pipeline producing unified code intelligence in 300–800ms.

### Parallel Dispatch

```
                    SOURCE CODE INPUT
                         │
                         ▼
            ┌────────────────────────┐
            │    LENS Controller     │
            │    cortex/lens/        │
            └────────────┬───────────┘
                         │
            ┌────────────┴───────────┐
            │   PARALLEL DISPATCH    │
            │   (all 10 concurrent)  │
            └────────────┬───────────┘
                         │
  ┌──────┬──────┬──────┬─┴──┬──────┬──────┬──────┬──────┬──────┐
  ▼      ▼      ▼      ▼    ▼      ▼      ▼      ▼      ▼      ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌─────┐
│AST │ │Git │ │Cmnt│ │Impt││Sec │ │Patn│ │Mtrc│ │Domn│ │Tech│ │Extra│
│    │ │Hist│ │    │ │    ││    │ │    │ │    │ │    │ │Stk │ │     │
└──┬─┘ └──┬─┘ └──┬─┘ └──┬─┘└──┬─┘ └──┬─┘ └──┬─┘ └──┬─┘ └──┬─┘ └──┬──┘
   │      │      │      │     │      │      │      │      │      │
   └──────┴──────┴──────┴─────┴──────┴──────┴──────┴──────┴──────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │      SYNTHESIS         │
                 │                        │
                 │  Merge 10 analyzer     │
                 │  results into unified  │
                 │  intelligence report   │
                 │                        │
                 │  • Confidence score    │
                 │  • Risk assessment     │
                 │  • Recommendations     │
                 │  • Cross-references    │
                 └────────────┬───────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │   CACHE (optional)     │
                 │   TTL-based storage    │
                 │   Skip if cached       │
                 └────────────┬───────────┘
                              │
                              ▼
                    LENS ANALYSIS RESULT
                    (300-800ms total)
```

### Analyzer Matrix

```
┌──────────────────────────────────────────────────────────┐
│                    ANALYZER MATRIX                       │
├─────────────┬────────────────────────────────────────────┤
│ Analyzer    │ Extracts                                   │
├─────────────┼────────────────────────────────────────────┤
│ AST         │ Classes, functions, inheritance, complexity │
│ Git History │ Commit frequency, authors, churn rate       │
│ Comment     │ Documentation quality, TODO/FIXME count     │
│ Import      │ Dependency graph, circular imports          │
│ Security    │ Vulnerabilities, secret patterns, CVEs      │
│ Pattern     │ Design patterns, anti-patterns detected     │
│ Metrics     │ Lines, complexity, duplication ratio         │
│ Domain      │ Business domain knowledge alignment         │
│ Tech Stack  │ Framework detection, language fingerprint   │
│ Extended    │ Additional context-specific analysis        │
└─────────────┴────────────────────────────────────────────┘
```

### LENS Acronym

```
L ─── Language    → AST analysis, syntax understanding
E ─── Examination → Deep code inspection (metrics, patterns)
N ─── Navigation  → Dependency graph, import chains
S ─── Synthesis   → Merge all findings into actionable report
```

---

## 5. Governance Flow

Three-layer enforcement ensuring every code change meets CORTEX standards.

```
                    CODE CHANGE
                         │
                         ▼
┌────────────────────────────────────────────────┐
│  LAYER 1: PRE-COMMIT                           │
│                                                │
│  pre_commit_validator.py                       │
│  ┌──────────────────────────────────────────┐  │
│  │ CORE-011: Type hints present?            │  │
│  │ CORE-012: Docstrings on public APIs?     │  │
│  │ CORE-028: File names snake_case?         │  │
│  │ CORE-035: No duplicate implementations?  │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ❌ Fail → Block commit                        │
│  ✅ Pass → Continue                            │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│  LAYER 2: CI PIPELINE                          │
│                                                │
│  EnforcementOrchestrator                       │
│  ┌──────────────────────────────────────────┐  │
│  │ All 38 active CORE rules evaluated       │  │
│  │ 10 enforcement agents execute            │  │
│  │                                          │  │
│  │ Agents:                                  │  │
│  │ ├── TestNamingAgent                      │  │
│  │ ├── FileNamingAgent                      │  │
│  │ ├── ImportValidationAgent                │  │
│  │ ├── TypeHintAgent                        │  │
│  │ ├── DocstringAgent                       │  │
│  │ ├── DuplicateDetectionAgent              │  │
│  │ ├── SecurityScanAgent                    │  │
│  │ └── ExtendedGovernanceAgent              │  │
│  │      (CORE-058 through CORE-063)         │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ❌ Fail → Block merge                         │
│  ✅ Pass → Continue                            │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│  LAYER 3: RUNTIME                              │
│                                                │
│  MasterOrchestrator Stage 4                    │
│  ┌──────────────────────────────────────────┐  │
│  │ CORE-002: Output inline (no .md files)   │  │
│  │ CORE-008: TDD enforced (test first)      │  │
│  │ CORE-048: Holistic validation gate       │  │
│  │ CORE-049: Silent autonomous execution    │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  All violations → CortexAuditDB                │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────┐
│  AUDIT TRAIL                                   │
│                                                │
│  CortexAuditDB (SQLite WAL)                    │
│  ┌──────────────────────────────────────────┐  │
│  │ • Timestamp                              │  │
│  │ • Rule ID (CORE-nnn)                     │  │
│  │ • Violation type                         │  │
│  │ • File path                              │  │
│  │ • Remediation applied                    │  │
│  │ • Hash chain (tamper-evident)            │  │
│  └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

### Active CORE Rules (subset)

```
┌─────────┬──────────────────────────────────────────────┐
│ Rule    │ Enforcement                                  │
├─────────┼──────────────────────────────────────────────┤
│ CORE-001│ Standard project structure                   │
│ CORE-002│ All output inline — no report files          │
│ CORE-005│ Conventional commit messages                 │
│ CORE-008│ TDD mandatory — test first                   │
│ CORE-011│ Type hints on all functions                  │
│ CORE-012│ Docstrings on all public APIs                │
│ CORE-013│ Error handling standards                     │
│ CORE-028│ File naming: snake_case only                 │
│ CORE-035│ Single canonical — no duplicates             │
│ CORE-048│ Holistic validation gate                     │
│ CORE-049│ Silent autonomous execution                  │
│ CORE-058│ Extended governance (ExtendedGovernanceAgent) │
│ …       │ + additional rules in skull-rules.yaml       │
└─────────┴──────────────────────────────────────────────┘
```

---

## 6. MCP Transport

Pylance-style stdio transport — auto-starts with VS Code, no manual server startup required.

```
┌─────────────────────────────────────────────────────────┐
│                    VS CODE                              │
│                                                         │
│  ┌──────────────────┐     ┌──────────────────────────┐  │
│  │   Copilot Chat   │     │  .vscode/settings.json   │  │
│  │                  │     │  mcpServers.cortex:       │  │
│  │  User types:     │     │    command: python3       │  │
│  │  "Implement      │     │    args: [-m, cortex.mcp] │  │
│  │   user auth"     │     │    transport: stdio       │  │
│  └────────┬─────────┘     └──────────────────────────┘  │
│           │                                             │
│           │ 1. Generate tool call                       │
│           ▼                                             │
│  ┌──────────────────┐                                   │
│  │  MCP Client      │                                   │
│  │  (in VS Code)    │                                   │
│  └────────┬─────────┘                                   │
└───────────┼─────────────────────────────────────────────┘
            │
            │ 2. JSON-RPC 2.0 over stdin
            │
            │  {"jsonrpc":"2.0","method":"tools/call",
            │   "params":{"name":"cortex_process_request",
            │   "arguments":{"operation":"implement",
            │   "request":"user auth"}},"id":1}
            │
            ▼
┌───────────────────────────────────────────────────────┐
│                 MCP SERVER PROCESS                     │
│           python3 -m cortex.mcp                       │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  stdin reader → JSON-RPC parser                 │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                  │
│                    ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Tool Registry → Find "cortex_process_request"  │  │
│  │  Validate parameters                            │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                  │
│                    ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  CortexProcessRequest.execute(args)             │  │
│  │  → MasterOrchestrator 4-stage pipeline          │  │
│  │  → IntentRouter → TDDOrchestrator               │  │
│  │  → Governance + Audit                           │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                  │
│                    ▼                                  │
│  ┌─────────────────────────────────────────────────┐  │
│  │  ToolResult → JSON-RPC response                 │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                  │
└────────────────────┼──────────────────────────────────┘
                     │
                     │ 3. JSON-RPC 2.0 over stdout
                     │
                     │  {"jsonrpc":"2.0","result":{
                     │   "content":[{"type":"text",
                     │   "text":"Implementation complete..."}]
                     │  },"id":1}
                     │
                     ▼
┌───────────────────────────────────────────────────────┐
│                    VS CODE                            │
│  ┌──────────────────┐                                 │
│  │   Copilot Chat   │                                 │
│  │                  │                                 │
│  │  Displays result │                                 │
│  │  to user         │                                 │
│  └──────────────────┘                                 │
└───────────────────────────────────────────────────────┘
```

### Lifecycle Management

```
VS Code Opens Workspace
    │
    ├── 1. Read .vscode/settings.json
    ├── 2. Find mcpServers.cortex config
    ├── 3. Spawn: python3 -m cortex.mcp
    ├── 4. Connect stdin/stdout
    ├── 5. Send tools/list → receive 28 tools (registered)
    │
    │   [normal operation — tool calls as needed]
    │
    ├── 6. VS Code closes
    └── 7. MCP server process terminates
```

---

## 7. Testing Pyramid

16,942 tests collected across layered execution tiers with parallel support.

### Test Pyramid

```
                        ▲
                       ╱ ╲
                      ╱   ╲
                     ╱     ╲
                    ╱ Golden ╲
                   ╱  Tests   ╲
                  ╱  (486 must ╲
                 ╱  ALWAYS pass)╲
                ╱────────────────╲
               ╱                  ╲
              ╱  Integration Tests ╲
             ╱  (cross-component)   ╲
            ╱────────────────────────╲
           ╱                          ╲
          ╱     ~15,000 Unit Tests     ╲
         ╱      (module-level)          ╲
        ╱────────────────────────────────╲
       ╱                                  ╲
      ╱        Smoke Tests (subset)        ╲
     ╱──────────────────────────────────────╲

  Total: 16,942 collected (all tiers including golden/phase)
```

### Execution Strategy

```
┌───────────────────────────────────────────────────────────────┐
│                    TEST EXECUTION MODES                       │
├─────────────┬──────────────┬─────────────────────────────────┤
│ Tier        │ Execution    │ Configuration                   │
├─────────────┼──────────────┼─────────────────────────────────┤
│ Smoke       │ Parallel     │ -m smoke -n auto --dist loadfile│
│ Unit        │ Parallel     │ -n auto --dist loadscope        │
│ Integration │ Parallel (4) │ -n 4 --dist loadfile            │
│ Golden      │ Serial       │ -p no:xdist (deterministic)     │
│ Full Suite  │ Parallel     │ -n auto --dist loadscope        │
│ Debug       │ Serial       │ -p no:xdist --tb=long -v -s     │
└─────────────┴──────────────┴─────────────────────────────────┘
```

### TestQualityGate Scoring

```
Score = Impact + Likelihood + Detection + Efficiency - Maintenance

┌──────────────┬─────────┬────────────────────────────────────┐
│ Factor       │ Range   │ Measures                           │
├──────────────┼─────────┼────────────────────────────────────┤
│ Impact       │ 0-3     │ Business impact if test missing    │
│ Likelihood   │ 0-2     │ Probability of catching real bugs  │
│ Detection    │ 0-2     │ Early detection value              │
│ Efficiency   │ 0-2     │ Execution speed & reliability      │
│ Maintenance  │ 0-2     │ Cost to maintain (subtracted)      │
├──────────────┼─────────┼────────────────────────────────────┤
│ Total        │ 0-9     │ Higher = better test               │
└──────────────┴─────────┴────────────────────────────────────┘

Score Interpretation:
  7-9  ★★★  Essential — high-impact, efficient
  4-6  ★★   Good — solid coverage value
  1-3  ★    Review — may need improvement
  0    ✗    Consider removing or rewriting
```

### TDD Cycle (CORE-008)

```
  ┌─────────┐         ┌─────────┐         ┌──────────────┐
  │         │         │         │         │              │
  │   RED   │ ──────→ │  GREEN  │ ──────→ │   REFACTOR   │
  │         │         │         │         │              │
  │ Write   │         │ Write   │         │ Clean up     │
  │ failing │         │ minimum │         │ with all     │
  │ test    │         │ code to │         │ tests        │
  │         │         │ pass    │         │ passing      │
  └────┬────┘         └─────────┘         └──────┬───────┘
       │                                         │
       └─────────────────────────────────────────┘
                    repeat cycle
```

### Test Directory Structure

```
tests/
├── api/                  ← API layer tests
├── chaos/                ← Chaos engineering tests
├── cli/                  ← CLI interface tests
├── core/                 ← Core module tests
├── domain_orchestrators/ ← Domain orchestrator tests
├── golden/               ← 486 golden tests (regression-proof)
├── governance/           ← Governance rule tests
├── infrastructure/       ← Infrastructure layer tests
├── integration/          ← Cross-component integration tests
├── intelligence/         ← Intelligence layer tests
├── knowledge/            ← Knowledge base tests
├── lens/                 ← LENS analyzer tests
├── mcp/                  ← MCP tool tests
├── models/               ← Data model tests
├── observability/        ← Observability tests
├── orchestrators/        ← Orchestrator tests
├── regression/           ← Regression tests
├── secrets/              ← Secret management tests
├── templates/            ← Template tests
├── testing/              ← Test framework meta-tests
├── tools/                ← Tool tests
└── fixtures/             ← Shared test fixtures
```

---

## 8. Brain Tiers

Three-tier cognitive architecture: Perception → Reasoning → Action.

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  TIER 3: ACTION                                             │
│  cortex/intelligence/action/                                │
│                                                             │
│  "Motor Cortex" — Executes decisions                        │
│                                                             │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Code Gen  │  │ Test Gen     │  │ Refactoring Exec.    │  │
│  │ (write)   │  │ (test first) │  │ (transform)          │  │
│  └───────────┘  └──────────────┘  └──────────────────────┘  │
│                                                             │
│  Receives: Reasoned plan + context                          │
│  Produces: Code, tests, transformations                     │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▲
                          │ plans & decisions
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                                                             │
│  TIER 2: REASONING                                          │
│  cortex/intelligence/reasoning/                             │
│                                                             │
│  "Prefrontal Cortex" — Analyzes, plans, decides             │
│                                                             │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Intent    │  │ Risk         │  │ Strategy             │  │
│  │ Analysis  │  │ Assessment   │  │ Selection            │  │
│  └───────────┘  └──────────────┘  └──────────────────────┘  │
│                                                             │
│  Receives: Structured perceptions from Tier 1               │
│  Produces: Plans, strategies, routing decisions             │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▲
                          │ structured perceptions
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                                                             │
│  TIER 1: PERCEPTION                                         │
│  cortex/intelligence/perception/                            │
│                                                             │
│  "Sensory Cortex" — Observes, parses, classifies            │
│                                                             │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ LENS      │  │ Code         │  │ Natural Language     │  │
│  │ Analysis  │  │ Parsing      │  │ Understanding        │  │
│  │ (10 anlyz)│  │ (AST)        │  │ (intent)             │  │
│  └───────────┘  └──────────────┘  └──────────────────────┘  │
│                                                             │
│  Receives: Raw input (code, text, requests)                 │
│  Produces: Structured observations                          │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▲
                          │
                    RAW INPUT
              (code, text, requests)
```

### Intelligence Subsystems

```
cortex/intelligence/
├── perception/       ← Tier 1: Observe & parse
├── reasoning/        ← Tier 2: Analyze & plan
├── action/           ← Tier 3: Execute & transform
├── domain_brain/     ← Domain-specific knowledge
├── learning/         ← Learning from past executions
├── knowledge/        ← Knowledge base management
├── lens/             ← LENS integration layer
├── infrastructure/   ← Intelligence infrastructure
├── governance/       ← Intelligence governance
├── documentation/    ← Documentation intelligence
├── crawler/          ← Code crawling & indexing
├── quality/          ← Quality assessment
├── observability/    ← Intelligence observability
└── wiring/           ← Cross-tier integration
```

### Learning Loop

```
┌────────────────────────────────────────────────┐
│                                                │
│  1. PERCEIVE → Code input analyzed by LENS     │
│                    │                           │
│  2. REASON  → IntentRouter classifies,         │
│                TDDOrchestrator plans            │
│                    │                           │
│  3. ACT     → Code generated, tests written    │
│                    │                           │
│  4. LEARN   → Outcome recorded in AuditDB      │
│                    │                           │
│  5. ADAPT   → Future perceptions enriched      │
│                by past outcomes                │
│                    │                           │
│  └────────────────┘ (continuous loop)          │
│                                                │
└────────────────────────────────────────────────┘
```

### Brain Analogy Summary

| Tier | Brain Region | Function | CORTEX Module |
|------|-------------|----------|---------------|
| Perception | Sensory cortex | See, hear, feel | `cortex/intelligence/perception/` |
| Reasoning | Prefrontal cortex | Think, plan, decide | `cortex/intelligence/reasoning/` |
| Action | Motor cortex | Move, build, execute | `cortex/intelligence/action/` |
| Learning | Hippocampus | Remember, adapt | `cortex/intelligence/learning/` |
| Knowledge | Long-term memory | Know, recall | `cortex/intelligence/knowledge/` |
| Domain | Specialized areas | Expert knowledge | `cortex/intelligence/domain_brain/` |

---

## 9. Golden Test Taxonomy

486 golden tests organised into canonical subfolders under `tests/golden/`.

### Canonical Subfolder Structure

```
tests/golden/
├── architecture/         ← Intelligence tier structure, OrchestratorMixin health
├── audit_trail/          ← AC_START/AC_COMPLETE marker completeness
├── governance/           ← CORE rule enforcement, stale construct absence
├── integration/          ← E2E routing, MCP tool calls, LENS pipeline
├── registry/             ← YAML audit: intelligence package, registry correctness
├── synthesis/            ← Knowledge synthesis, canonical import paths
├── workflow/             ← Workflow template E2E, trace chains, response rendering
├── holistic_integration/ ← Full scenario suite (high complexity)
├── orchestrators/        ← Per-orchestrator truth tests
├── production/           ← Production readiness checks
├── routing/              ← Intent routing differentiation tests
├── onboarding/           ← Repository onboarding E2E tests
├── knowledge_graph/      ← KG indexing and inference truth tests
├── agents/               ← Agent-level golden verifications
└── regression/           ← Regression baselines
```

### Naming Convention

All golden test files follow `test_<domain>_<concern>_truth.py` or `test_<concern>_golden.py`. Snake_case only (CORE-028).

### Scoring Dimensions (v2.0)

```
┌────────────────┬─────────┬───────────────────────────────────────┐
│ Dimension      │ Range   │ Measures                              │
├────────────────┼─────────┼───────────────────────────────────────┤
│ Impact         │ 0–5     │ Security, reliability, business       │
│ Likelihood     │ 0–3     │ Orchestration density, integration    │
│ Detection      │ 0–3     │ Data correctness, observability       │
│ Efficiency     │ 0–2     │ Lines per test, asserts per test      │
│ Maintenance    │ 0– -2   │ Mock ratio, stub ratio (penalty)      │
├────────────────┼─────────┼───────────────────────────────────────┤
│ KEEP threshold │ ≥ 7     │ Promoted to GOLDEN tier               │
│ REVIEW         │ 4–6     │ May need improvement                  │
│ DELETE         │ < 4     │ Consider removing or rewriting        │
└────────────────┴─────────┴───────────────────────────────────────┘
```

### Promotion Pipeline

New tests are promoted to GOLDEN tier by `TestClassifierOrchestrator` (CORE-055):
- Must match `tests/golden/` path pattern
- Must score ≥ 7 on quality gate
- Must have ≥ 2 orchestrator references
- Must have ≥ 2 asserts per test function

Governance template: `cortex-registry/workflows/templates/governance/golden-test-promotion.yaml`

---

*All diagrams verified against live codebase · February 2026*
