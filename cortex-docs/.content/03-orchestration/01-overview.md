# Orchestration Overview

---
title: CORTEX Orchestration — 51 Wired Orchestrators Across 4 Tiers
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-26
source_of_truth: cortex/orchestrators/ + cortex-registry/core/specifications/
phases_complete: [Phase 59, Phase 60, Phase 79-D, Phase 68, Phase 69, Phase 82]
order: 1
---

> **Brain analogy:** The orchestration layer is the **cerebral cortex** — the wrinkled outer surface of the brain with dozens of specialized regions, each handling a different cognitive function, all coordinated by the thalamus (MasterOrchestrator). No region works alone; they communicate constantly.

---

## Architecture

CORTEX has **51 wired orchestrators** across **4 canonical tiers**, all satisfying the `IOrchestrator` protocol. The canonical wiring specification lives in `cortex-registry/core/specifications/`.

| Tier | Count | Key Orchestrators |
|------|-------|-----------------|
| **Core** (Tier 1) | 17 | MasterOrchestrator, IntentRouter, TDDOrchestrator, WorkflowOrchestrator, EnforcementOrchestrator, ConversationOrchestrator, InteractionOrchestrator, AuditOrchestrator, MasterOrchestrationStage1, MasterOrchestrationStage3, MasterOrchestrationStage4, ResponseOrchestrator, MetaAuditOrchestrator, HolisticValidationOrchestrator, ChallengeEngine, SOLIDOrchestrator, SecurityVulnerabilityOrchestrator |
| **Domain** (Tier 2) | 7 | RefactoringOrchestrator, PlanningOrchestrator, DomainOrchestrator, DashboardOrchestrator, ServiceDecompositionOrchestrator, SDLCWorkflowOrchestrator, EnhancedPlanningOrchestrator |
| **Support** (Tier 3) | 23 | OnboardingOrchestrator, UpgradeOrchestrator, RollbackOrchestrator, SetupOrchestrator, HealthOrchestrator, SweepCatalogueOrchestrator, VacuumOrchestrator, BulkDigestOrchestrator, DigestSessionOrchestrator, DebuggerOrchestrator, UnifiedDiscoveryOrchestrator, UnifiedQualityOrchestrator, AutoHealingMCPOrchestrator, CortexDocsOrchestrator, PlanOrchestrator, RepositoryOnboardingOrchestrator, LENSVisualizationOrchestrator, VSCodeConfigurator, DependencyResolver, RequestRephraseOrchestrator, TrainerOrchestrator, SyncOrchestrator, DocumentationOrchestrator |
| **Git** (Tier 4) | 4 | GitOrchestrator, GitPublishOrchestrator, SanitizationOrchestrator, PreCommitEnforcementOrchestrator |

> **Note on total codebase:** `cortex/orchestrators/` contains many more classes (strategy implementations, mixin helpers, specialized sub-components). The **51 wired** are the canonical IOrchestrator-compliant entry points registered in the wiring specifications.

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

Every orchestrator satisfies the `IOrchestrator` protocol via `OrchestratorProtocolMixin` (Phase 58).
The standard 5-step lifecycle is:

```
setup() → govern() → execute() → validate() → teardown()
```

Additionally, **`OrchestratorProtocolMixin.execute_operation()`** auto-activates cross-cutting
hooks (LENS, KnowledgeSynthesis, GovernanceGate) and `execute()` / `run()` auto-log
`ORCHESTRATOR_START` and `ORCHESTRATOR_END` to `.cortex-runtime/audit.db` (SQLite WAL).
This audit logging is non-blocking — a failure to log never prevents execution.

> **Note:** The primary base is `OrchestratorProtocolMixin` (Phase 58), not `OrchestratorBase`.
> `OrchestratorBase` exists in `cortex/core/orchestrator_base.py` but is only used by 2 legacy
> orchestrators. All 51 wired orchestrators use `IOrchestrator` + `OrchestratorProtocolMixin`.

---

## Practical Examples

**Business Leader:** "51 specialized wired orchestrators means every type of development work has a dedicated engine. SweepCatalogueOrchestrator (CORE-064) ensures no long-running refactor sweep is ever abandoned between sessions."

**Product Owner:** "I track which orchestrators are used most. TDDOrchestrator handles IMPLEMENT/FIX. RefactoringOrchestrator handles semantic code transformations — including Roslyn-powered C# rename by symbol name. PlanningOrchestrator manages sprint-level planning."

**Developer:** "Each orchestrator has a clear responsibility. TDDOrchestrator handles RED→GREEN→REFACTOR. RefactoringOrchestrator handles semantic code transformations. I never wonder which one to use — IntentRouter decides."

---

*Orchestrator count verified via `grep -r 'class.*Orchestrator' cortex/orchestrators/` · 26 February 2026 · Phase 82 response template engine + 4-tier architecture reflected*
