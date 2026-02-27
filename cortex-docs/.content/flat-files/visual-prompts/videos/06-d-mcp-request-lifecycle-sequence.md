---
id: 06-d-mcp-request-lifecycle-sequence
title: MCP Request Lifecycle — Full Sequence
purpose: Illustrates the complete flow of an MCP tool request from gateway to execution — VIDEO 06 hero diagram
audience: [Software Developers, Product Owners]
source_of_truth: cortex/mcp/__wiring_contract__.yaml
last_verified: 2026-02-27
diagram_type: Sequence
interactive: false
tier: 2
learning_sequence: 19
video_prompt: 06-p-traceability-and-transparency.md
video_scene: "Scene 2–4 — The Request Particle tracks this exact sequence"
animation_notes: |
  ## Cinematic Simulation Prompt — 06: MCP Request Lifecycle

  ### Visual Physics & Ambience Protocol
  - **Environment:** Dark-blue vacuum (#0a0e27) with ray-traced reflections on glass corridor floor
  - **Participant stations:** Frosted glassmorphism blocks with per-role neon filaments
  - **Lighting:** Volumetric light bloom at each station, bioluminescent particle trail, ray-traced glass
  - **Request particle:** Cyan bioluminescent orb (~15px) with volumetric light cast and particle wake
  - **Feedback cues:** Green shield flash = governance approved, spinner = tool executing, holographic glitch = rejected

  **SCENE 1 — "The Awakening" (0:00–0:06)**
  Camera: Static center-frame, locked on ray-traced glassmorphism floor stretching
  into the distance — the glass corridor is visible as a perspective line.
  Environment: Absolute dark-blue vacuum (#0a0e27) with volumetric fog drifting low.
  CORTEX logo (cortex-logo.png) fades in as large central hero image with electric-aura
  glow — cyan pulse radiates outward. Ray-traced reflections of the aura stretch down
  the corridor. Hold 4s.
  Logo shrinks to bottom-right watermark (15% opacity) with ease-out parallax slide.

  **SCENE 2 — "FPV Drone Dive: The Gateway" (0:06–0:12)**
  Camera: FPV drone swoops in at a low angle along the glass corridor — volumetric fog
  parts with parallax depth as the drone races forward. Six frosted glassmorphism
  participant stations materialize left-to-right with time-lapse mechanical assembly —
  each station rising from the glass floor and sealing into place: Client, MCP Gateway,
  Intent Router, Master Orchestrator, MCP Tool, Governance Engine.
  Purple neon filaments for Gateway and Orchestrator — internal bioluminescent glow
  suggesting power and authority. Cyan neon filaments for Router and Tool — lighter,
  functional glow. Ray-traced reflections of each station shimmer on the glass corridor
  floor beneath them. Each station casts a volumetric light pool.

  **SCENE 3 — "The Request Particle's Journey" (0:12–0:32)**
  Camera: Slow dolly tracking follows the particle left-to-right with slight parallax
  against the station backgrounds. A bioluminescent cyan orb spawns at Client with
  particle condensation animation — micro-particles converge from the fog.
  2-second pause per station with volumetric light bloom — the orb illuminates each
  station's internal neon structure from within, revealing circuitry detail through
  the frosted glass. Ray-traced caustics dance on the corridor floor.
  At Governance: shield flash green with bioluminescent burst (approved ✅) — a holographic
  approval badge materializes briefly. Ray-traced green caustics bloom outward.
  At Tool: spinner animation with internal neon pulse, result emerges as a green-tinted
  orb with particle evolution — cyan input transforms to green output. Each station's
  activation bar glows on arrival, dims to 40% on departure with a slow neon fade.

  **SCENE 4 — "The Return Path" (0:32–0:42)**
  Camera: Reverse dolly tracking, now right-to-left, with parallax depth reversal.
  Result particle reverses right-to-left along the glass corridor. Each station dims to
  40% after particle passes — neon filaments cool with a time-lapse fade. The corridor
  darkens behind the particle, creating a visual wake of dimming stations.
  Particle arrives at Client and expands into a delivered response card with glassmorphism
  surface and cyan neon border. Latency badge fades in with holographic shimmer:
  "50–150ms typical." Ray-traced reflections of the response card glow on the floor.

  **SCENE 5 — "Orbital Reveal" (0:42–0:50)**
  Camera: 360-degree orbital pan around the horizontal request corridor at 20° elevation.
  All six stations glow at full luminosity with ray-traced reflections. Bioluminescent
  trail persists as a permanent cyan light path connecting all stations — a standing wave
  of particle energy pulses along the trail.
  Glassmorphism "Evidence Bundle" icon materializes center-frame — sealed document with
  cyan checkmark and holographic shimmer — fades to black.
related_diagrams:
  - 01-d-c4-container-full-system.md
  - 07-d-orchestrator-dispatch-flow.md
---

## MCP Request Lifecycle — Full Sequence

### Request Flow (left → right)

```
  Client        MCP Gateway     Intent Router   Master Orch.    MCP Tool    Governance
    │                │                │               │              │            │
    │  JSON-RPC Req  │                │               │              │            │
    │───────────────►│                │               │              │            │
    │                │                │               │              │            │
    │                │ Validate Proto │               │              │            │
    │                │◄──────────────►│               │              │            │
    │                │                │               │              │            │
    │                │  Route Intent  │               │              │            │
    │                │───────────────►│               │              │            │
    │                │                │               │              │            │
    │                │                │ Classify +    │              │            │
    │                │                │ Dispatch      │              │            │
    │                │                │──────────────►│              │            │
    │                │                │               │              │            │
    │                │                │               │ Check Gov.   │            │
    │                │                │               │─────────────────────────►│
    │                │                │               │              │            │
    │                │                │               │   ✅ Approved│            │
    │                │                │               │◄─────────────────────────│
    │                │                │               │              │            │
    │                │                │               │  Execute Tool│            │
    │                │                │               │─────────────►│            │
    │                │                │               │              │            │
    │                │                │               │    Result    │            │
    │                │                │               │◄─────────────│            │
    │                │                │               │              │            │
    │                │   Response     │               │              │            │
    │                │◄──────────────────────────────│              │            │
    │                │                │               │              │            │
    │ JSON-RPC Resp  │                │               │              │            │
    │◄───────────────│                │               │              │            │
    │                │                │               │              │            │

  Typical latency: 50–150ms end-to-end
```

### Governance Decision Paths

```
  Governance Engine receives request
          │
          ▼
  ┌──────────────────────────────┐
  │  Check 38 CORE Rules         │
  │  + validate context          │
  └──────────┬───────────────────┘
             │
      ┌──────┴───────┐
      │              │
   APPROVED        REJECTED
      │              │
      ▼              ▼
  Continue      Return error
  to Tool       to Orchestrator
                (logged to SQLite)
```

### Participant Roles

```
  ┌────────────────────┬──────────────────────────────────────────────┐
  │ Client             │ VS Code + Copilot Chat — initiates request    │
  │ MCP Gateway        │ JSON-RPC entry point, protocol validation     │
  │ Intent Router      │ Classifies request, selects orchestrator type │
  │ Master Orchestrator│ Coordinates execution, owns lifecycle         │
  │ Governance Engine  │ Enforces 38 CORE rules before any action      │
  │ MCP Tool           │ Performs the actual operation (29 tools)      │
  └────────────────────┴──────────────────────────────────────────────┘
```
