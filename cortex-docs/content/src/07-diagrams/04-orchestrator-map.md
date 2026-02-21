# Orchestrator Map

---
title: 52 Orchestrators Across 10 Domains
type: diagram
audience: [Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/orchestrators/
order: 4
---

## Domain Architecture

```
cortex/orchestrators/
├── core/           ← Primary orchestrators (MasterOrchestrator, IntentRouter, TDD)
├── domain/         ← Domain-specific orchestrators
├── git/            ← Git operations
├── health/         ← Health monitoring & diagnostics
├── intelligence/   ← AI & LENS orchestrators
├── strategies/     ← Strategy pattern implementations
├── support/        ← Support & utility orchestrators
├── synthesis/      ← Knowledge synthesis
├── validation/     ← Validation & compliance
└── workflow/       ← Workflow execution
```

## Orchestrator Hierarchy

```
OrchestratorBase (cortex/core/orchestrator_base.py)
    │
    │  All 52 orchestrators inherit from this base
    │
    ├── CORE DOMAIN
    │   ├── MasterOrchestrator        ← Entry point, 4-stage pipeline
    │   ├── IntentRouter              ← 12 intent classification
    │   ├── TDDOrchestrator           ← RED → GREEN → REFACTOR
    │   ├── EnforcementOrchestrator   ← Governance rule enforcement
    │   ├── RefactoringOrchestrator   ← Semantic refactoring
    │   ├── SecurityOrchestrator      ← Security analysis & gates
    │   ├── RequestRephraseOrchestrator ← Request clarification
    │   └── ... (additional core orchestrators)
    │
    ├── DOMAIN
    │   ├── DomainOrchestrators       ← Domain-specific logic
    │   └── ... (domain variations)
    │
    ├── GIT
    │   ├── GitOrchestrator           ← Git operations
    │   └── ... (git-specific flows)
    │
    ├── HEALTH
    │   ├── HealthOrchestrator        ← System health monitoring
    │   ├── DiagnosticOrchestrator    ← Issue diagnosis
    │   └── ... (health monitoring)
    │
    ├── INTELLIGENCE
    │   ├── LENSOrchestrator          ← LENS analysis coordination
    │   ├── BrainOrchestrator         ← Intelligence tier management
    │   └── ... (AI orchestrators)
    │
    ├── STRATEGIES
    │   └── StrategyOrchestrator      ← Strategy pattern dispatch
    │
    ├── SUPPORT
    │   ├── OnboardingOrchestrator    ← Repository onboarding
    │   ├── ExplanationOrchestrator   ← Code explanation
    │   └── ... (support orchestrators)
    │
    ├── SYNTHESIS
    │   └── SynthesisOrchestrator     ← Knowledge synthesis
    │
    ├── VALIDATION
    │   ├── ValidationOrchestrator    ← Code validation
    │   ├── ComplianceOrchestrator    ← Compliance checking
    │   └── ... (validation flows)
    │
    └── WORKFLOW
        ├── WorkflowOrchestrator      ← Workflow execution
        └── ... (workflow management)
```

## Cross-Orchestrator Communication

```
┌──────────────────┐     ┌──────────────────┐
│ MasterOrchestrator│────→│  IntentRouter    │
└────────┬─────────┘     └────────┬─────────┘
         │                        │
         │  routes to             │ classifies
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│ TDDOrchestrator  │◄───→│ LENS Orchestrator│
└────────┬─────────┘     └──────────────────┘
         │
         │  enforces
         ▼
┌──────────────────┐     ┌──────────────────┐
│   Enforcement    │────→│  Audit DB        │
│   Orchestrator   │     │  (record)        │
└──────────────────┘     └──────────────────┘
```

Communication uses the **OrchestratorEventBus** (`cortex/infrastructure/orchestrator_event_bus.py`) for decoupled inter-orchestrator messaging.

---

*Verified against `cortex/orchestrators/` directory · 20 February 2026*
