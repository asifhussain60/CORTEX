---
title: Orchestration System
consolidates:
  - 03-orchestration-overview.md
  - 03-orchestration-core-architecture.md
  - 03-orchestration-master-orchestrator.md
  - 03-orchestration-intent-router.md
  - 03-orchestration-end-to-end-flow.md
  - 03-orchestration-cross-orchestrator.md
  - 03-orchestration-request-rephrase.md
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/ + cortex-registry/core/specifications/
audience: [Business Leaders, Product Owners, Software Developers]
---

# Orchestration System

CORTEX has fifty-one wired orchestrators across four canonical tiers, all satisfying the IOrchestrator protocol. Every orchestrator uses OrchestratorProtocolMixin as its base, follows a universal five-step lifecycle, emits AC markers for audit traceability, and communicates exclusively through MasterOrchestrator.

---

## Four-Tier Architecture

The canonical wiring specification lives in `cortex-registry/core/specifications/`.

| Tier | Count | Purpose |
|------|-------|---------|
| **Core** (Tier 1) | 17 | Central coordination, intent routing, TDD enforcement, governance, audit |
| **Domain** (Tier 2) | 7 | Business-vertical specialisation — planning, refactoring, SDLC, dashboards |
| **Support** (Tier 3) | 23 | Onboarding, upgrade, health, vacuum, digest, debug, documentation |
| **Git** (Tier 4) | 4 | Git operations, publishing, sanitisation, pre-commit enforcement |

### Core Tier Orchestrators (17)

MasterOrchestrator, IntentRouter, TDDOrchestrator, WorkflowOrchestrator, EnforcementOrchestrator, ConversationOrchestrator, InteractionOrchestrator, AuditOrchestrator, MasterOrchestrationStage1, MasterOrchestrationStage3, MasterOrchestrationStage4, ResponseOrchestrator, MetaAuditOrchestrator, HolisticValidationOrchestrator, ChallengeEngine, SOLIDOrchestrator, SecurityVulnerabilityOrchestrator.

### Domain Tier Orchestrators (7)

RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator, ServiceDecompositionOrchestrator, SDLCWorkflowOrchestrator, EnhancedPlanningOrchestrator.

### Support Tier Orchestrators (23)

OnboardingOrchestrator, UpgradeOrchestrator, RollbackOrchestrator, SetupOrchestrator, HealthOrchestrator, SweepCatalogueOrchestrator, VacuumOrchestrator, BulkDigestOrchestrator, DigestSessionOrchestrator, DebuggerOrchestrator, UnifiedDiscoveryOrchestrator, UnifiedQualityOrchestrator, AutoHealingMCPOrchestrator, CortexDocsOrchestrator, PlanOrchestrator, RepositoryOnboardingOrchestrator, LENSVisualizationOrchestrator, VSCodeConfigurator, DependencyResolver, RequestRephraseOrchestrator, TrainerOrchestrator, SyncOrchestrator, DocumentationOrchestrator.

### Git Tier Orchestrators (4)

GitOrchestrator, GitPublishOrchestrator, SanitizationOrchestrator, PreCommitEnforcementOrchestrator.

---

## Universal Lifecycle

Every orchestrator satisfies the IOrchestrator protocol via OrchestratorProtocolMixin at `cortex/core/orchestrator_protocol_mixin.py`. The standard lifecycle is:

```
setup() → govern() → execute() → validate() → teardown()
```

The `execute_operation()` method auto-activates cross-cutting hooks (LENS, KnowledgeSynthesis, GovernanceGate). The `execute()` and `run()` methods auto-log ORCHESTRATOR_START and ORCHESTRATOR_END to `.cortex-runtime/audit.db` (SQLite WAL). Audit logging is non-blocking — a failure to log never prevents execution.

OrchestratorBase exists at `cortex/core/orchestrator_base.py` but is only used by two legacy orchestrators. All fifty-one wired orchestrators use IOrchestrator plus OrchestratorProtocolMixin.

---

## MasterOrchestrator — The Executive Coordinator

Location: `cortex/orchestrators/core/master_orchestrator.py`

MasterOrchestrator coordinates all fifty-one wired orchestrators through hierarchical dispatch. It receives enriched requests from the MCP Gateway, invokes IntentRouter for classification, dispatches to the appropriate orchestrator, monitors execution via AC markers, and records the audit trail to `.cortex-runtime/traces/orchestrator-traces.db`.

### Nine-Stage Audit Pipeline

MasterOrchestrator owns and coordinates the `/audit fix` pipeline:

