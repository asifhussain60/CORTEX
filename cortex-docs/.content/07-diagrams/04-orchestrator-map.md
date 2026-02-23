# Orchestrator Map

---
title: 22 Wired Orchestrators Across 3 Tiers
type: diagram
audience: [Software Developers]
last_verified: 2026-02-21
source_of_truth: cortex/orchestrators/
order: 4
---

## 3-Tier Architecture

```
cortex/orchestrators/
├── core/       ← 7 wired entry points (MasterOrchestrator, IntentRouter, TDD…)
├── domain/     ← 3 wired domain orchestrators (Refactoring, Planning, Domain)
└── support/    ← 7 wired support orchestrators (Onboarding, Health, SweepCatalogue…)
```

> Additional sub-components and adapters exist under `cortex/orchestrators/` but are not IOrchestrator-wired entry points.

## Orchestrator Hierarchy

```
OrchestratorBase (cortex/core/orchestrator_base.py)
    │  All 22 wired orchestrators inherit from this base
    │  Auto-logs every execute()/run() call to .cortex-runtime/audit.db (SQLite WAL)
    │
    ├── CORE TIER (7 wired)
    │   ├── MasterOrchestrator          ← Entry point, 4-stage pipeline
    │   ├── IntentRouter                ← 12+ intent classification (20–40ms)
    │   ├── TDDOrchestrator             ← RED → GREEN → REFACTOR
    │   ├── WorkflowOrchestrator        ← WorkflowEngine.load()/execute_step()
    │   ├── EnforcementOrchestrator     ← Governance rule enforcement
    │   ├── ConversationOrchestrator    ← Multi-turn conversation management
    │   └── InteractionOrchestrator     ← User interaction flows
    │
    ├── DOMAIN TIER (3 wired)
    │   ├── RefactoringOrchestrator     ← Semantic refactoring (Roslyn by-name rename)
    │   ├── PlanningOrchestrator        ← Plan-first execution (CORE-048)
    │   └── DomainOrchestrator          ← Domain-specific business logic
    │
    └── SUPPORT TIER (7 wired)
        ├── OnboardingOrchestrator      ← Repository onboarding (LENS analysis)
        ├── UpgradeOrchestrator         ← Upgrade lifecycle management
        ├── RollbackOrchestrator        ← Rollback & recovery
        ├── SetupOrchestrator           ← Environment setup
        ├── HealthOrchestrator          ← System health monitoring
        ├── SweepCatalogueOrchestrator  ← CORE-064 sweep completeness (SQLite WAL)
        └── VacuumOrchestrator          ← Markdown sprawl cleanup
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
