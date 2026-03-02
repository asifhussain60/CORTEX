---
id: debugging-multi-stack-pipeline
title: Multi-stack debug pipeline (8 strategies)
purpose: Show how CORTEX debugs across 5 technology stacks with smart marker injection and automatic cleanup.
audience:
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/support/debugger_orchestrator.py
  - cortex/orchestrators/support/debugging/marker_injection_engine.py
  - cortex-registry/workflows/templates/debugging/multi-stack-debug-pipeline.yaml
last_verified: 2026-03-02
diagram_type: Workflow
render: ascii
---

# Multi-Stack Debug Pipeline — 8 Strategies Across 5 Stacks

## 5-Phase Debug Lifecycle

```
 ═══════════════════════════════════════════════════════════════════════════════
  /debug {path} — inject → capture → analyze → fix-plan → cleanup
 ═══════════════════════════════════════════════════════════════════════════════

  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ PHASE 1  │    │ PHASE 2  │    │ PHASE 3  │    │ PHASE 4  │    │ PHASE 5  │
  │          │    │          │    │          │    │          │    │          │
  │  INJECT  │───▶│ CAPTURE  │───▶│ ANALYZE  │───▶│ FIX-PLAN │───▶│ CLEANUP  │
  │          │    │          │    │          │    │          │    │          │
  │ Smart    │    │ Run with │    │ Collect  │    │ Generate │    │ Remove   │
  │ markers  │    │ markers  │    │ output + │    │ root     │    │ ALL      │
  │ inserted │    │ active   │    │ evidence │    │ cause +  │    │ markers  │
  │ per      │    │          │    │          │    │ fix      │    │ auto     │
  │ strategy │    │          │    │          │    │ steps    │    │          │
  └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

## 8 Debug Strategies — Auto-Selected by Stack Detection

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  PYTHON STRATEGIES (3)                                                  │
  │                                                                         │
  │  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐  │
  │  │ TestFailure        │  │ RefactorRegression │  │ Governance       │  │
  │  │                    │  │                    │  │ Violation        │  │
  │  │ Failing pytest     │  │ Tests broke after  │  │ CORE rule       │  │
  │  │ → trace + assert   │  │ refactor → diff    │  │ breach → audit  │  │
  │  │   analysis         │  │   analysis         │  │   trace          │  │
  │  └────────────────────┘  └────────────────────┘  └──────────────────┘  │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  MULTI-STACK STRATEGIES (5)                                             │
  │                                                                         │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
  │  │  Frontend    │  │  HTML-Vision │  │  API Trace   │                  │
  │  │  Console     │  │  Mapping     │  │              │                  │
  │  │              │  │              │  │  REST /      │                  │
  │  │  JS/TS/React │  │  Vision API  │  │  GraphQL /   │                  │
  │  │  Angular/Vue │  │  screenshot  │  │  gRPC        │                  │
  │  │  console.log │  │  → CSS → DOM │  │  req/resp +  │                  │
  │  │  + DOM events│  │  correlation │  │  headers     │                  │
  │  └──────────────┘  └──────────────┘  └──────────────┘                  │
  │                                                                         │
  │  ┌──────────────┐  ┌──────────────┐                                    │
  │  │  SQL Trace   │  │  .NET Trace  │                                    │
  │  │              │  │              │                                    │
  │  │  SQL Server  │  │  C# method   │                                    │
  │  │  Oracle      │  │  entry/exit  │                                    │
  │  │  PostgreSQL  │  │  DI + middle │                                    │
  │  │  query plan  │  │  ware +      │                                    │
  │  │  + params    │  │  async trace │                                    │
  │  └──────────────┘  └──────────────┘                                    │
  └─────────────────────────────────────────────────────────────────────────┘
```

## Auto-Cleanup Guarantee

```
  After debugging:
    /debug-cleanup
         │
         ▼
  AutoCleanupManager scans ALL files
         │
         ▼
  Per-language strip patterns remove CORTEX_DEBUG markers
         │
         ├── Python:    # CORTEX_DEBUG markers
         ├── JS/TS:     // CORTEX_DEBUG markers
         ├── C#:        // CORTEX_DEBUG markers
         ├── SQL:       -- CORTEX_DEBUG markers
         └── HTML:      <!-- CORTEX_DEBUG --> markers
         │
         ▼
  Convergence: no_orphaned_markers == true → CLEAN ✅
```

**Business impact:** Debug any technology stack without switching tools. All debug instrumentation is automatically removed — zero risk of debug code reaching production.