| Stage | Name | Key Component |
|-------|------|---------------|
| −1 | Environment Readiness | UpgradeOrchestrator.validate_requirements() |
| 0 | Inflight Upgrade and Pre-Flight | git fetch origin/main check |
| 1 | Governance Pre-Flight | Full specification validation |
| 2 | 19-Point Production Scan | Checks one through nineteen, including SQLite health |
| 3 | Wiring Contract Validation | Architecture integrity L1 through L3 |
| 4 | Orchestrator Health (all 51 wired) | HealthOrchestrator.run_health_check() |
| 5 | Vacuum Cleanup | VacuumOrchestrator plus cortex_vacuum |
| 6 | Prompt and Agent Meta-Audit | Twenty-three checks |
| 7–8 | Auto-Fix Convergence Loop | detect-fix-rescan-loop until zero P0 and P1 |
| 9 | Tests and AC_COMPLETE | Test suite plus SQLite cleanup |

For complex pipelines, MasterOrchestrator delegates to stage-specific implementations: `master_orchestrator_stage_1.py` (governance audit and pre-flight), `master_orchestrator_stage_3.py` (wiring contract and architecture integrity), and `master_orchestrator_stage_4.py` (orchestrator health endpoints).

---

## IntentRouter — Request Classification

Location: `cortex/orchestrators/core/intent_router.py`

IntentRouter classifies every incoming request into one of twelve or more intent types using LENS-based intelligence. Classification takes twenty to forty milliseconds.

| Intent | Target Orchestrator |
|--------|-------------------|
| IMPLEMENT | TDDOrchestrator |
| FIX | TDDOrchestrator |
| REFACTOR | RefactoringOrchestrator |
| ANALYZE | LENS Synthesis |
| PLAN | PlanningOrchestrator |
| AUDIT | EnforcementOrchestrator |
| DESIGN | Design coordination |
| DEBUG | DebuggerOrchestrator |
| INVESTIGATE | IntelligenceOrchestrator |
| QUERY | Context-dependent routing |
| DIGEST | Digest coordination |
| REPHRASE | RequestRephraseOrchestrator |

---

## RequestRephraseOrchestrator — Automatic Enrichment

Location: `cortex/orchestrators/core/request_rephrase_orchestrator.py`

RequestRephraseOrchestrator runs at Stage minus one — before any other orchestrator sees the request. It enriches the raw user request with relevant CORE governance rules, a breaking-risk assessment, design pillar considerations, and challenge gate flags for high-risk operations. By the time MasterOrchestrator processes the request, it is fully contextualised.

---

## End-to-End Request Flow

A complete request traverses six stages:

**Stage minus one — Request Enrichment** (fifteen to thirty-five milliseconds): RequestRephraseOrchestrator enriches the request with CORE-008 (TDD), CORE-013 (error handling), security context, and breaking-risk assessment.

**Stage zero — MCP Gateway** (five to fifteen milliseconds): Validates JSON-RPC, routes to cortex_process_request, applies Native Tool Gate check.

**Stage one — IntentRouter** (twenty to forty milliseconds): LENS classification determines intent type and routes to the appropriate orchestrator.

**Stage two — LENS Analysis** (three hundred to eight hundred milliseconds): Nine parallel analyzers scan the target module producing AST structure, security findings, metrics, and domain context.

**Stage three — Brain Intelligence** (fifty to two hundred milliseconds): Perception matches architecture patterns, Reasoning selects the optimal strategy, Action produces a step plan with governance gates.

**Stage four — Governance Gate** (under one hundred and fifty milliseconds): Ten enforcement agents validate compliance. Results are PASS, PASS with WARNING, or BLOCKED.

**Stage five — Orchestrator Execution**: The target orchestrator executes the work. For TDDOrchestrator this means RED (write failing test), GREEN (implement to pass), REFACTOR (improve with all tests green).

**Stage six — Result Delivery**: Result delivered inline (CORE-002), audit trail written to CortexAuditDB, AC_COMPLETE marker emitted.

---

## Cross-Orchestrator Communication

Orchestrators never call each other directly. All communication flows through MasterOrchestrator, which ensures that inter-orchestrator communication is auditable, governance gates are checked between handoffs, no circular dependencies exist, and the audit trail captures the complete request path.

| Pattern | Example |
|---------|---------|
| Sequential | IntentRouter then TDDOrchestrator then EnforcementOrchestrator |
| Fan-out | MasterOrchestrator dispatches to multiple analyzers |
| Callback | Orchestrator requests LENS analysis mid-execution |
| Pipeline | RequestRephrase then Intent then TDD then Governance then Audit |

---

## Core Architecture — `cortex/core/`

