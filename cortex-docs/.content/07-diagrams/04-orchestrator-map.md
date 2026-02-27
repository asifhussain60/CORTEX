# Orchestrator Map

---
title: 17 Wired Orchestrators Across 3 Tiers
type: diagram
audience: [Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/ + cortex-registry/core/specifications/*-wiring.yaml
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
    │  Wired orchestrators satisfy the IOrchestrator protocol
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
    ├── DOMAIN TIER (6 wired)
    │   ├── RefactoringOrchestrator     ← Semantic refactoring (Roslyn by-name rename)
    │   ├── PlanningOrchestrator        ← Plan-first execution (CORE-048)
    │   ├── DomainOrchestrator          ← Domain-specific business logic
    │   ├── DashboardOrchestrator       ← Dashboard generation
    │   ├── ServiceDecompositionOrchestrator ← Service decomposition
    │   └── LegacyModernizationOrchestrator  ← Legacy modernization
    │
    └── SUPPORT TIER (14 wired)
        ├── OnboardingOrchestrator      ← Repository onboarding (LENS analysis)
        ├── UpgradeOrchestrator         ← Upgrade lifecycle management
        ├── RollbackOrchestrator        ← Rollback & recovery
        ├── SetupOrchestrator           ← Environment setup
        ├── HealthOrchestrator          ← System health monitoring
        ├── SweepCatalogueOrchestrator  ← CORE-064 sweep completeness (SQLite WAL)
        ├── VacuumOrchestrator          ← Markdown sprawl cleanup
        ├── BulkDigestOrchestrator      ← Bulk content ingestion
        ├── DigestSessionOrchestrator   ← Digest session management
        ├── DebuggerOrchestrator        ← Debug session coordination
        ├── UnifiedDiscoveryOrchestrator ← Repository discovery
        ├── UnifiedQualityOrchestrator  ← Quality gate enforcement
        ├── AutoHealingMCPOrchestrator  ← MCP auto-healing
        └── CortexDocsOrchestrator      ← Documentation generation
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

*Verified against `cortex/orchestrators/` directory + wiring YAML*
