---
id: orchestration-po-change-intelligence-pipeline
title: Product Owner Change Intelligence Pipeline
purpose: Show how CORTEX supports PO decision-making through a structured pipeline — from process discovery through gap analysis, change recommendations, requirements synthesis, and training documentation generation.
audience:
  - Business Leaders
  - Product Owners
source_of_truth:
  - cortex/orchestrators/domain/change_intelligence_orchestrator.py
  - cortex/orchestrators/domain/requirements_orchestrator.py
  - cortex-registry/workflows/templates/po/
last_verified: 2026-03-08
diagram_type: Orchestration
render: ascii
render_html: true
d3_method: "d3.tree() horizontal — 6-stage pipeline with branching sub-workflows"
---

# Product Owner Change Intelligence Pipeline

## From Stakeholder Question to Actionable Intelligence

```
 ═══════════════════════════════════════════════════════════════════════════════
  "Should we build this?" → CHANGE_INTELLIGENCE (0.94) → Evidence-Based Decision
 ═══════════════════════════════════════════════════════════════════════════════

  PO Request (natural language)
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │                   INTENT CLASSIFICATION                              │
  │                                                                      │
  │  "What does the system do?"        → CHANGE_INTELLIGENCE             │
  │  "Compare to best practice"        → CHANGE_INTELLIGENCE             │
  │  "What's the ROI of this change?"  → CHANGE_INTELLIGENCE             │
  │  "Should we build this idea?"      → CHANGE_INTELLIGENCE             │
  │  "Generate requirements"           → REQUIREMENTS                    │
  │  "Create training docs"            → DIGEST (po_training mode)       │
  └──────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │               CHANGE INTELLIGENCE ORCHESTRATOR                       │
  │                                                                      │
  │  ┌─────────────┐    ┌─────────────────┐    ┌──────────────────┐     │
  │  │  PROCESS     │    │  BEST-PRACTICE  │    │  CAPABILITY      │     │
  │  │  DISCOVERY   │───▶│  COMPARISON     │    │  SUMMARY         │     │
  │  │              │    │                 │    │                  │     │
  │  │  LENS scan   │    │  Gap analysis   │    │  System          │     │
  │  │  AST parse   │    │  Severity score │    │  inventory       │     │
  │  │  Pattern     │    │  Best-practice  │    │  Feature map     │     │
  │  │  extraction  │    │  alignment      │    │  Module tree     │     │
  │  └──────┬───────┘    └────────┬────────┘    └──────────────────┘     │
  │         │                     │                                      │
  │         ▼                     ▼                                      │
  │  ┌─────────────┐    ┌─────────────────┐                             │
  │  │  CHANGE      │    │  ROI            │                             │
  │  │  RECOMMEND.  │    │  ANALYSIS       │                             │
  │  │              │    │                 │                             │
  │  │  Impact      │    │  LOE→ROI        │                             │
  │  │  assessment  │    │  conversion     │                             │
  │  │  Challenge   │    │  Composite      │                             │
  │  │  gate (≥2    │    │  scoring        │                             │
  │  │  alternatives│    │  Priority tier  │                             │
  │  │  w/ tradeoff)│    │  projection     │                             │
  │  └──────────────┘    └─────────────────┘                             │
  └──────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │               REQUIREMENTS ORCHESTRATOR                              │
  │                                                                      │
  │  Stakeholder Intent                                                  │
  │         │                                                            │
  │         ▼                                                            │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
  │  │  Business    │  │  Functional │  │  Non-Func.  │  │ Acceptance│  │
  │  │  Requirements│  │  Requirements│  │  Requirements│  │ Criteria  │  │
  │  │             │  │             │  │             │  │           │  │
  │  │  Business   │  │  Behaviour  │  │  Performance│  │  Given/   │  │
  │  │  value      │  │  specs      │  │  Security   │  │  When/    │  │
  │  │  Outcome    │  │  API        │  │  Scalability│  │  Then     │  │
  │  │  KPIs       │  │  contracts  │  │  A11y       │  │  TDD-     │  │
  │  │             │  │             │  │             │  │  ready    │  │
  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
  │         │                │                │               │         │
  │         └────────────────┴────────────────┴───────────────┘         │
  │                          │                                          │
  │                   DoR Validation                                    │
  └──────────────────────────┬──────────────────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │                TDD PIPELINE (existing)                               │
  │  RED → GREEN → REFACTOR → Governance Gates → DoD                    │
  └──────────────────────────┬──────────────────────────────────────────┘
                             │
                             ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │              TRAINING DOC GENERATION                                  │
  │                                                                      │
  │  LENS diff analysis → Role-based materials → ContentLibraryEngine   │
  │  Output: Training documents per affected role                       │
  └──────────────────────────────────────────────────────────────────────┘
```

## Traceability Spine

```
  Process Discovery → Best-Practice Comparison → Change Recommendation
         │                                              │
         ▼                                              ▼
  Requirements Synthesis ──── Implementation (TDD) ──── Training Docs
```

Each artifact in the chain carries a forward reference to the next — providing full
traceability from "what does the system do today?" through "what did we change and why?"
to "how do we train teams on the change?"

## Workflow Templates (7 in `po/` category)

| Template | Stage | Reused Components |
|---|---|---|
| `process-discovery.yaml` | Discovery | LENS AST scan, intelligence injection |
| `best-practice-comparison.yaml` | Analysis | `gap-comparison` primitive, `cortex_knowledge` |
| `change-recommendation.yaml` | Decision | `impact-assessment`, `challenge-gate` |
| `roi-analysis.yaml` | Evaluation | `ROICompositeScorer` adaptation |
| `requirements-synthesis.yaml` | Specification | `sdlc/requirements-analysis`, `holistic-validation-gate` |
| `training-doc-generation.yaml` | Knowledge | LENS diff analysis, `ContentLibraryEngine` |
| `capability-summary.yaml` | Inventory | `process-discovery`, `cortex_git` |

## New Primitive

| Primitive | Purpose |
|---|---|
| `primitives/analysis/gap-comparison.yaml` | Compare current-state model against target-state pattern; produce structured gap list with severity scores |

**Business impact:** Product Owners make decisions backed by real codebase intelligence — not subjective estimates. Every recommendation includes a traceability chain from process discovery through implementation to training, ensuring changes are understood, approved, built correctly, and documented for the team.
