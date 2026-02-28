# Request Flow

---
title: End-to-End Request Flow Diagram
type: diagram
audience: [Product Owners, Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/core/master_orchestrator.py
order: 3
---

## MasterOrchestrator 4-Stage Pipeline

```
                    USER REQUEST
                    "Implement user auth"
                         │
                         ▼
┌────────────────────────────────────────────┐
│  STAGE 1: INTERACTION                      │
│  ┌──────────────────────────────────────┐  │
│  │  Display Definition of Ready (DoR)   │  │
│  │  ┌────────────────────────────────┐  │  │
│  │  │ • Scope clear?                 │  │  │
│  │  │ • Acceptance criteria defined? │  │  │
│  │  │ • Dependencies identified?     │  │  │
│  │  └────────────────────────────────┘  │  │
│  │  Await user approval                 │  │
│  └──────────────────────────────────────┘  │
└───────────────────┬────────────────────────┘
                    │ approved
                    ▼
┌────────────────────────────────────────────┐
│  STAGE 2: INTENT CLASSIFICATION            │
│  ┌──────────────────────────────────────┐  │
│  │  IntentRouter analyzes request       │  │
│  │                                      │  │
│  │  Input: "Implement user auth"        │  │
│  │  Output: IMPLEMENT (confidence: 0.95)│  │
│  │                                      │  │
│  │  12 intent types:                    │  │
│  │  IMPLEMENT, FIX, REFACTOR, ANALYZE,  │  │
│  │  TEST, DEBUG, ONBOARD, EXPLAIN,      │  │
│  │  REVIEW, DEPLOY, SECURITY, WORKFLOW  │  │
│  └──────────────────────────────────────┘  │
└───────────────────┬────────────────────────┘
                    │ intent: IMPLEMENT
                    ▼
┌────────────────────────────────────────────┐
│  STAGE 3: INTELLIGENCE PREFETCH            │
│  ┌──────────────────────────────────────┐  │
│  │  LENS Analysis (10 parallel analyzers)│  │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌─────────┐   │  │
│  │  │AST │ │Git │ │Imp │ │Security │   │  │
│  │  └────┘ └────┘ └────┘ └─────────┘   │  │
│  │  ┌─────┐ ┌────┐ ┌─────┐ ┌──────┐   │  │
│  │  │Commt│ │Patn│ │Metrc│ │Domain│   │  │
│  │  └─────┘ └────┘ └─────┘ └──────┘   │  │
│  │                                      │  │
│  │  → Synthesis → Confidence score      │  │
│  │  → 300-800ms total                   │  │
│  └──────────────────────────────────────┘  │
└───────────────────┬────────────────────────┘
                    │ LENS context ready
                    ▼
┌────────────────────────────────────────────┐
│  STAGE 4: EXECUTION                        │
│  ┌──────────────────────────────────────┐  │
│  │  Route to TDDOrchestrator            │  │
│  │                                      │  │
│  │  TDD Cycle:                          │  │
│  │  ┌─────┐   ┌───────┐   ┌──────────┐ │  │
│  │  │ RED │ → │ GREEN │ → │ REFACTOR │ │  │
│  │  │Write│   │Impl.  │   │Clean up  │ │  │
│  │  │test │   │minimum│   │all pass  │ │  │
│  │  └─────┘   └───────┘   └──────────┘ │  │
│  │                                      │  │
│  │  Governance gates enforced           │  │
│  │  Audit trail recorded                │  │
│  │  Result returned to user             │  │
│  └──────────────────────────────────────┘  │
└───────────────────┬────────────────────────┘
                    │
                    ▼
              STRUCTURED RESPONSE
              ┌──────────────────┐
              │ • Implementation │
              │ • Tests written  │
              │ • Tests passing  │
              │ • Audit ID       │
              └──────────────────┘
```

---

## Intent Routing Map

```
IntentRouter
    │
    ├── IMPLEMENT ──→ TDDOrchestrator
    ├── FIX ────────→ TDDOrchestrator
    ├── REFACTOR ───→ RefactoringOrchestrator
    ├── ANALYZE ────→ LENSSynthesis
    ├── TEST ───────→ TDDOrchestrator
    ├── DEBUG ──────→ DebugOrchestrator
    ├── ONBOARD ────→ OnboardingOrchestrator
    ├── EXPLAIN ────→ ExplanationOrchestrator
    ├── REVIEW ─────→ ReviewOrchestrator
    ├── DEPLOY ─────→ DeploymentOrchestrator
    ├── SECURITY ───→ SecurityOrchestrator
    └── WORKFLOW ───→ WorkflowOrchestrator
```

---

*Verified against MasterOrchestrator 4-stage pipeline*
