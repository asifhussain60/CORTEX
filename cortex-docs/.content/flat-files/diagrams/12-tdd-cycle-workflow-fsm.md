# TDD Cycle & Workflow Engine FSM
# RED → GREEN → REFACTOR cycle and WorkflowEngine state machine

```
                    ┌──────────────────────────────────────────────────────┐
                    │              TDD CYCLE (CORE-008)                    │
                    │                                                      │
                    │       ┌──────────────────────┐                       │
                    │       │                      │                       │
                    │       ▼                      │                       │
                    │  ┌─────────┐            ┌────┴───────┐               │
                    │  │         │            │            │               │
                    │  │   RED   │───────────→│  REFACTOR  │               │
                    │  │         │            │            │               │
                    │  │ 1. Write│   ┌────┐   │ 3. Improve │               │
                    │  │ failing │   │    │   │ code while │               │
                    │  │ test    │   │    │   │ all tests  │               │
                    │  │ (define │   │    │   │ still pass │               │
                    │  │ desired │   │    │   │            │               │
                    │  │ behav.) │   │    │   │ Clean up   │               │
                    │  └────┬────┘   │    │   │ Simplify   │               │
                    │       │        │    │   │ Optimize   │               │
                    │       ▼        │    │   └────────────┘               │
                    │  ┌─────────┐   │    │                                │
                    │  │         │   │    │                                │
                    │  │  GREEN  │───┘    │                                │
                    │  │         │        │                                │
                    │  │ 2. Write│────────┘                                │
                    │  │ minimum │                                         │
                    │  │ code to │   Governance gates checked at each      │
                    │  │ pass    │   step boundary by Enforcement          │
                    │  │ test    │   Orchestrator                          │
                    │  └─────────┘                                         │
                    │                                                      │
                    │  Enforced by: TDDOrchestrator + CORE-008             │
                    │  Applies to: IMPLEMENT, FIX intents                  │
                    └──────────────────────────────────────────────────────┘


                    ┌──────────────────────────────────────────────────────┐
                    │           WORKFLOW ENGINE FSM                        │
                    │           cortex/core/workflow_engine.py             │
                    │                                                      │
                    │  Workflow templates loaded from:                      │
                    │  cortex-registry/workflows/templates/                │
                    │                                                      │
                    │  ┌──────────┐                                        │
                    │  │ PENDING  │────────────────────────┐               │
                    │  │          │                        │               │
                    │  │ Step     │                        │               │
                    │  │ loaded   │                        │               │
                    │  └────┬─────┘                        │               │
                    │       │                              │               │
                    │       │ start()                      │               │
                    │       ▼                              │               │
                    │  ┌──────────┐                        │               │
                    │  │ RUNNING  │                        │               │
                    │  │          │                        │               │
                    │  │ Handler  │                        │               │
                    │  │ executing│                        │               │
                    │  └────┬─────┘                        │               │
                    │       │                              │               │
                    │       │ handler complete             │ error          │
                    │       ▼                              ▼               │
                    │  ┌──────────┐                  ┌──────────┐          │
                    │  │ CHECKING │                  │  FAILED  │          │
                    │  │          │                  │          │          │
                    │  │ Validate │                  │ Rollback │          │
                    │  │ output   │                  │ applied  │          │
                    │  └────┬─────┘                  └──────────┘          │
                    │       │                                              │
                    │       │ validation pass                              │
                    │       ▼                                              │
                    │  ┌──────────┐                                        │
                    │  │  PASSED  │                                        │
                    │  │          │                                        │
                    │  │ Next step│                                        │
                    │  │ or done  │                                        │
                    │  └──────────┘                                        │
                    │                                                      │
                    │  StepHandlerRegistry maps type IDs → callables       │
                    │  ConvergenceLoopExecutor: detect → fix → rescan      │
                    └──────────────────────────────────────────────────────┘
```
