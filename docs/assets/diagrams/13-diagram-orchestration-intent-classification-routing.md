---
id: orchestration-intent-classification-routing
title: Intent classification and orchestrator routing
purpose: Show how CORTEX classifies user requests into 33+ intent types and routes them to specialized orchestrators with confidence-based decisions.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/core/intent_router.py
  - cortex/models/canonical_enums.py
last_verified: 2026-03-08
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
  │  │  32+ Intent Types:                                           │    │
  │  │                                                              │    │
  │  │  CODE-TOUCHING          NON-CODE              LIFECYCLE      │    │
  │  │  ⚡ IMPLEMENT           📖 QUERY              📚 DIGEST     │    │
  │  │  🔧 FIX                 🎨 DESIGN             🔄 SYNC       │    │
  │  │  ♻️ REFACTOR            📋 PLAN               🎓 TRAIN      │    │
  │  │  🔎 AUDIT               💬 REPHRASE           🔁 TOTALRECALL│    │
  │  │  🐛 DEBUG               🔬 INVESTIGATE        👋 INTRODUCE  │    │
  │  │  🧹 VACUUM              🧠 RCA                              │    │
  │  │  🩺 HEALTH              🥇 GOLDEN_TEST        DECISION      │    │
  │  │                          🔧🔄 WORKFLOW_COMPOSE � CHANGE_INT │    │
  │  │                                                📝 REQUIREMTS │    │
  │  │                          REVIEWING                           │    │
  │  │                          👁️ REVIEW                           │    │
  │  │                          💬 FEEDBACK                         │    │
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
  │  PLAN ─────────  PlanningCoordinator / CAPE ─── CDR Triage          │
  │  QUERY ────────  QueryCoordinator ──────────── (none)                │
  │  VACUUM ──────── VacuumOrchestrator ─────────── (none)               │
  │  INTRODUCE ────  InteractionOrchestrator ────── (none)               │
  │  REVIEW ───────  CodeReviewOrchestrator ──────── (none)              │
  │  FEEDBACK ─────  FeedbackOrchestrator ─────────── (none)             │
  │  CHANGE_INT ───  ChangeIntelligenceOrchestrator ─ Challenge Gate     │
  │  REQUIREMENTS ─  RequirementsOrchestrator ──────── Holistic Valid.   │
  │  PO_TRAINING ──  DigestOrchestrator (po_training) ─ (none)          │
  └──────────────────────────────────────────────────────────────────────┘
```

## CAPE — Autonomous Planning for COMPLEX Requests

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │  ComplexityTriageEngine scores every PLAN/IMPLEMENT request          │
  │                                                                      │
  │  CDR Score:  clarity(0.25) + context(0.20) + scope(0.25)            │
  │              + risk(0.20) + precedent(0.10) = composite [0,1]       │
  │                                                                      │
  │  Routing:  ≥0.70 → DIRECT (no planning needed)                      │
  │            0.50–0.70 → MICRO_PLAN (light decomposition)              │
  │            0.30–0.50 → FULL_PLAN (CAPE 11-stage pipeline)            │
  │            < 0.30 → ESCALATION (human review required)              │
  │                                                                      │
  │  FULL_PLAN pipeline: Scaffold → TopologicalSort (Kahn's) →          │
  │    ThreatGate → QualityGate → SecurityGate → RCAGate → OPJGate →   │
  │    StabilizationInject → CompletionChecklist (7 items)              │
  └─────────────────────────────────────────────────────────────────────┘
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

**Business impact:** Every request is understood, classified, and routed to the right specialist — no manual selection required. 33+ intent types covering the complete engineering lifecycle, from autonomous planning and PO decision support through implementation, root cause analysis, and self-healing governance.
