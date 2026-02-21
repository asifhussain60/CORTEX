# Orchestration Overview

---
title: CORTEX Orchestration — 52 Orchestrators Across 10 Domains
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/orchestrators/
order: 1
---

> **Brain analogy:** The orchestration layer is the **cerebral cortex** — the wrinkled outer surface of the brain with dozens of specialized regions, each handling a different cognitive function, all coordinated by the thalamus (MasterOrchestrator). No region works alone; they communicate constantly.

---

## Architecture

After the 12-phase Cohesive Brain Refactor (120 → 52 orchestrators), CORTEX has **52 canonical orchestrator classes** organized into **10 domains**:

| Domain | Files | Key Orchestrators |
|--------|-------|------------------|
| **core** | 52 | MasterOrchestrator, IntentRouter, TDDOrchestrator, EnforcementOrchestrator, PlanningOrchestrator, RefactoringOrchestrator, SecurityOrchestrator, InteractionOrchestrator, DebuggerOrchestrator |
| **domain** | 30 | BusinessDomainOrchestrator, EcommerceOrchestrator, FinancialOrchestrator, HealthcareOrchestrator |
| **health** | 30 | HealthOrchestrator, VacuumOrchestrator |
| **intelligence** | 14 | IntelligenceOrchestrator, UnifiedAnalysisOrchestrator |
| **support** | 38 | OnboardingOrchestrator, SetupOrchestrator, UnifiedDiscoveryOrchestrator, RepositoryOnboardingOrchestrator |
| **validation** | 11 | HolisticValidationOrchestrator, ReviewOrchestrator, UnifiedQualityAssuranceOrchestrator |
| **workflow** | 13 | WorkflowOrchestrator, PhaseCompletionOrchestrator, CortexMasterPlanOrchestrator |
| **git** | 4 | GitOrchestrator, GitPublishOrchestrator |
| **strategies** | 1 | Strategy selection coordination |
| **synthesis** | 1 | Cross-domain synthesis |

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

Every orchestrator follows the OrchestratorBase 5-step lifecycle:

```
setup() → govern() → execute() → validate() → teardown()
```

This ensures governance is checked before every execution and audit trails are recorded after every operation.

---

## Practical Examples

**Business Leader:** "52 specialized orchestrators means every type of development work has a dedicated engine. No generic, one-size-fits-all processing."

**Product Owner:** "I track which orchestrators are used most. TDDOrchestrator handles 40% of requests, RefactoringOrchestrator 25%, PlanningOrchestrator 15%. This tells me what my team does day-to-day."

**Developer:** "Each orchestrator has a clear responsibility. TDDOrchestrator handles RED→GREEN→REFACTOR. RefactoringOrchestrator handles semantic code transformations. I never wonder which one to use — IntentRouter decides."

---

*Orchestrator count verified via `grep -r 'class.*Orchestrator' cortex/orchestrators/` · 20 February 2026*
