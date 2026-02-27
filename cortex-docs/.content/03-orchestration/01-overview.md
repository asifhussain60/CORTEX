# Orchestration Overview

---
title: CORTEX Orchestration — Wired Orchestrators Across 4 Tiers
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/ + cortex-registry/core/specifications/
order: 1
---

> **Brain analogy:** The orchestration layer is the **cerebral cortex** — the wrinkled outer surface of the brain with dozens of specialized regions, each handling a different cognitive function, all coordinated by the thalamus (MasterOrchestrator). No region works alone; they communicate constantly.

---

## Architecture

CORTEX has **wired orchestrators** across **4 canonical tiers**, all satisfying the `IOrchestrator` protocol. The canonical wiring specification lives in `cortex-registry/core/specifications/`.

| Tier | Key Orchestrators |
|------|-----------------|
| **Core** (Tier 1) | MasterOrchestrator, IntentRouter, TDDOrchestrator, WorkflowOrchestrator, EnforcementOrchestrator, ConversationOrchestrator, InteractionOrchestrator, AuditOrchestrator, MasterOrchestrationStage1, MasterOrchestrationStage3, MasterOrchestrationStage4, ResponseOrchestrator, MetaAuditOrchestrator, HolisticValidationOrchestrator, ChallengeEngine, SOLIDOrchestrator, SecurityVulnerabilityOrchestrator |
| **Domain** (Tier 2) | RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator, ServiceDecompositionOrchestrator, SDLCWorkflowOrchestrator, EnhancedPlanningOrchestrator |
| **Support** (Tier 3) | OnboardingOrchestrator, UpgradeOrchestrator, RollbackOrchestrator, SetupOrchestrator, HealthOrchestrator, SweepCatalogueOrchestrator, VacuumOrchestrator, BulkDigestOrchestrator, DigestSessionOrchestrator, DebuggerOrchestrator, UnifiedDiscoveryOrchestrator, UnifiedQualityOrchestrator, AutoHealingMCPOrchestrator, CortexDocsOrchestrator, PlanOrchestrator, RepositoryOnboardingOrchestrator, LENSVisualizationOrchestrator, VSCodeConfigurator, DependencyResolver, RequestRephraseOrchestrator, TrainerOrchestrator, SyncOrchestrator, DocumentationOrchestrator |
| **Git** (Tier 4) | GitOrchestrator, GitPublishOrchestrator, SanitizationOrchestrator, PreCommitEnforcementOrchestrator |

> **Note on total codebase:** `cortex/orchestrators/` contains many more classes (strategy implementations, mixin helpers, specialized sub-components). The **wired** orchestrators are the canonical IOrchestrator-compliant entry points registered in the wiring specifications.

---

## Dispatch Flow

```
[Request]
     │
     ▼
[MasterOrchestrator]  ← the conductor
     │
     ▼
[IntentRouter]  ← classifies intent (20-40ms)
     │
     ├── IMPLEMENT → TDDOrchestrator
     ├── FIX → TDDOrchestrator
     ├── REFACTOR → RefactoringOrchestrator
     ├── ANALYZE → LENS Synthesis
     ├── PLAN → PlanningOrchestrator
     ├── AUDIT → EnforcementOrchestrator
     ├── DESIGN → Design coordination
     ├── DEBUG → DebuggerOrchestrator
     ├── INVESTIGATE → IntelligenceOrchestrator
     ├── QUERY → Context-dependent routing
     ├── DIGEST → Support orchestrators
     └── REPHRASE → RequestRephraseOrchestrator
```

---

## Universal Lifecycle

Every orchestrator satisfies the `IOrchestrator` protocol via `OrchestratorProtocolMixin`.
The standard 5-step lifecycle is:

```
setup() → govern() → execute() → validate() → teardown()
```

Additionally, **`OrchestratorProtocolMixin.execute_operation()`** auto-activates cross-cutting
hooks (LENS, KnowledgeSynthesis, GovernanceGate) and `execute()` / `run()` auto-log
`ORCHESTRATOR_START` and `ORCHESTRATOR_END` to `.cortex-runtime/audit.db` (SQLite WAL).
This audit logging is non-blocking — a failure to log never prevents execution.

> **Note:** The primary base is `OrchestratorProtocolMixin`, not `OrchestratorBase`.
> `OrchestratorBase` exists in `cortex/core/orchestrator_base.py` but is only used by legacy
> orchestrators. All wired orchestrators use `IOrchestrator` + `OrchestratorProtocolMixin`.

---

## Practical Examples

**Business Leader:** "Specialized wired orchestrators means every type of development work has a dedicated engine. SweepCatalogueOrchestrator (CORE-064) ensures no long-running refactor sweep is ever abandoned between sessions."

**Product Owner:** "I track which orchestrators are used most. TDDOrchestrator handles IMPLEMENT/FIX. RefactoringOrchestrator handles semantic code transformations — including Roslyn-powered C# rename by symbol name. PlanningOrchestrator manages sprint-level planning."

**Developer:** "Each orchestrator has a clear responsibility. TDDOrchestrator handles RED→GREEN→REFACTOR. RefactoringOrchestrator handles semantic code transformations. I never wonder which one to use — IntentRouter decides."

---

*Orchestrator count verified via `grep -r 'class.*Orchestrator' cortex/orchestrators/`*
