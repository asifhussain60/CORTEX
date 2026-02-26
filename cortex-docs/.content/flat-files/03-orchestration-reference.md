---
title: Orchestration Reference
consolidates:
  - 03-orchestration-tdd-orchestrator.md
  - 03-orchestration-domain-orchestrators.md
  - 03-orchestration-workflow-engine.md
  - 03-orchestration-security-orchestrator.md
  - 03-orchestration-sweep-catalogue.md
last_verified: 2026-02-26
source_of_truth: cortex/orchestrators/core/ + cortex/orchestrators/domain/ + cortex/orchestrators/workflow/ + cortex/orchestrators/support/
audience: [Software Developers, Product Owners]
---

# Orchestration Reference

Detailed reference for specialised orchestrators — TDDOrchestrator, domain orchestrators, the WorkflowEngine runtime, SecurityOrchestrator, and SweepCatalogueOrchestrator.

---

## TDDOrchestrator — Test-Driven Development Engine

Location: `cortex/orchestrators/core/tdd_orchestrator.py`

TDDOrchestrator enforces CORE-008: TDD mandatory for all IMPLEMENT and FIX operations. It handles approximately forty percent of all requests.

### The TDD Cycle

**RED**: Write a failing test that specifies the desired behaviour. TDDOrchestrator checks that no implementation exists before the test and validates that the test fails initially, confirming it tests something real.

**GREEN**: Write the minimum code to make the test pass. No more than necessary.

**REFACTOR**: Improve code while keeping all tests green. Suggest extraction, rename, and structural improvements.

**VALIDATE**: Governance gate plus audit trail recording.

### TestQualityGate Integration

TDDOrchestrator integrates with TestQualityGate at `cortex/testing/quality_gate.py` to block test generation scoring below seven. Tests must be meaningful, not just present. The scoring formula is: Impact (zero to three) plus Likelihood (zero to two) plus Detection (zero to two) plus Efficiency (zero to two) minus Maintenance (zero to two).

### Unified Reinforcement Signals

TDDOrchestrator emits reinforcement signals after every TDD cycle completion, feeding the closed-loop learning system:

| Outcome | Signal | Delta |
|---------|--------|-------|
| GREEN on first try | STRONG_REWARD | +1.0 |
| GREEN with retries | MILD_REWARD | +0.5 |
| Stuck in RED | MILD_PUNISHMENT | −0.5 |

These signals adjust confidence scores on the patterns used during the cycle. Patterns that consistently produce first-try GREEN are promoted to T1 knowledge (confidence at or above 0.9). Patterns that consistently fail are quarantined (confidence at or below 0.3).

---

## Domain Orchestrators — Business-Vertical Specialisation

Location: `cortex/orchestrators/domain/`

Seven domain orchestrators implement IOrchestrator via OrchestratorProtocolMixin. Each has deep expertise in a specific engineering or business vertical.

| Orchestrator | Path | Purpose |
|-------------|------|---------|
| PlanningOrchestrator | `domain/planning_orchestrator.py` | Structured planning — decomposition, gap catalogue, TDD sequence generation |
| DomainOrchestrator | `domain/domain_orchestrator.py` | Domain-specific intelligence — LENS analysis with domain knowledge synthesis |
| RefactoringOrchestrator | `domain/refactoring_orchestrator.py` | Intelligent refactoring — duplication detection, code smell remediation, CORE-035 |
| SDLCWorkflowOrchestrator | `domain/sdlc_workflow_orchestrator.py` | SDLC Intelligence Engine — template selection, knowledge hydration, FSM execution |
| DashboardOrchestrator | `domain/dashboard_orchestrator.py` | Static dashboard generation — landing pages, per-repo dashboards, SQLite-backed metrics |
| EnhancedPlanningOrchestrator | `domain/enhanced_planning_orchestrator.py` | Advanced planning with ROI scoring, wave decomposition, audit-driven auto-planning |
| ServiceDecompositionOrchestrator | `domain/service_decomposition_orchestrator.py` | Microservice decomposition analysis |

### Domain Routing

IntentRouter classifies requests and routes to domain orchestrators:

| Intent | Target |
|--------|--------|
| PLAN | PlanningOrchestrator or EnhancedPlanningOrchestrator |
| REFACTOR | RefactoringOrchestrator |
| ANALYZE | DomainOrchestrator (domain knowledge synthesis) |
| SDLC | SDLCWorkflowOrchestrator (template selection plus FSM) |
| REPORT | DashboardOrchestrator (static site generation) |

### RefactoringOrchestrator Capabilities

