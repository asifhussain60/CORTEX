---
id: 07-d-orchestrator-dispatch-flow
title: Orchestrator Dispatch Flow — Intelligence Routing
purpose: Shows how the Master Orchestrator routes requests to specialized orchestrators via UnifiedIntelligenceProvider — VIDEO 07 hero diagram
audience: [Software Developers, Product Owners, Business Leaders]
source_of_truth: cortex/orchestrators/__wiring_contract__.yaml + cortex/intelligence/provider.py
last_verified: 2026-02-27
diagram_type: Flowchart
interactive: false
tier: 3
learning_sequence: 23
video_prompt: 07-p-cross-domain-intelligence.md
video_scene: "Scene 3 — The Three Brain Tiers (Perception → Reasoning → Action)"
animation_notes: |
  ## Cinematic Simulation Prompt — 07a: Orchestrator Dispatch Flow

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass pipeline surface
  - **Intelligence tiers:** Three concentric glassmorphism rings with graduated cyan intensity
  - **Lighting:** Volumetric fog, bioluminescent particle trails, ray-traced glass caustics
  - **Router decision:** Holographic diamond prism with light fan-out, selective neon path illumination
  - **Feedback cues:** Green pulse = validation pass, holographic glitch = error path, Lidar = intelligence scan

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on ray-traced glassmorphism floor.
  Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric fog at ground level.
  CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
  glow — cyan and purple pulse radiates outward. Ray-traced reflections on the floor. Hold 4s.
  Logo shrinks to bottom-right watermark (15% opacity) with ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: Request Entry" (0:06–0:12)**
  Camera: FPV drone arrives at the top of a vertical glassmorphism pipeline with
  parallax depth — foreground fog drifts faster than the pipeline behind it.
  MCP Request node glows green at the apex with bioluminescent pulse, casting volumetric
  light downward into the pipeline. A validation diamond appears with holographic surface
  shimmer — "Yes" path illuminates green with bioluminescent tracer, "No" path flashes
  red with holographic glitch effect and ghost particle trailing to Error node (translucent
  red, fading). Ray-traced light from the validation diamond casts prismatic caustics on
  adjacent pipeline surfaces.

  **SCENE 3 — "Intelligence Tiers" (0:12–0:24)**
  Camera: Slow dolly downward with orbital drift, tracking the particle's descent.
  The particle passes validation with a green pulse and enters Intent Classification.
  UnifiedIntelligenceProvider materializes as three concentric glassmorphism rings with
  time-lapse mechanical assembly:
  - Inner ring: "quick — <10ms" (thin cyan neon glow, minimal volumetric light)
  - Middle ring: "targeted — +company domains" (medium cyan glow, moderate volumetric light)
  - Outer ring: "full — +ADO sprint + KG index" (thick cyan neon glow, strong volumetric
    light with ray-traced caustics on all adjacent surfaces)
  Particle enters the appropriate tier based on request complexity — the selected ring
  ignites to full brightness with bioluminescent burst, other rings dim to 30% with
  slow neon cool-down. Lidar sweep confirms tier selection with green flash.

  **SCENE 4 — "The Routing Decision" (0:24–0:36)**
  Camera: Dolly-in to Router diamond, then pull-back to reveal orchestrator fan-out.
  Router diamond receives the particle — holographic prism surface refracts light into
  colored beams. Six orchestrator capsules fan out below as frosted glassmorphism nodes
  with domain-specific neon filaments. The particle follows ONE path — that capsule
  illuminates to full brightness with purple neon and bioluminescent internal glow;
  all others dim to 20% with neon cool-down. Selected orchestrator executes — internal
  neon filaments pulse with processing rhythm. Result feeds into Learning capture with
  a particle evolution: execution particle transforms from cyan to green, confidence
  score floats as holographic number. Bioluminescent trail persists as a permanent
  neon path with ray-traced reflections.

  **SCENE 5 — "Orbital Reveal" (0:36–0:46)**
  Camera: 360-degree orbital pan at 25° downward angle with parallax depth — pipeline
  rotates against volumetric fog backdrop. Bioluminescent trail persists as permanent
  neon path from entry to selected orchestrator — a standing wave of particle energy
  pulses along the trail. Ray-traced reflections of all components shimmer on the
  glass floor.
  Glassmorphism "Evidence Bundle" icon materializes — sealed document with cyan checkmark
  and holographic shimmer — fades to black.
related_diagrams:
  - 07-d-c4-component-master-orchestrator.md
  - 06-d-mcp-request-lifecycle-sequence.md
---

## Orchestrator Dispatch Flow — Intelligence Routing

### Main Dispatch Pipeline

```
                    ┌─────────────────┐
                    │   MCP Request   │  ◄── entry point
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Valid Request?  │
                    └────┬──────┬────┘
                    YES  │      │  NO
                         │      ▼
                         │  ┌──────────┐
                         │  │  Error   │
                         │  └──────────┘
                         ▼
              ┌────────────────────────┐
              │  Intent Classification │
              └──────────┬─────────────┘
                         │
                         ▼
         ┌───────────────────────────────────────┐
         │       UnifiedIntelligenceProvider     │
         │                                       │
         │  ┌─────────┐ ┌──────────┐ ┌────────┐ │
         │  │  quick  │ │targeted  │ │  full  │ │
         │  │ <10ms   │ │+company  │ │+ADO    │ │
         │  │         │ │ domains  │ │+KG idx │ │
         │  └────┬────┘ └────┬─────┘ └───┬────┘ │
         └───────┼───────────┼───────────┼──────┘
                 └───────────┼───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Intent Type?   │  ◄── routing decision
                    └──┬──┬──┬──┬──┬─┘
                       │  │  │  │  │
          ┌────────────┘  │  │  │  └──────────────┐
          │         ┌─────┘  │  └────────┐         │
          ▼         ▼        ▼           ▼         ▼
  ┌────────────┐ ┌──────┐ ┌──────┐ ┌─────────┐ ┌──────────────┐
  │Onboarding  │ │ TDD  │ │Plan  │ │ Debug   │ │  Sweep +     │
  │Orchestrator│ │Orch  │ │Orch  │ │ Orch    │ │  Domain Orch │
  └─────┬──────┘ └──┬───┘ └──┬───┘ └────┬────┘ └──────┬───────┘
        └───────────┴─────────┴──────────┴─────────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │  Execute Operation  │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │  Capture Learning   │  ◄── URS confidence update
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Return Response   │
                       └─────────────────────┘
```

### Intelligence Tier Selection

```
  ┌────────────────────────────────────────────────────────────┐
  │ Tier      │ Latency   │ Context loaded                     │
  ├────────────────────────────────────────────────────────────┤
  │ quick     │ < 10ms    │ Base knowledge only                │
  │ targeted  │ + 20ms    │ + Company domain overlays          │
  │ full      │ + 100ms   │ + ADO sprint context + KG index    │
  └────────────────────────────────────────────────────────────┘
```

### Orchestrator Roster

```
  ┌────────────────────────────────────────────────────────────┐
  │ OnboardingOrchestrator    → /onboard {repo}                │
  │ TDDOrchestrator           → /tdd, test generation          │
  │ PlanningOrchestrator      → /plan, phase decomposition     │
  │ DebuggerOrchestrator      → /debug {path}                  │
  │ SweepCatalogueOrchestrator→ /audit fix (Stages 7-8)        │
  │ Domain Orchestrators      → company-specific routing       │
  └────────────────────────────────────────────────────────────┘
  Total: 51 wired orchestrators across 4 tiers
```
