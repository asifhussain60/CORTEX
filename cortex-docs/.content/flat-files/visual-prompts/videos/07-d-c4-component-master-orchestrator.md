---
id: 07-d-c4-component-master-orchestrator
title: Master Orchestrator Internal Components
purpose: Detailed view of Master Orchestrator's internal structure and routing logic — VIDEO 07 deep-dive diagram
audience: [Software Developers]
source_of_truth: cortex/orchestrators/core/master_orchestrator.py + cortex/intelligence/provider.py
last_verified: 2026-02-27
diagram_type: C4-Component
interactive: false
tier: 3
learning_sequence: 23
video_prompt: 07-p-cross-domain-intelligence.md
video_scene: "Scene 3 supplement — internal component view when zooming into the Master Orchestrator"
animation_notes: |
  ## Cinematic Simulation Prompt — 07b: Master Orchestrator Internals

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. CORTEX logo fades in with electric-aura glow. Hold 4s.
  Logo shrinks to bottom-right watermark.

  **SCENE 2 — "FPV Drone Dive: Into the Orchestrator" (0:06–0:14)**
  Camera: Start zoomed out showing the full dispatch flow as a distant glassmorphism
  cityscape. FPV drone accelerates toward the Master Orchestrator node — a large frosted
  Deep Cobalt cube with purple neon filaments. Drone punches through the glass surface
  (shatter-refraction effect) and enters the interior: a vast Midnight Blue vacuum with
  internal component nodes.

  **SCENE 3 — "Component Cascade" (0:14–0:26)**
  Internal components materialize as frosted glassmorphism capsules. Entry Point glows
  green — a bioluminescent request particle spawns and flows:
  Entry Point → Request Validator (cyan pulse) → Intent Classifier → Intelligence Layer
  (UIP, CDL, ADOCtx, KGIdx light up with cyan filaments and Lidar laser sweeps).
  Intelligence Layer feeds Orchestrator Router (amber glow).

  **SCENE 4 — "The Routing Decision" (0:26–0:36)**
  Router fans out five glassmorphism paths to target orchestrators. ONE path illuminates
  (purple neon); others dim to 20%. LearningMixin pulses purple on completion — confidence
  score animates. ErrorHandler shown as dotted red ghost trail.

  **SCENE 5 — "Orbital Reveal" (0:36–0:46)**
  Camera: Pulls out through the glass wall (reverse shatter-refraction). 360-degree
  orbital pan around the Master Orchestrator cube — internal components visible through
  frosted glass. Glassmorphism "Evidence Bundle" icon materializes — sealed document with
  cyan checkmark — fades to black.
related_diagrams:
  - 07-d-orchestrator-dispatch-flow.md
  - 01-d-c4-container-full-system.md
---

## Master Orchestrator — Internal Components

### Component Map

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                    MASTER ORCHESTRATOR                               │
  │                                                                      │
  │  External: MCP Gateway ──────────────────────────────────────────┐  │
  │                                                                   │  │
  │                                                                   ▼  │
  │  ┌───────────────────────────────────────────────────────────────┐   │
  │  │  Entry Point  ◄── request arrives here                        │   │
  │  └──────────────────────┬────────────────────────────────────────┘   │
  │                         │                                            │
  │                         ▼                                            │
  │  ┌───────────────────────────────────────────────────────────────┐   │
  │  │  Request Validator   (schema, protocol, auth)                 │   │
  │  └──────────────────────┬────────────────────────────────────────┘   │
  │                         │                                            │
  │                         ▼                                            │
  │  ┌───────────────────────────────────────────────────────────────┐   │
  │  │  Intent Classifier   ──────────────────►  Intent Router Svc   │   │
  │  └──────────────────────┬────────────────────────────────────────┘   │
  │                         │                                            │
  │                         ▼                                            │
  │  ┌────────────────────────────────────────────────────────────────┐  │
  │  │  Intelligence Layer                                            │  │
  │  │                                                                │  │
  │  │   ┌─────────────────────────────────────────────┐             │  │
  │  │   │  UnifiedIntelligenceProvider (UIP)           │             │  │
  │  │   └────┬────────────┬──────────────┬────────────┘             │  │
  │  │        │            │              │                           │  │
  │  │        ▼            ▼              ▼                           │  │
  │  │  ┌──────────┐ ┌──────────┐ ┌────────────┐                     │  │
  │  │  │CompanyDom│ │ADOContext│ │KnowledgeIdx│                     │  │
  │  │  │ Loader   │ │ Mapper   │ │  (KGIdx)   │                     │  │
  │  │  └──────────┘ └──────────┘ └────────────┘                     │  │
  │  └────────────────────────────────────┬───────────────────────────┘  │
  │                                       │                              │
  │                                       ▼                              │
  │  ┌────────────────────────────────────────────────────────────────┐  │
  │  │  Orchestrator Router   ──►   Orchestrator Registry             │  │
  │  └──────────────────────────────────────┬─────────────────────────┘  │
  │                                         │                            │
  │                                         ▼                            │
  │  ┌────────────────────────────────────────────────────────────────┐  │
  │  │  Execution Dispatcher                                          │  │
  │  │      │                                                         │  │
  │  │      ├──► Governance Engine check ──► (approved / rejected)   │  │
  │  │      │                                                         │  │
  │  │      ├──► OnboardingOrchestrator                               │  │
  │  │      ├──► TDDOrchestrator                                      │  │
  │  │      ├──► PlanningOrchestrator                                 │  │
  │  │      ├──► SweepCatalogueOrchestrator                           │  │
  │  │      └──► Domain Orchestrators                                 │  │
  │  └──────────────────────────────────┬─────────────────────────────┘  │
  │                                     │                                │
  │               ┌─────────────────────┴──────────────┐                │
  │               │                                    │                │
  │               ▼                                    ▼                │
  │  ┌─────────────────────────┐         ┌──────────────────────────┐   │
  │  │  Learning Mixin         │         │  Error Handler           │   │
  │  │  (URS confidence update)│         │  (retry / escalate)      │   │
  │  └─────────────────────────┘         └──────────────────────────┘   │
  └──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

```
  ┌──────────────────────────┬───────────────────────────────────────────┐
  │ Entry Point              │ MCP Gateway hands off request here        │
  │ Request Validator        │ Protocol, schema, auth checks             │
  │ Intent Classifier        │ Determines what kind of work to do        │
  │ Intent Router Svc        │ External service — maps intent to orch.   │
  │ UIP                      │ Loads context (quick / targeted / full)   │
  │ CompanyDomainLoader      │ Overlays org-specific knowledge           │
  │ ADOContextMapper         │ Azure DevOps sprint + work item context   │
  │ KnowledgeIndexer         │ Cross-repo knowledge graph index          │
  │ Orchestrator Router      │ Selects the right orchestrator            │
  │ Orchestrator Registry    │ Registry of all 51 wired orchestrators    │
  │ Execution Dispatcher     │ Runs the selected orchestrator            │
  │ Governance Engine        │ 38 CORE rules checked before execution    │
  │ Learning Mixin           │ Captures outcome → URS confidence update  │
  │ Error Handler            │ Catches failures, retries, escalates      │
  └──────────────────────────┴───────────────────────────────────────────┘
```
