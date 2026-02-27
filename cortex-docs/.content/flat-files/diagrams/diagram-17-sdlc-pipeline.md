# SDLC Workflow Pipeline — 7-Phase Lifecycle
# Full SDLC execution from requirements through release with security gates at every phase

```
 ═══════════════════════════════════════════════════════════════════════════════
  CORTEX SDLC WORKFLOW ENGINE — 7-PHASE PIPELINE
 ═══════════════════════════════════════════════════════════════════════════════

  SDLCWorkflowOrchestrator (cortex/orchestrators/domain/sdlc_workflow_orchestrator.py)
  Templates: cortex-registry/workflows/templates/sdlc/
  Knowledge: cortex-registry/knowledge/sdlc/

 ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
 │    1.    │  │    2.    │  │    3.    │  │    4.    │  │    5.    │  │    6.    │  │    7.    │
 │REQUIRE- │─▶│SOLUTION  │─▶│IMPLEMENT │─▶│  CODE   │─▶│INTEGRA- │─▶│SECURITY │─▶│ RELEASE │
 │ MENTS   │  │ DESIGN   │  │ ATION    │  │ REVIEW  │  │  TION   │  │ ASSESS  │  │READINESS│
 │ANALYSIS │  │          │  │          │  │  GATE   │  │ VERIFY  │  │  MENT   │  │         │
 └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
      │              │              │              │              │              │              │
   🔒 SEC         🔒 SEC         🔒 SEC         🔒 SEC         🔒 SEC         🔒 SEC         🔒 SEC
   GATE            GATE            GATE            GATE            GATE            GATE            GATE
      │              │              │              │              │              │              │
   BLOCK-         BLOCK-         BLOCK-         BLOCK-         BLOCK-         BLOCK-         BLOCK-
   ANALYSIS       DESIGN-        CODE-          CODE-          INTEGRA-       SECURITY       RELEASE
                  DECISION       REVIEW         REVIEW         TION


 ═══════════════════════════════════════════════════════════════════════════════
  KNOWLEDGE HYDRATION — How Templates Get Intelligence
 ═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────┐
  │   SDLC Workflow         │
  │   Template (.yaml)      │
  │                         │
  │  knowledge_context:     │───────┐
  │    primary: "sdlc/..."  │       │    Resolution Order:
  │    supplementary: [...]│        │    ┌───────────────────┐
  │    company_overrides:   │       ├───▶│ 1. Company (wins) │
  │    resolution_order:    │       │    │ 2. Stack-specific │
  └─────────────────────────┘       │    │ 3. SDLC phase     │
                                    │    │ 4. Domain          │
  ┌─────────────────────────┐       │    │ 5. Generic         │
  │ cortex-registry/        │◀──────┘    └───────────────────┘
  │   knowledge/            │
  │   ├── sdlc/             │
  │   │   ├── analysis-*    │
  │   │   ├── security-*    │
  │   │   └── stack-specific│
  │   ├── architecture/     │
  │   ├── security/         │
  │   └── testing-*/        │
  └─────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  FSM EXECUTION — WorkflowEngine State Machine
 ═══════════════════════════════════════════════════════════════════════════════

  ┌─────────┐    ┌─────────┐    ┌───────────┐
  │ PENDING │───▶│ RUNNING │───▶│ COMPLETED │
  └─────────┘    └────┬────┘    └───────────┘
                      │
                      ├───▶ ┌────────┐    ┌───────┐
                      │     │ FAILED │───▶│ RETRY │──┐
                      │     └────────┘    └───────┘  │
                      │                              │
                      │          ┌───────────┐       │
                      └──── ───▶│  BLOCKED  │       │
                                │ (gate fail│       │
                                └───────────┘       │
                      ┌─────────────────────────────┘
                      ▼
                 ┌─────────┐
                 │ RUNNING │ (retry attempt)
                 └─────────┘

  Each step transition emits: AC_START → execution → AC_COMPLETE
  All recorded to: .cortex-runtime/traces/orchestrator-traces.db
```

**Source:** `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py` · `cortex-registry/workflows/templates/sdlc/`
**Governance:** CORE-008 (TDD at Phase 3), CORE-064 (Sweep Completeness at every phase)
