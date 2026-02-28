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

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) exterior; Midnight Blue (#0d1234) interior vacuum
  - **Orchestrator cube:** Deep Cobalt frosted glassmorphism with purple neon filaments
  - **Entry effect:** Shatter-refraction — glass surface fractures with ray-traced light dispersion
  - **Lighting:** Internal volumetric glow, bioluminescent capsules, Lidar sweeps, ray-traced caustics
  - **Feedback cues:** Green pulse = entry confirmed, cyan Lidar = intelligence scan, purple pulse = learning signal

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on ray-traced glassmorphism floor.
  Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric fog at ground level.
  CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
  glow — cyan and purple pulse radiates outward. Ray-traced reflections shimmer on the
  floor. Hold 4s.
  Logo shrinks to bottom-right watermark (15% opacity) with ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: Into the Orchestrator" (0:06–0:14)**
  Camera: Start zoomed out showing the full dispatch flow as a distant glassmorphism
  cityscape — multiple buildings, conduit highways, particle traffic visible in miniature.
  FPV drone accelerates toward the Master Orchestrator node — a large frosted Deep Cobalt
  cube with purple neon filaments casting volumetric light into surrounding fog.
  Drone reaches terminal velocity — motion blur on peripheral fog particles. The drone
  punches through the glass surface: shatter-refraction effect — glass fractures into
  prismatic shards, each shard casting ray-traced spectral light (rainbow caustics
  scatter briefly before reforming). The camera enters the interior: a vast Midnight
  Blue vacuum (#0d1234) with internal component nodes suspended in volumetric haze.
  Interior atmosphere: darker, more intimate — fog is denser, neon is brighter.

  **SCENE 3 — "Component Cascade" (0:14–0:26)**
  Camera: Slow orbital dolly through the interior with parallax depth — closer components
  drift faster than distant ones. Internal components materialize as frosted glassmorphism
  capsules with time-lapse mechanical assembly — each capsule condensing from particles.
  Entry Point glows green with bioluminescent confirmation pulse. A bioluminescent
  request particle spawns and flows through the component chain:
  Entry Point → Request Validator (cyan pulse with Lidar validation sweep) → Intent
  Classifier (holographic prism splits white light into colored intent beams) →
  Intelligence Layer (UIP, CDL, ADOCtx, KGIdx light up sequentially with cyan neon
  filaments — each sub-component triggers a Lidar laser sweep that confirms connection
  with green flash and ray-traced caustics on adjacent capsules).
  Intelligence Layer feeds Orchestrator Router with amber neon conduit — particle
  transfers with bioluminescent trail. Each component's internal neon filaments pulse
  like living circuitry.

  **SCENE 4 — "The Routing Decision" (0:26–0:36)**
  Camera: Macro zoom into Router, then dolly pull-back to reveal fan-out.
  Router fans out five glassmorphism paths to target orchestrators — each path a frosted
  glass conduit with neon filaments. ONE path illuminates with purple neon at full
  brightness — particle flows down the selected path with bioluminescent wake trail.
  All other paths dim to 20% with neon cool-down animation.
  LearningMixin pulses purple on completion — confidence score animates as a holographic
  floating number "+0.05" with green neon glow, rising and fading. ErrorHandler shown
  as a dotted red ghost trail — translucent path with holographic glitch shimmer,
  visible but inactive (dormant safety net). Ray-traced reflections of the selected
  path's purple light play across the interior glass walls.

  **SCENE 5 — "Orbital Reveal" (0:36–0:46)**
  Camera: Pulls out through the glass wall — reverse shatter-refraction effect: glass
  shards converge and reform the cube surface, prismatic caustics collapse inward.
  360-degree orbital pan around the Master Orchestrator cube — internal components
  visible through frosted glass as bioluminescent silhouettes. Parallax depth: internal
  glow shifts as camera orbits, revealing different component arrangements from each angle.
  Ray-traced reflections of the cube's purple neon shimmer on the exterior glass floor.
  Glassmorphism "Evidence Bundle" icon materializes — sealed document with cyan checkmark
  and holographic shimmer — fades to black.
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
  │ Orchestrator Registry    │ Registry of all wired orchestrators (259 files, 9 domains) │
  │ Execution Dispatcher     │ Runs the selected orchestrator            │
  │ Governance Engine        │ 38 CORE rules checked before execution    │
  │ Learning Mixin           │ Captures outcome → URS confidence update  │
  │ Error Handler            │ Catches failures, retries, escalates      │
  └──────────────────────────┴───────────────────────────────────────────┘
```
