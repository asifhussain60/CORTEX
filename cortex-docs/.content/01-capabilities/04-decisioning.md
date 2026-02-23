# Decisioning Capabilities

---
title: CORTEX Decisioning — Intent Routing & TDD Enforcement
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-20
source_of_truth: cortex/orchestrators/core/intent_router.py + cortex/orchestrators/core/tdd_orchestrator.py
order: 4
---

> **Brain analogy:** Decisioning is the **thalamus** — the relay station at the centre of the brain that routes every sensory signal to the correct processing region. Without it, signals go nowhere. IntentRouter is CORTEX's thalamus — every request must pass through it.

---

## IntentRouter

**Location:** `cortex/orchestrators/core/intent_router.py`

IntentRouter classifies every request into one of 12+ intent types using LENS-based classification (20–40ms):

| Intent | Routed To | What Happens |
|--------|-----------|-------------|
| **IMPLEMENT** | TDDOrchestrator | RED → GREEN → REFACTOR (new feature) |
| **FIX** | TDDOrchestrator | RED → GREEN → REFACTOR (bug repair) |
| **REFACTOR** | RefactoringOrchestrator | Semantic code improvement |
| **ANALYZE** | LENS Synthesis | 8-analyzer parallel scan |
| **PLAN** | PlanningOrchestrator | Development roadmap creation |
| **AUDIT** | EnforcementOrchestrator | Governance compliance check |
| **DESIGN** | Design coordination | Architecture decisions |
| **DEBUG** | DebuggerOrchestrator | Problem diagnosis |
| **INVESTIGATE** | IntelligenceOrchestrator | Deep analysis |
| **QUERY** | Context-dependent | Information retrieval |
| **DIGEST** | Digest Coordinator | Topic summarization |
| **REPHRASE** | RequestRephraseOrchestrator | Request refinement |

**Business Leader:** "Every request gets classified automatically. There's no ambiguity about which team or process handles it — the router decides in 20ms."

**Product Owner:** "I can track which intent types are most common across my team. If 70% are FIX requests, that tells me something about code quality."

**Developer:** "I don't need to know which orchestrator to call. I describe what I want, and IntentRouter figures out the rest."

---

## TDD Workflow Enforcement (CORE-008)

**Location:** `cortex/orchestrators/core/tdd_orchestrator.py`

Every IMPLEMENT and FIX operation follows **mandatory** RED → GREEN → REFACTOR:

```
┌──────────────────────────────────────────────────┐
│                TDD CYCLE (CORE-008)               │
│                                                  │
│  ┌─────────┐      ┌─────────┐      ┌──────────┐ │
│  │   RED   │─────▶│  GREEN  │─────▶│ REFACTOR │ │
│  │ Write   │      │ Write   │      │ Improve  │ │
│  │ failing │      │ minimum │      │ code,    │ │
│  │ test    │      │ code to │      │ tests    │ │
│  │         │      │ pass    │      │ still    │ │
│  │         │      │         │      │ pass     │ │
│  └─────────┘      └─────────┘      └──────────┘ │
│       ▲                                    │     │
│       └────────────────────────────────────┘     │
│              (next feature / next fix)           │
└──────────────────────────────────────────────────┘
```

**This is not optional.** CORE-008 is enforced at the architecture level by EnforcementOrchestrator. If you try to implement without a failing test, the governance gate blocks the operation.

**Business Leader:** "TDD isn't a suggestion — it's architecturally enforced. Every commit has tests written first. Technical debt doesn't accumulate silently."

**Product Owner:** "I never need to ask 'did they write tests?' The system enforces it. The TestQualityGate scores each test 0–9, so I also know the tests are meaningful."

**Developer:** "TDDOrchestrator handles the cycle for me. It writes the failing test (RED), implements minimum code (GREEN), and prompts me to refactor. All three phases are tracked and audited."

---

## Challenge Engine

Before high-impact operations, CORTEX's Challenge Engine performs a LENS analysis to:

- Assess the risk of the proposed change
- Identify potential breaking changes
- Surface governance considerations
- Recommend whether to proceed, review, or abort

**MCP Tool:** `cortex_challenge` — callable from any IDE.

---

*All paths verified against live codebase · 20 February 2026*
