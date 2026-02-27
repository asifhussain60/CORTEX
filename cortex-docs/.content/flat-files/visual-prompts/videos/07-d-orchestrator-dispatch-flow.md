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

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame. CORTEX logo fades in with electric-aura glow. Hold 4s.
  Logo shrinks to bottom-right watermark.

  **SCENE 2 — "FPV Drone Dive: Request Entry" (0:06–0:12)**
  Camera: FPV drone arrives at the top of a vertical glassmorphism pipeline. MCP Request
  node glows green at the apex. A validation diamond appears — "Yes" path illuminates
  green, "No" path flashes red with ghost particle to Error node.

  **SCENE 3 — "Intelligence Tiers" (0:12–0:24)**
  The particle passes validation and enters Intent Classification. UnifiedIntelligenceProvider
  materializes as three concentric glassmorphism rings:
  - Inner ring: "quick — <10ms" (thin cyan glow)
  - Middle ring: "targeted — +company domains" (medium cyan glow)
  - Outer ring: "full — +ADO sprint + KG index" (thick cyan glow)
  Particle enters the appropriate tier based on request complexity.

  **SCENE 4 — "The Routing Decision" (0:24–0:36)**
  Camera: Router diamond receives the particle. Six orchestrator capsules fan out below.
  The particle follows ONE path — that capsule illuminates to full brightness; all others
  dim to 20%. Selected orchestrator executes. Result feeds into Learning capture.

  **SCENE 5 — "Orbital Reveal" (0:36–0:46)**
  Camera: 360-degree orbital pan. Bioluminescent trail persists as permanent neon path.
  Glassmorphism "Evidence Bundle" icon materializes — sealed document with cyan checkmark
  — fades to black.
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
