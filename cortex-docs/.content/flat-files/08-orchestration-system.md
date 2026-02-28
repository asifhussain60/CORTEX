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
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/ + cortex-registry/core/specifications/
audience: [Business Leaders, Product Owners, Software Developers]
---

# Orchestration System

CORTEX has 259 orchestrator files across 9 domains (core:102, domain:28, support:51, git:4, health:27, intelligence:16, persona:6, validation:12, workflow:6), all satisfying the IOrchestrator protocol. Every orchestrator uses OrchestratorProtocolMixin as its base, follows a universal five-step lifecycle, emits AC markers for audit traceability, and communicates exclusively through MasterOrchestrator.

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

OrchestratorBase exists at `cortex/core/orchestrator_base.py` but is only used by two legacy orchestrators. All wired orchestrators use IOrchestrator plus OrchestratorProtocolMixin.

---

## MasterOrchestrator — The Executive Coordinator

Location: `cortex/orchestrators/core/master_orchestrator.py`

MasterOrchestrator coordinates all wired orchestrators through hierarchical dispatch. It receives enriched requests from the MCP Gateway, invokes IntentRouter for classification, dispatches to the appropriate orchestrator, monitors execution via AC markers, and records the audit trail to `.cortex-runtime/traces/orchestrator-traces.db`.

### Nine-Stage Audit Pipeline

MasterOrchestrator owns and coordinates the `/audit fix` pipeline:

| Stage | Name | Key Component |
|-------|------|---------------|
| −1 | Environment Readiness | UpgradeOrchestrator.validate_requirements() |
| 0 | Inflight Upgrade and Pre-Flight | git fetch origin/main check |
| 1 | Governance Pre-Flight | Full specification validation |
| 2 | 19-Point Production Scan | Checks one through nineteen, including SQLite health |
| 3 | Wiring Contract Validation | Architecture integrity L1 through L3 |
| 4 | Orchestrator Health | HealthOrchestrator.run_health_check() |
| 5 | Vacuum Cleanup | VacuumOrchestrator plus cortex_vacuum |
| 6 | Prompt and Agent Meta-Audit | Twenty-three checks |
| 7–8 | Auto-Fix Convergence Loop | detect-fix-rescan-loop until zero P0 and P1 |
| 9 | Tests and AC_COMPLETE | Test suite plus SQLite cleanup |

For complex pipelines, MasterOrchestrator delegates to stage-specific implementations: `master_orchestrator_stage_1.py` (governance audit and pre-flight), `master_orchestrator_stage_3.py` (wiring contract and architecture integrity), and `master_orchestrator_stage_4.py` (orchestrator health endpoints).

---

## IntentRouter — Request Classification

Location: `cortex/orchestrators/core/intent_router.py`

IntentRouter classifies every incoming request into one of twenty-eight intent types using a 4-stage pipeline: InteractionOrchestrator (Stage 1 — LENS per-turn comprehension), IntentRouter (Stage 2 — classification), WorkflowComplexityRouter (Stage 3 — technology-aware template binding), and MasterOrchestrator (Stage 4 — dispatch). Classification takes twenty to forty milliseconds.

| Intent | Target Orchestrator | Trigger Keywords |
|--------|-------------------|-----------------|
| IMPLEMENT | TDDOrchestrator | implement, build, create, add, write |
| FIX | TDDOrchestrator | fix, repair, resolve, patch, correct |
| REFACTOR | RefactoringOrchestrator | refactor, restructure, reorganize, clean up |
| ANALYZE | LENS Synthesis | analyze, examine, review, inspect |
| PLAN | PlanningOrchestrator | plan, design, architect, propose |
| AUDIT | EnforcementOrchestrator | audit, validate, check, verify |
| DESIGN | Design coordination | design, architect, blueprint |
| DEBUG | DebuggerOrchestrator | debug, trace, diagnose, troubleshoot |
| INVESTIGATE | IntelligenceOrchestrator | investigate, research, explore |
| QUERY | Context-dependent routing | query, search, find, look up |
| DIGEST | BulkDigestOrchestrator | digest, ingest, absorb, summarize |
| REPHRASE | RequestRephraseOrchestrator | rephrase, clarify, reword |
| TEST | TDDOrchestrator | test, verify, validate tests |
| ONBOARD | OnboardingOrchestrator | onboard, setup, initialize |
| UPGRADE | UpgradeOrchestrator | upgrade, update, migrate |
| VACUUM | VacuumOrchestrator | vacuum, clean, declutter |
| HEALTH | HealthOrchestrator | health, status, diagnostics |
| CHALLENGE | ChallengeEngine | challenge, alternatives, compare |
| SYNC | SyncOrchestrator | sync, synchronize, mirror |
| TRAIN | TrainerOrchestrator | train, teach, learn |
| PUBLISH | GitPublishOrchestrator | publish, release, deploy |
| ROLLBACK | RollbackOrchestrator | rollback, revert, undo |
| SECURITY | SecurityVulnerabilityOrchestrator | security, vulnerability, threat |
| DOCUMENT | DocumentationOrchestrator | document, docs, documentation |
| DASHBOARD | DashboardOrchestrator | dashboard, visualize, report |
| DISCOVER | UnifiedDiscoveryOrchestrator | discover, explore, scan |
| WORKFLOW | WorkflowOrchestrator | workflow, pipeline, template |
| WORKFLOW_COMPOSE | WorkflowComposer | compose, compose workflow, build pipeline |

As of Phase 98, all twenty-eight intents are fully wired with routing miss detection (Phase 91) — any unrecognised request falls through to a structured rephrase prompt rather than silent failure. Phase 98 performed a dead code cleanup that removed 24 dead workflow modules, 23 unreferenced YAML templates, and 14 orphaned test files, reducing the workflow domain from 29 to 6 files while preserving all live functionality.

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

