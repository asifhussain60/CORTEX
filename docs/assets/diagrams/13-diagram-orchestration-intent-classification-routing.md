---
id: orchestration-intent-classification-routing
title: Intent classification and orchestrator routing
purpose: Show how CORTEX classifies user requests into 30+ intent types and routes them to specialized orchestrators with confidence-based decisions.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/core/intent_router.py
  - cortex/models/canonical_enums.py
last_verified: 2026-03-03
diagram_type: Orchestration
render: ascii
render_html: true
d3_method: "d3.forceSimulation() — intent nodes with orchestrator routing edges"
---

# Intent Classification & Orchestrator Routing

## From Natural Language to Specialized Execution

```
 ═══════════════════════════════════════════════════════════════════════════════
  "Fix the auth bug" → FIX (0.92) → TDDOrchestrator → Bug resolved with tests
 ═══════════════════════════════════════════════════════════════════════════════

  User Request (natural language)
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │                     INTENT ROUTER                                    │
  │                                                                      │
  │  Keyword matching + context analysis → confidence score              │
  │                                                                      │
  │  ┌──────────────────────────────────────────────────────────────┐    │
  │  │  30+ Intent Types:                                           │    │
  │  │                                                              │    │
  │  │  CODE-TOUCHING          NON-CODE              LIFECYCLE      │    │
  │  │  ⚡ IMPLEMENT           📖 QUERY              📚 DIGEST     │    │
  │  │  🔧 FIX                 🎨 DESIGN             🔄 SYNC       │    │
  │  │  ♻️ REFACTOR            📋 PLAN               🎓 TRAIN      │    │
  │  │  🔎 AUDIT               💬 REPHRASE           🔁 TOTALRECALL│    │
  │  │  🐛 DEBUG               🔬 INVESTIGATE        👋 INTRODUCE  │    │
  │  │  🧹 VACUUM              🧠 RCA                              │    │
  │  │  🩺 HEALTH              🥇 GOLDEN_TEST        REVIEWING     │    │
  │  │                          🔧🔄 WORKFLOW_COMPOSE 👁️ REVIEW     │    │
  │  │                                                💬 FEEDBACK   │    │
  │  └──────────────────────────────────────────────────────────────┘    │
  └──────────────────────────┬───────────────────────────────────────────┘
                             │
                     Confidence score
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
      ≥ 0.85            0.60–0.84          < 0.60
      DIRECT             CLARIFY           REPHRASE
           │                 │                 │
           ▼                 ▼                 ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │ Route to     │  │ Route +      │  │ Ask user to  │
  │ domain       │  │ append       │  │ rephrase     │
  │ orchestrator │  │ clarification│  │ before       │
  │ immediately  │  │ question     │  │ routing      │
  └──────┬───────┘  └──────────────┘  └──────────────┘
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │                   ORCHESTRATOR ROUTING MAP                           │
  │                                                                      │
  │  Intent          Orchestrator                 Pre-gate               │
  │  ──────          ────────────                 ────────               │
  │  IMPLEMENT ───── TDDOrchestrator ──────────── Holistic Validation   │
  │  FIX ─────────── TDDOrchestrator ──────────── Holistic Validation   │
  │  REFACTOR ────── RefactoringOrchestrator ──── Holistic Validation   │
  │  AUDIT ────────  AuditCoordinator ─────────── (none)                │
  │  DEBUG ────────  DebuggerOrchestrator ──────── (none)                │
  │  DESIGN ──────── DesignCoordinator ─────────── (none)                │
  │  PLAN ─────────  PlanningCoordinator ────────── (none)               │
  │  QUERY ────────  QueryCoordinator ──────────── (none)                │
  │  VACUUM ──────── VacuumOrchestrator ─────────── (none)               │
  │  INTRODUCE ────  InteractionOrchestrator ────── (none)               │
  └──────────────────────────────────────────────────────────────────────┘
```

## MCP Tiered Blocking (CORE-050)

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Tier 0 (BLOCK):  IMPLEMENT, FIX, REFACTOR, AUDIT                  │
  │                    → Cannot proceed without MCP active              │
  │                                                                     │
  │  Tier 1 (WARN):   QUERY, DIGEST, DESIGN, PLAN                      │
  │                    → Warning shown, can proceed degraded            │
  │                                                                     │
  │  Tier 2 (SILENT): REPHRASE                                          │
  │                    → No MCP needed                                  │
  └─────────────────────────────────────────────────────────────────────┘
```

**Business impact:** Every request is understood, classified, and routed to the right specialist — no manual selection required. 30+ intent types covering the complete engineering lifecycle, from first implementation through root cause analysis and self-healing governance.
