# IntentRouter

---
title: IntentRouter — LENS-Based Request Classification and 4-Stage Pipeline Routing
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/core/intent_router.py + cortex/orchestrators/core/intent_router_impl.py
order: 3
---

## Purpose

IntentRouter classifies every incoming request into one of twenty-eight intent types using LENS-based intelligence and keyword/regex hybrid matching. Classification takes 20–40ms and feeds the 4-stage pipeline:

1. **Interaction** — comprehend request via InteractionOrchestrator
2. **Intent** — classify via IntentRouter.route()
3. **Intelligence** — LENS analysis (Language → Examination → Navigation → Synthesis)
4. **Execution** — delegate to domain orchestrator via MasterOrchestrator

**Location:** `cortex/orchestrators/core/intent_router.py` (primary), `cortex/orchestrators/core/intent_router_impl.py` (implementation)

**Implements:** `IOrchestrator`

## All 28 Intent Types (Phase 90–99 Complete)

| Intent | Target Orchestrator | Trigger Keywords |
|--------|-------------------|-----------------|
| IMPLEMENT | TDDOrchestrator | "build", "create", "add", "implement" |
| FIX | TDDOrchestrator | "fix", "bug", "broken", "error" |
| REFACTOR | RefactoringOrchestrator | "refactor", "improve", "optimize" |
| ANALYZE | DomainOrchestrator (LENS) | "analyze", "examine" |
| PLAN | PlanningOrchestrator | "plan", "phase", "roadmap" |
| AUDIT | AuditOrchestrator | "/audit", "scan", "check" |
| DESIGN | DesignCoordinator | "architect", "design", "structure" |
| DEBUG | DebuggerOrchestrator | "/debug", "trace", "diagnose" |
| INVESTIGATE | InvestigationOrchestrator | "investigate", "root cause" |
| QUERY | QueryCoordinator | "explain", "how", "what", "why" |
| DIGEST | DigestCoordinator | "summarize", "digest", "ingest" |
| REPHRASE | RequestRephraseOrchestrator | "rephrase" |
| VACUUM | VacuumOrchestrator | "/vacuum", "clean up", "markdown sprawl" |
| HEALTH | HealthOrchestrator | "/health", "health check" |
| SYNC | GitOrchestrator + WorkflowOrchestrator | "/sync", "sync to company" |
| TRAIN | TrainerOrchestrator | "/train", "learn from repo" |
| TOTALRECALL | MasterOrchestrator (7-phase) | "/totalrecall", "total recall" |
| RCA | InvestigationOrchestrator + RCAEngine | "root cause", "rca", "five whys" |
| GOLDEN_TEST | TDDOrchestrator | "golden test", "workflow template" |
| ONBOARD | OnboardingOrchestrator | "/onboard", "onboard repo" |
| UPGRADE | UpgradeOrchestrator | "/upgrade", "update dependencies" |
| CHALLENGE | ChallengeEngine | "/challenge", "alternatives" |
| SDLC | SDLCWorkflowOrchestrator | "sdlc", "workflow pipeline" |
| SECURITY | SecurityVulnerabilityOrchestrator | "security scan", "vulnerability" |
| REPORT | DashboardOrchestrator | "dashboard", "generate report" |
| KNOWLEDGE | KnowledgeOrchestrator | "knowledge search", "what does CORTEX know" |
| WORKFLOW_COMPOSE | WorkflowComposer | "compose workflow", "build pipeline", "workflow compose" |
| UNKNOWN | ConversationOrchestrator | Fallback when confidence < 0.6 |

## Routing Confidence Thresholds

| Confidence | Routing Decision |
|---|---|
| ≥ 0.85 | Direct route — immediately delegate |
| 0.60 – 0.84 | Route with clarification question |
| < 0.60 | ConversationOrchestrator — ask to rephrase |

## Routing Miss Detection (Phase 91)

When confidence falls below 0.4 or intent resolves to UNKNOWN, IntentRouter calls `_log_routing_miss()` to emit an `AC-91-ROUTING-MISS-001` audit marker. This creates a persistent record of unhandled request patterns, enabling:

- Pattern analysis to discover new intent types needed
- URS signal emission for missed-route learning
- Engagement chain rendering via EngagementRenderer

## WorkflowComplexityRouter (Phase 89)

For operations that involve workflow templates, `WorkflowComplexityRouter` at `cortex/orchestrators/core/intent_router/workflow_gate.py` evaluates whether the request requires simple or composite workflow execution. It gates workflow-aware routing to ensure template-bound operations use the correct execution path.

---

*Verified against intent_router.py + intent_router_impl.py + Phase 89–99 wiring*