*All orchestrator counts and file paths verified against live codebase*

---

## Orchestrator Engagement Visibility

CORTEX's orchestrators emit detailed audit traces — and engagement visibility surfaces these traces to users during a session through three composable blocks:

| Block | Purpose | When Rendered |
|-------|---------|--------------|
| `BLOCK-ENGAGEMENT-BREADCRUMB` | Routing chain — always visible | Every response |
| `BLOCK-ENGAGEMENT-TIMELINE` | Collapsible orchestrator timing panel | Multi-step operations |
| `BLOCK-PHASE-ROADMAP` | Full phase overview at operation start | `/audit fix`, `/totalrecall`, multi-phase ops |

**Breadcrumb format (example):**
```
Route: IntentRouter → MasterOrchestrator → TDDOrchestrator → EnforcementOrchestrator
```

**Progress format (phase-list+bar — mandatory):**
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

## DebuggerOrchestrator — Multi-Stack Debugging

`DebuggerOrchestrator` at `cortex/orchestrators/support/debugger_orchestrator.py` is an EventBus-driven coordinator that uses a **Strategy Pattern** to apply language-specific debug injection without modifying the orchestrator core.

**Currently live:** Python strategies (`TestFailureStrategy`, `RefactorRegressionStrategy`, `GovernanceViolationStrategy`) and multi-stack strategies (`FrontendConsoleStrategy`, `HtmlVisionMappingStrategy`, `ApiTraceStrategy`, `SqlTraceStrategy`, `DotNetTraceStrategy`) — eight strategies total (Phase 86).  

**Commands:**
- `/debug {path}` — full cycle: detect stack → inject → capture → analyze → fix-plan
- `/debug-inject {path}` — injection only
- `/debug-cleanup` — production-safe removal of all markers

**Intelligence wiring:** OPJMixin (learning persistence), URS signals (reinforcement feedback), IntelligenceMatrix cells, bidirectional EventBus publish, and KnowledgeSynthesisEngine pattern capture.

---

## Universal Convergence Gate (CORE-068)

No code-modifying operation is considered complete in a single pass. CORE-068 mandates a detect→fix→rescan loop that repeats until zero P0/P1 issues remain (maximum three cycles).

| Applies to | Exempt |
|---|---|
| IMPLEMENT, FIX, REFACTOR, AUDIT, DEBUG, VACUUM, HEALTH | QUERY, DESIGN, PLAN, DIGEST, REPHRASE, SYNC, TRAIN |

Each operation type defines its own convergence predicate — for example, IMPLEMENT requires `test_pass_count >= baseline AND lint_errors == 0`, while AUDIT requires `p0_count == 0 AND p1_count == 0`. The `/audit fix` pipeline uses this in Stages 7–8.

The governance rule lives at `cortex-registry/core/rules/core-068-convergence-gate.yaml`, and the workflow primitive at `cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml`.

---

## EngagementRenderer — Orchestrator Visibility

`EngagementRenderer` at `cortex/orchestrators/response/engagement_renderer.py` is the SSOT formatter for all engagement signals. Phase 92 introduced it to replace inconsistent per-orchestrator formatting.

It provides fourteen pre-built command chains (e.g., `/audit fix` → `IntentRouter → AuditOrchestrator → EnforcementOrchestrator → HealthOrchestrator → VacuumOrchestrator`) and the `breadcrumb_for_command()` API. Three engagement blocks are rendered per response: BLOCK-ENGAGEMENT-BREADCRUMB (always), BLOCK-ENGAGEMENT-TIMELINE (multi-step), and BLOCK-PHASE-ROADMAP (multi-phase start).

---

## Operational Workflow Pipeline (Phase 89)

Phase 89 wired the complete workflow infrastructure from inert YAML definitions to live, executable pipelines. Seven capability clusters were addressed: technology-aware routing (WorkflowComplexityRouter), PostRefactorLintGate, engagement visibility via EngagementRenderer, SQLite tracing of every workflow step, expanded template wiring (6→20 operation types), WorkflowComposer graph execution, and CORE-068 convergence binding.

The complete template library spans seventy-nine templates across seventeen categories at `cortex-registry/workflows/templates/`.

---

## WorkflowGateway and @enforce_gateway (Phase 94–99)

`WorkflowGateway` at `cortex/orchestrators/workflow/workflow_gateway.py` is the mandatory entry point for all code-modifying orchestrator operations. Phase 94 introduced the `@enforce_gateway` decorator, which ensures that every Category A orchestrator (those that modify code or state) routes through the WorkflowGateway before execution.

**Category A orchestrators** (gateway-enforced): TDDOrchestrator, RefactoringOrchestrator, DebuggerOrchestrator, SecurityVulnerabilityOrchestrator, SDLCWorkflowOrchestrator, TrainerOrchestrator, HealthOrchestrator, VacuumOrchestrator, and others.

The gateway performs three checks before allowing execution:
1. **Template resolution** — verifies a matching workflow template exists for the operation
2. **Governance pre-flight** — runs the holistic validation gate primitive
3. **Convergence binding** — attaches the detect-fix-rescan loop for post-execution validation

Phase 96 cleaned up the gateway flag scaffolding by removing the legacy `PHASE90_GATEWAY_ENABLED=False` guards. Phase 98 performed a dead code cleanup removing 24 dead workflow modules, reducing the workflow domain from 29 to 6 files. Phase 99 fixed five fatal breaks in the gateway→composer→template chain to restore full pipeline integrity.

The `WorkflowComposer` at `cortex/orchestrators/workflow/workflow_composer.py` sits behind the gateway and handles YAML template resolution, dependency graph construction, and step-by-step execution through the StepStateMachine.