The `cortex/core/` directory contains fifteen canonical subdirectories:

| Directory | Purpose |
|-----------|---------|
| common/ | Consolidated utilities — timeout profiles, file operations, debug logger, exceptions, thread safety, saga coordinator, validators |
| discovery/ | Repository and file discovery models |
| execution/ | Execution gateway and guards |
| governance/ | Governance enforcer, database, models |
| hallucination_prevention/ | Output validator |
| intelligence/ | Intelligence mixin and routing engine (thin — bulk in `cortex/intelligence/`) |
| intent/ | Intent models (thin — IntentRouter in orchestrators) |
| interaction/ | Interaction models (thin — moved to orchestrators) |
| interfaces/ | IOrchestrator protocol and OperationMode |
| knowledge/ | Knowledge guidance engine |
| models/ | Shared data models |
| orchestrator/ | OrchestratorBase (legacy — two orchestrators only) |
| registry/ | Feature registry |
| security/ | Security models |
| wiring/ | Wiring contracts and specifications |

Import compatibility is maintained by `cortex/core/compatibility_layer.py` — old import paths continue to work.

---

## AC Marker Protocol

Every orchestrator invocation emits AC markers:

```
AC_START: AC-{DOMAIN}-{TIMESTAMP}     ← open session
... orchestrator logic ...
AC_COMPLETE: AC-{DOMAIN}-{TIMESTAMP} ✅  ← close session (ms elapsed)
```

Markers persist to `.cortex-runtime/traces/orchestrator-traces.db`. Schema includes audit_sessions (one row per audit fix run), audit_stage_log (one row per stage), audit_violations (one row per violation), workflow_cycles (one row per detect-fix-rescan iteration), and workflow_runs (one row per loop invocation). No orphaned AC_START without matching AC_COMPLETE is permitted — this is a P0 governance violation.

---

*All orchestrator counts and file paths verified against live codebase — 27 February 2026*

---

## Orchestrator Engagement Visibility (Phase 85 PLANNED)

CORTEX's orchestrators have always emitted detailed audit traces — but those traces lived in SQLite, invisible to users during a session. Phase 85 surfaces engagement through three composable blocks:

| Block | Purpose | When Rendered |
|-------|---------|--------------|
| `BLOCK-ENGAGEMENT-BREADCRUMB` | Routing chain — always visible | Every response |
| `BLOCK-ENGAGEMENT-TIMELINE` | Collapsible orchestrator timing panel | Multi-step operations |
| `BLOCK-PHASE-ROADMAP` | Full phase overview at operation start | `/audit fix`, `/totalrecall`, multi-phase ops |

**Breadcrumb format (example):**
```
Route: IntentRouter → MasterOrchestrator → TDDOrchestrator → EnforcementOrchestrator
```

**Progress format (phase-list+bar — mandatory from Phase 85):**
```
⚙️ [████████░░] 80% — Stage 4 of 5

1. ✅ Environment check       (1.2s)
2. ✅ Governance pre-flight   (3.4s)
3. ✅ LENS analysis           (0.8s)
4. 🔵 Wiring validation       (running…)
5. ⚪ Test gate               —
```

**SSOT:** `.github/templates/cortex-response-templates.md`. No prompt or agent duplicates these rules inline — they pointer-reference the SSOT.

---

## DebuggerOrchestrator — Multi-Stack Debugging (Phase 86 PLANNED)

`DebuggerOrchestrator` at `cortex/orchestrators/support/debugger_orchestrator.py` is an EventBus-driven coordinator that uses a **Strategy Pattern** to apply language-specific debug injection without modifying the orchestrator core.

**Currently live:** 3 Python strategies (`TestFailureStrategy`, `RefactorRegressionStrategy`, `GovernanceViolationStrategy`)  
**Phase 86 adds:** 5 multi-stack strategies (Frontend/HTML-Vision/API/SQL/DotNet) + Vision API + multi-language `AutoCleanupManager` + unified intelligence wiring

**Commands:**
- `/debug {path}` — full cycle: detect stack → inject → capture → analyze → fix-plan
- `/debug-inject {path}` — injection only
- `/debug-cleanup` — production-safe removal of all markers

**Intelligence wiring gaps closed in Phase 86:** OPJMixin (learning persistence), URS signals (reinforcement feedback), IntelligenceMatrix cells CC-021/IC-021, bidirectional EventBus publish, and KnowledgeSynthesisEngine pattern capture.

See `cortex-registry/_cortex-master/phases/planned/phase-86-multi-stack-debug-pipeline.yaml` for the full 16-gap catalogue.