| Feature | Detail |
|---------|--------|
| Duplication detection | Identifies duplicate implementations across the codebase |
| Semantic rename | Roslyn by-name symbol rename (Python, C#, TypeScript) — no byte offset |
| Code smell remediation | Long methods, high complexity, poor naming |
| Multi-language | Python, TypeScript and JavaScript, C# and .NET |
| Governance gate | CORE-035 validation before and after refactor |

### SDLCWorkflowOrchestrator

The SDLC Intelligence Engine provides template selection (matching SDLC workflows to project type via LENS fingerprinting), knowledge hydration (injecting domain knowledge from `cortex-registry/knowledge-base/` into workflow context), and FSM execution (state machine execution via WorkflowEngine).

---

## WorkflowEngine — YAML to FSM Runtime

Location: `cortex/orchestrators/workflow/`

The WorkflowEngine translates YAML workflow template definitions into executable Finite State Machine step graphs with a convergence loop that guarantees every audit-fix sweep runs until all violations are resolved.

### Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| StepStateMachine | `workflow/step_state_machine.py` | FSM governing step progression |
| WorkflowComposer | `workflow/workflow_composer.py` | Composes YAML into executable step graphs |
| StepHandlerRegistry | `workflow/workflow_composer.py` | Maps step type IDs to Python callables |
| ConvergenceLoopExecutor | `workflow/convergence_loop_executor.py` | Detect-fix-rescan with exponential backoff |
| TemplateRegistry | `workflow/template_registry.py` | Discovers and caches YAML workflow templates |

### Step State Machine

Each workflow step progresses through states:

| State | Meaning |
|-------|---------|
| PENDING | Step queued, not yet started |
| RUNNING | Step actively executing |
| CHECKING | Convergence evaluation of success criteria |
| PASSED | Success criteria met — proceed to next step |
| RETRYING | Success criteria not met — re-execute (cycle incremented) |
| FAILED | Maximum cycles exceeded or unrecoverable error |
| SKIPPED | Optional step with unmet precondition |

### StepHandlerRegistry

Maps step type IDs to Python callables, decoupling YAML template definitions from implementation. Adding new step types requires only registering a handler — no modification to WorkflowComposer. Unknown types raise UnregisteredStepTypeError.

### ConvergenceLoopExecutor

Implements the detect-fix-rescan loop primitive with exponential backoff. Configuration includes maximum retries, initial backoff seconds, backoff multiplier, maximum backoff seconds, and total timeout seconds. The loop continues until the convergence check returns True — there is no single-pass mode. Partial sweeps are architecturally prevented (CORE-064).

This is the engine behind `/audit fix` Stages seven and eight: detect violations, fix them, rescan, repeat until P0 and P1 counts reach zero.

### Template Registry

Discovers all YAML workflow templates in `cortex-registry/workflows/templates/` and makes them available by ID. Templates are cached with a five-minute TTL and auto-reloaded on file change in development mode.

### Template Tiers

Templates are organised in a three-tier hierarchy:

**Tier 1 — Primitives** at `cortex-registry/workflows/templates/primitives/`: Atomic reusable building blocks with single responsibility. Categories include analysis, execution, governance, intelligence, and validation. Examples: lens-ast-scan, audit-trace, sweep-catalogue-open, detect-fix-rescan-loop.

**Tier 2 — Composites** at `cortex-registry/workflows/templates/composites/`: Composed of multiple primitives, representing a reusable workflow pattern for a domain. Must not duplicate a top-level workflow per CORE-035.

**Tier 3 — Workflows** at `cortex-registry/workflows/templates/<domain>/`: Full intent-specific execution workflows. Domains include tdd, security, lifecycle, backend, audit, and governance. Examples: tdd-feature-implementation, security-compliance-audit, onboarding-workflow, csharp-refactor-workflow.

---

## SecurityOrchestrator — Security-First Development

Location: `cortex/orchestrators/core/security_orchestrator.py`

SecurityOrchestrator handles security-focused operations including vulnerability scanning (via the LENS Security Analyzer), credential exposure detection, SQL injection pattern identification, SAST integration, and CVE pattern matching.

| Input | What It Provides |
|-------|-----------------|
| LENS Security Analyzer | Vulnerability findings with severity |
| EnforcementOrchestrator | Security agent validation |
| Bandit SAST | Python-specific security analysis |
| Requirements audit | Dependency CVE scanning |

---

## SweepCatalogueOrchestrator — CORE-064

Location: `cortex/orchestrators/support/sweep_catalogue_orchestrator.py`

The Sweep Completeness Contract (CORE-064) guarantees that every FIX, REFACTOR, or AUDIT operation exhausts its full issue catalogue before reporting success. Partial sweeps — where some issues are skipped due to token budget, time pressure, or oversight — are a P0 governance violation.

### Lifecycle

1. **open_sweep**: Register all discovered issues in a named catalogue at `.cortex-runtime/sweeps/{sweep_id}.db` (SQLite WAL mode)
2. **Process issues**: Orchestrator fixes issues one by one
3. **mark_resolved**: Called for each fixed issue
4. **assert_exhausted**: Final gate — raises SweepIncompleteError if any open issues remain
5. **Success**: Only after assert_exhausted passes can the sweep report completion

### Persistence

Sweep state is stored in SQLite WAL mode. Sweeps survive process restarts and token budget resets. A new session can resume an in-progress sweep by checking open issues.

### MCP Surface

The `cortex_sweep_status` MCP tool at `cortex/mcp/tools/sweep_status_tool.py` exposes the sweep catalogue to Copilot Chat with three operations: status (full sweep state with open and resolved counts), open (only unresolved issues for resuming), and assert (runs assert_exhausted and returns success or lists remaining items).

### Enforcement Integration

EnforcementOrchestrator calls assert_exhausted as part of the pre-commit gate. If any sweep registered for the current branch has open items, the commit is blocked.

---

*All orchestrator paths and component locations verified against live codebase — 26 February 2026*
